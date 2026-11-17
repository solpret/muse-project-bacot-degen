# AUDIT SWEEP G3 — Narasi pengganti X, feed real-time, katalog free-tier signup, GitHub

**Kaki:** G3 (sweep feed lain, free-tier signup, pengganti narasi X)
**Tanggal uji:** 14 Nov 2026 ~21:30–21:45 WIB, dari VM (curl / python `websockets` 17.4)
**Definisi "sempurna":** menurut SELURUH sumber daya GRATIS yang bisa dimanfaatkan.
**Aturan dipatuhi:** tidak ada signup (tidak ada browser), tidak ada layanan berbayar, tidak ada file lain diubah, tidak ada cron/wallet live disentuh. Semua angka free-tier berasal dari docs resmi / halaman pricing resmi (dicek via `browser.search`, terakhir diverifikasi sumber 2026-09 s.d. 2026-11); harga bisa berubah — cek ulang halaman resmi sebelum membuat key.

---

## A. Sumber narasi / sosial (pengganti X yang mati 402)

Penilaian kejujuran: **tidak ada satu pun sumber di bawah ini yang menggantikan X.** X adalah tempat narasi memecoin Solana lahir (KOL call, deployer shill, reply-guy). Yang ada hanyalah (a) stream publik kecil yang *bisa* dibaca dari VM, (b) feed akun yang sudah dikenal, (c) berita makro. Semuanya dinilai apa adanya.

