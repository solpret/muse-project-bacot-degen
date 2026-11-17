# Metode LP @CryptoSundayz (Meteora DLMM) — dan Adaptasinya ke PancakeSwap V3 (BNB)

**Status:** RISET SAJA — bukan rekomendasi, bukan otorisasi eksekusi. Tidak ada
posisi LP, tidak ada dana bergerak.
**Sumber:** postingan X https://x.com/CryptoSundayz/status/2121448260200198469
(14 Nov 2026, 10:40 WIB) + postingan terkait 10 Nov, 6 Nov, 4 Nov 2026.
**Cara baca:** postingan dibaca langsung via browser live 14 Nov ~20:21 WIB
(tanpa login; fxtwitter dialihkan ke x.com). Teks di bawah diringkas dari teks
verbatim postingan; setiap elemen diberi label **FAKTA** (tertulis di postingan)
atau **INTERPRETASI** (pemahaman/terjemahan penulis dokumen ini).
**Dokumen terkait:** hasil paper trade adaptasi di
`hidden_files/paper_lp_author_node.json` dan `hidden_files/paper_lp_author_si.json`;
harness `hidden_files/paper_lp_author.py` (selftest lolos 7/7).

---

## 1. Siapa author dan konteksnya (FAKTA)

- **Author:** CryptoSundayz (@CryptoSundayz, terverifikasi). Bio: "Building
  agentic perp trading desk on @HyperliquidX · Agentic LP desk on @MeteoraAG ·
  powered by GrokBot @bot | Override Web3 | Part of @get_optimum".
  1.154 pengikut, 7.327 postingan.
