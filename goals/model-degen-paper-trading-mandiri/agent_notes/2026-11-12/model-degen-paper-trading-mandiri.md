# Study Notes - 2026-11-12 - BACOT DEGEN
<!-- studying-run-start: 2026-11-12T12:37:05Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 to 2026-11-19. Variant A — same gates with a clean-universe pre-filter (GeckoTerminal dex == pancakeswap_v2, quote token WBNB, reserve >= $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:42 WIB.

## Study focus today

Learning state: review_due, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study is the day-8 check (2026-11-12, evidence window 2026-11-11T12:02:53Z to 2026-11-12T12:37:05Z, run start 19:37 WIB): a second consecutive zero-entry day in both arms — and, more importantly, a reversal of the deadline improvement the 2026-11-11 note reported. It does not confuse any of this with live BACOT SCALPING (real money; 0 wins / 4 losses, cumulative −0.00286388 WBNB, round 5 unfunded) or with MODAL BACOT live trading — separate ledgers, separate money. All figures below are PAPER/VIRTUAL unless stated otherwise.

## What today's evidence shows

### 1. Day 8 was a second zero day — ledgers read directly, not inferred from chat

Both ledgers were read in full this run (`workspace/paper-trading/ledger.json` and `workspace/paper-trading/variant-a/ledger.json`):

- Main model: cash 0.011071790886431537 BNB virtual, 0 open positions, daily 2026-11-12 realized 0, entries 0, exits 0. Cash identical to 2026-11-11.
- Variant A: cash 0.010724160078509572 BNB virtual, 0 open positions, daily 2026-11-12 realized 0, entries 0, exits 0. Cash identical to 2026-11-11.
- Both arms are still above the 0.010 BNB virtual starting capital (main +10.7%, Variant A +7.2%), entirely on the strength of one token on one day — GANG on 2026-11-10. The trial has now run 8 days with exactly one token ever entered, in both arms. Day count so far: 6 zero days (2026-11-05 to 2026-11-08, 2026-11-11, 2026-11-12), 1 entry day (2026-11-09), 1 winning day (2026-11-10, GANG only).

### 2. The deadline improvement reversed — the headline new finding

The 2026-11-11 note reported the GoPlus holder fix had cut the deadline-hit rate to 38% (main) and 23% (Variant A), and asked whether that was the new normal. This run read all 2026-11-12 rows in both diagnostics files (`workspace/paper-trading/run-diagnostics.jsonl`, 75 main runs; `workspace/paper-trading/variant-a/run-diagnostics.jsonl`, 71 Variant A runs, both through ~19:28–19:33 WIB):

- Main model: deadline hit in 46 of 75 runs (61.3%), elapsed mean 727.7 s (min 522.5, max 876.3), pairs seen mean 60.0 of a 79.5 universe. That is worse than 2026-11-11 (38%, 669.2 s, 68.3 of 79.2) — the improvement more than half-unwound in one day, though still better than the pre-fix 88.7% / 38.3 pairs.
- Variant A: deadline hit in 21 of 71 runs (29.6%), elapsed mean 608.2 s (min 300.4, max 865.6), pairs seen mean 14.6 of a 16.4 universe. Also worse than 2026-11-11 (23%, 568.1 s, 18.2 of 19.5), still better than the pre-fix 75.9% / 11.3 pairs.
- Worst coverage observed: a main run at 19:14:44 WIB saw only 10 of 80 pairs before the deadline (elapsed ~829 s in the neighbouring run); a Variant A run at 19:33:12 WIB saw only 4 of 22 pairs. On runs like these, "nothing qualified" is a verdict on a small fraction of the market, not on the market.
- Likely cause, not proven: 2026-11-12 was a bad-network day across the whole system — the same day's main-chat record shows the live-trading feed timing out repeatedly from 17:54 WIB, the backtest recorder losing all 4 Binance sources for 4+ ticks, and the pending-swap check failing outright at 18:51 WIB because even example.com was unreachable. Slow egress, not a change in the model code, is the simplest explanation for a one-day deadline regression in both arms at once. The next study should check whether the rate falls back toward 38% / 23% on a normal-network day before treating 61% / 30% as a new floor.

### 3. The bottleneck is still pair_info, and it got heavier

Stage seconds in the diagnostics are cumulative sums across the pairs a run processed, not wall-clock stage times, so they are compared relatively, not against elapsed time:

- Main model, 2026-11-12 means: pair_info 1,229.6 s cumulative (up from 1,091.9 s on 2026-11-11), holder 200.5 s (flat vs 203.6 s), quote 174.8 s, audit 70.2 s, chart 67.0 s.
- Variant A, 2026-11-12 means: pair_info 476.1 s (up from 443.8 s), holder 203.9 s (vs 189.5 s), quote 190.9 s, audit 70.7 s, chart 64.4 s.
- The 2026-11-11 diagnosis stands and sharpens: the next latency fix, if any, belongs in pair_info, not in another holder-source change. No fix was attempted in this study.

### 4. The gates still never fire — the model starves at the sighting, not at v2

Across all 2026-11-12 runs, v2_holders / v2_dev / v2_lp killed 0 pairs in both arms — the third consecutive day measured with zero v2 kills:

- Main: sighting kills 334, holder_gate kills 334, over 2,220 total sightings recorded, 0 entries. (Non-v2 reverts 1,963 and dust 535 dominate the earlier rejections.)
- Variant A: sighting kills 292, holder_gate kills 331, over 1,556 total sightings, 0 entries.
- The binding constraint remains the 2-sighting growth confirmation (holder +10% and reserve +5% between sightings) plus the holder gate. The machine now sees most of the market on good runs and still admits nothing. The two readings the trial cannot yet separate — genuinely nothing met the bar, or the sighting rule is calibrated too tightly — remain unseparated, because the control arm still does not exist (see Prerequisite check).

### 5. What did not move: control arm, forward-return ledger, trial clock

- Forward-return ledger (`workspace/paper-trading/forward-return-ledger.md`): still an empty table — no rows at all. GANG's first entries were never recorded there, so the screen's hit rate remains unmeasured even after its first entries and TP exits. This was already an open item in the 2026-11-10 and 2026-11-11 notes; it is still open.
- Control arm (coin-flip control + hold benchmark): still not built. The 2026-11-10 wins therefore still cannot be distinguished from luck by the trial's own standard, and now two consecutive zero days cannot be distinguished from a too-tight sighting rule either.
- Trial clock: 7 days remain (ends 2026-11-19). Eight days in, the record is 6 zero days, 1 entry day, 1 winning day, one token ever traded. A single-token trial cannot prove a model, and the trial is now past its midpoint with the deadline rate moving the wrong way.

## Prerequisite check

- Prerequisites in place: v2 engine on the 15-minute cron (paper-trading-15m), Variant A on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, GoPlus holder source live in both arms, kill switch equity-based since 2026-11-09 ~20:20 WIB, trial window to 2026-11-19 (7 days remain from 2026-11-12).
- Gap to close first (unchanged, now sharper): no control arm and no benchmark. A winning day — even a +30% TP in both arms — cannot be distinguished from luck, and now two zero days cannot be distinguished from a too-tight sighting rule either. Both directions need the control.
- Second gap (changed): the deadline rate regressed in one day (main 38% → 61.3%, Variant A 23% → 29.6%) on a day the whole system suffered slow egress. Before trusting either the 2026-11-11 improvement or the 2026-11-12 regression, the next study should re-check the rate on a normal-network day; the bottleneck remains pair_info either way.
- Third gap (unchanged): the forward-return ledger is still empty; GANG was never recorded there. Check it next time rather than assuming.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if equity falls below 70% (equity-measured since 2026-11-09 ~20:20 WIB) — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards. Since 2026-11-09 ~19:50 WIB, the holder snapshot comes from GoPlus (not eth_getLogs), and bundle/dev-cluster checks are recorded unverified rather than assumed clean. Since 2026-11-11, the known bottleneck is the pair_info stage, not the holder stage — and the v2 gates have still killed 0 pairs on any day measured, because pairs are stopped earlier at the sighting and holder gates. Since 2026-11-12, the deadline rate is known to be unstable day to day (main 38% → 61.3% in one day), plausibly with VM egress slowness rather than the model itself.

## Worked example

Walk-through of one real 2026-11-12 run: the main-model run ending 19:28:53 WIB, the last main run inside this window.

1. Run: elapsed 829.4 s, deadline_hit true (750 s limit exceeded), universe 80 pairs, pairs seen 15.
2. Rejection counts: non_v2_id 1, non_v2_revert 8, dust 0, audit_skip 1, holder_skip 3, holder_gate 3, chart_skip 1, sighting 1, v2_holders / v2_dev / v2_lp 0.
3. Stage cost (cumulative across pairs): pair_info 651.7 s, quote 193.0 s, audit 82.5 s, holder 226.1 s, chart 69.6 s.
4. Outcome: entries_made 0, sightings 28, open_positions 0. The ledger did not change.
5. What this shows: on a bad-network day the machine worked a full run, saw under a fifth of the universe, rejected everything before the v2 gates, and ended exactly where it started. What it does not show: whether any of the 65 unseen pairs would have qualified. That is the cost of a 61% deadline rate — on a run like this one, the verdict "nothing qualified" is only a verdict on the small part of the market the machine reached.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/ledger.json and state, in one sentence, the cash, the number of positions, and the 2026-11-12 daily realized PnL (expected: cash 0.01107179 BNB virtual, 0 positions, realized 0).
2. Open workspace/paper-trading/variant-a/ledger.json and do the same for Variant A (expected: cash 0.01072416 BNB virtual, 0 positions, realized 0); confirm both arms agree the day was a zero day, and that cash is unchanged from 2026-11-11.
3. From the two run-diagnostics.jsonl files, compute the 2026-11-12 deadline-hit rate for each arm (expected: main 46/75 ≈ 61%, Variant A 21/71 ≈ 30%) and compare with 2026-11-11 (38% / 23%) and pre-fix (88.7% / 75.9%).
4. Compare the mean cumulative stage seconds for pair_info vs holder in each arm (expected: main 1,229.6 vs 200.5; Variant A 476.1 vs 203.9) and name the current bottleneck.
5. Feedback check: if both arms show zero entries on a day when the main model saw only 60 of ~80 pairs per run on average — and 10 of 80 on the worst run — the correct conclusion is "the machine saw part of the market and admitted nothing, but on the worst runs it saw too little to say anything about the market" — not "the model is broken" and not "there was nothing in the market," because the control arm that would separate those two readings still does not exist.

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading both ledgers directly instead of trusting a chat summary, computing the deadline rate from the full day's diagnostics instead of quoting one slow run, comparing stage costs relatively instead of against elapsed time, checking the network context before blaming the model for a one-day regression), name the one most useful next adjustment (e.g. always pair a zero-entry day with the coverage figure — a zero on a day the machine saw 10 of 80 pairs means something different from a zero on a day it saw 68 of 79 — and never present a virtual balance as real profit), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to resume BACOT SCALPING (real money) once funds return, and whether the paper model's gates should inform that decision. Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. Today's transfer warning is specific: two zero-entry days after a +30% day are exactly the kind of whiplash that tempts either "the model is dead" or "the model is proven" — both are premature with 7 days left, one token ever traded, and no control arm. The deadline regression adds a second warning: do not rebuild the model around a one-day latency number that moves with the network.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, forgetting the kill-switch is now equity-measured, forgetting that holder data now comes from GoPlus with bundle/dev-cluster unverified, forgetting that the current bottleneck is pair_info rather than holder, or forgetting that the deadline rate regressed on 2026-11-12) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will the model find a second, different token before 2026-11-19, or will the whole trial's wins be GANG alone? A single-token trial cannot prove a model, and the trial is past its midpoint.
- Is the 61% / 30% deadline rate a one-day network artefact or a new floor? Re-check on a normal-network day; the next latency work should still target pair_info, not the holder stage.
- When will the coin-flip control + hold benchmark be built? Without it, neither the 2026-11-10 wins nor the two consecutive zero days can meet the trial's own "proven" gate.
- Was GANG ever recorded in the forward-return ledger? Still no — the ledger table is empty. If it stays empty, the screen's hit rate stays unmeasured even after its first entries.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL (0 wins / 4 losses, −0.00286388 WBNB) or with MODAL BACOT live trading (live-trading-feed stalled repeatedly on 2026-11-12, last state write 17:54 WIB, runs 17:50 and 18:05 timing out). Keep the three ledgers separate in every future note and letter.
- The user asked on 2026-11-09 whether 5–10% per day from trading is possible; the honest answer given then was no, not proven. One virtual +30% day followed by two zero days does not change that answer — it is three data points inside a trial that ends 2026-11-19.

## Next review

2026-11-13T12:37:05Z. Next study should re-check the deadline-hit rate on a normal-network day, confirm whether the forward-return ledger and control arm moved at all, and count the zero days since the last entry.

## Already Covered in Main Chat

- The 2026-11-12 18:19 WIB 2-hour recap restated paper cash 0.011072 BNB virtual (main) and 0.010724 BNB virtual (Variant A), 0 open positions, and 0 entry / 0 exit on 2026-11-12 — so today's zero-entry day and unchanged cash were already reported to the user.
- The same recap reported the live-trading feed stalling (last state 17:54 WIB, run 17:50 timeout) and the narrative pulse having no new signal — the network-degradation context for today's deadline regression.
- Later main-chat messages on 2026-11-12 reported the backtest recorder losing all 4 Binance sources for 4+ ticks and the 18:51 WIB pending-swap check failing outright because RPC calls could not reach the network — further evidence the day's slowness was system-wide, not model-specific.
- The 2026-11-11 Day Seven brief (delivered 2026-11-12 05:28 WIB) already covered the day-7 zero day, the GoPlus holder fix, the 38% / 23% deadline rates, and the pair_info bottleneck — the themes today's note extends.
- Not reported in main chat: the full-day 2026-11-12 deadline-hit rates (61.3% main / 29.6% Variant A), the pairs-seen means (60.0 / 79.5 main, 14.6 / 16.4 Variant A), the worst-coverage runs (10 of 80; 4 of 22), or the pair_info stage means (1,229.6 s main / 476.1 s Variant A).

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers, diagnostics, and forward-return ledger are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-11/model-degen-paper-trading-mandiri.md (read in full): day-7 check, zero-entry day 2026-11-11 in both arms, deadline rates 38% main / 23% Variant A, pair_info bottleneck finding (1,091.9 s main / 443.8 s Variant A cumulative), v2 kills 0, forward-return ledger still empty, control arm still missing.
- Prior study notes 2026-11-05 through 2026-11-10 (known from the 2026-11-11 note's trajectory): 0 trades until 2026-11-09, first GANG entries 2026-11-09, TP exits +30% both arms 2026-11-10, GoPlus holder fix and equity kill-switch fix applied.
- Prior briefs (filenames listed): BACOT DEGEN Day Five (2026-11-09 12.24.28).html, BACOT DEGEN Head-to-Head (2026-11-08 12.17.08).html, Variant A Day One (2026-11-07 12.28.06).html, BACOT DEGEN Day Seven (2026-11-11 12.15.09).html — the Day Seven brief's text was checked and covers the day-7 zero day, the deadline improvement, and the pair_info bottleneck.
- Repetition search (grep over this goal's agent_notes/*.md, variants "zero-entry", "deadline", "pair_info bottleneck", "GANG take-profit", "day eight"): the 2026-11-11 note matches on "GANG", "deadline", "pair_info", and "zero day" (the TP exits, the fixes, the deadline question, and the day-7 zero are all there); no prior note or brief contains the 2026-11-12 deadline rates (61.3% / 29.6%), the pairs-seen means, or the worst-coverage runs. Today's quantitative findings are new against the notes and briefs, but the Letter's centre — another zero-entry day with unchanged cash — was already reported in the 2026-11-12 18:19 WIB main-chat recap, which is what decides the ruling below.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active; current state "Posisi GANG ditutup take-profit +30% virtual; kas virtual 0,01107 BNB dan tidak ada posisi terbuka." — still accurate after the second zero day, since the ledgers did not move.
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-13T12:37:05Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Ledgers read directly in this turn: workspace/paper-trading/ledger.json (cash 0.011071790886431537 BNB virtual, positions [], daily 2026-11-12 realized 0 / entries 0 / exits 0) and workspace/paper-trading/variant-a/ledger.json (cash 0.010724160078509572 BNB virtual, positions [], daily 2026-11-12 realized 0 / entries 0 / exits 0).
- Diagnostics read directly in this turn: workspace/paper-trading/run-diagnostics.jsonl (75 runs on 2026-11-12, 46 deadline hits, elapsed mean 727.7 s, pairs seen mean 60.0/79.5, entries 0, v2 kills 0, sighting kills 334, holder_gate 334, pair_info stage mean 1,229.6 s cumulative, holder 200.5 s) and workspace/paper-trading/variant-a/run-diagnostics.jsonl (71 runs, 21 deadline hits, elapsed mean 608.2 s, pairs seen mean 14.6/16.4, entries 0, v2 kills 0, sighting kills 292, holder_gate 331, pair_info 476.1 s, holder 203.9 s).
- Forward-return ledger read in this turn: workspace/paper-trading/forward-return-ledger.md — table still empty, no rows.
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window 2026-11-11T12:02:53Z → 2026-11-12T12:42:22Z) plus the run's chunk handoff: the 2026-11-12 18:19 WIB recap already reported today's zero entries and unchanged cash; the network-degradation reports (feed stalls, Binance sources failing, pending-swap check failing) came from the same window.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet; daily profit benchmark 10% net with symmetric 10% loss limit; never force a trade to chase the daily target; trial ends 2026-11-19.

### Searches skipped or unavailable

- No new web search was run: the trial's own record is primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief HTML files were listed and the Day Seven brief's text checked via grep; the three earlier briefs predate the first entries, the TP exits, and the zero days, so re-reading their rendered HTML in full would not change the newness ruling.
