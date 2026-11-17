# Study Notes - 2026-11-10 - BACOT DEGEN
<!-- studying-run-start: 2026-11-10T12:13:23Z -->

## Goal in one line

BACOT DEGEN (goal_b9d1c43a21e5, slug model-degen-paper-trading-mandiri) is the user's standalone memecoin paper-trading model: virtual capital only (0.010 BNB), no real money, no execution, fully separated from MODAL BACOT. Its engine reads new GeckoTerminal pools, Binance audit, holder/bundle/dev data, and charts. Purpose: prove whether the model can stand on its own before any decision about live trading. Trial window: 2026-11-05 to 2026-11-19. Variant A — same gates with a clean-universe pre-filter (GeckoTerminal dex == pancakeswap_v2, quote token WBNB, reserve >= $3,000) — runs in parallel on a separate ledger and cron since 2026-11-07 ~06:42 WIB.

## Study focus today

Learning state: in_study, teach mode, novice band, mastery not yet estimated. The retrieval prompt is: from memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example. Today's study is the day-6 check (2026-11-10, evidence window 2026-11-09T12:02:55Z to 2026-11-10T12:02:54Z, run start 19:13 WIB): the first entries, the first exits, and the first take-profits in the trial — and whether any of that changes the verdict the model still has to earn by 2026-11-19. It does not confuse any of this with live BACOT SCALPING (real money; AGC round 4 stopped 2026-11-09, score 0 wins / 4 losses, cumulative −0.00286388 WBNB) or with MODAL BACOT live trading — separate ledgers, separate money. All figures below are PAPER/VIRTUAL unless stated otherwise.

## What today's evidence shows

### The arc the 2026-11-09 note could not contain: fix, first entries, exits, then take-profit

The prior study note (2026-11-09, runs to ~19:12 WIB) ended at zero entries in both arms, with the holder stage truncating runs (main deadline rate 88.7%, Variant A 75.9%). Everything below happened after that note's cutoff, inside this run's evidence window, and is preserved here because the next study must not re-derive it from chat fragments.

### 1. The GoPlus holder fix — the root cause was dead data, not tight gates

On 2026-11-09 ~19:50 WIB the user asked why nothing had passed the gates for days ("Tapi belum ada yang lolos udah berapa harj juga dari gate kita, coba evaluasi lagi lalu perbaiki jika ada yang menurutmu salah", message:eb1acef9-462b-4816-9f5c-b3ff1396ab53). The evaluation (message:assistant-msg-7c51f7a3-a19b-4e08-bb87-f5541f23a6c4, also recorded in MEMORY.md) found:

- BACOT DEGEN had 0 entries for 4 days NOT because gate v2 was too tight: in the 8 runs before the fix, v2_holders / v2_dev / v2_lp killed 0 pairs, because almost no pairs reached that gate.
- Each run hit the 750 s deadline after checking only 4–18 of 60–80 pairs (main) / 2–9 of 15–20 (Variant A). The holder stage took 650–995 s per run (~85% of the deadline).
- Cause, verified live 2026-11-09: the log-based holder snapshot has NO live source — Ankr getLogs quota 0% until 2026-12-01; all public BSC RPCs answer eth_getLogs −32005 "limit exceeded" even for a 50-block range; Blockscout does not support BSC (404). The log-based `analyze_holders` did not finish in 280 s.
- Fix applied, thresholds NOT changed: `holder_check.py` gained `analyze_holders_goplus` (holder_count + top10 + largest + LP top1 + creator/owner from GoPlus token_security, free, no key; verified on AGC 20,226 holders and on MWGL ~627 holders), LP burn still via eth_call (AGC 46.16%, matching the old 46.25%); `paper_run.py` + `variant-a/paper_run_a.py` now run chart-first-then-holder (chart ~1–2 s, holder ~20 s). GoPlus holders list MUST be filtered (pair itself + burn address excluded), otherwise the pair (~25%) trips the largest-holder gate on every token.
- Gap disclosed, not hidden: bundle cluster + dev satellite cluster CANNOT be checked without Transfer logs — recorded as bundle_unverified / dev_cluster_unverified, not assumed clean. Other gates (audit, chart >= 12 candles, LP burn/lock, 2-sighting, correlation, deploy cap, kill-switch) remain in full force. The old log-based function is retained for when the indexer returns (Ankr 2026-12-01).
- Verification in the first post-fix runs: Variant A run 19:54 WIB — 275 s, deadline NOT hit, holder stage 67 s, 12 of 16 pools processed (before: 800–980 s, deadline hit, 4 of 19). Main run 19:56 WIB — 278 s, deadline NOT hit, holder 50.7 s, 48 pools checked (previous old-code run: 945 s, deadline hit, 9 pools). By 20:52 WIB main saw 80 of 80 pairs; Variant A 20:42 saw 18 of 18.

