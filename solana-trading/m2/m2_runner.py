#!/usr/bin/env python3
"""M2 — LP CryptoSundayz DLMM Solana NATIVE (paper, LIVE runner).

Metode author (FAKTA dari postingan 14 Nov 2026, lihat
~/workspace/goals/riset-penyedia-likuiditas/files/metode-lp-cryptosundayz-hasil-solana-dlmm.md):
screening pair SOL, bin step 80/100/200, TVL $5k-$150k, mcap $300k-$20M,
holder >=500, umur token >=3 jam, vol 30 mnt >=$3k, freeze/mint authority
mati, tanpa tax; posisi MIRING range -60% s.d. +5% (modal dominan di bawah
harga); exit TP +8% PnL, tembus atas range -> tunggu ~10 mnt lalu tutup
bila untung >=0.5% atau reposisi (maks 2x), bawah range >4 jam + vol 1 jam
<$20k -> tutup, stop darurat PnL -50% / harga -80%, maks hold 48 jam;
safety: 5 mnt pertama TP/SL tidak dicek, PnL cross-check sebelum TP,
pause setelah 2 rugi beruntun.

PAPER MURNI: tidak pernah sign, broadcast, memanggil baw, menyentuh
wallet/key, atau swap nyata. Satu-satunya "eksekusi" adalah penulisan
ledger virtual ~/workspace/solana-trading/m2/m2-ledger.json + satu file
hasil per trade tertutup di
~/workspace/goals/riset-penyedia-likuiditas/hidden_files/ untuk sync_m2.

Matematika bin DLMM dipakai dari harness historis (jangan ditulis ulang):
  paper_lp_dlmm.bin_bounds / dlmm_bin_amounts / dlmm_L_for_capital
Harness itu simulasi hourly historis; runner ini mesin live per-tick
(poll 15 menit) dengan logika exit yang sama, diadaptasi ke resolusi poll.

KOREKSI LAYOUT LbPair (17 Nov 2026, terverifikasi on-chain, BUKAN
tebakan): docstring harness menyebut "IDL lb_clmm 0.12.0" dengan
StaticParameters 28 byte — layout itu SALAH untuk program yang
ter-deploy. Layout BENAR dari IDL @meteora-ag/dlmm terbaru, diverifikasi
byte-per-byte terhadap akun live STANK + AMD (keduanya 904 byte):
  base_factor u16 @8, protocol_share u16 @32, base_fee_power_factor u8 @34,
  active_id i32 @76, bin_step u16 @80, base_factor_seed u16 @84,
  token_x_mint pubkey @88, token_y_mint pubkey @120,
  last_updated_at i64 @712. StaticParameters = 32 byte (8..40),
  VariableParameters = 32 byte (40..72). Cross-check: base_factor_seed ==
  base_factor (mengikat); active_id == index_reference HANYA diagnostik
  (HOGE live 17 Nov membuktikan keduanya bisa berbeda secara normal).
  STANK: bin_step 100, base_factor 20000, protocol_share 1000, active -407.
  AMD:   bin_step 100, base_factor 10000, protocol_share 1000, active -600.
  Base fee = base_factor * bin_step * 10 * 10^power / 1e9;
  fee LP = base fee * (1 - protocol_share/10000).
  STANK -> base 2,0% LP 1,8%; AMD -> base 1,0% LP 0,9% (cocok dgn ronde-0).

Fee calibration (metode fee_calibration.json, 14 Nov): pangsa fee diukur
dari BinArray on-chain aktif saat entry:
  S' = liq_active * w / amount_y_active, w = sqrt(p_hi) - sqrt(p_lo)
  (harga Q64.64 ternormalisasi), share = L_saya_raw * S' / liq_active,
  L_saya_raw = L_harness * 10^((decX+9)/2).
Bila BinArray tidak terukur -> proxy reserve (nilai posisi / reserve),
DAN TIAP TRADE DILABEL fee_method-nya ("calibrated_onchain" vs
"proxy_reserve").

Baseline HODL TETAP (koreksi audit 14 Nov): hx0/hy0 disimpan saat entry
dan TIDAK PERNAH diubah saat reposisi.

Aturan pause (keputusan operasional runner, BUKAN perubahan metode —
author tidak menyebut durasi pause): sesudah 2 rugi beruntun, entry
dijeda 24 jam, lalu streak direset. Tanpa batas ini runner bisa macet
total bila 2 rugi datang di awal ronde (10 trial takkan tercapai).

Discovery (gratis, tanpa key): GeckoTerminal dexes/meteora/pools +
trending_pools + new_pools (dex id HARUS "meteora" persis — BUKAN
meteora-dbc / meteora-damm-v2), DexScreener boosts/profiles -> resolver
GT token pools, infra pools.db graduated -> resolver yang sama.

Penggunaan:
  python3 m2_runner.py [--dry-run] [--selftest] [--max-eval N]
  --dry-run: discovery + screening live, TANPA tulis ledger/state/hasil,
             TANPA buka posisi.
  --selftest: uji offline (bin math, semua cabang exit, baseline HODL,
             formula fee, idempotent close, decode LbPair, nama file
             sync_m2). Semua harus PASS sebelum runner dipakai live.
"""
import argparse
import base64
import json
import math
import os
import sqlite3
import struct
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
HERE = os.path.dirname(os.path.abspath(__file__))          # .../solana-trading/m2
SOL_DIR = os.path.dirname(HERE)                            # .../solana-trading
LEDGER_PATH = os.path.join(HERE, "m2-ledger.json")
RUNS_LOG = os.path.join(HERE, "m2-runs.log")
LP_DIR = "/home/hatch/workspace/goals/riset-penyedia-likuiditas/hidden_files"
POOLS_DB = os.path.join(SOL_DIR, "infra", "pools.db")

# Harness historis: pinjam matematika bin murni (jangan ditulis ulang).
sys.path.insert(0, LP_DIR)
from paper_lp_dlmm import bin_bounds, dlmm_bin_amounts, dlmm_L_for_capital  # noqa: E402

SOL_MINT = "So11111111111111111111111111111111111111112"
WSOL_MINT = SOL_MINT
GT = "https://api.geckoterminal.com/api/v2"
DS = "https://api.dexscreener.com"
RC = "https://api.rugcheck.xyz/v1/tokens"
SOL_RPC = "https://api.mainnet-beta.solana.com"
DLMM_PROGRAM = "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"

# ---------------- parameter author (CHALLENGE.md §5.2) ----------------
LOW_PCT = 0.60        # batas bawah range: -60%
HIGH_PCT = 0.05       # batas atas range: +5%
CAPITAL_SOL = 0.1625  # modal per trade
TP_PNL = 0.08
BREAK_TP_PNL = 0.005
BREAK_WAIT_S = 600    # ~10 menit
SL_PNL = -0.50
SL_PRICE = 0.20       # harga token tersisa 20% dari entry (-80%)
MAX_REPOS = 2
MAX_HOLD_H = 48
BELOW_HOURS = 4
BELOW_VOL_USD = 20000.0
GAS_SOL = 0.0001      # per siklus trade; per reposisi +0.0001
GRACE_S = 300         # 5 menit pertama: tidak ada cek TP/SL
BIN_STEPS = {80, 100, 200}
TVL_MIN_USD = 5000.0
TVL_MAX_USD = 150000.0
MCAP_MIN_USD = 300000.0
MCAP_MAX_USD = 20000000.0
MIN_HOLDERS = 500
MIN_AGE_H = 3.0
MIN_VOL_M30_USD = 3000.0
PAUSE_HOURS = 24      # keputusan operasional runner (lihat docstring)
MAX_EVAL_PER_RUN = 10
RUN_DEADLINE_S = 200   # satu run cron (±280 dtk) berhenti evaluasi baru
RUN_DEADLINE_TS = None  # diisi run() dgn start + RUN_DEADLINE_S
PRICE_SANITY_TOL = 0.15   # harga bin aktif vs DexScreener, maks deviasi 15%
FEE_SHARE_MAX = 0.05      # pangsa kalibrasi di atas ini = tidak wajar -> proxy

UA = {"User-Agent": "m2-lp-dlmm-paper/1.0 (read-only research)"}


def now_wib():
    return datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")


def now_ts():
    return int(time.time())


def log(msg):
    line = f"[{now_wib()}] {msg}"
    print(line, flush=True)
    try:
        with open(RUNS_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _curl_json(url, timeout=30):
    """Fallback via curl (tahan IncompleteRead egress VM lebih baik
    daripada urllib — terbukti di probe 17 Nov). Kembalikan dict/list
    atau {'_error': ...}."""
    import subprocess
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", str(timeout), "-A", UA["User-Agent"], url],
            capture_output=True, text=True, timeout=timeout + 5)
        if not r.stdout.strip():
            return {"_error": f"curl_empty_rc={r.returncode}"}
        return json.loads(r.stdout)
    except Exception as e:
        return {"_error": f"curl_{e}"}


def http_json(url, timeout=15, retries=1):
    """GET JSON; kembalikan dict/list, atau {'_error': ...} / {'_http_error': code}.
    urllib dulu; bila gagal transport (IncompleteRead/timeout/5xx/429),
    fallback curl sekali. Timeout dijaga pendek (15 dtk) agar satu run
    cron (±280 dtk) tidak habis oleh segelintir call yang flap."""
    last = {"_error": "no_attempt"}
    for _ in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            last = {"_http_error": e.code}
            if e.code in (429, 500, 502, 503):
                time.sleep(3)
                continue
            return last
        except Exception as e:
            last = {"_error": str(e)}
            time.sleep(2)
    # transport gagal berulang -> curl sekali
    if "_http_error" not in last:
        cur = _curl_json(url, timeout=max(timeout, 20))
        if "_error" not in cur and "_http_error" not in cur:
            return cur
        last = cur
    return last


