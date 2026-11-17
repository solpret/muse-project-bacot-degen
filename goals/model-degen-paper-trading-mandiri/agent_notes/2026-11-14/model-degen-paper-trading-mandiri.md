# Study Notes - 2026-11-14 - BACOT DEGEN
<!-- studying-run-start: 2026-11-14T12:08:43Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only, no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. On 2026-11-14 ~18:15 WIB the user ordered ALL trading (MODAL BACOT live, BACOT DEGEN paper, scalping) moved from BSC to Solana — so the BSC trial ended early that evening and a new Solana paper trial began the same day. This note records the BSC trial's final state and the Solana paper trial's first day.

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study is the day-10 check (2026-11-14, evidence window 2026-11-13T12:24:29Z to 2026-11-14T12:08:43Z, run start 19:08 WIB) — and the day the goal itself changed chains. Two things to get right: (1) close the BSC trial honestly with final numbers, including its worst coverage day, without letting the chain move rewrite what the BSC trial showed; (2) record the Solana paper trial's starting conditions, its first two dry runs, and the infrastructure/backtest verdict exactly as measured, including the parts that did NOT prove out. Do not confuse any of this with live BACOT SCALPING (real money; 0 wins / 4 losses, cumulative −0.00286388 WBNB) or with MODAL BACOT live trading — separate ledgers, separate money. All figures below are PAPER/VIRTUAL unless stated otherwise.

## What today's evidence shows

### 1. The BSC trial ended early by user order, not by its own verdict

At ~18:15 WIB on 2026-11-14 the user ordered all trading moved BSC → Solana (message:00129de7-6e10-497a-8551-a0eaf00ac0ba in main chat). The BSC paper crons were disabled (not deleted): paper-trading-15m and paper-trading-variant-a-15m, alongside the MODAL BACOT live and scalping jobs. The last BSC runs were main 18:11:07 WIB and Variant A 18:15:16 WIB. The ledgers were read directly in this run and did not move on the final day:

- Main model: cash 0.011071790886431537 BNB virtual, 0 open positions, daily 2026-11-14 realized 0, entries 0, exits 0. Cash identical to 2026-11-11, 2026-11-12, and 2026-11-13.
- Variant A: cash 0.010724160078509572 BNB virtual, 0 open positions, daily 2026-11-14 realized 0, entries 0, exits 0. Cash identical to the same three days.
- Final BSC record over 10 days (2026-11-05 to 2026-11-14): 8 zero days (05, 06, 07, 08, 11, 12, 13, 14 Nov), 1 entry day (09 Nov), 1 winning day (10 Nov, GANG only). One token ever traded, in both arms. Main +10.7% vs starting 0.010 BNB virtual; Variant A +7.2% — entirely from GANG on 10 Nov (main: trailing exit −0.00003 BNB then TP +30% +0.0011019 BNB; Variant A: trailing +0.000118, stop −0.000472, TP +0.001078 BNB).
- Caution: the ledger files still carry `ends_at` 2026-11-19. That field was not rewritten; the operative end is the cron disable at ~18:15 WIB on 2026-11-14, not the file field. Do not quote 19 Nov as the trial end for the BSC arm.
- The trial therefore never reached its planned verdict date, and its planned question — does the model beat a control over a full trial — was never answered on BSC. The 2026-11-13 note's warning stands: a single-token trial cannot prove a model, and this one closed at two-thirds of its planned length with the same single token.

### 2. The final BSC day had the worst deadline rates of the trial — recorded, not explained away

Diagnostics read directly in this run (`workspace/paper-trading/run-diagnostics.jsonl` and `workspace/paper-trading/variant-a/run-diagnostics.jsonl`, parsed by run timestamp, not by substring):