| # | Sumber | Uji langsung dari VM | Hasil | Penilaian kejujuran |
|---|--------|----------------------|-------|---------------------|
| A1 | **Bluesky Jetstream** (firehose publik, `wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post`) | ✅ JALAN — stream masuk, 300 post terpindai dalam 20 detik | 0 hit kata kunci `solana/memecoin/pump` dalam jendela 20 detik | **Paling menjanjikan secara teknis, paling lemah secara densitas.** Tanpa auth, real-time, filter keyword di sisi klien. Tapi Bluesky bukan tempat narasi memecoin Solana — volume crypto kecil, dan postingan token-spesifik (ticker/CA) nyaris tidak ada. Cocok sebagai *jaring lebar* (deteksi kata "solana" + "pump" + ticker), bukan sebagai sinyal utama. Alternatif: subscribe hanya commit dari DID akun yang dilacak (lebih hemat daripada firehose global). |
| A2 | **Bluesky public API — getAuthorFeed / getFeed / searchActors** (`public.api.bsky.app/xrpc/...`) | ✅ JALAN tanpa auth (dengan UA browser). `searchActors?q=solana` → akun `solana.com` dkk. `getAuthorFeed?actor=solana.com` → post asli. `getFeed` whats-hot → jalan. | Feed akun resmi Solana terbaca | **Berguna untuk akun yang SUDAH dikenal** (Solana Foundation, KOL yang pindah ke Bluesky). Bukan discovery: tidak bisa mencari postingan tentang token baru. |
| A3 | **Bluesky searchPosts** (`app.bsky.feed.searchPosts`) | ❌ **403 Forbidden** dari VM, dengan dan tanpa UA (halaman block bergaya Cloudflare/Bunny) | — | Endpoint pencarian keyword Bluesky diblokir dari egress VM. Jangan andalkan. (Bila suatu saat lewat proxy lain, ini yang paling dicari — tapi hari ini mati.) |
| A4 | **Nostr — relay nos.lol** (`wss://nos.lol`, REQ kinds:[1] `#t:["solana"]`) | ✅ JALAN — 2 EVENT asli bertag `solana` + EOSE (berita DTCC/tokenized stocks Solana, Formation Securities) | Postingan nyata, relevan Solana | **Pengganti narasi terbaik ke-2.** Query hashtag/token bisa dilakukan langsung, tanpa key. Kelemahan: komunitas Nostr kecil dan isinya berita/analisis, bukan call memecoin cepat; relay lain gagal (`relay.damus.io` = connection closed, `relay.primal.net` = handshake timeout). Pakai `nos.lol` sebagai relay utama + fallback `relay.nostr.band` (belum sempat diuji — antrean). |
| A5 | **Farcaster — Warpcast API publik** (`api.warpcast.com/v2/search-casts?q=solana`) | ✅ JALAN tanpa key — mengembalikan cast + author + followerCount | Hasil teratas bertimestamp Feb 2024 (1708622910000) — pencarian tampaknya diurutkan relevansi, bukan recency murni | **Crypto-native, tapi kecil dan lambat.** Cocok untuk cek "apakah token X pernah dibahas di Farcaster", bukan untuk deteksi narasi menit-ke-menit. Perlu validasi urutan waktu sebelum dipakai sebagai sinyal. |
| A6 | **Farcaster — Neynar API** (`api.neynar.com/v2/farcaster/cast/search`) | ⚠️ BUTUH KEY — tidak diuji signup. Catatan dari docs/komunitas: **endpoint `/cast/search` butuh plan BERBAYAR; key gratis mengembalikan 402** (sumber: commit Coral withcoral, 2026; dok rate-limit Neynar). Free plan sendiri murah hati (lihat §C). | — | Jangan jadikan Neynar sebagai jalur narasi gratis — search-nya berbayar. Warpcast API publik (A5) adalah jalur gratisnya. |
| A7 | **Telegram — halaman publik `t.me/s/<channel>`** | ✅ JALAN — `t.me/s/pumpfun` 105 KB (20 pesan, teks `tgme_widget_message_text` bisa diekstrak), `t.me/s/screener` 30 KB | Pesan channel resmi Pump.fun terbaca (pengumuman fitur, bukan call) | **Berguna untuk channel yang SUDAH dikenal** (pengumuman resmi proyek). Bukan discovery: tidak ada pencarian lintas-channel; channel tanpa preview publik mengembalikan 302 (`/solana`, `/dex`, `/solanamemecoins` — tidak ada / privat). Daftar channel call memecoin yang dikenal publik perlu dikurasi manual dan masing-masing diuji `t.me/s/`. |
| A8 | **Reddit public JSON** (`old.reddit.com/.../new.json`, `api.reddit.com`, `www.reddit.com/...json`) | ❌ **Diblokir** — "Blocked … due to a network policy" (semua varian, dengan UA) | — | Mati dari VM tanpa OAuth. Reddit butuh aplikasi terdaftar (OAuth, gratis tapi butuh signup + client ID). Catat sebagai "butuh signup OAuth", bukan "gratis langsung". |
| A9 | **Lens / Hey API** (`api-v2.lens.dev`, GraphQL) | ❌ **HTTP 000** — koneksi gagal dari VM (endpoint lama diduga sudah dimatikan; endpoint baru tidak terverifikasi) | — | Tidak bisa dipakai dari VM hari ini. Lens juga sepi untuk memecoin Solana. Tidak relevan — jangan kejar. |
| A10 | **Google News RSS** (`news.google.com/rss/search?q=solana+memecoin`) | ✅ JALAN — XML valid, `lastBuildDate` 14 Nov 2026 14:30 GMT | Judul berita segar | **Berita makro saja.** Tidak ada mention token-spesifik di bawah $1M MC. Berguna sebagai konteks pasar (mis. "Solana ETF", "pump.fun dituntut"), bukan sinyal entry. |
| A11 | **CoinDesk RSS** (`coindesk.com/arc/outboundfeeds/rss/`, perlu `-L`) | ✅ JALAN dengan follow-redirect | XML valid | Sama seperti A10: makro saja. |
| A12 | **Cointelegraph RSS** (`cointelegraph.com/rss`) | ✅ JALAN | XML valid | Sama seperti A10: makro saja. |
| A13 | **CryptoPanic RSS** (`cryptopanic.com/news/rss/`) | ❌ **410 Gone** | — | Mati. Jangan pakai. |
| A14 | **YouTube Data API** | — (butuh key, tidak diuji signup) | — | Butuh Google Cloud key (gratis 10.000 unit/hari, tanpa kartu untuk kuota gratis). Potensi: cari video "Solana memecoin" terbaru — tapi latensi jam-an dan isinya didominasi shill berbayar. Prioritas rendah; catat saja. |

