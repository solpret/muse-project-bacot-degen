---
id: m2-lp-dlmm-live
title: M2 LP DLMM live paper runner (15 menit)
enabled: false
owner: goal:riset-penyedia-likuiditas
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-17T09:49:11
  every: 15m
timeout_secs: 900
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
M2 LP DLMM SOLANA — RUNNER PAPER TIAP 15 MENIT (user 2026-11-17 ~08:52 "Untuk M2 coba di bangun agar bisa berjalan"; runner sudah terverifikasi parent 17 Nov: selftest LOLOS 11/11 + 38 cek, posisi paper pertama HOGE terbuka 09:36 WIB).

TIAP RUN:
1. Jalankan: cd ~/workspace/solana-trading/m2 && python3 m2_runner.py >> ~/workspace/solana-trading/m2/m2-runs.log 2>&1
   (Runner paper-only by construction — tidak pernah sign, broadcast, memanggil baw, menyentuh wallet/key, atau swap nyata. Jangan ubah perintah ini menjadi apa pun yang menyentuh wallet.)
2. Baca ~/workspace/solana-trading/m2/m2-ledger.json + tail m2-runs.log.
3. LAPOR ke chat utama HANYA bila: posisi baru dibuka; posisi DITUTUP (sertakan file hasil paper_lp_dlmm_live_*.json + PnL vs HODL + alasan exit); pause 24 jam terpicu (2 rugi beruntun); atau runner gagal/crash 2 run berturut-turut. Selain itu DIAM.
4. JANGAN buat/edit cron lain, jangan sentuh M1/M3/CHALLENGE.md/trials-m2/scoreboard. Observasi run ke ~/memory/YYYY-MM-DD.md. Jangan edit MEMORY.md.
