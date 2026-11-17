# Audit Sweep G2 — RPC Publik Solana

- **Tanggal:** Sabtu 2026-11-14, ~21:30–21:45 WIB
- **Auditor kaki:** G2 (sweep RPC publik)
- **Mint uji:** 8azHd6ZpAdpyFzGAaNkofyKhr19RWNNquSC8bAGEpump (mint M1 yang open; program pemilik **Token-2022** `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`, supply 963.363.833,712024, desimal 6)
- **Metode:** JSON-RPC POST via Python urllib, timeout 20 dtk/panggilan, jeda 1,2 dtk antar panggilan (tidak menembak bertubi-tubi). Slot selama sweep: ~469.362.150–469.364.747.
- **Skrip:** `/tmp/g2_sweep.py`, `/tmp/g2_followup.py`, `/tmp/g2_ws.py` (hasil mentah `/tmp/g2_sweep_results.json`, log `/tmp/g2_sweep.log`)

## Temuan utama (baca ini dulu)

1. ✅ **CELAH #1 TERTUTUP — `getTokenLargestAccounts` ADA yang melayani gratis: `https://public.rpc.solanavibestation.com`** (Solana Vibe Station, public, tanpa key). **4 dari 4 panggilan OK** (n=20 tiap kali; top holder bergerak 126,09 jt → 124,92 jt → 122,32 jt → 120,62 jt → 122,50 jt token antar panggilan = data live, bukan cache). Alchemy demo sempat OK 1× lalu 429 permanen — **bukan** jalan keluar.
2. ✅ **CELAH #2 TERTUTUP — `getProgramAccounts` enumerasi holder BERHASIL di mainnet-beta DAN SVS**, asal filternya benar: program **Token-2022** + `memcmp` mint offset 0, **TANPA filter `dataSize: 165`** → **4.840 akun (4.707 bersaldo >0), identik di kedua endpoint** (SVS 3,7 dtk; mainnet-beta 2,7 dtk).
3. ⚠️ **Jebakan `dataSize: 165`:** dengan filter itu hanya 3 akun kembali. Akun Token-2022 yang punya extension berukuran >165 byte, jadi filter 165 nyaris mengosongkan hasil. **Jangan pernah pakai `dataSize: 165` untuk Token-2022.** (Untuk mint program Token legacy, 165 tetap benar.)
4. ⚠️ **Koreksi nama method:** `getParsedTokenAccountsByOwner` **TIDAK ADA** di Solana RPC (semua endpoint: `-32601 Method not found`). Nama benarnya **`getTokenAccountsByOwner`** (+ `encoding: jsonParsed`) — dan itu **OK di mainnet-beta (2,82 dtk) maupun SVS (2,44 dtk)**.
5. ✅ **CELAH #3 & #4 TERTUTUP di mainnet-beta + SVS:** `getSignaturesForAddress` (limit 5 OK), `getTokenSupply`, `getAccountInfo`, `getMultipleAccounts` semua OK.
6. ⚠️ **WebSocket SEBAGIAN tertutup:** `accountSubscribe` berhasil di `wss://api.mainnet-beta.solana.com` (sub id 212068917) dan `wss://solana-rpc.publicnode.com` (sub id 274692); koneksi bertahan 8 dtk tanpa notifikasi (wajar — akun mint statis). `logsSubscribe`/`programSubscribe` **belum diuji**. WS RPC **bukan** pengganti trade stream (tidak ada feed trade via RPC).
7. ❌ **Mayoritas endpoint publik MATI dari VM ini** — sebagian besar karena Cloudflare error **1010** (IP egress VM kemungkinan ter-flag sebagai bot): PublicNode, GenesysGo, dRPC, BlockPI, 1RPC semua 403/1010 di HTTPS. Hasil untuk endpoint-endpoint itu bisa berbeda dari IP lain.

## Matriks endpoint × method

Legenda: ✅ OK (latensi) · ❌ GAGAL (kode + pesan) · `—` tidak diuji di jalur itu