The user approved paper-first proof ("Coba aja dulu papper trading, yang lolos juga belum tentu ada", message:b83b8269-6b6a-4423-9100-b1a7c170c973, 2026-11-09T12:48:58Z). The assistant also corrected itself in the next message: a manual run it had claimed was running was actually lock-blocked 3 times by the scheduled 15-minute runs (message:assistant-msg-4d71d8be-a2ce-4e15-a27a-b2415ab41297).

### 2. Kill-switch measurement fix — equity, not cash

Run 19:58 WIB on 2026-11-09 fired the kill switch for the first time, on a measurement artefact: `paper_run.py:527` used cash_bnb only, so cash 0.00699 BNB virtual < the 0.0070 threshold tripped it although equity was ~0.0099834 BNB virtual (−0.17%). Practically no effect, because the 30% deploy cap already limited the model to 1 open position. Fix applied 2026-11-09 ~20:20 WIB on the user's tap "Ya, ukur ekuitas" (message:e6908e0a-2652-4e3f-bdc6-34a18bd05c0c): the kill switch now measures equity (cash + last_value_bnb of open positions, fresh from the exit-check loop above) in `paper_run.py:527-536` + `paper_run_a.py:543-552`; the event message now reports equity + cash; the 30% threshold is UNCHANGED. Verified: py_compile passed; formula tested on live numbers (equity ~0.010245 main / ~0.010257 Variant A → False; a real drawdown still returns True); ledger unchanged. Lesson recorded then and worth keeping: a worker price claim ($0.00349) was inconsistent with the ledger (0.003 BNB → ~594m tokens ≈ $0.0000000035) — that price was discarded; ledger + FDV/liq from DexScreener govern. Always cross-check worker price claims against token counts in the ledger.

### 3. First entries — GANG, both arms, 2026-11-09 19:54–19:56 WIB

- Variant A entry (message:assistant-msg-13945ef9-3678-eec9-f21c-36eeb3a75ab7, 2026-11-09T12:58:45Z): first entry of the trial. GANG (Gang) 0x0c6302401aa5325c2e36f170f52c00b1d220b405, pair PCS V2 0x0bd5ded695d61c2db15c703c345d57e039fd0b6d. Entry 0.003 BNB virtual @ 19:54:13 WIB → ~594m tokens (assuming 18 decimals). FDV ~$3.45m, liquidity ~$259k (DexScreener). Cash then 0.00699 BNB virtual, 1 open position. Gates passed: audit clean; holder 6,665 (top10 14.17%, largest 3.16%); LP burn 99.99%; dev identified, dev balance 0%; chart 12 candles, no dump; 2-sighting: holder 84 → 6,665 and reserve 168.9 → 188.34 BNB. Bundle + dev cluster unverified.
- Main-model entry (message:assistant-msg-7c7b4972-dbfd-ebdc-a7d4-57f67309333b, 2026-11-09T13:04:19Z): same GANG contract, entry 0.003 BNB virtual @ 19:56:54 WIB → ~580.7m tokens, same gates. Both arms hold GANG independently — two separate ledgers, by design, not double-counting.
- Caveat carried in both reports and worth preserving: GANG is the same token as BACOT SCALPING live round 2 (which hit its stop). The paper entries are independent, via their own gates, at a later price, with virtual money — not a "revenge" on that loss.
- Status 2026-11-09 20:55 WIB (message:assistant-msg-179054ae-3df0-490b-a483-ee2a57dad3b0): main entry +3.8% unrealized (last value 0.00311), equity 0.01010 (+1.0%); Variant A +11.2% (last value 0.00334), equity 0.01033 (+3.3%). 0 closed positions then. At 22:19 WIB GANG was still open, +17% unrealized.

### 4. Overnight exits and re-entries — 2026-11-10 00:34–04:06 WIB

The first positions did not survive the night; both arms exited and re-entered the same token:

