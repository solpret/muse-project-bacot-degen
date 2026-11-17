# Catatan GAP — Metode LP dari X @CryptoSundayz (14 Nov 2026 ~20:14 WIB)

Status: **TERBLOKIR di langkah 1 — isi postingan tidak berhasil dibaca.**
Dokumen metode LP TIDAK ditulis (menulisnya tanpa isi postingan = mengarang metode).
Paper trade metode author TIDAK dijalankan (tidak ada parameter author untuk diuji).
Yang sudah disiapkan: harness simulasi + pool kandidat + baseline berlabel — lihat §4.

## 1. Yang diminta
User 14 Nov ~20:13 WIB: "Coba pelajari ini lalu terapkan untuk membuat metode lp
lalu coba paper trade nya" — postingan https://x.com/CryptoSundayz/status/2121448260200198469

## 2. Upaya membaca postingan (semua gagal, dicatat jujur)
- fxtwitter via browser.open (cara yang diadopsi user): GAGAL — "page was fetched, but
  no readable text could be extracted". Instruksi developer setelah kegagalan itu
  melarang mengulang request yang sama lewat tool/endpoint lain — dipatuhi, tidak
  dicoba ulang via curl/x.com/mirror.
- twitterapi.io: MATI (HTTP 402 sejak 2026-11-02) — dilarang dipakai, tidak dicoba.
- browser.search (4 query: nama author + LP/Meteora, ID status, "CryptoSundayz" Meteora):
  tweet TIDAK terindeks mesin pencari. Satu-satunya fakta author yang terverifikasi
  dari snippet: bio @CryptoSundayz = "Building agentic perp trading desk on
  @HyperliquidX · Agentic LP desk on @MeteoraAG · powered by GrokBot" (1K followers).
- Browser task read-only: TIDAK tersedia untuk subagen — tugas ini memang
  menginstruksikan fallback itu, tapi subagen tidak bisa meluncurkan browser task.

## 3. Yang DIBUTUHKAN dari parent (agar tugas bisa lanjut)
Parent (main agent) perlu membaca postingan itu lewat **live browser task** dan
menyalin **teks lengkap postingan + thread/reply author yang relevan** ke subagen
lanjutan. Setelah teks ada: ekstrak metode (pair/chain, rentang, sizing, masuk/
keluar, rebalance, fee, IL) dengan label FAKTA vs INTERPRETASI, tulis dokumen
metode di `files/`, lalu jalankan paper trade dengan parameter author memakai
harness di §4. Catatan adaptasi: author LP di **Meteora DLMM (Solana)** — goal ini
riset pool **BNB (PancakeSwap V3)** — metode DLMM (bin) harus diterjemahkan ke
V3 (tick) secara eksplisit, bukan diasumsikan sama.

## 4. Yang SUDAH disiapkan (terverifikasi, siap pakai saat teks postingan ada)
- Harness: `hidden_files/paper_lp_harness.py` — simulasi posisi V3 dari data harga
  nyata (CoinGecko BNB/USD hourly + volume GeckoTerminal OHLCV hourly, gratis).
  Validasi LOLOS 5/5: contoh kerja goal (masuk $10.000, BNB 2x -> HODL $15.000,
  LP $14.142, shortfall $858, fee 3% -> net -$558) + konvergensi V3 rentang lebar
  ke IL V2 ($14.143,91 vs $14.142). Dua bug ditemukan & diperbaiki selama kerja:
  (a) rumus L V3 harus dari total nilai (bukan y0 = C/2) — campuran awal ditentukan
  rentang; (b) OHLCV pool USDT/WBNB GeckoTerminal close-nya ~$1 (harga USDT),
  BUKAN kurs WBNB/USDT — harga kini diambil dari CoinGecko, volume dari pool.
  Satu file hasil baseline pertama DIBUANG karena bug (b) (harga datar ~$1).
- Pool kandidat (data live 14 Nov ~20:20 WIB, GeckoTerminal):
  - 0x172fcd41e0913e95784454622d1c3724f546f849 — USDT/WBNB 0.01% (V3),
    reserve $12.274.123, vol24 $147.941.207, ~340 ribu tx/24 jam.
  - 0x36696169c63e42cd08ce11f5deebbcebae652050 — USDT/WBNB 0.05% (V3),
    reserve $13.172.812, vol24 $31.839.315, ~18,5 ribu tx/24 jam.
