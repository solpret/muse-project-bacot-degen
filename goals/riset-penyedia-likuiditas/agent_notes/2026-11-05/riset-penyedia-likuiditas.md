# Study Notes - 2026-11-05 - RISET PENYEDIA LIKUIDITAS
<!-- studying-run-start: 2026-11-05T12:08:10.698244+00:00 -->

## Goal snapshot

- Goal: RISET PENYEDIA LIKUIDITAS (`goal_2da9e3ed9aff`, slug `riset-penyedia-likuiditas`, category money, kind exploratory). Created 2026-11-04T17:56:36Z; last activity 2026-11-04T18:07:19Z; status active, momentum on_track.
- Value alignment (from `user_goal.get`): "Mencari jalur cuan baru di luar trading dan free mint, dengan riset dulu sebelum mempertaruhkan dana."
- Current state (goal view): "Halaman riset LP selesai dibangun, sudah diverifikasi, dan sudah disampaikan; belum ada posisi LP dan belum ada dana yang bergerak."
- Phase: research only. No LP position, no funds moved, no execution authorised. Any LP execution needs a separate user order after the user has read the research. This goal is kept separate from BACOT DEGEN (paper trading v2, trial to 2026-11-19); BACOT DEGEN is not touched by this goal.
- Selection trigger for this run: `review_due`. Study task plan: target skill RISET PENYEDIA LIKUIDITAS, mode teach, mastery band novice, evidence label tentative. Next review: 2026-11-06T12:08:11.096341490Z.
- Mastery: not yet estimated. No observed performance of the user on this skill exists yet (zero of the three observations needed); do not fabricate a number.

## What the research already established (2026-11-04, delivered)

Source: the deep-research report at `workspace/research_notes/riset-penyedia-likuiditas-untung-20261104-1757/report.md` (8 questions, sources named with URLs + access dates) and the summary page built from it and delivered to the user 2026-11-05 ~01:07 WIB (goal update `goal_update_b843d1a76f53`). The core findings were also stated to the user in main chat on 2026-11-04T18:03:35Z (`message:assistant-msg-de4d25e0-dd93-d3a2-b70b-d5aac4ef3345`).