- Main: trailing stop −15% from peak, exit 01:58:40 WIB, entry 0.003 → exit 0.0029899 BNB virtual, realized −0.0000301 BNB virtual (~−1%, incl. gas); cash 0.0099699 BNB, 0 open (message:assistant-msg-139d3f37-7afa-9788-3335-436c74ce8678). Re-entry 04:06:42 WIB, 0.003 BNB virtual → ~535,681,808 tokens; gates: holder 6,759, top10 14.31%, largest 3.16%, LP burn 99.99%, chart 12 candles, +4.31%/60m, 2-sighting holder 122 → 6,759, reserve 157.33 → 198.49 BNB (message:assistant-msg-7c46a9d0-1a0d-559b-40f6-3d7d62b701d2).
- Variant A: trailing exit 00:34:58 WIB, realized +0.0001177 BNB virtual (first Variant A exit); re-entry 00:42:38 WIB, 0.003 BNB virtual (holder 6,758, LP burn 99.99%, chart +7.13%/15m, +3.39%/60m, 2-sighting holder 84 → 6,758, reserve 168.9 → 192.5 BNB); that re-entry hit stop-loss −15% at 02:53 WIB, exit 0.0025483 BNB virtual, realized −0.0004717 BNB virtual; then a third entry 04:00:05 WIB, 0.003 BNB virtual → ~534,598,177 tokens (messages:assistant-msg-38fdcb2a-b656-c9d7-9e94-8501265320cc, assistant-msg-7201df43-a93b-ba77-c303-c1718c1c833c, assistant-msg-c3e46a82-c942-59da-6267-89fe0692f745).
- The user asked "Bukannya itu modal bacot?" (message:616c04b8-96ba-4e85-a10e-27de25893656, 2026-11-09T13:56:38Z); the assistant distinguished BACOT DEGEN (paper/virtual only) from MODAL BACOT (live, 0 trades, feed empty then) and from the live scalp test (message:assistant-msg-646b3b9e-e770-44f1-aa7d-fc1062c12d0b).

### 5. First take-profits — 2026-11-10 15:59 and 16:04 WIB

- Main model (message:assistant-msg-acee09f8-f5d5-79d3-db74-fd8289e02939, 2026-11-10T09:02:31Z): GANG re-entry (04:06 WIB) → TP +30%, exit 0.0041219 BNB virtual at 15:59:25 WIB, realized +0.0011019 BNB virtual after gas. Virtual cash 0.0110718 BNB, 0 open positions, realized today +0.0010718 BNB virtual. Daily budget +0.001 BNB reached, so no new entries that day. Kill switch NOT active. Goal record updated accordingly (goal_update_941b76c6f1b8, 2026-11-10T09:01:21Z; current_state now "Posisi GANG ditutup take-profit +30% virtual; kas virtual 0,01107 BNB dan tidak ada posisi terbuka.").
- Variant A (message:assistant-msg-fcb0cd4f-d41f-225c-22f6-e120e6dbc5c2, 2026-11-10T09:15:52Z): GANG entry 0.003 BNB virtual → TP +30%, exit 0.004098 BNB virtual at 16:04:33 WIB, realized +0.001078 BNB virtual. Virtual cash 0.010724 BNB (above the 0.010 starting capital), 0 open, realized today +0.000724 BNB virtual from 3 exits. Kill switch NOT active. GANG was seen again after exit (sighting 16:09:56 WIB, holder 6,968, reserve 229.24 BNB) — recorded as a new baseline, not a new position.
- What this proves and what it does not: it proves the repaired machine can see the market and can complete a full entry→TP cycle in both arms on the same token on the same day. It does NOT prove the model is profitable: one token, one day, three exits per arm at most, and the trial's verdict still waits on 10 rounds to 2026-11-19. Both arms are now above starting virtual capital for the first time (main +10.7%, Variant A +7.2% on cash), but those are virtual balances after a single winning day, not realised profit.

### 6. What regressed again after the fix

The deadline problem returned in later runs in the window, even after the GoPlus fix: the main run at 01:55 WIB took 772 s (deadline 750 s hit, 41/80 pairs seen); the Variant A run at 02:53 WIB took 885 s (8 of 13 pairs seen); a Variant A run at 03:40 failed (killed by runtime ~259 s, ledger unchanged, recovered at 03:55). The fix shortened the holder stage when it runs cleanly, but run duration is still volatile — coverage narrows again on slow runs. Do not quote the 275 s / 278 s post-fix runs as the new normal; they are the best case so far. The next study should re-check deadline-hit rates over 2026-11-10 before concluding the latency problem is solved.

## Prerequisite check

