# Study Notes - 2026-11-09 - BACOT DEGEN
<!-- studying-run-start: 2026-11-09T12:12:49Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 to 2026-11-19. Variant A — the same gates with a clean-universe pre-filter (GeckoTerminal dex == pancakeswap_v2, quote token WBNB, reserve >= $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:46 WIB, by the user's correction to "varian A saja dulu".

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study is the day-5 check (2026-11-09, runs to 19:18 WIB): after five days with zero entries in either arm, is "0 entries" still a gates verdict, or has the measurement itself broken down? It does not confuse any of this with live BACOT SCALPING (real money; AGC round 4 bought 2026-11-09 12:44 WIB, 0.0048 WBNB, still holding) or with MODAL BACOT live trading — separate ledgers, separate money.

## What today's evidence shows

### Day 5, 2026-11-09 (runs to 19:18 WIB): still zero — and the deadline problem is now the story

Ledgers and diagnostics read 2026-11-09 ~19:12 WIB (run start). Both arms still at zero: cash 0.010 BNB, 0 positions, 0 trades, daily 2026-11-09 entries 0, exits 0, realized 0.0. Day 5 of the trial with no entry in either arm; cumulative main 410 runs, Variant A 202 runs, entries 0 everywhere.

- Main arm, 2026-11-09: 71 runs, **63 deadline hits (88.7%)**, average elapsed 810.8 s, average pairs seen **38.3 of 80**. Average stage seconds: pair_info 629.3, holder 541.3, quote 102.4, audit 41.6, chart 7.0.
- Variant A, 2026-11-09: 54 runs, **41 deadline hits (75.9%)**, average elapsed 737.8 s, average pairs seen **11.3 of ~18-19 surviving the pre-filter**. Average stage seconds: holder 502.2, pair_info 313.5, quote 117.5, audit 41.6, chart 4.7.
- Comparison: on 2026-11-08 the deadline rates were main 68% and Variant A 46% (partial day, 73 and 68 runs), with average pairs seen 59.4 and 14.7. Both rates got much worse today, and the coverage fell with them — main pairs seen 59.4 → 38.3, Variant A 14.7 → 11.3. The last runs of the day are the extreme case: main 19:18:20 WIB saw only 11 of 80 pairs, Variant A 19:18:16 WIB only 4 of 19, both after ~855 s, both deadline-hit, with the holder stage alone taking ~792-795 s.

### The v2 diagnosis reversed: almost nothing reaches the v2 gate today

This reverses the 2026-11-08 note's genuinely new finding, and that reversal is today's most important change.

- Main arm, 2026-11-09 reason totals: non_v2_revert 1,045, non_v2_id 358, dust 392, non_wbnb 267, holder_skip 273, holder_gate 269, audit_skip 240, sighting 68, **v2_gate 6, v2_partial 5, v2_lp 5**, v2_candle 1, v2_dev 1. Only 6 of 71 runs had any v2_gate evaluation.
- Main arm, 2026-11-08 for comparison: v2_gate 20 across 73 runs, in 20 runs.
- Variant A, 2026-11-09: holder_skip 253, holder_gate 252, audit_skip 197, dust 69, sighting 52, **v2_gate 8, v2_partial 8, v2_lp 8**, non_v2 0 (pre-filter still working). Only 8 of 54 runs had any v2_gate evaluation.
- Variant A, 2026-11-08 for comparison: v2_gate 25 across 68 runs, in 25 runs.
- Reading: yesterday the funnel's terminal blocker had moved one stage deeper — candidates reached v2 and died on v2_partial / v2_lp. Today it moved back out: candidates almost never reach v2 at all, because the deadline now truncates runs while the holder stage is still running (holder ~500-540 s on average, ~795 s in the last runs). The 2026-11-08 question — whether v2_partial is a data problem and whether v2_lp failures are real LP quality — is therefore unanswerable from today's data: there were only 6 and 8 v2 evaluations to learn from. Do not quote today's v2_partial / v2_lp counts as evidence about LP quality; they are evidence about truncation. The next fix is upstream of v2: the holder stage's latency, or the deadline itself, before any v2 conclusion can be trusted.

### Sightings: 7 in each arm, still no confirmation

- Main sightings: 7 (was 5 on 2026-11-08); Variant A sightings: 7 (was 7). Sighting reason-counts today: main 68, Variant A 52 — again, a high reason-count is not a growing watchlist; the ledger lists are flat.
- One sighting appears in both arms: BURN (0x7de1606230aa70802caecf1a3e90039a6265b1c4), first seen 2026-11-08 19:49 WIB (main) / 19:59 WIB (Variant A), holders 120 → 128, BNB reserve 57.22 → 57.52. This is a paper sighting only — BURN is also a live-scalp candidate in the user's other work, and the two must not be conflated: no entry was made here, and this sighting is not a buy signal.
- New main sightings first seen 2026-11-09: 0x7ab8d02cbb51ff7223fde700eaaa2a91bf750314 (07:43 WIB, 45 holders, 540.37 BNB reserve), 0xd7057e7c56b9c2d5f0a3e639d07610db31c949c8 (07:46 WIB, 255 holders, 810.66 BNB reserve), 0x55c69ee391094b7c4d9de0eedc04929f1bae7777 (09:07 WIB, 59 holders, 4.77 BNB reserve). None confirmed into an entry.

### What has not changed

- Still zero trades in both arms after five days of the trial (2026-11-05 to 2026-11-09): both cash balances 0.010 BNB intact.
- Forward-return ledger (workspace/paper-trading/forward-return-ledger.md, read 2026-11-09 ~19:12 WIB): still empty — no candidate has ever been recorded, so the screen's hit rate is still unmeasured.
- Control arm and hold benchmark (Quant-Lab "proven" gate, from the 2026-11-05 note): still not built. The trial still cannot distinguish a future win streak from luck.
- Trial end date unchanged (2026-11-19); 10 days remain. Daily 10% budget framing unchanged; separation from MODAL BACOT unchanged. BACOT SCALPING's real-money results stay in their own ledger and are not this goal's numbers.

## Prerequisite check

- Prerequisites in place: v2 engine running on the 15-minute cron (paper-trading-15m), Variant A running on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, pre-filter verified working in code and in diagnostics (non_v2 = 0 across all 54 Variant A runs today), trial window to 2026-11-19.
- Gap to close first (unchanged, now sharper): no control arm and no benchmark in the trial. Until a coin-flip control and a hold benchmark run beside the model, a future win streak cannot be distinguished from luck.
- Second gap (changed today — the bottleneck moved back upstream): the binding constraint is again the holder stage's latency plus the deadline, not the v2 gate. Before trusting "0 entries" as a gates verdict, the next study should check (i) whether the holder stage can be made faster or parallel (it averages ~502-541 s today and ~795 s in the last runs), (ii) whether the deadline budget itself needs revisiting, and (iii) only then re-ask whether v2_partial is a data gap or a real quality signal, once v2 evaluations are numerous enough to judge.
- Third gap (unchanged): the forward-return ledger is still empty; the first recorded candidate is still waiting.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if cash falls below 70% — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards.

## Worked example

Walk-through of one real Variant A evaluation: the 2026-11-09 19:18:16 WIB run (deadline hit).

1. Universe: 80 raw GeckoTerminal pools; pre-filter drops 61 (dex 49, quote 9, liq 3) to 19 to evaluate.
2. Shape filters: non_v2_id 0, non_v2_revert 0, dust 0 — the upstream leak is still gone in this arm.
3. Holder stage: 0 holder_skip + 0 holder_gate recorded — not because holders passed, but because the run died mid-stage; audit_skip 0 for the same reason.
4. V2 gate: v2_gate 0, v2_partial 0, v2_lp 0 — nothing reached v2 on this run.
5. Sighting leg: 4 sighting counts recorded; ledger sightings stand at 7.
6. Result: 0 entries, 0 positions, cash unchanged at 0.010 BNB; 852.5 s, deadline hit, only 4 of 19 pairs seen, holder stage 791.9 s.
7. What this shows: the pre-filter still works exactly as designed, but the run's verdict covers only 4 of 19 cleaned pairs. "No trade" here is a truncation artefact, not a gates verdict — and it is the opposite of the 2026-11-08 worked example, where a candidate reached v2 and died there.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/variant-a/ledger.json and state, in one sentence, the cash, the number of positions, and the number of sightings.
2. Open workspace/paper-trading/variant-a/run-diagnostics.jsonl, take the latest line, and state the raw universe, how many pairs survived the pre-filter, how many were seen, and whether the deadline was hit.
3. List the top two rejection reasons by count in that run, and say whether any v2_gate evaluation appears — and if so, what v2_partial and v2_lp say.
4. Compare the outcome to the main ledger (cash_bnb, positions, trades) and confirm both arms agree on entries = 0.
5. Feedback check: if entries = 0 and cash = 0.010 BNB in both arms, the correct conclusion is "deadline hits got much worse (main 88.7%, Variant A 75.9%), almost nothing reached v2 today, and the last runs saw only a handful of pairs — so 0 entries today is mostly unmeasured, not proven" — not "Variant A failed" and not "the model is proven safe."

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading the diagnostic reasons and stage timings instead of guessing why no entry happened), name the one most useful next adjustment (e.g. always check whether the run hit its deadline — and which stage ate the time — before concluding the full universe was evaluated, and never read v2_partial / v2_lp counts as LP evidence on a day when almost nothing reached v2), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to resume BACOT SCALPING (real money; AGC round 4 bought 2026-11-09, still holding) once funds return, and whether the paper model's gates should inform that decision. Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. BACOT DEGEN's lesson transfers directly: fixing the most visible leak (universe quality) does not fix the outcome if the next bottleneck (holder-stage latency, now the deadline itself) is the binding one — check where the funnel actually narrows before spending on the next fix.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, or forgetting the kill-switch) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will any of the 7 main-arm / 7 Variant A sightings confirm into the model's first entry before 2026-11-19, or will the trial end with zero trades? Either outcome needs interpreting: zero trades means the gates may be too strict — or, as today shows, the measurement may be too truncated — not that the model is "safe."
- Is the deadline worsening (main 68% → 88.7%, Variant A 46% → 75.9% in one day) a one-day spike or a trend — and is it holder-stage latency, RPC slowness, or universe growth?
- Once runs stop truncating, does the v2_partial / v2_lp pattern from 2026-11-08 return, or was that a one-day artefact too?
- Is the holder gate's kill rate (~96% of Variant A survivors on 2026-11-07) a real quality signal or a data problem — how much of holder_skip is RPC/timeout failure vs genuinely unreadable snapshots?
- When will the coin-flip control + hold benchmark be built (method-adoptions section 5d step 1)? Without it, the trial cannot meet its own "proven" gate.
- The forward-return ledger's first row: which candidate, and when? If no candidate is ever recorded, the screen's hit rate stays unmeasured.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL or with MODAL BACOT live trading. Keep the three ledgers separate in every future note and letter.

