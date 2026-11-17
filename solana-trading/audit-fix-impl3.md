# Perbaikan Framework + M2 + Wallet + M1 — impl-3 (koordinator, 14 Nov ~22:00 WIB)

## 1. Scoreboard F1–F3 — DITERAPKAN + terverifikasi
- File: ~/workspace/trading-challenge/update_scoreboard.py (edit bedah — file .AUDITF-PATCHED kaki F mengandung path sandbox /tmp, TIDAK disalin mentah).
- F1 (sync_m2): file HANYA ditandai imported bila SEMUA trade live tercatat (atau duplikat); bila append_trial menolak, file dicoba lagi sync berikut + pesan "BELUM imported penuh".
- F2 (cmd_add): filter waktu di jalur manual — M1/M2 ≥ 14 Nov 20:34 WIB, M3 ≥ 21:11 WIB.
- F3 (sync_m3): patokan M3 21:11 WIB (bukan 20:34) + validasi gerbang wajib lolos + pnl_usd_net wajib ada.
- Bukti: baterai verifikasi /tmp/auditF2/verify_f.py — 12/12 PASS (F2: M1 exit 19:00 ditolak, M2 exit 6 Nov ditolak, M3 money_flow=false ditolak, M3 exit 20:45 ditolak, M3/M1 valid diterima; F3: sync_m3 failgate/pre-start tidak diimpor, valid diimpor; F1: file ditolak TIDAK ditandai imported + pesan BELUM, retry sesudah open diimpor + ditandai; sync sandbox normal M1/M3 delta 0).
- Live sync sesudah patch: 0 trial baru, scoreboard.json TIDAK berubah; status M1 1W/0L, M2 0/0, M3 0/0 (saat itu). Sync ulang ~22:00 WIB mencatat trial 2 M1 (SL −15%) → M1 1W/1L.

## 2. M2 HODL fix — DITERAPKAN + terverifikasi
- File: ~/workspace/goals/riset-penyedia-likuiditas/hidden_files/paper_lp_dlmm.py (diff 4 baris vs /tmp/auditE/paper_lp_dlmm_fixed.py → DIFF KOSONG).
- Perbaikan: simpan hx0,hy0 saat entry; hodl_sol pakai hx0/hy0 (bukan x0,y0 yang ditimpa reposisi); reposisi menulis _nx,_ny (dibuang).
- Bukti: --selftest 11/11 PASS (LOLOS).
- Angka terkoreksi (dihitung ulang dari trade tersimpan, jendela + trade SAMA — total PnL/keputusan exit tidak berubah):
  - Dasar: STANK 0,0302→+0,0238 SOL (7/8→6/8); AMD −0,0260→−0,0272 (1/3); gabungan +0,0041→**−0,0034 SOL** (8/11→7/11) — berbalik negatif.
  - Terkalibrasi: STANK 0,0103→+0,0040 (4/8 tetap); AMD 0,1199→+0,1136 (9/9); gabungan +0,1302→**+0,1176 SOL** (13/17 tetap).
  - Sensitivitas gabungan: 0,2× −0,1070→−0,1196; 0,5× +0,0052→**−0,0059** (berbalik negatif); 1,0× +0,0041→−0,0034; 2,0× +0,1830→+0,1704.
  - Catatan: kaki E melaporkan STANK calib lama 0,0113/5 menang dari rerun live (jendela bergeser) — angka dokumen yang benar dari trade tersimpan adalah 0,0103/4 menang; koreksi di atas memakai trade tersimpan.
- Dokumen diperbarui: metode-lp-cryptosundayz-hasil-solana-dlmm.md (§1 tabel + vonis, §4.1, §4.2, §4.3 + kesimpulan, §5 poin 2–3, + blok KOREKSI AUDIT) dan CHALLENGE.md §3 baris M2. M2 tetap waiting 0/10 (backtest = bukti ronde-0).

## 3. Cabal loader fix — DITERAPKAN + terverifikasi
- File: ~/workspace/solana-trading/infra/wallet_signal.py (kembangkan evidence.members → tiap member terdaftar, cluster id cabal-<koin bersama>).
- Bukti: test_wallet_signal.py 47 → **51 PASS / 0 FAIL** (4 tes regresi baru: counts, cluster map, skor 2 holder cabal + smart = 40, flag cabal True).
- Dokumentasi: wallet-signals.md (blok KOREKSI AUDIT). Dampak: skor wallet anggota cabal 0→+25 bila 2 holder klaster sama; M1 tidak memakai skor sebagai gate + M3 hanya info/gate factory → tidak ada trial terpengaruh.
- Deviasi 6a/6b/6c TIDAK diterapkan (proposal saja).

## 4. M1 last_value_sol saat entry — DITERAPKAN + terverifikasi
- File: ~/workspace/solana-trading/paper_run_solana.py (penggantian atomik, py_compile OK): posisi baru `"last_value_sol": size` (fallback ekuitas bila re-price gagal; jalur normal tidak berubah — loop exit me-reprice dulu).
- Bukti: audit-verify-m1-20261114.py 47 PASS sebelum crash pada cek yang mengakses led["positions"][0] — crash karena posisi open SUDAH TUTUP saat verifikasi (trial 2 tutup 21:51:47), bukan karena patch (skrip berasumsi ada posisi open; saat kaki A jalan posisi masih open → 54/54).
- Dokumentasi: CHALLENGE.md §2 M1 + trials-m1-solana-degen.md (trial 1–2 tercatat: 1W/1L).

## 5. Koreksi label CHALLENGE.md — DITERAPKAN
- "≥ 8 menang dari 10 (75%)" → "≥ 8 menang dari 10 (bar 8 = ceil 75% dari 10; 8/10 = 80%)" — bar 8 TIDAK diubah.
- Baris "Menang (scalping)" di tabel §1 dihapus (scalping excluded §5.4; baris konteks terpisah di §5.4 dengan bar vonis sendiri 40% TIDAK disentuh).