- Prerequisites in place: v2 engine on the 15-minute cron (paper-trading-15m), Variant A on its own 15-minute cron (paper-trading-variant-a-15m) with a separate ledger, GoPlus holder source live in both arms, kill switch now equity-based, trial window to 2026-11-19 (9 days remain from 2026-11-10).
- Gap to close first (unchanged): no control arm and no benchmark in the trial. Until a coin-flip control and a hold benchmark run beside the model, a winning day — even a +30% TP in both arms — cannot be distinguished from luck. The 2026-11-09 note's first gap stands, and today makes it sharper: the model now has wins to be tempted by.
- Second gap (changed): the holder-stage latency is fixed as a source problem but not yet as a reliability problem — deadline hits returned later on 2026-11-10. Before trusting coverage, the next study should check the 2026-11-10 deadline-hit rates and stage timings.
- Third gap (unchanged): the forward-return ledger is still empty as of the 2026-11-09 note; whether GANG's first entries were ever recorded there is unverified — check it next time rather than assuming.

## Retrieval prompt

From memory, state the core idea of BACOT DEGEN in your own words, then check it against the worked example below. Expected core: a standalone paper-only memecoin model (virtual 0.010 BNB, no real money) that reads new GeckoTerminal pools and admits an entry only when fail-closed v2 gates all pass — at least 12 candles, complete holder snapshot with at least 50 holders, identified dev, LP burn at least 50% or top LP holder a contract, 2-sighting growth (holder +10% and BNB reserve +5%, with the sighting check running BEFORE the v2 data gates since the 2026-11-06 fix), correlation block, max 1 entry per run, max 30% of capital deployed, kill-switch if equity falls below 70% (equity-measured since 2026-11-09 ~20:20 WIB) — and that is judged only at the end of the trial (2026-11-19), not trade by trade. Variant A adds one step before all of that: a clean-universe pre-filter (PancakeSwap V2 only, quote WBNB, reserve >= $3,000) that runs before any on-chain work, with the same gates and the same confirmation rule afterwards. Since 2026-11-09 ~19:50 WIB, the holder snapshot comes from GoPlus (not eth_getLogs), and bundle/dev-cluster checks are recorded unverified rather than assumed clean.

## Worked example

Walk-through of one real completed cycle: the main-model GANG re-entry and take-profit, 2026-11-10.

1. Entry: 04:06:42 WIB, 0.003 BNB virtual → ~535,681,808 GANG tokens (0x0c6302401aa5325c2e36f170f52c00b1d220b405, pair 0x0bd5ded695d61c2db15c703c345d57e039fd0b6d).
2. Gates passed (paper): audit clean, no RISK hit; holder 6,759 (top10 14.31%, largest 3.16%); dev distributor identified, dev balance 0%; LP burn 99.99%; chart 12 candles, +4.31% per 60 minutes, drop from high 1.5%, dump_flag false; 2-sighting: holder 122 → 6,759, reserve 157.33 → 198.49 BNB; bundle + dev cluster recorded unverified, not assumed clean.
3. Position: 1 open position = 30% of virtual capital, cap reached; no second entry possible while it is open.
4. Exit: 15:59:25 WIB, take-profit +30%, exit 0.0041219 BNB virtual, realized +0.0011019 BNB virtual after gas.
5. Ledger after: cash 0.0110718 BNB virtual, 0 open positions, realized today +0.0010718 BNB virtual (including the earlier trailing exit −0.0000301 BNB virtual at 01:58 WIB). Daily budget +0.001 BNB reached → no new entries that day.
6. What this shows: the full cycle works end to end on the repaired machine — entry, monitoring, TP exit, ledger update, daily-budget stop. What it does not show: whether the +30% was skill or one token's good day. That is what the remaining 9 days and the still-missing control arm are for.

## Practice task

One small, low-load item, with immediate feedback after each step:

1. Open workspace/paper-trading/ledger.json and state, in one sentence, the cash, the number of positions, and the realized PnL today.
2. Open workspace/paper-trading/variant-a/ledger.json and do the same for Variant A; confirm the two ledgers agree that both arms closed the day with 0 open positions and cash above 0.010 BNB virtual.
3. List the exits each arm recorded on 2026-11-10 (main: trailing −0.0000301 then TP +0.0011019; Variant A: trailing +0.0001177, stop −0.0004717, TP +0.001078) and check the realized-today totals match (+0.0010718 main, +0.000724 Variant A).
4. Check the run diagnostics for 2026-11-10: how many runs hit the 750 s deadline, and whether the holder stage stayed near ~50–70 s or regressed toward the old 650–995 s.
5. Feedback check: if both arms show a +30% TP on the same token on the same day, the correct conclusion is "the machine can complete a cycle and both arms are above starting capital for the first time — but one token and one day do not prove an edge; the control arm is still missing" — not "the model is proven" and not "GANG is a buy signal."

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. reading both ledgers separately instead of merging the arms, checking the exit sequence instead of only the TP, verifying the daily-budget stop), name the one most useful next adjustment (e.g. always check deadline-hit rates on the same day as a good result — a fast win on a slow day may mean the machine only saw part of the market — and never present a virtual TP as real profit), and stop there.