- **Core idea (one line):** an LP earns only when fees (+ incentives, if any) minus gas and other costs beat impermanent loss (IL) versus simply holding the same assets — `fee − gas − costs > IL` is the breakeven test.
- **How it works:** an LP deposits two tokens into an AMM pool; traders swap against the pool; the LP is paid a share of swap fees proportional to its active liquidity. PancakeSwap V2 is full-range (passive, fungible LP token, fee 0.25% total of which 0.17% goes back to the pool for LPs, auto-compounding); V3 is concentrated liquidity (position is an NFT, earns fees only while the price is inside the chosen range, fees must be claimed manually, out-of-range means 0 fee and 100% one token).
- **IL math (50/50 full-range):** `IL = 2√r/(1+r) − 1`, where r is the price ratio at exit vs entry. 1.25x ≈ 0.6%, 2x ≈ 5.7%, 5x ≈ 25.5% vs HODL; symmetric (2x up and −50% give the same IL); non-linear. Worked example from the report (verified in the summary page calculator): deposit $10,000 ($5,000 BNB + $5,000 stablecoin), BNB rises 2x — HODL becomes $15,000, LP $14,142, so $858 of fees (8.6% of starting capital) is needed just to break even vs HODL.
- **Empirical evidence (both studies are Uniswap/Ethereum, not PancakeSwap/BSC — numbers do not transfer raw):** Loesch et al., arXiv:2111.09192 (Uniswap V3, May–Sep 2021, 17 largest pools): fees $199.3M vs IL $260.1M, aggregate −$60.8M vs HODL. Bitquery revised study (Oct 2026, 8 busiest Uniswap V3 pools on Ethereum, 14 Oct 2025–13 Oct 2026, ~121,000 positions): fees $41.6M, price-move loss vs HODL $60.6M, gas $1.4M, net −$20.4M vs HODL; only 34% of regular closed positions beat HODL after gas (49% before gas). Winners concentrate in sideways/stable pools; no range width won more often than it lost.
- **Strategies:** no strategy is proven generally dominant. Stable–stable minimises IL but pays tiny fees and carries depeg risk. Blue-chip pairs have deep volume but still lose in strong trends. Narrow V3 ranges raise fee per dollar *and* IL per dollar. Rebalancing crystallises IL and adds gas/slippage; its superiority over passive positions is not conclusively proven. Single-sided (Zap) still ends two-sided — IL still applies. Hedged (delta-neutral) LP reduces directional variance but does not remove IL/LVR (arXiv Mar 2026, optimal hedge ratio in practice 50–70% under liquidation constraints).
- **Memecoin/new pools on BNB:** no trustworthy study measures how often fees cover IL + rug risk for BNB memecoin pools specifically — that rate is unproven. Thin TVL means one trade can move price 2x–10x (IL spikes); 24h volume spikes cannot be annualised; LP holds two opposite risks at once (token moons → pool sells the winner; token crashes → pool buys the loser, −68.4% of capital if the pair token falls 90%). Rug/pull, owner dumps, minting, changeable tax, honeypots are binary losses IL math does not cover.
- **Small capital on BSC:** gas is *not* the main barrier — BSC standard gas 0.05 gwei, a full deposit–claim–withdraw cycle costs on the order of a few US cents, so gas is <1% even for a tens-of-dollars position. The real small-capital costs are IL (same % regardless of size), slippage/price impact entering and exiting thin pools, and token tax.
- **Checklist before LP (from the report §6):** fee APR from volume / *active* TVL (not total TVL), split fee (apyBase) from incentives (apyReward), compare fee APR against IL under sideways / moderate-trend (2x) / stress (5x, −90%) scenarios, verify LP lock/burn + expiry on-chain (BscScan, not the project site), and screen mint/tax/honeypot/blacklist/pause/owner control via scanner *plus* on-chain confirmation. A high headline fee APR is a question, not an answer — a 2026 preprint found fee-APR-ranked pools had the worst net returns in its Uniswap V3 sample.
- **What is explicitly unproven (report's own section):** no BSC/PancakeSwap LP profitability study; no measured success rate for memecoin-pool LP; rebalancing superiority unproven; "4000x capital efficiency" for V3 is a theoretical maximum for narrow stable ranges, not an expected result; no documented native single-sided PancakeSwap product found.

## What changed today (2026-11-05) — new, user-specific LP evidence

None of this changes the research conclusions above, but each item is a live application of the checklist to pools and products the user actually touches. All of it was already reported to the user in main chat today (see Already Covered in Main Chat), so it is preserved here for the next study, not as new Letter material.

- **AGC LP substance check (reported 2026-11-05 ~11:39 WIB, main chat):** the "whale" holding 13.13% of AGC supply is not a free wallet — it is a PinkLock contract (verified on-chain, Sourcify exact_match), holding 2 locks totalling 9,222,950,000 AGC (4.2B locked until 2027-11-02; 5,022,950,000 vesting from 2026-12-03). After excluding the locker, the largest non-pair wallet holds only ~1.69%. LP burn is 53.59% to the dead address; the remaining ~46.38% of LP is held by the minter contract, whose source was read: `withdrawLP` only redeems the caller's own Mode B position after 14 days — no `removeLiquidity`/rescue path, so LP cannot be pulled unilaterally. This is the report's "substance over score" test applied live: the Clarus-style ≥95% burn/lock gate fails on paper, but the unilateral-withdrawal question is answered no.
- **BURN LP (reported 2026-11-05 ~15:02 WIB, main chat):** LP is 100% dead-burn, verified on-chain — no one can withdraw liquidity at all. Token 0x7De1606230AA70802caeCF1A3e90039A6265B1c4, pair PCS V2 0x53895464c524c6fDD82aD5189bF92D9b798c6a51; GoPlus clean, tax 2%/2%, Binance audit riskLevel 1 with no hits.
- **AGC Mode B LP redemption estimate (from chunk 3 handoff, told to the user 2026-11-05):** at pool conditions read ~08:57 WIB (pool AGC/WBNB 0xE56041..., reserves ~10,489,042,154.91 AGC + 163.7807 WBNB, total LP 1,264,883.01), user positions pos0 LP 6.900705 and pos1 LP 9.256809 were estimated at unlock (17 Nov and 19 Nov 2026) at ±57,224.1 AGC + 0.000894 BNB and ±76,762.1 AGC + 0.001199 BNB — total ±133,986.2 AGC + 0.002092 BNB ≈ $2.81 (AGC $0.000009813, BNB $715.77) vs 0.004 BNB (~$2.86) principal for those two positions. I.e. LP roughly returns principal before withdraw gas; the locked reward (2,654,755.15 AGC total across Mode B at that time) is the profit part. Estimate only, at same pool conditions — LP value moves with the pool.
- **Syra / Meteora LP skill — studied, not adopted (reported 2026-11-05, main chat):** Ikhwanhsn's Grok Bot LP MCP skill (Solana + Meteora) was read read-only. Verdict unchanged: real functioning product, but wrong chain (Solana, project is BSC-only), zero performance data in the skill, and a custodial catch — the skill creates a Solana wallet whose keys are held by the Syra server (api.syraa.fun); the private key is not exportable via API, only via a Telegram bot after binding; funds are withdrawable only to one payout address set once. Transferable only: preview-before-execution and a short-lived confirmation token — already used. Nothing installed, nothing run, no SOL sent.
- **Meteora "RABBIT TIGHT STRAT" post (@magersih, reported 2026-11-05 00:42 UTC, main chat):** claim of 30 SOL → ~567 SOL in under 3 months via ultra-narrow (≤20 bin) ranges held under 3 minutes. Not applied: Solana/Meteora, wrong chain; claim unverified (summary of someone else's article, no contract address or on-chain proof); contradicts the LP research's aggregate finding unless executed with automation and infrastructure the user does not have; and LP deployment is not an authorised execution scope.
- **Five new methods adopted 2026-11-05 ~18:46 WIB (reported in main chat, `message:assistant-msg-94689368-d89a-68f0-9102-5dc4cb7372db`):** DeFade bundle/dev forensics (free core, read-only, live test on AGC + Grok Bot still running at report time — results not yet in this note); BscHouse "How to Find BSC Gems Early" metrics (positive deployer track record — 3x 10x+ without a rug; top-10 holder bands in the first 5 minutes: <25% healthy, 25–40% risky, >40% trap; LP/market-cap ratio healthy 2–5%, <1% practically unexitable); PolyRob Treasury Trading skill installed as method only; Quant-Lab bake-off validation methodology (coin-flip control + hold benchmark + bootstrap CI); Solana Screener forward-return ledger. None of these changed any live gate, schedule, or execution scope.

## Tentative new application — LP/market-cap lens on the user's own pools (not yet told to the user)

This is a first-pass computation from today's live figures, marked tentative because the BscHouse 2–5% band was written for screening *new* gems, not for judging pools the user already trades, and because both figures are snapshots.

- AGC: liquidity ~$254,700 (reported 2026-11-05 ~16:19 WIB) vs market cap ~$788,500 → LP/MCAP ≈ 32%.
- BURN: liquidity ~$87,000 vs market cap ~$380,000 (reported 2026-11-05 ~15:00 WIB) → LP/MCAP ≈ 23%.
- Both sit far *above* the BscHouse 2–5% "healthy" band — i.e. unusually deep liquidity relative to market cap, so entry/exit slippage for the user's small sizes should be low. That does not make either pool a good LP candidate: the binding question remains the report's breakeven test (fee vs IL on a trending memecoin), and AGC's claim emission keeps selling pressure structural. Next study should verify these ratios fresh and check whether the band even means the same thing for a mining-emission token before using it as a screen.

## Prerequisite check

- Prerequisites in place: the user has the full research report and the summary page with the interactive IL calculator (calculator verified: 2.00x / $10,000 / 3% fee → HODL $15,000, LP $14,142, net −$558); the user holds live LP-relevant positions to learn from (AGC Mode B LP, AGC/BURN trading pools); the user already corrects the assistant's screening standards from experience (PinkLock correction, mining-coin sell-pressure correction, degen-standard correction on 2026-11-05).
- Gaps to close first: (1) no BSC-specific LP profitability study exists, so any "LP beats HODL" claim for a BNB pool is an extrapolation, not evidence — the user must be told this before any sizing discussion; (2) the user has not yet stated a decision rule for LP (which pool type, what size, what exit) — retrieval and practice below must not assume one; (3) DeFade live-test results on AGC/Grok Bot were still pending at the last report — do not cite a DeFade score until it lands.

## Retrieval prompt

From memory, without re-reading the report: state the core idea of RISET PENYEDIA LIKUIDITAS in your own words — what must be true for an LP to beat simply holding — then check it against the worked example below. The check is: fee (+ incentives) − gas − other costs > IL, with IL from the price ratio at exit.

## Worked example

Scenario (from the report §2.2, generic BNB/stablecoin pair, not a recommendation): deposit $10,000 = $5,000 BNB + $5,000 stablecoin into a PancakeSwap V2 pool.

1. Entry: the pool holds your $5,000 + $5,000; you receive LP tokens proportional to your share.
2. BNB rises 2x (r = 2): arbitrageurs buy the "cheap" BNB out of the pool until the pool price catches up. The pool has sold winners and bought losers automatically.
3. Exit value before fees: LP position $14,142 (IL = 2√2/(1+2) − 1 ≈ −5.7% vs HODL). HODL of the same assets would be $15,000. Shortfall: $858.
4. Breakeven: fees collected must exceed $858 (8.6% of starting capital) just to match HODL. At V2's LP fee share (0.17% of volume), that needs sustained volume/TVL — e.g. at 10% daily volume/TVL, fee APR is only ~6.2%/year, so one 2x move nearly wipes out a year of fees.
5. If BNB instead falls 50% (r = 0.5): IL is the same 5.7% ($429 shortfall vs HODL $7,500), and the LP position is $7,071. If the pair token falls 90% (r = 0.1): IL vs HODL is 42.5%, but the absolute loss is 68.4% of starting capital ($10,000 → $3,162).
6. Lesson to state back: the LP can be up in dollars and still lose to HODL; the correct comparison is always vs HODL at the same exit price, never vs starting capital. And if the price returns to the entry ratio, IL is zero — "impermanent" only means "reversible if price returns", not "will return".

## Practice task

One small, low-load item, no funds involved. Take the AGC pool the user already watches: (a) write down today's liquidity and market cap from DexScreener, compute LP/MCAP; (b) write down the fee the pool would pay on $100 of volume at V2's 0.17% LP share; (c) pick one price scenario (sideways, 2x, or −50%) and compute the IL shortfall on a hypothetical $100 position using the table in the worked example; (d) state in one sentence whether the fee in (b) could plausibly cover the shortfall in (c) over a week at current volume. Immediate feedback after each step: (a) check the ratio against the tentative 32% computed above — a large gap means stale figures, re-read them; (b) $100 × 0.17% = $0.17 per $100 of volume is the *pool-wide* fee, the user's share is that times their share of active liquidity — forgetting the share step is the common error; (c) 2x → 5.7% of the HODL value, i.e. ~$5.70 on $100; (d) if the answer is "only if volume stays at spike levels", that is the correct sceptical answer — 24h volume cannot be annualised.

## Feedback rubric

Task- and process-focused only; no praise, shame, or overload. Name what was correct (e.g. compared vs HODL, used the LP fee share 0.17% not the 0.25% headline, used active TVL), then name the single most useful next adjustment (e.g. "next time, separate fee from CAKE incentives before judging the pool" or "re-check the volume figure as a multi-week average, not 24h"). Do not turn a correct computation into a recommendation to enter any pool.

## Transfer challenge

One real situation in the user's life where this applies: the user already holds AGC Mode B LP positions (pos0 unlock 2026-11-17, pos1/pos2 unlock 2026-11-19) whose LP value at unlock was estimated at roughly principal before gas. Before those unlock dates, apply the breakeven test to the *actual* position: locked reward already claimed via the 4-hour claims + LP redemption value at unlock vs what the same BNB + AGC would have been worth held. That is the first real LP-vs-HODL measurement the user will have — record it when it happens, do not pre-judge it now. A second situation: any future moment when a new memecoin pool tempts an LP entry — run the §6 checklist (volume/active TVL, IL scenarios, lock/burn + expiry, token screens) before any sizing talk.

## Confidence check

Ask the user to rate confidence (1–10) after doing the retrieval prompt, then compare it to performance on the worked example: if confidence is high but the IL figure or the fee-share figure is wrong, the gap is the lesson (usually: using the 0.25% headline fee instead of the 0.17% LP share, or comparing vs starting capital instead of vs HODL). Record the rating and the actual errors; do not adjust mastery from a single attempt.

## Support implications for Muse

- Keep this goal research-only. Never present the report, the calculator, or any checklist result as authorisation to provide liquidity; execution needs a separate explicit user order.
- When the user asks about LP for a specific pool, run the report's checklist in order and report each leg's result plainly; a high fee APR is a question ("why is it high — thin TVL? spike volume? high LVR?"), never a green light.
- Watch for the AGC Mode B unlocks (2026-11-17, 2026-11-19) as the user's first real LP-vs-HODL data point; offer to measure it then, unprompted only as a measurement, not as a trade.
- Watch the DeFade live-test results (AGC + Grok Bot) when they land; a bundle score is a second opinion on coordinated supply, never a replacement for the sellability/round-trip checks.
- Do not revive dropped topics in this goal's name (PoEFE/Robinhood, AgentID ETH, BNBS) — the user ordered those forgotten on 2026-11-05.
- Language: the user works in Indonesian; keep LP material in Bahasa Indonesia, with the English terms (impermanent loss, fee APR, TVL) kept as-is.

## Open questions

- Does the BscHouse LP/MCAP 2–5% band mean anything for mining-emission tokens like AGC, or is it only a new-gem screen? (Tentative application above; needs a fresh read before use.)
- What were the DeFade live-test scores for AGC and Grok Bot? (Pending at last report, 2026-11-05 ~18:46 WIB.)
- What is the user's decision rule for LP — pool type, size, exit — if any? Not yet stated; do not assume.
- No trustworthy study exists for BNB memecoin-pool LP success rates. This stays unproven until one appears; do not fill it with anecdotes.

## Already Covered in Main Chat

- User created the goal on 2026-11-04 and ordered research-only LP study from trustworthy sources, separate from BACOT DEGEN (`message:assistant-msg-ca2d2987-6f40-4ce7-9de2-6da6d1fe44b8` is the assistant's acknowledgement; goal created 2026-11-04T17:56:36Z).
- Main agent told the user the research's headline findings on 2026-11-04T18:03:35Z: aggregate LP loses vs HODL (Loesch $199.3M fees vs $260.1M IL; Bitquery only 34% beat HODL after gas), IL 2x = 5.7% / 5x = 25.5%, $10,000 / 2x example (HODL $15,000 vs LP $14,142, $858 to break even), BSC gas not the barrier, and no trustworthy BNB memecoin LP study exists.
- Main agent told the user the summary page with the interactive IL calculator was built, verified, and delivered (goal update 2026-11-04T18:07:19Z; calculator check 2.00x / $10,000 / 3% fee → HODL $15,000, LP $14,142, net −$558).
- Main agent told the user on 2026-11-05 that the AGC 13% "whale" is PinkLock (not dumpable), LP burn 53.59% with the minter holding the rest under a no-unilateral-withdrawal design, and that BURN LP is 100% dead-burn.
- Main agent told the user on 2026-11-05 that the Syra/Meteora LP skill was read and not adopted (Solana, custodial keys held by the Syra server, no performance data) and that the Meteora "RABBIT TIGHT STRAT" post would not be applied.
- Main agent told the user on 2026-11-05 ~18:46 WIB that five new methods were adopted, including DeFade bundle forensics and the BscHouse LP/market-cap and holder-band metrics (live DeFade test results still pending at that report).
- User has not asked for an LP execution, position, or sizing decision in the recent conversation; no LP funds have moved.

## Research Trajectory

- *External sources viewed* (all opened and read in full for this study; the report itself was the prior study's work, re-read today):
  - Riset Edukasi LP report (deep-research agent, 2026-11-04) — `workspace/research_notes/riset-penyedia-likuiditas-untung-20261104-1757/report.md` — the 8-question report: V2/V3 mechanics, IL math, Loesch + Bitquery evidence, strategies, memecoin pools, checklist, small-capital BSC reality, risks. Re-read 2026-11-05 for this note; figures quoted above come from it.
  - PancakeSwap Docs, Liquidity Pools — https://docs.pancakeswap.finance/earn/pancakeswap-pools — V2 0.17% LP fee share, V3 tiers and manual fee claims (via the report, accessed 2026-11-04).
  - Binance Academy, Impermanent Loss Explained — https://www.binance.com/en/academy/articles/impermanent-loss-explained — IL formula and table, constant-product mechanics (via the report, accessed 2026-11-04).
  - Loesch et al., "Impermanent Loss in Uniswap v3", arXiv:2111.09192 — http://arxiv.org/abs/2111.09192 — fees $199.3M vs IL $260.1M (via the report, accessed 2026-11-04).
  - Bitquery, "Uniswap v3 LPs Earned $42M in Fees and Still Lost $20M" (revised Oct 2026) — https://bitquery.io/investigations/uniswap-v3-lp-returns — 34% beat HODL after gas (via the report, accessed 2026-11-04).
  - Uniswap Developers, Liquidity Overview — https://developers.uniswap.org/docs/liquidity/overview — V2 vs V3 mechanics (via the report, accessed 2026-11-04).
- *Prior trajectories reviewed*: chunk 1–3 handoff for this run (2026-11-05T12:08:10Z compaction) — LP research baseline, AGC Mode B mechanics and unlock estimates, Syra/Meteora readings, five-method adoption; chunk 4/4 main-chat evidence — AGC/BURN LP checks, scalp rounds, and the 18:46 WIB methods report. Prior study notes for this goal: none exist (empty `agent_notes/` directory, verified by listing and grep).
- *Scaffolds and support tactics*: assigned study task plan for this goal (teach mode, novice band, tentative evidence) — prerequisite check, retrieval prompt, worked example, practice task, feedback rubric, transfer challenge, confidence check, next review 2026-11-06T12:08:11.096341490Z. No category-scaffold registry entry was consulted beyond the plan; no learning-style claim is made anywhere in this note.
- *Connected user data*: goal record via `user_goal.get` (`goal_2da9e3ed9aff` — state, timeline, briefing history: no prior briefings); goal workspace `workspace/goals/riset-penyedia-likuiditas/GOAL.md` (scope, boundaries, delivery record); no connector data (wallet, calendar, or device) was needed for this research-only goal. AGC/BURN figures cited are from main-chat reports already verified on-chain by the main agent, not re-read here.
- *Image references checked*: none.
- *User context and memory*: `MEMORY.md` (LP research delivery, AGC/BURN scalp context, dropped topics); memory search on "RISET PENYEDIA LIKUIDITAS LP impermanent loss" (`memory/2026-11-04.md#L4238`, `memory/2026-11-05.md#L308`, `memory/2026-11-05.md#L477`–`L479` — goal creation, report completion, summary-page delivery); `~/dreams/alignment/derived/ALIGNMENT_SYNTHESIS.md` (user is a careful BSC collector; research-only scopes; latest word honoured).
- *Searches skipped or unavailable*: no fresh web search was run — the 2026-11-04 report's sources are one day old and the topic's evidence base did not move today; a fresh search would not change this note. The `muse.context_fetch` conversation query for LP terms returned the window head (bounded output saved to `/tmp/jarvis-tool-output-8lYK8L.txt`); the LP delivery messages were located in that saved output by grep (lines 153–156) rather than in the truncated inline view.
- *Repetition search (required before ruling)*: grep over `workspace/goals/riset-penyedia-likuiditas/agent_notes/` and `workspace/goals/riset-penyedia-likuiditas/briefs/` for keyword variants "penyedia likuiditas", "liquidity provider", "impermanent loss", "LP BNB" — zero hits in both directories; both directories are empty (no prior notes, no prior briefs). Filename listings of both directories were also checked — no titles to overlap. The search therefore returned nothing to rule against, but the recent-conversation check (above) does rule: the Letter's centre was already delivered in main chat.
