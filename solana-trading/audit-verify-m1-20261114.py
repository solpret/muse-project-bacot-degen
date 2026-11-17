#!/usr/bin/env python3
"""Verifikasi matematika M1 Solana (audit kaki A, 14 Nov 2026) — read-only thd ledger.
Import paper_run_solana sebagai modul (main tidak jalan saat import).
"""
import sys, json, copy
sys.path.insert(0, "/home/hatch/workspace/solana-trading")
import paper_run_solana as m

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"PASS {name} {detail}")
    else: FAIL += 1; print(f"FAIL {name} {detail}")

# 1. Konstanta ambang (daftar lengkap untuk koordinator)
consts = {k: getattr(m, k) for k in
    ["VIRTUAL_CAPITAL_SOL","MAX_POSITION_SOL","MAX_OPEN","DAILY_BUDGET_SOL",
     "DUST_MIN_SOL","EST_FEE_SOL","RUN_DEADLINE_SECS","MIN_CANDLES","MIN_HOLDERS",
     "MAX_TOP1_PCT","MAX_TOP10_PCT","MAX_CREATOR_PCT","MIN_LP_LOCK_PCT",
     "MAX_RUGCHECK_SCORE","MAX_NEW_PER_RUN","MAX_DEPLOY_PCT","TRIAL_KILL_DRAWDOWN",
     "SIGHTING_GROWTH_HOLDERS","SIGHTING_GROWTH_POOL","SIGHTING_MAX_AGE_HOURS",
     "MAX_AGE_HOURS","POOL_PAIR_WORKERS","POOL_QUOTE_WORKERS","POOL_AUDIT_WORKERS",
     "POOL_UNIVERSE_WORKERS"]}
print("KONSTANTA:", json.dumps(consts, indent=0))
check("modal 0.08", m.VIRTUAL_CAPITAL_SOL == 0.08)
check("max_pos 0.024", m.MAX_POSITION_SOL == 0.024)
check("dust 0.004", m.DUST_MIN_SOL == 0.004)
check("budget 0.008", m.DAILY_BUDGET_SOL == 0.008)
check("kill 30% -> ambang ~0.056", abs((1-m.TRIAL_KILL_DRAWDOWN)*0.08-0.056) < 1e-12, f"nilai float={(1-m.TRIAL_KILL_DRAWDOWN)*0.08!r}")

# 2. Ukuran posisi: min(0.024, 1% reserve SOL); dust guard
def size(reserve_usd, sol_price):
    sol_res = reserve_usd/2.0/sol_price
    return min(m.MAX_POSITION_SOL, 0.01*sol_res)
check("size cap 0.024 (reserve besar)", size(20055.9452, 75.16) == 0.024,
      f"got {size(20055.9452,75.16)}")
check("size reserve 3000 -> cap 0.024 (1% dari 20 SOL reserve = 0.2, kena cap)",
      abs(size(3000,75.0)-0.024)<1e-12, f"{size(3000,75.0)}")
check("size reserve 300 -> 0.02 (1% dari 2 SOL reserve, di bawah cap)",
      abs(size(300,75.0)-0.02)<1e-12, f"{size(300,75.0)}")
check("size reserve 60000 -> cap 0.024 (1% reserve=4 SOL, kena cap)",
      abs(size(60000,75.0)-0.024)<1e-12, f"{size(60000,75.0)}")
check("size reserve 60 -> 0.004 tepat (1% dari 0.4 SOL reserve)",
      abs(size(60,75.0)-0.004)<1e-12, f"{size(60,75.0)}")
check("size reserve 30 -> 0.002 dust-block (<0.004)",
      abs(size(30,75.0)-0.002)<1e-12, f"{size(30,75.0)}")
# reserve entry posisi ledger: 20055.9452/2/75.16 ~133.4 SOL -> 1% =1.334 -> cap 0.024 OK

# 3. Kas ledger: rekonstruksi aritmetika dari ledger.json saat ini
led = json.load(open("/home/hatch/workspace/solana-trading/ledger.json"))
# start 0.08 - entry1 (0.024+0.00001) + sell1 proceeds (0.031970477-0.00001) - entry2 (0.024+0.00001)
calc = 0.08 - 0.02401 + (0.031970477-0.00001) - 0.02401
check("kas ledger == rekonstruksi 2 entry + 1 sell",
      abs(led["cash_sol"]-calc) < 1e-9, f"ledger={led['cash_sol']} calc={calc}")
check("realized sell1", abs(led["trades"][0]["realized_sol"] -
      (0.031970477-0.00001-0.024-0.00001)) < 1e-12,
      f"{led['trades'][0]['realized_sol']}")
check("daily realized == trade realized",
      abs(led["daily"]["2026-11-14"]["realized_sol"]-led["trades"][0]["realized_sol"])<1e-12)
check("daily entries==2 exits==1",
      led["daily"]["2026-11-14"]["entries"]==2 and led["daily"]["2026-11-14"]["exits"]==1)

# 4. Kill-switch EKUITAS (bukan kas saja) — replika rumus main()
def equity(led_, last_values):
    return led_["cash_sol"] + sum(last_values)