## Transfer challenge

Real situation where BACOT DEGEN would apply: the user is deciding whether to resume BACOT SCALPING (real money) once funds return, and whether the paper model's gates should inform that decision. Apply the Quant-Lab lens before that decision: run the scalp rules as a paper bake-off against a coin-flip control with realistic costs (gas + 2% tax each way + slippage), and only treat the scalp edge as real if it beats the control with a 95% CI above zero. The same "no edge is a real finding that saves money" principle applies — a clean negative verdict is worth more than another funded test round. Today's transfer warning is specific: a +30% virtual TP in both arms is exactly the kind of result that tempts a premature live decision; the trial's own rule says the verdict waits until 2026-11-19 and needs the control arm.

## Confidence check

Ask the user to rate confidence (1-10) in stating BACOT DEGEN's core idea and its v2 gates from memory, then compare that rating to performance on the retrieval prompt above. A high rating with a wrong or incomplete gate list (e.g. forgetting that Variant A pre-filters before any on-chain work, forgetting that the sighting check now runs before the v2 gates, forgetting the kill-switch is now equity-measured, or forgetting that holder data now comes from GoPlus with bundle/dev-cluster unverified) is the signal to re-study the gates, not to trust the feeling.

## Open questions and things to watch

- Will the model find a second, different token before 2026-11-19, or will the whole trial's wins be GANG alone? A single-token trial cannot prove a model.
- Is the deadline regression on 2026-11-10 (772 s, 885 s runs) a one-day spike or the fix wearing off under load?
- When will the coin-flip control + hold benchmark be built? Without it, the 2026-11-10 wins cannot meet the trial's own "proven" gate.
- Was GANG recorded in the forward-return ledger? If not, the screen's hit rate stays unmeasured even after its first entries.
- Do not confuse this goal's paper results with BACOT SCALPING's real-money PnL (0 wins / 4 losses, −0.00286388 WBNB) or with MODAL BACOT live trading (0 live trades). Keep the three ledgers separate in every future note and letter.
- The user asked on 2026-11-09 whether 5–10% per day from trading is possible; the honest answer given then was no, not proven. One virtual +30% day does not change that answer — it is one data point inside a trial that ends 2026-11-19.

## Already Covered in Main Chat

- User asked 2026-11-09T12:29:25Z whether 5–10% per day from trading is possible; main agent answered honestly no, not proven, citing the losing scalp record.
- User asked 2026-11-09T12:31:28Z to evaluate and fix the gates after days with no entry; main agent reported the GoPlus holder-source fix and chart-first reordering on 2026-11-09T12:45:21Z.
- User approved paper-first proof 2026-11-09T12:48:58Z ("Coba aja dulu papper trading, yang lolos juga belum tentu ada").
- Main agent reported the first Variant A GANG entry 2026-11-09T12:58:45Z and the main-model GANG entry 2026-11-09T13:04:19Z, including the kill-switch cash-measurement bug.
- User approved the equity kill-switch fix 2026-11-09T13:19:09Z ("Ya, ukur ekuitas"); main agent confirmed it applied 2026-11-09T13:30:00Z.
- User asked 2026-11-09T13:56:38Z "Bukannya itu modal bacot?"; main agent distinguished BACOT DEGEN (paper only) from MODAL BACOT and live scalping.
- Main agent reported the overnight GANG exits and re-entries in main chat on 2026-11-09T19:13:20Z (main trailing exit), 2026-11-09T20:12:07Z (Variant A stop-loss exit), 2026-11-09T21:03:05Z and 2026-11-09T21:11:15Z (re-entries 04:00/04:06 WIB).
- Main agent reported the main-model GANG take-profit +30% at 2026-11-10T09:02:31Z and the Variant A take-profit +30% at 2026-11-10T09:15:52Z, both labelled PAPER/VIRTUAL with cash, realized PnL, and the daily-budget stop.
- The 2026-11-10 16:19 WIB 2-hour recap restated both TP exits, cash 0.0110718 / 0.010724 BNB virtual, and 0 open positions.