def sol_rpc(method, params, timeout=30):
    """Satu call JSON-RPC Solana; kembalikan result atau None."""
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                          "params": params}).encode()
    for _ in range(2):
        try:
            req = urllib.request.Request(
                SOL_RPC, data=payload,
                headers={"Content-Type": "application/json", **UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
            if "error" in d:
                return None
            return d.get("result")
        except Exception:
            time.sleep(2)
    return None


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------- decode on-chain (layout terverifikasi 17 Nov 2026) ----------------

def decode_lbpair(raw):
    """Decode akun LbPair 904 byte -> dict, atau None bila tidak cocok.
    Offsets dari IDL @meteora-ag/dlmm terbaru (lihat docstring)."""
    if raw is None or len(raw) != 904:
        return None
    disc = list(raw[:8])
    if disc != [33, 11, 49, 98, 181, 101, 177, 13]:
        return None
    base_factor, = struct.unpack_from("<H", raw, 8)
    protocol_share, = struct.unpack_from("<H", raw, 32)
    power_factor = raw[34]
    idx_ref, = struct.unpack_from("<i", raw, 48)
    active_id, = struct.unpack_from("<i", raw, 76)
    bin_step, = struct.unpack_from("<H", raw, 80)
    base_factor_seed, = struct.unpack_from("<H", raw, 84)
    token_x = base64.b64encode(raw[88:120]).decode()
    token_y = base64.b64encode(raw[120:152]).decode()
    # pubkey base58 (tanpa dependensi solana): konversi manual
    token_x_b58 = b58encode(raw[88:120])
    token_y_b58 = b58encode(raw[120:152])
    base_fee = base_factor * bin_step * 10 * (10 ** power_factor) / 1e9
    fee_lp = base_fee * (1 - protocol_share / 10000.0)
    return {
        "base_factor": base_factor, "base_factor_seed": base_factor_seed,
        "protocol_share": protocol_share,
        "base_fee_power_factor": power_factor,
        "index_reference": idx_ref, "active_id": active_id,
        "bin_step": bin_step, "token_x_mint": token_x_b58,
        "token_y_mint": token_y_b58,
        "base_fee": base_fee, "fee_rate_lp": fee_lp,
        "cross_active_eq_idxref": active_id == idx_ref,
        "cross_seed_eq_factor": base_factor_seed == base_factor,
    }


_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(b):
    n = int.from_bytes(b, "big")
    s = ""
    while n > 0:
        n, r = divmod(n, 58)
        s = _B58[r] + s
    pad = 0
    for c in b:
        if c == 0:
            pad += 1
        else:
            break
    return "1" * pad + s


def fetch_lbpair(pool_addr):
    """Baca akun LbPair pool -> dict decode, atau None."""
    res = sol_rpc("getAccountInfo", [pool_addr, {"encoding": "base64"}])
    if not res or not res.get("value"):
        return None
    try:
        raw = base64.b64decode(res["value"]["data"][0])
    except Exception:
        return None
    return decode_lbpair(raw)


def fetch_bin_arrays(pool_addr):
    """getProgramAccounts BinArray pool -> {bin_id: {amount_x, amount_y,
    price_u128, liq}} atau None. Pola bin_calib.py (dataSize 10136,
    memcmp offset 24 = pool)."""
    res = sol_rpc("getProgramAccounts", [DLMM_PROGRAM, {
        "encoding": "base64",
        "filters": [{"dataSize": 10136},
                    {"memcmp": {"offset": 24, "bytes": pool_addr}}]}],
        timeout=60)
    if not res:
        return None
    out = {}
    try:
        for a in res:
            data = base64.b64decode(a["account"]["data"][0])
            if len(data) != 10136:
                continue
            idx, = struct.unpack_from("<q", data, 8)
            for i in range(70):
                off = 56 + i * 144
                ax, = struct.unpack_from("<Q", data, off)
                ay, = struct.unpack_from("<Q", data, off + 8)
                price = int.from_bytes(data[off + 16:off + 32], "little")
                liq = int.from_bytes(data[off + 32:off + 48], "little")
                out[idx * 70 + i] = {"amount_x": ax, "amount_y": ay,
                                     "price_u128": price, "liq": liq}
    except Exception:
        return None
    return out or None


def fetch_token_decimals(mint):
    res = sol_rpc("getTokenSupply", [mint])
    if not res or not res.get("value"):
        return None
    try:
        return int(res["value"]["decimals"])
    except Exception:
        return None


def bin_price_human(price_u128, dec_x):
    """Harga bin aktif dalam SOL/token (human units).
    price_u128/2^64 adalah harga RAW (tanpa desimal) — terbukti live
    17 Nov: STANK price_u128/2^64 = 0,0174261 = (1,01)^-407 persis,
    sementara harga DS 1,777e-05 SOL/token; raw x 10^(6-9) = 1,7426e-05
    (dev 1,95%). Jadi human = raw x 10^(decX-9). JANGAN bandingkan raw
    langsung dgn harga DS (selisih ~1000x utk token 6 desimal)."""


    return (price_u128 / 2**64) * 10 ** (dec_x - 9)


def calibrate_fee_share(bins, active_id, bin_step_bps, L_harness, dec_x):
    """Pangsa fee dari bin aktif on-chain (metode fee_calibration.json).
    Kembalikan (share, detail) atau (None, alasan)."""
    if not bins or active_id not in bins:
        return None, "active_bin_not_in_arrays"
    b = bins[active_id]
    if b["amount_y"] == 0 or b["liq"] == 0:
        return None, "active_bin_empty"
    s = bin_step_bps / 10000.0
    p_lo = b["price_u128"] / 2**64
    nxt = bins.get(active_id + 1)
    p_hi = (nxt["price_u128"] / 2**64) if nxt else p_lo * (1 + s)
    if p_lo <= 0 or p_hi <= p_lo:
        return None, "bad_bin_prices"
    w = math.sqrt(p_hi) - math.sqrt(p_lo)
    s_prime = b["liq"] * w / b["amount_y"]
    L_raw = L_harness * 10 ** ((dec_x + 9) / 2.0)
    share = L_raw * s_prime / b["liq"]
    detail = {"active_bin": active_id, "liq_active": b["liq"],
              "amount_y_active": b["amount_y"], "s_prime": s_prime,
              "L_harness": L_harness, "L_raw": L_raw,
              "price_active_raw": p_lo, "w_full": w}
    if not (0 < share < FEE_SHARE_MAX):
        return None, f"share_out_of_range_{share:.2e}"
    return share, detail


# ---------------- harga & data pair ----------------

def sol_price_usd(last_known=None):
    """SOL/USD: GeckoTerminal token_price -> CoinGecko simple -> last known."""
    d = http_json(f"{GT}/simple/networks/solana/token_price/{SOL_MINT}")
    try:
        return float(d["data"]["attributes"]["token_prices"][SOL_MINT])
    except Exception:
        pass
    d = http_json("https://api.coingecko.com/api/v3/simple/price"
                  "?ids=solana&vs_currencies=usd", timeout=20)
    try:
        return float(d["solana"]["usd"])
    except Exception:
        pass
    return last_known if last_known else 75.0


def gt_pool(pool_addr):
    """GeckoTerminal single pool: reserve, volume m5/m15/m30/h1/h6/h24,
    market cap, harga token USD."""
    d = http_json(f"{GT}/networks/solana/pools/{pool_addr}")
    try:
        a = d["data"]["attributes"]
        vol = a.get("volume_usd") or {}
        return {"pool": pool_addr, "name": a.get("name"),
                "reserve_usd": float(a.get("reserve_in_usd") or 0),
                "market_cap_usd": (float(a["market_cap_usd"])
                                   if a.get("market_cap_usd") else None),
                "price_usd": float(a.get("base_token_price_usd") or 0),
                "vol_m5": float(vol.get("m5") or 0),
                "vol_m15": float(vol.get("m15") or 0),
                "vol_m30": float(vol.get("m30") or 0),
                "vol_h1": float(vol.get("h1") or 0),
                "vol_h6": float(vol.get("h6") or 0),
                "vol_h24": float(vol.get("h24") or 0),
                "source": "geckoterminal_pool"}
    except Exception:
        return None


def ds_pair(pool_addr):
    """DexScreener pair endpoint: harga, volume, likuiditas, mcap/fdv,
    pairCreatedAt, txns."""
    d = http_json(f"{DS}/latest/dex/pairs/solana/{pool_addr}")
    try:
        p = (d.get("pairs") or [None])[0]
        if not p:
            return None
        vol = p.get("volume") or {}
        return {"pool": pool_addr, "dex": (p.get("dexId") or "").lower(),
                "labels": p.get("labels") or [],
                "price_usd": float(p.get("priceUsd") or 0),
                "liq_usd": float((p.get("liquidity") or {}).get("usd") or 0),
                "fdv": float(p.get("fdv") or 0),
                "mcap": float(p.get("marketCap") or 0),
                "vol_m5": float(vol.get("m5") or 0),
                "vol_h1": float(vol.get("h1") or 0),
                "vol_h6": float(vol.get("h6") or 0),
                "vol_h24": float(vol.get("h24") or 0),
                "txns": p.get("txns") or {},
                "created_at_ms": p.get("pairCreatedAt"),
                "symbol": (p.get("baseToken") or {}).get("symbol"),
                "mint": (p.get("baseToken") or {}).get("address"),
                "source": "dexscreener_pair"}
    except Exception:
        return None


def gt_pool_hourly(pool_addr, limit=60):
    """GeckoTerminal OHLCV jam: {ts: {token_usd, volume_usd}}."""
    d = http_json(f"{GT}/networks/solana/pools/{pool_addr}/ohlcv/hour"
                  f"?aggregate=1&limit={limit}")
    out = {}
    try:
        for row in d["data"]["attributes"]["ohlcv_list"]:
            out[int(row[0])] = {"token_usd": float(row[4]),
                                "volume_usd": float(row[5])}
    except Exception:
        return None
    return out


def fetch_sol_hourly():
    """CoinGecko SOL/USD per jam: {hour_ts: price} (pola harness)."""
    d = http_json("https://api.coingecko.com/api/v3/coins/solana/market_chart"
                  "?vs_currency=usd&days=3&interval=hourly", timeout=25)
    out = {}
    try:
        for ts_ms, price in d.get("prices", []):
            hour = (int(ts_ms) // 3600000) * 3600
            out[hour] = float(price)
    except Exception:
        return None
    return out or None


def rugcheck(mint):
    d = http_json(f"{RC}/{mint}/report", timeout=25)
    time.sleep(1.0)
    if not isinstance(d, dict) or d.get("_error") or d.get("_http_error"):
        return None
    return d


# ---------------- discovery ----------------

def gt_pools_page(kind, page=1):
    """Satu halaman daftar pool GeckoTerminal (trending/new/dex)."""
    if kind.startswith("dex:"):
        url = f"{GT}/networks/solana/dexes/{kind[4:]}/pools?page={page}"
    else:
        url = f"{GT}/networks/solana/{kind}?page={page}"
    d = http_json(url)
    if isinstance(d, dict) and ("_error" in d or "_http_error" in d):
        log(f"gt_pools_page {kind} p{page}: GAGAL {d}")
        return []
    out = []
    try:
        for p in d.get("data", []):
            a = p.get("attributes", {})
            rel = p.get("relationships", {})
            dex = (rel.get("dex", {}).get("data", {}) or {}).get("id", "")
            bt = (rel.get("base_token", {}).get("data", {}) or {}).get("id", "")
            qt = (rel.get("quote_token", {}).get("data", {}) or {}).get("id", "")
            mint = bt.replace("solana_", "") if bt.startswith("solana_") else ""
            quote_sol = qt == f"solana_{SOL_MINT}"
            out.append({"pool": a.get("address"),
                        "name": a.get("name", ""),
                        "symbol": (a.get("name", "").split(" / ")[0] or ""),
                        "mint": mint, "dex": dex, "quote_sol": quote_sol,
                        "reserve_usd": (float(a["reserve_in_usd"])
                                        if a.get("reserve_in_usd") else None),
                        "mcap_usd": (float(a["market_cap_usd"])
                                     if a.get("market_cap_usd") else None)})
    except Exception:
        return []
    return out


def gt_token_pools(mint):
    """Pool-pool GeckoTerminal untuk satu mint -> alamat pool Meteora/SOL."""
    d = http_json(f"{GT}/networks/solana/tokens/{mint}/pools")
    out = []
    try:
        for p in d.get("data", []):
            a = p.get("attributes", {})
            rel = p.get("relationships", {})
            dex = (rel.get("dex", {}).get("data", {}) or {}).get("id", "")
            qt = (rel.get("quote_token", {}).get("data", {}) or {}).get("id", "")
            if dex == "meteora" and qt == f"solana_{SOL_MINT}":
                out.append(a.get("address"))
    except Exception:
        return []
    return out


def ds_meteora_pool(mint):
    """DexScreener tokens/v1 -> pool Meteora DLMM SOL terbesar utk mint."""
    d = http_json(f"{DS}/tokens/v1/solana/{mint}")
    if not isinstance(d, list):
        return None
    best = None
    for p in d:
        if (p.get("dexId") or "").lower() != "meteora":
            continue
        if "DLMM" not in (p.get("labels") or []):
            continue
        if ((p.get("quoteToken") or {}).get("symbol")) != "SOL":
            continue
        liq = (p.get("liquidity") or {}).get("usd") or 0
        if best is None or liq > best[1]:
            best = (p.get("pairAddress"), liq)
    return best[0] if best else None


def discovery():
    """Kembalikan list kandidat {pool, mint, symbol, sources} terurut
    prioritas: pool Meteora GT dulu, lalu trending/new, lalu DS/infra."""
    out = {}

    def add(pool, mint, symbol, source, reserve_usd=None, mcap_usd=None):
        if not pool:
            return
        e = out.setdefault(pool, {"pool": pool, "mint": mint,
                                  "symbol": symbol, "sources": [],
                                  "reserve_usd": reserve_usd,
                                  "mcap_usd": mcap_usd})
        if mint and not e["mint"]:
            e["mint"] = mint
        if symbol and not e["symbol"]:
            e["symbol"] = symbol
        if reserve_usd is not None and e.get("reserve_usd") is None:
            e["reserve_usd"] = reserve_usd
        if source not in e["sources"]:
            e["sources"].append(source)

    # 1. daftar pool Meteora (DLMM) langsung dari GeckoTerminal, 2 halaman
    for page in (1, 2):
        got = []
        for attempt in (1, 2):
            got = gt_pools_page("dex:meteora", page)
            if got:
                break
            log(f"dex meteora p{page}: kosong (percobaan {attempt}), "
                f"ulang 5 dtk")
            time.sleep(5)
        for c in got:
            if c["dex"] == "meteora" and c["quote_sol"]:
                add(c["pool"], c["mint"], c["symbol"], f"gt_meteora_p{page}",
                    reserve_usd=c.get("reserve_usd"),
                    mcap_usd=c.get("mcap_usd"))
        time.sleep(0.5)
    # 2. trending + new pools (saring dex meteora + quote SOL)
    for kind in ("trending_pools", "new_pools"):
        for c in gt_pools_page(kind, 1):
            if c["dex"] == "meteora" and c["quote_sol"]:
                add(c["pool"], c["mint"], c["symbol"], f"gt_{kind}",
                    reserve_usd=c.get("reserve_usd"),
                    mcap_usd=c.get("mcap_usd"))
        time.sleep(0.5)
    # 3. DexScreener boosts + profiles -> mint -> pool Meteora (GT resolver)
    mints = {}
    for kind in ("top", "latest"):
        d = http_json(f"{DS}/token-boosts/{kind}/v1")
        if isinstance(d, list):
            for b in d:
                if b.get("chainId") == "solana":
                    mints[b.get("tokenAddress")] = f"ds_boost_{kind}"
        time.sleep(0.5)
    d = http_json(f"{DS}/token-profiles/latest/v1")
    if isinstance(d, list):
        for b in d:
            if b.get("chainId") == "solana":
                mints.setdefault(b.get("tokenAddress"), "ds_profile_latest")
    time.sleep(0.5)
    # 4. infra pools.db graduated/watch 6 jam terakhir
    try:
        con = sqlite3.connect(f"file:{POOLS_DB}?mode=ro", uri=True, timeout=10)
        rows = con.execute(
            "SELECT mint, pair FROM pools WHERE status IN ('graduated','watch') "
            "ORDER BY last_seen_wib DESC LIMIT 20").fetchall()
        con.close()
        for mint, pair in rows:
            mints.setdefault(mint, "infra_pools")
    except Exception as e:
        log(f"pools.db baca gagal: {e}")
    for mint, src in list(mints.items())[:8]:
        if RUN_DEADLINE_TS and time.time() > RUN_DEADLINE_TS:
            log("discovery: deadline tercapai — stop resolusi mint")
            break
        if not mint or mint == SOL_MINT:
            continue
        pool = ds_meteora_pool(mint)
        if not pool:
            pools = gt_token_pools(mint)
            pool = pools[0] if pools else None
        if pool:
            add(pool, mint, None, src)
        time.sleep(0.3)
    cands = list(out.values())
    # Urutkan: pool dgn reserve dalam band TVL author ($5k-$150k) dulu,
    # lalu yang reserve-nya tak diketahui (resolver DS/infra), terakhir
    # yang jelas di luar band — supaya slot evaluasi tidak habis untuk
    # pool raksasa dari halaman GT yang terurut volume.
    def _rank(c):
        r = c.get("reserve_usd")
        if r is None:
            return (1, 0.0)
        if TVL_MIN_USD <= r <= TVL_MAX_USD:
            return (0, r)
        return (2, r)
    cands.sort(key=_rank)
    log(f"discovery: {len(cands)} pool Meteora/SOL unik")
    return cands


# ---------------- screening (fungsi murni — bisa di-selftest) ----------------

def screen_pair(gt, ds, now):
    """Kaki pair dari GT + DS. Kembalikan (lolos, legs dict)."""
    legs = {}
    if gt is None and ds is None:
        return False, {"pair_data": "unavailable"}
    # TVL: GT reserve dulu, fallback DS liquidity
    tvl, tvl_src = None, None
    if gt and gt.get("reserve_usd"):
        tvl, tvl_src = gt["reserve_usd"], "gt_reserve"
    elif ds and ds.get("liq_usd"):
        tvl, tvl_src = ds["liq_usd"], "ds_liquidity"
    legs["tvl_usd"] = tvl
    legs["tvl_source"] = tvl_src
    legs["tvl_pass"] = tvl is not None and TVL_MIN_USD <= tvl <= TVL_MAX_USD
    # mcap: DS marketCap -> GT market_cap -> DS fdv.
    # GUARD (17 Nov, bukti live TTWO): DS marketCap kadang glitch
    # (TTWO: DS $92 padahal GT $5,39 jt / fdv $5,4 jt). Bila DS mcap
    # < $1k sementara GT/fdv tersedia, pakai GT/fdv.
    mcap, mcap_src = None, None
    ds_mcap = ds.get("mcap") if ds else None
    gt_mcap = gt.get("market_cap_usd") if gt else None
    fdv = ds.get("fdv") if ds else None
    if ds_mcap and ds_mcap >= 1000:
        mcap, mcap_src = ds_mcap, "ds_marketCap"
    elif gt_mcap:
        mcap, mcap_src = gt_mcap, "gt_market_cap"
    elif fdv:
        mcap, mcap_src = fdv, "ds_fdv"
    elif ds_mcap:
        mcap, mcap_src = ds_mcap, "ds_marketCap"
    legs["mcap_usd"] = mcap
    legs["mcap_source"] = mcap_src
    legs["mcap_pass"] = mcap is not None and MCAP_MIN_USD <= mcap <= MCAP_MAX_USD
    # volume 30 mnt: GT m30 (sumber utama)
    vol30 = gt.get("vol_m30") if gt else None
    legs["vol_m30_usd"] = vol30
    legs["vol_m30_source"] = "gt_m30" if gt else None
    legs["vol_m30_pass"] = vol30 is not None and vol30 >= MIN_VOL_M30_USD
    # umur token: DS pairCreatedAt
    age_h = None
    if ds and ds.get("created_at_ms"):
        age_h = (now - int(ds["created_at_ms"]) / 1000.0) / 3600.0
    legs["age_hours"] = age_h
    legs["age_pass"] = age_h is not None and age_h >= MIN_AGE_H
    ok = all([legs["tvl_pass"], legs["mcap_pass"], legs["vol_m30_pass"],
              legs["age_pass"]])
    return ok, legs


def screen_rugcheck(rc):
    """Kaki RugCheck: holder >=500, authority mati, tanpa transfer fee,
    tidak rugged. Kembalikan (lolos, legs dict)."""
    if rc is None:
        return False, {"rugcheck": "unavailable"}
    legs = {}
    legs["holders"] = rc.get("totalHolders")
    legs["holders_pass"] = (rc.get("totalHolders") or 0) >= MIN_HOLDERS
    tok = rc.get("token") or {}
    legs["mint_authority"] = tok.get("mintAuthority")
    legs["freeze_authority"] = tok.get("freezeAuthority")
    legs["authority_pass"] = (tok.get("mintAuthority") is None
                              and tok.get("freezeAuthority") is None)
    ext = rc.get("token_extensions") or {}
    legs["transfer_fee_config"] = ext.get("transferFeeConfig")
    legs["no_tax_pass"] = ext.get("transferFeeConfig") is None
    legs["rugged"] = rc.get("rugged")
    legs["not_rugged_pass"] = not rc.get("rugged")
    legs["score_normalised"] = rc.get("score_normalised")
    legs["risks"] = [r.get("name") for r in (rc.get("risks") or [])]
    ok = all([legs["holders_pass"], legs["authority_pass"],
              legs["no_tax_pass"], legs["not_rugged_pass"]])
    return ok, legs


def screen_lbpair(lb, mint, price_ds_sol):
    """Kaki on-chain LbPair: bin step di {80,100,200}, mint X/Y cocok,
    harga bin aktif wajar vs DexScreener. Kembalikan (lolos, legs dict)."""
    if lb is None:
        return False, {"lbpair": "unavailable"}
    legs = {}
    legs["bin_step"] = lb.get("bin_step")
    legs["bin_step_pass"] = lb.get("bin_step") in BIN_STEPS
    legs["base_factor"] = lb.get("base_factor")
    legs["protocol_share"] = lb.get("protocol_share")
    legs["base_fee"] = lb.get("base_fee")
    legs["fee_rate_lp"] = lb.get("fee_rate_lp")
    legs["active_id"] = lb.get("active_id")
    legs["token_x_mint"] = lb.get("token_x_mint")
    legs["token_y_mint"] = lb.get("token_y_mint")
    legs["mint_match"] = (lb.get("token_x_mint") == mint
                          and lb.get("token_y_mint") == WSOL_MINT)
    # cross_active_eq_idxref HANYA diagnostik, BUKAN gate (koreksi 17 Nov:
    # HOGE live membuktikan active_id != index_reference itu NORMAL —
    # index_reference adalah acuan volatilitas yang bisa tertinggal dari
    # active_id saat harga baru bergerak; STANK/AMD yang cocok hanya
    # kebetulan). Gate integritas yang mengikat: discriminator + 904 byte
    # + mint_match + seed==factor.
    legs["cross_active_eq_idxref"] = lb.get("cross_active_eq_idxref")
    legs["cross_seed_eq_factor"] = lb.get("cross_seed_eq_factor")
    legs["price_ds_sol"] = price_ds_sol
    ok = all([legs["bin_step_pass"], legs["mint_match"],
              legs["cross_seed_eq_factor"]])
    return ok, legs


# ---------------- posisi: nilai, fee, exit (logika murni) ----------------

def seg_for_ts(pos, ts):
    """Segmen range yang aktif pada ts (riwayat reposisi)."""
    seg = pos["segments"][0]
    for s in pos["segments"]:
        if s["from_ts"] <= ts:
            seg = s
        else:
            break
    return seg


def position_value(pos, R, ts=None):
    """Nilai posisi (SOL) + (x, y) pada harga R memakai segmen aktif."""
    seg = seg_for_ts(pos, ts if ts is not None else now_ts())
    x, y = dlmm_bin_amounts(seg["L"], R, seg["R0"], pos["s"],
                            seg["k_min"], seg["k_max"])
    return x * R + y, x, y


def pnl_state(pos, R):
    """PnL posisi saat ini: (pnl_frac, pos_sol, hodl_sol)."""
    pos_sol, _, _ = position_value(pos, R)
    hodl_sol = pos["hx0"] * R + pos["hy0"]
    pnl = (pos_sol + pos["fees_sol"] - pos["gas_sol"]
           - pos["capital_sol"]) / pos["capital_sol"]
    return pnl, pos_sol, hodl_sol


def accrue_fees(pos, candles, sol_hourly, reserve_usd, now):
    """Akrual fee dari candle jam GeckoTerminal yang sudah lengkap dan
    belum dihitung (ts > last_fee_hour_ts, ts > entry_ts). Mengubah
    pos['fees_sol'] + pos['last_fee_hour_ts']. Kembalikan (fee_sol, n_jam).
    share: kalibrasi (tetap) atau proxy (nilai posisi jam tsb / reserve)."""
    if not candles:
        return 0.0, 0
    cur_hour = (now // 3600) * 3600
    fee = 0.0
    n = 0
    last = pos.get("last_fee_hour_ts") or pos["entry_ts"]
    for ts in sorted(candles):
        if ts <= last or ts <= pos["entry_ts"] or ts >= cur_hour:
            continue
        c = candles[ts]
        sol_usd = (sol_hourly or {}).get(ts) or pos.get("entry_sol_usd")
        if not sol_usd:
            continue
        R = c["token_usd"] / sol_usd
        seg = seg_for_ts(pos, ts)
        in_range = seg["Pa"] < R < seg["Pb"]
        if not in_range:
            pos["last_fee_hour_ts"] = ts
            continue
        if pos["fee_method"] == "calibrated_onchain":
            share = pos["fee_share"]
        else:
            pv, _, _ = position_value(pos, R, ts)
            share = (pv * sol_usd / reserve_usd) if reserve_usd else 0.0
        fee += c["volume_usd"] * pos["fee_rate_lp"] * share / sol_usd
        pos["last_fee_hour_ts"] = ts
        n += 1
    pos["fees_sol"] = pos.get("fees_sol", 0.0) + fee
    return fee, n


def evaluate_exits(pos, tick):
    """Satu tick live (15 mnt). Kembalikan aksi:
    ('hold', None) | ('close', reason) | ('reposition', None).
    Mengubah pos: pending_break, below_hours, in_range_hours, reposisi.
    Urutan sama dgn harness: SL pnl -> SL harga -> TP -> tembus atas ->
    bawah range -> max hold. Grace 5 mnt: tidak ada cek exit."""
    now = tick["ts"]
    R = tick["R"]
    age_s = now - pos["entry_ts"]
    pos["last_manage_ts"] = now
    pos["hours_held"] = age_s / 3600.0
    seg = seg_for_ts(pos, now)
    # akumulasi waktu in-range / below-range (elapsed sejak poll lalu)
    dt_h = 0.0
    if pos.get("prev_manage_ts"):
        dt_h = max(0.0, (now - pos["prev_manage_ts"]) / 3600.0)
        dt_h = min(dt_h, 1.0)  # cap 1 jam per poll (outage tidak ditebak)
    pos["prev_manage_ts"] = now
    if seg["Pa"] < R < seg["Pb"]:
        pos["in_range_hours"] = pos.get("in_range_hours", 0.0) + dt_h
        pos["below_hours"] = 0.0
    elif R < seg["Pa"]:
        pos["below_hours"] = pos.get("below_hours", 0.0) + dt_h
    else:
        pos["below_hours"] = 0.0
    if age_s < GRACE_S:
        return "hold", None
    pnl, _, _ = pnl_state(pos, R)
    if pnl <= SL_PNL:
        return "close", "sl_pnl_-50pct"
    if tick["token_usd"] / pos["entry_token_usd"] <= SL_PRICE:
        return "close", "sl_price_-80pct"
    if pnl >= TP_PNL:
        # cross-check PnL: panggil ulang harga segar sebelum tutup.
        # crosscheck_R False = re-read gagal -> JANGAN tutup (fail-closed).
        cc = tick.get("crosscheck_R")
        if cc is False:
            pos["tp_crosscheck_fail"] = pos.get("tp_crosscheck_fail", 0) + 1
            return "hold", None
        if cc is not None:
            pnl2, _, _ = pnl_state(pos, cc)
            if pnl2 < TP_PNL:
                pos["tp_crosscheck_fail"] = pos.get("tp_crosscheck_fail", 0) + 1
                return "hold", None
        return "close", "tp_8pct"
    if R > seg["Pb"]:
        pb = pos.get("pending_break")
        if pb is None:
            pos["pending_break"] = {"since_ts": now, "pnl_at_detect": pnl}
            return "hold", None
        if now - pb["since_ts"] >= BREAK_WAIT_S:
            if pnl >= BREAK_TP_PNL:
                return "close", "break_above_tp"
            if pos["repos_count"] < MAX_REPOS:
                do_reposition(pos, R, now)
                return "reposition", None
            return "close", "break_above_max_repos"
        return "hold", None
    if pos.get("pending_break") is not None:
        pos["pending_break"] = None  # kembali masuk range: batalkan tunggu
    if R < seg["Pa"]:
        if (pos.get("below_hours", 0.0) > BELOW_HOURS
                and tick.get("vol_h1_usd") is not None
                and tick["vol_h1_usd"] < BELOW_VOL_USD):
            return "close", "below_range_low_vol"
    if age_s >= MAX_HOLD_H * 3600:
        return "close", "max_hold_48h"
    return "hold", None


def do_reposition(pos, R, now):
    """Reposisi ke harga baru. Baseline HODL (hx0/hy0) TIDAK DIUBAH —
    koreksi audit 14 Nov (bug lama menimpa baseline)."""
    pos_sol, _, _ = position_value(pos, R)
    s = pos["s"]
    k_min, k_max = bin_bounds(R, s)
    L = dlmm_L_for_capital(pos_sol, R, s, k_min, k_max)
    seg = {"from_ts": now, "R0": R, "Pa": (1 - LOW_PCT) * R,
           "Pb": (1 + HIGH_PCT) * R, "k_min": k_min, "k_max": k_max, "L": L}
    pos["segments"].append(seg)
    pos["repositions"].append({"ts": now, "price_sol": R,
                              "pos_value_sol": pos_sol})
    pos["gas_sol"] = pos.get("gas_sol", 0.0) + GAS_SOL
    pos["repos_count"] = pos.get("repos_count", 0) + 1
    pos["pending_break"] = None
    pos["below_hours"] = 0.0


def open_position(cand, lb, fee_method, fee_share, fee_detail,
                  entry_token_usd, entry_sol_usd, sol_usd_now):
    """Bangun dict posisi baru (entry). hx0/hy0 = baseline HODL tetap."""
    R0 = entry_token_usd / entry_sol_usd
    s = lb["bin_step"] / 10000.0
    k_min, k_max = bin_bounds(R0, s)
    L = dlmm_L_for_capital(CAPITAL_SOL, R0, s, k_min, k_max)
    x0, y0 = dlmm_bin_amounts(L, R0, R0, s, k_min, k_max)
    ts = now_ts()
    seg = {"from_ts": ts, "R0": R0, "Pa": (1 - LOW_PCT) * R0,
           "Pb": (1 + HIGH_PCT) * R0, "k_min": k_min, "k_max": k_max, "L": L}
    return {
        "pool": cand["pool"], "mint": cand["mint"], "symbol": cand["symbol"],
        "pool_name": cand.get("pool_name"),
        "discovery": ",".join(cand["sources"]),
        "bin_step_bps": lb["bin_step"], "base_factor": lb["base_factor"],
        "protocol_share": lb["protocol_share"],
        "base_fee": lb["base_fee"], "fee_rate_lp": lb["fee_rate_lp"],
        "fee_method": fee_method, "fee_share": fee_share,
        "fee_detail": fee_detail,
        "capital_sol": CAPITAL_SOL, "s": s,
        "entry_ts": ts, "entry_time_wib": now_wib(),
        "entry_token_usd": entry_token_usd, "entry_sol_usd": entry_sol_usd,
        "entry_price_sol": R0,
        "entry_reserve_usd": cand.get("reserve_usd"),
        "entry_vol_m30_usd": cand.get("vol_m30_usd"),
        "segments": [seg], "repositions": [],
        "hx0": x0, "hy0": y0, "x0": x0, "y0": y0,
        "fees_sol": 0.0, "gas_sol": GAS_SOL, "repos_count": 0,
        "below_hours": 0.0, "in_range_hours": 0.0, "hours_held": 0.0,
        "pending_break": None, "last_fee_hour_ts": ts,
        "prev_manage_ts": None, "last_manage_ts": ts,
        "screening": cand.get("screening"),
    }


def close_position(pos, exit_ts, exit_token_usd, exit_sol_usd,
                   exit_reason, fees_partial=False):
    """Finalisasi trade -> dict skema harness + field sync_m2
    (pool, il_usd, fee_method). Baseline HODL dari hx0/hy0 entry."""
    R = exit_token_usd / exit_sol_usd
    pos_sol, _, _ = position_value(pos, R)
    hodl_sol = pos["hx0"] * R + pos["hy0"]
    il_sol = pos_sol - hodl_sol
    fees_sol = pos.get("fees_sol", 0.0)
    gas_sol = pos.get("gas_sol", GAS_SOL)
    cap = pos["capital_sol"]
    total_pnl_sol = pos_sol + fees_sol - gas_sol - cap
    net_sol = il_sol + fees_sol - gas_sol
    seg = seg_for_ts(pos, exit_ts)
    hours_held = (exit_ts - pos["entry_ts"]) / 3600.0
    in_range_h = pos.get("in_range_hours", 0.0)
    return {
        "pool": pos["pool"], "pool_name": pos.get("pool_name"),
        "symbol": pos.get("symbol"), "mint": pos["mint"],
        "entry_ts": pos["entry_ts"], "exit_ts": exit_ts,
        "entry_time_wib": pos["entry_time_wib"],
        "exit_time_wib": datetime.fromtimestamp(exit_ts, WIB).strftime(
            "%Y-%m-%dT%H:%M:%S+07:00"),
        "entry_token_usd": pos["entry_token_usd"],
        "exit_token_usd": exit_token_usd,
        "token_return_pct": 100.0 * (exit_token_usd / pos["entry_token_usd"] - 1),
        "entry_sol_usd": pos["entry_sol_usd"], "exit_sol_usd": exit_sol_usd,
        "entry_price_sol": pos["entry_price_sol"], "exit_price_sol": R,
        "exit_reason": exit_reason,
        "hours_held": round(hours_held, 3),
        "repos_count": pos.get("repos_count", 0),
        "hours_in_range": round(in_range_h, 3),
        "pct_in_range": round(100.0 * in_range_h / max(hours_held, 1e-9), 2),
        "n_bins": seg["k_max"] - seg["k_min"] + 1,
        "bin_step_bps": pos["bin_step_bps"],
        "base_factor": pos["base_factor"],
        "protocol_share": pos["protocol_share"],
        "fee_rate_lp": pos["fee_rate_lp"],
        "fee_method": pos["fee_method"],
        "fee_share": pos.get("fee_share"),
        "capital_sol": cap,
        "pos_value_sol": pos_sol, "hodl_value_sol": hodl_sol,
        "il_sol": il_sol, "il_usd": il_sol * exit_sol_usd,
        "il_pct_vs_hodl": 100.0 * il_sol / hodl_sol if hodl_sol else 0.0,
        "fees_sol": fees_sol, "fees_usd": fees_sol * exit_sol_usd,
        "fees_partial": fees_partial,
        "gas_sol": gas_sol,
        "net_vs_hodl_sol": net_sol,
        "net_vs_hodl_pct": 100.0 * net_sol / cap,
        "net_vs_hodl_usd": net_sol * exit_sol_usd,
        "total_pnl_sol": total_pnl_sol,
        "total_pnl_pct": 100.0 * total_pnl_sol / cap,
        "total_pnl_usd": total_pnl_sol * exit_sol_usd,
        "entry_vol_m30_proxy_usd": pos.get("entry_vol_m30_usd"),
        "entry_vol_leg_pass": True,
        "repositions": pos.get("repositions", []),
        "screening": pos.get("screening"),
        "discovery": pos.get("discovery"),
    }


def result_filename(trade):
    """SATU file per trade tertutup, cocok dgn glob sync_m2
    (paper_lp_*dlmm*.json). Nama deterministik dari entry_ts."""
    poolshort = (trade["pool"] or "")[:8]
    date = datetime.fromtimestamp(trade["entry_ts"], WIB).strftime("%Y%m%d")
    return (f"paper_lp_dlmm_live_{date}_{poolshort}_"
            f"{trade['entry_ts']}.json")


def write_result_file(trade, pos):
    """Tulis file hasil (bila belum ada — idempotent). Kembalikan path."""
    name = result_filename(trade)
    path = os.path.join(LP_DIR, name)
    if os.path.exists(path):
        return path, False
    doc = {
        "label": "m2-live",
        "method": "CryptoSundayz (Meteora DLMM) NATIVE di Solana — LIVE paper runner",
        "pool": trade["pool"], "pool_name": trade.get("pool_name"),
        "symbol": trade.get("symbol"), "mint": trade.get("mint"),
        "bin_step_bps": trade["bin_step_bps"],
        "base_fee": None, "protocol_share": trade["protocol_share"],
        "fee_rate_lp": trade["fee_rate_lp"],
        "fee_method": trade["fee_method"],
        "range": "asimetris -60%/+5% (Pa=0.40*P0, Pb=1.05*P0), "
                 "distribusi spot (likuiditas sama tiap bin)",
        "capital_sol": trade["capital_sol"],
        "reserve_usd": pos.get("entry_reserve_usd"),
        "entry_time_wib": trade["entry_time_wib"],
        "exit_time_wib": trade["exit_time_wib"],
        "data_source": "LIVE: DexScreener + GeckoTerminal + RugCheck + "
                       "Solana RPC (LbPair/BinArray on-chain)",
        "trades": [trade],
        "assumptions": [
            "UANG VIRTUAL — tidak ada posisi LP on-chain, tidak ada transaksi.",
            "NATIVE DLMM: nilai posisi dari jumlah bin diskrit eksak "
            "(distribusi spot, likuiditas sama tiap bin); bin step + base "
            "fee + protocol share dibaca on-chain dari akun LbPair "
            "(layout IDL @meteora-ag/dlmm terbaru, terverifikasi 17 Nov 2026).",
            "Fee = volume pool/jam x fee_rate_LP x pangsa; pangsa diukur "
            "on-chain dari bin aktif saat entry (calibrated_onchain) atau "
            "proxy reserve nilai-posisi/reserve (proxy_reserve) — lihat "
            "fee_method tiap trade. HANYA base fee yang dimodelkan (minimum); "
            "variable fee TIDAK dimodelkan.",
            "Fee diakrual dari candle jam GeckoTerminal yang sudah lengkap "
            "saja (jam berjalan tidak dihitung); jam tanpa candle terhitung "
            "sebagai di luar range bila harga close di luar range.",
            "'Tunggu ~10 menit' tembus-atas = poll berikut (interval cron "
            "15 mnt); '5 menit pertama TP/SL tidak dicek' = grace 300 dtk.",
            "TP +8% = PnL posisi (nilai+fee-gas-modal)/modal, dgn "
            "cross-check harga segar sebelum tutup.",
            "Baseline HODL (hx0/hy0) disimpan saat entry dan TIDAK PERNAH "
            "diubah saat reposisi (koreksi audit 14 Nov).",
            "Pause: 2 rugi beruntun (total_pnl_sol < 0) -> entry dijeda "
            "24 jam, lalu streak direset (keputusan operasional runner; "
            "author tidak menyebut durasi).",
            "Gas Solana 0,0001 SOL/siklus trade + 0,0001/reposisi.",
            "Satu file per trade tertutup (sync_m2 tidak pernah membaca "
            "ulang file yang sudah diimpor).",
        ],
    }
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    return path, True


# ---------------- ledger ----------------

def init_ledger():
    return {"created_wib": now_wib(), "last_run_wib": None,
            "last_sol_usd": None, "open_position": None,
            "closed_trades": [], "consec_losses": 0,
            "pause_until_ts": None,
            "stats": {"runs": 0, "screened": 0, "entries": 0, "closes": 0,
                      "wins": 0, "losses": 0, "skip_reasons": {}}}


def note_skip(led, reason):
    s = led["stats"]["skip_reasons"]
    s[reason] = s.get(reason, 0) + 1


def finalize_close(led, pos, trade):
    """Tutup posisi: tulis file hasil (idempotent) -> catat trade ->
    update streak/pause -> kosongkan posisi. Mengembalikan path file."""
    path, created = write_result_file(trade, pos)
    if not created:
        try:
            trade = json.load(open(path))["trades"][0]
        except Exception:
            pass
    if not any(t["entry_ts"] == trade["entry_ts"] and t["pool"] == trade["pool"]
               for t in led["closed_trades"]):
        led["closed_trades"].append(trade)
        if trade["total_pnl_sol"] < 0:
            led["consec_losses"] = led.get("consec_losses", 0) + 1
            led["stats"]["losses"] += 1
        else:
            led["consec_losses"] = 0
            led["stats"]["wins"] += 1
        if led["consec_losses"] >= 2:
            led["pause_until_ts"] = now_ts() + PAUSE_HOURS * 3600
            led["consec_losses"] = 0
            log(f"PAUSE: 2 rugi beruntun — entry dijeda {PAUSE_HOURS} jam "
                f"s.d. {datetime.fromtimestamp(led['pause_until_ts'], WIB)}")
        led["stats"]["closes"] += 1
    led["open_position"] = None
    return path


# ---------------- live: kelola posisi terbuka ----------------

def manage_open_position(led, sol_usd, dry_run=False):
    """Satu poll untuk posisi terbuka. Kembalikan True bila posisi
    tertutup pada run ini."""
    pos = led.get("open_position")
    if not pos:
        return False
    now = now_ts()
    ds = ds_pair(pos["pool"])
    gt = gt_pool(pos["pool"])
    if ds is None and gt is None:
        log(f"manage {pos.get('symbol')}: harga tak terbaca, lewati")
        return False
    token_usd = (ds.get("price_usd") if ds and ds.get("price_usd")
                 else (gt.get("price_usd") if gt else 0))
    if not token_usd or not sol_usd:
        log(f"manage {pos.get('symbol')}: harga 0, lewati")
        return False
    R = token_usd / sol_usd
    # akrual fee dari candle jam yang sudah lengkap
    fees_partial = False
    candles = gt_pool_hourly(pos["pool"], limit=60)
    if candles is not None:
        sol_h = fetch_sol_hourly()
        reserve = (gt.get("reserve_usd") if gt else None) or pos.get(
            "entry_reserve_usd")
        fee, n = accrue_fees(pos, candles, sol_h, reserve, now)
        if n:
            log(f"fee {pos.get('symbol')}: +{fee:.6f} SOL dari {n} jam")
    else:
        fees_partial = True
    tick = {"ts": now, "R": R, "token_usd": token_usd,
            "vol_h1_usd": (gt.get("vol_h1") if gt else None)}
    # cross-check PnL sebelum TP: bila sinyal TP, baca harga segar sekali
    pnl, _, _ = pnl_state(pos, R)
    if pnl >= TP_PNL:
        ds2 = ds_pair(pos["pool"])
        if ds2 and ds2.get("price_usd"):
            tick["crosscheck_R"] = ds2["price_usd"] / sol_usd
        else:
            tick["crosscheck_R"] = False  # re-read gagal -> jangan tutup
        log(f"TP sinyal {pos.get('symbol')} pnl={100*pnl:.2f}% "
            f"crosscheck_R={tick['crosscheck_R']}")
    action, reason = evaluate_exits(pos, tick)
    if action == "reposition":
        log(f"REPOSISI {pos.get('symbol')} ke R={R:.6e} "
            f"(#{pos['repos_count']}, gas total {pos['gas_sol']:.4f} SOL)")
    elif action == "close":
        # akrual fee final (jam terakhir yang baru lengkap)
        if candles is not None:
            try:
                fee, n = accrue_fees(pos, candles, fetch_sol_hourly(),
                                     (gt.get("reserve_usd") if gt else None)
                                     or pos.get("entry_reserve_usd"), now)
            except Exception:
                fees_partial = True
        trade = close_position(pos, now, token_usd, sol_usd, reason,
                               fees_partial=fees_partial)
        if dry_run:
            log(f"[DRY] akan tutup {pos.get('symbol')} {reason} "
                f"net_vs_hodl={trade['net_vs_hodl_sol']:.4f} SOL "
                f"(${trade['net_vs_hodl_usd']:.2f})")
            return False
        path = finalize_close(led, pos, trade)
        log(f"CLOSED {pos.get('symbol')} {reason} "
            f"net_vs_hodl={trade['net_vs_hodl_sol']:.4f} SOL "
            f"(${trade['net_vs_hodl_usd']:.2f}) "
            f"total_pnl={trade['total_pnl_sol']:.4f} SOL "
            f"file={os.path.basename(path)}")
        return True
    else:
        pnl, pos_sol, hodl = pnl_state(pos, R)
        log(f"hold {pos.get('symbol')}: R={R:.6e} pnl={100*pnl:.2f}% "
            f"pos={pos_sol:.4f} SOL hodl={hodl:.4f} "
            f"fee={pos['fees_sol']:.6f} jam={pos['hours_held']:.2f} "
            f"below={pos.get('below_hours', 0):.2f}j repos={pos['repos_count']}")
    return False


# ---------------- live: evaluasi kandidat ----------------

def evaluate_candidate_live(cand, sol_usd, now):
    """Satu kandidat: pair -> RugCheck -> LbPair on-chain -> BinArray
    (harga + kalibrasi fee). Kembalikan dict hasil dgn 'pass'."""
    res = {"pool": cand["pool"], "mint": cand.get("mint"),
           "symbol": cand.get("symbol"), "sources": cand.get("sources", [])}
    gt = gt_pool(cand["pool"])
    time.sleep(0.3)
    ds = ds_pair(cand["pool"])
    ok, legs = screen_pair(gt, ds, now)
    res["pair_legs"] = legs
    res["reserve_usd"] = legs.get("tvl_usd")
    res["vol_m30_usd"] = legs.get("vol_m30_usd")
    if gt:
        res["pool_name"] = gt.get("name")
    if ds:
        res["symbol"] = res["symbol"] or ds.get("symbol")
        res["mint"] = res["mint"] or ds.get("mint")
    if not ok:
        failed = [k for k in ("tvl_pass", "mcap_pass", "vol_m30_pass",
                              "age_pass") if not legs.get(k)]
        res["skip"] = "pair_" + "+".join(failed)
        return res
    mint = res["mint"]
    if not mint:
        res["skip"] = "mint_unknown"
        return res
    rc = rugcheck(mint)
    ok, rlegs = screen_rugcheck(rc)
    res["rugcheck_legs"] = rlegs
    if not ok:
        failed = [k for k in ("holders_pass", "authority_pass",
                              "no_tax_pass", "not_rugged_pass")
                  if not rlegs.get(k)]
        res["skip"] = "rugcheck_" + "+".join(failed)
        return res
    lb = fetch_lbpair(cand["pool"])
    price_ds_sol = None
    if ds and ds.get("price_usd") and sol_usd:
        price_ds_sol = ds["price_usd"] / sol_usd
    ok, llegs = screen_lbpair(lb, mint, price_ds_sol)
    res["lbpair_legs"] = llegs
    if not ok:
        failed = [k for k in ("bin_step_pass", "mint_match",
                              "cross_seed_eq_factor") if not llegs.get(k)]
        res["skip"] = "lbpair_" + "+".join(failed)
        return res
    # harga bin aktif + kalibrasi fee dari BinArray
    fee_method, fee_share, fee_detail = "proxy_reserve", None, {}
    dec_x = fetch_token_decimals(mint)
    bins = fetch_bin_arrays(cand["pool"])
    if bins is not None and lb["active_id"] in bins:
        # harga bin aktif: RAW -> human dgn 10^(decX-9); tanpa decX,
        # sanity check dilewati (bukan gagal) karena tak bermakna.
        if dec_x is not None:
            p_bin = bin_price_human(bins[lb["active_id"]]["price_u128"],
                                    dec_x)
            res["bin_active_price_sol"] = p_bin
            res["price_ds_sol"] = price_ds_sol
            if price_ds_sol:
                dev = abs(p_bin - price_ds_sol) / price_ds_sol
                res["price_deviation"] = dev
                if dev > PRICE_SANITY_TOL:
                    res["skip"] = f"price_sanity_dev_{dev:.1%}>{PRICE_SANITY_TOL:.0%}"
                    return res
        else:
            res["price_sanity"] = "skipped_no_decimals"
        if dec_x is not None:
            s = lb["bin_step"] / 10000.0
            k_min, k_max = bin_bounds(price_ds_sol or p_bin, s)
            L_h = dlmm_L_for_capital(CAPITAL_SOL, price_ds_sol or p_bin,
                                     s, k_min, k_max)
            share, detail = calibrate_fee_share(bins, lb["active_id"],
                                                lb["bin_step"], L_h, dec_x)
            if share is not None:
                fee_method, fee_share, fee_detail = (
                    "calibrated_onchain", share, detail)
            else:
                fee_detail = {"calibration_fail": detail}
    else:
        fee_detail = {"calibration_fail": "binarrays_unavailable"}
    if fee_method == "proxy_reserve":
        reserve = legs.get("tvl_usd") or 0
        fee_share = (CAPITAL_SOL * sol_usd / reserve) if reserve else 0.0
        fee_detail["proxy_share_entry"] = fee_share
    res["fee_method"] = fee_method
    res["fee_share"] = fee_share
    res["fee_detail"] = fee_detail
    res["lbpair"] = lb
    res["screening"] = {"pair": legs, "rugcheck": rlegs, "lbpair": llegs,
                        "fee_method": fee_method, "fee_share": fee_share}
    res["pass"] = True
    return res


# ---------------- run utama ----------------

def run(dry_run=False, max_eval=MAX_EVAL_PER_RUN):
    global RUN_DEADLINE_TS
    RUN_DEADLINE_TS = time.time() + RUN_DEADLINE_S
    log(f"M2-LP-DLMM run dimulai (dry_run={dry_run})")
    led = load_json(LEDGER_PATH, None) or init_ledger()
    sol_usd = sol_price_usd(led.get("last_sol_usd"))
    log(f"SOL=${sol_usd:.2f}")
    led["stats"]["runs"] += 1
    closed = False
    if led.get("open_position"):
        try:
            closed = manage_open_position(led, sol_usd, dry_run=dry_run)
        except Exception as e:
            log(f"manage posisi error: {e}")
    # pause entries?
    now = now_ts()
    if led.get("pause_until_ts") and now < led["pause_until_ts"]:
        left = (led["pause_until_ts"] - now) / 3600.0
        log(f"PAUSE aktif: entry dijeda {left:.1f} jam lagi")
    elif led.get("pause_until_ts"):
        led["pause_until_ts"] = None
        log("pause berakhir — entry dibuka lagi")
    can_enter = (not led.get("open_position") and not closed
                 and not (led.get("pause_until_ts")
                         and now < led["pause_until_ts"]))
    if can_enter:
        try:
            cands = discovery()
        except Exception as e:
            log(f"discovery error: {e}")
            cands = []
        evaluated = 0
        entered = False
        for cand in cands:
            if evaluated >= max_eval or entered:
                break
            if RUN_DEADLINE_TS and time.time() > RUN_DEADLINE_TS:
                log("evaluasi: deadline tercapai — stop")
                break
            if not cand.get("pool"):
                continue
            try:
                res = evaluate_candidate_live(cand, sol_usd, now)
            except Exception as e:
                log(f"eval {cand['pool'][:8]} error: {e}")
                continue
            evaluated += 1
            led["stats"]["screened"] += 1
            if not res.get("pass"):
                note_skip(led, res.get("skip", "unknown"))
                stage = (res.get("skip", "").split("_")[0])
                legs_show = {"pair": res.get("pair_legs"),
                             "rugcheck": res.get("rugcheck_legs"),
                             "lbpair": res.get("lbpair_legs")}.get(stage)
                log(f"SKIP {res.get('symbol') or cand['pool'][:8]}: "
                    f"{res.get('skip')} legs={legs_show}")
                continue
            # ENTRY (paper)
            token_usd = None
            ds = ds_pair(cand["pool"])
            if ds and ds.get("price_usd"):
                token_usd = ds["price_usd"]
            else:
                gt = gt_pool(cand["pool"])
                token_usd = gt.get("price_usd") if gt else None
            if not token_usd:
                log(f"SKIP {res.get('symbol')}: harga entry tak terbaca")
                continue
            cand2 = dict(cand)
            cand2.update({"pool_name": res.get("pool_name"),
                          "reserve_usd": res.get("reserve_usd"),
                          "vol_m30_usd": res.get("vol_m30_usd"),
                          "screening": res.get("screening"),
                          "symbol": res.get("symbol") or cand.get("symbol"),
                          "mint": res.get("mint")})
            pos = open_position(cand2, res["lbpair"], res["fee_method"],
                                res["fee_share"], res["fee_detail"],
                                token_usd, sol_usd, sol_usd)
            if dry_run:
                log(f"[DRY] akan ENTRY {pos['symbol']} pool "
                    f"{pos['pool'][:8]} bin_step={pos['bin_step_bps']} "
                    f"fee_lp={100*pos['fee_rate_lp']:.2f}% "
                    f"fee_method={pos['fee_method']} "
                    f"share={pos['fee_share']:.2e} "
                    f"entry_R={pos['entry_price_sol']:.6e} SOL/token")
            else:
                led["open_position"] = pos
                led["stats"]["entries"] += 1
                log(f"ENTRY {pos['symbol']} pool {pos['pool']} "
                    f"bin_step={pos['bin_step_bps']} "
                    f"fee_lp={100*pos['fee_rate_lp']:.2f}% "
                    f"fee_method={pos['fee_method']} "
                    f"share={pos['fee_share']:.2e} "
                    f"entry_R={pos['entry_price_sol']:.6e} SOL/token")
            entered = True
        log(f"evaluasi: {evaluated} kandidat, entry={entered}")
    else:
        if led.get("open_position"):
            log("posisi terbuka — tidak ada entry baru (maks 1)")
        elif closed:
            log("posisi baru saja tertutup — entry ditunda ke run berikut")
    led["last_run_wib"] = now_wib()
    led["last_sol_usd"] = sol_usd
    if not dry_run:
        save_json(LEDGER_PATH, led)
    else:
        log("DRY-RUN: tidak ada tulis ledger/state/hasil")
    log(f"run selesai: open={bool(led.get('open_position'))} "
        f"closed_total={len(led.get('closed_trades', []))} "
        f"wins={led['stats']['wins']} losses={led['stats']['losses']} "
        f"screened_total={led['stats']['screened']}")
    return 0


# ---------------- selftest ----------------

def _b58decode(s):
    n = 0
    for c in s:
        n = n * 58 + _B58.index(c)
    b = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + b


def _test_pos(entry_ts=None, R0=0.025, fee=0.018):
    """Posisi sintetis: entry R0 SOL/token, tanpa fee, untuk selftest."""
    if entry_ts is None:
        entry_ts = now_ts() - 7200
    s = 0.01
    k_min, k_max = bin_bounds(R0, s)
    L = dlmm_L_for_capital(CAPITAL_SOL, R0, s, k_min, k_max)
    x0, y0 = dlmm_bin_amounts(L, R0, R0, s, k_min, k_max)
    seg = {"from_ts": entry_ts, "R0": R0, "Pa": (1 - LOW_PCT) * R0,
           "Pb": (1 + HIGH_PCT) * R0, "k_min": k_min, "k_max": k_max,
           "L": L}
    return {
        "pool": "TESTPOOL1111111111111111111111111111111111",
        "mint": "TESTMINT1111111111111111111111111111111111",
        "symbol": "TEST", "bin_step_bps": 100, "base_factor": 20000,
        "protocol_share": 1000, "base_fee": 0.02, "fee_rate_lp": fee,
        "fee_method": "calibrated_onchain", "fee_share": 0.0001,
        "capital_sol": CAPITAL_SOL, "s": s, "entry_ts": entry_ts,
        "entry_time_wib": "2026-11-17T00:00:00+07:00",
        "entry_token_usd": R0 * 75.0, "entry_sol_usd": 75.0,
        "entry_price_sol": R0, "entry_reserve_usd": 140000.0,
        "entry_vol_m30_usd": 5000.0, "segments": [seg], "repositions": [],
        "hx0": x0, "hy0": y0, "x0": x0, "y0": y0,
        "fees_sol": 0.0, "gas_sol": GAS_SOL, "repos_count": 0,
        "below_hours": 0.0, "in_range_hours": 0.0, "hours_held": 0.0,
        "pending_break": None, "last_fee_hour_ts": entry_ts,
        "prev_manage_ts": None, "last_manage_ts": entry_ts,
    }


def _tick(pos, ts, ratio, vol_h1=100000.0, sol_usd=75.0):
    R = pos["entry_price_sol"] * ratio
    return {"ts": ts, "R": R, "token_usd": R * sol_usd,
            "vol_h1_usd": vol_h1}


def selftest():
    """Uji offline runner. Semua harus PASS sebelum dipakai live."""
    global LP_DIR
    import fnmatch
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {name} {detail}")

    print("== M2 runner selftest ==")
    # 0. harness selftest (11 cek bin math + exit hourly)
    sys.path.insert(0, LP_DIR)
    import paper_lp_dlmm
    rc = paper_lp_dlmm.selftest()
    check("harness_selftest_11", rc == 0, f"-> rc={rc}")

    # 1. bin math vs harness (impor langsung, bukan tulis ulang)
    s = 0.01
    P0 = 0.025
    k_min, k_max = bin_bounds(P0, s)
    L = dlmm_L_for_capital(0.1625, P0, s, k_min, k_max)
    x0, y0 = dlmm_bin_amounts(L, P0, P0, s, k_min, k_max)
    check("bin_math_sol_share_94pct",
          0.90 < y0 / (x0 * P0 + y0) < 0.97,
          f"-> SOL {100*y0/(x0*P0+y0):.1f}%")
    check("bin_math_bins_97", k_max - k_min + 1 == 97)

    # 2. decode LbPair dari fixture sintetis (nilai STANK terverifikasi)
    raw = bytearray(904)
    raw[0:8] = bytes([33, 11, 49, 98, 181, 101, 177, 13])
    struct.pack_into("<H", raw, 8, 20000)     # base_factor
    struct.pack_into("<H", raw, 32, 1000)     # protocol_share
    raw[34] = 0                                # power factor
    struct.pack_into("<i", raw, 48, -407)     # index_reference
    struct.pack_into("<i", raw, 76, -407)     # active_id
    struct.pack_into("<H", raw, 80, 100)      # bin_step
    struct.pack_into("<H", raw, 84, 20000)    # base_factor_seed
    raw[88:120] = _b58decode("5wsjHxT5nW5jQuVupXUNnYszF3WoWCfGGk9LMcsCJzY8")
    raw[120:152] = _b58decode(SOL_MINT)
    lb = decode_lbpair(bytes(raw))
    check("lbpair_decode_stank",
          lb is not None and lb["bin_step"] == 100
          and lb["base_factor"] == 20000 and lb["protocol_share"] == 1000
          and abs(lb["fee_rate_lp"] - 0.018) < 1e-9
          and lb["active_id"] == -407
          and lb["token_x_mint"] == "5wsjHxT5nW5jQuVupXUNnYszF3WoWCfGGk9LMcsCJzY8"
          and lb["token_y_mint"] == SOL_MINT
          and lb["cross_active_eq_idxref"] and lb["cross_seed_eq_factor"],
          f"-> fee_lp={lb['fee_rate_lp'] if lb else None}")
    check("lbpair_decode_bad_len", decode_lbpair(bytes(100)) is None)
    check("lbpair_decode_bad_disc",
          decode_lbpair(bytes(bytearray(904))) is None)

    # 3. kalibrasi fee (angka sintetis, hitung tangan)
    bins = {5: {"amount_x": 0, "amount_y": 27_000_000_000,
                "price_u128": int(0.01742 * 2**64), "liq": 6_090_000_000_000_000_000_000_000_000_000},
            6: {"amount_x": 0, "amount_y": 1,
                "price_u128": int(0.01742 * 1.01 * 2**64), "liq": 1}}
    # L harness 80.71 (STANK) -> share = L_raw*w/amount_y
    share, det = calibrate_fee_share(bins, 5, 100, 80.71, 6)
    w_exp = math.sqrt(0.01742 * 1.01) - math.sqrt(0.01742)
    share_exp = 80.71 * 10**7.5 * w_exp / 27_000_000_000
    check("fee_calibration_formula",
          share is not None and abs(share - share_exp) / share_exp < 1e-6,
          f"-> share={share:.3e} (ekspektasi {share_exp:.3e})")
    check("fee_calibration_empty_bin",
          calibrate_fee_share({5: {"amount_x": 0, "amount_y": 0,
                                   "price_u128": 1, "liq": 1}},
                              5, 100, 80.71, 6)[0] is None)
    # harga bin: raw -> human (bukti live STANK 17 Nov)
    p_stank = bin_price_human(int(0.01742612682573299 * 2**64), 6)
    check("bin_price_human_stank",
          abs(p_stank - 1.742612682573299e-05) / 1.742612682573299e-05 < 1e-9,
          f"-> {p_stank:.6e} SOL/token")
    check("bin_price_human_dec9",
          abs(bin_price_human(int(0.0108 * 2**64), 9) - 0.0108) < 1e-12)

    # 4. cabang exit — grace (5 mnt pertama tidak ada exit)
    pos = _test_pos()
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 60, 0.10))
    check("exit_grace_5min", (a, r) == ("hold", None), f"-> {a}/{r}")

    # 5. SL crash -> sl_pnl atau sl_price
    pos = _test_pos()
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 3600, 0.15))
    check("exit_sl_crash", a == "close" and r in ("sl_pnl_-50pct",
                                                  "sl_price_-80pct"),
          f"-> {a}/{r}")

    # 6. below-range + vol rendah >4 jam
    pos = _test_pos()
    a = r = None
    for i in range(1, 20):
        a, r = evaluate_exits(
            pos, _tick(pos, pos["entry_ts"] + i * 900, 0.35, vol_h1=100.0))
        if a == "close":
            break
    check("exit_below_range_low_vol",
          (a, r) == ("close", "below_range_low_vol"),
          f"-> {a}/{r} jam_below={pos['below_hours']:.2f}")

    # 7. below-range tapi vol tinggi -> TIDAK tutup
    pos = _test_pos()
    a = r = None
    for i in range(1, 20):
        a, r = evaluate_exits(
            pos, _tick(pos, pos["entry_ts"] + i * 900, 0.35,
                       vol_h1=100000.0))
    check("exit_below_range_high_vol_hold",
          (a, r) == ("hold", None), f"-> {a}/{r}")

    # 8. tembus atas -> tunggu -> reposisi (maks 2x), baseline TETAP
    pos = _test_pos()
    hx0, hy0 = pos["hx0"], pos["hy0"]
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 3600, 1.20))
    check("exit_break_wait", (a, r) == ("hold", None)
          and pos["pending_break"] is not None, f"-> {a}/{r}")
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 4500, 1.20))
    check("exit_break_reposition", (a, r) == ("reposition", None)
          and pos["repos_count"] == 1, f"-> {a}/{r} repos={pos['repos_count']}")
    check("hodl_baseline_fix_reposition",
          pos["hx0"] == hx0 and pos["hy0"] == hy0,
          "-> hx0/hy0 tidak berubah sesudah reposisi")
    check("reposition_gas", abs(pos["gas_sol"] - 2 * GAS_SOL) < 1e-12,
          f"-> gas={pos['gas_sol']}")

    # 9. tembus atas + pnl >=0.5% -> break_above_tp
    pos = _test_pos()
    pos["fees_sol"] = 0.0015  # fee terakrual dorong pnl >0.5%
    evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 3600, 1.10))
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 4500, 1.10))
    check("exit_break_above_tp", (a, r) == ("close", "break_above_tp"),
          f"-> {a}/{r}")

    # 10. tembus atas + repos habis (2x) -> break_above_max_repos
    pos = _test_pos()
    pos["repos_count"] = 2
    evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 3600, 1.20))
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 4500, 1.20))
    check("exit_break_max_repos",
          (a, r) == ("close", "break_above_max_repos"), f"-> {a}/{r}")

    # 11. TP +8% (fee) + cross-check lolos / gagal / re-read gagal
    pos = _test_pos()
    pos["fees_sol"] = 0.0135  # ~8.3% dari modal
    t = _tick(pos, pos["entry_ts"] + 3600, 1.00)
    t["crosscheck_R"] = pos["entry_price_sol"] * 1.00
    a, r = evaluate_exits(pos, t)
    check("exit_tp_8pct", (a, r) == ("close", "tp_8pct"), f"-> {a}/{r}")
    pos = _test_pos()
    pos["fees_sol"] = 0.0135
    t = _tick(pos, pos["entry_ts"] + 3600, 1.00)
    t["crosscheck_R"] = pos["entry_price_sol"] * 0.90  # harga jatuh
    a, r = evaluate_exits(pos, t)
    check("exit_tp_crosscheck_fail_hold", (a, r) == ("hold", None),
          f"-> {a}/{r}")
    pos = _test_pos()
    pos["fees_sol"] = 0.0135
    t = _tick(pos, pos["entry_ts"] + 3600, 1.00)
    t["crosscheck_R"] = False  # re-read gagal
    a, r = evaluate_exits(pos, t)
    check("exit_tp_reread_fail_hold", (a, r) == ("hold", None),
          f"-> {a}/{r}")

    # 12. max hold 48 jam
    pos = _test_pos()
    a, r = evaluate_exits(pos, _tick(pos, pos["entry_ts"] + 49 * 3600, 1.00))
    check("exit_max_hold_48h", (a, r) == ("close", "max_hold_48h"),
          f"-> {a}/{r}")

    # 13. akrual fee: 2 jam lengkap, tanpa double-count
    pos = _test_pos()
    candles = {pos["entry_ts"] + 3600: {"token_usd": 1.875,
                                        "volume_usd": 100000.0},
               pos["entry_ts"] + 7200: {"token_usd": 1.875,
                                        "volume_usd": 100000.0}}
    sol_h = {pos["entry_ts"] + 3600: 75.0, pos["entry_ts"] + 7200: 75.0}
    fee, n = accrue_fees(pos, candles, sol_h, 140000.0,
                         pos["entry_ts"] + 10800)
    exp = 2 * 100000.0 * 0.018 * 0.0001 / 75.0
    check("fee_accrual_2h", n == 2 and abs(fee - exp) < 1e-9,
          f"-> fee={fee:.6f} (ekspektasi {exp:.6f})")
    fee2, n2 = accrue_fees(pos, candles, sol_h, 140000.0,
                           pos["entry_ts"] + 10800)
    check("fee_no_double_count", n2 == 0 and fee2 == 0.0,
          f"-> n2={n2} fee2={fee2}")
    # fee proxy path
    pos2 = _test_pos()
    pos2["fee_method"] = "proxy_reserve"
    fee3, n3 = accrue_fees(pos2, candles, sol_h, 140000.0,
                           pos2["entry_ts"] + 10800)
    share_p = 0.1625 * 75.0 / 140000.0
    exp3 = 2 * 100000.0 * 0.018 * share_p / 75.0
    check("fee_accrual_proxy", n3 == 2 and abs(fee3 - exp3) < 1e-9,
          f"-> fee={fee3:.6f} (ekspektasi {exp3:.6f})")

    # 14. close + net vs HODL memakai baseline entry (bukan reposisi)
    pos = _test_pos()
    do_reposition(pos, pos["entry_price_sol"] * 1.20,
                  pos["entry_ts"] + 3600)
    tr = close_position(pos, pos["entry_ts"] + 7200,
                        pos["entry_token_usd"] * 1.20, 75.0, "break_above_tp")
    check("close_net_vs_hodl_baseline",
          abs(tr["net_vs_hodl_sol"]
              - (tr["il_sol"] + tr["fees_sol"] - tr["gas_sol"])) < 1e-12
          and "il_usd" in tr and "pool" in tr,
          f"-> net={tr['net_vs_hodl_sol']:.6f} il_usd={tr['il_usd']:.4f}")
    check("close_exit_ts_gte_challenge",
          tr["exit_ts"] >= 1763134440,  # 14 Nov 2026 20:34 WIB
          f"-> exit_ts={tr['exit_ts']}")

    # 15. nama file cocok glob sync_m2 + satu file per trade
    name = result_filename(tr)
    check("result_filename_glob_dlmm",
          fnmatch.fnmatch(name, "paper_lp_*dlmm*.json"), f"-> {name}")
    check("result_filename_deterministic",
          result_filename(tr) == name)

    # 16. screening legs (sintetis)
    ok_p, legs = screen_pair(
        {"reserve_usd": 100000.0, "market_cap_usd": 1000000.0,
         "vol_m30": 5000.0},
        {"mcap": 1000000.0, "created_at_ms": (now_ts() - 5 * 3600) * 1000},
        now_ts())
    check("screen_pair_pass", ok_p, f"-> {legs}")
    # guard mcap glitch (kasus live TTWO 17 Nov: DS mcap $92, GT $5,39 jt)
    ok_pg, legs_g = screen_pair(
        {"reserve_usd": 100000.0, "market_cap_usd": 5392386.0,
         "vol_m30": 5000.0},
        {"mcap": 92.0, "fdv": 5392386.0,
         "created_at_ms": (now_ts() - 5 * 3600) * 1000},
        now_ts())
    check("screen_pair_mcap_glitch_guard",
          ok_pg and legs_g["mcap_usd"] == 5392386.0
          and legs_g["mcap_source"] == "gt_market_cap",
          f"-> mcap={legs_g['mcap_usd']} src={legs_g['mcap_source']}")
    ok_p2, _ = screen_pair(
        {"reserve_usd": 200000.0, "market_cap_usd": 1000000.0,
         "vol_m30": 5000.0},
        {"mcap": 1000000.0, "created_at_ms": (now_ts() - 5 * 3600) * 1000},
        now_ts())
    check("screen_pair_tvl_fail", not ok_p2)
    ok_r, _ = screen_rugcheck(
        {"totalHolders": 1000, "token": {"mintAuthority": None,
                                         "freezeAuthority": None},
         "token_extensions": {}, "rugged": False, "score_normalised": 5,
         "risks": []})
    check("screen_rugcheck_pass", ok_r)
    ok_r2, _ = screen_rugcheck(
        {"totalHolders": 100, "token": {"mintAuthority": None,
                                        "freezeAuthority": None},
         "token_extensions": {}, "rugged": False})
    check("screen_rugcheck_holders_fail", not ok_r2)
    ok_l, _ = screen_lbpair(
        {"bin_step": 100, "base_factor": 20000, "protocol_share": 1000,
         "base_fee": 0.02, "fee_rate_lp": 0.018, "active_id": -407,
         "token_x_mint": "MINTX", "token_y_mint": SOL_MINT,
         "cross_active_eq_idxref": True, "cross_seed_eq_factor": True},
        "MINTX", 0.000016)
    check("screen_lbpair_pass", ok_l)
    # HOGE live 17 Nov: active != idxref itu NORMAL (diagnostik saja)
    ok_l3, legs_l3 = screen_lbpair(
        {"bin_step": 80, "base_factor": 12500, "protocol_share": 1000,
         "base_fee": 0.01, "fee_rate_lp": 0.009, "active_id": -615,
         "token_x_mint": "MINTX", "token_y_mint": SOL_MINT,
         "cross_active_eq_idxref": False, "cross_seed_eq_factor": True},
        "MINTX", 0.0000087)
    check("screen_lbpair_cross_idxref_info_only",
          ok_l3 and legs_l3["cross_active_eq_idxref"] is False)
    ok_l2, _ = screen_lbpair(
        {"bin_step": 25, "base_factor": 20000, "protocol_share": 1000,
         "base_fee": 0.02, "fee_rate_lp": 0.018, "active_id": -407,
         "token_x_mint": "MINTX", "token_y_mint": SOL_MINT,
         "cross_active_eq_idxref": True, "cross_seed_eq_factor": True},
        "MINTX", 0.000016)
    check("screen_lbpair_binstep_fail", not ok_l2)

    # 17. idempotent close: file + ledger masing-masing sekali
    import tempfile
    tmp = tempfile.mkdtemp(prefix="m2_selftest_")
    old_dir = LP_DIR
    LP_DIR = tmp
    try:
        led = init_ledger()
        pos = _test_pos(entry_ts=1_800_000_000)
        tr = close_position(pos, 1_800_003_600,
                            pos["entry_token_usd"] * 1.01, 75.0, "tp_8pct")
        p1 = finalize_close(led, pos, tr)
        n_files_1 = len(os.listdir(tmp))
        # ulangi close yang sama (simulasi crash antara tulis file & save)
        tr2 = close_position(pos, 1_800_003_600,
                             pos["entry_token_usd"] * 1.01, 75.0, "tp_8pct")
        led["open_position"] = pos  # seolah ledger belum tersimpan
        p2 = finalize_close(led, pos, tr2)
        n_files_2 = len(os.listdir(tmp))
        check("idempotent_close_one_file",
              p1 == p2 and n_files_1 == 1 and n_files_2 == 1,
              f"-> files={n_files_2}")
        check("idempotent_close_one_ledger_entry",
              len(led["closed_trades"]) == 1,
              f"-> closed={len(led['closed_trades'])}")
    finally:
        LP_DIR = old_dir
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print("HASIL SELFTEST M2:", "LOLOS" if ok else "GAGAL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--max-eval", type=int, default=MAX_EVAL_PER_RUN)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(dry_run=args.dry_run, max_eval=args.max_eval)


if __name__ == "__main__":
    sys.exit(main())
