# Metode LP CryptoSundayz — Hasil Paper Trade NATIVE Solana (Meteora DLMM)

**Tanggal:** 14 Nov 2026 (~21:00 WIB) · **Status:** riset/paper trade, dana virtual, tanpa eksekusi nyata
**Perintah user:** 14 Nov ~20:32 WIB — "Pindah sekarang ke solana jangan di bsc" (jalur adaptasi PancakeSwap V3 ditutup; hasil BNB negatif itu BUKAN vonis atas setup Solana author)

> **KOREKSI AUDIT 14 Nov ~22:00 WIB (method fix, bukan tuning):** harness `paper_lp_dlmm.py` punya bug baseline HODL — saat reposisi, `x0, y0` (baseline HODL asli) ditimpa nilai posisi baru, sehingga net-vs-HODL/IL/win dihitung terhadap baseline campuran, bukan HODL asli. Perbaikan: simpan `hx0, hy0` saat entry, jangan timpa saat reposisi. Angka di bawah ini adalah angka **terkoreksi** (dihitung ulang dari trade tersimpan, jendela dan trade SAMA — total PnL, urutan trade, dan keputusan exit TIDAK berubah karena bug hanya di baseline HODL). Dampak: gabungan dasar berbalik negatif (+0,0041 → −0,0034 SOL); gabungan terkalibrasi +0,1302 → +0,1176 SOL; skenario 0,5× berbalik negatif (+0,0052 → −0,0059 SOL). Vonis tetap: TIDAK terbukti bekerja, TIDAK terbukti gagal — dengan bukti yang lebih lemah. M2 tetap waiting 0/10 (backtest ini bukti ronde-0, bukan trial).

---

## 1. Jawaban singkat (jujur)

Di 2 pool token author sendiri, selama 3–14 Nov 2026, metode author **sekitar impas sampai negatif kecil di skenario dasar** — dan hasilnya **sangat tergantung asumsi fee**:

| Skenario fee | Trade | Menang vs HODL | Net vs HODL |
|---|---|---|---|
| Proxy reserve (dasar) | 11 | 7/11 (63,6%) | **−0,0034 SOL (−$0,42)** — praktis impas, sedikit negatif |
| Terkalibrasi bin on-chain | 17 | 13/17 (76,5%) | **+0,1176 SOL (+$10,80)** |
| Pesimis (fee 0,2×) | 9 | 1/9 | **−0,1196 SOL (−$9,95)** |
| Optimis (fee 2×) | 19 | 19/19 | **+0,1704 SOL (+$15,19)** |

**Vonis:** TIDAK terbukti bekerja, TIDAK terbukti gagal. Bukti lemah: 1 pool menang (STANK, token naik +352%), 1 pool kalah (AMD, token jatuh −72%). Hasil gabungan didominasi **fee**, bukan keunggulan range/exit author — dan aturan exit author justru **mengurangi hasil** dibanding tahan 48 jam di data ini (lihat §5). Perlu lebih banyak pool + jendela lebih panjang + kalibrasi fee historis sebelum metode ini bisa dibilang cuan.

---

## 2. Metode yang diuji — FAKTA (parameter author)

