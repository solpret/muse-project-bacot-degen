# Study Notes - 2026-11-07 - BACOT DEGEN
<!-- studying-run-start: 2026-11-07T12:11:09Z -->

## Goal in one line

BACOT DEGEN (`goal_b9d1c43a21e5`, slug `model-degen-paper-trading-mandiri`) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 → 2026-11-19. Variant A — the same gates with a clean-universe pre-filter (GeckoTerminal `dex == pancakeswap_v2`, quote token WBNB, reserve ≥ $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:46 WIB, by the user's correction to "varian A saja dulu" (2026-11-06 ~23:42 WIB, after first saying "Uji Varian A + B"). Variant B was not built.

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The plan's retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study therefore checks (a) Variant A's first full day head-to-head against the main model — did the pre-filter change anything, and where does the model now actually die? (b) whether the trial has produced its first entry yet in either arm, and (c) whether the deadline problem is better or worse — without confusing any of this with the live BACOT SCALPING work (real money, re-enabled 2026-11-07 with a STOCKMEMES buy at ~18:52 WIB, round 1 lost ~19:05 WIB), which is a different activity with a separate ledger.

## What today's evidence shows

### Variant A day 1: the upstream leak is closed — and the blocker moved downstream to the holder stage

- Variant A ledger (`~/workspace/paper-trading/variant-a/ledger.json`, read 2026-11-07 ~19:11 WIB): started 2026-11-07T06:46:15+07:00, ends 2026-11-19, virtual capital 0.010 BNB, cash 0.010 BNB, positions `[]`, trades `[]`, daily 2026-11-07 realized 0.0, entries 0, exits 0, sightings 8.
- Variant A diagnostics (`run-diagnostics.jsonl`, 45 runs on 2026-11-07): entries sum 0. Pre-filter drops per run are large and stable — e.g. latest run 2026-11-07 19:13:06 WIB: raw universe 80 → 16 after pre-filter (dex 40, quote 7, liq 17 dropped), 16/16 seen, 546.5 s, no deadline hit, entries 0, sightings 8. Across all 45 runs today, `non_v2_id` = 0 and `non_v2_revert` = 0 — the 2026-11-06 evaluation's biggest killer (~53% of the universe not PCS V2) is gone from this arm, as the launch report promised.
- But the pre-filter did not buy an entry, and it exposed the next bottleneck. Aggregated over Variant A's 45 runs today: `holder_skip` 347 + `holder_gate` 347 = 694 of ~720 pair-slots evaluated — essentially every pair that survives the pre-filter dies at the holder stage (snapshot unreadable, or concentration/LP/bundle failure), before the sighting leg can confirm anything. `sighting` 114 is the count of candidates reaching that stage; none confirmed. `audit_skip` 145 (audit without result = fail-closed) is the second-largest bucket. `v2_gate` only 2.
- The holder stage is also now the latency bottleneck in Variant A: average stage seconds today are holder 480.5 s vs pair_info 195.7 s, audit 42.3 s, quote 79.3 s, chart 8.7 s. The deadline still hits Variant A despite the small universe: 13 of 45 runs (29%) hit the soft deadline — e.g. 2026-11-07 19:02:22 WIB, 803.4 s, only 11/16 pairs seen, holder stage 548.0 s. So "clean universe" fixed the pair_info cost but not the run's total cost; the holder stage alone now eats most of the budget.
- Main model, same day: 77 runs, entries 0, deadline hit 32 of 77 (42%) — worse than the 2026-11-06 note's 2 of the last 6 runs. Average pairs seen 69.7/80. Aggregated reasons today: `non_v2_revert` 2,013, `non_v2_id` 953, dust 734, non-WBNB 643, `holder_skip` 566, `holder_gate` 534, `audit_skip` 243, `sighting` 180. Average stage seconds: pair_info 649.0 s, holder 408.0 s. The 2026-11-06 note's warning stands and is now quantified for a full day: on deadline-hit runs roughly half the universe is never evaluated, so "0 entries" on those runs is a partial-universe verdict, not a full one.
- Main ledger (`~/workspace/paper-trading/ledger.json`, read 2026-11-07 ~19:11 WIB): cash 0.010 BNB, 0 positions, 0 trades, daily 2026-11-07 entries 0, sightings 10 (was 8 on 2026-11-06). New baselines first seen 2026-11-07: `0x7ab8…314` 07:26:42 WIB (48 holders, reserve 534.67), `0x0c63…405` 08:17:31 WIB (91 holders, 155.18), `0x6ec9…edb` 08:17:51 WIB (51 holders, 705.27), `0xb2a4…777` 09:18:10 WIB (113 holders, 7.87), `0xa34c…777` 09:56:36 WIB (158 holders, 8.07), `0x50c5…777` 10:09:10 WIB (454 holders, 39.02), `0xfb81…777` 10:20:57 WIB (132 holders, 7.36), `0x2a63…777` 14:15:47 WIB (243 holders, 9.16), `0x3303…60e` 18:13:56 WIB (7 holders, 64.36). The 2026-11-06 sighting `0x94fa…777` (first seen 2026-11-06 20:18:05 WIB, 118 holders) is still carried.
- One sighting deserves a named follow-up, not a conclusion: `0x50c5fd46f8e8d56f35c358d99b33e67d8f547777` (RELAY, also discussed in main chat on 2026-11-07 as a live-feed coin) is a baseline in both ledgers — main: 454 holders / reserve 39.02 at 10:09:10 WIB; Variant A: 582 holders / reserve 46.31 at 14:00:25 WIB. Timing matters here: per the main-chat RELAY investigation, wave 2 of the run peaked at ~04:00 WIB (market cap ~$797K) and the price had already fallen to ~$0.00036 by the time it was discussed — so the main arm baselined RELAY roughly 6 hours after its peak and Variant A roughly 10 hours after. The sighting leg recorded the runner post-hoc, not before its run. Holders +28% and reserve +19% between those two readings would clear the +10%/+5% confirmation thresholds if compared directly, yet neither arm recorded an entry. Do not conclude it "should have entered": the two readings are from different arms with different first-seen times, and confirmation is measured against each arm's own baseline on a second sighting, which may have failed on audit/holder/v2 gates or on a deadline-truncated run. The next study should check RELAY's per-run confirmation path explicitly before drawing any lesson from it.

### What has not changed

- Still zero trades in both arms after three days of the trial (2026-11-05 → 2026-11-07): main 229 runs total, Variant A 45 runs, entries 0 everywhere, both cash balances 0.010 BNB intact.
- Forward-return ledger (`~/workspace/paper-trading/forward-return-ledger.md`, read 2026-11-07 ~19:11 WIB): still empty — no candidate has ever been recorded, so the screen's hit rate is still unmeasured. The 2026-11-06 evaluation's "measure the near-misses" layer has not produced its first row either.
- Control arm and hold benchmark (Quant-Lab "proven" gate, from the 2026-11-05 note): still not built. The trial still cannot distinguish a future win streak from luck.
- Trial end date unchanged (2026-11-19); daily 10% budget framing unchanged; separation from MODAL BACOT unchanged. BACOT SCALPING's real-money round 1 (STOCKMEMES, −0.002 WBNB + gas, lost ~19:05 WIB 2026-11-07) and the live MODAL BACOT feed are separate ledgers — do not mix them into this goal's numbers.
- First head-to-head comparison is scheduled for ~07:00 WIB 2026-11-08, after ~24 hours of parallel running (per the Variant A launch report, 2026-11-07 07:43 WIB). That comparison is the next decision point for this goal.

## Prerequisite check

- Prerequisites in place: v2 engine running on the 15-minute cron (paper-trading-15m), Variant A running on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, pre-filter verified working in code and in diagnostics (`non_v2` = 0 across 45 runs), trial window to 2026-11-19.
- Gap to close first (unchanged from 2026-11-05, now sharper): **no control arm and no benchmark** in the trial. Until a coin-flip control and a hold benchmark run beside the model, a future win streak cannot be distinguished from luck.
- Second gap (changed today — it moved): **the binding constraint is now the holder stage, not the universe**. Variant A proved the upstream leak is fixable, but holder snapshots/gates kill ~96% of surviving pairs and the holder stage (avg ~480 s in Variant A) is what pushes runs past the deadline. Before trusting "0 entries" as a gates verdict, the next study should check (i) whether the holder gate's fail-closed snapshot failures are a data problem (RPC/timeouts) or a real quality signal, and (ii) whether the holder stage can be made faster or parallel, since it is now the single biggest time cost in both arms.
- Third gap (unchanged): the forward-return ledger is still empty; the first recorded candidate is still waiting. The RELAY double-baseline question above is the concrete first check for it.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — ≥12 candles, complete holder snapshot with ≥50 holders, identified dev, LP burn ≥50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if cash falls below 70% — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve ≥ $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards.

## Worked example

Walk-through of one real Variant A evaluation: the 2026-11-07 19:13:06 WIB run.

1. **Universe:** 80 raw GeckoTerminal pools; pre-filter drops 64 (dex 40, quote 7, liq 17) → 16 to evaluate.
2. **Shape filters:** `non_v2_id` 0, `non_v2_revert` 0, dust 1 — the upstream leak is gone in this arm.
3. **Holder stage (the new bottleneck):** 9 `holder_skip` + 9 `holder_gate` — more than the 16 pairs seen, because reasons accumulate across the run's evaluations; effectively every surviving pair dies here or at audit (`audit_skip` 3).
4. **Sighting leg:** 3 candidates reached the sighting stage; the ledger's Variant A sighting total stands at 8; none confirmed.
5. **Result:** 0 entries, 0 positions, cash unchanged at 0.010 BNB; 546.5 s, no deadline hit on this run — but the run before it (19:02:22 WIB) hit the deadline at 803.4 s with only 11/16 seen, holder stage 548.0 s.
6. **What this shows:** the pre-filter works exactly as designed, and the model still makes no trade — because the constraint was never only the universe. The holder gate and the holder stage's latency are now the binding constraints, and on deadline-hit runs the "no trade" verdict covers only part of the cleaned universe.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open `~/workspace/paper-trading/variant-a/ledger.json` and state, in one sentence, the cash, the number of positions, and the number of sightings.
2. Open `~/workspace/paper-trading/variant-a/run-diagnostics.jsonl`, take the latest line, and state the raw universe, how many pairs survived the pre-filter, how many were seen, and whether the deadline was hit.
3. List the top two rejection reasons by count in that run, and say which stage (pair_info / holder / audit / quote / chart) took the most seconds.
4. Compare the outcome to the main ledger (`cash_bnb`, `positions`, `trades`) and confirm both arms agree on entries = 0.
5. Feedback check: if entries = 0 and cash = 0.010 BNB in both arms, the correct conclusion is "pre-filter works, holder stage is now the blocker, no evidence about entries yet" — not "Variant A failed" and not "the model is proven safe."

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading the diagnostic reasons and stage timings instead of guessing why no entry happened), name the one most useful next adjustment (e.g. always check whether the run hit its deadline — and which stage ate the time — before concluding the full universe was evaluated), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is about to decide whether to add funds to BACOT SCALPING (real money, round 1 of the new 5-round flap test lost 0.002 WBNB on 2026-11-07, and the earlier AGC/BURN test sat at 2 wins / 6 rounds, below the 40% bar). Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. Variant A's lesson transfers directly: fixing the most visible leak (universe quality) does not fix the outcome if the next bottleneck (holder stage) is the binding one — check where the funnel actually narrows before spending on the next fix.