- Asumsi harness (tercetak di tiap file hasil): uang VIRTUAL; tanpa rebalance
  (baseline); fee = volume/jam x fee tier x (nilai posisi / reserve) — reserve
  sebagai proxy likuiditas aktif sehingga fee adalah BATAS ATAS (optimistis);
  in-range dari close per jam; gas BSC $0,05/siklus; tanpa slippage.

## 5. Baseline berlabel (BUKAN metode CryptoSundayz — hanya validasi harness +
##    titik acuan; JANGAN dilaporkan sebagai hasil metode author)
Periode 14 hari, 336 jam, modal virtual $100, BNB masuk $703,63 -> keluar $610,54
(rasio 0,8677; -13,2% — pasar turun).
- `paper_lp_baseline_001.json` — pool 0.01%, rentang ±10%: in-range 92,9%;
  IL -$4,48 (-4,78% vs HODL); fee $0,86; net vs HODL **-$3,67 (-3,67%)**;
  return total -9,96% vs HODL -6,29%. Fee hanya menutup ~19% IL.
- `paper_lp_baseline_005.json` — pool 0.05%, rentang ±10%: IL sama -$4,48;
  fee $0,79 (LEBIH KECIL dari pool 0.01% meski tier 5x — volumenya jauh lebih
  kecil); net vs HODL **-$3,74 (-3,74%)**.
- `paper_lp_sens_range25.json` — pool 0.01%, rentang ±25%: in-range 100%;
  IL -$1,96 (-2,08%); fee $0,98; net vs HODL **-$1,03 (-1,03%)**.
  Rentang lebih lebar = IL lebih kecil di jendela turun ini, tetap kalah dari HODL.
  (HODL akhir sedikit berbeda antar run — $93,71 vs $94,17 — karena campuran
  awal x0/y0 ditentukan rentang; tiap run membandingkan dengan HODL-nya sendiri,
  sesuai metodologi goal.)
- Pembacaan jujur: di jendela 14 hari yang turun ini, LP terkonsentrasi kalah
  dari HODL di semua varian baseline — dan angka fee di atas adalah batas atas
  optimistis, jadi hasil riil kemungkinan lebih buruk, bukan lebih baik.
  Ini BUKAN vonis atas metode author (parameternya belum diketahui).

## 6. File yang dibuat (semua di hidden_files/ goal ini — bukan files/ user)
- paper_lp_harness.py (harness + validasi)
- paper_lp_baseline_001.json, paper_lp_baseline_005.json, paper_lp_sens_range25.json
- cryptosundayz-lp-gap-note.md (file ini)

## 7. RESOLVED — postingan berhasil dibaca + metode diekstrak + paper trade jalan (14 Nov ~20:21-20:45 WIB)
- Browser live (parent) berhasil baca postingan x.com tanpa login; teks lengkap
  diwariskan ke subagen lanjutan. Metode diekstrak dgn label FAKTA vs INTERPRETASI.
- Dokumen metode (user): `files/metode-lp-cryptosundayz-meteora-adaptasi-v3-bnb.md`
- Harness adaptasi: `paper_lp_author.py` (selftest 7/7; range asimetris -60%/+5%,
  semua aturan exit author, filter volume entry, aturan pause, kontrol entry-sama).
- Hasil paper trade (15 hari, $100/trade, UANG VIRTUAL):
  - SI/WBNB: 9 trade, 0 menang vs HODL, total net -$48,39 (rata-rata -$5,38);
    kontrol tanpa exit -$73,16 (exit menyelamatkan +$24,77). TP +8%: 0x kena.
    SL darurat: 0x kena. Fee rata-rata $0,34 vs IL rata-rata -$5,61.
  - NODE/WBNB V3 0.25%: 1 trade saja (52 slot ditolak screening volume),
    net -$0,08 (~impas), PnL +2,20%.
  - Bukan vonis atas setup DLMM asli author (tidak diuji) — hanya adaptasi V3 BNB.
- Perbaikan harness selama kerja: forward-fill jam tanpa trade (sebelumnya NODE
  hanya 77 bar/15 hari sehingga "hold 48 jam" salah hitung); filter kaki volume
  di entry (proxy volume jam sebelum entry / 2); kontrol memakai entry yang sama.
- Baseline lama (§5) tetap berlaku sebagai titik acuan terpisah; BUKAN hasil metode author.
