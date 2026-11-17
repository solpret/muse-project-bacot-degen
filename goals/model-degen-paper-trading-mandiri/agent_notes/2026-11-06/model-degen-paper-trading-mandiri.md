# Study Notes - 2026-11-06 - BACOT DEGEN
<!-- studying-run-start: 2026-11-06T12:02:55Z -->

## Goal in one line

BACOT DEGEN (`goal_b9d1c43a21e5`, slug `model-degen-paper-trading-mandiri`) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 → 2026-11-19.

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The plan's retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study therefore checks (a) whether the P-1 sighting fix applied on 2026-11-06 actually produced the model's first sightings, (b) whether the trial has produced its first entry yet, and (c) whether the deadline problem the P-2/P-3 fixes were meant to solve is actually gone — without confusing any of this with the live BACOT SCALPING work (AGC/BURN, real money, stopped by the user on 2026-11-06 ~09:08 WIB), which is a different activity.

## What today's evidence shows

### Paper trial status: still zero trades, cash intact — but the sighting leg is alive for the first time

- Ledger (`~/workspace/paper-trading/ledger.json`, read 2026-11-06 ~19:02 WIB): started 2026-11-05T00:21:01+07:00, ends 2026-11-19T00:21:01+07:00, virtual capital 0.010 BNB, cash 0.010 BNB, positions `[]`, trades `[]`, daily 2026-11-06 realized 0.0, entries 0, exits 0.
- Diagnostics (`run-diagnostics.jsonl`, 135 runs total; 75 runs on 2026-11-06): entries sum 0 across all of today's runs. Latest run 2026-11-06 19:02:36 WIB — 77/80 pairs seen, 401.1 s, no deadline hit, entries 0, sightings total 8, open positions 0.
- The change since the 2026-11-05 note (which recorded `sightings: {}` and 0 sightings in every run): the ledger now holds **8 first-sighting baselines**, all recorded on 2026-11-06 after the P-1 fix moved the sighting check before the v2 data gates (visible in `paper_run.py`: "The sighting check runs BEFORE the v2 data gates (fix 2026-11-06)"). First two: `0xba30…7777`, 410 holders, BNB reserve 212.70, first seen 2026-11-06 07:07:09 WIB; `0x7ab8…314`, 53 holders, reserve 527.07, first seen 07:20:31 WIB. Six more followed between 08:04 and 11:12 WIB. This is the first time the two-sighting confirmation leg has recorded anything at all — in the 2026-11-05 note it was dead code, because v2 gates killed every candidate before a baseline could be recorded.
- No sighting has yet confirmed into an entry: the nearest miss reported to the user on 2026-11-06 08:14 WIB was holder growth +9% against the +10% requirement. A memory run note from 07:40 WIB records another sighting (`0x63dea5…`) at holders +0% (needs +10%) and reserve +4% (needs +5%). So the confirmation leg is now observing growth, but nothing has cleared both thresholds on a second sighting.

### The deadline problem is not gone

- The verification run cited to the user on 2026-11-06 08:14 WIB ran 576.7 s with 78/80 pools seen and no deadline hit. But later runs still hit the 750 s soft deadline: 17:58:44 WIB (43/80 seen, deadline hit) and 18:38:47 WIB (43/80 seen, deadline hit) — 2 of the last 6 runs. The universe is now 80 pools per run (was 40 on 2026-11-05), so each run has roughly twice the work, and the P-2 fast-path revert fix plus P-3 per-stage timing diagnostics have not eliminated the truncation. Consequence: on deadline-hit runs, roughly half the universe is never evaluated, and any sighting baselines in the unseen half are missed for that run. This was not reported to the user in main chat today; it is a standing infra caveat, not a new failure mode.
- Rejection pattern in the latest run (19:02 WIB): non-v2-id 10, non-v2-revert 18, dust 19, holder_gate 2, sighting 4 — the same shape as yesterday, with dust now the largest single bucket at 80-pool universe size.

### What has not changed

