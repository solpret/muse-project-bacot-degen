# Study Notes - 2026-11-05 - BACOT DEGEN
<!-- studying-run-start: 2026-11-05T12:08:10.698244+00:00 -->

## Goal in one line

BACOT DEGEN (`goal_b9d1c43a21e5`, slug `model-degen-paper-trading-mandiri`) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 → 2026-11-19 (extended 2026-11-05 ~08:12 WIB after the Ankr pagination fix was verified).

## Study focus today

Learning state: review_due, teach mode, novice band, mastery not yet estimated. The plan's retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study therefore checks (a) what the v2 paper trial has actually produced since restart, and (b) what today's five newly adopted validation methods change about how the model should be judged — without confusing either with the live BACOT SCALPING work (AGC/BURN), which is a different, real-money activity.

## What today's evidence shows

### Paper trial status: still zero trades, cash intact

- Ledger (`~/workspace/paper-trading/ledger.json`, read 2026-11-05 ~19:08 WIB): started 2026-11-05T00:21:01+07:00, ends 2026-11-19T00:21:01+07:00, virtual capital 0.010 BNB, cash 0.010 BNB, positions `[]`, trades `[]`, daily 2026-11-05 realized 0.0, entries 0, exits 0, sightings `{}`.
- Latest diagnostics (`run-diagnostics.jsonl`, 43 runs total): run 2026-11-05 19:04:49 WIB — 40/40 pairs seen, 530.1 s, no deadline hit, entries 0, sightings 0, open positions 0. The two runs before it (18:21, 18:37 WIB) are identical in outcome: 40/40 pairs, 0 entries, 0 sightings. Rejection reasons in the 19:04 run: non-v2-id 12, non-v2-revert 16, non-WBNB 5, dust 1, holder skip 4, chart skip 1, v2 gate 1.
- Interpretation: v2 fail-closed gates are doing what they were built to do — nothing passes, so nothing is entered. That is the model behaving correctly under its own rules, not a failure to run. But it is also the core open problem: after a full day of v2 runs (00:40 → 19:04 WIB), the model has produced zero observations of its own entry/exit behaviour. Mastery stays unestimated (fewer than three observed performances — in fact zero).
- The 18:19 WIB 2-hour recap already told the user the same status (0 trades, cash 0.01 BNB), and the 12:55 and 09:40 WIB run notes in memory record the same pattern. No new trial outcome exists today.

### Five validation methods adopted today (2026-11-05 ~18:42 WIB, user: "semua saja")

All five were adopted as read-only, keyless, no-execution complements. None changed a live gate, sizing, schedule, or execution scope. Full record in `~/workspace/method-adoptions-2026-11-05.md` §5a–§5e.

