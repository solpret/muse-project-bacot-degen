---
id: paper-trading-solana-15m
title: Paper trading Solana (simulasi, 15 menit)
enabled: false
owner: goal:model-degen-paper-trading-mandiri
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-14T18:51:13
  every: 15m
timeout_secs: 900
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PAPER TRADING SOLANA — BACOT DEGEN di Solana (paper only, uang virtual, TIDAK ADA eksekusi live/trade nyata). Disetujui user 14 Nov 2026 ~18:35 WIB (tap "Ya, jalankan paper tiap 15 menit"). Trial 7 hari: 14 Nov 18:20 WIB s.d. 21 Nov 18:20 WIB. Modal virtual 0,08 SOL. Mesin: ~/workspace/solana-trading/paper_run_solana.py (lolos dry run 1, 53 pool, 0 entry).

TIAP RUN:
1. Jalankan `cd ~/workspace/solana-trading && python3 -u paper_run_solana.py` (mesin sudah punya lock file + deadline internal 750 dtk; bila lock terkunci/run sebelumnya masih jalan, akhiri diam tanpa retry).
2. Baca hasil run: run-diagnostics.jsonl + ledger.json (kas, posisi open, trade, sightings, events).
3. LAPOR ke chat utama HANYA bila ada: entry baru, exit (TP/stop/trailing/chart-dump/liq-collapse), kill switch aktif, atau alasan blokir BARU yang belum pernah dilaporkan. Sebutkan token (mint address), harga/entry, kas sesudah, dan alasan.
4. Bila tidak ada entry/exit/kill switch/alasan baru: DIAM (jangan kirim laporan rutin tiap run).
5. Bila run gagal (exit bukan 0, timeout, lock macet): catat singkat ke log harian ~/memory/YYYY-MM-DD.md + DIAM ke chat, kecuali gagal 3 run berturut-turut — laporkan sekali.
6. Bila trial berakhir (ledger ends_at 2026-11-21T18:20 WIB terlewati): laporkan sekali ringkasan akhir trial (kas akhir, total trade, win/loss, posisi open) dan JANGAN jalankan mesin lagi.
7. JANGAN pernah: trade live, sign, swap nyata, ubah ambang/gate di script, atau edit MEMORY.md. Observasi singkat ke log harian bila ada entry/exit.