| # | Endpoint | getHealth | getSlot | getTokenLargestAccounts | getTokenSupply | getAccountInfo | getSignaturesForAddress (limit 5) | getMultipleAccounts | getTokenAccountsByOwner* | getProgramAccounts† |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | api.mainnet-beta.solana.com | ✅ 1,09 dtk | ✅ 0,91 dtk | ❌ HTTP 429 `Too many requests for a specific RPC call` | ✅ 1,02 dtk | ✅ 0,91 dtk | ✅ 1,47 dtk (n=5) | ✅ 0,86 dtk | ✅ 2,82 dtk | ✅ 2,7 dtk (memcmp-only, 4.840 akun) |
| 2 | api.mainnet.solana.com | ✅ 1,06 dtk | ✅ 2,75 dtk | ❌ HTTP 429 (sama) | ✅ 2,63 dtk | ✅ 2,65 dtk | ✅ 1,95 dtk | ✅ 2,22 dtk | (tidak diuji ulang; alias host sama) | (tidak diuji ulang) |
| 3 | solana.public-rpc.com | ❌ SSL `CERTIFICATE_VERIFY_FAILED: self-signed certificate` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 4 | solana-rpc.publicnode.com | ❌ HTTP 403 `error code: 1010` (Cloudflare) | ❌ 403/1010 | ❌ 403/1010 | ❌ 403/1010 | ❌ conn closed | ❌ 403/1010 | ❌ 403/1010 | ❌ 403/1010 | ❌ 403/1010 |
| 5 | ssc-dao.genesysgo.net | ❌ HTTP 403 `error code: 1010` | ❌ 403/1010 | ❌ conn closed | ❌ 403/1010 | ❌ 403/1010 | ❌ conn closed | ❌ 403/1010 | ❌ 403/1010 | ❌ 403/1010 |
| 6 | rpc.ankr.com/solana | ❌ HTTP 403 `API key is not allowed to access blockchain, json-rpc code: -32052, rest code: 403` (semua method; dulu 401, kini 403 — tetap mati) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 7 | solana.drpc.org | ❌ HTTP 403 `error code: 1010` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 8 | solana.blockpi.network/v1/rpc/public | ❌ HTTP 403 `error code: 1010` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 9 | 1rpc.io/sol | ❌ HTTP 403 `error code: 1010` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 10 | api.metaplex.solana.com | ❌ `Remote end closed connection without response` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 11 | solana-mainnet.g.alchemy.com/v2/demo | ✅ 0,88 dtk | ❌ HTTP 429 | ⚠️ **OK 1×** (0,98 dtk, n=20, top 128.361.283,068295) lalu ❌ 429 di retest #2, #3, dan retest cooldown (tetap 429) | ❌ HTTP 429 | ❌ HTTP 429 | ❌ HTTP 429 | ❌ HTTP 429 | ❌ HTTP 429 | ❌ HTTP 429 |
| 12 | rpc.helius.xyz/?api-key= (tanpa key) | ❌ TIMEOUT 20 dtk | ❌ TIMEOUT 20 dtk | ❌ TIMEOUT 20 dtk | ❌ TIMEOUT 20 dtk | ❌ HTTP 401 `Unauthorized` | ❌ HTTP 401 | ❌ HTTP 401 | ❌ HTTP 401 | ❌ HTTP 401 |
| 13 | public.rpc.blxrbdn.com (bloXroute) | ❌ `Remote end closed connection without response` (semua method — host ini ETH-only) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 14 | rpc.magicblock.app/mainnet | ❌ HTTP 403 halaman `Access Restricted - Magicblock` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 15 | **public.rpc.solanavibestation.com** | ✅ 2,07 dtk | ✅ 3,06 dtk | ✅ **OK 4×** (3,52 / 1,04 / 3,08 / 2,38 dtk; n=20) | ✅ 2,66 dtk | ✅ 1,58 dtk | ✅ 2,11 dtk (n=5) | ✅ 2,13 dtk | ✅ 2,44 dtk | ✅ 3,89 dtk (memcmp-only, 4.840 akun) |
| 16 | solana.leorpc.com (tanpa key) | ❌ HTTP 401 `{"message":"missing key"}` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 17 | solana.api.onfinality.io/public | ❌ HTTP 429 `-32029 Too Many Requests, Please apply an OnFinality API key or contact us to receive a higher rate limit` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |
| 18 | solana-mainnet.rpcpool.com | ❌ HTTP 403 `{"code": 403, "message": "Access forbidden"}` (semua method) | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama | ❌ sama |