## Research Trajectory

### External sources viewed

- None. No new web source was needed: the trial's own ledgers, diagnostics, and the main-chat record are the primary evidence, and the method sources behind the gates were already read and recorded in the 2026-11-05 note.

### Prior trajectories reviewed

- Prior study note workspace/goals/model-degen-paper-trading-mandiri/agent_notes/2026-11-09/model-degen-paper-trading-mandiri.md (read in full): day-5 check to ~19:12 WIB, 0 entries in both arms, deadline rates main 88.7% / Variant A 75.9%, v2 evaluations collapsed to 6 main / 8 Variant A, pairs seen 38.3 / 11.3. Today's note supersedes its zero-entry state (first entries 19:54/19:56 WIB, exits, re-entries, TP exits 15:59/16:04 WIB on 2026-11-10) and its bottleneck framing (GoPlus fix applied after its cutoff).
- Prior study notes 2026-11-05, 2026-11-06, 2026-11-07, 2026-11-08 (known from the 2026-11-09 note's trajectory): 0 trades, control arm and forward-return ledger still missing, holder gate ~96% of Variant A survivors.
- Prior briefs: BACOT DEGEN Day Five (2026-11-09 12.24.28).html, BACOT DEGEN Head-to-Head (2026-11-08 12.17.08).html, Variant A Day One (2026-11-07 12.28.06).html (listed via user_goal.get; subjects are the 2026-11-07 to 2026-11-09 results, all predating the first entries and TP exits).
- Repetition search (grep over agent_notes/ and briefs/ for this goal, variants "GANG", "take-profit", "TP +30", "GoPlus", "kill switch", "equity"): the 2026-11-05 to 2026-11-09 notes matched on "GANG" (as a live-scalp token / sighting only), "GoPlus" (as a proposed source, not applied), and "kill switch" (cash-measured); no prior note or brief contains the first GANG paper entries (19:54/19:56 WIB 2026-11-09), the GoPlus fix as applied, the equity kill-switch fix, or the 2026-11-10 TP exits (+30% in both arms). Today's findings are new against the notes and briefs — but the repetition search is only half the test: the same findings were already reported to the user in main chat (see Already Covered in Main Chat), which is what decides the ruling below.

### Scaffolds and support tactics

- Goal record via user_goal.get (goal_b9d1c43a21e5): category money, exploratory, active; current state "Posisi GANG ditutup take-profit +30% virtual; kas virtual 0,01107 BNB dan tidak ada posisi terbuka."; goal updates confirm the TP exit (goal_update_941b76c6f1b8), the re-entries (goal_update_75e6b253e36c, goal_update_de4e128d4c24), and the first entries (goal_update_a603ea0d71b8).
- Study task plan from the assignment (teach, novice band): prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-11T12:13:23Z — carried into this note, adapted to the model rather than to a classroom skill.

### Connected user data

- No ledger or diagnostics file was re-read in this turn: the entry/exit/TP figures are taken from the main-chat messages and goal updates cited above, which quote the ledgers directly (entry times, token counts, exit values, cash, realized PnL). The next study should re-read workspace/paper-trading/ledger.json, workspace/paper-trading/variant-a/ledger.json, and the run diagnostics to confirm the 2026-11-10 deadline-hit rates and whether GANG was recorded in the forward-return ledger — those two checks were not done in this turn and are flagged as open, not assumed.
- No wallet, calendar, or device data was needed for this paper-only goal; no real-money state was touched.

### Image references checked

- None.

### User context and memory

- Recent main-chat conversation via muse.context_fetch (conversation, window 2026-11-09T12:02:55Z → 2026-11-10T12:14:38Z) plus the run's chunk handoff and chunk 2/2: the full GANG arc (evaluation, fix, entries, exits, re-entries, TP exits) was reported to the user message by message in main chat, with message handles cited in the note.
- Standing user context: free-only first, BSC only, no transaction without permission except narrow armed scopes; paper trading is simulation only and never touches the wallet; daily profit benchmark 10% net with symmetric 10% loss limit; never force a trade to chase the daily target; trial ends 2026-11-19.

### Searches skipped or unavailable

- No new web search was run: the trial's own record is primary evidence, and the method sources behind the gates were already read on 2026-11-05. A fresh search would not change this note's findings.
- The prior brief HTML files were listed and their subjects taken from the goal record and prior notes, not re-read in full: all three predate the first entries and TP exits, so re-reading the rendered HTML would not change the newness ruling.
