#!/usr/bin/env python3
"""Repro + verifikasi bug urutan argumen score_mint di m3_engine.wallet_score.

Kasus uji (alamat dari wallet-signals.json, 14 Nov 2026):
- HEALTHY_DEPLOYER: GnYdutPAifmH3usS1cRzUjU1UjSxWPGx7de8TVUZkAYi (deployer 2/2 migrasi)
  -> score_mint benar memberi +50.
- FACTORY_BLOCKED: ArLugmai8XHkZY4cvz3hM3jPeEwz7FA7CgZUSXQtZq1X (pabrik 11.769 mint)
  -> score_mint benar memberi blocked=True + score 0.
- FACTORY_BLOCKED2: 6z8ruxQPJLu1kVbeQQ21FQaie1oGTWgkLuGYpoVkYGoS (self-graduated 98,4%)
  -> blocked=True sebagai top holder juga.
Tidak menulis ledger/state; hanya memanggil fungsi murni.
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/solana-trading/m3")
import m3_engine as m3

HEALTHY = "GnYdutPAifmH3usS1cRzUjU1UjSxWPGx7de8TVUZkAYi"
FACTORY = "ArLugmai8XHkZY4cvz3hM3jPeEwz7FA7CgZUSXQtZq1X"
FACTORY2 = "6z8ruxQPJLu1kVbeQQ21FQaie1oGTWgkLuGYpoVkYGoS"
MINT = "TestMint11111111111111111111111111111111111111"

fails = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        fails.append(name)


# 1. Ground truth: panggilan BENAR langsung ke score_mint
sys.path.insert(0, "/home/hatch/workspace/solana-trading/infra")
import wallet_signal
sig = wallet_signal.load_signals(m3.WALLET_SIGNALS_PATH)
r_healthy = wallet_signal.score_mint(MINT, [], HEALTHY, signals=sig)
check("ground-truth healthy deployer skor=50", r_healthy["score"] == 50,
      f"got score={r_healthy['score']} blocked={r_healthy['blocked']}")
r_factory = wallet_signal.score_mint(MINT, [], FACTORY, signals=sig)
check("ground-truth factory creator blocked=True skor=0",
      r_factory["blocked"] is True and r_factory["score"] == 0,
      f"got score={r_factory['score']} blocked={r_factory['blocked']}")
r_factory2 = wallet_signal.score_mint(
    MINT, [{"owner": FACTORY2, "pct": 5.0}], HEALTHY, signals=sig)
check("ground-truth factory sbg top holder blocked=True",
      r_factory2["blocked"] is True, f"got blocked={r_factory2['blocked']}")

# 2. Wrapper m3_engine.wallet_score (yang dipakai evaluate_candidate)
w_healthy = m3.wallet_score(MINT, [], HEALTHY)
check("m3.wallet_score healthy deployer skor=50",
      w_healthy.get("score") == 50,
      f"got score={w_healthy.get('score')} blocked={w_healthy.get('blocked')}")
w_factory = m3.wallet_score(MINT, [], FACTORY)
check("m3.wallet_score factory creator blocked=True skor=0",
      w_factory.get("blocked") is True and w_factory.get("score") == 0,
      f"got score={w_factory.get('score')} blocked={w_factory.get('blocked')}")
w_factory2 = m3.wallet_score(MINT, [{"owner": FACTORY2, "pct": 5.0}], HEALTHY)
check("m3.wallet_score factory sbg top holder blocked=True",
      w_factory2.get("blocked") is True,
      f"got blocked={w_factory2.get('blocked')}")

# 3. Konsekuensi gate: skip wallet_blocked_factory harus bisa menyala
check("gate wallet_blocked_factory menyala utk factory",
      bool(w_factory.get("blocked")), "skip di m3_engine.py:663-664")

print()
print("HASIL:", "SEMUA PASS" if not fails else f"{len(fails)} GAGAL: {fails}")
sys.exit(1 if fails else 0)