\* Kolom `getTokenAccountsByOwner` = nama method **benar** (diuji di follow-up). Di sweep awal, nama salah `getParsedTokenAccountsByOwner` dipakai sesuai tugas → semua endpoint menjawab `-32601 Method not found` (SVS menjawab eksplisit `Method not found: getParsedTokenAccountsByOwner is not supported`).

† Kolom `getProgramAccounts` = filter **benar** (program Token-2022 + `memcmp` mint offset 0, tanpa `dataSize`). Di sweep awal, filter program Token legacy + `dataSize: 165` dipakai sesuai tugas → mainnet-beta/SVS menjawab OK tapi `n=0` (bukan gagal — mint ini Token-2022, jadi program legacy memang tidak punya akunnya; dan `dataSize: 165` saja hanya mengembalikan 3 akun).

### WebSocket (uji terpisah, `accountSubscribe` pada mint uji, tunggu 8 dtk)

| Endpoint WS | Hasil |
|---|---|
| wss://api.mainnet-beta.solana.com | ✅ SUBSCRIBED (id 212068917), koneksi bertahan 8 dtk, 0 notifikasi (akun mint statis — wajar) |
| wss://solana-rpc.publicnode.com | ✅ SUBSCRIBED (id 274692), koneksi bertahan 8 dtk, 0 notifikasi — **WS PublicNode hidup meski HTTPS-nya 403/1010 dari VM ini** |

`logsSubscribe` / `programSubscribe` belum diuji.

## Bukti holder untuk mint uji (via SVS)

- `getTokenLargestAccounts`: n=20; **top1 12,72%, top5 16,33%, top20 23,83%** dari supply (pengukuran terakhir; top1 bergerak 126,09 jt → 120,62 jt → 122,50 jt antar panggilan — holder aktif jual/beli).
- Top 5 (alamat ATA + jumlah): 8PFNBTov… 122.503.339,26 · 3U7F84MJ… 16.853.613,22 · 8RHeDC7s… 6.150.256,53 · 8HAX6byd… 5.980.000,69 · DZPjBkSb… 5.846.582,15.
- `getProgramAccounts` (Token-2022, memcmp-only): **4.840 akun total, 4.707 bersaldo >0** — angka identik di SVS dan mainnet-beta.

## Kesimpulan per celah

| Celah | Status | Penutup |
|---|---|---|
| 1. `getTokenLargestAccounts` (distribusi/top holder) | ✅ **TERTUTUP** | **Solana Vibe Station public** — satu-satunya endpoint gratis yang melayani dari VM ini, 4/4 OK. Alchemy demo hanya 1 hit lalu 429 — tidak bisa diandalkan. |
| 2. `getProgramAccounts` (enumerasi holder / posisi DLMM) | ✅ **TERTUTUP untuk holder**; ⚠️ belum untuk DLMM | Holder: Token-2022 + memcmp-only, OK di mainnet-beta & SVS (4.840 akun). **Posisi DLMM Meteora & Pump.fun belum diuji** — `getProgramAccounts` tanpa filter pada program itu sangat berat; butuh uji terpisah dengan filter diskriminatif (mis. memcmp owner/posisi) sebelum dipakai. |
| 3. `getSignaturesForAddress` (aktivitas / umur token) | ✅ **TERTUTUP** | mainnet-beta & SVS, limit 5 OK (~1,5–2,1 dtk). |
| 4. `getTokenSupply`, `getAccountInfo`, `getMultipleAccounts`, `getTokenAccountsByOwner` | ✅ **TERTUTUP** | mainnet-beta & SVS semua OK. |
| 5. WebSocket publik | ⚠️ **SEBAGIAN** | `accountSubscribe` OK di mainnet-beta & PublicNode WS. Bukan pengganti trade stream; `logsSubscribe`/`programSubscribe` belum diuji. |