### Verdict narasi (jujur)
- **Tidak ada pengganti X.** Yang paling dekat dengan "narasi yang bisa dibaca mesin" adalah kombinasi: **Jetstream (Bluesky) + Nostr nos.lol + Warpcast search + Telegram channel terkurasi + RSS makro**. Semuanya bersama-sama pun hanya menghasilkan sinyal lemah: postingan tentang token spesifik yang baru launch hampir tidak ada di luar X/Telegram tertutup.
- **Yang sudah ada tetap yang terbaik:** DexScreener metas/boosts/profiles + GeckoTerminal trending (proxy on-chain, bukan narasi — tapi setidaknya mengukur uang, bukan kata-kata). Jangan klaim narasi sosial "tertutup" bila yang dipakai tetap proxy ini.
- **Satu-satunya jalur narasi token-spesifik gratis yang belum diuji:** daftar channel Telegram call memecoin publik (butuh kurasi manual nama channel + uji `t.me/s/` satu per satu) dan relay Nostr tambahan (`relay.nostr.band`, `relay.damus.io` lewat retry). Itu pekerjaan lanjutan kaki G3, bukan temuan hari ini.

---

## B. Feed real-time (selain PumpPortal WS)

| # | Feed | Uji langsung dari VM | Hasil |
|---|------|----------------------|-------|
| B1 | **PumpPortal WS new-token** (`wss://pumpportal.fun/api/data`, `subscribeNewToken`) | ✅ **VERIFIKASI ULANG JALAN** — 3 token dalam hitungan detik (ASKING, RUBIUS, +1) | Tetap feed utama new-token. Tanpa key untuk subscribe dasar (trade stream butuh key — sudah diketahui). |
| B2 | **Solana public WS logsSubscribe** (`wss://api.mainnet-beta.solana.com`, `mentions: [Pump.fun program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P]`, commitment processed) | ✅ **JALAN — diuji di kaki ini** (tidak ditemukan bukti kaki G2 sudah mengujinya di file infra; bila G2 sudah, ini konfirmasi independen) | Subscribe OK (id 1), **2 notifikasi log dalam <25 detik** (slot 469364138). Artinya: deteksi mint/launch Pump.fun langsung dari chain publik TANPA key dan TANPA PumpPortal — jalur redundansi yang nyata. Perlu parser log (decode instruksi `create`/`buy`) sebelum jadi sinyal. |
| B3 | **Helius webhooks** | Butuh key (lihat §C). Menurut docs: webhook = 1 kredit/event, tersedia di semua plan termasuk Free. | Jalur push terbaik bila key Helius dibuat: webhook alamat/program (mint, transfer, swap) langsung ke endpoint. Tidak bisa diuji tanpa key. |
| B4 | **Birdeye WebSocket** | Butuh key; menurut docs resmi: **WS mulai dari plan Premium $199/bulan** (500 koneksi). Free Standard tidak ada WS. | Bukan jalur gratis. Coret untuk stack gratis. |
| B5 | **Solana public RPC no-key (HTTP)** — `api.mainnet-beta.solana.com`, `solana-rpc.publicnode.com` | ✅ `publicnode` getSlot → slot 469364652, HTTP 200 | Cadangan RPC tanpa signup. Rate limit ketat dan tidak dijamin — hanya fallback. |
| B6 | **dRPC public nodes Solana** (`solana.drpc.org`) | ❌ **"chain is not available on free plan, please upgrade"** (HTTP 400, code 35) | Klaim "210M CU/mo free" TIDAK berlaku untuk Solana di endpoint publik tanpa key. Jangan andalkan untuk Solana. |
| B7 | **Pump.fun frontend API** (`frontend-api.pump.fun/coins`) | ❌ Cloudflare "Just a moment..." (challenge) | Mati dari VM. Jangan pakai. |

---

## C. Katalog free-tier signup (tanpa kartu — dibaca dari docs resmi, TIDAK signup)

> "Butuh kartu?" = kartu kredit untuk mengaktifkan free tier. Semua di bawah ini diklaim no-card oleh sumbernya; verifikasi akhir tetap saat signup oleh user/parent.

### C1. RPC / infra Solana (yang paling relevan untuk mesin M1/M3)

