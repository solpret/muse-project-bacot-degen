# MANIFEST — muse-project-bacot-degen

- **Tanggal:** 20 November 2026
- **Repo publik:** `muse-project-bacot-degen` — https://github.com/solpret/muse-project-bacot-degen
- **Ukuran:** 16 MB (16.028.300 byte), 117 file
- **Cakupan:** Project BACOT DEGEN — paper trading mandiri Solana (M1)
  + riset LP / track M2 (DLMM).

## Isi

| Bagian | Isi |
|---|---|
| `goals/model-degen-paper-trading-mandiri/` | Goal BACOT DEGEN (mesin mandiri, tanpa sinyal Modal Bacot) |
| `goals/riset-penyedia-likuiditas/` | Riset LP: metode CryptoSundayz, hasil paper DLMM Solana (STANK/AMD), harness `paper_lp_dlmm.py`, kalibrasi fee on-chain |
| `solana-trading/paper_run_solana.py`, `ledger.json` | Engine M1 + ledger (kill switch aktif, trial berakhir 21 Nov) |
| `solana-trading/m2/` | Runner live paper M2 (`m2_runner.py`, dibangun 17 Nov 2026) |
| `solana-trading/audit-*.md`, `audit-verify-m1-20261114.py`, `repro_wallet_bug.py` | Audit + verifikasi M1 |
| `trading-challenge/trials-m1-solana-degen.md`, `trials-m2-lp-dlmm-solana.md` | Log trial M1 + M2 |

## Catatan M2
Track M2 (LP CryptoSundayz DLMM Solana) dicatat di tree ini: metodenya
di `goals/riset-penyedia-likuiditas/`, runner-nya di `solana-trading/m2/`,
log trial-nya di `trading-challenge/trials-m2-lp-dlmm-solana.md`.
Backtest historis 3–14 Nov adalah bukti ronde-0, BUKAN trial challenge.

## Yang sengaja TIDAK ikut / ada di tempat lain
- File `.bak*`, `.log`, `.jsonl`, DB — dibuang.
- `CHALLENGE.md` + scoreboard ada di `common/` (repo `muse-project-common`).
- Ingest Solana ada di `common/infra/`.

## Pembaruan 2026-11-20 (sejak 17 Nov)
- Trading DIHENTIKAN user 19 Nov 18:22 WIB (cron paper-trading 15m +
  solana-ingest-watchdog diperbarui).
- Ledger M1 (`solana-trading/ledger.json`) + M2 (`m2/m2-ledger.json`)
  diperbarui; 3 log run paper LP 17–18 Nov
  (`paper_lp_dlmm_live_*.json`, ~5 KB tiap file) sebagai bukti trial M2;
  `hidden_files/` + `crons/` baru di goals.
- Pemecahan repo: TIDAK diperlukan — tree 16 MB; tidak ada file >90 MB.

## Audit rahasia
Bersih (20 Nov 2026, `audit-secret-2026-11-20.txt` di folder induk):
0 temuan bernilai — layak repo publik.