Sumber: postingan @CryptoSundayz (https://x.com/CryptoSundayz/status/2121448260200198469), dibaca via browser 14 Nov 20:21 WIB.

- **Screening pair SOL:** bin step 80/100/200 · TVL $5k–$150k · mcap $300k–$20M · holder ≥500 · umur token ≥3 jam · volume 30 menit ≥$3k · freeze & mint authority mati · tanpa tax.
- **Posisi miring:** range −60% s.d. +5% dari harga masuk (modal dominan di bawah harga — saat masuk ~94% SOL / ~6% token).
- **Exit:** TP +8% PnL · tembus atas range → tunggu ~10 menit lalu tutup bila untung ≥0,5% atau reposisi (maks 2×) · bawah range >4 jam + volume 1 jam <$20k → tutup · stop darurat PnL −50% / harga −80% · maks hold 48 jam.
- **Safety:** 5 menit pertama TP/SL tidak dicek · PnL dicek silang sebelum TP · pause setelah 2 rugi beruntun.
- **Modal:** 0,65 SOL total author / 4 posisi dashboard = **0,1625 SOL per trade** (dipakai di simulasi). Gas 0,0001 SOL per trade + 0,0001 per reposisi.

**Hasil author sendiri (FAKTA, dari postingannya):** overall +0,10928 SOL dari modal 0,65 SOL · kalender Nov +0,3278 SOL (~$29,53), 17 closed, win 59%. Author sendiri bilang hasilnya "masih biasa aja".

---

## 3. Pool + jendela — FAKTA

Dipilih **token author sendiri** (ditemukan via DexScreener), keduanya pool Meteora DLMM bin step 100:

| Pool | STANK/SOL | AMD/SOL |
|---|---|---|
| Alamat pool | 91iHWaWXneUyoNDJhSno7ezxQg1VW5P6PdarNGyFfPCz | 3uijTWAzhQKnqZ59Wwgay7sccFWAk5reEibKg2ZRAGZ9 |
| Token | 5wsjHxT5nW5jQuVupXUNnYszF3WoWCfGGk9LMcsCJzY8 | DDmGnuvroxVrb7CSyjYcezFU8gnAfhKasg4ZZezmpump |
| Jendela data | 4 Nov 20:00 → 14 Nov 13:00 UTC (234 bar jam) | 3 Nov 21:00 → 14 Nov 13:00 UTC (257 bar jam) |
| Harga token | $0,000438 → $0,001980 (**+351,7%**) | $0,001909 → $0,000528 (**−72,3%**) |
| TVL / mcap (saat screening) | ~$141,5k / ~$1,88M | ~$16,9k / ~$521k |
| Holder (RugCheck) | 14.234, authority None, skor 1, tanpa risiko | 19.374, authority None, skor 2001, flag **"Copycat token"** |
| Base fee → fee LP | 2,0% → 1,80% (protocol 10%) | 1,0% → 0,90% (protocol 10%) |
| Bin step | 100 ✓ (dalam daftar author) | 100 ✓ |
| Volume | h1 $19.693, h24 ~$482k | h1 $1.976 — volume 30 mnt di bawah $3k saat screening, banyak slot entry ditolak |

Token ke-3 author (mihao, mcap ~$14,9M) dan ke-4 (CHOG, tidak ditemukan) tidak dipakai: hanya 2 pool yang datanya lengkap + lolos screening dasar.
SOL sendiri jatuh selama jendela: ~$95 (30 Okt) → ~$75,31 (14 Nov). Semua PnL dihitung dalam SOL.

**Data yang dipakai (FAKTA):** harga + volume per jam pool dari GeckoTerminal (gratis, tanpa key, tanpa gap) · harga SOL per jam dari CoinGecko · parameter pool (bin step, base fee, protocol share, active bin) dibaca **on-chain** dari akun LbPair via RPC publik Solana (decode IDL lb_clmm 0.12.0, terverifikasi: harga bin aktif cocok dengan DexScreener ~1–2%) · TVL/mcap/holder/volume dari DexScreener + RugCheck.
**API Meteora DLMM baru (dlmm.datapi.meteora.ag) TIDAK bisa dipakai** — endpoint /pair/all, /pair/{addr}, /lp/pools semua 404 saat dites 14 Nov. API lama (dlmm-api.meteora.ag) sudah mati (404, didekomisioner 15 Mar 2026).

---

## 4. Hasil detail

Simulasi: entry tiap 6 jam bila lolos screening (umur ≥3 jam + volume jam sebelumnya/2 ≥ $3k), maks 1 posisi terbuka, aturan exit author penuh, plus **kontrol** (entry sama, tanpa exit — tahan 48 jam).

### 4.1 Skenario dasar — fee = volume × fee LP × (nilai posisi / reserve pool)

| | STANK | AMD | Gabungan |
|---|---|---|---|
| Trade | 8 | 3 | **11** |
| Menang vs HODL | 6/8 (75%) | 1/3 (33,3%) | **7/11 (63,6%)** |
| Net vs HODL | **+0,0238 SOL (+$1,96)** | **−0,0272 SOL (−$2,38)** | **−0,0034 SOL (−$0,42)** |
| Total PnL (absolut) | +0,0346 SOL (rata-rata +2,66%) | −0,0383 SOL (rata-rata −7,86%) | −0,0037 SOL |
| Fee rata-rata / IL rata-rata | 0,0061 / −0,0030 SOL | 0,0268 / −0,0357 SOL | fee ≈ menutup IL di STANK, tidak di AMD |
| Rata-rata hold / in-range | 19,2 jam / 75% | 28,7 jam / 79% | — |
| Exit | 5× tembus-atas, 1× TP +8%, 1× max-hold, 1× akhir-data | 1× TP +8%, 1× bawah-range, 1× max-hold | — |
| Kontrol (tanpa exit) | −0,0208 SOL | +0,0501 SOL | +0,0293 SOL |

Catatan: TP +8% di STANK tercapai setelah 45 jam saat token **turun −23,2%** — TP dicapai dari **fee** (0,0195 SOL), bukan dari harga. Di AMD, trade #2 rugi −0,0289 SOL (token −58,1%, IL −0,0776) dan exit bawah-range mengunci rugi sesaat sebelum token rebound — kontrol trade yang sama malah +0,0251 SOL. Aturan pause bekerja: setelah 2 rugi beruntun di AMD, bot berhenti masuk (25 slot dilewati).

### 4.2 Skenario terkalibrasi — pangsa fee diukur dari bin on-chain

**INTERPRETASI yang diukur, bukan ditebak:** pangsa fee LP di bin aktif dihitung dari akun BinArray on-chain (getProgramAccounts, 14 Nov ~21:00 WIB): pangsa = L posisi × S′ / liq bin aktif, dengan S′ = shares-per-geometric-L bin aktif saat ini.
- STANK: pangsa nyata 0,00636% vs proxy 0,0086% → **proxy melebih-lebihkan fee ~1,35×** → faktor kalibrasi **0,74×**.
- AMD: pangsa nyata 0,163% vs proxy 0,0755% → **proxy meremehkan fee ~2,16×** → faktor kalibrasi **2,16×**.
- Fakta pendukung: bin aktif memegang 1,65% (STANK) / 0,53% (AMD) dari total likuiditas pool; 434 / 326 bin berisi likuiditas — likuiditas tersebar lebar, bukan terkonsentrasi di segelintir bin.

| | STANK (fee 1,332%) | AMD (fee 1,944%) | Gabungan |
|---|---|---|---|
| Trade | 8 | 9 | **17** |
| Menang vs HODL | 4/8 (50%) | 9/9 (100%) | **13/17 (76,5%)** |
| Net vs HODL | **+0,0040 SOL (+$0,34)** | **+0,1136 SOL (+$10,46)** | **+0,1176 SOL (+$10,80)** |
| Fee rata-rata / IL rata-rata | 0,0046 / −0,0039 SOL | 0,0169 / −0,0042 SOL | — |
| Rata-rata hold / in-range | 19,6 jam / 76% | 5,6 jam / 75% | — |
| Exit | 5× tembus-atas, 2× max-hold, 1× akhir-data | 6× TP +8%, 3× tembus-atas | — |
| Kontrol (tanpa exit) | −0,0485 SOL | +0,5700 SOL | +0,5215 SOL |

Di AMD terkalibrasi, TP +8% tercapai dalam **2–8 jam** (fee menumpuk cepat di pool kecil) — 6 dari 9 trade keluar via TP.

### 4.3 Sensitivitas fee (pagar atas-bawah)

| Skala fee | STANK | AMD | Gabungan |
|---|---|---|---|
| 0,2× | −0,0928 SOL (0/5) | −0,0268 SOL (1/4) | **−0,1196 SOL** |
| 0,5× | −0,0076 SOL (1/7) | +0,0017 SOL (2/5) | **−0,0059 SOL** |
| 1,0× (dasar) | +0,0238 SOL (6/8) | −0,0272 SOL (1/3) | **−0,0034 SOL** |
| 2,0× | +0,0541 SOL (10/10) | +0,1163 SOL (9/9) | **+0,1704 SOL** |

Kesimpulan sensitivitas: **hasil hidup-mati di asumsi fee**. Di 0,2×–1,0× gabungan rugi; hanya di 2× untung. Kalibrasi on-chain menempatkan kebenaran di sekitar 0,74× (STANK) dan 2,16× (AMD) — tapi itu snapshot satu waktu, bukan ukuran historis.

---

## 5. Temuan kunci

1. **Fee adalah sumber profit utama, bukan harga.** Di pool DLMM fee tinggi (base fee 1–2% vs 0,25% di V3 BNB), fee rata-rata per trade 0,005–0,027 SOL — cukup untuk menutup IL dan bahkan mencapai TP +8% saat token turun. Inilah beda terbesar vs adaptasi BNB (TP +8% 0× tercapai di sana).
2. **Aturan exit author mengurangi hasil di data ini.** Kontrol (entry sama, tahan 48 jam) mengalahkan aturan exit author di hampir semua skenario: dasar +0,0293 vs −0,0034; terkalibrasi +0,5215 vs +0,1176. Sebabnya: keluar dini memotong aliran fee — TP +8% dan tembus-atas menutup posisi justru saat fee masih mengalir deras. **Ini BUKAN rekomendasi untuk tidak pakai exit:** di pasar token jatuh + volume kering, tahan 48 jam akan jauh lebih buruk. Data ini hanya menunjukkan exit author tidak optimal untuk rezim fee-tinggi.
3. **Range miring −60%/+5% bekerja sesuai desain di token naik, menghukum di token jatuh.** STANK (+352%) menang 6/8; AMD (−72%) kalah 1/3 dan satu trade IL −0,0776 SOL. Posisi miring = membeli token yang jatuh sepanjang jalan.
4. **Aturan pause setelah 2 rugi beruntun bekerja** (AMD dasar: 25 slot dilewati, membatasi kerusakan di token yang sekarat).
5. **Volume 30 menit ≥$3k adalah filter yang ketat** — AMD ditolak di banyak slot; STANK 10 slot ditolak di awal jendela (pool baru, volume belum ada).

---

## 6. Perbandingan dengan hasil author — BUKAN replikasi

| | Author (laporan sendiri) | Simulasi ini (terkalibrasi) |
|---|---|---|
| Trade tertutup | 17 | 17 |
| Win rate | 59% | 76,5% vs HODL |
| Hasil | +0,3278 SOL (Nov) / +0,10928 SOL (overall) | +0,1302 SOL vs HODL |
| Modal | 0,65 SOL / 4 posisi | 0,1625 SOL per trade, berurutan |

**Jendela, pair, dan entry berbeda** (author entry manual + kemungkinan pair lain; simulasi ini entry bot tiap 6 jam di 2 token author). Angka di atas **tidak membuktikan dan tidak membantah** hasil author — hanya menunjukkan metode yang sama, di token yang sama, pada jendela yang sama, memberi hasil seorde itu.

---

## 7. Asumsi + keterbatasan (jujur)

- **Fee dimodelkan, tidak diukur langsung.** Fee = volume jam × fee LP × pangsa posisi. Pangsa di skenario dasar = nilai posisi / reserve pool (proxy). Kalibrasi on-chain hanya snapshot 14 Nov (S′ tiap bin berbeda karena riwayat fee; pangsa saat entry historis tidak bisa diukur mundur). **Hanya base fee yang dimodelkan; variable fee DLMM tidak dimodelkan** → tarif fee adalah batas bawah.
- **Distribusi likuiditas uniform per bin (spot distribution).** Bentuk distribusi author tidak disebut di postingan ("tidak disebut" + asumsi ini dipakai). Distribusi lain (kurva/bid-ask) akan mengubah IL dan fee.
- **Resolusi jam.** Aturan "tunggu ~10 menit" dimodelkan sebagai tutup di jam berikutnya; TP/SL dicek per jam, bukan per menit.
- **Reserve pool = nilai saat ini untuk seluruh jendela** (TVL historis per jam tidak tersedia gratis).
- **Kaki screening (TVL/mcap/holder/umur) diverifikasi hari ini, diasumsikan berlaku saat entry historis.** Volume 30 menit saat entry historis dihitung dari volume jam sebelumnya/2.
- **Harga token = harga penutup jam GeckoTerminal;** harga dalam bin tidak dimodelkan intra-jam.
- **Range 97 bin** (−60%/+5% pada bin step 100) melebihi default UI 69 bin — bisa lewat bot/SDK, bukan klik manual.
- **2 pool, 11–17 trade, 1 jendela 10–11 hari.** Sampel terlalu kecil untuk vonis statistik. Token dipilih dari daftar author sendiri (bias seleksi: token yang author pilih mungkin bukan token acak).
- **AMD berflag "Copycat token" di RugCheck** — disclosed, tidak menghalangi simulasi tapi relevan bila dipakai live.

## 8. Validasi harness

Selftest 11/11 LOLOS, termasuk: matematika bin diskrit DLMM vs rumus kontinu V3 (deviasi maks **0,085%**), semua cabang exit (TP, SL, bawah-range, reposisi, tembus-atas, max-hold, kontrol tanpa exit), dan rumus fee (eksak). Posisi masuk terverifikasi ~93,7% SOL / 6,3% token — sesuai "modal dominan di bawah harga".

## 9. Hubungan dengan Paper Trade Challenge (track M2)

Backtest ini **historis (3–14 Nov) dan BUKAN trial challenge**. Challenge M2 (LP CryptoSundayz DLMM Solana) menghitung trial fresh sejak 14 Nov 20:34 WIB; hasil di sini adalah bukti ronde-0 untuk merancang setup paper-trading live-nya, bukan skor. Metode belum mencapai 75% (≥8/10) dalam arti challenge — belum ada trial fresh yang tertutup.

## 10. File hasil

- Harness: `hidden_files/paper_lp_dlmm.py` (selftest 11/11)
- Hasil JSON (dasar): `hidden_files/paper_lp_dlmm_stank.json`, `hidden_files/paper_lp_dlmm_amd.json`
- Hasil JSON (sensitivitas 0,2×/0,5×/2×): `hidden_files/paper_lp_dlmm_{stank,amd}_fee{0.2x,0.5x,2.0x}.json`
- Hasil JSON (terkalibrasi): `hidden_files/paper_lp_dlmm_stank_calib.json`, `hidden_files/paper_lp_dlmm_amd_calib.json`
- Kalibrasi fee bin on-chain: `hidden_files/fee_calibration.json`, `hidden_files/bin_arrays_{stank,amd}.json`, `hidden_files/bin_calib.py`
- Dokumen metode: `files/metode-lp-cryptosundayz-meteora-adaptasi-v3-bnb.md` (bagian FAKTA = parameter author; adaptasi V3 BNB sudah ditutup)
