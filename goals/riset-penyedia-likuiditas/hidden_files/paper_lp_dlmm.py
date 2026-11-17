"""Paper trade — metode LP @CryptoSundayz (Meteora DLMM, Solana) NATIVE.
UANG VIRTUAL — tidak ada posisi LP on-chain, tidak ada transaksi.

Metode author (FAKTA dari postingan 14 Nov 2026, lihat dokumen metode di
files/ goal): screening pair SOL, bin step 80/100/200, TVL $5k-$150k,
mcap $300k-$20M, holder >=500, umur token >=3 jam, vol 30 mnt >=$3k,
freeze/mint authority mati, tanpa tax; posisi MIRING range -60% s.d. +5%
(modal dominan di bawah harga); exit TP +8% PnL, tembus atas range ->
tunggu ~10 mnt lalu tutup bila untung >=0.5% atau reposisi (maks 2x),
bawah range >4 jam + vol 1 jam <$20k -> tutup, stop darurat PnL -50% /
harga -80%, maks hold 48 jam; safety: 5 mnt pertama TP/SL tidak dicek,
PnL cross-check sebelum TP, pause setelah 2 rugi beruntun.

NATIVE DLMM (bukan adaptasi V3):
- Pool Meteora DLMM nyata; bin_step + base_factor dibaca ON-CHAIN dari
  akun LbPair via Solana RPC publik (decode layout IDL lb_clmm 0.12.0,
  terverifikasi: discriminator + token mint X/Y cocok).
- Base fee (FAKTA, rumus dokumen Meteora): base_fee_rate =
  base_factor x bin_step x 10 x 10^base_fee_power_factor (presisi 1e9).
  LP hanya menerima (1 - protocol_share) dari fee; protocol_share dibaca
  on-chain (1000 bps = 10% utk kedua pool uji).
  STANK: base_factor 20000, bin_step 100 -> base fee 2,0%, LP 1,8%.
  AMD:   base_factor 10000, bin_step 100 -> base fee 1,0%, LP 0,9%.
  Yang dipakai di simulasi HANYA base fee (minimum). Variable fee
  (volatilitas, maks total 10%) TIDAK dimodelkan -> fee dihitung
  KONSERVATIF dari sisi tarif (fee riil >= yang dimodelkan bila volatil).
- Nilai posisi dihitung dari JUMLAH BIN DISKRIT (matematika DLMM eksak
  utk distribusi spot = likuiditas sama per bin), BUKAN rumus V3 kontinu.
  Selftest membandingkan keduanya: selisih <1% pada bin step 100.
- Harga P = harga token dalam SOL (token_usd / sol_usd); PnL dalam SOL.
  Modal per trade 0,1625 SOL (= 0,65 SOL modal author / 4 posisi dashboard).
  Gas Solana 0,0001 SOL/siklus trade + 0,0001/reposisi (dinyatakan).
- Fee per jam bila in-range: fee_SOL = volume_usd/jam x fee_rate_LP x
  (nilai posisi / reserve_usd). Reserve = proxy pangsa likuiditas aktif
  (nilai SAAT INI utk seluruh jendela; pangsa bin aktif sebenarnya tidak
  tersedia gratis — arah bias tidak dapat dipastikan; lihat asumsi).

Data (GRATIS, tanpa key): harga token USD + volume pool per jam dari
GeckoTerminal OHLCV pool Solana; SOL/USD per jam dari CoinGecko;
screening (holder/authority) dari RugCheck; TVL/mcap/volume dari
DexScreener + GeckoTerminal.

Penggunaan:
  python3 paper_lp_dlmm.py --pool 0x... --bin-step 100 --base-fee-lp 0.018 \\
      --capital-sol 0.1625 --label dlmm-stank --out hasil.json [--no-exits]
  python3 paper_lp_dlmm.py --selftest
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paper_lp_harness import _curl_json, v3_amounts  # noqa: E402

GT_BASE = "https://api.geckoterminal.com/api/v2"

LOW_PCT = 0.60    # batas bawah range: -60%
HIGH_PCT = 0.05   # batas atas range: +5%
TP_PNL = 0.08
BREAK_TP_PNL = 0.005
SL_PNL = -0.50
SL_PRICE = 0.20   # harga token tersisa 20% dari entry (-80%)
MAX_REPOS = 2
MAX_HOLD_H = 48
BELOW_HOURS = 4
BELOW_VOL_USD = 20000.0
GAS_SOL = 0.0001  # per siklus trade; per reposisi +0.0001 (dinyatakan)


# ---------------------------------------------------------------- DLMM bins
def bin_bounds(P0, s):
    """Bin k mencakup [P0*(1+s)^k, P0*(1+s)^(k+1)).
    Range -60%/+5% -> k_min..k_max. Kembalikan (k_min, k_max)."""
    k_min = math.ceil(math.log(1 - LOW_PCT) / math.log(1 + s))
    k_max = math.floor(math.log(1 + HIGH_PCT) / math.log(1 + s))
    return k_min, k_max


def dlmm_bin_amounts(L, P, P0, s, k_min, k_max):
    """Jumlah token X + SOL Y pada posisi DLMM distribusi spot (L sama
    tiap bin) saat harga token P (SOL/token). P0 = harga entry.
    Matematika bin diskrit eksak (bandingkan selftest vs rumus V3)."""
    x_tot, y_tot = 0.0, 0.0
    for k in range(k_min, k_max + 1):
        p_lo = P0 * (1 + s) ** k
        p_hi = P0 * (1 + s) ** (k + 1)
        if p_hi <= P:
            # bin seluruhnya di bawah harga: hanya SOL (Y)
            y_tot += L * (math.sqrt(p_hi) - math.sqrt(p_lo))
        elif p_lo >= P:
            # bin seluruhnya di atas harga: hanya token (X)
            x_tot += L * (1 / math.sqrt(p_lo) - 1 / math.sqrt(p_hi))
        else:
            # bin aktif: campuran
            x_tot += L * (1 / math.sqrt(P) - 1 / math.sqrt(p_hi))
            y_tot += L * (math.sqrt(P) - math.sqrt(p_lo))
    return x_tot, y_tot


def dlmm_L_for_capital(C_sol, P0, s, k_min, k_max):
    """Likuiditas per bin agar nilai posisi di entry = C_sol."""
    x1, y1 = dlmm_bin_amounts(1.0, P0, P0, s, k_min, k_max)
    val1 = x1 * P0 + y1
    return C_sol / val1


# ------------------------------------------------------------------- data
def fetch_sol_hourly(days):
    cg = _curl_json(
        "https://api.coingecko.com/api/v3/coins/solana/market_chart"
        f"?vs_currency=usd&days={days}&interval=hourly")
    out = {}
    for ts_ms, price in cg.get("prices", []):
        hour = (int(ts_ms) // 3600000) * 3600
        out[hour] = float(price)
    return out


def fetch_pool(pool_address, days):
    limit = min(days * 24 + 24, 1000)
    gt = _curl_json(
        f"{GT_BASE}/networks/solana/pools/{pool_address}/ohlcv/hour"
        f"?aggregate=1&limit={limit}")
    rows = {}
    for row in gt["data"]["attributes"]["ohlcv_list"]:
        rows[int(row[0])] = {"token_usd": float(row[4]),
                             "volume_usd": float(row[5])}
    info = _curl_json(
        f"{GT_BASE}/networks/solana/pools/{pool_address}")["data"]["attributes"]
    return rows, {"reserve_usd": float(info["reserve_in_usd"]),
                  "vol24_usd": float(info["volume_usd"]["h24"]),
                  "pool_name": info.get("name"),
                  "market_cap_usd": float(info.get("market_cap_usd") or 0)}


def fetch_candles(pool_address, days):
    sol = fetch_sol_hourly(days)
    rows, meta = fetch_pool(pool_address, days)
    if not rows:
        raise ValueError("tidak ada bar OHLCV pool")
    first, last = min(rows), max(rows)
    # Grid jam penuh dari seri SOL; jam tanpa trade di-forward-fill
    # (harga terakhir, volume 0) agar "hold 48 jam" = jam kalender.
    grid = sorted(h for h in sol if first <= h <= last)
    if len(grid) < 24:
        raise ValueError(f"data gabungan terlalu sedikit: {len(grid)} jam")
    candles = []
    last_close = rows[first]["token_usd"]
    for h in grid:
        if h in rows:
            last_close = rows[h]["token_usd"]
            vol = rows[h]["volume_usd"]
        else:
            vol = 0.0
        candles.append({"t": h, "token_usd": last_close,
                        "sol_usd": sol[h], "volume_usd": vol})
    meta.update({"hours": len(candles),
                 "price_source": "GeckoTerminal pool OHLCV close (harga "
                                 "token USD); jam tanpa trade di-forward-fill "
                                 "+ volume 0",
                 "sol_source": "CoinGecko SOL/USD hourly",
                 "volume_source": f"GeckoTerminal pool {pool_address}"})
    return candles, meta


# --------------------------------------------------------------- simulasi
def simulate_dlmm_trade(candles, start_idx, capital_sol, fee_rate_lp,
                        reserve_usd, bin_step_bps, use_exits=True,
                        max_hold_h=MAX_HOLD_H, gas_sol=GAS_SOL):
    """Satu trade metode author (native DLMM) mulai candles[start_idx]."""
    s = bin_step_bps / 10000.0
    entry = candles[start_idx]
    R0 = entry["token_usd"] / entry["sol_usd"]
    Pa, Pb = (1 - LOW_PCT) * R0, (1 + HIGH_PCT) * R0
    k_min, k_max = bin_bounds(R0, s)
    L = dlmm_L_for_capital(capital_sol, R0, s, k_min, k_max)
    x0, y0 = dlmm_bin_amounts(L, R0, R0, s, k_min, k_max)
    hx0, hy0 = x0, y0  # FIX AUDIT: baseline HODL asli, jangan di-reset saat reposisi
    fees = 0.0
    gas = gas_sol
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
        R = c["token_usd"] / c["sol_usd"]
        x, y = dlmm_bin_amounts(L, R, R0, s, k_min, k_max)
        pos_sol = x * R + y
        hodl_sol = hx0 * R + hy0
        in_range = Pa < R < Pb
        if in_range:
            in_range_h += 1
            fees += (c["volume_usd"] * fee_rate_lp
                     * (pos_sol * c["sol_usd"] / reserve_usd)
                     / c["sol_usd"])
        pnl = (pos_sol + fees - gas - capital_sol) / capital_sol
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
        if R > Pb:
            if pending_break is None:
                pending_break = (i, pnl)
            else:
                if pnl >= BREAK_TP_PNL:
                    exit_reason = "break_above_tp"
                    break
                if repos < MAX_REPOS:
                    # reposisi ke harga baru (range baru di sekitar R)
                    R0 = R
                    Pa, Pb = (1 - LOW_PCT) * R0, (1 + HIGH_PCT) * R0
                    k_min, k_max = bin_bounds(R0, s)
                    L = dlmm_L_for_capital(pos_sol, R0, s, k_min, k_max)
                    _nx, _ny = dlmm_bin_amounts(L, R0, R0, s, k_min, k_max)
                    gas += gas_sol
                    repos += 1
                    pending_break = None
                    below_hours = 0
                else:
                    exit_reason = "break_above_max_repos"
                    break
        elif pending_break is not None:
            pending_break = None  # harga kembali masuk range: batalkan tunggu
        if R < Pa:
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
    R = ex["token_usd"] / ex["sol_usd"]
    x, y = dlmm_bin_amounts(L, R, R0, s, k_min, k_max)
    pos_sol = x * R + y
    hodl_sol = hx0 * R + hy0
    il_sol = pos_sol - hodl_sol
    total_pnl_sol = pos_sol + fees - gas - capital_sol
    if start_idx > 0:
        vol_m30 = candles[start_idx - 1]["volume_usd"] / 2.0
    else:
        vol_m30 = 0.0
    return {
        "entry_ts": entry["t"], "exit_ts": ex["t"],
        "entry_token_usd": entry["token_usd"],
        "exit_token_usd": ex["token_usd"],
        "token_return_pct": 100.0 * (ex["token_usd"] / entry["token_usd"] - 1),
        "entry_sol_usd": entry["sol_usd"], "exit_sol_usd": ex["sol_usd"],
        "exit_reason": exit_reason,
        "hours_held": last_i - start_idx,
        "repos_count": repos,
        "hours_in_range": in_range_h,
        "pct_in_range": 100.0 * in_range_h / max(last_i - start_idx, 1),
        "n_bins": k_max - k_min + 1,
        "pos_value_sol": pos_sol,
        "hodl_value_sol": hodl_sol,
        "il_sol": il_sol,
        "il_pct_vs_hodl": 100.0 * il_sol / hodl_sol,
        "fees_sol": fees,
        "fees_usd": fees * ex["sol_usd"],
        "gas_sol": gas,
        "net_vs_hodl_sol": il_sol + fees - gas,
        "net_vs_hodl_pct": 100.0 * (il_sol + fees - gas) / capital_sol,
        "net_vs_hodl_usd": (il_sol + fees - gas) * ex["sol_usd"],
        "total_pnl_sol": total_pnl_sol,
        "total_pnl_pct": 100.0 * total_pnl_sol / capital_sol,
        "total_pnl_usd": total_pnl_sol * ex["sol_usd"],
        "entry_vol_m30_proxy_usd": vol_m30,
        "entry_vol_leg_pass": vol_m30 >= 3000.0,
    }


def run_pool(candles, capital_sol, fee_rate_lp, reserve_usd, bin_step_bps,
             use_exits=True, entry_step_h=6, vol_filter=True,
             min_age_h=3):
    """Bot sekuensial satu pool: tiap entry_step_h jam, bila tidak ada
    posisi terbuka, umur pool >= min_age_h jam, dan (bila vol_filter)
    kaki volume 30 mnt lolos, buka posisi. Aturan pause: 2 rugi beruntun
    (PnL absolut < 0) -> berhenti masuk."""
    trades = []
    entry_indices = []
    rejected = 0
    paused_skipped = 0
    age_rejected = 0
    consec_losses = 0
    i = 0
    n = len(candles)
    while i < n - 1:
        if use_exits and consec_losses >= 2:
            paused_skipped += 1
            i += entry_step_h
            continue
        if i < min_age_h:
            age_rejected += 1
            i += entry_step_h
            continue
        if vol_filter and i > 0 and candles[i - 1]["volume_usd"] / 2.0 < 3000.0:
            rejected += 1
            i += entry_step_h
            continue
        tr = simulate_dlmm_trade(candles, i, capital_sol, fee_rate_lp,
                                 reserve_usd, bin_step_bps,
                                 use_exits=use_exits)
        trades.append(tr)
        entry_indices.append(i)
        if use_exits:
            consec_losses = consec_losses + 1 if tr["total_pnl_sol"] < 0 else 0
        i = i + max(tr["hours_held"], 1)
        i = ((i + entry_step_h - 1) // entry_step_h) * entry_step_h
    return trades, entry_indices, rejected, paused_skipped, age_rejected


def aggregate(trades, capital_sol):
    n = len(trades)
    if n == 0:
        return {"n_trades": 0}
    reasons = {}
    for tr in trades:
        reasons[tr["exit_reason"]] = reasons.get(tr["exit_reason"], 0) + 1
    net = [tr["net_vs_hodl_sol"] for tr in trades]
    pnl = [tr["total_pnl_sol"] for tr in trades]
    return {
        "n_trades": n,
        "wins_net_vs_hodl": sum(1 for v in net if v > 0),
        "wins_total_pnl": sum(1 for v in pnl if v > 0),
        "win_rate_net_pct": 100.0 * sum(1 for v in net if v > 0) / n,
        "total_net_vs_hodl_sol": sum(net),
        "avg_net_vs_hodl_sol": sum(net) / n,
        "avg_net_vs_hodl_pct": 100.0 * (sum(net) / n) / capital_sol,
        "total_net_vs_hodl_usd": sum(tr["net_vs_hodl_usd"] for tr in trades),
        "total_pnl_sol": sum(pnl),
        "avg_total_pnl_pct": 100.0 * (sum(pnl) / n) / capital_sol,
        "avg_hours_held": sum(tr["hours_held"] for tr in trades) / n,
        "avg_in_range_pct": sum(tr["pct_in_range"] for tr in trades) / n,
        "avg_fees_sol": sum(tr["fees_sol"] for tr in trades) / n,
        "avg_il_sol": sum(tr["il_sol"] for tr in trades) / n,
        "exit_reason_counts": reasons,
    }


def selftest():
    """Uji matematika bin DLMM + tiap cabang exit pada candle sintetis."""
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and cond
        print(f"  {'PASS' if cond else 'FAIL'}  {name} {detail}")

    # 0. Bin diskrit vs rumus V3 kontinu (bin step 100, range -60%/+5%)
    import math as _m
    s = 0.01
    P0 = 0.025
    k_min, k_max = bin_bounds(P0, s)
    C = 0.1625
    L = dlmm_L_for_capital(C, P0, s, k_min, k_max)
    x0, y0 = dlmm_bin_amounts(L, P0, P0, s, k_min, k_max)
    sol_share = y0 / (x0 * P0 + y0)
    check("bins_count_97", k_max - k_min + 1 == 97,
          f"-> {k_max - k_min + 1} bin")
    check("sol_share_~94pct", 0.90 < sol_share < 0.97,
          f"-> SOL {100*sol_share:.1f}% / token {100*(1-sol_share):.1f}%")
    max_dev = 0.0
    for ratio in (1.0, 0.5, 1.04, 0.41, 0.2, 2.0, 0.05):
        P = P0 * ratio
        xd, yd = dlmm_bin_amounts(L, P, P0, s, k_min, k_max)
        val_d = xd * P + yd
        Ra, Rb = 0.40 * P0, 1.05 * P0
        cap_w = C  # nilai dalam SOL; V3 dgn harga R (SOL/token)
        Lv = cap_w / (2 * _m.sqrt(P0) - _m.sqrt(Ra) - P0 / _m.sqrt(Rb))
        xv, yv = v3_amounts(Lv, P, Ra, Rb)
        val_v = xv * P + yv
        dev = abs(val_d - val_v) / val_v
        max_dev = max(max_dev, dev)
    check("dlmm_vs_v3_lt_1pct", max_dev < 0.01,
          f"-> dev maks {100*max_dev:.3f}%")

    def synth(prices, vols, sol=75.0):
        return [{"t": 3600 * i, "token_usd": p * sol, "sol_usd": sol,
                 "volume_usd": v} for i, (p, v) in enumerate(zip(prices, vols))]

    base = [0.025] * 60
    vol_hi = [1_000_000.0] * 60
    vol_lo = [100.0] * 60
    kw = dict(fee_rate_lp=0.018, reserve_usd=140_000, bin_step_bps=100)
    # 1. max hold: harga datar, volume kecil
    tr = simulate_dlmm_trade(synth(base, vol_lo), 0, 0.1625, **kw)
    check("max_hold_48h", tr["exit_reason"] == "max_hold_48h",
          f"-> {tr['exit_reason']}")
    # 2. SL crash ke 0.15x
    crash = [0.025] * 5 + [0.0125, 0.0075, 0.00375] + [0.00375] * 50
    tr = simulate_dlmm_trade(synth(crash, vol_lo), 0, 0.1625, **kw)
    check("sl_crash", tr["exit_reason"] in ("sl_pnl_-50pct", "sl_price_-80pct"),
          f"-> {tr['exit_reason']} jam {tr['hours_held']}")
    # 3. below-range + vol rendah: harga 0.35x (>4 jam, PnL ~-46% < SL)
    low = [0.025] * 3 + [0.00875] * 50
    tr = simulate_dlmm_trade(synth(low, vol_lo), 0, 0.1625, **kw)
    check("below_range_low_vol", tr["exit_reason"] == "below_range_low_vol",
          f"-> {tr['exit_reason']} jam {tr['hours_held']}")
    # 4. reposisi: harga lompat ke 1.20x lalu bertahan
    jump = [0.025] * 3 + [0.030] * 50
    tr = simulate_dlmm_trade(synth(jump, vol_lo), 0, 0.1625, **kw)
    check("reposition_1x", tr["repos_count"] >= 1,
          f"-> repos {tr['repos_count']} exit {tr['exit_reason']}")
    # 5. TP +8%: volume raksasa -> fee dorong PnL >=8%
    tr = simulate_dlmm_trade(synth(base, vol_hi), 0, 0.1625, **kw)
    check("tp_8pct", tr["exit_reason"] == "tp_8pct",
          f"-> {tr['exit_reason']} pnl {tr['total_pnl_pct']:.1f}%")
    # 6. break-above TP: harga ke 1.06x dgn volume sedang
    brk = [0.025] * 3 + [0.0265] * 50
    tr = simulate_dlmm_trade(synth(brk, [50_000.0] * 60), 0, 0.1625, **kw)
    check("break_above_tp", tr["exit_reason"] == "break_above_tp",
          f"-> {tr['exit_reason']} pnl {tr['total_pnl_pct']:.2f}%")
    # 7. kontrol tanpa exit: crash tapi hold sampai 48 jam
    tr = simulate_dlmm_trade(synth(crash, vol_lo), 0, 0.1625, use_exits=False,
                             **kw)
    check("no_exits_hold_48h", tr["exit_reason"] == "max_hold_48h"
          and tr["hours_held"] == 48,
          f"-> {tr['exit_reason']} jam {tr['hours_held']}")
    # 8. fee sanity: 1 jam in-range, vol $100k, fee 1.8%, posisi/reserve ~1/1000
    one = synth([0.025] * 3, [100_000.0] * 3)
    tr = simulate_dlmm_trade(one, 0, 0.1625, **kw)
    exp_fee = 100_000 * 0.018 * (0.1625 * 75 / 140_000) / 75
    check("fee_formula", abs(tr["fees_sol"] - 2 * exp_fee) < 0.2 * exp_fee,
          f"-> fee {tr['fees_sol']:.6f} SOL (ekspektasi ~{2*exp_fee:.6f})")
    print("HASIL SELFTEST:", "LOLOS" if ok else "GAGAL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=False)
    ap.add_argument("--days", type=int, default=15)
    ap.add_argument("--capital-sol", type=float, default=0.1625)
    ap.add_argument("--fee-rate-lp", type=float, required=False,
                    help="tarif fee LP (sesudah potongan protokol), fraksi")
    ap.add_argument("--base-fee", type=float, required=False,
                    help="base fee pool (fraksi); LP = base*(1-protocol_share)")
    ap.add_argument("--protocol-share", type=float, default=0.10)
    ap.add_argument("--bin-step", type=int, default=100)
    ap.add_argument("--label", default="dlmm")
    ap.add_argument("--out", required=False)
    ap.add_argument("--no-exits", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.pool:
        print("butuh --pool (alamat pool Meteora DLMM)", file=sys.stderr)
        return 2
    if args.fee_rate_lp is not None:
        fee_lp = args.fee_rate_lp
    elif args.base_fee is not None:
        fee_lp = args.base_fee * (1 - args.protocol_share)
    else:
        print("butuh --fee-rate-lp atau --base-fee", file=sys.stderr)
        return 2
    candles, meta = fetch_candles(args.pool, args.days)
    reserve = meta["reserve_usd"]
    trades, entry_idx, rejected, paused, age_rej = run_pool(
        candles, args.capital_sol, fee_lp, reserve, args.bin_step,
        use_exits=not args.no_exits)
    control_trades = None
    control_agg = None
    if not args.no_exits:
        control_trades = [
            simulate_dlmm_trade(candles, s, args.capital_sol, fee_lp,
                                reserve, args.bin_step, use_exits=False)
            for s in entry_idx
        ]
        control_agg = aggregate(control_trades, args.capital_sol)
    res = {
        "label": args.label,
        "method": "CryptoSundayz (Meteora DLMM) NATIVE di Solana",
        "pool": args.pool,
        "pool_name": meta.get("pool_name"),
        "bin_step_bps": args.bin_step,
        "base_fee": args.base_fee,
        "protocol_share": args.protocol_share,
        "fee_rate_lp": fee_lp,
        "range": "asimetris -60%/+5% (Pa=0.40*P0, Pb=1.05*P0), "
                 "distribusi spot (likuiditas sama tiap bin)",
        "capital_sol": args.capital_sol,
        "days": args.days,
        "hours": meta["hours"],
        "reserve_usd": reserve,
        "vol24_usd": meta["vol24_usd"],
        "market_cap_usd": meta["market_cap_usd"],
        "exits_enabled": not args.no_exits,
        "screen_rejected_entries": rejected,
        "paused_skipped_entries": paused,
        "age_rejected_entries": age_rej,
        "period_start_ts": candles[0]["t"],
        "period_end_ts": candles[-1]["t"],
        "entry_price_token_usd_first": candles[0]["token_usd"],
        "exit_price_token_usd_last": candles[-1]["token_usd"],
        "data_source": "Harga token USD + volume pool dari GeckoTerminal "
                       "OHLCV hourly (Solana); SOL/USD dari CoinGecko hourly",
        "data_meta": meta,
        "trades": trades,
        "aggregate": aggregate(trades, args.capital_sol),
        "control_trades_same_entries": control_trades,
        "control_aggregate": control_agg,
        "assumptions": [
            "UANG VIRTUAL — tidak ada posisi LP on-chain, tidak ada transaksi.",
            "NATIVE DLMM: nilai posisi dari jumlah bin diskrit eksak "
            "(distribusi spot, likuiditas sama tiap bin); bin step + base "
            "fee dibaca on-chain dari akun LbPair (IDL lb_clmm 0.12.0).",
            "Fee = volume pool/jam x fee_rate_LP x (nilai posisi / "
            "reserve); fee_rate_LP = base fee x (1 - protocol_share). "
            "HANYA base fee yang dimodelkan (minimum); variable fee "
            "(volatilitas, maks total 10%) TIDAK dimodelkan, jadi fee "
            "hasil simulasi adalah batas bawah dari sisi tarif.",
            "Pangsa fee memakai proxy reserve (nilai posisi / reserve "
            "saat ini utk seluruh jendela). Pangsa bin aktif sebenarnya "
            "tidak tersedia gratis (butuh data bin historis); arah bias "
            "tidak dapat dipastikan.",
            "Reserve dipakai nilai SAAT INI utk seluruh jendela (tidak ada "
            "histori reserve).",
            "'Tunggu ~10 menit' didekati dgn close jam berikutnya (resolusi "
            "jam-an). '5 menit pertama TP/SL tidak dicek' didekati dgn tanpa "
            "cek exit pada jam entry.",
            "TP +8% = PnL posisi (nilai+fee-gas-modal)/modal; stop darurat "
            "PnL -50% atau harga token -80% dari entry.",
            "'Rugi' utk aturan pause = PnL absolut trade < 0; 2 rugi "
            "beruntun -> bot berhenti masuk sampai akhir jendela (durasi "
            "pause tidak disebut author).",
            "Entry sekuensial tiap 6 jam bila tidak ada posisi terbuka, umur "
            "pool >=3 jam, dan kaki volume 30 mnt (proxy: volume jam SEBELUM "
            "entry / 2) >= $3k.",
            "Kontrol memakai entry YANG SAMA (range sama, tanpa exit, tanpa "
            "pause) agar perbandingan mengisolasi aturan exit.",
            "Gas Solana 0,0001 SOL/siklus trade + 0,0001/reposisi. Tanpa "
            "slippage; price impact swap >1,5% tidak dimodelkan (posisi "
            "0,1625 SOL di pool ini dampaknya kecil).",
            "Kaki screening (TVL/mcap/holder/umur) hanya terverifikasi HARI "
            "INI; di entry historis diasumsikan lolos — hanya kaki volume "
            "yang dicek per entry.",
            "In-range diukur dari close tiap jam; ekskursi intra-jam tidak "
            "tertangkap. Jam tanpa trade di-forward-fill (harga terakhir, "
            "volume 0).",
        ],
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        print(f"disimpan: {args.out}")
    agg = res["aggregate"]
    print(f"  trades: {agg['n_trades']}  screen_rejected: {rejected}  "
          f"paused_skipped: {paused}  age_rejected: {age_rej}")
    print(f"  win_rate_net: {agg['win_rate_net_pct']:.1f}%  "
          f"total_net_vs_hodl: {agg['total_net_vs_hodl_sol']:.4f} SOL  "
          f"(${agg['total_net_vs_hodl_usd']:.2f})  "
          f"avg_net: {agg['avg_net_vs_hodl_sol']:.4f} SOL")
    if control_agg:
        print(f"  KONTROL (entry sama, tanpa exit): trades "
              f"{control_agg['n_trades']}  total_net_vs_hodl: "
              f"{control_agg['total_net_vs_hodl_sol']:.4f} SOL  "
              f"avg_net: {control_agg['avg_net_vs_hodl_sol']:.4f} SOL")
    print(f"  total_pnl: {agg['total_pnl_sol']:.4f} SOL  "
          f"avg_total_pnl_pct: {agg['avg_total_pnl_pct']:.2f}%")
    print(f"  exit_reasons: {agg['exit_reason_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