| Provider | Free tier | Butuh kartu? | Rate limit | Yang dibukanya untuk stack ini | Catatan |
|----------|-----------|--------------|------------|-------------------------------|---------|
| **Alchemy** ⭐ | **30M Compute Units/bulan** (~3 juta standard read), permanen, tanpa kedaluwarsa | ❌ Tidak | 15–25 RPS (sumber berbeda; halaman resmi terbaru 15 RPS) | RPC + DAS + Photon API; 5 apps, 5 webhooks | **Free tier RPC terbesar.** Satu-satunya yang ~3× Helius dalam volume. Kelemahan: CU per method (getAccountInfo 10 CU, getProgramAccounts 20 CU) — tetap paling murah untuk pola baca M1/M3. |
| **Helius** ⭐ | **1M kredit/bulan** | ❌ Tidak | 10 RPC RPS; DAS 2 RPS; sendTransaction 1/s | **DAS API (holder API!)** — `getAssetsByOwner`, `searchAssets`, holder snapshot tanpa getProgramAccounts mahal; **webhooks** (1 kredit/event); Enhanced Transactions (100 kredit); LaserStream WS (method standar) | **Satu-satunya free tier dengan DAS + webhooks.** DAS = jawaban atas "holder API" yang selama ini tidak ada di RPC publik. 1M kredit ≈ 100 ribu call DAS (10 kredit/call) atau 1 juta RPC standar — cukup untuk polling holder berkala, tidak cukup untuk firehose. |
| **Chainstack** | **3M Request Units/bulan** | ❌ Tidak | 25 RPS umum; **5 RPS di Solana mainnet** | RPC standar; Yellowstone gRPC = premium | 3M RU lumayan, tapi 5 RPS Solana membatasi polling cepat. Cadangan yang bagus. |
| **Shyft** | **Unlimited credits** (tanpa meteran kredit) | ❌ Tidak | 10 RPC RPS; **1 API RPS** | RPC + parsed transaction API + NFT/token API + GraphQL SuperIndexer (program IDL → GraphQL) | Unlimited credits tapi 1 API RPS = hanya ~86 ribu call API/hari, dan gRPC/RabbitStream/accelerated gPA TIDAK termasuk (mulai $199/bln). Berguna untuk parsed-tx sesekali, bukan polling. |
| **dRPC** | 210M CU/bulan klaim publik (~10,5 jt req, ~100 RPS per IP) | ❌ Tidak (public nodes) | ~100 RPS/IP | — | **TIDAK BERLAKU untuk Solana tanpa key** (diuji §B6: chain not available on free plan). Hanya relevan bila user membuat key dashboard; itu pun belum terverifikasi. |
| **QuickNode** | **Trial 1 bulan: 10M credits, 15 RPS** | ❌ Tidak | 15 RPS | RPC + Streams + Webhooks + DAS add-on | **Bukan free tier permanen — trial 1 bulan.** Setelah habis, endpoint berhenti (tidak ada overage). Berguna sebagai booster satu bulan, bukan fondasi. Solana call = 30 credits → 10M credits ≈ 333 ribu call. |
| **GetBlock** | **50K CU/bulan**, 2 endpoint | ❌ Tidak (per sumber) | 20 RPS | RPC multichain | Terlalu kecil (50K CU ≈ ribuan call Solana). Cadangan darurat saja. |
| **Moralis** | **TIDAK ADA free plan** (dihentikan 1 Sep 2026; hanya trial on-request) | — | — | — | Coret. Paid mulai $149/bln. |
| **Triton One** | **TIDAK ADA free tier** — deposit prepaid minimum $125 (PAYG $10/1 jt call + $0,08/GB) | — | — | — | Coret untuk stack gratis. (Yellowstone gRPC penciptanya, tapi berbayar.) |
| **Instanodes** (bonus dari riset) | 600K req/bulan, 40 RPS | ❌ Tidak | 40 RPS | RPC | RPS tertinggi di free tier; volume kecil. Cadangan RPS. |

**Stacking yang masuk akal (semua gratis, tanpa kartu):** Alchemy (volume) + Helius (DAS holder + webhooks) + Chainstack/Shyft (cadangan) + PublicNode (tanpa key, darurat). Total ~4–5 juta read/bulan + DAS + webhooks, $0.

### C2. Data / harga / holder (API kunci)

