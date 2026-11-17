# Perbaikan Infra — impl-1 (koordinator, 14 Nov ~21:47 WIB)

## 1. Restart daemon ingest — DITERAPKAN + terverifikasi
- Masalah: daemon mati sejak VM restart 20:45 WIB; `websocket-client` hilang dari VM baru (system site-packages tidak persisten).
- Perbaikan: `pip install --user --break-system-packages websocket-client` → 1.9.2 terpasang di `~/.local` (persisten). Catatan: pip menolak `--user` tanpa `--break-system-packages` (PEP 668, externally-managed).
- Restart: `nohup python3 ~/workspace/solana-trading/infra/ingest.py >> ingest.log 2>&1 &` (PID 15615). Log: handshake pertama 502 Bad Gateway (transien, nginx PumpPortal), lalu "connected + subscribed (newToken, migration)".
- Bukti: pools.db 780 → 822, newest 2026-11-14T21:47:02+07:00 (segar); token baru mengalir (4gNXcRYD…, PfkwVMD4…, 6VwEyFWJ…).
- Sisa: daemon tetap tanpa watchdog (mati bila VM restart lagi) — watchdog cron TIDAK dibuat di sini (butuh keputusan parent; diusulkan di laporan akhir).

## 2. Backfill poller Jupiter — DITERAPKAN + terverifikasi
- `python3 jupiter_poller.py --iterations 3` → polls 3, fetched 90, new 38, known 52, rate_limited 0. Pools 780 → 821 (sebelum ingest menambah lagi).

## 3. Patch monitor.py — DITERAPKAN + terverifikasi
- Sumber: /tmp/mon-test/monitor_patched.py (kaki B) → diterapkan atomik (cp + mv), py_compile OK.
- Isi: db_freshness() + INGEST STALE (>30 mnt) / FUNNEL STALE (>60 mnt) / HARGA STALE (>120 mnt); error_counts kini hitung sim_no_route + sim_sellback_fail.
- Bukti: `--check` sesudah patch, saat ingest mati: `MONITOR MASALAH | run_terakhir=3mnt_lalu | ingest_stale=60mnt` (sebelumnya palsu SEHAT). Sesudah ingest hidup: `MONITOR SEHAT | run_terakhir=5mnt_lalu`.

## 4. Patch prices.py — DITERAPKAN + terverifikasi
- Sumber: /tmp/prices-test/prices.py (kaki B) → diterapkan atomik, py_compile OK.
- Isi: retry IncompleteRead + HTTPException; fallback curl (--retry 2).
- Bukti: kaki B menguji backfill 1.000 candle OK 37,4 dtk (sebelumnya 3/3 gagal). Verifikasi ulang pasca-terap: py_compile OK + watched_pairs (lihat 5).

## 5. Bug watched_pairs() — DITERAPKAN + terverifikasi
- Masalah: query `status IN ('watch','active')` padahal status DB hanya new/graduated → sumber pools.db selalu kosong.
- Perbaikan: `status IN ('new','graduated')` di ~/workspace/solana-trading/infra/prices.py.
- Bukti: `watched_pairs()` kini mengembalikan 700 pair (sebelumnya 0 dari pools.db).