1. **DeFade** (defade.org) — bundle & funding-origin forensics; red-flag score 0–100 across 35 on-chain modules, with kill-switch floors and honest degradation. **Correction found by live test 2026-11-05 ~19:13 WIB: the free tier requires sign-in** (email magic link or wallet connect); the "free without login" claim from the FAQ was wrong in practice. No scores exist for AGC or Grok Bot because the test stopped at the sign-in gate without logging in. Method adopted as a lens only; live scans need the user to log in himself in the live browser.
2. **BscHouse** (bschousesignal.com) — three new screening lenses: (a) deployer track record used positively (a deployer with 3× 10x+ and no rugs has a materially higher base rate — the reverse of the existing same-owner discard, which only uses deployer negatively); (b) top-10 holder band in the first 5 minutes (<25% healthy, 25–40% risky, >40% trap) plus funding-timing bundle heuristics; (c) LP/market-cap ratio (healthy 2–5%, <1% practically unexitable) — an exitability lens distinct from the absolute liquidity floor and the vol/liq ratio the model already uses.
3. **PolyRob Treasury Trading** (MIT) — skill installed at `~/workspace/custom-skills/treasury-trading/SKILL.md` (method only; `defi_trade`/`defi_data` verbs declared not applicable here). Adopted: two screens only (honeypot = hard reject; sell tax >~10% = reject), ledger-reconcile discipline, anti-dust rule (relevant — the wallet receives a lot of dust). Note the deliberate tension: this skill drops establishment filters (mintable/hidden-owner) for super-early coins, which conflicts with this model's fail-closed gates; the model's gates win here, the skill is calibration only.
4. **Quant-Lab** — validation methodology (bake-off with control), not a strategy. Five traps to avoid (overfitting, multiple-testing, free fills, survivorship bias, shrinking published edges); design: 5 strategies + coin-flip control + hold benchmark, bootstrap CI + permutation test; "proven" gate: 100+ closed trades, 30+ days, profit, profit even with costs doubled, 95% CI per-trade return above zero, beats the control after multiple-testing correction, max drawdown <40%. A 5-step application plan to BACOT DEGEN paper (add coin-flip control + hold benchmark) and to BACOT SCALPING (bake-off before any extra funds) is recorded — **planned, not yet executed**.
5. **Solana Screener forward-return ledger** — every screened candidate recorded with forward returns at 1h/6h/24h/7d horizons; dead tokens recorded as −100%, never discarded (anti-survivorship); horizon cells write-once and time-gated. Ledger created at `~/workspace/paper-trading/forward-return-ledger.md` — **empty, ready to fill**. Tier B recorded as a silent control group.

### What changes how Muse should understand this goal

- The model's validation question has sharpened: the trial no longer tests only "does v2 pick winners" but "does v2 beat a coin-flip control and a hold benchmark, with costs doubled, over 100+ trades" (Quant-Lab gate). The current trial design (single model, no control, no benchmark, 0 trades so far) cannot answer that yet.
- The forward-return ledger gives the model its first honest scoreboard — but it is empty, and it only becomes useful if candidates are actually recorded when screened, including the ones that die.
- DeFade closes the biggest known hole (bundle forensics) in principle, but in practice it is login-gated, so it is not yet an operating input. Do not cite DeFade scores for any token — none exist.
- The BscHouse deployer lens is the first positive use of deployer history in this project; previously deployer was only a discard signal. It is a lens, not a gate, and needs its own base-rate measurement before it can promote anything.
- Nothing today changes the trial's end date (2026-11-19), the daily 10% budget framing, or the separation from MODAL BACOT. The 2026-11-05 ~07:03 WIB live MODAL BACOT re-enable does not touch this goal.

## Prerequisite check

- Prerequisites in place: v2 engine running on the 15-minute cron (paper-trading-15m), ledger clean (0.010 BNB, 0 positions), Ankr pagination fix verified (40/40 pairs, no 900 s kill), trial window to 2026-11-19.
- Gap to close first: **no control arm and no benchmark** in the trial. Until a coin-flip control and a hold benchmark run beside the model, a future win streak cannot be distinguished from luck. This is the first thing to close before the trial's verdict is trusted — it is recorded as a plan (method-adoptions §5d step 1), not yet built.
- Second gap: the forward-return ledger is empty; the next screened candidate that passes any screen should be its first row, or the ledger stays a good intention.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — ≥12 candles, complete holder snapshot with ≥50 holders, identified dev, LP burn ≥50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if cash falls below 70% — and that is judged only at the end of the trial (2026-11-19), not trade by trade.

## Worked example

Walk-through of one real v2 evaluation: the 2026-11-05 19:04 WIB run.

