"""Paper-trade harness — LP terkonsentrasi (PancakeSwap V3) di pool BNB, UANG VIRTUAL.

Tujuan: mesin simulasi generik untuk menguji SEBUAH metode LP (rentang, fee tier,
aturan rebalance) pada data harga nyata. Harness ini BUKAN metodenya: parameter
strategi diisi dari luar (lihat --range-pct, --fee-tier, --rebalance).

Matematika posisi V3 (harga P = USDT per WBNB; posisi dalam rentang [Pa, Pb]):
  L = C / (2*sqrt(P0) - sqrt(Pa) - P0/sqrt(Pb))   (total nilai awal = C; campuran
      token ditentukan rentang — 50/50 hanya bila rentang simetris dalam sqrt-harga)
  P <= Pa : x = L*(1/sqrt(Pa) - 1/sqrt(Pb)), y = 0
  Pa < P < Pb : x = L*(1/sqrt(P) - 1/sqrt(Pb)), y = L*(sqrt(P) - sqrt(Pa))
  P >= Pb : x = 0, y = L*(sqrt(Pb) - sqrt(Pa))
  nilai posisi (USDT) = x*P + y
HODL: x0, y0 awal dipertahankan; nilai = x0*P + y0.
IL (vs HODL) = nilai_posisi_tanpa_fee - nilai_HODL (negatif = rugi vs HODL).

Fee per jam (hanya bila harga jam itu di dalam rentang):
  fee = volume_pool_jam_USD * fee_tier * (nilai_posisi / reserve_pool_USD)
  Reserve dipakai sebagai proxy likuiditas aktif -> fee adalah BATAS ATAS (optimistis),
  karena di V3 hanya likuiditas in-range yang berbagi fee.
Waktu in-range diukur dari harga close tiap jam (ekskursi intra-jam tidak tertangkap).

Data: GeckoTerminal OHLCV jam-an (gratis, tanpa key).
Validasi: --validate memeriksa rumus IL V2 terhadap contoh kerja goal yang terverifikasi
  (masuk $10.000, BNB 2x -> HODL $15.000, LP $14.142, shortfall $858; fee 3% -> net -$558)
  dan konvergensi V3 rentang lebar ke IL V2.

Penggunaan:
  python3 paper_lp_harness.py --pool 0x172f... --days 14 --capital 100 \\
      --range-pct 10 --fee-tier 0.0001 --out hasil.json
  python3 paper_lp_harness.py --validate
"""
import argparse
import json
import math
import sys
import urllib.request

GT_BASE = "https://api.geckoterminal.com/api/v2"


def il_v2(r):
    """IL 50/50 full-range vs HODL, r = rasio harga akhir/awal."""
    return 2 * math.sqrt(r) / (1 + r) - 1


def v3_amounts(L, P, Pa, Pb):
    """(x, y) token0=WBNB, token1=USDT pada harga P untuk likuiditas L."""
    sP, sPa, sPb = math.sqrt(P), math.sqrt(Pa), math.sqrt(Pb)
    if P <= Pa:
        return L * (1 / sPa - 1 / sPb), 0.0
    if P >= Pb:
        return 0.0, L * (sPb - sPa)
    return L * (1 / sP - 1 / sPb), L * (sP - sPa)


def _curl_json(url, tries=3):
    """GET JSON lewat curl (urllib di VM ini sering memotong respons besar)."""
    import subprocess
    last = None
    for _ in range(tries):
        try:
            out = subprocess.run(
                ["curl", "-s", "-m", "40", url], capture_output=True,
                timeout=60, check=True)
            return json.loads(out.stdout.decode("utf-8"))
        except Exception as e:  # noqa: BLE001 - retry lalu lempar terakhir
            last = e
    raise last