- Main model, 2026-11-14: 71 runs, deadline hit in 58 (81.7%), pairs seen mean 52.1, entries 0. Previous days: 38% (11 Nov), 61.3% (12 Nov), 53.2% (13 Nov).
- Variant A, 2026-11-14: 66 runs, deadline hit in 28 (42.4%), pairs seen mean 14.7, entries 0. Previous days: 23% (11 Nov), 29.6% (12 Nov), 14.5% (13 Nov).
- The four-day sequences now read main 38 → 61.3 → 53.2 → 81.7 and Variant A 23 → 29.6 → 14.5 → 42.4. Both arms worsened sharply on the final day, and the arms still did not move together across the four days. The 2026-11-12 note's open question — artefact or new floor — is answered as: neither a stable floor nor a single shared cause; the rate is unstable day to day in both directions, and the final day is the worst observed, not a representative one.
- No cause is assigned in this note. The same day's main chat records repeated live-feed stalls and egress flapping (feed last wrote 14:15:47 WIB, ~2 h stale by the 16:19 WIB recap; Binance trending sources failing in repeated episodes), which is consistent with a bad-network day, but the diagnostics alone do not prove the network caused the deadline hits. The practical consequence is the same as the 2026-11-13 note's: on a day the main model saw 52.1 pairs on average, "nothing qualified" is a verdict on a partially seen market.
- The v2-gate pattern did not change on the final day: 0 entries in both arms, and the 2026-11-13 note's zero-v2-kill streak is not contradicted by anything read today (no 14 Nov kill breakdown was computed in this run beyond entries 0 — do not claim a 14 Nov kill count without reading it).

### 3. The Solana paper trial started the same evening: 0.08 SOL virtual, two zero-entry runs

The replacement engine (`workspace/solana-trading/paper_run_solana.py`, header: "Pengganti mesin BSC sesudah perintah user 14 Nov 2026 ~18:15 WIB") was built, dry-run, and scheduled the same evening. Ledger read directly in this run (`workspace/solana-trading/ledger.json`):

- Started 2026-11-14T18:20:20+07:00, ends 2026-11-21T18:20:20+07:00, chain Solana, virtual capital 0.08 SOL (~$6.07 at SOL $75.86 at start), cash 0.08 SOL, 0 positions, 0 trades, daily 2026-11-14 realized 0, entries 0, exits 0.
- Cron paper-trading-solana-15m active since ~18:35 WIB (user tap "Ya, jalankan paper tiap 15 menit"), first run ~18:51 WIB, trial 7 days to 2026-11-21 18:20 WIB. Paper only — the file's own header and the parent verification both confirm no signing, private key, broadcast, baw, or real swap in the machine.
- Diagnostics read directly (`workspace/solana-trading/run-diagnostics.jsonl`, 2 rows):
  - Run 1, 18:32:43 WIB: elapsed 742.5 s, deadline_hit false, universe 53 pools, entries 0, sightings 1. Reasons: sim_fail 13, chart_skip 9, audit_skip 11, holder_gate 9, dust 6, sighting 1, age_gt_12h 4. Stage seconds: pair 72.9, quote 330.4, audit 194.1, holder 0.0, chart 30.5. SOL $75.86.
  - Run 2, 19:03:53 WIB: elapsed 758.0 s, deadline_hit false, universe 53 pools, entries 0, sightings 2. Reasons: audit_skip 10, sim_fail 12, chart_skip 15, dust 5, holder_gate 6, age_gt_12h 3, sighting 2. Stage seconds: pair 80.4, quote 331.4, audit 196.5, holder 0.0, chart 37.5. SOL $75.97.
- Sightings so far (ledger): GPiHbgbvWbZHkqivF1V8aUpaUSt3MqSV3ZB2SBjuLGnD — holders 225, reserve $41,333.71, first seen 18:30:45 WIB; HLNFrydlB2kmF8T6e2K2xdSo5G3qnFd9DF5xtBMRpump — holders 469, reserve $4,930.46, first seen 19:03:43 WIB. These are first sightings awaiting a second confirmation, not entries and not candidates. Do not present either as a pick.
- Tooling, verified live by the parent on 2026-11-14 and recorded in BUILD_PROGRESS.md / the main-chat reports: working — GeckoTerminal, DexScreener, RugCheck (the only audit/holder/LP source), Jupiter v1 quote. Dead and NOT used — Solscan (404), GoPlus Solana (api returns code 2022 "main chain is not supported"), Jupiter v6 (HTTP 000), public Solana RPC for holder data (persistent 429). The machine makes no RPC calls at all.
- Bottleneck moved with the chain: on Solana the expensive stages are quote (~330 s) and audit (~195 s), not pair_info as on BSC. A 15-minute schedule against ~750 s runs is tight in the same way the BSC 750 s deadline was tight — watch whether the Solana runs start hitting their own deadline, rather than assuming the BSC deadline problem is gone.

### 4. Infrastructure 7/7 done — but the honest backtest verdict is negative, and two items are still open

