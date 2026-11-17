---
id: paper-trading-15m
title: BACOT DEGEN — paper trading (simulasi, 15 menit)
enabled: false
owner: goal:model-degen-paper-trading-mandiri
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-05T00:10:49
  every: 15m
timeout_secs: 1500
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
Jalankan mesin BACOT DEGEN (paper trading memecoin, SIMULASI SAJA, tanpa uang asli) lalu laporkan hanya bila ada yang baru.

PERINTAH TIAP RUN:
1. Jalankan: ~/workspace/.abi-venv/bin/python ~/workspace/paper-trading/paper_run.py
2. Baca hasilnya dan ~/workspace/paper-trading/ledger.json.
3. LAPORKAN ke chat utama HANYA bila ada: (a) entry BUY paper baru (token, ukuran BNB virtual, gate yang diloloskan: audit + holder + dev + chart + gate v2: candle ≥12, snapshot holder lengkap ≥50 holder, dev teridentifikasi, LP burn ≥50% atau lock kontrak, konfirmasi pertumbuhan 2-sighting, blok korelasi, cap deploy 30%); (b) exit SELL paper (alasan: stop-loss / take-profit / chart dump / trailing / likuiditas + realized PnL virtual setelah gas); (c) pemblokiran eksekusi dengan alasan BARU yang belum pernah dilaporkan; (d) KILL_SWITCH aktif (drawdown virtual >30%) — laporkan SEKALI. Selain itu DIAM (run rutin tanpa entry/exit baru tidak menghasilkan laporan).
4. Selalu beri label PAPER/VIRTUAL pada setiap angka — jangan pernah sajikan hasil paper sebagai profit/kerugian nyata.

LARANGAN KERAS: jangan pernah menyentuh baw, wallet, approval, sign, swap, atau transaksi nyata apa pun. Mesin ini simulasi murni. Bila script gagal atau mengembalikan "already running" (lock), jangan laporkan ke chat — cukup catat di hasil run. Bila ledger tidak berubah dan tidak ada entry/exit baru, diam.

KONTEKS: BACOT DEGEN BERDIRI SENDIRI — tidak memakai sinyal, state, atau hasil MODAL BACOT apa pun; hasilnya tidak dilaporkan sebagai bagian MODAL BACOT. Trial paper sejak 2026-11-05 (reset setelah siklus 1), DIPERPANJANG sampai 2026-11-19 atas perintah user 2026-11-05 setelah perbaikan terverifikasi, modal virtual 0,010 BNB, maks 1 entry baru per run, maks 0,003 BNB per posisi, total posisi terbuka maks 30% modal. Setelah 2026-11-19, beri tahu user sekali bahwa masa trial habis supaya diputuskan lanjut atau berhenti — jangan perpanjang sendiri.
