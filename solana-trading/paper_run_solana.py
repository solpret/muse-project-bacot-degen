#!/usr/bin/env python3
"""BACOT DEGEN — SOLANA paper trading runner. SIMULATION ONLY.

Pengganti mesin BSC (paper_run.py) sesudah perintah user 14 Nov 2026 ~18:15 WIB:
semua project trading pindah BSC -> Solana. Mesin ini PAPER MURNI:
tidak pernah sign, broadcast, memanggil baw, menyentuh wallet/key, atau
swap nyata. Satu-satunya "eksekusi" adalah penulisan ledger virtual.

Sumber data (gratis, tanpa key):
  - Universe: GeckoTerminal solana new_pools (hal 1-2) + DexScreener
    token-profiles/latest (Solana saja) + infra/candidates.json (funnel,
    bila ada — sumber tambahan, dedupe by pair)
  - Data pair/harga/reserve: GeckoTerminal pool endpoint (fallback DexScreener)
  - Chart: GeckoTerminal OHLCV minute aggregate=5 (logika dump = BSC chart_check)
  - Audit: RugCheck report/summary (PRIMER). GoPlus TIDAK mendukung Solana
    (api.gopluslabs.io chain 101 -> code 2022 "main chain is not supported",
    terverifikasi 14 Nov 2026) -> tidak dipakai.
  - Holder: RugCheck report (totalHolders, topHolders, creator, lockers)
  - Simulasi beli/jual: Jupiter Swap v1 quote API (api.jup.ag/swap/v1/quote).
    Endpoint v6 quote-api.jup.ag TIDAK terjangkau dari VM ini (HTTP 000),
    v1 bekerja (terverifikasi 14 Nov 2026).
  - Skor wallet (bonus info, BUKAN gate): infra/wallet_signal.py bila ada;
    bila modul/file sinyal belum ada -> skor 0, lanjut normal.

Gate entry (SEMUA harus lolos; unverified = BLOCK, fail-closed) — port dari
DEGEN BSC v2, ambang sama, satuan disesuaikan SOL:
  - Pool baru Solana 0-12 jam, pasangan vs SOL
  - Ukuran = min(0.024 SOL, 1% reserve SOL), dust guard 0.004 SOL
  - Simulasi beli (Jupiter SOL->token) out > 0 DAN simulasi jual-balik
    (token->SOL untuk jumlah beli penuh) out > 0
  - Audit RugCheck: report ada, score_normalised <= 30, tanpa risk level
    "danger", mintAuthority null, freezeAuthority null, transferFee 0%,
    rugged False
  - Chart: >= 12 candle 5-menit (histori 60 menit); dump gates BSC
    (drop 15m <= -15% atau drop dari high 60m >= 30%)
  - Holder: totalHolders >= 50, top1 <= 25%, top10 <= 60%,
    creator <= 15% supply
  - Dev teridentifikasi (creator RugCheck non-null)
  - LP: lpLockedPct >= 50% ATAU lockers non-empty (RugCheck)
  - Two-sighting: baseline dicatat di sighting pertama; entry butuh
    holders +10% DAN reserve USD +5% vs baseline di run berikutnya
  - Korelasi: suffix mint / dev sama dengan posisi terbuka -> block
  - Deploy: maks 1 entry baru per run; total exposure <= 30% modal;
    maks 3 posisi terbuka; kill switch ekuitas < 70% modal awal
Exit (sama seperti BSC): stop-loss -15%, take-profit +30%,
chart dump, trailing -15% dari peak, likuiditas collapse > 50%.
Biaya paper: 0.00001 SOL per leg swap (estimasi fee jaringan Solana).

Modal virtual: 0.08 SOL (~$6.06 @ SOL $75.80, harga live 14 Nov 2026).
Setara modal DEGEN BSC 0.010 BNB (~$6.31 @ BNB ~$631). Harga SOL dibaca
live tiap run hanya untuk pelaporan USD; modal tetap 0.08 SOL.

PERBAIKAN 14 Nov 2026 (komponen 5 infra — sim_fail rinci + paralel + integrasi):
  - sim_fail diurai: sim_no_route (Jupiter jawab tapi outAmount kosong/
    tidak ada rute), sim_transport (timeout/HTTP/JSON error),
    sim_sellback_fail (beli OK, jual-balik gagal). Alasan per mint dicatat
    di events seperti alasan lain; total alasan primer tetap = universe.
  - Entry diproses 4 fase: (1) pair_data paralel (4 worker, cache per run),
    (2) simulasi Jupiter paralel (4 worker + limiter 2,0 dtk antar quote —
    batas Jupiter lite 5 call/10 dtk per IP, dipakai bersama semua komponen),
    (3) audit RugCheck paralel (3 worker, sleep 1,5 dtk/call dipertahankan),
    (4) gate berurutan (chart/holder/sighting/v2/korelasi/deploy) dalam
    urutan universe — ambang TIDAK ada yang dilonggarkan.
  - Universe + infra/candidates.json (funnel) bila file ada & valid;
    kandidat infra tanpa created_ts diisi dari pair_data (created_at pool),
    tetap fail-closed bila tak terbaca.
  - Skor wallet dicatat di events (BUY + SKIP pasca-audit bila > 0),
    di posisi ledger, di baseline sighting, dan di rincian kandidat diag —
    TIDAK pernah jadi gate dan TIDAK memblokir token tanpa skor.
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(BASE, "ledger.json")
DIAG_PATH = os.path.join(BASE, "run-diagnostics.jsonl")
LOCK_PATH = os.path.join(BASE, ".run.lock")
INFRA_CANDIDATES_PATH = os.path.join(BASE, "infra", "candidates.json")
WALLET_SIGNALS_PATH = os.path.join(BASE, "wallets", "wallet-signals.json")

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

VIRTUAL_CAPITAL_SOL = 0.08
MAX_POSITION_SOL = 0.024
MAX_OPEN = 3
DAILY_BUDGET_SOL = 0.008  # 10% modal: target profit harian + batas rugi
DUST_MIN_SOL = 0.004
EST_FEE_SOL = 0.00001
RUN_DEADLINE_SECS = 750

MIN_CANDLES = 12
MIN_HOLDERS = 50
MAX_TOP1_PCT = 25.0
MAX_TOP10_PCT = 60.0
MAX_CREATOR_PCT = 15.0
MIN_LP_LOCK_PCT = 50.0
MAX_RUGCHECK_SCORE = 30
MAX_NEW_PER_RUN = 1
MAX_DEPLOY_PCT = 0.30
TRIAL_KILL_DRAWDOWN = 0.30
SIGHTING_GROWTH_HOLDERS = 0.10
SIGHTING_GROWTH_POOL = 0.05
SIGHTING_MAX_AGE_HOURS = 24
MAX_AGE_HOURS = 12

# Paralelisasi (aman, hormati rate limit — lihat _RateLimiter):
POOL_PAIR_WORKERS = 4
POOL_QUOTE_WORKERS = 4
POOL_AUDIT_WORKERS = 3
POOL_UNIVERSE_WORKERS = 4

UA = {"Accept": "application/json", "User-Agent": "solana-paper/1.0"}

_SIM_FAIL_TEXT = {
    "sim_no_route": "Jupiter: tidak ada rute / outAmount kosong",
    "sim_transport": "Jupiter: transport error (timeout/HTTP/JSON)",
    "sim_sellback_fail": "beli OK, jual-balik gagal",
}


class _RateLimiter:
    """Jeda minimum antar panggilan ke satu host, dibagi antar thread.

    Jupiter v1 (api.jup.ag, tier lite): koordinator mencatat batas
    5 call/10 dtk per IP yang dipakai BERSAMA semua komponen infra ->
    interval 2,0 dtk antar quote. GeckoTerminal/DexScreener: jeda kecil
    0,3 dtk untuk menghindari thundering herd saat paralel.
    """

    def __init__(self, min_interval_s):
        self.min_interval = min_interval_s
        self._lock = threading.Lock()
        self._last = 0.0

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            wait = self.min_interval - (now - self._last)
            if wait > 0:
                time.sleep(wait)
                now = time.monotonic()
            self._last = now


_JUP_LIMITER = _RateLimiter(2.0)
_FETCH_LIMITER = _RateLimiter(0.3)


class NoRouteError(RuntimeError):
    """Jupiter menjawab tapi tidak ada rute / outAmount kosong."""


def http_json(url, timeout=30, tries=3):
    """GET JSON dengan retry; fallback curl (lebih tahan terhadap egress flaky)."""
    last_err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 * (attempt + 1))
    # Fallback: curl --retry (terbukti lebih tahan IncompleteRead)
    try:
        out = subprocess.run(
            ["curl", "-s", "-m", str(timeout), "--retry", "2", url],
            capture_output=True, text=True, timeout=timeout + 15,
        )
        if out.stdout.strip():
            return json.loads(out.stdout)
    except Exception as e:  # noqa: BLE001
        last_err = e
    raise RuntimeError(f"GET {url[:80]} gagal: {last_err}")


def diag(record):
    try:
        with open(DIAG_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
            f.flush()
    except Exception:
        pass


def load_ledger():
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH) as f:
            return json.load(f)
    now = datetime.now(WIB)
    return {
        "started_at": now.isoformat(),
        "ends_at": (now + timedelta(days=7)).isoformat(),
        "chain": "solana",
        "virtual_capital_sol": VIRTUAL_CAPITAL_SOL,
        "cash_sol": VIRTUAL_CAPITAL_SOL,
        "positions": [],
        "trades": [],
        "daily": {},
        "sightings": {},
        "sol_price_usd_at_start": None,
    }


def save_ledger(led):
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(led, f, indent=2)
    os.replace(tmp, LEDGER_PATH)


def acquire_lock():
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        try:
            pid = int(open(LOCK_PATH).read().strip())
            os.kill(pid, 0)
            return False
        except Exception:  # noqa: BLE001 - stale lock, steal it
            try:
                os.remove(LOCK_PATH)
            except OSError:
                pass
            return acquire_lock()


def release_lock():
    try:
        os.remove(LOCK_PATH)
    except OSError:
        pass


# ---------------- sumber data ----------------

def sol_price_usd():
    """Harga SOL live via DexScreener; fallback None (pelaporan USD saja)."""
    try:
        d = http_json(
            f"https://api.dexscreener.com/tokens/v1/solana/{SOL_MINT}", timeout=30
        )
        for p in d:
            if p.get("priceUsd"):
                return float(p["priceUsd"])
    except Exception:
        pass
    return None


def gt_pool(pair):
    """Data pair GeckoTerminal: harga USD, reserve USD, umur."""
    _FETCH_LIMITER.acquire()
    d = http_json(
        f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pair}",
        timeout=30,
    )
    a = d["data"]["attributes"]
    created = a.get("pool_created_at")
    created_ts = None
    if created:
        try:
            created_ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            pass
    return {
        "pair": pair,
        "price_usd": float(a["base_token_price_usd"]) if a.get("base_token_price_usd") else None,
        "reserve_usd": float(a["reserve_in_usd"]) if a.get("reserve_in_usd") else 0.0,
        "fdv_usd": float(a["fdv_usd"]) if a.get("fdv_usd") else None,
        "market_cap_usd": float(a["market_cap_usd"]) if a.get("market_cap_usd") else None,
        "volume_usd_h24": None,
        "created_at": created,
        "created_ts": created_ts,
        "name": a.get("name"),
    }


def dexscreener_pair(pair):
    """Fallback data pair via DexScreener (bila GT gagal)."""
    _FETCH_LIMITER.acquire()
    d = http_json(f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}", timeout=30)
    pairs = d.get("pairs") or []
    if not pairs:
        raise RuntimeError("dexscreener: pair tidak ditemukan")
    p = pairs[0]
    created_ts = None
    if p.get("pairCreatedAt"):
        created_ts = datetime.fromtimestamp(p["pairCreatedAt"] / 1000, tz=timezone.utc)
    return {
        "pair": pair,
        "price_usd": float(p["priceUsd"]) if p.get("priceUsd") else None,
        "reserve_usd": float(p.get("liquidity", {}).get("usd") or 0),
        "fdv_usd": float(p["fdv"]) if p.get("fdv") else None,
        "market_cap_usd": float(p["marketCap"]) if p.get("marketCap") else None,
        "volume_usd_h24": float(p.get("volume", {}).get("h24") or 0),
        "created_at": created_ts.isoformat() if created_ts else None,
        "created_ts": created_ts,
        "name": f"{p['baseToken']['symbol']} / {p['quoteToken']['symbol']}",
    }


def pair_data(pair):
    try:
        return gt_pool(pair)
    except Exception as e:  # noqa: BLE001
        try:
            return dexscreener_pair(pair)
        except Exception:
            raise e


_PAIR_CACHE = {}
_PAIR_CACHE_LOCK = threading.Lock()


def pair_data_cached(pair):
    """pair_data + cache per run (thread-safe). Gagal fetch tidak di-cache."""
    with _PAIR_CACHE_LOCK:
        if pair in _PAIR_CACHE:
            return _PAIR_CACHE[pair]
    pd = pair_data(pair)
    with _PAIR_CACHE_LOCK:
        _PAIR_CACHE[pair] = pd
    return pd


def analyze_chart(pair):
    """OHLCV GT 5-menit; logika dump = BSC chart_check (port langsung)."""
    d = http_json(
        "https://api.geckoterminal.com/api/v2/networks/solana/pools/"
        f"{pair}/ohlcv/minute?aggregate=5&limit=12",
        timeout=30,
    )
    rows = d.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
    candles = []
    for row in rows:
        if len(row) < 6:
            continue
        ts, o, h, l, c, v = row[:6]
        if c and c > 0:
            candles.append({"ts": ts, "open": float(o), "high": float(h),
                            "low": float(l), "close": float(c), "volume": float(v)})
    candles.sort(key=lambda k: k["ts"])
    if len(candles) < 2:
        raise RuntimeError("not enough candles")
    last = candles[-1]
    close_now = last["close"]

    def pct_ago(n):
        if len(candles) > n:
            ref = candles[-1 - n]["close"]
            return close_now / ref - 1.0 if ref else 0.0
        return None

    change_15m = pct_ago(3)
    change_60m = pct_ago(11)
    high_60m = max(c["high"] for c in candles)
    drop_from_high = 1.0 - close_now / high_60m if high_60m else 0.0
    dump_flag = False
    dump_reason = None
    if change_15m is not None and change_15m <= -0.15:
        dump_flag = True
        dump_reason = f"drop 15m {change_15m:.1%}"
    elif drop_from_high >= 0.30:
        dump_flag = True
        dump_reason = f"drop from 60m high {drop_from_high:.1%}"
    return {
        "candles": len(candles),
        "change_15m": round(change_15m, 4) if change_15m is not None else None,
        "change_60m": round(change_60m, 4) if change_60m is not None else None,
        "drop_from_high": round(drop_from_high, 4),
        "dump_flag": dump_flag,
        "gate_block": f"chart dump: {dump_reason}" if dump_flag else None,
    }


def jupiter_quote(input_mint, output_mint, amount_base_units):
    """Jupiter Swap v1 quote (tanpa key). Out = base units output mint.

    Limiter 2,0 dtk antar quote (batas lite 5 call/10 dtk per IP, dibagi
    semua komponen). NoRouteError bila Jupiter jawab tanpa rute/outAmount.
    """
    _JUP_LIMITER.acquire()
    url = (
        "https://api.jup.ag/swap/v1/quote?inputMint=" + input_mint
        + "&outputMint=" + output_mint
        + "&amount=" + str(int(amount_base_units))
        + "&slippageBps=50"
    )
    d = http_json(url, timeout=30)
    out = d.get("outAmount")
    if out is None:
        raise NoRouteError("jupiter: no route / no outAmount")
    out_int = int(out)
    if out_int <= 0:
        raise NoRouteError("jupiter: outAmount 0 (tidak ada rute usable)")
    return out_int, d


def simulate_roundtrip(size_sol, mint):
    """Simulasi beli + jual-balik via Jupiter v1.

    Return (buy_out_base, sell_back_lamports, fail_reason|None).
    fail_reason: 'sim_no_route' | 'sim_transport' | 'sim_sellback_fail'.
    """
    try:
        buy_out_base, _ = jupiter_quote(SOL_MINT, mint, int(size_sol * 1e9))
    except NoRouteError:
        return 0, 0, "sim_no_route"
    except Exception:  # noqa: BLE001 - timeout/HTTP/JSON error
        return 0, 0, "sim_transport"
    if buy_out_base <= 0:
        return 0, 0, "sim_no_route"
    try:
        sell_back_lamports, _ = jupiter_quote(mint, SOL_MINT, buy_out_base)
    except Exception:  # noqa: BLE001 - beli OK, jual-balik gagal (alasan apa pun)
        return buy_out_base, 0, "sim_sellback_fail"
    if sell_back_lamports <= 0:
        return buy_out_base, 0, "sim_sellback_fail"
    return buy_out_base, sell_back_lamports, None


def rugcheck_report(mint):
    """RugCheck full report. Sleep 1.5 dtk sesudahnya (rate limit)."""
    try:
        d = http_json(f"https://api.rugcheck.xyz/v1/tokens/{mint}/report", timeout=30)
    finally:
        time.sleep(1.5)
    if isinstance(d, dict) and d.get("error"):
        raise RuntimeError(f"rugcheck: {d['error']}")
    return d


def rugcheck_summary(mint):
    try:
        d = http_json(
            f"https://api.rugcheck.xyz/v1/tokens/{mint}/report/summary", timeout=30
        )
    finally:
        time.sleep(1.0)
    if isinstance(d, dict) and d.get("error"):
        raise RuntimeError(f"rugcheck summary: {d['error']}")
    return d


# ---------------- gate ----------------

def audit_gate(report, summary):
    """Audit RugCheck. Return block reason atau None."""
    score = report.get("score_normalised")
    if score is None:
        score = summary.get("score_normalised")
    if score is None:
        return "audit: RugCheck tanpa skor (no result)"
    if score > MAX_RUGCHECK_SCORE:
        return f"audit: RugCheck score {score} (> {MAX_RUGCHECK_SCORE})"
    for r in report.get("risks", []) or []:
        if r.get("level") == "danger":
            return f"audit: risk danger '{r.get('name')}'"
    tok = report.get("token", {}) or {}
    if tok.get("mintAuthority") is not None:
        return "audit: mintAuthority masih ada (bisa mint tak terbatas)"
    if tok.get("freezeAuthority") is not None:
        return "audit: freezeAuthority masih ada (bisa freeze wallet)"
    if report.get("rugged") is True:
        return "audit: rugged=True"
    tf = report.get("transferFee") or {}
    if isinstance(tf, dict) and float(tf.get("pct") or 0) > 0:
        return f"audit: transferFee {tf.get('pct')}% (> 0)"
    return None


def holder_analysis(report, summary):
    """Ringkasan holder + LP dari RugCheck. Return dict + gate_block."""
    th = report.get("topHolders", []) or []
    top1 = float(th[0].get("pct", 0)) if th else 0.0
    top10 = round(sum(float(h.get("pct", 0)) for h in th[:10]), 2)
    total_holders = report.get("totalHolders") or 0
    tok = report.get("token", {}) or {}
    supply = tok.get("supply")
    creator = report.get("creator")
    creator_pct = None
    if creator and report.get("creatorBalance") is not None and supply:
        try:
            creator_pct = float(report["creatorBalance"]) / float(supply) * 100.0
        except (TypeError, ValueError, ZeroDivisionError):
            creator_pct = None
    lockers = report.get("lockers") or {}
    lp_locked_pct = summary.get("lpLockedPct")
    if lp_locked_pct is None:
        lp_locked_pct = 0.0
    lp_source = "summary"
    if float(lp_locked_pct) <= 0:
        # Fallback (disetujui user 14 Nov ~18:58 WIB): ringkasan RugCheck
        # kadang 0 padahal LP market utama burned 100% (kasus Rex/STOKE,
        # summary 0 saat dites koordinator 19:00 WIB, per-market 100%).
        # Hanya bila summary 0: pakai max lpLockedPct per-market dari
        # full report. Di luar kasus ini gate tidak berubah.
        per_market = []
        for m in report.get("markets") or []:
            lp = (m or {}).get("lp") or {}
            try:
                per_market.append(float(lp.get("lpLockedPct") or 0))
            except (TypeError, ValueError):
                pass
        if per_market:
            lp_locked_pct = max(per_market)
            lp_source = "per_market"
    lp_ok = float(lp_locked_pct) >= MIN_LP_LOCK_PCT or len(lockers) > 0
    gate_block = None
    if total_holders < MIN_HOLDERS:
        gate_block = f"holder: hanya {total_holders} holder (<{MIN_HOLDERS})"
    elif top1 > MAX_TOP1_PCT:
        gate_block = f"holder: top1 {top1:.1f}% (>{MAX_TOP1_PCT}%)"
    elif top10 > MAX_TOP10_PCT:
        gate_block = f"holder: top10 {top10:.1f}% (>{MAX_TOP10_PCT}%)"
    elif creator_pct is not None and creator_pct > MAX_CREATOR_PCT:
        gate_block = f"holder: creator {creator_pct:.1f}% (>{MAX_CREATOR_PCT}%)"
    elif not lp_ok:
        gate_block = (
            f"LP: locked {float(lp_locked_pct):.1f}% <50% dan tidak ada locker"
        )
    return {
        "holder_count": total_holders,
        "top1_pct": round(top1, 2),
        "top10_pct": top10,
        "creator": creator,
        "creator_pct": round(creator_pct, 2) if creator_pct is not None else None,
        "lp_locked_pct": round(float(lp_locked_pct), 2),
        "lp_source": lp_source,
        "lockers": len(lockers),
        "decimals": tok.get("decimals"),
        "gate_block": gate_block,
    }


def v2_data_gate_block(holders, chart):
    if chart["candles"] < MIN_CANDLES:
        return f"chart: hanya {chart['candles']} candle (<{MIN_CANDLES})"
    if holders.get("holder_count", 0) < MIN_HOLDERS:
        return f"holder: hanya {holders.get('holder_count', 0)} holder (<{MIN_HOLDERS})"
    if not holders.get("creator"):
        return "dev tidak teridentifikasi (creator RugCheck kosong)"
    if holders.get("gate_block") and "LP:" in holders["gate_block"]:
        return holders["gate_block"]
    return None


def v2_subgate_fails(holders, chart):
    fails = []
    if chart["candles"] < MIN_CANDLES:
        fails.append("candle")
    if holders.get("holder_count", 0) < MIN_HOLDERS:
        fails.append("holders")
    if not holders.get("creator"):
        fails.append("dev")
    if holders.get("gate_block") and "LP:" in holders["gate_block"]:
        fails.append("lp")
    return fails


def correlation_block(led, mint, holders):
    suffix = mint[-4:].lower()
    devs = {holders.get("creator")} - {None}
    for pos in led["positions"]:
        if pos["token"][-4:].lower() == suffix:
            return f"korelasi: suffix {suffix} sama dengan posisi terbuka"
        pos_devs = {pos.get("dev_owner")} - {None}
        if devs & pos_devs:
            return "korelasi: dev sama dengan posisi terbuka"
    return None


def sighting_block(led, mint, holders, reserve_usd):
    """Two-sighting growth confirmation (port BSC)."""
    sightings = led.setdefault("sightings", {})
    key = mint.lower()
    now = datetime.now(WIB)
    for k, entry in list(sightings.items()):
        first_seen = entry.get("first_seen")
        if not first_seen:
            continue
        try:
            seen_at = datetime.fromisoformat(first_seen)
            if (now - seen_at).total_seconds() > SIGHTING_MAX_AGE_HOURS * 3600:
                del sightings[k]
        except ValueError:
            del sightings[k]
    base = sightings.get(key)
    if base is None:
        if holders.get("holder_count", 0) == 0:
            return "sighting pertama: holder_count 0, baseline tidak dicatat"
        sightings[key] = {
            "holders": holders.get("holder_count", 0),
            "reserve_usd": reserve_usd,
            "first_seen": now.isoformat(),
        }
        return "sighting pertama: baseline dicatat, menunggu konfirmasi pertumbuhan"
    h0 = base.get("holders", 0) or 0
    r0 = base.get("reserve_usd", 0) or 0
    h_now = holders.get("holder_count", 0)
    h_growth = (h_now / h0 - 1.0) if h0 else 0.0
    r_growth = (reserve_usd / r0 - 1.0) if r0 else 0.0
    if h_growth >= SIGHTING_GROWTH_HOLDERS and r_growth >= SIGHTING_GROWTH_POOL:
        return None
    return (
        f"konfirmasi pertumbuhan belum terpenuhi "
        f"(holders {h_growth:+.0%} butuh +10%, reserve {r_growth:+.0%} butuh +5%)"
    )


# ---------------- wallet signal (bonus info, BUKAN gate) ----------------

def load_wallet_module():
    """Import infra/wallet_signal.py bila ada.

    Return (modul, signals) atau (None, None) bila modul/file belum ada —
    pemanggil tetap jalan dengan skor 0.
    """
    try:
        infra_dir = os.path.join(BASE, "infra")
        if infra_dir not in sys.path:
            sys.path.insert(0, infra_dir)
        import wallet_signal  # noqa: PLC0415 - import opsional, toleran
        sig = wallet_signal.load_signals(WALLET_SIGNALS_PATH)
        return wallet_signal, sig
    except Exception:  # noqa: BLE001 - modul belum ada / load gagal
        return None, None


def wallet_score_for(ws_mod, signals, mint, report):
    """Skor wallet 0-100 (bonus info). Selalu kembalikan dict; gagal -> 0.

    Memakai antarmuka komponen 3: score_mint(mint, top_holders, creator,
    signals=...). TIDAK pernah raise, TIDAK pernah memblokir.
    """
    empty = {"score": 0, "hits": [], "reasons": ["skor wallet tidak tersedia"],
             "cabal_flag": False, "categories_hit": [],
             "signals_available": False}
    if ws_mod is None:
        return empty
    try:
        res = ws_mod.score_mint(mint, report.get("topHolders") or [],
                                report.get("creator"), signals=signals)
        if isinstance(res, dict) and "score" in res:
            return res
        if isinstance(res, (int, float)):
            out = dict(empty)
            out["score"] = int(res)
            return out
        return empty
    except TypeError:
        # Varian tanda tangan lain (defensif): score_mint(signals, mint, ...)
        try:
            res = ws_mod.score_mint(signals, mint, report.get("topHolders") or [],
                                    report.get("creator"))
            if isinstance(res, dict) and "score" in res:
                return res
        except Exception:  # noqa: BLE001
            pass
        return empty
    except Exception:  # noqa: BLE001
        return empty


# ---------------- universe ----------------

def load_infra_candidates():
    """Kandidat funnel dari infra/candidates.json (komponen 2).

    Skema: {"generated_wib", "candidates": [{"mint","pair","score","lane",
    "first_seen_wib","graduated_at","metrics","reasons"}]}.
    File belum ada / rusak / kosong -> [] (lanjut normal tanpa error).
    created_ts diisi belakangan dari pair_data (created_at pool).
    """
    try:
        with open(INFRA_CANDIDATES_PATH) as f:
            d = json.load(f)
        out = []
        for c in d.get("candidates") or []:
            if not isinstance(c, dict):
                continue
            mint = c.get("mint")
            pair = c.get("pair")
            if not mint or not pair:
                continue
            out.append({
                "pair": pair,
                "mint": mint,
                "created_ts": None,
                "source": "infra_funnel",
                "infra_score": c.get("score"),
                "infra_lane": c.get("lane"),
            })
        return out
    except Exception:  # noqa: BLE001 - file belum ada / rusak
        return []


def _gt_new_pools_entry(item):
    pid = item.get("id", "")
    if not pid.startswith("solana_"):
        return None
    pair = pid[len("solana_"):]
    rel = (item.get("relationships", {}) or {}).get("base_token", {}) or {}
    mint = (rel.get("data", {}) or {}).get("id", "")
    if mint.startswith("solana_"):
        mint = mint[len("solana_"):]
    quote = ((item.get("relationships", {}) or {}).get("quote_token", {}) or {}).get("data", {}) or {}
    quote_id = quote.get("id", "")
    if quote_id != "solana_" + SOL_MINT:
        return None  # hanya pasangan vs SOL
    created = (item.get("attributes", {}) or {}).get("pool_created_at")
    created_ts = None
    if created:
        try:
            created_ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            pass
    return {"pair": pair, "mint": mint,
            "created_ts": created_ts, "source": "gt_new_p"}


def _gt_new_pools_page(page):
    try:
        _FETCH_LIMITER.acquire()
        d = http_json(
            "https://api.geckoterminal.com/api/v2/networks/solana/new_pools"
            f"?page={page}",
            timeout=30,
        )
        entries = []
        for item in d.get("data", []) or []:
            e = _gt_new_pools_entry(item)
            if e is not None:
                e["source"] = f"gt_new_p{page}"
                entries.append(e)
        return entries
    except Exception:  # noqa: BLE001 - halaman gagal, halaman lain tetap jalan
        return []


def _ds_token_pairs(mint):
    try:
        _FETCH_LIMITER.acquire()
        return (mint, http_json(
            f"https://api.dexscreener.com/tokens/v1/solana/{mint}", timeout=30))
    except Exception:  # noqa: BLE001
        return (mint, None)


def fetch_universe():
    """GT new_pools hal 1-2 + DexScreener token-profiles latest (Solana)
    + infra/candidates.json (funnel, bila ada).

    Return list dict {pair, mint, created_ts, source, [infra_score, infra_lane]}.
    Dedupe by pair; kandidat infra yang pair-nya sudah ada memperkaya entri
    yang ada (infra_score/lane) tanpa duplikasi.
    """
    universe = {}
    # GT new_pools hal 1-2 paralel
    with ThreadPoolExecutor(max_workers=2) as ex:
        for entries in ex.map(_gt_new_pools_page, (1, 2)):
            for e in entries:
                universe[e["pair"]] = e
    # DexScreener token-profiles latest (Solana) — lookup pair per token paralel
    try:
        _FETCH_LIMITER.acquire()
        d = http_json("https://api.dexscreener.com/token-profiles/latest/v1", timeout=30)
        profile_mints = []
        for prof in d or []:
            if prof.get("chainId") != "solana":
                continue
            mint = prof.get("tokenAddress")
            if mint:
                profile_mints.append(mint)
        with ThreadPoolExecutor(max_workers=POOL_UNIVERSE_WORKERS) as ex:
            token_pairs = dict(ex.map(_ds_token_pairs, profile_mints))
        for mint in profile_mints:
            pairs = token_pairs.get(mint)
            if not pairs:
                continue
            best = None
            for p in pairs or []:
                if p.get("chainId") != "solana":
                    continue
                if p.get("quoteToken", {}).get("address") != SOL_MINT:
                    continue
                liq = float((p.get("liquidity") or {}).get("usd") or 0)
                if best is None or liq > best[0]:
                    best = (liq, p)
            if best is None:
                continue
            p = best[1]
            pair = p["pairAddress"]
            if pair in universe:
                continue
            created_ts = None
            if p.get("pairCreatedAt"):
                created_ts = datetime.fromtimestamp(p["pairCreatedAt"] / 1000, tz=timezone.utc)
            universe[pair] = {"pair": pair, "mint": mint,
                              "created_ts": created_ts, "source": "dex_profiles"}
    except Exception:  # noqa: BLE001 - DexScreener gagal, GT tetap dipakai
        pass
    # Funnel infra (komponen 2) — sumber tambahan, dedupe by pair
    for ic in load_infra_candidates():
        if ic["pair"] in universe:
            universe[ic["pair"]]["infra_score"] = ic.get("infra_score")
            universe[ic["pair"]]["infra_lane"] = ic.get("infra_lane")
            universe[ic["pair"]]["infra_source"] = True
        else:
            universe[ic["pair"]] = ic
    return list(universe.values())


# ---------------- main ----------------

def main():
    os.makedirs(BASE, exist_ok=True)
    if not acquire_lock():
        print(json.dumps({"ok": False, "error": "already running"}))
        return
    run_start = time.monotonic()
    led = load_ledger()
    led.setdefault("initial_capital_sol", VIRTUAL_CAPITAL_SOL)
    led.setdefault("sightings", {})
    today = datetime.now(WIB).strftime("%Y-%m-%d")
    day = led["daily"].setdefault(today, {"realized_sol": 0.0, "entries": 0, "exits": 0})
    events = []
    try:
        sol_price = sol_price_usd()
    except Exception:
        sol_price = None
    if sol_price and not led.get("sol_price_usd_at_start"):
        led["sol_price_usd_at_start"] = sol_price
    if sol_price:
        events.append(f"SOL ${sol_price:.2f} (DexScreener)")

    # --- exits dulu: re-price posisi terbuka ---
    still_open = []
    for pos in led["positions"]:
        try:
            pd = pair_data(pos["pair"])
            price_now = pd["price_usd"]
            price_entry = pos["entry_price_usd"]
            ratio = (price_now / price_entry) if price_now and price_entry else 0
            # simulasi jual via Jupiter (token -> SOL, jumlah penuh)
            sell_out_lamports, _ = jupiter_quote(pos["token"], SOL_MINT, pos["tokens_base"])
            cur_value = sell_out_lamports / 1e9
            ratio = cur_value / pos["entry_sol"] if pos["entry_sol"] else ratio
            collapsed = pd["reserve_usd"] < 0.5 * pos["entry_reserve_usd"]
            peak = pos.get("peak_ratio", ratio)
            if ratio > peak:
                peak = ratio
                pos["peak_ratio"] = peak
            try:
                chart_dump = bool(analyze_chart(pos["pair"])["dump_flag"])
            except Exception:  # noqa: BLE001 - chart unreadable, price exits only
                chart_dump = False
            reason = None
            if ratio <= 0.85:
                reason = "stop_loss_-15%"
            elif ratio >= 1.30:
                reason = "take_profit_+30%"
            elif chart_dump:
                reason = "chart_dump_fast"
            elif peak > 1.0 and ratio <= 0.85 * peak:
                reason = "trailing_-15%_from_peak"
            elif collapsed:
                reason = "liquidity_collapse_>50%"
            if reason:
                proceeds = cur_value - EST_FEE_SOL
                realized = proceeds - pos["entry_sol"] - pos["buy_fee_sol"]
                led["cash_sol"] += proceeds
                day["realized_sol"] += realized
                day["exits"] += 1
                led["trades"].append({
                    "type": "SELL", "token": pos["token"], "pair": pos["pair"],
                    "reason": reason, "entry_sol": pos["entry_sol"],
                    "exit_sol": cur_value, "realized_sol": realized,
                    "time": datetime.now(WIB).isoformat(),
                    "x_status": pos.get("x_status", "belum_dikonfirmasi"),
                })
                events.append(f"SELL {pos['token'][:12]} reason={reason} realized={realized:.6f} SOL")
                continue
            pos["last_value_sol"] = cur_value
            still_open.append(pos)
        except Exception as e:  # noqa: BLE001 - stuck, never force-sold
            pos["stuck_reason"] = str(e)[:120]
            still_open.append(pos)
            events.append(f"STUCK {pos['token'][:12]}: {str(e)[:80]}")
    led["positions"] = still_open

    # --- entries ---
    budget_blocked = day["realized_sol"] <= -DAILY_BUDGET_SOL or day["realized_sol"] >= DAILY_BUDGET_SOL
    equity_sol = led["cash_sol"] + sum(float(p.get("last_value_sol") or 0) for p in led["positions"])
    kill_switch = equity_sol < (1 - TRIAL_KILL_DRAWDOWN) * led["initial_capital_sol"]
    if kill_switch:
        events.append(
            f"KILL_SWITCH trial drawdown >30%: equity={equity_sol:.6f} "
            f"cash={led['cash_sol']:.6f} initial={led['initial_capital_sol']:.6f}, no entries"
        )
    reasons = {}
    entries_made = 0
    deadline_hit = False
    universe_n = 0
    infra_n = 0
    infra_enriched = 0
    wallet_signals_available = False
    cand_details = []
    stage_t = {"universe": 0.0, "pair": 0.0, "quote": 0.0, "audit": 0.0,
               "holder": 0.0, "chart": 0.0}
    if not budget_blocked and not kill_switch and len(led["positions"]) < MAX_OPEN:
        ws_mod, ws_signals = load_wallet_module()
        wallet_signals_available = bool(
            ws_signals is not None and getattr(ws_signals, "available", False))

        def _count(reason):
            reasons[reason] = reasons.get(reason, 0) + 1

        def _detail(cand, block, wallet_score=None):
            cand_details.append({
                "mint": cand.get("mint"),
                "pair": cand.get("pair"),
                "source": cand.get("source"),
                "infra_score": cand.get("infra_score"),
                "infra_lane": cand.get("infra_lane"),
                "wallet_score": wallet_score,
                "block": block,
            })

        def _deadline_exceeded():
            return time.monotonic() - run_start > RUN_DEADLINE_SECS

        try:
            _t0 = time.monotonic()
            universe = fetch_universe()
            stage_t["universe"] = time.monotonic() - _t0
        except Exception as e:  # noqa: BLE001
            universe = []
            events.append(f"universe fetch failed: {str(e)[:100]}")
        universe_n = len(universe)
        infra_n = sum(1 for c in universe if c.get("source") == "infra_funnel")
        infra_enriched = sum(1 for c in universe if c.get("infra_source"))
        open_tokens = {p["token"].lower() for p in led["positions"]}
        now_utc = datetime.now(timezone.utc)

        # --- pra-filter: umur (bila created_ts diketahui) + sudah terbuka ---
        # Urutan sama seperti mesin lama: umur dulu, baru already_open.
        pre = []
        for cand in universe:
            mint = cand.get("mint")
            if not mint:
                continue
            cts = cand.get("created_ts")
            if cts is not None:
                age_h = (now_utc - cts).total_seconds() / 3600.0
                if age_h > MAX_AGE_HOURS:
                    _count("age_gt_12h")
                    _detail(cand, "age_gt_12h")
                    continue
            if mint.lower() in open_tokens:
                _count("already_open")
                _detail(cand, "already_open")
                continue
            pre.append(cand)

        # --- FASE 1: pair_data paralel (cache per run) ---
        # Kandidat infra tanpa created_ts: umur diisi dari pair_data di bawah.
        items = []
        if pre and not _deadline_exceeded():
            def _phase1(cand):
                t0 = time.monotonic()
                try:
                    pd = pair_data_cached(cand["pair"])
                    return (cand, pd, None, time.monotonic() - t0)
                except Exception as e:  # noqa: BLE001
                    return (cand, None, str(e)[:80], time.monotonic() - t0)

            with ThreadPoolExecutor(max_workers=POOL_PAIR_WORKERS) as ex:
                p1 = list(ex.map(_phase1, pre))
            for cand, pd, err, dt in p1:
                stage_t["pair"] += dt
                mint = cand["mint"]
                if err is not None:
                    _count("pair_exc")
                    _detail(cand, "pair_exc")
                    events.append(f"SKIP pair {cand['pair'][:12]}: {err}")
                    continue
                cts = cand.get("created_ts") or pd.get("created_ts")
                if cts is None:
                    _count("age_unknown")
                    _detail(cand, "age_unknown")
                    continue
                age_h = (now_utc - cts).total_seconds() / 3600.0
                if age_h > MAX_AGE_HOURS:
                    _count("age_gt_12h")
                    _detail(cand, "age_gt_12h")
                    continue
                if mint.lower() in open_tokens:
                    _count("already_open")
                    _detail(cand, "already_open")
                    continue
                if not pd["price_usd"] or pd["price_usd"] <= 0:
                    _count("no_price")
                    _detail(cand, "no_price")
                    continue
                if sol_price is None:
                    _count("no_sol_price")
                    _detail(cand, "no_sol_price")
                    continue
                sol_reserve = pd["reserve_usd"] / 2.0 / sol_price
                size = min(MAX_POSITION_SOL, 0.01 * sol_reserve)
                if size < DUST_MIN_SOL or size < 2 * EST_FEE_SOL:
                    _count("dust")
                    _detail(cand, "dust")
                    continue
                items.append({"cand": cand, "pd": pd, "size": size})
        elif pre:
            deadline_hit = True
            events.append(f"deadline {RUN_DEADLINE_SECS}s hit sebelum fase pair, saving ledger")

        # --- FASE 2: simulasi Jupiter paralel (limiter 2,0 dtk antar quote) ---
        # sim_fail lama kini terurai: sim_no_route / sim_transport / sim_sellback_fail.
        items2 = []
        if items and not _deadline_exceeded():
            def _phase2(item):
                t0 = time.monotonic()
                buy, sell, fail = simulate_roundtrip(item["size"], item["cand"]["mint"])
                return (item, buy, sell, fail, time.monotonic() - t0)

            with ThreadPoolExecutor(max_workers=POOL_QUOTE_WORKERS) as ex:
                p2 = list(ex.map(_phase2, items))
            for item, buy, sell, fail, dt in p2:
                stage_t["quote"] += dt
                mint = item["cand"]["mint"]
                if fail is not None:
                    _count(fail)
                    _detail(item["cand"], fail)
                    events.append(f"SKIP sim {mint[:12]}: {_SIM_FAIL_TEXT[fail]}")
                    continue
                item["buy_out"] = buy
                item["sell_back"] = sell
                items2.append(item)
        elif items:
            deadline_hit = True
            events.append(f"deadline {RUN_DEADLINE_SECS}s hit sebelum fase simulasi, saving ledger")

        # --- FASE 3: audit RugCheck paralel (sleep 1,5 dtk/call dipertahankan) ---
        items3 = []
        if items2 and not _deadline_exceeded():
            def _phase3(item):
                t0 = time.monotonic()
                try:
                    report = rugcheck_report(item["cand"]["mint"])
                    summary = rugcheck_summary(item["cand"]["mint"])
                    return (item, report, summary, None, time.monotonic() - t0)
                except Exception as e:  # noqa: BLE001
                    return (item, None, None, str(e)[:80], time.monotonic() - t0)

            with ThreadPoolExecutor(max_workers=POOL_AUDIT_WORKERS) as ex:
                p3 = list(ex.map(_phase3, items2))
            for item, report, summary, err, dt in p3:
                stage_t["audit"] += dt
                mint = item["cand"]["mint"]
                if err is not None:
                    _count("audit_exc")
                    _detail(item["cand"], "audit_exc")
                    events.append(f"SKIP audit {mint[:12]}: exception {err}")
                    continue
                audit_block = audit_gate(report, summary)
                if audit_block:
                    _count("audit_skip")
                    _detail(item["cand"], "audit_skip")
                    events.append(f"SKIP audit {mint[:12]}: {audit_block}")
                    continue
                item["report"] = report
                item["summary"] = summary
                items3.append(item)
        elif items2:
            deadline_hit = True
            events.append(f"deadline {RUN_DEADLINE_SECS}s hit sebelum fase audit, saving ledger")

        # --- FASE 4: gate berurutan dalam urutan universe (ambang TIDAK berubah) ---
        for item in items3:
            if _deadline_exceeded():
                deadline_hit = True
                events.append(f"deadline {RUN_DEADLINE_SECS}s hit, saving ledger")
                break
            if entries_made >= MAX_NEW_PER_RUN:
                break
            cand = item["cand"]
            mint = cand["mint"]
            pair = cand["pair"]
            pd = item["pd"]
            report = item["report"]
            summary = item["summary"]
            size = item["size"]
            try:
                # Skor wallet: bonus info (dicatat, BUKAN gate). Dihitung sekali
                # untuk semua kandidat yang lolos audit — tanpa API call tambahan.
                wscore = wallet_score_for(ws_mod, ws_signals, mint, report)
                item["wallet_score"] = wscore["score"]
                _t0 = time.monotonic()
                try:
                    chart = analyze_chart(pair)
                except Exception as e:  # noqa: BLE001
                    _count("chart_skip")
                    _detail(cand, "chart_skip", wscore["score"])
                    events.append(f"SKIP chart {mint[:12]}: {str(e)[:80]}")
                    continue
                finally:
                    stage_t["chart"] += time.monotonic() - _t0
                if chart["gate_block"]:
                    _count("chart_skip")
                    _detail(cand, "chart_skip", wscore["score"])
                    events.append(f"SKIP chart {mint[:12]}: {chart['gate_block']}")
                    continue
                _t0 = time.monotonic()
                holders = holder_analysis(report, summary)
                stage_t["holder"] += time.monotonic() - _t0
                if holders["gate_block"]:
                    _count("holder_gate")
                    _detail(cand, "holder_gate", wscore["score"])
                    events.append(f"SKIP holders {mint[:12]}: {holders['gate_block']}")
                    continue
                # sighting SEBELUM v2 (port fix BSC 2026-11-06)
                sight_block = sighting_block(led, mint, holders, pd["reserve_usd"])
                if mint.lower() in led.get("sightings", {}):
                    led["sightings"][mint.lower()]["wallet_score"] = wscore["score"]
                if sight_block:
                    _count("sighting")
                    _detail(cand, "sighting", wscore["score"])
                    ws_txt = f" wallet_score={wscore['score']}" if wscore["score"] else ""
                    events.append(f"SKIP sighting {mint[:12]}: {sight_block}{ws_txt}")
                    continue
                v2_block = v2_data_gate_block(holders, chart)
                if v2_block:
                    _count("v2_gate")
                    for code in v2_subgate_fails(holders, chart):
                        _count("v2_" + code)
                    _detail(cand, "v2_gate", wscore["score"])
                    events.append(f"SKIP v2 {mint[:12]}: {v2_block}")
                    continue
                corr_block = correlation_block(led, mint, holders)
                if corr_block:
                    _count("correlation")
                    _detail(cand, "correlation", wscore["score"])
                    events.append(f"SKIP correlation {mint[:12]}: {corr_block}")
                    continue
                open_exposure = sum(p["entry_sol"] for p in led["positions"])
                if open_exposure + size > MAX_DEPLOY_PCT * led["initial_capital_sol"]:
                    _count("deploy_cap")
                    _detail(cand, "deploy_cap", wscore["score"])
                    continue
                if size + EST_FEE_SOL > led["cash_sol"]:
                    _count("cash")
                    _detail(cand, "cash", wscore["score"])
                    events.append(f"SKIP cash {mint[:12]}: need {size + EST_FEE_SOL:.6f} have {led['cash_sol']:.6f}")
                    continue
                led["cash_sol"] -= size + EST_FEE_SOL
                day["entries"] += 1
                led["positions"].append({
                    "token": mint,
                    "pair": pair,
                    "entry_sol": size,
                    # FIX AUDIT (14 Nov): fallback ekuitas bila re-price gagal —
                    # posisi ikut ekuitas sebesar size, bukan 0 (kill-switch
                    # tidak false-trip). Jalur normal tidak berubah: loop exit
                    # me-reprice last_value_sol dulu (baris ~900) sebelum
                    # ekuitas dihitung.
                    "last_value_sol": size,
                    "tokens_base": item["buy_out"],
                    "decimals": holders.get("decimals"),
                    "entry_price_usd": pd["price_usd"],
                    "entry_reserve_usd": pd["reserve_usd"],
                    "entry_time": datetime.now(WIB).isoformat(),
                    "buy_fee_sol": EST_FEE_SOL,
                    "x_status": "belum_dikonfirmasi",
                    "holders": holders,
                    "chart": chart,
                    "peak_ratio": 1.0,
                    "dev_owner": holders.get("creator"),
                    "suffix": mint[-4:].lower(),
                    "wallet_score": wscore["score"],
                    "wallet_categories": wscore.get("categories_hit") or [],
                    "infra_score": cand.get("infra_score"),
                    "infra_lane": cand.get("infra_lane"),
                })
                open_tokens.add(mint.lower())
                entries_made += 1
                _detail(cand, "ENTRY", wscore["score"])
                ws_txt = f" wallet_score={wscore['score']}" if wscore["score"] else ""
                infra_txt = ""
                if cand.get("infra_score") is not None:
                    infra_txt = f" infra_score={cand.get('infra_score')} lane={cand.get('infra_lane')}"
                events.append(f"BUY {mint[:12]} size={size:.6f} SOL tokens_base={item['buy_out']}{ws_txt}{infra_txt}")
            except Exception as e:  # noqa: BLE001 - skip pair, keep going
                _count("pair_exc")
                events.append(f"SKIP pair {pair[:12]}: {str(e)[:80]}")
        events.append(
            "universe " + str(universe_n) + " pools: "
            + ", ".join(f"{k}={v}" for k, v in reasons.items())
        )
        diag({
            "time_wib": datetime.now(WIB).isoformat(),
            "elapsed_s": round(time.monotonic() - run_start, 1),
            "deadline_hit": deadline_hit,
            "universe_pools": universe_n,
            "infra_candidates_new": infra_n,
            "infra_candidates_enriched": infra_enriched,
            "wallet_signals_available": wallet_signals_available,
            "reasons": reasons,
            "stage_seconds": {k: round(v, 1) for k, v in stage_t.items()},
            "entries_made": entries_made,
            "sightings": len(led.get("sightings", {})),
            "open_positions": len(led["positions"]),
            "sol_price_usd": sol_price,
            "candidates": cand_details,
        })
    elif budget_blocked:
        events.append(f"daily budget hit: realized={day['realized_sol']:.6f} SOL, no entries")

    save_ledger(led)
    release_lock()
    print(json.dumps({
        "ok": True,
        "cash_sol": round(led["cash_sol"], 6),
        "open": len(led["positions"]),
        "realized_today_sol": round(day["realized_sol"], 6),
        "sol_price_usd": sol_price,
        "events": events,
    }))


if __name__ == "__main__":
    main()