1. **Universe:** 40 new GeckoTerminal pools, all seen (40/40), 530.1 s, no deadline hit.
2. **Shape filters first:** 12 pools were not v2-shaped IDs, 16 reverted on the v2 check, 5 were non-WBNB pairs, 1 was dust — 34 of 40 removed before any judgement about quality.
3. **Holder gate:** 4 more skipped (snapshot partial or too few holders — the exact fail-closed behaviour that v1 lacked, where an empty snapshot read as a pass).
4. **Chart gate:** 1 skipped (fewer than 12 candles).
5. **v2 gate:** 1 more failed the combined v2 gate.
6. **Result:** 0 sightings recorded, 0 entries, 0 positions, cash unchanged at 0.010 BNB.
7. **What this shows:** the model can process a full universe cleanly and still enter nothing. In v1 the same day would very likely have produced entries from vacuous passes (cycle 1 lost 75% of virtual capital in 17 minutes on 3 entries). The worked example's lesson is that "no trade" is a valid, intended output of a fail-closed model — but it also means the trial is currently collecting zero evidence about entry quality, which is why the Quant-Lab control arm matters.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open `~/workspace/paper-trading/run-diagnostics.jsonl` and take the latest line. State, in one sentence, how many pairs were seen and how many entries were made.
2. List the top two rejection reasons by count in that run.
3. State whether the run hit its deadline, and what that implies about data completeness.
4. Compare the outcome to the ledger (`cash_bnb`, `positions`, `trades`) and confirm they agree.
5. Feedback check: if entries = 0 and cash = 0.010 BNB, the correct conclusion is "model ran, gates held, no evidence about entries yet" — not "model is broken" and not "model is proven safe."

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading the diagnostic reasons instead of guessing why no entry happened), name the one most useful next adjustment (e.g. always cross-check the diagnostic line against the ledger before concluding anything about the trial), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is about to decide whether to add funds to BACOT SCALPING (AGC/BURN, real money, currently 2 wins / 6 rounds, below the 40% bar). Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round.

## Confidence check

Ask the user to rate confidence (1–10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting the 2-sighting rule or the kill-switch) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will the v2 model record its first sighting/entry before 2026-11-19, or will the trial end with zero trades? Either outcome needs interpreting: zero trades means the gates may be too strict for the current market, not that the model is "safe."
- When will the coin-flip control + hold benchmark be built (method-adoptions §5d step 1)? Without it, the trial cannot meet its own "proven" gate.
- Will the user log in to DeFade himself (email magic link, no card, no wallet connect) so bundle scores can be produced, or should DeFade stay a method note only? The main agent already asked this in chat (2026-11-05 19:14 WIB); do not re-ask unprompted.
- The forward-return ledger's first row: which candidate, and when? If no candidate is ever recorded, the screen's hit rate stays unmeasured.
- Ledger `ends_at` is now 2026-11-19 in `ledger.json` — the earlier inconsistency (GOAL.md said 2026-11-19 while ledger said 2026-11-12) is resolved in the file read today.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL (−0.0015283649 BNB cumulative, 2/6 wins) or with MODAL BACOT live trading. Keep the three ledgers separate in every future note and letter.

## Already Covered in Main Chat

- User ordered the memecoin-method research and then "semua saja" (adopt all five) on 2026-11-05 ~18:35–18:41 WIB; main agent reported all five adoptions at 18:46 WIB.
- Main agent reported the DeFade live-test outcome (sign-in required, no scores for AGC/Grok Bot, user login needed to proceed) at 2026-11-05 19:14 WIB.
- Main agent reported BACOT DEGEN paper status in the 18:19 WIB 2-hour recap (0 trades today, cash 0.01 BNB) and in earlier recaps; user was told the v2 restart, gates, and trial extension (to 2026-11-19) on 2026-11-05 ~00:34–08:12 WIB.
- User set the daily 10% profit/loss benchmark and the BACOT SCALPING 5-round test (win rate ≥40% to continue) in main chat; those belong to the live scalp work, not this paper goal.
- No prior study note or brief exists for this goal (agent_notes/ and briefs/ are empty as of this run).

## Research Trajectory

### External sources viewed