- Forward-return ledger (`~/workspace/paper-trading/forward-return-ledger.md`, read 2026-11-06 ~19:02 WIB): still empty — no candidate has ever been recorded, so the screen's hit rate is still unmeasured.
- Control arm and hold benchmark (Quant-Lab "proven" gate, from the 2026-11-05 note): still not built. The trial still cannot distinguish a future win streak from luck.
- Trial end date unchanged (2026-11-19); daily 10% budget framing unchanged; separation from MODAL BACOT unchanged. BACOT SCALPING's real-money PnL (−0.0015283649 BNB cumulative, 2/6 wins) and the live MODAL BACOT feed are separate ledgers — do not mix them into this goal's numbers.

## Prerequisite check

- Prerequisites in place: v2 engine running on the 15-minute cron (paper-trading-15m), ledger clean (0.010 BNB, 0 positions), P-1 sighting fix verified in code and in the ledger (8 baselines), trial window to 2026-11-19.
- Gap to close first (unchanged from 2026-11-05): **no control arm and no benchmark** in the trial. Until a coin-flip control and a hold benchmark run beside the model, a future win streak cannot be distinguished from luck.
- Second gap (new today): **deadline truncation at 80-pool universe size** — 2 of the last 6 runs saw only 43/80 pairs. Before trusting "0 entries" as a gates verdict, the next study should check whether the unseen half ever contained a would-be sighting. The P-3 per-stage timings exist now, so the fix can be targeted (slowest stage in the 17:18 run was pair_info at 792.5 s of stage time).
- Third gap (unchanged): the forward-return ledger is still empty; the first recorded candidate is still waiting.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — ≥12 candles, complete holder snapshot with ≥50 holders, identified dev, LP burn ≥50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if cash falls below 70% — and that is judged only at the end of the trial (2026-11-19), not trade by trade.

## Worked example

Walk-through of one real v2 evaluation: the 2026-11-06 19:02:36 WIB run.

1. **Universe:** 80 new GeckoTerminal pools; 77 seen, 401.1 s, no deadline hit.
2. **Shape filters first:** 10 pools were not v2-shaped IDs, 18 reverted on the v2 check, 4 were non-WBNB pairs, 19 were dust — 51 of 77 removed before any judgement about quality.
3. **Holder gate:** 2 more failed the holder gate; 6 skipped on holder snapshot in the 17:18 run — the fail-closed behaviour that v1 lacked.
4. **Sighting leg (now alive):** 4 pools recorded as first sightings or pending confirmations in this run; the ledger's sighting total stands at 8.
5. **Result:** 0 entries, 0 positions, cash unchanged at 0.010 BNB.
6. **What this shows:** the model now records baselines instead of discarding everything before the confirmation leg can see it — the P-1 fix works as intended. But "no trade" is still the only output, and on deadline-hit runs (17:58, 18:38 WIB) the model only saw 43/80 pools, so "no trade" on those runs is a partial-universe verdict, not a full one.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open `~/workspace/paper-trading/ledger.json` and state, in one sentence, the cash, the number of positions, and the number of sightings.
2. Open `~/workspace/paper-trading/run-diagnostics.jsonl`, take the latest line, and state how many pairs were seen out of the universe and whether the deadline was hit.
3. List the top two rejection reasons by count in that run.
4. Compare the outcome to the ledger (`cash_bnb`, `positions`, `trades`) and confirm they agree.
5. Feedback check: if entries = 0 and cash = 0.010 BNB, the correct conclusion is "model ran, gates held, sightings now being recorded, no evidence about entries yet" — not "model is broken" and not "model is proven safe."

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading the diagnostic reasons instead of guessing why no entry happened), name the one most useful next adjustment (e.g. always check whether the run hit its deadline before concluding the full universe was evaluated), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is about to decide whether to add funds to BACOT SCALPING (AGC/BURN, real money, currently 2 wins / 6 rounds, below the 40% bar, and stopped by the user on 2026-11-06). Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round.

## Confidence check

Ask the user to rate confidence (1–10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that the sighting check now runs before the v2 gates, or forgetting the kill-switch) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will any of the 8 recorded sightings confirm into the model's first entry before 2026-11-19, or will the trial end with zero trades? Either outcome needs interpreting: zero trades means the gates may be too strict for the current market, not that the model is "safe."
- When will the coin-flip control + hold benchmark be built (method-adoptions §5d step 1)? Without it, the trial cannot meet its own "proven" gate.
- Will the deadline truncation at 80 pools be fixed (slowest stage: pair_info), or will roughly half the universe keep going unevaluated on some runs?
- The forward-return ledger's first row: which candidate, and when? If no candidate is ever recorded, the screen's hit rate stays unmeasured.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL or with MODAL BACOT live trading. Keep the three ledgers separate in every future note and letter.

