---
id: solana-ingest-watchdog
title: Watchdog daemon ingest Solana (nyalakan ulang bila mati)
enabled: false
owner: goal:model-degen-paper-trading-mandiri
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-14T22:17:39
  every: 2m
timeout_secs: 300
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
WATCHDOG DAEMON INGEST SOLANA — dibuat 2026-11-14 ~22:15 WIB atas perintah user ("Ya, pasang watchdog ingest", keputusan pasca-audit Solana). Tugas: jaga daemon ingest PumpPortal tetap hidup; daemon ini mengisi pools.db yang dipakai discovery M1/M3 (infra_pools) dan screening funnel. Watchdog ini HANYA me-restart daemon bila mati/macet; TIDAK PERNAH mengubah ingest.py, TIDAK PERNAH menjalankan backfill poller, TIDAK PERNAH me-regenerasi candidates.json, TIDAK PERNAH menyentuh cron mesin M1/M3 atau ledger.

MIGRASI SYSTEMD (2026-11-17 ~08:20 WIB, user "Ya, pindahkan ke systemd"): daemon kini jalan sebagai SERVICE SYSTEMD `solana-ingest` (bukan lagi setsid/nohup), model unsolvable-live. Unit kanonik: ~/workspace/solana-trading/infra/solana-ingest.service (salinan di /etc/systemd/system/ HILANG tiap VM diganti — langkah 5c menciptakannya lagi dari kanonik). EnvironmentFile proxy: ~/workspace/solana-trading/infra/proxy.env (token proxy egress BERGANTI TIAP RUN — file ini WAJIB disegarkan dari env run ini sebelum restart, langkah 5b; token dari exec call mati dalam hitungan menit, token dari run agen seperti run watchdog ini tahan lebih lama). Unit memakai Environment=HOME=/home/hatch (WAJIB — service jalan sebagai root, HOME default /root, padahal pool_db.py memakai expanduser("~/workspace/...") untuk pools.db DAN websocket-client terpasang --user di /home/hatch/.local). JANGAN PERNAH kembali menjalankan ingest.py via setsid/nohup/tmux — itu membuat duplikat di luar systemd. Watchdog run 08:14 WIB 17 Nov sudah mengadopsi service ini sebagai restart #42 (PID 8000) sesudah migrasi.

KONTEKS (jangan diubah tanpa perintah baru):
- Daemon mati 2026-11-14 20:45 WIB saat VM restart (boot 13:45 UTC); restart manual 21:45 WIB (PID 15615) dan sejak itu sehat (pools.db 992 baris, ~6,8 token/menit).
- System site-packages TIDAK persisten melewati restart VM — `websocket-client` pernah hilang dan membuat restart crash instan (ModuleNotFoundError). Dependensi sudah dipasang `--user` (1.9.2, persisten di `~`); sebelum restart WAJIB verifikasi `import websocket`, dan bila gagal pasang dulu `python3 -m pip install --user websocket-client`.
- Jalur: skrip ~/workspace/solana-trading/infra/ingest.py; log ~/workspace/solana-trading/infra/ingest.log; DB ~/workspace/solana-trading/infra/pools.db. State watchdog: ~/workspace/solana-trading/infra/ingest-watchdog-state.json (catat last_restart_at, restart_count, last_report_at). Log watchdog: ~/workspace/solana-trading/infra/ingest-watchdog.log.

TIAP RUN (2 menit), urutan cek:
1. Cek service: `systemctl is-active --quiet solana-ingest` DAN MainPID via `systemctl show solana-ingest -p MainPID` DAN kesegaran via pools.db-wal: mtime file pools.db-wal (atau baris NEW di ingest.log). Daemon menulis tiap token baru (~6,8/menit) ke WAL, jadi mtime pools.db-wal <10 menit = segar. JANGAN pakai mtime pools.db utama — dalam mode WAL, mtime file utama hanya bergerak saat checkpoint/close sehingga bisa basi 17+ menit padahal daemon sehat (ini yang dulu salah membunuh PID 2828 yang sehat).
2. Bila service AKTIF dan pools.db-wal segar (<10 menit, atau ada baris NEW di ingest.log <10 menit) → daemon SEHAT → lanjut langkah 4 (cek duplikat), lalu DIAM, jangan lakukan apa pun, jangan kirim pesan.
3. Bila service AKTIF tapi pools.db-wal basi >10 menit DAN tidak ada baris NEW di ingest.log <10 menit → daemon MACET (wedged) → lanjut ke langkah 5 (restart via systemctl; JANGAN kill manual).
4. DUPLIKAT: bila ada proses `infra/ingest.py` yang BUKAN MainPID service (mis. sisa setsid era lama) DAN service sudah terverifikasi sehat (langkah 2) → kill duplikat itu saja, catat ke log watchdog (jangan laporkan ke chat kecuali >30 menit sejak laporan terakhir). JANGAN PERNAH kill MainPID service. Bila service TIDAK sehat, jangan kill duplikat dulu — pulihkan service dulu (langkah 5), duplikat ditangani run berikutnya.
5. Bila service TIDAK AKTIF (inactive/failed) atau MACET (langkah 3) → PULIHKAN VIA SYSTEMD (JANGAN via setsid/nohup/tmux — dilarang, membuat duplikat): (a) verifikasi `python3 -c "import websocket"`; bila gagal, `python3 -m pip install --user websocket-client` lalu verifikasi ulang; (b) segarkan proxy.env dari env run ini: `env | grep -iE '^(https?_proxy|all_proxy|no_proxy)=' > ~/workspace/solana-trading/infra/proxy.env` (bila hasilnya kosong, JANGAN timpa file lama — pakai yang ada); (c) bila file /etc/systemd/system/solana-ingest.service TIDAK ADA (habis VM diganti): salin dari ~/workspace/solana-trading/infra/solana-ingest.service ke /etc/systemd/system/ lalu `systemctl daemon-reload`; (d) `systemctl restart solana-ingest` (atau `start` bila inactive); (e) tunggu 10 detik lalu verifikasi `systemctl is-active` + MainPID hidup via kill -0 + pools.db-wal mtime bergerak maju (atau baris "connected + subscribed" di ingest.log) dalam 60 detik. Bila verifikasi gagal, coba restart SEKALI lagi; bila tetap gagal, catat ke log watchdog dan laporkan ke chat utama.
6. Sesudah restart BERHASIL: catat ke ingest-watchdog-state.json (last_restart_at + hitung restart + PID service). Laporkan ke chat utama HANYA bila last_report_at >30 menit lalu (atau belum pernah lapor): "Daemon ingest Solana mati/macet dan sudah dinyalakan lagi (via systemd, terakhir menulis pools.db jam X)". Bila restart GAGAL → laporkan SEKALI ke chat utama + catat ke log watchdog. Bila restart berhasil tapi laporannya sudah dikirim <30 menit lalu → restart saja, DIAM (jangan spam chat bila daemon terus mati).

LARANGAN: jangan pernah menjalankan ingest.py via setsid/nohup/tmux; jangan pernah spawn daemon kedua selagi service sehat; jangan pernah mengubah ingest.py, pools.db, cron mesin, atau ledger; jangan pernah menyentuh MEMORY.md (observasi ke ingest-watchdog.log + log harian ~/memory/YYYY-MM-DD.md saja).