From `workspace/solana-trading/INFRA_PROGRESS.md` (coordinator log, verified by the parent, 7/7 components complete by 19:00 WIB on 2026-11-14): real-time PumpPortal WebSocket ingest (discovery in seconds vs ~7.5 min polling lag), screening funnel from the 2026-11-14 Solana research (§4), wallet-signal leg, price store (10 pair / 1,009 candles), engine speed-up, backtest validation, monitoring. Runtime in a /tmp test fell 742.5 → 350.2 s (−53%). Two cautions that matter for the next study:

- The 350.2 s figure is from a /tmp test, not a cron run: the 19:03:53 WIB cron run still took 758.0 s. Do not claim the speedup is proven in production until a post-fix cron run shows it.
- Backtest verdict (component 6, re-checked by the coordinator from the dataset): the new funnel is NOT proven better than the old gate. Median +24 h return: old gate +3.1% vs new funnel −14.8% (primer n=10; extended n=20; new_only=0; TP 0% both; stop 40% vs 50%). The big winners (+927%, +195%) were rejected by the first-hour chart-dump rule. The old gate stays in use; the new funnel is only an additional candidate source, not a replacement. This is the correct reading and the one already reported to the user — do not soften it into "infrastructure improved, therefore the model improved."
- LP correction (coordinator's side finding): the claim "the LP gate blocks ALL pump.fun graduates" was NOT proven — the measure had read the wrong RugCheck field. Live check of 8 pump tokens: summary lpLockedPct passed 6/8 (61–100%), 0 on 2/8 (Rex, STOKE) while per-market burned was 100%. The user-approved fix (tap 18:58 WIB, applied 19:00 WIB) adds a fallback to max per-market lpLockedPct ONLY when the RugCheck summary is 0; thresholds unchanged; synthetic 0/0 still blocked (fail-closed intact). Note the parent's own caveat: on re-test the Rex/STOKE summaries had already recovered to ~100% on their own, so the fallback is a safety net, not a fix that changed today's results.
- Daemon ingest live: `nohup python3 infra/ingest.py` (PID 9651, from 18:59:58 WIB), PumpPortal WS connected and subscribed, log showing NEW tokens at 19:11:53 and 19:12:06 WIB. Caveat recorded by the parent: the daemon dies on VM restart and has no watchdog yet.
- Still open at run start (19:08 WIB): `wallet-signals.json` had NOT landed — `workspace/solana-trading/wallets/` contains the hunt scripts and `raw/` captures but no `wallet-signals.json`. The wallet-signal leg is built and tested (32 PASS / 0 FAIL / 1 SKIP) but has no signal data to score with yet. GMGN bundle data is NOT available free (403 without key), so bundle stays "unverified", never assumed clean — same rule as BSC since 2026-11-09.
- Live Solana is blocked, not started: agent Solana wallet EnGohiaof1t5Uw6tCfyEpcFF8cA7eASNMPqmHo4J6NHj holds 0 SOL (verified live 2026-11-14 ~18:15 WIB). No gas, no capital. The user chose "Paper Solana dulu, live menyusul" (18:23 WIB). Do not treat any paper result as a live-readiness claim, and do not propose funding live until paper has run.

### 5. What did not move: control arm, forward-return ledger, daily benchmark

- Forward-return ledger (`workspace/paper-trading/forward-return-ledger.md`): still an empty table — header rows only, no data rows. GANG was never recorded there on BSC, and nothing has been recorded for Solana either. The screen's hit rate remains unmeasured on both chains. This was already open in the 2026-11-10, 2026-11-11, 2026-11-12, and 2026-11-13 notes; it is still open, now on a second chain.
- Control arm (coin-flip control + hold benchmark): still not built — no control ledger or control script in either `workspace/paper-trading/` or `workspace/solana-trading/`. The BSC wins (+30% GANG) still cannot be distinguished from luck by the trial's own standard, and the Solana trial starts with the same gap. The chain move did not fix the trial-design gap; it only moved the trial.
- The user's daily benchmark (10% net profit / 10% loss limit, 2026-11-05) is unchanged and unmet by either trial: BSC closed at +10.7% / +7.2% virtual over 10 days (not per day), Solana at 0 after two runs. The 2026-11-09 honest answer — 5–10% per day is not proven — is unchanged by the move.

## Prerequisite check

- Prerequisites in place: Solana paper engine built and verified (paper_run_solana.py, py_compile OK, no signing/broadcast code), Solana paper cron active every 15 min (paper-trading-solana-15m, first run ~18:51 WIB), trial window to 2026-11-21 18:20 WIB, virtual capital 0.08 SOL, RugCheck as audit/holder source, Jupiter v1 for simulation quotes, ingest daemon live (PID 9651), LP fallback fix applied, monitoring in place.
- Prerequisites closed (BSC arm): both BSC paper crons disabled 2026-11-14 ~18:15 WIB by user order; final ledgers frozen at cash 0.01107179 / 0.01072416 BNB virtual, 0 positions. Do not restart the BSC arm without a fresh user order.
- Gap to close first (unchanged, now on two chains): no control arm and no benchmark. A winning day cannot be distinguished from luck, and zero days cannot be distinguished from too-tight gates. The Solana trial needs the control built into it from the start, not bolted on at the end the way BSC never got it.
- Second gap (unchanged): the forward-return ledger is still empty on both chains. Check it next time rather than assuming; record the Solana sightings' forward returns when their horizons mature.
- Third gap (new): wallet-signals.json has not landed, so the wallet-signal leg scores nothing yet; and the 350 s runtime improvement is unproven in a cron run. Both need a re-check, not an assumption.
- Fourth gap (unchanged, structural): live Solana needs funded SOL (wallet currently 0 SOL) plus a verified Jupiter + signing execution rail — neither exists yet, and the user has explicitly deferred live until paper proves itself.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual capital, no real money) that reads new pools and admits an entry only when fail-closed gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if equity falls below 70% (equity-measured since 2026-11-09 ~20:20 WIB) — and that is judged only at the end of the trial, not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards. Since 2026-11-09 ~19:50 WIB, the holder snapshot comes from GoPlus (not eth_getLogs), and bundle/dev-cluster checks are recorded unverified rather than assumed clean. Since 2026-11-11, the known BSC bottleneck is the pair_info stage, and the v2 gates have still killed 0 pairs on any day measured, because pairs are stopped earlier at the sighting and holder gates. Since 2026-11-12, the BSC deadline rate is known to be unstable day to day. Since 2026-11-13, the two BSC arms moved in opposite directions (main 53.2%, Variant A 14.5%). Since 2026-11-14: the BSC trial ended early by user order (final day deadline rates main 81.7% / Variant A 42.4%, the worst of the trial; final cash 0.01107179 / 0.01072416 BNB virtual; one token ever traded, GANG), and the model moved to Solana as a new 7-day paper trial (0.08 SOL virtual, RugCheck instead of GoPlus/Binance audit, Jupiter v1 instead of PCS quotes, first two runs 0 entries, 53 pools each, ~750 s each, first sighting GPiHbgbvWbZH… with 225 holders and $41,333.71 reserve). The new funnel from the Solana research is NOT proven better than the old gate (median +24 h −14.8% vs +3.1%), so the old gate stays.

