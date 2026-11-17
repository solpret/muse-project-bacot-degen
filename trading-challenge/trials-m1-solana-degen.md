# Log Trial — M1 BACOT DEGEN Solana (paper)

**Metode:** mesin `~/workspace/solana-trading/paper_run_solana.py` (cron 15 menit,
trial 14–21 Nov 2026, modal virtual 0,08 SOL).
**Definisi trial:** 1 trade tertutup oleh mesin; menang = `realized_sol` > 0.
**Aturan:** trial dihitung bila EXIT sesudah challenge mulai (14 Nov 2026
20:34 WIB), dalam urutan close. Trial TIDAK PERNAH dibuang/diulang.
**Sumber kebenaran:** `~/workspace/solana-trading/ledger.json` (`trades[]`).
Update otomatis: `python3 update_scoreboard.py sync`.

## Posisi open saat challenge dibuat
| Token | Entry | Ukuran | Catatan |
|---|---|---|---|
| 8azHd6ZpAdpyFzGAaNkofyKhr19RWNNquSC8bAGEpump | 14 Nov 2026 20:26:36 WIB | 0,024 SOL @ $0,00005775 | Masuk SEBELUM challenge; bila tutup sesudah 20:34 WIB menjadi trial 1 ronde 1 |

## Ronde 1 (terbuka, 1W/1L — 2/10 tertutup, update 14 Nov ~22:00 WIB)
| # | Token | Entry → Exit | Alasan exit | Realized (SOL) | Hasil |
|---|---|---|---|---|---|
| 1 | 8azHd6ZpAdpyFzGAaNkofyKhr19RWNNquSC8bAGEpump | 20:26:36 → 21:21:26 WIB | take_profit_+30% | +0,007950477 | MENANG |
| 2 | 8azHd6ZpAdpyFzGAaNkofyKhr19RWNNquSC8bAGEpump (re-entry 21:27:18 WIB) | 21:27:18 → 21:51:47 WIB | stop_loss_-15% | −0,023545073 | KALAH |

**Catatan trial 2 (temuan audit, bukan vonis):** stop-loss −15% dimaksudkan membatasi rugi di ~0,0204 SOL, tapi exit_sol terealisasi 0,000474927 SOL (−98% dari size) — harga/quote jual runtuh antara pengecekan SL dan eksekusi jual. SL tidak melindungi seperti yang dirancang pada keruntuhan cepat; diselidiki untuk ronde berikut (bukan perbaikan tengah ronde).
**Method fix audit 14 Nov ~22:00 WIB:** `last_value_sol` = size saat entry (fallback ekuitas bila re-price gagal). Detail: CHALLENGE.md §2 M1.

## Ronde-ronde berikut
Belum ada. Ronde 2 dibuka otomatis oleh updater: ronde validasi bila ronde 1
lolos (metode sama), atau ronde perbaikan bila ronde 1 gagal (butuh perintah
`fix` dengan perubahan metode yang didokumentasikan).