| Provider | Free tier | Butuh kartu? | Yang dibukanya | Catatan |
|----------|-----------|--------------|----------------|---------|
| **Birdeye Data API** | **Standard Free: 30.000 CU/bulan, 1 RPS**, akses terbatas (3 endpoint menurut satu sumber) | ❌ Tidak (per docs) | Harga, OHLCV, wallet/holder analytics (terbatas), token discovery | 30K CU sangat kecil (≈ ratusan–ribuan call tergantung endpoint); WS TIDAK termasuk (mulai Premium $199). Berguna untuk cek harga/token sesekali, bukan polling. |
| **Jupiter Price API V3** | Gratis tanpa key (sudah dikenal) | — | Harga token | Sudah dipakai; verifikasi singkat cache token list OK (§D). |
| **CoinGecko / GeckoTerminal** | Gratis tanpa key, 30 call/menit | — | Trending, harga, pool | Sudah dipakai. |

### C3. Analitik SQL (bukan real-time — untuk riset/backtest)

| Provider | Free tier | Status 2026 | Catatan |
|----------|-----------|-------------|---------|
| **Dune Analytics** | ❌ **Free plan DIHAPUS 10 Sep 2026** — akses gratis kini view-only (lihat dashboard, tanpa eksekusi query, tanpa API). Pengganti: trial 14 hari, 2.500 kredit total (bukan per bulan). | Mati sebagai sumber gratis | Jangan rencanakan query Dune gratis. Paid mulai $75/bln (Analyst, 4.000 kredit). |
| **Flipside Crypto** | Studio/Dashboards/API **deprecated Juli 2025**; pivot ke Snowflake Marketplace (35+ chain, gratis via Snowflake — tapi butuh akun Snowflake) | Berubah bentuk | Bukan lagi "buka web, tulis SQL, gratis". Hanya relevan bila ada akun Snowflake. |
| **DefiLlama API** | Gratis, 31 endpoint publik, tanpa key (dari riset sekunder) | Jalan | TVL/fees — makro, bukan per-token Solana baru. |

### C4. Sosial (butuh key — untuk narasi bila user membuat key)

| Provider | Free tier | Catatan |
|----------|-----------|---------|
| **Neynar (Farcaster)** | Free: **10M kredit/bulan** (halaman neynar.com saat ini; sumber lama menyebut 100K — angka berubah, pakai yang terbaru saat signup), 600 RPM/endpoint, 1 webhook | ⚠️ **`/cast/search` butuh plan BERBAYAR (402 pada key gratis)** — jadi free tier Neynar TIDAK membuka pencarian narasi. Free tier hanya berguna untuk feed user/channel yang sudah dikenal. |
| **Bluesky** | Tanpa key untuk read publik (kecuali searchPosts yang diblokir dari VM, §A3) | Tidak perlu signup untuk A1/A2. |

---

## D. Data GitHub publik

| # | Sumber | Uji | Hasil |
|---|--------|-----|-------|
| D1 | **solana-labs/token-list** | ✅ `api.github.com/repos/solana-labs/token-list` + raw README terbaca | ⚠️ **EOL / ARCHIVED** — README: "This repository is EOL… as of June 20th, this repository will be archived and will receive no more updates." Jangan jadikan sumber token list. Pengganti: Jupiter (D2) / Metaplex token-metadata. |
| D2 | **Jupiter token list** | ✅ `cache.jup.ag/tokens` → HTTP 200, **66.673.053 byte** | Berfungsi. (`token.jup.ag/all` dan `/strict` gagal koneksi dari VM — pakai cache endpoint.) |
| D3 | **Pump.fun program ID / IDL (GitHub search publik)** | ✅ `api.github.com/search/repositories?q=pump.fun+program+solana` | Ditemukan: `s6nqou/pump-anchor` (Pump.fun Anchor SDK: IDL & CPI only), `AmirAgassi/dump.fun` (sniper, reverse-engineered program), `bilix-software/solana-program-idl-fetcher`. IDL Pump.fun tersedia publik — cukup untuk decode log B2. |
| D4 | **Meteora DLMM IDL (GitHub search publik)** | ✅ `api.github.com/search/repositories?q=meteora+dlmm+idl` | Ditemukan: `fuyofulo/meteora_dlmm_indexer` (dan repo DLMM resmi Meteora sudah dikenal: `MeteoraAg/dlmm-sdk` — tidak diuji ulang di sini, tapi SDK publik). |
| D5 | **DexScreener token-profiles** | ✅ `api.dexscreener.com/token-profiles/latest/v1` → HTTP 200, data profil masuk | Sudah dikenal; verifikasi singkat lolos. |

