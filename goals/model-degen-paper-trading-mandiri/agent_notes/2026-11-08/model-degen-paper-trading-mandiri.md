# Study Notes - 2026-11-08 - BACOT DEGEN
<!-- studying-run-start: 2026-11-08T12:02:54Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 to 2026-11-19. Variant A — the same gates with a clean-universe pre-filter (GeckoTerminal dex == pancakeswap_v2, quote token WBNB, reserve >= $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:46 WIB, by the user's correction to "varian A saja dulu".

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study therefore delivers the head-to-head comparison that was due ~07:00 WIB on 2026-11-08 and was still outstanding at the run start (19:02 WIB): after ~36 hours of parallel running, did Variant A change anything, where does the model now actually die, and is the deadline problem better or worse? It also closes the RELAY double-baseline question left open in the 2026-11-07 note. It does not confuse any of this with live BACOT SCALPING (real money, rounds 3-10 postponed since 2026-11-08 07:01 WIB, score 0 wins / 2 losses, pool now HYPE on HyperEVM) or with MODAL BACOT live trading — separate ledgers, separate money.

## What today's evidence shows

### Head-to-head, 2026-11-08 (partial day, runs to 18:56 WIB)

Ledgers read 2026-11-08 ~19:02 WIB. Both arms still at zero: cash 0.010 BNB, 0 positions, 0 trades, daily 2026-11-08 entries 0, exits 0, realized 0.0. Day 4 of the trial with no entry in either arm.

- Main arm: 73 runs on 2026-11-08, 50 hit the soft deadline (68%), average elapsed 733 s, average pairs seen 59.4 of 80. Full-day 2026-11-07 for comparison: 96 runs, 50 deadline hits (52%), average pairs seen 66.3. The deadline problem got worse, not better — on more than two-thirds of today's runs the verdict covers only part of the universe. Average stage seconds today: pair_info 734.3, holder 446.7, quote 111.7, audit 47.1, chart 6.4. Pair_info is again the biggest time cost in the main arm, holder second.
- Variant A: 68 runs on 2026-11-08, 31 deadline hits (46%), average elapsed 680 s, average pairs seen 14.7 of ~17-22 surviving the pre-filter. Full-day 2026-11-07: 61 runs, 24 deadline hits (39%), average pairs seen 14.3. Also worse. Average stage seconds today: holder 467.4, pair_info 262.9, quote 107.3, audit 46.2, chart 9.2. In Variant A the holder stage is still the single biggest time cost, as the 2026-11-07 note found.
- Caveat on the comparison: 2026-11-08 is a partial day (runs end 18:37 WIB main, 18:56 WIB Variant A at read time), while 2026-11-07 is a full calendar day. The direction (worse in both arms) is consistent across both arms, but the exact percentages will move when the day completes.

### The bottleneck moved again: candidates now reach the v2 gate — and die on partial snapshot / LP

This is the genuinely new funnel finding today, and it was not in the 2026-11-07 note or brief.

- Main arm, 2026-11-08 reason totals: non_v2_revert 1,466, non_v2_id 718, dust 631, non_wbnb 558, holder_skip 504, holder_gate 495, audit_skip 286, sighting 133, v2_gate 20, v2_partial 19, v2_lp 20. Runs with at least one v2_gate evaluation: 20 of 73.
- Main arm, full-day 2026-11-07: only 4 runs had any v2_gate evaluation, total v2_gate 4.
- Variant A, 2026-11-08: holder_skip 469, holder_gate 458, audit_skip 244, sighting 162, dust 90, v2_gate 25, v2_partial 24, v2_lp 25, non_v2 0 (pre-filter still working). Runs with at least one v2_gate evaluation: 25 of 68.
- Variant A, full-day 2026-11-07: only 2 runs had any v2_gate evaluation, total v2_gate 2.
- Reading: the holder stage still kills the large majority (~96% of Variant A survivors, as before), but the survivors that do get through now reach the v2 gate in real numbers — 20 main, 25 Variant A evaluations today against 4 and 2 yesterday — and essentially all of them die there on v2_partial (incomplete snapshot/candles) or v2_lp (LP check). The funnel's terminal blocker has shifted one stage deeper: from "nothing reaches v2" to "things reach v2 and fail on data completeness / LP". That is a different diagnosis from the 2026-11-07 note, and it changes the next fix: the question is now whether v2_partial is a data problem (snapshot/candle coverage) and whether v2_lp failures are real LP quality or the same snapshot incompleteness wearing a different label. Do not conclude the LP gate itself is too strict until those two are separated.
- Sighting reason-counts also rose (main 133, Variant A 162 today), but sightings carried in the ledgers fell: main 5 (was 10 on 2026-11-07), Variant A 7 (was 8). One new main sighting today: 0x0cee7a04355b2e2d7248d9566db8889cf44f7777, first seen 2026-11-08 18:12 WIB (273 holders, reserve 12.51). Sightings churn — old baselines leave the list without confirming — so a high sighting reason-count is not the same as a growing watchlist.

### RELAY question closed: no entry, no longer carried

The 2026-11-07 note left open why RELAY (0x50c5fd46f8e8d56f35c358d99b33e67d8f547777) recorded a baseline in both arms with apparent holder/reserve growth between readings yet produced no entry. Today's check: RELAY appears in neither ledger's current sightings list. It never confirmed into an entry in either arm and is no longer carried. That closes the question as a negative: the double-baseline was two arms baselining the same post-peak runner at different times (main ~6 hours after its ~04:00 WIB peak, Variant A ~10 hours after), not a missed confirmation. Do not reopen it as a near-miss without fresh per-run evidence.

### What has not changed

- Still zero trades in both arms after four days of the trial (2026-11-05 to 2026-11-08): main 321 runs total, Variant A 129 runs total, entries 0 everywhere, both cash balances 0.010 BNB intact.
- Forward-return ledger (workspace/paper-trading/forward-return-ledger.md, read 2026-11-08 ~19:02 WIB): still empty — no candidate has ever been recorded, so the screen's hit rate is still unmeasured.
- Control arm and hold benchmark (Quant-Lab "proven" gate, from the 2026-11-05 note): still not built. The trial still cannot distinguish a future win streak from luck.
- Trial end date unchanged (2026-11-19); daily 10% budget framing unchanged; separation from MODAL BACOT unchanged. BACOT SCALPING's real-money results stay in their own ledger and are not this goal's numbers.
- The user was told in main chat on 2026-11-08 17:10 WIB that the head-to-head comparison was still being prepared and would arrive separately. As of this run it had not arrived — this note is the first complete version of it.

## Prerequisite check

- Prerequisites in place: v2 engine running on the 15-minute cron (paper-trading-15m), Variant A running on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, pre-filter verified working in code and in diagnostics (non_v2 = 0 across all 68 Variant A runs today), trial window to 2026-11-19.
- Gap to close first (unchanged, now sharper): no control arm and no benchmark in the trial. Until a coin-flip control and a hold benchmark run beside the model, a future win streak cannot be distinguished from luck.
- Second gap (changed today — it moved one stage deeper): the binding constraint is no longer only the holder stage. Candidates now reach the v2 gate and die on v2_partial / v2_lp. Before trusting "0 entries" as a gates verdict, the next study should check (i) whether v2_partial is missing candle/snapshot data or a real quality signal, (ii) whether v2_lp failures are genuine LP failures or the same incompleteness, and (iii) whether the holder stage can be made faster, since deadline hits rose in both arms today (main 68%, Variant A 46%).
- Third gap (unchanged): the forward-return ledger is still empty; the first recorded candidate is still waiting.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if cash falls below 70% — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards.

## Worked example

Walk-through of one real Variant A evaluation: the 2026-11-08 18:33:06 WIB run (deadline hit).

1. Universe: 80 raw GeckoTerminal pools; pre-filter drops 58 (dex 39, quote 9, liq 10) to 22 to evaluate.
2. Shape filters: non_v2_id 0, non_v2_revert 0, dust 3 — the upstream leak is still gone in this arm.
3. Holder stage: 9 holder_skip + 9 holder_gate; audit_skip 5.
4. V2 gate (the new stage): v2_gate 1, v2_partial 1, v2_lp 1 — a candidate reached the v2 gate and died there on partial data / LP.
5. Sighting leg: 0 candidates reached it on this run; ledger sightings stand at 7.
6. Result: 0 entries, 0 positions, cash unchanged at 0.010 BNB; 835.0 s, deadline hit, only 18 of 22 pairs seen, holder stage 595.8 s.
7. What this shows: the pre-filter still works exactly as designed, the holder stage still eats most of the time and kills most pairs, and the newsworthy part is step 4 — candidates are now getting far enough to fail at v2, which the 2026-11-07 note never saw. On deadline-hit runs the "no trade" verdict still covers only part of the cleaned universe.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/variant-a/ledger.json and state, in one sentence, the cash, the number of positions, and the number of sightings.
2. Open workspace/paper-trading/variant-a/run-diagnostics.jsonl, take the latest line, and state the raw universe, how many pairs survived the pre-filter, how many were seen, and whether the deadline was hit.
3. List the top two rejection reasons by count in that run, and say whether any v2_gate evaluation appears — and if so, what v2_partial and v2_lp say.
4. Compare the outcome to the main ledger (cash_bnb, positions, trades) and confirm both arms agree on entries = 0.
5. Feedback check: if entries = 0 and cash = 0.010 BNB in both arms, the correct conclusion is "pre-filter works, holder stage is still the blocker, but candidates now reach v2 and die on partial/LP, and deadline hits got worse" — not "Variant A failed" and not "the model is proven safe."

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading the diagnostic reasons and stage timings instead of guessing why no entry happened), name the one most useful next adjustment (e.g. always check whether the run hit its deadline — and which stage ate the time — before concluding the full universe was evaluated, and now also check whether v2_partial is a data gap before blaming the LP gate), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to resume BACOT SCALPING (real money, rounds 3-10 postponed, score 0 wins / 2 losses) once funds return, and whether the paper model's gates should inform that decision. Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. BACOT DEGEN's lesson transfers directly: fixing the most visible leak (universe quality) does not fix the outcome if the next bottleneck (holder stage, now v2 partial/LP) is the binding one — check where the funnel actually narrows before spending on the next fix.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, or forgetting the kill-switch) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will any of the 5 main-arm / 7 Variant A sightings confirm into the model's first entry before 2026-11-19, or will the trial end with zero trades? Either outcome needs interpreting: zero trades means the gates may be too strict for the current market, not that the model is "safe."
- Is v2_partial a data-completeness problem or a real quality signal — and are v2_lp failures genuine LP failures or the same incompleteness? Separating those two decides the next fix.
- Is the holder gate's kill rate (~96% of Variant A survivors) a real quality signal or a data problem — how much of holder_skip is RPC/timeout failure vs genuinely unreadable snapshots?
- Can the holder stage be made faster (it averages ~467 s in Variant A, ~447 s in main today) so deadline hits stop truncating the universe — 68% of main runs and 46% of Variant A runs hit the deadline today, both worse than 2026-11-07?
- When will the coin-flip control + hold benchmark be built (method-adoptions section 5d step 1)? Without it, the trial cannot meet its own "proven" gate.
- The forward-return ledger's first row: which candidate, and when? If no candidate is ever recorded, the screen's hit rate stays unmeasured.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL or with MODAL BACOT live trading. Keep the three ledgers separate in every future note and letter.