# Skenario A: kas 0.05599 (sesudah entry1) + posisi bernilai 0.03197 -> ekuitas 0.08796 > 0.056, TIDAK kill
check("kill-switch TIDAK trip saat kas<0.056 tapi ekuitas tinggi",
      not (equity({"cash_sol":0.05599},[0.03197]) < 0.056),
      f"equity={0.05599+0.03197:.5f}")
# Skenario B: kas saja 0.05599 < 0.056 -> rumus kas-saja AKAN salah trip; rumus ekuitas tidak
check("rumus kas-saja akan salah-trip (kontrol negatif)", 0.05599 < 0.056)
# Skenario C: ekuitas benar-benar <0.056 -> trip
check("kill-switch trip saat ekuitas 0.05", 0.05 < (1-m.TRIAL_KILL_DRAWDOWN)*0.08)
# Skenario D (CELAH): posisi baru tanpa last_value_sol -> kontribusi 0
pos_no_lv = {"entry_sol":0.024}
eq_d = 0.05599 + sum(float(p.get("last_value_sol") or 0) for p in [pos_no_lv])
check("CELAH: posisi tanpa last_value_sol dihitung 0 -> ekuitas semu 0.05599 < 0.056 (salah-trip bila exit re-price gagal)",
      eq_d < 0.056, f"equity_semu={eq_d}")
# Catatan: di main(), exit-loop me-reprice dulu sebelum kill-switch, jadi jalur normal aman;
# celah hanya bila re-price gagal (STUCK).

# 5. Exit ratios: TP +30% (1.30), stop -15% (0.85), trailing 0.85*peak, collapse 0.5x reserve
def exit_reason(ratio, peak, reserve, entry_reserve, chart_dump=False):
    if ratio <= 0.85: return "stop_loss_-15%"
    if ratio >= 1.30: return "take_profit_+30%"
    if chart_dump: return "chart_dump_fast"
    if peak > 1.0 and ratio <= 0.85*peak: return "trailing_-15%_from_peak"
    if reserve < 0.5*entry_reserve: return "liquidity_collapse_>50%"
    return None
check("TP di 1.30", exit_reason(1.30,1.30,100,100)=="take_profit_+30%")
check("TP sell1: exit 0.03197/0.024=1.332 -> TP", abs(0.031970477/0.024-1.3321)<0.001)
check("stop di 0.85", exit_reason(0.85,1.0,100,100)=="stop_loss_-15%")
check("trailing peak 1.20 ratio 1.02 (=0.85*1.20)", exit_reason(1.02,1.20,100,100)=="trailing_-15%_from_peak")
check("trailing TIDAK trip di 1.03", exit_reason(1.03,1.20,100,100) is None)
check("collapse reserve 0.49x", exit_reason(1.0,1.0,49,100)=="liquidity_collapse_>50%")
check("collapse TIDAK di 0.51x", exit_reason(1.0,1.0,51,100) is None)

# 6. LP fallback: summary=0 -> max per-market; summary>0 -> summary dipakai; 0/0 tetap blokir
def mk_report(lp_summary, markets):
    return {"topHolders":[{"pct":1.0}],"totalHolders":100,"token":{"supply":1000,"decimals":6},
            "creator":"DevX","creatorBalance":0,"lockers":{},"markets":markets,"rugged":False}
s = {"lpLockedPct":0}
r = mk_report(0, [{"lp":{"lpLockedPct":100}},{"lp":{"lpLockedPct":20}}])
h = m.holder_analysis(r, s)
check("LP fallback summary0 -> per_market 100", h["lp_locked_pct"]==100.0 and h["lp_source"]=="per_market" and h["gate_block"] is None, str(h))
s2 = {"lpLockedPct":80}
h2 = m.holder_analysis(mk_report(80, [{"lp":{"lpLockedPct":100}}]), s2)
check("LP summary 80 dipakai, bukan max per-market", h2["lp_locked_pct"]==80.0 and h2["lp_source"]=="summary", str(h2))
h3 = m.holder_analysis(mk_report(0, [{"lp":{"lpLockedPct":0}}]), {"lpLockedPct":0})
check("LP 0/0 tetap blokir", h3["gate_block"] is not None and "LP:" in h3["gate_block"], str(h3))
h4 = m.holder_analysis(mk_report(0, []), {"lpLockedPct":0})
check("LP 0 tanpa markets tetap blokir, source summary", h4["gate_block"] is not None and h4["lp_source"]=="summary", str(h4))
# CELAH: max lintas SEMUA market (bukan market utama) — market kecil 100% bisa meloloskan
h5 = m.holder_analysis(mk_report(0, [{"lp":{"lpLockedPct":0}},{"lp":{"lpLockedPct":100}}]), {"lpLockedPct":0})
check("CELAH-DOK: max semua market (market kecil 100% meloloskan)", h5["lp_locked_pct"]==100.0, str(h5))

