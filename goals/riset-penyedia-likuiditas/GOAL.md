# RISET PENYEDIA LIKUIDITAS

Goal ID: goal_2da9e3ed9aff
Goal slug: riset-penyedia-likuiditas

## Description
Proyek baru yang terpisah dari BACOT DEGEN, khusus mempelajari cara menjadi penyedia likuiditas (LP) yang untung di pool BNB. Fase pertama hanya riset dari berbagai sumber terpercaya — belum ada eksekusi, posisi LP, atau dana yang bergerak. Hasil riset menjadi dasar keputusan apakah dan bagaimana LP dijalankan nanti.

## Status
Fase 1 = RISET SAJA. Belum ada eksekusi, belum ada posisi LP, belum ada dana
yang bergerak, belum ada persetujuan untuk menyediakan likuiditas ke pool mana pun.
Dibuat: 2026-11-05 ~00:55 WIB atas perintah user.

## Batasan yang dipegang
- Proyek ini TERPISAH dari BACOT DEGEN. BACOT DEGEN (paper trading v2, cron
  paper-trading-15m) dibiarkan berjalan apa adanya — tidak disentuh, tidak
  dijeda, tidak dicampur hasilnya dengan proyek ini.
- Riset bersifat edukasi, bukan rekomendasi investasi personal: tidak ada
  rekomendasi token/pool spesifik, tidak ada janji return.
- Sumber harus terpercaya dan disebut dengan URL + tanggal: dokumentasi resmi
  (PancakeSwap, Uniswap), Binance Academy, DeFiLlama, studi kuantitatif/paper.
  Klaim influencer tanpa data = tidak terverifikasi, bukan bukti.
- Keputusan eksekusi LP (bila ada) HANYA setelah hasil riset dibaca user dan
  user memberi perintah terpisah. Riset ini sendiri bukan otorisasi eksekusi.

## Ruang lingkup riset
- Cara kerja LP di AMM: V2 full-range vs V3 concentrated liquidity.
- Matematika untung: fee vs impermanent loss (IL), kapan LP mengalahkan HODL.
- Bukti empiris: berapa persen LP yang benar-benar untung vs HODL (studi yang ada).
- Strategi: stable-stable, blue-chip, concentrated range, rebalancing,
  single-sided, hedged LP.
- Kasus khusus pool memecoin/baru di BNB: apakah fee pernah menutup IL +
  risiko rug/tarik likuiditas.
- Checklist evaluasi pool sebelum LP: rasio volume/TVL, fee APR vs IL,
  status lock/burn likuiditas, risiko token.
- Realita modal kecil: fee vs gas di BSC, ukuran posisi yang masuk akal.
- Risiko: IL, rug/pull likuiditas, smart contract, lock.

## Konteks user
- Fokus awal: pool BNB di BSC (PancakeSwap), sejalan dengan jalur degen yang
  sedang dibahas. Modal relatif kecil, jadi viabilitas modal kecil wajib dibahas.
- Bahasa laporan: Bahasa Indonesia.

## Jejak kerja
- 2026-11-05 ~00:55 WIB: goal dibuat + riset deep-research didelegasikan.
  Hasil riset (saat handoff tiba) ditulis ke files/ goal ini lalu dilaporkan.
- 2026-11-05 ~01:02 WIB: riset selesai (laporan 8 pertanyaan + 12 poin yang
  belum terbukti). Halaman ringkas sedang dibangun sebagai dokumen goal dari
  laporan tersebut. Tetap: belum ada posisi LP, belum ada dana bergerak,
  eksekusi LP butuh perintah terpisah.
- 2026-11-05 ~01:07 WIB: halaman "Riset Penyedia Likuiditas" selesai dibangun
  + terverifikasi (audit lolos, kalkulator IL cocok dengan contoh laporan:
  2,00x / $10.000 / fee 3% → HODL $15.000, LP $14.142, bersih -$558) dan sudah
  disampaikan ke user. Tetap riset saja — belum ada eksekusi.
- 2026-11-14 ~20:32 WIB: user memerintahkan track metode LP CryptoSundayz
  PINDAH KE SOLANA, jangan di BSC — metode diuji native di Meteora DLMM
  (Solana) dengan parameter author apa adanya, bukan lagi adaptasi
  PancakeSwap V3 BNB. Riset dasar BSC lama tetap jadi referensi, tidak
  dihapus. Hasil adaptasi BSC (SI/WBNB 9 trade 0 menang vs HODL, net
  -$48,39; NODE/WBNB 1 trade -$0,08) adalah hasil negatif untuk TERJEMAHAN
  V3 saja, bukan vonis atas setup Solana author. Tetap riset saja — belum
  ada eksekusi.
