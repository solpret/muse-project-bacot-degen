# Study Notes - 2026-11-13 - BACOT DEGEN
<!-- studying-run-start: 2026-11-13T12:33:17Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 to 2026-11-19. Variant A — same gates with a clean-universe pre-filter (GeckoTerminal dex == pancakeswap_v2, quote WBNB, reserve >= $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:42 WIB.

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study is the day-9 check (2026-11-13, evidence window 2026-11-12T12:24:29Z to 2026-11-13T12:33:17Z, run start 19:33 WIB): a third consecutive zero-entry day in both arms — and, more importantly, the deadline rates moved in opposite directions in the two arms, which answers the question the 2026-11-12 note left open. It does not confuse any of this with live BACOT SCALPING (real money; 0 wins / 4 losses, cumulative −0.00286388 WBNB) or with MODAL BACOT live trading — separate ledgers, separate money. All figures below are PAPER/VIRTUAL unless stated otherwise.

## What today's evidence shows

### 1. Day 9 was a third zero day — ledgers read directly, not inferred from chat

Both ledgers were read in full this run (`workspace/paper-trading/ledger.json` and `workspace/paper-trading/variant-a/ledger.json`):

- Main model: cash 0.011071790886431537 BNB virtual, 0 open positions, daily 2026-11-13 realized 0, entries 0, exits 0. Cash identical to 2026-11-11 and 2026-11-12.
- Variant A: cash 0.010724160078509572 BNB virtual, 0 open positions, daily 2026-11-13 realized 0, entries 0, exits 0. Cash identical to 2026-11-11 and 2026-11-12.
- Both arms are still above the 0.010 BNB virtual starting capital (main +10.7%, Variant A +7.2%), entirely on the strength of one token on one day — GANG on 2026-11-10. The trial has now run 9 days with exactly one token ever entered, in both arms. Day count so far: 7 zero days (2026-11-05 to 2026-11-08, 2026-11-11, 2026-11-12, 2026-11-13), 1 entry day (2026-11-09), 1 winning day (2026-11-10, GANG only).

### 2. The deadline rates split — the headline new finding

The 2026-11-12 note asked whether the one-day deadline regression (main 38% → 61.3%, Variant A 23% → 29.6%) was a network artefact or a new floor, and said to re-check on a normal-network day. This run read all 2026-11-13 rows in both diagnostics files (main 79 runs, 00:12–19:22 WIB; Variant A 76 runs, 00:02–19:28 WIB):

- Main model: deadline hit in 42 of 79 runs (53.2%), elapsed mean 699.9 s, pairs seen mean 66.4 of a 79.7 universe. That is between the 2026-11-11 rate (38%) and the 2026-11-12 rate (61.3%) — the regression partly unwound, but did not return to 38%.
- Variant A: deadline hit in 11 of 76 runs (14.5%), elapsed mean 593.8 s, pairs seen mean 14.9 of a 15.5 universe. That is better than both 2026-11-11 (23%) and 2026-11-12 (29.6%) — the best Variant A rate measured since the GoPlus fix.
- Worst coverage observed: a main run at 17:56:11 WIB saw only 34 of 80 pairs before the deadline; Variant A's worst run saw 9 of a 9-pair universe — full coverage, the universe itself was just small that run.
- Reading: the deadline rate is unstable day to day in both arms, and the two arms moved in opposite directions on the same day, which weakens the "one bad-network day explains everything" story from 2026-11-12 — the network was bad enough to stall the live-trading feed repeatedly on 2026-11-13 too (episodes from 11:21, 12:25, 13:26, 15:39, and 17:25 WIB in main chat), yet Variant A improved to its best rate while the main model stayed above 50%. No single-day rate should be quoted as the model's floor. The practical consequence is unchanged: on a main-model run like the 17:56 WIB one, "nothing qualified" is a verdict on 34 of 80 pairs, not on the market.

### 3. The bottleneck is still pair_info, and the gates still never fire

Stage seconds in the diagnostics are cumulative sums across the pairs a run processed, not wall-clock stage times, so they are compared relatively, not against elapsed time:

- Main model, 2026-11-13 means: pair_info 1,149.5 s cumulative (down slightly from 1,229.6 s on 2026-11-12), holder 221.2 s (vs 200.5 s), quote 169.7 s, audit 71.6 s, chart 67.9 s.
- Variant A, 2026-11-13 means: pair_info 457.1 s (down from 476.1 s), holder 209.6 s (vs 203.9 s), quote 176.2 s, audit 72.8 s, chart 68.7 s.
- The 2026-11-11 diagnosis stands: the next latency fix, if any, belongs in pair_info, not in another holder-source change. No fix was attempted in this study.
- Across all 2026-11-13 runs, v2_holders / v2_dev / v2_lp killed 0 pairs in both arms — extending the zero-v2-kill streak the 2026-11-12 note counted at three consecutive days. Main: sighting kills 300, holder_gate kills 467, over 1,339 total sightings recorded, 0 entries. (Non-v2 reverts 2,194 and non-v2-id 979 dominate the earlier rejections.) Variant A: sighting kills 242, holder_gate kills 472, over 1,069 total sightings, 0 entries.
- The binding constraint remains the 2-sighting growth confirmation (holder +10% and reserve +5% between sightings) plus the holder gate. The machine now sees most of the market on good runs — Variant A saw 14.9 of 15.5 pairs on average — and still admits nothing. The two readings the trial cannot yet separate — genuinely nothing met the bar, or the sighting rule is calibrated too tightly — remain unseparated, because the control arm still does not exist (see Prerequisite check). Note the new asymmetry: Variant A's near-full coverage on 2026-11-13 makes "the machine saw the market and admitted nothing" a stronger statement for Variant A than for the main model, whose 53.2% deadline rate still leaves a third of its runs partially blind.

### 4. What did not move: control arm, forward-return ledger, trial clock

- Forward-return ledger (`workspace/paper-trading/forward-return-ledger.md`): still an empty table — header rows only, no data rows at all, and no mention of 2026-11-13. GANG's first entries were never recorded there, so the screen's hit rate remains unmeasured even after its first entries and TP exits. This was already an open item in the 2026-11-10, 2026-11-11, and 2026-11-12 notes; it is still open.
- Control arm (coin-flip control + hold benchmark): still not built — no control ledger or control script appears in the `workspace/paper-trading/` listing. The 2026-11-10 wins therefore still cannot be distinguished from luck by the trial's own standard, and now three consecutive zero days cannot be distinguished from a too-tight sighting rule either.
- Trial clock: 6 days remain (ends 2026-11-19). Nine days in, the record is 7 zero days, 1 entry day, 1 winning day, one token ever traded. A single-token trial cannot prove a model, and the trial is now two-thirds done.

## Prerequisite check

- Prerequisites in place: v2 engine on the 15-minute cron (paper-trading-15m), Variant A on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, GoPlus holder source live in both arms, kill switch equity-based since 2026-11-09 ~20:20 WIB, trial window to 2026-11-19 (6 days remain from 2026-11-13).
- Gap to close first (unchanged, now sharper): no control arm and no benchmark. A winning day — even a +30% TP in both arms — cannot be distinguished from luck, and now three zero days cannot be distinguished from a too-tight sighting rule either. Both directions need the control. Variant A's near-full coverage on 2026-11-13 sharpens the second half: if the sighting rule is the binding constraint, a control arm is the only way to show it.
- Second gap (changed): the deadline rate is now known to be unstable day to day in both directions — main 38% → 61.3% → 53.2%, Variant A 23% → 29.6% → 14.5% across 2026-11-11 to 2026-11-13. Do not quote any single day's rate as the model's floor, and do not rebuild around one day's number. The bottleneck remains pair_info either way.
- Third gap (unchanged): the forward-return ledger is still empty; GANG was never recorded there. Check it next time rather than assuming.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if equity falls below 70% (equity-measured since 2026-11-09 ~20:20 WIB) — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards. Since 2026-11-09 ~19:50 WIB, the holder snapshot comes from GoPlus (not eth_getLogs), and bundle/dev-cluster checks are recorded unverified rather than assumed clean. Since 2026-11-11, the known bottleneck is the pair_info stage, not the holder stage — and the v2 gates have still killed 0 pairs on any day measured, because pairs are stopped earlier at the sighting and holder gates. Since 2026-11-12, the deadline rate is known to be unstable day to day (main 38% → 61.3% in one day). Since 2026-11-13, the two arms moved in opposite directions (main 53.2%, Variant A 14.5% — Variant A's best rate since the fix), and Variant A now sees nearly its whole universe on average (14.9 of 15.5 pairs), which makes its zero-entry days a stronger statement about the market than the main model's.

## Worked example

Walk-through of one real 2026-11-13 run: the main-model run ending 19:22:12 WIB, the last main run inside this window.

1. Run: elapsed 675.9 s, deadline_hit false (under the 750 s limit), universe 80 pairs, pairs seen 74.
2. Rejection counts: non_v2_id 16, non_v2_revert 34, non_wbnb 6, dust 3, holder_skip 5, holder_gate 5, chart_skip 1, sighting 9, v2_holders / v2_dev / v2_lp 0.
3. Stage cost (cumulative across pairs): pair_info 797.1 s, quote 120.6 s, audit 61.6 s, holder 276.8 s, chart 112.5 s.
4. Outcome: entries_made 0, sightings 23, open_positions 0. The ledger did not change.
5. What this shows: on a run with good coverage (74 of 80 pairs, no deadline hit), the machine still rejected everything before the v2 gates — 9 pairs stopped at the sighting rule, 5 at the holder gate. What this does not show: whether the sighting rule itself is set too tightly, because the control arm that would answer that still does not exist. Contrast with the worst main run of the day (17:56:11 WIB, 34 of 80 pairs): the same "0 entries" outcome there says far less.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/ledger.json and state, in one sentence, the cash, the number of positions, and the 2026-11-13 daily realized PnL (expected: cash 0.01107179 BNB virtual, 0 positions, realized 0).
2. Open workspace/paper-trading/variant-a/ledger.json and do the same for Variant A (expected: cash 0.01072416 BNB virtual, 0 positions, realized 0); confirm both arms agree the day was a zero day, and that cash is unchanged from 2026-11-11 and 2026-11-12.
3. From the two run-diagnostics.jsonl files, compute the 2026-11-13 deadline-hit rate for each arm (expected: main 42/79 ≈ 53%, Variant A 11/76 ≈ 14%) and compare with 2026-11-11 (38% / 23%) and 2026-11-12 (61.3% / 29.6%). Note that the arms moved in opposite directions.
4. Compare the mean cumulative stage seconds for pair_info vs holder in each arm (expected: main 1,149.5 vs 221.2; Variant A 457.1 vs 209.6) and name the current bottleneck.
5. Feedback check: if Variant A saw 14.9 of 15.5 pairs on average and still admitted nothing, the correct conclusion for Variant A is "the machine saw nearly the whole market and admitted nothing" — a stronger statement than for the main model, which saw 66.4 of 79.7 on average and only 34 of 80 on its worst run. Neither conclusion is "the model is proven" or "the model is broken" without the control arm.

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading both ledgers directly instead of trusting a chat summary, computing the deadline rate from the full day's diagnostics instead of quoting one slow run, comparing stage costs relatively instead of against elapsed time, noticing that the two arms moved in opposite directions before blaming the network for both), name the one most useful next adjustment (e.g. always pair a zero-entry day with the coverage figure — a zero on a day Variant A saw 14.9 of 15.5 pairs means something different from a zero on a day the main model saw 34 of 80 — and never present a virtual balance as real profit), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to resume BACOT SCALPING (real money) once funds return, and whether the paper model's gates should inform that decision. Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. Today's transfer warning is specific: three zero-entry days after a +30% day are exactly the kind of whiplash that tempts either "the model is dead" or "the model is proven" — both are premature with 6 days left, one token ever traded, and no control arm. The deadline split adds a second warning: do not rebuild the model around a one-day latency number that moves in opposite directions in the two arms on the same day.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, forgetting the kill-switch is now equity-measured, forgetting that holder data now comes from GoPlus with bundle/dev-cluster unverified, forgetting that the current bottleneck is pair_info rather than holder, or forgetting that the deadline rates split on 2026-11-13 — main 53.2%, Variant A 14.5%) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will the model find a second, different token before 2026-11-19, or will the whole trial's wins be GANG alone? A single-token trial cannot prove a model, and the trial is now two-thirds done.
- Is the deadline rate's day-to-day instability a property of the network, the model, or both? The 2026-11-13 split (main worse, Variant A best) argues against a single shared cause; keep recording the rate per arm per day rather than averaging.
- When will the coin-flip control + hold benchmark be built? Without it, neither the 2026-11-10 wins nor the three consecutive zero days can meet the trial's own "proven" gate.
- Was GANG ever recorded in the forward-return ledger? Still no — the ledger table is empty. If it stays empty, the screen's hit rate stays unmeasured even after its first entries.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL (0 wins / 4 losses, −0.00286388 WBNB) or with MODAL BACOT live trading (live-trading-feed stalled repeatedly on 2026-11-13, episodes from 11:21, 12:25, 13:26, 15:39, and 17:25 WIB). Keep the three ledgers separate in every future note and letter.
- The user asked on 2026-11-09 whether 5–10% per day from trading is possible; the honest answer given then was no, not proven. One virtual +30% day followed by three zero days does not change that answer — it is four data points inside a trial that ends 2026-11-19.
- The user declined a sell-all AGC offer on 2026-11-13 ~19:01 WIB (tap "Tidak, tahan AGC") — do not re-offer selling all AGC unless the user reopens it. That decision is about AGC holdings, not about this paper model, and the two must stay separate.

## Next review

2026-11-14T12:33:17Z. Next study should re-check the deadline-hit rate per arm, confirm whether the forward-return ledger and control arm moved at all, and count the zero days since the last entry (now three).

## Already Covered in Main Chat

- The 2026-11-13 12:19 WIB, 14:19 WIB, 16:19 WIB, and 18:19 WIB 2-hour recaps each restated paper cash 0.01107 BNB virtual (main) and 0.01072 BNB virtual (Variant A), 0 open positions, and 0 entry / 0 exit on 2026-11-13 — so today's zero-entry day and unchanged cash were already reported to the user four times.
- The 2026-11-13 18:53 WIB "Cek tugas rutin" reply restated the same paper status (0 entry/exit today) alongside the routine-jobs check.
- The same recaps reported the live-trading feed stalling repeatedly through the day (episodes from 11:21, 12:25, 13:26, 15:39, and 17:25 WIB) — the network-degradation context for today's deadline figures.
- The 2026-11-11 Day Seven brief (delivered 2026-11-12 05:28 WIB) already covered the day-7 zero day, the GoPlus holder fix, the 38% / 23% deadline rates, and the pair_info bottleneck — the themes today's note extends.
- Not reported in main chat: the full-day 2026-11-13 deadline-hit rates (53.2% main / 14.5% Variant A), the pairs-seen means (66.4 / 79.7 main, 14.9 / 15.5 Variant A), the worst-coverage main run (34 of 80 at 17:56:11 WIB), the opposite-direction move of the two arms, or the pair_info stage means (1,149.5 s main / 457.1 s Variant A).

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers, diagnostics, and forward-return ledger are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-12/model-degen-paper-trading-mandiri.md (read in full): day-8 check, second consecutive zero-entry day in both arms, deadline rates 61.3% main / 29.6% Variant A, pair_info bottleneck finding (1,229.6 s main / 476.1 s Variant A cumulative), v2 kills 0, forward-return ledger still empty, control arm still missing, and the open question whether the deadline regression was a network artefact or a new floor.
- Prior study notes 2026-11-05 through 2026-11-11 (known from the 2026-11-12 note's trajectory): 0 trades until 2026-11-09, first GANG entries 2026-11-09, TP exits +30% both arms 2026-11-10, GoPlus holder fix and equity kill-switch fix applied, day-7 zero day and 38% / 23% deadline rates on 2026-11-11.
- Prior briefs (filenames listed): BACOT DEGEN Day Five (2026-11-09 12.24.28).html, BACOT DEGEN Head-to-Head (2026-11-08 12.17.08).html, Variant A Day One (2026-11-07 12.28.06).html, BACOT DEGEN Day Seven (2026-11-11 12.15.09).html — the Day Seven brief covers the day-7 zero day, the deadline improvement, and the pair_info bottleneck; no brief exists for day 8 or day 9.
- Repetition search (grep over this goal's agent_notes/*.md and briefs/, variants "zero-entry", "deadline", "pair_info bottleneck", "GANG take-profit", "day eight", "day nine"): the 2026-11-11 and 2026-11-12 notes match on "GANG", "deadline", "pair_info", and "zero day" (the TP exits, the fixes, the deadline question, and the day-7 and day-8 zeros are all there); no prior note or brief contains the 2026-11-13 deadline rates (53.2% / 14.5%), the pairs-seen means, the opposite-direction move, or the worst-coverage run. Today's quantitative findings are new against the notes and briefs, but the Letter's centre — another zero-entry day with unchanged cash — was already reported in main chat four times on 2026-11-13 (12:19, 14:19, 16:19, and 18:19 WIB recaps), which is what decides the ruling below.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active; current state "Posisi GANG ditutup take-profit +30% virtual; kas virtual 0,01107 BNB dan tidak ada posisi terbuka." — still accurate after the third zero day, since the ledgers did not move.
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-14T12:33:17Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Ledgers read directly in this turn: workspace/paper-trading/ledger.json (cash 0.011071790886431537 BNB virtual, positions empty, daily 2026-11-13 realized 0 / entries 0 / exits 0) and workspace/paper-trading/variant-a/ledger.json (cash 0.010724160078509572 BNB virtual, positions empty, daily 2026-11-13 realized 0 / entries 0 / exits 0).
- Diagnostics read directly in this turn: workspace/paper-trading/run-diagnostics.jsonl (79 runs on 2026-11-13, 00:12–19:22 WIB, 42 deadline hits, elapsed mean 699.9 s, pairs seen mean 66.4/79.7, entries 0, v2 kills 0, sighting kills 300, holder_gate 467, pair_info stage mean 1,149.5 s cumulative, holder 221.2 s) and workspace/paper-trading/variant-a/run-diagnostics.jsonl (76 runs, 00:02–19:28 WIB, 11 deadline hits, elapsed mean 593.8 s, pairs seen mean 14.9/15.5, entries 0, v2 kills 0, sighting kills 242, holder_gate 472, pair_info 457.1 s, holder 209.6 s).
- Forward-return ledger read in this turn: workspace/paper-trading/forward-return-ledger.md — table header only, no data rows, no 2026-11-13 mention.
- Control-arm check in this turn: workspace/paper-trading/ directory listing shows no control ledger or control script; the control arm remains unbuilt.
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window 2026-11-12T12:24:29Z → 2026-11-13T12:34:52Z) plus the run's chunk handoff: the four 2026-11-13 2-hour recaps (12:19, 14:19, 16:19, 18:19 WIB) already reported today's zero entries and unchanged cash; the feed-stall episodes and the user's 2026-11-13 ~19:01 WIB refusal of the sell-all AGC offer ("Tidak, tahan AGC") came from the same window.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet; daily profit benchmark 10% net with symmetric 10% loss limit; never force a trade to chase the daily target; trial ends 2026-11-19.

### Searches skipped or unavailable

- No new web search was run: the trial's own record is primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief HTML files were listed and their subjects taken from the goal record and prior notes, not re-read in full: all four predate the 2026-11-13 zero day and the deadline split, so re-reading their rendered HTML would not change the newness ruling.