- **Setup:** bot LP agentic di **Meteora DLMM (Solana)**, dijalankan via GrokBot.
  Mulai running ~3–4 Nov 2026 (postingan 4 Nov: "kemarin sempat tanya2
  @Ikhwanhsn akhirnya mulai running"). Jadi saat postingan metode ditulis
  (14 Nov), setup ini berumur **~10 hari**.
- **Kejujuran author (FAKTA — penting):** "Hasilnya emang masih biasa aja,
  masih pake modal kecil per posisi" dan "ingat LP itu ada resikonya, walau yg
  gw kasih liat cuan belum tentu bsok2 masih cuan". Postingan 10 Nov: "so far
  masih hijau tapi belum memuaskan, sempat off dari Jumat sampe Senin sore krna
  limit @bot weekly nya habis" dan "Sekarang lagi testing2 1 side sol, soalnya
  beberapa x dual side kena SL". Postingan 6 Nov: "Doakan ga cuma keberuntungan
  ya tapi emang dia pinter!" dan "Kl lancar nanti gw minta agent buat kasih
  setup dari awal… Tapi kl ga sustain beberapa hari kedepan brti gw pecut
  lagi sampe jadi".
- **Artinya:** ini setup **eksperimental berumur ~10 hari, modal kecil**,
  yang author sendiri belum anggap terbukti. Bukan metode mapan.

## 2. Metode author apa adanya (FAKTA — dari postingan utama 14 Nov)

### 2.1 Screening — pool harus lolos SEMUA ini
- Pair SOL, **bin step 80/100/200**
- **TVL $5k–$150k**
- **Mcap $300k–$20M**
- **Holder ≥500, umur token ≥3 jam**
- **Volume 30 menit ≥$3k**
- **Freeze & mint authority mati, nggak ada tax**
- **Fee/volume sehat, nggak lagi pump/dump, buy/sell seimbang**
  (INTERPRETASI: tiga kriteria terakhir tidak diberi angka oleh author —
  "sehat", "nggak lagi pump/dump", "seimbang" adalah penilaian kualitatif.)

### 2.2 Posisi miring
- **Range bid-ask lebar, dari –60% sampai +5%.** Kebanyakan modal nunggu di
  bawah harga, jadi kalau harga turun, bot beli bertahap sambil makan fee.
  Swap token cuma sedikit, buat bagian kecil di atas harga.
- Kalau **price impact swap >1,5%**, bot coba lagi beberapa kali. Kalau masih
  mahal, pool di-skip.
  (INTERPRETASI: "posisi miring" = likuiditas tidak simetris; ~94% modal dalam
  bentuk SOL (di bawah harga) dan hanya ~6% dalam bentuk token — angka 94/6
  ini dihitung dari rumus V3 pada rentang tersebut, lihat §4.)

### 2.3 Exit
- **TP +8%**
- Harga **tembus atas range: tunggu ~10 menit**. Kalau untung **≥0,5%**,
  tutup. Kalau belum, **reposisi ke harga baru (maks 2x)**.
- **Di bawah range >4 jam dan volume 1 jam < $20k: tutup.**
- **Stop darurat: PnL –50% atau harga turun 80% dari harga masuk.**
- **Maks hold 48 jam.**

### 2.4 Safety
- **5 menit pertama** setelah buka, TP/SL **nggak dicek** karena data indexer
  suka belum lengkap.
- **PnL dicek silang** sama hitungan sendiri sebelum TP.
- **2 kali rugi beruntun, bot pause.**

### 2.5 Yang TIDAK disebut author (tidak ada di postingan — jangan diasumsikan)
- Ukuran modal **per posisi** (hanya "modal kecil per posisi", tanpa angka).
- Pair SOL yang mana saja (tidak ada daftar token).
- Berapa kali tepatnya retry saat price impact >1,5%.
- Durasi pause setelah 2 rugi beruntun (tidak disebut).
- Apakah "TP +8%" dan "untung ≥0,5%" dihitung dari PnL posisi atau dari
  harga — dokumen ini memakai PnL posisi (lihat §4, INTERPRETASI).
- Apakah metode 14 Nov ini sudah versi "1-side SOL" yang disebut di
  postingan 10 Nov — tidak dinyatakan eksplisit (INTERPRETASI: rentang miring
  –60%/+5% secara efektif sudah hampir satu sisi, konsisten dengan arah
  testing 1-side itu, tapi postingan tidak mengatakannya).

## 3. Hasil author sendiri (FAKTA TERBATAS — dari gambar, sebagian terpotong)

Angka-angka ini **terbaca dari gambar** di postingan; teks kecil di gambar
sebagian terpotong/tidak terbaca penuh. Disajikan apa adanya, tanpa
rekonsiliasi yang tidak didukung gambar.

- **Dashboard LP Desk (gambar 1, postingan 14 Nov):** 4 posisi — mihao-SOL,
  CHOG-SOL, STANK-SOL, AMD-SOL. PnL posisi yang terbaca: **+0,36%, +0,56%,
  –0,11%, –0,55%, +4,55%**. Panel kanan: **"Balance & overall PnL +0,10928
  SOL", "CAPITAL: 0,6500 SOL", "Deposit: 2026-11-03", "Deposit: 2026-11-09"**.
  Grafik bin AMD-SOL · bin step 100 · in range, "Price 0.000006390 · bin -601".
  (INTERPRETASI aritmetika: 0,10928 / 0,65 ≈ 16,8% dari modal yang tampil —
  BUKAN ROI bersih yang bisa dikutip, karena ada dua tanggal deposit dan
  timing-nya tidak diketahui.)
- **Kalender PnL November (gambar 2, postingan 14 Nov — sebagian terpotong):**
  3 Nov "+0,0045 / 6 closes", 9 Nov "–0,0939 / 1 close", 10 Nov "–0,0177 /
  7 closes". Sel lain tidak terbaca penuh.
- **Kalender PnL (gambar postingan 6 Nov):** "10 up · 7 down · 17 closed ·
  win 59%", "November 2026", **"+0,3278 SOL +$29,53"**. Per tanggal: 2 Nov
  "+0,0070 / 1 close", 3 Nov "+0,0356 / 8 closes", 4 Nov "–0,0236 / 3 closes",
  5 Nov "–0,0767 / 2 closes", 6 Nov "+0,3854 / 3 closes".
  (Catatan jujur: angka kalender s.d. 6 Nov (+0,3278 SOL, closed-only) dan
  dashboard 14 Nov (overall +0,10928 SOL) berbeda cakupan dan tanggal —
  kalender menghitung posisi yang sudah ditutup saja, dashboard menghitung
  keseluruhan; sel 9–10 Nov menunjukkan kerugian. Dokumen ini TIDAK
  merekonsiliasi keduanya menjadi satu angka.)
- **Implikasi harga SOL:** +0,3278 SOL = +$29,53 → SOL ≈ $90 pada tanggal
  itu (aritmetika dari angka gambar). Modal author 0,65 SOL ≈ **~$58**.

**Pembacaan:** hasil author kecil (puluhan dolar), bercampur menang-kalah,
dan author sendiri menyebutnya biasa saja / belum memuaskan. Ini **BUKAN
bukti metode terbukti cuan** — ini bukti metode sedang diuji dengan modal
kecil selama ~10 hari.

## 4. Terjemahan ke PancakeSwap V3 (BNB) — INTERPRETASI, belum teruji

| Elemen DLMM (author) | Terjemahan V3 BNB (dokumen ini) | Status |
|---|---|---|
| Pair SOL | Pair **WBNB** (token/WBNB) | Terjemahan langsung |
| Bin step 80/100/200 | **Fee tier 0,25%** untuk kedua pool uji | INTERPRETASI — tidak ada padanan 1:1. Bin step 100 ≈ 1% per bin; tick spacing V3 terdekat adalah tier 1% (2% per tick). Dipakai 0,25% karena itu tier aktual pool NODE dan tier standar pair volatil di PCS V3. Sensitivitas tier 1% belum dijalankan (catatan: fee 4x lipat pun tidak membalik hasil rata-rata, lihat §6). |
| Range –60% s.d. +5% | **Pa = 0,40 × P0, Pb = 1,05 × P0**, P = harga token dalam WBNB | Terjemahan langsung (rentang kontinu V3 sebagai padanan bin DLMM) |
| Freeze & mint authority mati (Solana) | **GoPlus: is_mintable = 0, owner = 0x0 / renounced, is_honeypot = 0** | Padanan BSC (INTERPRETASI — konsep Solana diterjemahkan ke pemeriksaan owner/mint BSC) |
| Tanpa tax | **GoPlus buy_tax / sell_tax ≈ 0** | Terjemahan langsung |
| Volume 30 mnt ≥$3k | Proxy: **volume jam SEBELUM entry / 2 ≥ $3k** (pakai jam penuh entry = look-ahead, tidak dipakai) | INTERPRETASI (proxy data) |
| Tunggu ~10 menit (tembus atas) | Dicek pada **close jam berikutnya** (resolusi data jam-an) | INTERPRETASI (pendekatan) |
| 5 menit pertama TP/SL tidak dicek | **Tidak ada cek exit pada jam entry** | INTERPRETASI (pendekatan) |
| TP +8% / untung ≥0,5% | **PnL posisi** (nilai + fee − gas − modal) / modal | INTERPRETASI — TP berbasis harga tidak mungkin: harga tidak bisa naik >+5% sambil tetap in-range (batas atas +5%), jadi TP harga tidak akan pernah kena. |
| "Rugi" (aturan pause) | **PnL absolut trade < 0** | INTERPRETASI |
| Durasi pause | **Berhenti masuk sampai akhir jendela** (tidak disebut author) | INTERPRETASI (asumsi ketat) |
| Price impact swap >1,5% | **Tidak dimodelkan** (posisi $100 di pool ini dampaknya kecil) | Keterbatasan |

**Yang tidak bisa diterjemahkan 1:1:**
- **Bin DLMM ≠ tick V3.** DLMM membagi harga ke bin diskrit dengan fee per
  bin; V3 memakai tick kontinu dengan fee tier. Bentuk likuiditas "miring"
  yang sama (banyak di bawah harga) bisa dicapai, tapi distribusi fee dan
  perilaku saat harga bergerak tidak identik.
- **Single-sided DLMM ≠ posisi V3.** Postingan 10 Nov menyebut testing
  1-side SOL; posisi V3 selalu dua sisi (campuran token + WBNB ditentukan
  rentang — pada range ini ~94% WBNB / ~6% token saat entry).
- **Fee DLMM ≠ fee V3.** Struktur fee Meteora (per bin, dinamis) berbeda
  dari fee tier V3 yang tetap.
- **Indexer/data Solana ≠ data BSC.** Aturan "5 menit pertama" lahir dari
  perilaku indexer Solana; padanannya di BSC adalah keterlambatan data
  GeckoTerminal/DexScreener, yang tidak diukur di sini.

## 5. Screening 2 pool uji — dicek hari ini (14 Nov ~20:30 WIB)

| Kaki screening author | SI / WBNB (SpaceX Inu) | NODE / WBNB (NodeOps) |
|---|---|---|
| Pair BNB (adaptasi dari SOL) | ✓ WBNB | ✓ WBNB |
| TVL $5k–$150k | ✓ **$100.100** | ✓ **$13.305** |
| Mcap $300k–$20M | ✓ **$537.443** | ✓ **$2.282.154** |
| Holder ≥500 | ✓ **3.103** | ✓ **58.750** |
| Umur token ≥3 jam | ✓ ~27 hari | ✓ ~15 bulan |
| Volume 30 mnt ≥$3k | ✗ saat ini (~$1.764 proxy h1/2; bervariasi per jam) | ✓ ~$12.600 (m5 $2.108 × 6) |
| Freeze/mint authority mati | ✓ owner 0x0, is_mintable 0 | ⚠️ GoPlus null (tidak terverifikasi) |
| Tanpa tax | ✓ 0,03% / 0,03% (praktis nol) | ✓ 0 / 0 |
| Buy/sell seimbang | ✗ saat ini (h1: 54 beli / 19 jual) | ✓ h1: 555 / 462; h24: 2074 / 2107 |
| Honeypot | ✓ is_honeypot 0 | (GoPlus is_honeypot null — tidak terverifikasi) |

- **SI:** pool yang dipakai 0x5a606e1533fb11870f3b6c2f98a7edda699b94bf —
  ini pool **V2** PancakeSwap. Pool V3 SI (tier 1%) ada tapi mati (reserve
  $3,84, vol24 $0,09). Posisi V3 0,25% **dimodelkan di atas seri harga/volume
  pool V2** — diberi label di hasil. Token: 0x725CCC7B5cEaCb0324B64CCb7DA3EcA2cd3a6666.
- **NODE:** pool yang dipakai 0xd741e051815f4cd350ffd1f4bba800f1df62b828 —
  ini **benar pool V3 tier 0,25%**. Token: 0x2F714d7b9A035d4ce24af8d9b6091c07E37f43Fb.
- **Catatan penting:** kaki TVL/mcap/holder/umur hanya terverifikasi HARI INI.
  Di entry historis, kaki-kaki itu diasumsikan lolos; hanya kaki volume yang
  dicek per entry dari data. Ini keterbatasan (lihat §7).

## 6. Paper trade adaptasi — hasil (UANG VIRTUAL, $100/trade)

**Periode:** 30 Okt 14:00 → 14 Nov 13:00 UTC (15 hari, 360 jam).
**Aturan main:** entry sekuensial tiap 6 jam bila tidak ada posisi terbuka
dan kaki volume lolos; maks hold 48 jam; semua aturan exit author aktif;
kontrol = range sama, tanpa aturan exit, pada ENTRY YANG SAMA.

### 6.1 SI / WBNB — 9 trade
| Ukuran | Author (aturan penuh) | Kontrol (tanpa exit) |
|---|---|---|
| Trade | 9 (20 entry ditolak screening volume) | 9 (entry sama) |
| Menang vs HODL | **0 / 9 (0%)** | 1 / 9 (11%) |
| Menang PnL absolut | 4 / 9 | 1 / 9 |
| Total net vs HODL | **−$48,39** (rata-rata −$5,38/trade) | −$73,16 (rata-rata −$8,13) |
| Total PnL absolut | −$52,37 (rata-rata −5,82%) | −$84,87 (rata-rata −9,43%) |
| Rata-rata fee | $0,34/trade | $0,63/trade |
| Rata-rata IL | −$5,61/trade | −$8,70/trade |
| Rata-rata hold | 25,2 jam | 46,6 jam |
| Rata-rata in-range | 70,5% | 60,6% |
| Alasan exit | 4× tembus-atas-TP, 2× tembus-atas-maks-reposisi, 2× maks-hold, 1× akhir-data | 8× maks-hold, 1× akhir-data |

Per-trade (net vs HODL): −$5,16; −$2,22; −$2,61; −$1,91; −$0,80; −$1,92;
−$0,26; −$0,09; **−$33,41** (trade terakhir: token −61,4% dalam 35 jam,
IL −$33,76).
Tanpa trade pertama (artefak awal jendela, masuk tanpa cek volume):
8 trade, total net **−$43,23**, tetap 0 menang vs HODL.

### 6.2 NODE / WBNB — 1 trade
- **52 dari 53 slot entry ditolak** screening volume — pool nyaris mati
  selama ~14 hari, volume baru meledak di 6 jam terakhir jendela
  (h6 $219.657 dari h24 $219.856).
- 1 trade: net vs HODL **−$0,08** (≈ impas), PnL absolut **+2,20%**,
  exit maks-hold 48 jam, in-range 100%, token −0,9%, IL −$0,07, fee $0,04.
  Kontrol identik (tidak ada exit yang kena).
- Trade ini masuk di jam pertama jendela **tanpa verifikasi volume**
  (artefak awal jendela — tidak ada jam sebelumnya untuk dicek). Sampel
  NODE praktis tidak ada: **1 trade, hasil ~impas**.

### 6.3 Pembacaan jujur
1. **Adaptasi ini kalah dari HODL di 9 dari 9 trade SI.** Ini hasil
   adaptasi V3 di 2 pool BNB selama 15 hari — BUKAN vonis atas setup DLMM
   asli author di Solana (yang tidak diuji di sini: tidak ada data SOL,
   tidak ada simulasi DLMM).
2. **Aturan exit membantu, tapi tidak membalikkan hasil.** Dibanding kontrol
   tanpa exit, aturan author menyelamatkan **+$24,77 net** (+$32,49 PnL)
   di SI — exit memotong kerugian sekitar sepertiga. Tapi tetap kalah.
   Per-trade campur aduk: 2 trade justru lebih buruk dengan exit
   (keluar dini melewatkan rebound / reposisi menambah eksposur saat jatuh).
3. **TP +8% tidak pernah kena (0 dari 10 trade).** Struktural: posisi masuk
   ~94% WBNB / ~6% token, jadi kenaikan harga token sampai batas atas range
   (+5%) hanya memberi ~+0,3% PnL posisi + fee. TP +8% praktis hanya bisa
   dari akumulasi fee — fee rata-rata $0,34/trade, jauh dari $8 yang
   dibutuhkan. (Sensitivitas kasar: fee tier 1% sekalipun — 4x fee — hanya
   menambah ~$1/trade, tidak membalik rata-rata −$5,38.)
4. **Stop darurat tidak pernah kena (0 dari 10 trade).** Ambangnya sangat
   lebar: trade terburuk rugi −43,74% absolut tanpa menyentuh SL PnL −50%
   maupun harga −80% (token −61,4%).
5. **Aturan "bawah range >4 jam + vol <$20k" tidak pernah kena (0×).**
   Jendelanya sempit: butuh penurunan 60–68% (di bawah itu SL −50% kena
   duluan — dibuktikan selftest) DAN volume jam <$20k. Pada crash terakhir
   SI, volume justru tinggi, jadi aturan ini tidak jalan.
6. **Exit "tembus atas" memotong upside.** 4 trade ditutup via
   tembus-atas-TP dengan PnL absolut kecil positif (+0,5–0,7%) tapi tetap
   kalah vs HODL (−$0,26 s.d. −$2,22): token naik 16–45% selama trade itu,
   HODL menang besar, posisi miring hanya mengambil remahnya.
7. **Fee tidak berarti dibanding IL.** Rata-rata fee $0,34 vs IL −$5,61
   per trade SI — dan fee ini sudah **batas atas optimistis** (reserve
   sebagai proxy likuiditas aktif), jadi fee riil lebih kecil lagi.
8. **Screening volume bekerja nyata.** 20 slot SI dan 52 slot NODE ditolak
   — bot author sebagian besar waktu TIDAK masuk posisi. Tanpa filter itu,
   hasilnya akan lebih buruk (2 trade pertama yang lolos artefak awal
   jendela termasuk yang merugi).

## 7. Keterbatasan paper trade ini
- **Sampel kecil:** 9 trade SI + 1 trade NODE, 15 hari, 2 pool. Bukan
  statistik yang cukup untuk vonis metode secara umum.
- **Bukan setup author yang diuji:** yang diuji adalah ADAPTASI V3 di BNB,
  bukan DLMM di Solana. Hasil buruk adaptasi tidak membuktikan setup asli
  author buruk — dan sebaliknya.
- **Screening historis tidak lengkap:** TVL/mcap/holder/umur hanya dicek
  hari ini; di entry historis diasumsikan lolos. Hanya kaki volume yang
  dicek per entry.
- **Resolusi jam-an:** "tunggu ~10 menit" didekati close jam berikut;
  ekskursi intra-jam tidak tertangkap; "5 menit pertama" didekati tanpa cek
  exit di jam entry.
- **Fee batas atas:** reserve dipakai sebagai proxy likuiditas aktif; fee
  riil lebih kecil. Reserve dipakai nilai SAAT INI untuk seluruh jendela
  (tidak ada histori reserve). Jam tanpa trade di-forward-fill (harga
  terakhir, volume 0).
- **Tanpa slippage / price impact** (posisi $100, dampak kecil — tapi tidak
  diukur). Gas BSC $0,05/siklus, reposisi +$0,05.
- **2 trade pertama** (satu per pool) masuk di jam pertama jendela tanpa
  verifikasi volume — artefak batas data, sudah dilaporkan terpisah.
- **Periode turun/volatile:** jendela ini mencakup crash SI −61% dan BNB
  yang melemah; hasil pada jendela sideways bisa berbeda (tidak diuji).

## 8. Yang masih belum terjawab dari postingan
- Ukuran modal per posisi (hanya "modal kecil").
- Daftar pair yang dipakai author.
- Angka untuk "fee/volume sehat", "buy/sell seimbang", "tidak lagi
  pump/dump", jumlah retry price impact, dan durasi pause.
- Apakah TP dihitung dari PnL atau harga (dokumen ini memakai PnL).
- Apakah metode 14 Nov sudah versi 1-side dari testing 10 Nov.
- Apakah setup author bertahan setelah 14 Nov (tidak ada data lanjutan).

## 9. Kesimpulan sementara (bukan rekomendasi)
Metode author adalah **eksperimen 10 hari dengan modal ~$58** yang author
sendiri sebut biasa saja. Adaptasinya ke V3 BNB — diuji paper trade 15 hari
di 2 pool — **kalah dari HODL di 9 dari 9 trade SI** (rata-rata −5,38%
per trade), dengan aturan exit yang membantu memotong kerugian tapi tidak
membalikkan hasil. **TP +8% secara struktural hampir tidak terjangkau**
dengan rentang miring ini, dan **stop darurat terlalu lebar** untuk
menangkap crash −61%. Sebelum metode ini dipakai dengan dana nyata (itu pun
butuh perintah terpisah dari user), yang perlu dijawab: apakah TP harus
diturunkan / range diubah, apakah ambang SL perlu dirapatkan, dan apakah
hasilnya bertahan di jendela sideways dan di setup DLMM asli — semuanya
belum terjawab di sini.