def fetch_candles(pool_address, days):
    """Kembalikan list {t, close, volume_usd} dengan close = USD per WBNB.

    Harga: CoinGecko market_chart BNB/USD per jam (sumber kanonis, tanpa
    ambiguitas orientasi token). Volume: kolom volume_usd OHLCV jam-an
    GeckoTerminal pool yang dipilih (volume pool valid apa pun orientasi
    harga pool itu). Digabung per jam; jam tanpa volume -> 0.
    """
    cg = _curl_json(
        "https://api.coingecko.com/api/v3/coins/binancecoin/market_chart"
        f"?vs_currency=usd&days={days}&interval=hourly")
    prices = {}
    for ts_ms, price in cg.get("prices", []):
        hour = (int(ts_ms) // 3600000) * 3600
        prices[hour] = float(price)
    limit = min(days * 24 + 24, 1000)
    gt = _curl_json(
        f"{GT_BASE}/networks/bsc/pools/{pool_address}/ohlcv/hour"
        f"?aggregate=1&limit={limit}")
    volumes = {}
    for row in gt["data"]["attributes"]["ohlcv_list"]:
        volumes[int(row[0])] = float(row[5])
    hours = sorted(set(prices) & set(volumes))
    if len(hours) < 24:
        hours = sorted(prices)
        volumes = {h: volumes.get(h, 0.0) for h in hours}
    out = [{"t": h, "close": prices[h], "volume_usd": volumes.get(h, 0.0)}
           for h in hours]
    out.sort(key=lambda r: r["t"])
    if not out:
        raise ValueError("tidak ada candle gabungan harga+volume")
    return out, {"price_source": "CoinGecko BNB/USD hourly",
                 "volume_source": f"GeckoTerminal pool {pool_address}",
                 "hours": len(out)}


def simulate(candles, capital, range_pct, fee_tier, reserve_usd, gas_usd=0.05):
    """Simulasi satu posisi V3 tanpa rebalance (baseline)."""
    P0 = candles[0]["close"]
    Pa = max(P0 * (1 - range_pct / 100.0), P0 * 1e-6)
    Pb = P0 * (1 + range_pct / 100.0)
    L = capital / (2 * math.sqrt(P0) - math.sqrt(Pa) - P0 / math.sqrt(Pb))
    x0, y0 = v3_amounts(L, P0, Pa, Pb)
    assert abs(x0 * P0 + y0 - capital) < capital * 0.01, "modal awal tidak cocok"
    fees = 0.0
    in_range_hours = 0
    series = []
    for c in candles:
        P = c["close"]
        x, y = v3_amounts(L, P, Pa, Pb)
        pos_value = x * P + y
        hodl_value = x0 * P + y0
        in_range = Pa < P < Pb
        if in_range:
            in_range_hours += 1
            fees += c["volume_usd"] * fee_tier * (pos_value / reserve_usd)
        series.append({"t": c["t"], "price": P, "pos_value": pos_value,
                       "hodl_value": hodl_value, "fees_cum": fees,
                       "in_range": in_range})
    last = series[-1]
    il_usd = last["pos_value"] - last["hodl_value"]
    net_vs_hodl = il_usd + fees - gas_usd
    return {
        "entry_price": P0,
        "exit_price": last["price"],
        "price_ratio": last["price"] / P0,
        "range": [Pa, Pb],
        "range_pct": range_pct,
        "fee_tier": fee_tier,
        "capital_usd": capital,
        "hours": len(candles),
        "hours_in_range": in_range_hours,
        "pct_in_range": 100.0 * in_range_hours / len(candles),
        "pos_value_ex_fees": last["pos_value"],
        "hodl_value": last["hodl_value"],
        "il_usd": il_usd,
        "il_pct_vs_hodl": 100.0 * il_usd / last["hodl_value"],
        "fees_usd": fees,
        "gas_usd": gas_usd,
        "net_vs_hodl_usd": net_vs_hodl,
        "net_vs_hodl_pct": 100.0 * net_vs_hodl / capital,
        "total_return_usd": last["pos_value"] + fees - gas_usd,
        "total_return_pct": 100.0 * (last["pos_value"] + fees - gas_usd - capital) / capital,
        "hodl_return_pct": 100.0 * (last["hodl_value"] - capital) / capital,
        "series": series,
    }


def validate():
    """Cek rumus terhadap contoh kerja goal yang terverifikasi."""
    ok = True

    def check(name, got, want, tol):
        nonlocal ok
        good = abs(got - want) <= tol
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {name}: {got:.2f} (harapan {want:.2f})")

    print("== Validasi rumus IL V2 vs contoh kerja goal (masuk $10.000, BNB 2x) ==")
    r = 2.0
    il = il_v2(r)  # ~ -0.0572
    hodl = 5000 * r + 5000
    lp = hodl * (1 + il)
    check("HODL", hodl, 15000, 0.01)
    check("LP tanpa fee", lp, 14142, 1.0)
    check("shortfall (fee breakeven)", hodl - lp, 858, 1.0)
    check("net dgn fee 3% modal", lp + 300 - 10000 - 5000, -558, 1.0)
    print("== Validasi konvergensi V3 rentang lebar -> V2 ==")
    P0 = 600.0
    wide = simulate(
        [{"t": 0, "close": P0, "volume_usd": 0},
         {"t": 1, "close": P0 * 2, "volume_usd": 0}],
        capital=10000, range_pct=1e10, fee_tier=0.0, reserve_usd=1e9, gas_usd=0)
    check("V3 lebar, LP tanpa fee (2x)", wide["pos_value_ex_fees"], 14142, 2.0)
    print("HASIL VALIDASI:", "LOLOS" if ok else "GAGAL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=False)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--capital", type=float, default=100.0)
    ap.add_argument("--range-pct", type=float, default=10.0)
    ap.add_argument("--fee-tier", type=float, default=0.0001)
    ap.add_argument("--reserve-usd", type=float, default=0.0,
                    help="reserve pool USD; 0 = ambil dari GeckoTerminal")
    ap.add_argument("--label", default="baseline")
    ap.add_argument("--out", required=False)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if args.validate:
        return validate()
    if not args.pool:
        print("butuh --pool (alamat pool BSC)", file=sys.stderr)
        return 2
    candles, meta = fetch_candles(args.pool, args.days)
    reserve = args.reserve_usd
    if reserve <= 0:
        pool = _curl_json(f"{GT_BASE}/networks/bsc/pools/{args.pool}")["data"]["attributes"]
        reserve = float(pool["reserve_in_usd"])
        vol24 = float(pool["volume_usd"]["h24"])
    else:
        vol24 = None
    res = simulate(candles, args.capital, args.range_pct, args.fee_tier, reserve)
    res.update({
        "label": args.label,
        "pool": args.pool,
        "reserve_usd": reserve,
        "vol24_usd": vol24,
        "data_source": "Harga CoinGecko BNB/USD hourly + volume GeckoTerminal OHLCV hourly (gratis)",
        "data_meta": meta,
        "period_start_ts": candles[0]["t"],
        "period_end_ts": candles[-1]["t"],
        "assumptions": [
            "UANG VIRTUAL — tidak ada posisi LP on-chain, tidak ada transaksi.",
            "Tanpa rebalance (baseline): posisi dibuka sekali, ditutup di akhir periode.",
            "Fee = volume pool per jam x fee tier x (nilai posisi / reserve pool).",
            "Reserve dipakai sebagai proxy likuiditas aktif: fee adalah BATAS ATAS "
            "(optimistis) karena di V3 hanya likuiditas in-range yang berbagi fee.",
            "In-range diukur dari harga close tiap jam; ekskursi intra-jam tidak tertangkap.",
            "Gas BSC $0.05 untuk satu siklus deposit-claim-withdraw (sesuai catatan goal).",
            "Volume OHLCV GeckoTerminal dipakai apa adanya; tidak ada slippage saat masuk/keluar.",
        ],
    })
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        print(f"disimpan: {args.out}")
    for k in ("entry_price", "exit_price", "price_ratio", "hours", "hours_in_range",
              "pct_in_range", "pos_value_ex_fees", "hodl_value", "il_usd",
              "il_pct_vs_hodl", "fees_usd", "gas_usd", "net_vs_hodl_usd",
              "net_vs_hodl_pct", "total_return_pct", "hodl_return_pct"):
        v = res[k]
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