## Already Covered in Main Chat

- Main agent reported Variant A Day One on 2026-11-08 17:10 WIB: pre-filter works (80 pools to 16), almost all survivors die at the holder check (~96%), both arms cash 0.010 BNB intact, 0 entries; head-to-head comparison still being prepared and to be delivered separately.
- Main agent reported the BACOT DEGEN Head-to-Head brief on 2026-11-08 ~19:17 WIB (brief created 2026-11-08T12:21:53Z): deadline rates main 68% / Variant A 46% on 2026-11-08, candidates reaching v2 and dying on v2_partial / v2_lp (20 main, 25 Variant A).
- 2-hour recaps on 2026-11-09 (12:19, 14:19, 16:19, 18:19 WIB) reported paper trading only as "0 trade / 0 posisi, kas 0,01 BNB" in both arms, with no deadline rates, no v2 counts, and no funnel diagnosis.
- No main-chat message on 2026-11-09 contains today's deadline rates (main 88.7%, Variant A 75.9%), the v2 collapse to 6 and 8 evaluations, the pairs-seen fall (38.3 / 11.3), or the reversal of the 2026-11-08 v2 diagnosis.
- User set the daily 10% profit/loss benchmark and the BACOT SCALPING 5-round test in main chat; those belong to the live scalp work, not this paper goal.

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers and diagnostics are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-08/model-degen-paper-trading-mandiri.md (read in full): head-to-head 2026-11-08, deadline main 68% / Variant A 46%, candidates reaching v2 and dying on v2_partial / v2_lp (20 main, 25 Variant A), sightings 5 main / 7 Variant A, RELAY double-baseline closed as a negative. Today's note supersedes its funnel diagnosis (almost nothing reaches v2 today; truncation is again the binding constraint) and updates its deadline rates.
- Prior study notes 2026-11-05, 2026-11-06, 2026-11-07 (known from the 2026-11-08 note's trajectory): 0 trades, control arm and forward-return ledger still missing, holder gate ~96% of Variant A survivors.
- Prior briefs: BACOT DEGEN Head-to-Head (2026-11-08 12.17.08).html and Variant A Day One (2026-11-07 12.28.06).html (listed; subjects are the 2026-11-08 and 2026-11-07 results respectively, summarised in the 2026-11-07 and 2026-11-08 notes).
- Repetition search (grep over agent_notes/ and briefs/ for this goal, variants "deadline", "v2_gate", "v2_partial", "day 5", "zero trades", "0 entries", "pairs_seen", "BACOT DEGEN", "paper trading", "head-to-head"): the 2026-11-05 to 2026-11-08 notes matched on "deadline", "v2_gate", "v2_partial", "BACOT DEGEN" and "paper trading", and the Head-to-Head brief matched on "head-to-head" — but only with the 2026-11-08 rates and counts. No prior note or brief contains the 2026-11-09 deadline rates (88.7% / 75.9%), the v2 collapse (6 main, 8 Variant A), the pairs-seen averages (38.3 / 11.3), or the last-run truncation (11 and 4 pairs seen). Today's day-5 reversal is new against everything the search returned.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active, current state "BACOT DEGEN v2 is active on a 15-minute cron, with the paper trial running to November 19."
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-10T12:12:49.589956955Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Main paper ledger workspace/paper-trading/ledger.json — cash 0.010 BNB, 0 positions, 0 trades, sightings 7, daily 2026-11-09 entries 0 (read 2026-11-09 ~19:12 WIB).
- Main run diagnostics workspace/paper-trading/run-diagnostics.jsonl — 410 runs total, 71 on 2026-11-09, 63 deadline hits, 0 entries; latest 2026-11-09 19:18:20 WIB, 11/80 pairs, 857.0 s, entries 0, sightings 7.
- Variant A ledger workspace/paper-trading/variant-a/ledger.json — cash 0.010 BNB, 0 positions, 0 trades, sightings 7, daily 2026-11-09 entries 0 (read 2026-11-09 ~19:12 WIB).
- Variant A run diagnostics workspace/paper-trading/variant-a/run-diagnostics.jsonl — 202 runs total, 54 on 2026-11-09, 41 deadline hits, 0 entries; latest 2026-11-09 19:18:16 WIB, raw 80 to 19 after pre-filter, 4/19 seen, 852.5 s, entries 0, sightings 7.
- Forward-return ledger workspace/paper-trading/forward-return-ledger.md — still empty (read 2026-11-09 ~19:12 WIB).
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window since 2026-11-08T12:02:53Z) — the 2026-11-09 2-hour recaps' "0 trade, cash 0.01 BNB" lines are the only BACOT DEGEN items today, and none contains the deadline rates, the v2 collapse, or the funnel reversal; the 2026-11-08 Head-to-Head brief is the last delivered comparison.
- Handoff from chunks 1-2 of this run: Variant A built + verified + running 2026-11-07 ~07:44 WIB; main-model evaluation 178 runs / 9,032 pairs / 0 entries; BACOT SCALPING postponed 2026-11-08 07:01 WIB, score 0/2, then AGC round 4 bought 2026-11-09 12:44 WIB.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet.

### Searches skipped or unavailable

- No new web search was run: the trial's own ledgers/diagnostics are primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief files were listed and their subjects summarised from the prior notes, not re-read in full: their subjects (2026-11-07 day one, 2026-11-08 head-to-head) are already summarised in the 2026-11-07 and 2026-11-08 notes, and re-reading the rendered HTML would not change the newness ruling.