# 7. Holder gates
def holder_case(top1, top10_n, total, creator_pct):
    th=[{"pct":top1}]+[{"pct":(top10_n-top1)/9}]*9
    rep={"topHolders":th,"totalHolders":total,"token":{"supply":1000,"decimals":6},
         "creator":"DevX","creatorBalance":creator_pct*10,"lockers":{"a":1},"markets":[],"rugged":False}
    return m.holder_analysis(rep, {"lpLockedPct":100})
check("holder top1 25.01 blokir", holder_case(25.01,30,100,0)["gate_block"] is not None)
check("holder top1 25.0 lolos", holder_case(25.0,30,100,0)["gate_block"] is None)
check("holder top10 60.01 blokir", holder_case(10,60.01,100,0)["gate_block"] is not None)
check("holder 49 blokir", holder_case(10,30,49,0)["gate_block"] is not None)
check("holder creator 15.01 blokir", holder_case(10,30,100,15.01)["gate_block"] is not None)

# 8. Audit gate
base_rep={"score_normalised":20,"risks":[],"token":{"mintAuthority":None,"freezeAuthority":None},"rugged":False,"transferFee":{"pct":0}}
check("audit bersih lolos", m.audit_gate(copy.deepcopy(base_rep),{}) is None)
bad=copy.deepcopy(base_rep); bad["score_normalised"]=31
check("audit skor 31 blokir", m.audit_gate(bad,{}) is not None)
bad=copy.deepcopy(base_rep); bad["risks"]=[{"level":"danger","name":"X"}]
check("audit danger blokir", m.audit_gate(bad,{}) is not None)
bad=copy.deepcopy(base_rep); bad["token"]["mintAuthority"]="abc"
check("audit mintAuthority blokir", m.audit_gate(bad,{}) is not None)
bad=copy.deepcopy(base_rep); bad["transferFee"]={"pct":5}
check("audit transferFee blokir", m.audit_gate(bad,{}) is not None)
bad={"score_normalised":None,"risks":[],"token":{},"rugged":False}
check("audit tanpa skor blokir (fail-closed)", m.audit_gate(bad,{"score_normalised":None}) is not None)

# 9. Sighting 2-sighting: +10% holder & +5% reserve
led2={"sightings":{}}
b1=m.sighting_block(led2,"MintAAA",{"holder_count":100},1000.0)
check("sighting pertama catat baseline", b1 is not None and "baseline dicatat" in b1 and "mintaaa" in led2["sightings"])
b2=m.sighting_block(led2,"MintAAA",{"holder_count":109},1049.0)
check("sighting growth 9%/4.9% BELUM lolos", b2 is not None, b2 or "")
b3=m.sighting_block(led2,"MintAAA",{"holder_count":110},1050.0)
check("sighting growth 10%/5% lolos (batas inklusif)", b3 is None, str(b3))

# 10. Deploy cap vs MAX_OPEN: 1 posisi 0.024 sudah cap 30% -> posisi ke-2 max-size terblokir
check("deploy cap 30% x 0.08 = 0.024 (satu posisi max-size menghabiskan cap)",
      0.024+0.024 > m.MAX_DEPLOY_PCT*0.08, "MAX_OPEN=3 praktis tak tercapai untuk ukuran max")
check("daily budget: realized 0.00795 < 0.008 TIDAK blokir (selisih 0.00005)",
      not (0.007950477 <= -0.008 or 0.007950477 >= 0.008))

# 11. Korelasi: suffix & dev sama posisi terbuka
led3={"positions":[{"token":"xxxxpump","dev_owner":"DevX"}]}
check("korelasi suffix blokir", m.correlation_block(led3,"yyyyPump",{"creator":"Other"}) is not None)
check("korelasi dev blokir", m.correlation_block(led3,"yyyyabcd",{"creator":"DevX"}) is not None)
check("korelasi beda lolos", m.correlation_block(led3,"yyyyabcd",{"creator":"DevY"}) is None)

# 12. Ledger posisi saat ini vs snapshot tugas (20:26)
pos=led["positions"][0]
print("POSISI_SEKARANG:", json.dumps({k:pos[k] for k in ["token","entry_sol","tokens_base","entry_price_usd","entry_time"]}))
print("KAS_SEKARANG:", led["cash_sol"])
check("SNAPSHOT-TUGAS: entry_time 20:26 TIDAK cocok (sekarang 21:27 re-entry)",
      pos["entry_time"].startswith("2026-11-14T21:27"), pos["entry_time"])
check("SNAPSHOT-TUGAS: tokens 30375502403 TIDAK cocok (sekarang 21974938479)",
      pos["tokens_base"]!=30375502403, str(pos["tokens_base"]))
check("SNAPSHOT-TUGAS: kas 0.05599 TIDAK cocok (sekarang 0.063940477)",
      abs(led["cash_sol"]-0.05599)>1e-9, str(led["cash_sol"]))
# Tapi snapshot tugas COCOK dengan entry pertama: kas 0.08-0.02401=0.05599 persis
check("snapshot tugas = entry PERTAMA 20:26 (kas 0.08-0.02401=0.05599)",
      abs(0.08-0.024-0.00001-0.05599)<1e-12)

print(f"\nTOTAL: {PASS} PASS, {FAIL} FAIL")