## Already Covered in Main Chat

- User delegated full gate-fix authority on 2026-11-06 ~07:48 WIB ("Perbaiki semuanya, saya serahkan keputusan itu padamu sepenuhnya"), and the main agent reported the gate evaluation plus the L-1/L-2/L-3 and P-1/P-2/P-3 fixes at 07:24 and 08:14 WIB.
- Main agent reported the paper verification run at 08:14 WIB (576.7 s, 78/80 pools, sighting 5, near-miss holder +9% vs +10% needed).
- Main agent reported paper status in the 2-hour recaps at 16:19 and 18:19 WIB (0 trades, 0 positions, cash 0.01 BNB, second day of the trial).
- User set the daily 10% profit/loss benchmark and the BACOT SCALPING 5-round test in main chat; those belong to the live scalp work, not this paper goal.
- No prior brief exists for this goal (briefs/ is empty as of this run).

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledger and diagnostics are the primary evidence, and the 2026-11-05 method sources were already read and recorded in the prior note.

### Prior trajectories reviewed

- Prior study note `workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-05/model-degen-paper-trading-mandiri.md` (read in full): 0 trades, 0 sightings, 43 runs, 40/40 pairs, five validation methods adopted, control arm and forward-return ledger still missing. Today's note re-confirms its trial-status finding and supersedes its "sighting leg is dead code" observation with the P-1 fix evidence.
- Repetition search (grep over `agent_notes/` and `briefs/` for this goal, variants "BACOT DEGEN", "paper trading", "paper-trading", "sighting", "gate fix", "near-miss", "holder +9%"): only the 2026-11-05 note matched; `briefs/` is empty (no brief files exist for this goal). The sighting-alive finding is new against the prior note, but it was already reported to the user in main chat on 2026-11-06 08:14 WIB, so it does not earn a new Letter.

### Scaffolds and support tactics

- Goal record via `user_goal.get` (goal_b9d1c43a21e5): category money, exploratory, active, current state "BACOT DEGEN v2 is active on a 15-minute cron, with the paper trial running to November 19."
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-07T12:02:55.737166419Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Paper-trading ledger `~/workspace/paper-trading/ledger.json` — cash 0.010 BNB, 0 positions, 0 trades, 8 sightings (first 07:07:09 WIB 2026-11-06), ends 2026-11-19 (read 2026-11-06 ~19:02 WIB).
- Run diagnostics `~/workspace/paper-trading/run-diagnostics.jsonl` — 135 runs total, 75 on 2026-11-06, 0 entries; latest 2026-11-06 19:02:36 WIB, 77/80 pairs, 401.1 s, no deadline; deadline hit 17:58:44 and 18:38:47 WIB (43/80 seen each).
- Forward-return ledger `~/workspace/paper-trading/forward-return-ledger.md` — still empty (read 2026-11-06 ~19:02 WIB).
- `paper_run.py` — P-1 fix comment verified in the file header (sighting check before v2 data gates, dated 2026-11-06); universe now 80 pools per run.
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- `muse.memory_search` ("BACOT DEGEN paper trading v2 sighting", "BACOT DEGEN trial zero trades") — v1 wipeout and reset, standalone split 2026-11-05, v2 gates, trial extension to 2026-11-19, run notes 2026-11-06 04:08 WIB (0 entry/0 sighting, deadline pattern) and 07:40 WIB (sighting 0x63dea5… holders +0%, reserve +4%).
- Recent main-chat conversation via `muse.context_fetch` (conversation, window since 2026-11-05T12:02:53Z) — the gate evaluation, the P-1/P-2/P-3 fixes, the verification run, the near-miss, and the paper status were all already reported to the user in main chat (see Already Covered in Main Chat). The saved fetch output (`/tmp/jarvis-tool-output-Ibi9xo.txt`) was grepped for BACOT DEGEN / paper mentions.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet.

### Searches skipped or unavailable

- No new web search was run: the trial's own ledger/diagnostics are primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- No prior-brief reading was possible: no briefs exist for this goal.