## Worked example

Walk-through of one real run: the Solana paper dry run 1, ending 18:32:43 WIB on 2026-11-14 — the first run of the new trial.

1. Run: elapsed 742.5 s, deadline_hit false, universe 53 pools, entries_made 0, sightings 1, open_positions 0, SOL price $75.86.
2. Rejection counts: sim_fail 13, chart_skip 9, audit_skip 11, holder_gate 9, dust 6, sighting 1, age_gt_12h 4. (These sum to 53 — every pool in the universe is accounted for.)
3. Stage cost: pair 72.9 s, quote 330.4 s, audit 194.1 s, holder 0.0 s, chart 30.5 s. The expensive stages are quote and audit — the opposite of the BSC bottleneck (pair_info).
4. Outcome: cash stayed 0.08 SOL, ledger unchanged, one first sighting recorded (GPiHbgbvWbZH…, holders 225, reserve $41,333.71, first seen 18:30:45 WIB).
5. What this shows: the gates work on the new chain — 11 pools failed audit, 9 failed the holder gate, 13 failed the buy/sell-back simulation (later diagnosed as sim_sellback_fail: fresh pump tokens buyable but with no full-size Jupiter sell-back route, so the gate correctly refused them fail-closed). What this does not show: whether the model can find a winner on Solana, whether the 742.5 s runtime fits a 15-minute schedule once the funnel and wallet legs are wired in, or whether the first sighting will confirm on a second sighting. Contrast with run 2 (19:03:53 WIB, 758.0 s, 53 pools, 0 entries, sightings 2): same verdict, slightly different rejection mix (chart_skip 15, audit_skip 10, sim_fail 12) — two zero runs are two data points, not a pattern.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/ledger.json and state, in one sentence, the final BSC cash, the number of positions, and the 2026-11-14 daily realized PnL for the main arm (expected: cash 0.01107179 BNB virtual, 0 positions, realized 0 — unchanged since 2026-11-11).
2. Open workspace/solana-trading/ledger.json and do the same for the Solana trial (expected: cash 0.08 SOL virtual, 0 positions, realized 0; trial 2026-11-14 to 2026-11-21).
3. From the two BSC run-diagnostics.jsonl files, compute the 2026-11-14 deadline-hit rate for each arm (expected: main 58/71 ≈ 82%, Variant A 28/66 ≈ 42%) and compare with 2026-11-11 (38% / 23%), 2026-11-12 (61.3% / 29.6%), and 2026-11-13 (53.2% / 14.5%). Note that the final day was the worst for both arms and that the arms still did not move together across the four days.
4. From workspace/solana-trading/run-diagnostics.jsonl, state the two Solana runs' elapsed times and entries (expected: 742.5 s and 758.0 s, 0 entries each) and name the most expensive stage in run 1 (expected: quote, 330.4 s — not pair_info as on BSC).
5. Feedback check: if the user asks "did the Solana move fix the model?", the correct answer is no — the move changed the chain, the data sources, and the bottleneck, but the trial-design gaps (no control arm, empty forward-return ledger) moved with it, the new funnel backtested worse than the old gate (−14.8% vs +3.1% median +24 h), and live Solana is blocked on 0 SOL. Two zero-entry runs prove the gates run, nothing more.

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading both BSC ledgers and the Solana ledger directly instead of trusting a chat summary, computing the final-day deadline rates from the full day's diagnostics instead of quoting one slow run, keeping the BSC and Solana ledgers separate and in different units, noting that the 350 s speedup is a /tmp test and not yet a cron run, refusing to soften the negative backtest verdict), name the one most useful next adjustment (e.g. always pair a zero-entry day with the coverage figure and the chain it happened on — a Solana zero on 53 pools with a 758 s run means something different from a BSC zero on 52.1 pairs with an 81.7% deadline rate — and never present a virtual balance as real profit), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to fund the Solana agent wallet (currently 0 SOL) for live trading once the paper trial runs. Apply the Quant-Lab lens before that decision: run the Solana paper rules as a bake-off against a coin-flip control with realistic costs (Solana fees + Jupiter slippage + the sell-back failure rate the dry runs just measured — 13 and 12 sim_fail per run, mostly sim_sellback_fail), and only treat a live edge as real if it beats the control with a 95% CI above zero over the full 7-day trial to 2026-11-21. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict on Solana is worth more than funding a live wallet to test the same question with real SOL. Today's transfer warning is specific: the chain move feels like a fresh start, but a fresh start with the same missing control arm and the same empty forward-return ledger will produce the same unprovable verdict on 21 Nov that BSC produced on 14 Nov — only the token names will be different. Build the control into the Solana trial now, while it is 2 runs old, not at the end.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, forgetting the kill-switch is now equity-measured, forgetting that holder data on BSC came from GoPlus with bundle/dev-cluster unverified, forgetting that the BSC trial ended early on 2026-11-14 with final cash 0.01107179 / 0.01072416 BNB virtual, forgetting that the Solana trial uses RugCheck + Jupiter v1 with 0.08 SOL virtual to 2026-11-21, forgetting that the new funnel backtested worse than the old gate, or forgetting that live Solana is blocked on 0 SOL) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will the Solana paper trial find a second, different token — the first non-GANG entry anywhere — before 2026-11-21, or will the whole BACOT DEGEN story stay one token on one day on BSC plus zeros on Solana?
- Will wallet-signals.json land, and does the wallet-signal leg change any admission once it scores real data? Until it lands, the leg is built but silent.
- Will a post-fix cron run actually show the ~350 s runtime, or does the Solana engine stay near ~750 s (run 2 was 758.0 s after the fix was applied)? If it stays near 750 s, the 15-minute schedule is as tight as BSC's was.
- When will the coin-flip control + hold benchmark be built for Solana? Without it, neither a Solana win nor a week of Solana zeros can meet the trial's own "proven" gate.
- Will the forward-return ledger get its first row — BSC GANG retroactively, or a Solana sighting prospectively? If it stays empty, the screen's hit rate stays unmeasured on both chains.
- Is the BSC deadline spike (81.7% main on the final day) the tail of the egress problems that stalled the live feed all day, or a property of the BSC engine under load? The trial is over, so the question is now diagnostic for the Solana engine's own deadline behaviour, not for BSC.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL (0 wins / 4 losses, −0.00286388 WBNB; its AGC test stopped at round 5 when trading moved to Solana) or with MODAL BACOT live trading (disabled 2026-11-14 ~18:15 WIB with the move). Keep the three ledgers separate in every future note and letter.
- The user asked on 2026-11-09 whether 5–10% per day from trading is possible; the honest answer given then was no, not proven. One virtual +30% day on BSC followed by eight zero days and two zero Solana runs does not change that answer.
- The user declined a sell-all AGC offer on 2026-11-13 ~19:01 WIB (tap "Tidak, tahan AGC") — do not re-offer selling all AGC unless the user reopens it. That decision is about AGC holdings, not about this paper model, and the two must stay separate.