## Confidence check

Ask the user to rate confidence (1–10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, or forgetting the kill-switch) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will any of the 10 main-arm / 8 Variant A sightings confirm into the model's first entry before 2026-11-19, or will the trial end with zero trades? Either outcome needs interpreting: zero trades means the gates may be too strict for the current market, not that the model is "safe."
- Why did RELAY (`0x50c5…777`) record a baseline in both arms with apparent holder/reserve growth between readings, yet produce no entry in either? Check its per-run confirmation path before the 2026-11-08 ~07:00 WIB comparison.
- Is the holder gate's kill rate (~96% of Variant A survivors) a real quality signal or a data problem — how much of `holder_skip` is RPC/timeout failure vs genuinely unreadable snapshots?
- Can the holder stage be made faster (it averages ~480 s in Variant A, ~408 s in main) so deadline hits stop truncating the universe — 42% of main runs and 29% of Variant A runs hit the deadline today?
- When will the coin-flip control + hold benchmark be built (method-adoptions §5d step 1)? Without it, the trial cannot meet its own "proven" gate.
- The forward-return ledger's first row: which candidate, and when? If no candidate is ever recorded, the screen's hit rate stays unmeasured.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL or with MODAL BACOT live trading. Keep the three ledgers separate in every future note and letter.

## Already Covered in Main Chat

