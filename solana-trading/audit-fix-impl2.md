# Perbaikan M3 — impl-2 (koordinator, 14 Nov ~22:05 WIB)

Semua perubahan di ~/workspace/solana-trading/m3/m3_engine.py (penggantian atomik, py_compile OK).
Ronde M3 0/10, 0 trade — tidak ada trial di-restart. Dokumentasi method-fix: CHALLENGE.md §5.3.1a + trials-m3-modal-bacot-solana.md.

## 1. BUG-1 (kaki D) — dicatat, tidak diubah lagi
`score_mint` urutan argumen salah → skor wallet selalu 0, gate factory tidak aktif. Sudah diperbaiki kaki D (repro 7/7 PASS). Catatan method-fix ditulis di CHALLENGE.md §5.3.1a.

## 2. BUG-2 — DITERAPKAN + terverifikasi
- Masalah: sighting dicatat bila price_usd ada meski gerbang audit/holder gagal → holders=None → konfirmasi entry TypeError (ditelan try → skip diam-diam); 8/8 sighting saat itu holders: null.
- Perbaikan: (a) sighting HANYA bila holders terisi; (b) refresh baseline bila holders None dan evaluasi ulang punya holders (holders + liq + vol + price); (c) defensif `(baseline.get("holders") or 0)` di konfirmasi entry.
- Bukti: repro_m3_logic.py (diperbarui ke ekspektasi fix) — C1 TIDAK TypeError lagi (pass=True), C2 kontrol holders=500 pass True skor 95,1; SEMUA PASS.
- Catatan: 20 sighting lama masih holders: null (dry-run tidak menulis state); akan ter-refresh saat mint-nya dievaluasi ulang di run live berikutnya, atau tetap beku bila tidak muncul lagi (tidak bisa entry via holder leg, hanya via liq leg).

## 3. BUG-3 — DITERAPKAN + terverifikasi
- Masalah: pnl_usd_net tidak memotong drag entry (entry $40 @2x: +$38,9993 dilaporkan vs +$38,4986 kas nyata).
- Perbaikan: pos menyimpan entry_drag_usd + komponen (entry_fee/slip/gas_usd); settle_exit melacak exit_fee/slip/gas_usd; finalize: pnl = realized − size − entry_drag; pnl_breakdown berisi komponen nyata (bukan hardcoded 0.0).
- Bukti: repro D1 pnl laporan == pnl kas (38.4986), D1b == +38.4986 (bukan +38.9993), D2 breakdown {fees 0.3, gas 0.0014, slip 1.2, entry_drag 0.5007}; SEMUA PASS.

## 4. GoPlus Solana sebagai audit kedua — DITERAPKAN + terverifikasi
- Aturan dari field live (BONK + mint M1, 14 Nov): result keyed by mint; blokir bila code != 1, result kosong (code 2 partial = blokir), mintable/freezable/closable status "1", atau transfer_fee non-empty.
- Dipanggil HANYA untuk kandidat yang sudah lolos semua gerbang RugCheck (hemat panggilan ~4 dtk).
- Bukti: G1 GoPlus live BONK lolos (semua status "0", holder_count 1.021.385); G2 code 2 diblokir; G3 None diblokir; G4 mintable=1 diblokir; G5 transfer_fee diblokir — SEMUA PASS.
- Catatan: token termuda GoPlus lag (code 2 partial) → fail-closed; token pra-pair tetap tidak lolos via jalur ini.

## 5. Jupiter Token API v2 /recent sebagai discovery — DITERAPKAN + terverifikasi
- Tambah 30 token terbaru per run (berumur menit, sebelum pair DexScreener); pair dari firstPool bila ada; kandidat tetap lewat semua gerbang (pra-pair fail-closed via no_pair_data).
- Bukti: J1 discovery mengembalikan 30 mint jup_recent. Dry-run live 2×: 40 kandidat dievaluasi (dari 20 sebelumnya), 0 entry; ledger/state sha256 TIDAK berubah.
- Dry-run 1 skip: no_pair_data 21, audit danger 16, holder 2, chart 1. Dry-run 2: no_pair_data 23, danger 10, holder 5, chart 2.

## 6. Klaim Helius — DIPERBAIKI (teks)
- Docstring m3_engine.py: klaim "Helius DAS getAsset bila env HELIUS_API_KEY ada" dihapus (kode tidak pernah membacanya); klaim "GoPlus tidak ada di Solana" diperbaiki. CHALLENGE.md §5.3.1 audit bullet diperbarui sama.