- Method adoptions file 2026-11-05, `~/workspace/method-adoptions-2026-11-05.md` §5a–§5e — the five adoptions (DeFade, BscHouse, PolyRob Treasury Trading, Quant-Lab, Solana Screener forward-return ledger) and the DeFade sign-in correction, read in full on 2026-11-05.
- DeFade FAQ and whitepaper, https://defade.org/faq and https://defade.org/whitepaper — bundle/forensics method, 3 free scans/day, read via the method-adoptions record; live test found sign-in required, so no scores were produced.
- BscHouse, "How to Find BSC Gems Early", https://bschousesignal.com/how-to-find-bsc-gems.html — three screening lenses (deployer track record, top-10 holder band, LP/market-cap ratio).
- PolyRob Treasury Trading skill, https://github.com/jackutery/polyrob/blob/HEAD/data/prompts/skills/treasury-trading/SKILL.md — two-screen doctrine, ledger-reconcile, anti-dust; installed locally as method only.
- Quant-Lab, https://github.com/Stolls32/quant-lab (RESEARCH.md) — bake-off with coin-flip control, bootstrap CI, "proven" gate; methodology adopted, repo not installed.
- Solana Screener, https://github.com/yousefjan2007-crypto/solana_screener/blob/HEAD/CLAUDE.md — forward-return ledger method, anti-survivorship; method adopted, repo not installed.

### Prior trajectories reviewed

- No prior study notes or briefs exist for this goal: `workspace/goals/model-degen-paper-trading-mandiri/agent_notes/` and `.../briefs/` are both empty (listed 2026-11-05 ~19:08 WIB). Repetition search over both directories for variants "BACOT DEGEN", "paper trading", "paper-trading", "model degen", "forward-return", "Quant-Lab", "DeFade", "BscHouse" returned no hits (grep exit 1).
- Prior trajectory carried in the run handoff (chunks 1–3): v1 cycle-1 wipeout (−0.007505 BNB, 3 entries stopped in 17 minutes), reset + v2 restart 2026-11-05 ~00:34 WIB, Ankr pagination fix verified 08:08 WIB (40/40 pairs, 14,240 AGC logs, non-partial), trial extended to 2026-11-19.

### Scaffolds and support tactics

- Goal record via `user_goal.get` (goal_b9d1c43a21e5): category money, exploratory, active, current state "BACOT DEGEN v2 is active on a 15-minute cron, with the paper trial running to November 19."; GOAL.md read in full (separation from MODAL BACOT, v2 gates, restart verification).
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-06T12:08:11Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Paper-trading ledger `~/workspace/paper-trading/ledger.json` — cash 0.010 BNB, 0 positions, 0 trades, ends 2026-11-19 (read 2026-11-05 ~19:08 WIB).
- Run diagnostics `~/workspace/paper-trading/run-diagnostics.jsonl` — 43 runs; latest 2026-11-05 19:04:49 WIB, 40/40 pairs, 0 entries, 0 sightings.
- Forward-return ledger `~/workspace/paper-trading/forward-return-ledger.md` — created, empty table, ready to fill.
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- `muse.memory_search` ("BACOT DEGEN paper trading v2", "BACOT DEGEN trial paper trading", "paper trading DEGEN gates") — v1 wipeout and reset, standalone split 2026-11-05 ~00:27 WIB, v2 gates, trial extension to 2026-11-19, per-gate diagnostic log + 750 s soft limit fix in progress, run notes 09:25/09:40/12:55 WIB (all 0 trades).
- Recent main-chat conversation via `muse.context_fetch` (conversation, window since 2026-11-04T12:02:53Z) — the five adoptions, the DeFade correction, and the paper-trial status were all already reported to the user in main chat (see Already Covered in Main Chat). The saved fetch output (`/tmp/jarvis-tool-output-jYTd1A.txt`) was grepped to confirm the DeFade follow-up message at 2026-11-05T12:14:10Z.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet.

### Searches skipped or unavailable

- No new web search was run: the five methods' sources were already read and recorded in the method-adoptions file today, and the trial's own ledger/diagnostics are primary evidence. A fresh search would not change this note's findings.
- No prior-brief reading was possible: no briefs exist for this goal.