## Rekomendasi pemakaian (untuk M1/M3)

1. **Snapshot holder berkala → SVS public (`https://public.rpc.solanavibestation.com`)**, SATU-SATUNYA sumber `getTokenLargestAccounts` gratis yang terbukti. Pakai hemat: maks ~1 panggilan per token per run engine, sekuensial dengan jeda ≥1 dtk (dokumen pihak ketiga mengukur public endpoint ini ~1 req/s; latensi terukur 1,0–3,5 dtk; tanpa SLA, limit bisa berubah sewaktu-waktu).
2. **Data dasar + signatures + enumerasi holder → `https://api.mainnet-beta.solana.com`** (latensi ~1 dtk, paling responsif). `getTokenLargestAccounts` di sini 429 persisten — jangan pernah memakainya untuk method itu; lempar ke SVS.
3. **Failover:** SVS ↔ mainnet-beta saling menutup semua method kecuali `getTokenLargestAccounts` (hanya SVS). Alchemy demo hanya sebagai tembakan terakhir sekali (ekspektasi: 429).
4. **JANGAN dipakai dari VM ini:** PublicNode/dRPC/BlockPI/1RPC/GenesysGo HTTPS (Cloudflare 1010), Ankr (403), Helius & LeoRPC tanpa key (401), MagicBlock (403), rpcpool (403), Metaplex (koneksi ditutup), bloXroute Solana (ETH-only), solana.public-rpc.com (TLS self-signed + `curl -k` gagal HTTP 000).
5. **Aturan filter `getProgramAccounts`:** tentukan dulu program pemilik mint dari `getAccountInfo` (Token legacy vs Token-2022). Token-2022 → **tanpa `dataSize`**, hanya `memcmp` mint offset 0. Token legacy → `dataSize: 165` + `memcmp` boleh.
6. **WebSocket:** `wss://api.mainnet-beta.solana.com` untuk `accountSubscribe` (monitoring posisi/mint); `wss://solana-rpc.publicnode.com` sebagai cadangan. Jangan jadikan pengganti trade stream.
7. **Catatan kehati-hatian:** (a) Semua hasil diukur dari IP egress VM ini — endpoint yang 403/1010 di sini (khususnya PublicNode & MagicBlock, yang dilaporkan pihak lain berfungsi) mungkin hidup dari IP lain; bila SVS mati suatu hari, uji ulang PublicNode/MagicBlock dari lokasi lain sebelum menyimpulkan mati total. (b) Top-holder bergerak antar panggilan dalam hitungan menit — snapshot WAJIB dicap waktu. (c) `getProgramAccounts` memcmp-only pada mint ramai mengembalikan ribuan akun (di sini 4.840, ~3–4 dtk) — untuk mint jauh lebih besar, siapkan pagination/timeout lebih panjang.

## Yang TIDAK diuji (batas audit ini)

- `getProgramAccounts` program Pump.fun & Meteora DLMM (butuh filter terarah; tanpa filter berisiko timeout/429).
- `logsSubscribe` / `programSubscribe` via WS.
- Free tier ber-key (Alchemy/Chainstack/dRPC/Helius/QuickNode/OnFinality dengan API key gratis) — di luar ruang lingkup "tanpa key" kaki ini; layak jadi kaki terpisah bila SVS goyah.
- Perilaku rate limit SVS di bawah beban (hanya diuji sekuensial ringan, bukan burst).