---

## Rekomendasi 3 teratas (untuk parent/user)

1. **Buat key Helius Free (1M kredit/bulan, tanpa kartu) — prioritas #1.**
   Alasan: satu-satunya free tier yang membuka **DAS = holder API** (yang selama ini tidak ada: holder snapshot, `getAssetsByOwner`, `searchAssets`) **+ webhooks** (alert mint/transfer/swap push, 1 kredit/event). Ini menutup dua celah nyata stack: (a) holder API, (b) feed push selain PumpPortal. Volume 1M kredit/bulan cukup untuk polling holder berkala + webhook event; bukan untuk firehose — pasangkan dengan Alchemy untuk volume baca.
2. **Buat key Alchemy Free (30M CU/bulan, tanpa kartu) — prioritas #2.**
   Alasan: volume baca gratis terbesar (≈3 juta standard read/bulan, 15–25 RPS), permanen. Menjadi RPC utama pengganti endpoint publik yang rate-limit-nya tidak dijamin, sekaligus cadangan bila Helius habis. Tambah DAS/Photon sebagai bonus.
3. **Bangun narasi lapis-3 dari yang sudah terbukti jalan tanpa key — Bluesky Jetstream + Nostr nos.lol + Warpcast search + Telegram `t.me/s/` terkurasi — dengan ekspektasi JUJUR.**
   Alasan: tidak ada pengganti X, dan memaksakan klaim sebaliknya adalah oversell. Lapis ini memberi (a) deteksi kata kunci real-time yang sangat jarang tapi bukan nol (Jetstream), (b) query hashtag Solana yang berfungsi (Nostr), (c) cek pembahasan token di Farcaster (Warpcast), (d) pengumuman resmi proyek (Telegram). Implementasi murah (semua tanpa key, semua sudah teruji jalan dari VM). Ekspektasi: sinyal lemah, frekuensi rendah — tetap kalah dari proxy DexScreener/GeckoTerminal untuk keputusan entry; fungsinya konteks, bukan trigger.

**Tidak direkomendasikan:** Birdeye WS (mulai $199), Moralis (tanpa free), Dune (free dihapus Sep 2026), Triton (deposit $125), QuickNode sebagai fondasi (trial 1 bulan saja), Neynar untuk pencarian narasi (search berbayar, 402 pada free key), Reddit/Lens (mati dari VM), Bluesky searchPosts (403 dari VM), CryptoPanic RSS (410), token-list solana-labs (EOL).

---

## Lampiran — perintah uji (reproduksibilitas)

```bash
# Narasi
curl -s -A "Mozilla/5.0" "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=solana.com&limit=3"
curl -s "https://api.warpcast.com/v2/search-casts?q=solana&limit=3"
curl -s -A "Mozilla/5.0" "https://t.me/s/pumpfun" | grep -o 'tgme_widget_message_text[^<]*'
curl -s -A "Mozilla/5.0" "https://news.google.com/rss/search?q=solana%20memecoin&hl=en-US&gl=US&ceid=US:en"
# Feed
python3 /tmp/g3/ws_test.py   # PumpPortal WS + Solana logsSubscribe (program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P)
python3 /tmp/g3/ws_test2.py  # Bluesky Jetstream + Nostr nos.lol
# GitHub
curl -s "https://cache.jup.ag/tokens" -o jup_cache.json   # 66 MB, HTTP 200
curl -s "https://api.github.com/search/repositories?q=pump.fun+program+solana&per_page=3"
```

**Batas yang diakui:** tidak ada signup dilakukan (tidak ada browser); angka free-tier berasal dari docs/halaman resmi dan ringkasan pihak ketiga yang mengutipnya — harga/limit dapat berubah; Nostr relay lain (`relay.nostr.band`) dan kurasi channel Telegram call belum diuji; parser log Pump.fun (B2) belum dibangun; densitas Jetstream hanya diukur 20 detik (0 hit/300 post) — pengukuran lebih panjang mungkin menemukan hit sesekali, tapi orde besarnya tidak berubah.