- User asked "Bacot degen kemana muse?" on 2026-11-06 ~23:29 WIB; main agent reported the 178-run / 9,032-pair evaluation (0 entries, sighting leg the terminal blocker) and proposed Variants A and B.
- User first said "Uji Varian A + B" then corrected to "varian A saja dulu" on 2026-11-06 ~23:41–23:42 WIB; main agent confirmed Variant A only, B not built.
- Main agent reported Variant A built, verified, and running on 2026-11-07 ~07:43 WIB (pre-filter working, non_v2 = 0, 0 entries in its first 3 runs, first comparison ~07:00 WIB 2026-11-08).
- Main agent reported paper status in the 2-hour recaps on 2026-11-07 (08:19, 10:19, 16:19 WIB): 0 trades, 0 positions, cash 0.010 BNB in both arms.
- What main chat has NOT yet heard: today's full-day aggregates (main 77 runs / 32 deadline hits; Variant A 45 runs / 13 deadline hits), the holder gate as the new dominant blocker (~96% of Variant A survivors), the holder stage as the latency bottleneck (~480 s average in Variant A), or the RELAY double-baseline observation.
- User set the daily 10% profit/loss benchmark and the BACOT SCALPING 5-round test in main chat; those belong to the live scalp work, not this paper goal.
- No prior brief exists for this goal (briefs/ is empty as of this run).

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers and diagnostics are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note `workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-06/model-degen-paper-trading-mandiri.md` (read in full): 0 trades, 8 sightings, 135 runs, deadline hit 2 of last 6 runs, P-1 sighting fix verified, control arm and forward-return ledger still missing. Today's note supersedes its "deadline problem is not gone" observation with full-day counts (main 32/77, Variant A 13/45) and adds the Variant A arm, which did not exist when that note was written.
- Prior study note `workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-05/model-degen-paper-trading-mandiri.md` (known from the 2026-11-06 note's trajectory and the repetition grep): 0 trades, 0 sightings, 43 runs, five validation methods adopted, control arm and forward-return ledger still missing.
- Repetition search (grep over `agent_notes/` and `briefs/` for this goal, variants "Variant A", "Varian A", "holder gate", "deadline", "BACOT DEGEN", "paper trading"): the 2026-11-05 and 2026-11-06 notes matched on "BACOT DEGEN", "paper trading", "deadline", and "holder gate"; neither note contains any Variant A result (Variant A was proposed in main chat on 2026-11-06 ~23:39 WIB and built after the 2026-11-06 note), and neither contains the holder-stage bottleneck finding; `briefs/` is empty (no brief files exist for this goal). The day-1 Variant A head-to-head and the holder-stage diagnosis are new against everything the search returned.

### Scaffolds and support tactics

- Goal record via `user_goal.get` (goal_b9d1c43a21e5): category money, exploratory, active, current state "BACOT DEGEN v2 is active on a 15-minute cron, with the paper trial running to November 19."
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-08T12:11:09.503882929Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Main paper ledger `~/workspace/paper-trading/ledger.json` — cash 0.010 BNB, 0 positions, 0 trades, sightings 10, ends 2026-11-19 (read 2026-11-07 ~19:11 WIB).
- Main run diagnostics `~/workspace/paper-trading/run-diagnostics.jsonl` — 229 runs total, 77 on 2026-11-07, 0 entries, 32 deadline hits; latest 2026-11-07 19:08:57 WIB, 57/80 pairs, 785.3 s, deadline hit, entries 0, sightings 10.
- Variant A ledger `~/workspace/paper-trading/variant-a/ledger.json` — cash 0.010 BNB, 0 positions, 0 trades, sightings 8, started 2026-11-07T06:46:15+07:00 (read 2026-11-07 ~19:11 WIB).
- Variant A run diagnostics `~/workspace/paper-trading/variant-a/run-diagnostics.jsonl` — 45 runs, all on 2026-11-07, 0 entries, 13 deadline hits; latest 2026-11-07 19:13:06 WIB, raw 80 → 16 after pre-filter, 16/16 seen, 546.5 s, no deadline, entries 0, sightings 8.
- Forward-return ledger `~/workspace/paper-trading/forward-return-ledger.md` — still empty (read 2026-11-07 ~19:11 WIB).
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via `muse.context_fetch` (conversation, window since 2026-11-06T12:02:53Z) — the 2026-11-06 evaluation, the Variant A/B proposal, the user's "varian A saja dulu" correction, the Variant A launch report, and the 2-hour recaps were all already reported to the user (see Already Covered in Main Chat). The saved fetch output (`/tmp/jarvis-tool-output-olDIGt.txt`) was grepped for BACOT DEGEN / paper / Variant A mentions; Variant A appears 10 times, all about the proposal, the correction, the launch, or the "0 trade" recap lines — none about today's holder-gate or deadline aggregates.
- Handoff from chunks 1–2 of this run: Variant A built + verified + running 2026-11-07 ~07:44 WIB, first comparison ~07:00 WIB 2026-11-08; main-model evaluation 178 runs / 9,032 pairs / 0 entries; BACOT SCALPING stopped 2026-11-06 then re-enabled 2026-11-07 with the STOCKMEMES round-1 loss.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet.

### Searches skipped or unavailable

- No new web search was run: the trial's own ledgers/diagnostics are primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- No prior-brief reading was possible: no briefs exist for this goal.
