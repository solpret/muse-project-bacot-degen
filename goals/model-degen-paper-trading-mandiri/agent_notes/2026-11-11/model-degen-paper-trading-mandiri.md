# Study Notes - 2026-11-11 - BACOT DEGEN
<!-- studying-run-start: 2026-11-11T12:02:56Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 to 2026-11-19. Variant A — same gates with a clean-universe pre-filter (GeckoTerminal dex == pancakeswap_v2, quote token WBNB, reserve >= $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:42 WIB.

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study is the day-7 check (2026-11-11, evidence window 2026-11-10T12:02:54Z to 2026-11-11T12:02:53Z, run start 19:02 WIB): a full day with zero entries in both arms — and the answer to the question the 2026-11-10 note left open, whether the GoPlus holder fix actually solved the deadline problem. It does not confuse any of this with live BACOT SCALPING (real money; 0 wins / 4 losses, cumulative −0.00286388 WBNB, round 5 unfunded) or with MODAL BACOT live trading — separate ledgers, separate money. All figures below are PAPER/VIRTUAL unless stated otherwise.

## What today's evidence shows

### 1. Day 7 was a zero day — ledgers read directly, not inferred from chat

Both ledgers were read in full this run (`workspace/paper-trading/ledger.json` and `workspace/paper-trading/variant-a/ledger.json`):

- Main model: cash 0.011071790886431537 BNB virtual, 0 open positions, daily 2026-11-11 realized 0, entries 0, exits 0. Last trades remain the 2026-11-10 ones: trailing exit −0.0000301 BNB virtual at 01:58:40 WIB and TP +30% +0.0011019 BNB virtual at 15:59:25 WIB, both GANG (0x0c6302401aa5325c2e36f170f52c00b1d220b405).
- Variant A: cash 0.010724160078509572 BNB virtual, 0 open positions, daily 2026-11-11 realized 0, entries 0, exits 0. Last trades remain the three 2026-11-10 GANG exits (trailing +0.0001177, stop −0.0004717, TP +0.001078 BNB virtual).
- Cash is therefore unchanged since the 2026-11-10 TP exits in both arms. Both arms are still above the 0.010 BNB virtual starting capital (main +10.7%, Variant A +7.2%), entirely on the strength of one token on one day — GANG on 2026-11-10. The trial has now run 7 days with exactly one token ever entered, in both arms.

### 2. The deadline question, answered with a full day of diagnostics

The 2026-11-10 note warned not to quote the 275 s / 278 s post-fix runs as the new normal and asked the next study to re-check deadline-hit rates. This run read all 2026-11-11 rows in both diagnostics files (`workspace/paper-trading/run-diagnostics.jsonl`, 73 main runs 00:24–18:53 WIB; `workspace/paper-trading/variant-a/run-diagnostics.jsonl`, 70 Variant A runs 00:15–18:47 WIB):

- Main model: deadline hit in 28 of 73 runs (38%), elapsed mean 669.2 s (min 449.0, max 850.6), pairs seen mean 68.3 of a 79.2 universe. Pre-fix (2026-11-09, from the 2026-11-09 note) the deadline rate was 88.7% with 38.3 pairs seen per run. So the deadline rate more than halved and coverage nearly doubled — the GoPlus fix did real work — but 38% of runs still time out and a third of the universe still goes unseen on the average run.
- Variant A: deadline hit in 16 of 70 runs (23%), elapsed mean 568.1 s (min 289.5, max 890.0), pairs seen mean 18.2 of a 19.5 universe. Pre-fix the deadline rate was 75.9% with 11.3 pairs seen. Variant A is now close to full coverage on most runs.
- Worst coverage observed: a main run at 18:38:49 WIB saw only 12 of 80 pairs before the deadline (elapsed 776.9 s). Slow days are not gone; they are less frequent.

### 3. The bottleneck moved — pair_info, not holder

Stage seconds in the diagnostics are cumulative sums across the pairs a run processed, not wall-clock stage times, so they are compared relatively, not against elapsed time:

- Main model, 2026-11-11 means: pair_info 1,091.9 s cumulative, holder 203.6 s cumulative. The holder stage — the 650–995 s wall-clock monster of 2026-11-09 — is no longer the dominant cost. The per-pair identification step (pair_info) now consumes the most work.
- Variant A, 2026-11-11 means: pair_info 443.8 s cumulative, holder 189.5 s cumulative. Same pattern, smaller universe.
- Implication: the next latency fix, if any, belongs in pair_info (what it fetches per pair and whether it can be batched or cached), not in another holder-source change. This is a new diagnosis, not a repeat of the 2026-11-09 one. No fix was attempted in this study; the finding is preserved for whoever owns the next change.

### 4. The gates still never fire — the model starves at the sighting, not at v2

Across all 2026-11-11 runs, v2_holders / v2_dev / v2_lp killed 0 pairs in both arms — exactly as on 2026-11-09. Almost no pair reaches the v2 gates, so the v2 thresholds remain untested by live data:

- Main: sighting kills 335, holder_gate kills 461, over 1,481 total sightings recorded, 0 entries.
- Variant A: sighting kills 293, holder_gate kills 448, over 1,626 total sightings, 0 entries.
- The binding constraint is the 2-sighting growth confirmation (holder +10% and reserve +5% between sightings) plus the holder gate — the same shape as before the fix. The machine now sees far more of the market and still admits nothing. That is consistent with two readings that the trial cannot yet separate: the market genuinely offered nothing that met the bar on 2026-11-11, or the sighting rule is calibrated so tightly that a second token will rarely qualify. The control arm would help separate them; it still does not exist (see Prerequisite check).

### 5. What did not move: control arm, forward-return ledger, trial clock

- Forward-return ledger (`workspace/paper-trading/forward-return-ledger.md`): still an empty table — no rows at all. GANG's first entries were never recorded there, so the screen's hit rate remains unmeasured even after its first entries and TP exits. This was already an open item in the 2026-11-10 note; it is still open.
- Control arm (coin-flip control + hold benchmark): still not built. The 2026-11-10 wins therefore still cannot be distinguished from luck by the trial's own standard.
- Trial clock: 8 days remain (ends 2026-11-19). Seven days in, the record is: 4 zero days, 1 entry day (2026-11-09), 1 winning day (2026-11-10, GANG only), 1 zero day (2026-11-11). A single-token trial cannot prove a model, and the trial is now past its midpoint with only one token ever traded.

## Prerequisite check

- Prerequisites in place: v2 engine on the 15-minute cron (paper-trading-15m), Variant A on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, GoPlus holder source live in both arms, kill switch equity-based since 2026-11-09 ~20:20 WIB, trial window to 2026-11-19 (8 days remain from 2026-11-11).
- Gap to close first (unchanged, now sharper): no control arm and no benchmark. A winning day — even a +30% TP in both arms — cannot be distinguished from luck, and now a zero day cannot be distinguished from a too-tight sighting rule either. Both directions need the control.
- Second gap (changed): the holder-stage latency is fixed as a source problem and substantially improved as a reliability problem (deadline rate 88.7% → 38% main, 75.9% → 23% Variant A; coverage 38.3 → 68.3 pairs main, 11.3 → 18.2 Variant A) — but the bottleneck has moved to pair_info, and 38% / 23% of runs still hit the deadline. Before trusting coverage, the next latency work should target pair_info, not the holder stage.
- Third gap (unchanged): the forward-return ledger is still empty; GANG was never recorded there. Check it next time rather than assuming.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if equity falls below 70% (equity-measured since 2026-11-09 ~20:20 WIB) — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards. Since 2026-11-09 ~19:50 WIB, the holder snapshot comes from GoPlus (not eth_getLogs), and bundle/dev-cluster checks are recorded unverified rather than assumed clean. Since 2026-11-11, the known bottleneck is the pair_info stage, not the holder stage — and the v2 gates have still killed 0 pairs on any day measured, because pairs are stopped earlier at the sighting and holder gates.

## Worked example

Walk-through of one real 2026-11-11 run: the main-model run ending 18:53:45 WIB, the last main run inside this window.

1. Run: elapsed 773.7 s, deadline_hit true (750 s limit exceeded), universe 80 pairs, pairs seen 41.
2. Rejection counts: non_v2_id 2, non_v2_revert 15, non_wbnb 1, dust 11, audit_skip 2, holder_skip 3, holder_gate 3, chart_skip 4, sighting 3, v2_holders / v2_dev / v2_lp 0.
3. Stage cost (cumulative across pairs): pair_info 1,198.2 s, quote 303.5 s, audit 64.3 s, holder 146.2 s, chart 73.7 s. Pair_info alone exceeds the run's whole elapsed time in cumulative terms — it is where the work goes.
4. Outcome: entries_made 0, sightings 24, open_positions 0. The ledger did not change.
5. What this shows: the machine worked a full run, saw half the universe, rejected everything before the v2 gates, and ended exactly where it started. What it does not show: whether any of the 39 unseen pairs would have qualified. That is the cost of the remaining 38% deadline rate — on a run like this one, the verdict "nothing qualified" is only a verdict on the half of the market the machine reached.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/ledger.json and state, in one sentence, the cash, the number of positions, and the 2026-11-11 daily realized PnL (expected: cash 0.01107179 BNB virtual, 0 positions, realized 0).
2. Open workspace/paper-trading/variant-a/ledger.json and do the same for Variant A (expected: cash 0.01072416 BNB virtual, 0 positions, realized 0); confirm both arms agree the day was a zero day.
3. From the two run-diagnostics.jsonl files, compute the 2026-11-11 deadline-hit rate for each arm (expected: main 28/73 ≈ 38%, Variant A 16/70 ≈ 23%) and compare with the pre-fix rates (88.7% / 75.9% from the 2026-11-09 note).
4. Compare the mean cumulative stage seconds for pair_info vs holder in each arm (expected: main 1,091.9 vs 203.6; Variant A 443.8 vs 189.5) and name the current bottleneck.
5. Feedback check: if both arms show zero entries on a day when the machine saw ~68 of ~79 pairs per run on average, the correct conclusion is "the machine saw most of the market and admitted nothing — the binding constraint is the sighting/holder stage, and the v2 gates remain untested" — not "the model is broken" and not "there was nothing in the market," because the control arm that would separate those two readings still does not exist.

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading both ledgers directly instead of trusting a chat summary, computing the deadline rate from the full day's diagnostics instead of quoting one slow run, comparing stage costs relatively instead of against elapsed time), name the one most useful next adjustment (e.g. always pair a zero-entry day with the coverage figure — a zero on a day the machine saw 12 of 80 pairs means something different from a zero on a day it saw 68 of 79 — and never present a virtual balance as real profit), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to resume BACOT SCALPING (real money) once funds return, and whether the paper model's gates should inform that decision. Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. Today's transfer warning is specific: a zero-entry day after a +30% day is exactly the kind of whiplash that tempts either "the model is dead" or "the model is proven" — both are premature with 8 days left, one token ever traded, and no control arm.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, forgetting the kill-switch is now equity-measured, forgetting that holder data now comes from GoPlus with bundle/dev-cluster unverified, or forgetting that the current bottleneck is pair_info rather than holder) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will the model find a second, different token before 2026-11-19, or will the whole trial's wins be GANG alone? A single-token trial cannot prove a model, and the trial is past its midpoint.
- Is the 38% / 23% deadline rate the new floor, or does a pair_info fix push it lower? The next latency work should target pair_info, not the holder stage.
- When will the coin-flip control + hold benchmark be built? Without it, neither the 2026-11-10 wins nor the 2026-11-11 zero can meet the trial's own "proven" gate.
- Was GANG ever recorded in the forward-return ledger? Still no — the ledger table is empty. If it stays empty, the screen's hit rate stays unmeasured even after its first entries.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL (0 wins / 4 losses, −0.00286388 WBNB) or with MODAL BACOT live trading (live-trading-feed stalled repeatedly on 2026-11-10/11, 4 consecutive failures by the 2026-11-11 12:00 UTC scheduler check). Keep the three ledgers separate in every future note and letter.
- The user asked on 2026-11-09 whether 5–10% per day from trading is possible; the honest answer given then was no, not proven. One virtual +30% day followed by a zero day does not change that answer — it is two data points inside a trial that ends 2026-11-19.

## Already Covered in Main Chat

- Main agent reported the Variant A run at 2026-11-10 20:16 WIB as having no entry/exit but hitting the time limit again (768 s, 14 of 18 pools processed).
- The 2026-11-10 20:19 WIB 2-hour recap restated paper cash 0.011072 BNB virtual, 0 open positions, realized today +0.001072 BNB virtual, and the kill switch not active.
- The 2026-11-10 21:37 WIB daily opportunity evaluation restated paper results (main +0.0010718 BNB, Variant A +0.0007242 BNB, GANG exits, 0 open positions).
- The 2026-11-10 TP exits themselves (+30% in both arms, cash 0.0110718 / 0.010724 BNB virtual) were reported in main chat on 2026-11-10 and are already recorded in the 2026-11-10 study note.
- Not reported in main chat: the 2026-11-11 zero-entry day in either arm, the full-day deadline-hit rates (38% main / 23% Variant A), the pair_info bottleneck finding, or the empty forward-return ledger.

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers, diagnostics, and forward-return ledger are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-10/model-degen-paper-trading-mandiri.md (read in full): day-6 check, first GANG entries 19:54/19:56 WIB 2026-11-09, TP exits 15:59/16:04 WIB 2026-11-10 (+30% both arms), GoPlus holder fix and equity kill-switch fix applied, and the open instruction not to quote the 275 s / 278 s runs as the new normal but to re-check deadline-hit rates — which this note does, for 2026-11-11.
- Prior study notes 2026-11-05 through 2026-11-09 (known from the 2026-11-10 note's trajectory): 0 trades until 2026-11-09, control arm and forward-return ledger still missing, holder gate ~96% of Variant A survivors.
- Prior briefs: BACOT DEGEN Day Five (2026-11-09 12.24.28).html, BACOT DEGEN Head-to-Head (2026-11-08 12.17.08).html, Variant A Day One (2026-11-07 12.28.06).html (listed via user_goal.get and the briefs directory; all three predate the first entries, the TP exits, and the 2026-11-11 zero day).
- Repetition search (grep over agent_notes/ and briefs/ for this goal, variants "GANG take-profit", "deadline-hit rate", "pair_info bottleneck", "zero-entry day", plus "GoPlus", "kill switch", "equity", "Variant A"): the 2026-11-05 to 2026-11-10 notes matched on "GANG", "GoPlus", "kill switch", and "deadline" (the TP exits, the fixes, and the open deadline question are all in the 2026-11-10 note); no prior note or brief contains the 2026-11-11 zero-entry day, the full-day deadline-hit rates (38% / 23%), or the pair_info bottleneck finding. Today's findings are new against the notes and briefs, and the aggregate findings were not reported in main chat (see Already Covered in Main Chat) — which is what decides the ruling below.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active; current state "Posisi GANG ditutup take-profit +30% virtual; kas virtual 0,01107 BNB dan tidak ada posisi terbuka." — still accurate after the zero day, since the ledgers did not move.
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-12T12:02:56Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Ledgers read directly in this turn: workspace/paper-trading/ledger.json (cash 0.011071790886431537 BNB virtual, positions [], daily 2026-11-11 realized 0 / entries 0 / exits 0) and workspace/paper-trading/variant-a/ledger.json (cash 0.010724160078509572 BNB virtual, positions [], daily 2026-11-11 realized 0 / entries 0 / exits 0).
- Diagnostics read directly in this turn: workspace/paper-trading/run-diagnostics.jsonl (73 runs on 2026-11-11, 28 deadline hits, elapsed mean 669.2 s, pairs seen mean 68.3/79.2, entries 0, v2 kills 0, sighting kills 335, holder_gate 461, pair_info stage mean 1,091.9 s cumulative, holder 203.6 s) and workspace/paper-trading/variant-a/run-diagnostics.jsonl (70 runs, 16 deadline hits, elapsed mean 568.1 s, pairs seen mean 18.2/19.5, entries 0, v2 kills 0, sighting kills 293, holder_gate 448, pair_info 443.8 s, holder 189.5 s).
- Forward-return ledger read in this turn: workspace/paper-trading/forward-return-ledger.md — table still empty, no rows.
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window 2026-11-10T12:02:54Z → 2026-11-11T12:05:50Z) plus the run's chunk handoff: the 2026-11-10 TP exits, the 20:16 WIB slow Variant A run, the 20:19 WIB recap, and the 21:37 WIB daily evaluation were all reported to the user; the 2026-11-11 aggregate findings in this note were not.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet; daily profit benchmark 10% net with symmetric 10% loss limit; never force a trade to chase the daily target; trial ends 2026-11-19.

### Searches skipped or unavailable

- No new web search was run: the trial's own record is primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief HTML files were listed and their subjects taken from the goal record and prior notes, not re-read in full: all three predate the first entries, the TP exits, and the 2026-11-11 zero day, so re-reading the rendered HTML would not change the newness ruling.
