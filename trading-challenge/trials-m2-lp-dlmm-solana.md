# Log Trial — M2 LP CryptoSundayz DLMM Solana (native)

**Metode:** parameter author apa adanya (Meteora DLMM, Solana) — screening
SOL pair, bin step 80/100/200, TVL $5k–$150k, mcap $300k–$20M, holder ≥500,
umur ≥3 jam, vol 30 mnt ≥$3k, freeze/mint authority mati, tanpa tax; range
miring −60%/+5%; TP +8%; tembus atas → tunggu ~10 mnt / tutup bila untung
≥0,5% / reposisi maks 2x; bawah range >4 jam + vol 1 jam <$20k → tutup;
stop darurat PnL −50% / harga −80%; maks hold 48 jam; safety 5 mnt pertama,
cross-check PnL, pause sesudah 2 rugi beruntun.
**Definisi trial:** 1 posisi LP lengkap entry → exit; menang = net vs HODL > 0.
**Sumber kebenaran:** hasil paper trade subagen LP Solana (file
`paper_lp_*solana*.json` / `paper_lp_*dlmm*.json` di
`~/workspace/goals/riset-penyedia-likuiditas/hidden_files/`).
Update otomatis: `python3 update_scoreboard.py sync` (impor file hasil baru).

## Status ronde 1
**MENUNGGU** hasil subagen LP Solana (di-spawn 14 Nov 2026 20:32 WIB, masih
jalan saat challenge dibuat). JANGAN duplikasi kerjanya. Begitu file hasil
muncul, updater mengimpor trade-nya sebagai trial 1–10 ronde 1.

## Evaluasi pra-challenge (kenapa venue dipindah — BUKAN skor challenge)
Adaptasi V3 BNB: SI/WBNB 9 trade 0 menang vs HODL (net −$48,39), NODE/WBNB
1 trade net −$0,08. Tiga temuan struktural (lihat CHALLENGE.md §6):
TP +8% tak terjangkau dari posisi ~94% WBNB; exit tembus-atas memotong
upside; aturan bawah-range+volume redundan. Perbaikan yang diambil: pindah
ke venue asli author (DLMM Solana) — trial BSC tidak dipakai ulang.

## Ronde 1 (menunggu, 0/10)
| # | Pool | Entry → Exit | Alasan exit | Net vs HODL (USD) | Fee / IL (USD) | Hasil |
|---|---|---|---|---|---|---|
| _menunggu file hasil subagen LP_ | | | | | | |