## Next review

2026-11-15T12:08:43Z. Next study should re-check the Solana paper runs (entries, sightings confirming or not, runtime vs the 15-minute schedule), confirm whether wallet-signals.json landed and whether the forward-return ledger and control arm moved at all, and count the zero days on Solana since the trial started.

## Already Covered in Main Chat

- The user ordered the BSC → Solana move for all trading at 2026-11-14 ~18:15 WIB, and the main agent reported the BSC jobs disabled and the Solana paper engine being built in the same message.
- The main agent reported the Solana paper engine built and dry run 1 passed at 2026-11-14 ~18:33 WIB (53 pools, 0 entry, cash 0.08 SOL, 4 tools working and 4 dead).
- The main agent reported the Solana infrastructure 7/7 complete and the honest backtest verdict at 2026-11-14 ~18:56 WIB (funnel new median −14.8% vs old gate +3.1%, old gate stays).
- The main agent reported the LP fix applied and the ingest daemon started at 2026-11-14 ~19:00 WIB (fallback only when RugCheck summary is 0; daemon PID 9651 from 18:59:58 WIB).
- The 2026-11-14 18:22 WIB 2-hour recap reported the BSC paper trial ended early with final cash 0.011072 BNB virtual (main) and 0.010724 BNB (Variant A), 0 positions, and the 0 SOL live blocker.
- The 2026-11-13 12:19, 14:19, 16:19, and 18:19 WIB 2-hour recaps each restated paper cash 0.01107 BNB virtual (main) and 0.01072 BNB virtual (Variant A), 0 open positions, and 0 entry / 0 exit on 2026-11-13.
- Not reported in main chat: the final-day BSC deadline-hit rates (main 81.7% / Variant A 42.4%), the pairs-seen mean (52.1 main), the Solana run 2 diagnostics (19:03:53 WIB, 758.0 s, 0 entries, second sighting HLNFrydlB2kmF8T6e2K2xdSo5G3qnFd9DF5xtBMRpump with 469 holders and $4,930.46 reserve), or that wallet-signals.json had still not landed at 19:08 WIB.

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers, diagnostics, and infrastructure progress files are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-13/model-degen-paper-trading-mandiri.md (read in full): day-9 check, third consecutive zero-entry day in both BSC arms, deadline rates 53.2% main / 14.5% Variant A, pair_info bottleneck, v2 kills 0, forward-return ledger still empty, control arm still missing, trial 6 days remaining at that point.
- Prior study notes 2026-11-05 through 2026-11-12 (known from the 2026-11-13 note's trajectory): 0 trades until 2026-11-09, first GANG entries 2026-11-09, TP exits +30% both arms 2026-11-10, GoPlus holder fix and equity kill-switch fix applied, day-7 zero day and 38% / 23% deadline rates on 2026-11-11, deadline regression question on 2026-11-12.
- Prior briefs (filenames listed): BACOT DEGEN Day Five (2026-11-09 12.24.28).html, BACOT DEGEN Head-to-Head (2026-11-08 12.17.08).html, Variant A Day One (2026-11-07 12.28.06).html, BACOT DEGEN Day Seven (2026-11-11 12.15.09).html — the Day Seven brief covers the day-7 zero day, the deadline improvement, and the pair_info bottleneck; no brief exists for day 8, day 9, or day 10, and no brief covers Solana at all.
- Repetition search (grep over this goal's agent_notes/*.md and briefs/, variants "solana", "paper solana", "pindah solana", "funnel baru", "zero-entry", "deadline", "pair_info bottleneck", "GANG take-profit"): no prior note or brief mentions Solana, a Solana paper trial, a funnel backtest, or a chain move — those are new to the goal's own record. The 2026-11-11, 2026-11-12, and 2026-11-13 notes match on "GANG", "deadline", "pair_info", and "zero day" (the TP exits, the fixes, the deadline question, and the day-7/8/9 zeros are all there). Today's BSC findings extend that thread rather than starting a new one.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active; current state "Posisi GANG ditutup take-profit +30% virtual; kas virtual 0,01107 BNB dan tidak ada posisi terbuka." — still accurate for the frozen BSC arm, but now stale as a whole-goal summary because the goal's live work is the Solana trial (cash 0.08 SOL virtual, 0 positions).
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-15T12:08:43Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- Ledgers read directly in this turn: workspace/paper-trading/ledger.json (cash 0.011071790886431537 BNB virtual, positions empty, daily 2026-11-14 realized 0 / entries 0 / exits 0) and workspace/paper-trading/variant-a/ledger.json (cash 0.010724160078509572 BNB virtual, positions empty, daily 2026-11-14 realized 0 / entries 0 / exits 0); workspace/solana-trading/ledger.json (started 2026-11-14T18:20:20+07:00, ends 2026-11-21T18:20:20+07:00, cash 0.08 SOL virtual, positions empty, trades empty, daily 2026-11-14 realized 0 / entries 0 / exits 0, sightings GPiHbgbvWbZH… 225 holders / $41,333.71 and HLNFrydlB2kmF8T6e2K2xdSo5G3qnFd9DF5xtBMRpump 469 holders / $4,930.46).
- Diagnostics read directly in this turn: workspace/paper-trading/run-diagnostics.jsonl (71 main runs on 2026-11-14, 58 deadline hits, pairs seen mean 52.1, first 00:11:33 WIB, last 18:11:07 WIB, entries 0) and workspace/paper-trading/variant-a/run-diagnostics.jsonl (66 runs, 28 deadline hits, pairs seen mean 14.7, first 00:03:38 WIB, last 18:15:16 WIB, entries 0); workspace/solana-trading/run-diagnostics.jsonl (2 rows: 18:32:43 WIB 742.5 s / 53 pools / 0 entries; 19:03:53 WIB 758.0 s / 53 pools / 0 entries).
- Forward-return ledger read in this turn: workspace/paper-trading/forward-return-ledger.md — table header only, no data rows.
- Control-arm check in this turn: listings of workspace/paper-trading/ and workspace/solana-trading/ show no control ledger or control script in either; the control arm remains unbuilt.
- Infrastructure files read in this turn: workspace/solana-trading/INFRA_PROGRESS.md (7/7 complete, backtest verdict, LP correction, daemon PID 9651 from 18:59:58 WIB, wallet-signals.json not landed at 19:00 WIB), workspace/solana-trading/paper_run_solana.py header (Solana replacement engine, paper-only, no signing/broadcast), workspace/solana-trading/wallets/ listing (scripts + raw/ only, no wallet-signals.json), workspace/solana-trading/infra/ingest.log tail (NEW tokens 19:11:53 and 19:12:06 WIB).
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window 2026-11-13T12:24:29Z → 2026-11-14T12:11:26Z) plus the run's chunk handoff (covering to 2026-11-14T12:02:00Z): the user's 2026-11-14 ~18:15 WIB order to move all trading to Solana, the "Paper Solana dulu, live menyusul" decision (~18:23 WIB), the infra/backtest/LP/daemon reports (~18:33–19:00 WIB), the 18:22 WIB recap reporting the BSC trial's early end, and the four 2026-11-13 2-hour recaps reporting the zero entries and unchanged BSC cash.
- Standing user context: free-only first, BSC only for the old scope (now superseded for trading by the 2026-11-14 Solana order); no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet; daily profit benchmark 10% net with symmetric 10% loss limit; never force a trade to chase the daily target; AGC hold — do not re-offer selling all AGC (user declined 2026-11-13 ~19:01 WIB).

### Searches skipped or unavailable

- No new web search was run: the trial's own record is primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief HTML files were listed and their subjects taken from the goal record and prior notes, not re-read in full: all four predate the 2026-11-14 chain move and the final BSC day, so re-reading their rendered HTML would not change the newness ruling.