## Already Covered in Main Chat

- User asked "Bacot degen kemana muse?" on 2026-11-06 ~23:29 WIB; main agent reported the 178-run / 9,032-pair evaluation (0 entries, sighting leg the terminal blocker) and proposed Variants A and B.
- User first said "Uji Varian A + B" then corrected to "varian A saja dulu" on 2026-11-06 ~23:41-23:42 WIB; main agent confirmed Variant A only, B not built.
- Main agent reported Variant A built, verified, and running on 2026-11-07 ~07:43 WIB (pre-filter working, non_v2 = 0, 0 entries in its first 3 runs, first comparison ~07:00 WIB 2026-11-08).
- Main agent reported Variant A Day One on 2026-11-08 17:10 WIB: pre-filter works (80 pools to 16), almost all survivors die at the holder check (~96%), both arms cash 0.010 BNB intact, 0 entries; head-to-head comparison still being prepared and to be delivered separately.
- Main agent reported paper status in the 2-hour recaps on 2026-11-07 and 2026-11-08 (08:20, 10:19, 12:19, 14:19, 16:19, 18:19 WIB): 0 trades, 0 positions, cash 0.010 BNB in both arms.
- What main chat has NOT yet heard: the head-to-head comparison itself; today's deadline worsening (main 68%, Variant A 46%); candidates now reaching the v2 gate and dying on v2_partial / v2_lp (20 main, 25 Variant A evaluations today vs 4 and 2 on 2026-11-07); sightings falling to 5 main / 7 Variant A; or the RELAY double-baseline closing as a negative.
- User set the daily 10% profit/loss benchmark and the BACOT SCALPING 5-round test in main chat; those belong to the live scalp work, not this paper goal.

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers and diagnostics are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-07/model-degen-paper-trading-mandiri.md (read in full): Variant A day 1, holder gate ~96% of survivors, holder stage latency bottleneck (~480 s Variant A), deadline hits main 32/77 and Variant A 13/45 as counted to ~19:11 WIB, RELAY double-baseline left open, head-to-head comparison scheduled ~07:00 WIB 2026-11-08. Today's note supersedes its funnel diagnosis (candidates now reach v2 and die on partial/LP) and closes the RELAY question.
- Prior study notes 2026-11-05 and 2026-11-06 (known from the 2026-11-07 note's trajectory and the repetition grep): 0 trades, control arm and forward-return ledger still missing.
- Prior brief workspace/goals/model-degen-paper-trading-mandiri/briefs/Variant A Day One (2026-11-07 12.28.06).html (listed, not re-read in full; its subject is the 2026-11-07 day-one result, and its own text states the head-to-head comparison is due 2026-11-08 ~07:00 WIB). Delivered to the user 2026-11-08T10:10:28Z per the goal record.
- Repetition search (grep over agent_notes/ and briefs/ for this goal, variants "Variant A", "Varian A", "holder gate", "deadline", "BACOT DEGEN", "paper trading", "head-to-head", "perbandingan"): the 2026-11-05, 2026-11-06 and 2026-11-07 notes matched on "BACOT DEGEN", "paper trading", "deadline" and "holder gate"; the 2026-11-07 note and the Variant A Day One brief matched on "Variant A" and "head-to-head" — but only as the day-one result and as a comparison still to come. No prior note or brief contains the 2026-11-08 deadline rates, the v2_gate/v2_partial/v2_lp counts, the sightings fall to 5/7, or the RELAY closing. Today's head-to-head comparison is new against everything the search returned.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active, current state "BACOT DEGEN v2 is active on a 15-minute cron, with the paper trial running to November 19."
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-09T12:02:54.709241576Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Main paper ledger workspace/paper-trading/ledger.json — cash 0.010 BNB, 0 positions, 0 trades, sightings 5, daily 2026-11-08 entries 0 (read 2026-11-08 ~19:02 WIB).
- Main run diagnostics workspace/paper-trading/run-diagnostics.jsonl — 321 runs total, 73 on 2026-11-08, 50 deadline hits, 0 entries; latest 2026-11-08 18:37:59 WIB, 80/80 pairs, 728.1 s, entries 0, sightings 5.
- Variant A ledger workspace/paper-trading/variant-a/ledger.json — cash 0.010 BNB, 0 positions, 0 trades, sightings 7, daily 2026-11-08 entries 0 (read 2026-11-08 ~19:02 WIB).
- Variant A run diagnostics workspace/paper-trading/variant-a/run-diagnostics.jsonl — 129 runs total, 68 on 2026-11-08, 31 deadline hits, 0 entries; latest 2026-11-08 18:56:31 WIB, raw 80 to 17 after pre-filter, 17/17 seen, 451.6 s, entries 0, sightings 7.
- Forward-return ledger workspace/paper-trading/forward-return-ledger.md — still empty (read 2026-11-08 ~19:02 WIB).
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window since 2026-11-07T12:02:53Z) — the saved fetch output was grepped for BACOT DEGEN / paper / Variant A mentions; the 2026-11-08 17:10 WIB Variant A Day One report and the 2-hour recaps' "0 trade, cash 0.01 BNB" lines are the only BACOT DEGEN items today, and none contains the head-to-head comparison, the deadline rates, or the v2-stage finding.
- Handoff from chunks 1-2 of this run: Variant A built + verified + running 2026-11-07 ~07:44 WIB, first comparison ~07:00 WIB 2026-11-08; main-model evaluation 178 runs / 9,032 pairs / 0 entries; BACOT SCALPING stopped 2026-11-06 then re-enabled 2026-11-07 with the STOCKMEMES round-1 loss; scalp test postponed 2026-11-08 07:01 WIB, score 0/2.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet.

### Searches skipped or unavailable

- No new web search was run: the trial's own ledgers/diagnostics are primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief file was listed and its closing paragraph quoted in the repetition grep, not re-read in full: its subject (2026-11-07 day one) is already summarised in the 2026-11-07 note, and re-reading the rendered HTML would not change the newness ruling.
