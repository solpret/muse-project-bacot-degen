# BACOT DEGEN — paper trading mandiri

Goal ID: goal_b9d1c43a21e5
Goal slug: model-degen-paper-trading-mandiri

## Description
Model trading memecoin mandiri yang diuji hanya dengan uang virtual, terpisah dari MODAL BACOT. Mesinnya membaca pool baru GeckoTerminal, audit Binance, holder/bundle/dev, dan chart — tanpa sinyal narasi atau wallet terpantau MODAL BACOT, dan tanpa eksekusi uang asli. Tujuannya membuktikan apakah model ini layak berdiri sendiri sebelum ada keputusan apa pun soal trading live.

## Pemisahan dari MODAL BACOT (keputusan user 2026-11-05 ~00:27 WIB)
- BACOT DEGEN BERDIRI SENDIRI: bukan validasi metode MODAL BACOT, bukan anak dari proyek MODAL BACOT.
- Bukti pemisahan teknis (dicek 2026-11-05): kode mesin di `~/workspace/paper-trading/` (paper_run.py, holder_check.py, chart_check.py) TIDAK punya referensi apa pun ke mesin MODAL BACOT (ponyin-tools, narrative-pulse, tier-ab, live_loop, feed-queue, arming-scope). Yang dibaca mesin hanya: ledger sendiri, GeckoTerminal, RPC BSC, audit Binance.
- Cron `paper-trading-15m` dipindah dari goal `bsc-paper-trading-validation` (goal validasi MODAL BACOT) ke goal ini. Judul cron diubah menjadi "BACOT DEGEN — paper trading (simulasi, 15 menit)".
- Yang TETAP di MODAL BACOT dan TIDAK disentuh: job-job sinyal MODAL BACOT (narrative-pulse, tier-ab, holder-candidate, backtest, continuity-watch), arming scope di `~/workspace/ponyin-tools/live-executor-draft/`, dan monitor lama `paper-bsc-monitor` (nonaktif).
- Aliran dua arah diputus: sinyal/hasil MODAL BACOT tidak masuk ke BACOT DEGEN, dan hasil BACOT DEGEN tidak dihitung sebagai hasil MODAL BACOT (termasuk di rekap 2 jam — hasil paper tidak lagi dilaporkan sebagai bagian MODAL BACOT).
- Pemisahan ini TIDAK mengubah status eksekusi: cron tetap NONAKTIF (dijeda sejak 2026-11-05 ~00:21 WIB untuk evaluasi). Restart hanya atas keputusan user soal model v2.

## Keadaan saat pemisahan
- Modal virtual awal 0,010 BNB. Siklus 1 (2026-11-04 23:54 → 2026-11-05 00:11 WIB): 3 entry, ketiganya stop out, rugi virtual -0,007505 BNB, kas 0,002495.
- Ledger di-reset 2026-11-05 ~00:21 WIB: kas 0,010, 0 posisi, jendela 2026-11-05 → 2026-11-12, DIPERPANJANG 2026-11-05 ~08:12 WIB sampai 2026-11-19 atas perintah user 2026-11-05 ~07:03 WIB ("perpanjang setelah diperbaiki") setelah perbaikan terverifikasi (run cron 08:08 WIB memakai kode pagination, 40/40 pair, tanpa kill 900 detik). Arsip siklus 1: `~/workspace/paper-trading/ledger-cycle1-2026-11-04.json`. Forensik: `~/workspace/paper-trading/forensics-cycle1.json`.
- Evaluasi selesai 2026-11-05: akar masalah = lolos vakum (chart 3 candle, snapshot holder kosong dengan coverage_partial yang tidak dicek, dev tak dikenal dibaca 0%) + tanpa gate LP burn/lock, umur minimum, money-flow, dan korelasi + 90% modal terdeploy dalam satu run.
- Model v2 diusulkan (fail-closed, umur minimum, gate LP, money-flow/X ditegakkan, 1 entry/run, blok korelasi, kill-switch 30%) — MENUNGGU keputusan user. Jangan implementasikan atau restart sebelum user memilih.

## Batasan
- Simulasi saja: tidak pernah menandatangani, menyiarkan, atau menyentuh wallet. Tidak ada uang asli.
- Keputusan trading live apa pun (model apa pun) butuh perintah terpisah dan persetujuan mandat.

## Nama project huruf besar semua (keputusan user 2026-11-05 ~00:32 WIB)
Semua nama project ditulis huruf besar semua: BACOT DEGEN, MODAL BACOT, FREE BACOT. Berlaku untuk judul goal, judul cron, GOAL.md, MEMORY.md, dan AGENTS.md. Yang TIDAK diubah: slug/ID teknis (mis. model-degen-paper-trading-mandiri, paper-trading-15m), path file, dan arsip harian bertanggal (riwayat).

## Restart v2 (keputusan user 2026-11-05 ~00:29 WIB, tap "Terapkan model v2 dan restart paper")
- Cron `paper-trading-15m` DIAKTIFKAN KEMBALI 2026-11-05 ~00:34 WIB; run v2 pertama ~00:40 WIB. Jendela trial: 2026-11-05 → 2026-11-12, DIPERPANJANG sampai 2026-11-19 (2026-11-05 ~08:12 WIB, setelah perbaikan terverifikasi).
- Gate v2 yang diterapkan di paper_run.py + holder_check.py: candle ≥12 (60 menit), snapshot holder tidak partial + ≥50 holder, dev teridentifikasi (owner/distributor), LP burn ≥50% atau top LP holder berupa kontrak (heuristik lock), konfirmasi pertumbuhan 2-sighting (sighting pertama hanya mencatat baseline; entry butuh holder +10% DAN reserve BNB +5% di run berikutnya), blok korelasi (suffix/dev sama dengan posisi terbuka), maks 1 entry baru per run, total posisi terbuka maks 30% modal, kill-switch (kas <70% modal awal → tidak ada entry baru).
- Perbaikan _snapshot: chunk >5000 log kini dipecah rekursif, bukan berhenti; range yang tidak bisa dipecah dikembalikan sebagai partial (data hilang), dan partial MEMBLOKIR entry di paper_run.
- Substitusi yang dinyatakan terus terang: kaki X draf TIDAK ditegakkan di kode (pemeriksaan X via browser tidak bisa diotomatisasi di dalam script); sebagai gantinya konfirmasi datang dari leg pertumbuhan 2-sighting milik model sendiri. X tetap tercatat "belum_dikonfirmasi" sebagai informasi saja. Model ini TIDAK memakai money-flow MODAL BACOT (pemisahan berdiri sendiri).
- Verifikasi sebelum restart: py_compile ketiga modul lolos; 15/15 uji gate sintetis lolos (termasuk satu bug pruning sighting yang ditemukan dan diperbaiki oleh uji itu sendiri); tidak ada referensi mesin MODAL BACOT di kode (satu-satunya kecocokan grep adalah docstring yang menyatakan independensi).
- Ledger saat restart: kas 0,010, 0 posisi (reset 2026-11-05 ~00:21 WIB). Uji manual mesin TIDAK dijalankan — run v2 pertama adalah run cron itu sendiri, supaya ledger tetap bersih.
