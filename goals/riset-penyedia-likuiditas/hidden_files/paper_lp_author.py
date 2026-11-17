"""Paper trade — adaptasi metode LP @CryptoSundayz (Meteora DLMM, Solana)
ke PancakeSwap V3 (BNB). UANG VIRTUAL — tidak ada posisi LP on-chain.

Metode author (FAKTA dari postingan 14 Nov 2026, lihat dokumen metode di
files/ goal): screening SOL pair bin step 80/100/200, TVL $5k-$150k,
mcap $300k-$20M, holder >=500, umur >=3 jam, vol 30 mnt >=$3k, freeze/mint
authority mati, tanpa tax; posisi MIRING range -60% s.d. +5% (modal dominan
di bawah harga); exit TP +8% PnL, tembus atas range -> tunggu ~10 mnt lalu
tutup bila untung >=0.5% atau reposisi (maks 2x), bawah range >4 jam + vol
1 jam <$20k -> tutup, stop darurat PnL -50% / harga -80%, maks hold 48 jam;
safety: 5 mnt pertama TP/SL tidak dicek, PnL cross-check sebelum TP, pause
setelah 2 rugi beruntun.

ADAPTASI ke V3 (INTERPRETASI, belum teruji — lihat dokumen metode):
- bin step DLMM -> fee tier V3 (dipakai 0.25% utk kedua pool uji; NODE memang
  pool V3 0.25%; SI tidak punya pool V3 hidup, jadi posisi V3 0.25% dimodelkan
  di atas seri harga/volume pool V2-nya — diberi label di hasil).
- Range -60%/+5% -> Pa = 0.40 x P0, Pb = 1.05 x P0, dgn P = harga TOKEN
  dalam WBNB (rasio token_usd / bnb_usd).
- "Tunggu ~10 menit" -> dicek pada close jam berikutnya (resolusi data jam-an).
- "5 menit pertama TP/SL tidak dicek" -> tidak ada cek exit pada jam entry
  (loop mulai jam entry+1).
- TP +8% = PnL posisi (nilai + fee - gas - modal) / modal >= +8%.
  (TP berbasis harga tidak mungkin: harga tidak bisa naik >+5% sambil tetap
  in-range; baca dokumen metode.)
- "Rugi" utk aturan pause = PnL absolut trade < 0 (nilai + fee - gas < modal).

Posisi: x TOKEN + y WBNB; nilai USD = x*token_usd + y*bnb_usd.
HODL: x0,y0 awal dipertahankan. Fee = volume pool/jam x fee tier x
(nilai posisi / reserve) hanya bila in-range — reserve sbg proxy likuiditas
aktif -> fee adalah BATAS ATAS (optimistis), sama seperti harness baseline.
Gas BSC $0.05/siklus; tiap reposisi +$0.05.

Data: harga token USD per jam + volume pool per jam dari GeckoTerminal OHLCV
pool (close TERBUKTI = harga token USD — cocok dgn DexScreener priceUsd utk
SI maupun NODE); harga BNB/USD per jam dari CoinGecko.

Penggunaan:
  python3 paper_lp_author.py --pool 0x... --days 15 --capital 100 \\
      --fee-tier 0.0025 --label author-node --out hasil.json [--no-exits]
  python3 paper_lp_author.py --selftest
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paper_lp_harness import v3_amounts, _curl_json  # noqa: E402

GT_BASE = "https://api.geckoterminal.com/api/v2"

LOW_PCT = 0.60   # batas bawah range: -60%
HIGH_PCT = 0.05  # batas atas range: +5%
TP_PNL = 0.08
BREAK_TP_PNL = 0.005
SL_PNL = -0.50
SL_PRICE = 0.20  # harga token tersisa 20% dari entry (-80%)
MAX_REPOS = 2
MAX_HOLD_H = 48
BELOW_HOURS = 4
BELOW_VOL_USD = 20000.0


def fetch_bnb_hourly(days):
    cg = _curl_json(
        "https://api.coingecko.com/api/v3/coins/binancecoin/market_chart"
        f"?vs_currency=usd&days={days}&interval=hourly")
    out = {}
    for ts_ms, price in cg.get("prices", []):
        hour = (int(ts_ms) // 3600000) * 3600
        out[hour] = float(price)
    return out


def fetch_pool(pool_address, days):
    limit = min(days * 24 + 24, 1000)
    gt = _curl_json(
        f"{GT_BASE}/networks/bsc/pools/{pool_address}/ohlcv/hour"
        f"?aggregate=1&limit={limit}")
    rows = {}
    for row in gt["data"]["attributes"]["ohlcv_list"]:
        rows[int(row[0])] = {"token_usd": float(row[4]),
                             "volume_usd": float(row[5])}
    info = _curl_json(f"{GT_BASE}/networks/bsc/pools/{pool_address}")["data"]["attributes"]
    return rows, {"reserve_usd": float(info["reserve_in_usd"]),
                  "vol24_usd": float(info["volume_usd"]["h24"]),
                  "pool_name": info.get("name")}


def fetch_candles(pool_address, days):
    bnb = fetch_bnb_hourly(days)
    rows, meta = fetch_pool(pool_address, days)
    if not rows:
        raise ValueError("tidak ada bar OHLCV pool")
    first, last = min(rows), max(rows)
    # Grid jam penuh: GeckoTerminal hanya mengembalikan jam yang ada trade,
    # jadi jam tanpa trade diisi harga terakhir (forward-fill) + volume 0.
    # Tanpa ini, "hold 48 jam" dihitung dari bar yang berjauhan — salah.
    grid = sorted(h for h in bnb if first <= h <= last)
    if len(grid) < 24:
        raise ValueError(f"data gabungan terlalu sedikit: {len(grid)} jam")
    candles = []
    last_close = rows[first]["token_usd"]  # jangkar: jam grid pertama
    # memakai harga bar pool pertama (grid bisa mulai setelah `first`)
    for h in grid:
        if h in rows:
            last_close = rows[h]["token_usd"]
            vol = rows[h]["volume_usd"]
        else:
            vol = 0.0
        candles.append({"t": h, "token_usd": last_close,
                        "bnb_usd": bnb[h], "volume_usd": vol})
    meta.update({"hours": len(candles),
                 "price_source": "GeckoTerminal pool OHLCV close (harga token USD); "
                                 "jam tanpa trade di-forward-fill + volume 0",
                 "bnb_source": "CoinGecko BNB/USD hourly",
                 "volume_source": f"GeckoTerminal pool {pool_address}"})
    return candles, meta


def simulate_author_trade(candles, start_idx, capital_usd, fee_tier, reserve_usd,
                          use_exits=True, max_hold_h=MAX_HOLD_H, gas_usd=0.05):
    """Satu trade metode author mulai candles[start_idx]. Kembalikan dict."""
    entry = candles[start_idx]
    R0 = entry["token_usd"] / entry["bnb_usd"]
    Ra, Rb = (1 - LOW_PCT) * R0, (1 + HIGH_PCT) * R0
    cap_wbnb = capital_usd / entry["bnb_usd"]
    L = cap_wbnb / (2 * math.sqrt(R0) - math.sqrt(Ra) - R0 / math.sqrt(Rb))
    x0, y0 = v3_amounts(L, R0, Ra, Rb)
    fees = 0.0
    gas = gas_usd
    repos = 0
    below_hours = 0
    pending_break = None
    in_range_h = 0
    exit_reason = None
    last_i = start_idx
    end_idx = min(start_idx + max_hold_h, len(candles) - 1)
    for i in range(start_idx + 1, end_idx + 1):
        c = candles[i]
        last_i = i
        hours_held = i - start_idx
        R = c["token_usd"] / c["bnb_usd"]
        x, y = v3_amounts(L, R, Ra, Rb)
        pos_wbnb = x * R + y
        pos_usd = pos_wbnb * c["bnb_usd"]
        hodl_usd = x0 * c["token_usd"] + y0 * c["bnb_usd"]
        in_range = Ra < R < Rb
        if in_range:
            in_range_h += 1
            fees += c["volume_usd"] * fee_tier * (pos_usd / reserve_usd)
        pnl = (pos_usd + fees - gas - capital_usd) / capital_usd
        if not use_exits:
            if hours_held >= max_hold_h:
                exit_reason = "max_hold_48h"
                break
            continue
        # --- aturan exit author (tidak dicek pada jam entry) ---
        if pnl <= SL_PNL:
            exit_reason = "sl_pnl_-50pct"
            break
        if c["token_usd"] / entry["token_usd"] <= SL_PRICE:
            exit_reason = "sl_price_-80pct"
            break
        if pnl >= TP_PNL:
            exit_reason = "tp_8pct"
            break
        if R > Rb:
            if pending_break is None:
                pending_break = (i, pnl)
            else:
                if pnl >= BREAK_TP_PNL:
                    exit_reason = "break_above_tp"
                    break
                if repos < MAX_REPOS:
                    Ra, Rb = (1 - LOW_PCT) * R, (1 + HIGH_PCT) * R
                    L = pos_wbnb / (2 * math.sqrt(R) - math.sqrt(Ra)
                                    - R / math.sqrt(Rb))
                    gas += gas_usd
                    repos += 1
                    pending_break = None
                    below_hours = 0
                else:
                    exit_reason = "break_above_max_repos"
                    break
        elif pending_break is not None:
            pending_break = None  # harga kembali masuk range: batalkan tunggu
        if R < Ra:
            below_hours += 1
            if below_hours > BELOW_HOURS and c["volume_usd"] < BELOW_VOL_USD:
                exit_reason = "below_range_low_vol"
                break
        else:
            below_hours = 0
        if hours_held >= max_hold_h:
            exit_reason = "max_hold_48h"
            break
    if exit_reason is None:
        exit_reason = "data_end"
    ex = candles[last_i]
    R = ex["token_usd"] / ex["bnb_usd"]
    x, y = v3_amounts(L, R, Ra, Rb)
    pos_usd = (x * R + y) * ex["bnb_usd"]
    hodl_usd = x0 * ex["token_usd"] + y0 * ex["bnb_usd"]
    il_usd = pos_usd - hodl_usd
    total_pnl_usd = pos_usd + fees - gas - capital_usd
    # Kaki volume screening di entry: volume 30 mnt trailing ~ volume jam
    # SEBELUM entry / 2 (pakai jam penuh entry = look-ahead, tidak dipakai).
    if start_idx > 0:
        vol_m30 = candles[start_idx - 1]["volume_usd"] / 2.0
    else:
        vol_m30 = 0.0
    return {
        "entry_ts": entry["t"], "exit_ts": ex["t"],
        "entry_token_usd": entry["token_usd"],
        "exit_token_usd": ex["token_usd"],
        "token_return_pct": 100.0 * (ex["token_usd"] / entry["token_usd"] - 1),
        "entry_bnb_usd": entry["bnb_usd"], "exit_bnb_usd": ex["bnb_usd"],
        "exit_reason": exit_reason,
        "hours_held": last_i - start_idx,
        "repos_count": repos,
        "hours_in_range": in_range_h,
        "pct_in_range": 100.0 * in_range_h / max(last_i - start_idx, 1),
        "pos_value_ex_fees": pos_usd,
        "hodl_value": hodl_usd,
        "il_usd": il_usd,
        "il_pct_vs_hodl": 100.0 * il_usd / hodl_usd,
        "fees_usd": fees,
        "gas_usd": gas,
        "net_vs_hodl_usd": il_usd + fees - gas,
        "net_vs_hodl_pct": 100.0 * (il_usd + fees - gas) / capital_usd,
        "total_pnl_usd": total_pnl_usd,
        "total_pnl_pct": 100.0 * total_pnl_usd / capital_usd,
        "entry_vol_m30_proxy_usd": vol_m30,
        "entry_vol_leg_pass": vol_m30 >= 3000.0,
    }


def run_pool(candles, capital_usd, fee_tier, reserve_usd, use_exits=True,
             entry_step_h=6, vol_filter=True):
    """Bot sekuensial satu pool: tiap entry_step_h jam, bila tidak ada posisi
    terbuka dan (bila vol_filter) kaki volume 30 mnt lolos, buka posisi.
    Aturan pause: 2 rugi beruntun (PnL absolut < 0) -> berhenti masuk.
    Kembalikan (trades, entry_indices, n_screen_rejected, n_paused_skipped)."""
    trades = []
    entry_indices = []
    rejected = 0
    paused_skipped = 0
    consec_losses = 0
    i = 0
    n = len(candles)
    while i < n - 1:
        if use_exits and consec_losses >= 2:
            paused_skipped += 1
            i += entry_step_h
            continue
        if vol_filter and i > 0 and candles[i - 1]["volume_usd"] / 2.0 < 3000.0:
            rejected += 1
            i += entry_step_h
            continue
        tr = simulate_author_trade(candles, i, capital_usd, fee_tier,
                                   reserve_usd, use_exits=use_exits)
        trades.append(tr)
        entry_indices.append(i)
        if use_exits:
            consec_losses = consec_losses + 1 if tr["total_pnl_usd"] < 0 else 0
        # lanjut setelah posisi tutup (tidak ada posisi tumpang tindih)
        i = i + max(tr["hours_held"], 1)
        # ratakan ke kelipatan entry_step_h berikutnya
        i = ((i + entry_step_h - 1) // entry_step_h) * entry_step_h
    return trades, entry_indices, rejected, paused_skipped


def aggregate(trades):
    n = len(trades)
    if n == 0:
        return {"n_trades": 0}
    reasons = {}
    for tr in trades:
        reasons[tr["exit_reason"]] = reasons.get(tr["exit_reason"], 0) + 1
    net = [tr["net_vs_hodl_usd"] for tr in trades]
    pnl = [tr["total_pnl_usd"] for tr in trades]
    return {
        "n_trades": n,
        "wins_net_vs_hodl": sum(1 for v in net if v > 0),
        "wins_total_pnl": sum(1 for v in pnl if v > 0),
        "win_rate_net_pct": 100.0 * sum(1 for v in net if v > 0) / n,
        "total_net_vs_hodl_usd": sum(net),
        "avg_net_vs_hodl_usd": sum(net) / n,
        "avg_net_vs_hodl_pct": 100.0 * (sum(net) / n) / 100.0,
        "total_pnl_usd": sum(pnl),
        "avg_total_pnl_pct": 100.0 * (sum(pnl) / n) / 100.0,
        "avg_hours_held": sum(tr["hours_held"] for tr in trades) / n,
        "avg_in_range_pct": sum(tr["pct_in_range"] for tr in trades) / n,
        "avg_fees_usd": sum(tr["fees_usd"] for tr in trades) / n,
        "avg_il_usd": sum(tr["il_usd"] for tr in trades) / n,
        "exit_reason_counts": reasons,
    }


def selftest():
    """Uji tiap cabang exit pada candle sintetis."""
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and cond
        print(f"  {'PASS' if cond else 'FAIL'}  {name} {detail}")

    def synth(prices, vols, bnb=600.0):
        return [{"t": 3600 * i, "token_usd": p, "bnb_usd": bnb,
                 "volume_usd": v} for i, (p, v) in enumerate(zip(prices, vols))]

    base = [1.0] * 60
    vol_hi = [1_000_000.0] * 60
    vol_lo = [100.0] * 60
    # 1. max hold: harga datar, volume kecil
    tr = simulate_author_trade(synth(base, vol_lo), 0, 100, 0.0025, 50_000)
    check("max_hold_48h", tr["exit_reason"] == "max_hold_48h", f"-> {tr['exit_reason']}")
    # 2. SL harga -80%: crash ke 0.15x
    crash = [1.0] * 5 + [0.5, 0.3, 0.15] + [0.15] * 50
    tr = simulate_author_trade(synth(crash, vol_lo), 0, 100, 0.0025, 50_000)
    check("sl_crash", tr["exit_reason"] in ("sl_pnl_-50pct", "sl_price_-80pct"),
          f"-> {tr['exit_reason']} jam {tr['hours_held']}")
    # 3. below-range + vol rendah: harga 0.35x (di bawah Ra=0.40x, tapi PnL
    # ~-46% sehingga SL darurat -50% belum kena) bertahan >4 jam
    low = [1.0] * 3 + [0.35] * 20 + [0.35] * 30
    tr = simulate_author_trade(synth(low, vol_lo), 0, 100, 0.0025, 50_000)
    check("below_range_low_vol", tr["exit_reason"] == "below_range_low_vol",
          f"-> {tr['exit_reason']} jam {tr['hours_held']}")
    # 4. reposisi: harga lompat ke 1.20x lalu bertahan, fee kecil (PnL <0.5%)
    jump = [1.0] * 3 + [1.20] * 50
    tr = simulate_author_trade(synth(jump, vol_lo), 0, 100, 0.0025, 50_000)
    check("reposition_1x", tr["repos_count"] >= 1,
          f"-> repos {tr['repos_count']} exit {tr['exit_reason']}")
    # 5. TP +8%: volume raksasa + fee tier besar -> fee dorong PnL >=8%
    tr = simulate_author_trade(synth(base, vol_hi), 0, 100, 0.5, 50_000)
    check("tp_8pct", tr["exit_reason"] == "tp_8pct",
          f"-> {tr['exit_reason']} pnl {tr['total_pnl_pct']:.1f}%")
    # 6. break-above TP: harga ke 1.06x (di atas Rb=1.05) dgn volume sedang
    # (fee ~$0.25/jam -> PnL jam berikut ~0.86%, di antara 0.5% dan 8%)
    brk = [1.0] * 3 + [1.06] * 50
    tr = simulate_author_trade(synth(brk, [50_000.0] * 60), 0, 100, 0.0025,
                               50_000)
    check("break_above_tp", tr["exit_reason"] == "break_above_tp",
          f"-> {tr['exit_reason']} pnl {tr['total_pnl_pct']:.2f}%")
    # 7. kontrol tanpa exit: harga crash tapi tetap hold sampai 48 jam
    tr = simulate_author_trade(synth(crash, vol_lo), 0, 100, 0.0025, 50_000,
                               use_exits=False)
    check("no_exits_hold_48h", tr["exit_reason"] == "max_hold_48h"
          and tr["hours_held"] == 48, f"-> {tr['exit_reason']} jam {tr['hours_held']}")
    print("HASIL SELFTEST:", "LOLOS" if ok else "GAGAL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=False)
    ap.add_argument("--days", type=int, default=15)
    ap.add_argument("--capital", type=float, default=100.0)
    ap.add_argument("--fee-tier", type=float, default=0.0025)
    ap.add_argument("--label", default="author")
    ap.add_argument("--out", required=False)
    ap.add_argument("--no-exits", action="store_true",
                    help="kontrol: range sama, tanpa aturan exit author")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.pool:
        print("butuh --pool (alamat pool BSC)", file=sys.stderr)
        return 2
    candles, meta = fetch_candles(args.pool, args.days)
    reserve = meta["reserve_usd"]
    trades, entry_idx, rejected, paused = run_pool(
        candles, args.capital, args.fee_tier, reserve,
        use_exits=not args.no_exits)
    control_trades = None
    control_agg = None
    if not args.no_exits:
        # Kontrol: range sama, tanpa aturan exit — pada ENTRY YANG SAMA,
        # supaya perbandingan mengisolasi nilai aturan exit author.
        control_trades = [
            simulate_author_trade(candles, s, args.capital, args.fee_tier,
                                  reserve, use_exits=False)
            for s in entry_idx
        ]
        control_agg = aggregate(control_trades)
    res = {
        "label": args.label,
        "method": "CryptoSundayz (Meteora DLMM) diadaptasi ke PancakeSwap V3",
        "pool": args.pool,
        "pool_name": meta.get("pool_name"),
        "fee_tier": args.fee_tier,
        "range": "asimetris -60%/+5% (Pa=0.40*P0, Pb=1.05*P0)",
        "capital_usd": args.capital,
        "days": args.days,
        "hours": meta["hours"],
        "reserve_usd": reserve,
        "vol24_usd": meta["vol24_usd"],
        "exits_enabled": not args.no_exits,
        "screen_rejected_entries": rejected,
        "paused_skipped_entries": paused,
        "period_start_ts": candles[0]["t"],
        "period_end_ts": candles[-1]["t"],
        "entry_price_token_usd_first": candles[0]["token_usd"],
        "exit_price_token_usd_last": candles[-1]["token_usd"],
        "data_source": "Harga token USD + volume pool dari GeckoTerminal OHLCV hourly; BNB/USD dari CoinGecko hourly",
        "data_meta": meta,
        "trades": trades,
        "aggregate": aggregate(trades),
        "control_trades_same_entries": control_trades,
        "control_aggregate": control_agg,
        "assumptions": [
            "UANG VIRTUAL — tidak ada posisi LP on-chain, tidak ada transaksi.",
            "ADAPTASI, bukan setup DLMM asli author: bin DLMM -> fee tier V3; "
            "range -60%/+5% -> Pa=0.40*P0, Pb=1.05*P0 pada rasio token/WBNB.",
            "'Tunggu ~10 menit' didekati dgn close jam berikutnya (resolusi jam-an).",
            "'5 menit pertama TP/SL tidak dicek' didekati dgn tanpa cek exit pada jam entry.",
            "TP +8% = PnL posisi (nilai+fee-gas-modal)/modal; stop darurat PnL -50% "
            "atau harga token -80% dari entry.",
            "'Rugi' utk aturan pause = PnL absolut trade < 0; 2 rugi beruntun -> "
            "bot berhenti masuk sampai akhir jendela (durasi pause tidak disebut author).",
            "Entry sekuensial tiap 6 jam bila tidak ada posisi terbuka; entry ditolak "
            "bila kaki volume 30 mnt (proxy: volume jam SEBELUM entry / 2) < $3k.",
            "Kontrol memakai entry YANG SAMA dgn run author (range sama, tanpa exit, "
            "tanpa pause) agar perbandingan mengisolasi aturan exit.",
            "Fee = volume pool/jam x fee tier x (nilai posisi / reserve); reserve "
            "dipakai sbg proxy likuiditas aktif -> fee BATAS ATAS (optimistis).",
            "Reserve dipakai nilai SAAT INI utk seluruh jendela (tidak ada histori reserve).",
            "Jam tanpa trade di-forward-fill (harga terakhir, volume 0) agar 'hold 48 jam' "
            "adalah jam kalender, bukan jumlah bar.",
            "In-range diukur dari close tiap jam; ekskursi intra-jam tidak tertangkap.",
            "Gas BSC $0.05/siklus; tiap reposisi +$0.05. Tanpa slippage; price impact "
            "swap >1.5% tidak dimodelkan (posisi $100 di pool ini dampaknya kecil).",
            "Kaki screening (TVL/mcap/holder/umur) hanya terverifikasi HARI INI; "
            "di entry historis diasumsikan lolos — hanya kaki volume yang dicek per entry.",
        ],
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        print(f"disimpan: {args.out}")
    agg = res["aggregate"]
    print(f"  trades: {agg['n_trades']}  screen_rejected: {rejected}  "
          f"paused_skipped: {paused}")
    print(f"  win_rate_net: {agg['win_rate_net_pct']:.1f}%  "
          f"total_net_vs_hodl: ${agg['total_net_vs_hodl_usd']:.2f}  "
          f"avg_net: ${agg['avg_net_vs_hodl_usd']:.2f}")
    if control_agg:
        print(f"  KONTROL (entry sama, tanpa exit): trades {control_agg['n_trades']}  "
              f"total_net_vs_hodl: ${control_agg['total_net_vs_hodl_usd']:.2f}  "
              f"avg_net: ${control_agg['avg_net_vs_hodl_usd']:.2f}")
    print(f"  total_pnl: ${agg['total_pnl_usd']:.2f}  "
          f"avg_total_pnl_pct: {agg['avg_total_pnl_pct']:.2f}%")
    print(f"  exit_reasons: {agg['exit_reason_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
