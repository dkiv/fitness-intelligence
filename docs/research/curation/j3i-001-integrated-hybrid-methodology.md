# Fitness Intelligence — J3I.1
## Consolidated hybrid training methodology integration

**Revision:** 0.1 · 2026-11-25  
**Status:** AI-assisted integration candidate; pending independent methodology and scientific review where applicable. Not a registered J1 method, operational rule, or athlete-approved prescription.  
**Scope:** E4 generalized planner design for an initially single-user experienced recreational hybrid athlete. All examples are synthetic.  
**Repository:** <https://github.com/dkiv/fitness-intelligence> · read-only snapshot [`1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf`](https://github.com/dkiv/fitness-intelligence/commit/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf).

## 1. Executive summary

M01, M02 and M03 are complementary parts of one coaching method. The athlete and M02 decide what matters, what is protected, and what can change. M01 and M03 supply bounded domain-specific prescriptions and alternatives. One planner validates and places the combined week, records its rationale and seals it for approval. The approved prescription and subsequent actuals are distinct objects. The coach reviews the result, not a hypothetical readiness state.

**Recommendation:** adopt a single candidate integration profile, `J3I-HYBRID-0.1`, for review. Retain familiar exposure as the starting point; progress only for an identifiable goal or approved weekly intent. Support ordinary easy running and strength repetition/load progression first. Permit concurrent upper-body and running progression when independently justified and jointly feasible. For competing lower-body/running demand use the conservative default; include a narrowly scoped optional `J-EASY-SMALL` exception, disabled unless separately reviewed and explicitly present in the approved block. Do not implement arbitrary weighted workload, injury-risk, fitness or fatigue scores. Keep higher-complexity operators optional, not blockers for the initial coach.

Key decisions:

- Consolidate 55 parameters into common history/review settings, role-specific operators, block envelopes and a few athlete choices. Keep all original identifiers traceable; do not require 55 preferences.
- Use a single eligibility and provenance projection with action-specific predicates. A batch attestation can confirm identified completed Hevy working sets without changing the imported facts or pretending all sets have measured RPE. Running rep completion and measured rep pace remain different evidence.
- Keep three separate anchors: initial approved block baseline (cumulative bounds), approved predecessor (positive change bounds), current eligible actual reference (credible capacity). Add a non-increasing carry-forward ceiling when resuming below earlier work; do not create a new baseline from a missed session or a new week.
- Resolve the inconsistencies in the original examples and definitions in §7. Choose **two total eligible Q0 exposures**, not an initial exposure plus two additional repeats; introduce a specific run/walk increment; distinguish target effort from execution cap; treat nominally unchanged new weeks as proposals requiring approval.
- Calendar search reports its domain and whether it was exhausted. If a safety conflict exists, a familiar hold is not an acceptable fallback. No hard commitment may be silently relaxed.

### Source baseline and boundaries

The exact local predecessor documents were opened and read, not reconstructed from prior chat summaries:

| Candidate | Source archive and SHA-256 | Key sections |
|---|---|---|
| M01 0.1 | `fitness-intelligence-j3b-001.md`, `8d25b228e109036e9524e7b2a91599ba712737d766cceaf3d57aaf906172d3c5` | §§3–8, W1–W7, §10 |
| M02 0.1 | `fitness-intelligence-j3b-002.md`, `ee81af3b755d81cd352894126b78c9fe5a7f12f8bbf1b492a7f368c05c5b3347` | §§3–8, programs A–C, §10 |
| M03 0.1 | `fitness-intelligence-j3b-003.md`, `45382b0df18ff2ea3ca857df42f86542c6f9dd44657765c5fbd275ca5b756915` | §§3–8, programs A–D, §10 |

Pinned [curation index](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/docs/research/curation/README.md) includes M01/M02 (PR #27 merged); it ends with the J3A.3 handoff, not a staged M03 review. Use the delivered M03 local archive as the candidate, not an assumed merged record. The original archives and evidence revisions remain intact. This document specifies recommended integration deltas, not silent supersession. References to Packets 005/008/009/010 follow the predecessor methodologies' observation-aware framework; no new publication appraisal was undertaken.

## 2. Integrated method responsibilities

| Component | Owns | Consumes / produces | Must not do |
|---|---|---|---|
| M02 | Objective ranking, block archetype/horizon, initial allocation between disciplines, exposure/outcome contracts, weekly intents, baseline and protection, revision/transition | Current context + shared eligible-history summaries + domain proposals → proposed block and permitted envelopes | Prescribe detailed running intervals independently of M03 or strength progression independently of M01; assert maintenance from counts |
| M01 | Specific movement/group selection, load/reps/effort/rest, sets and local adjustments, strength-specific evidence gate | M02 intent and envelopes + actuals → bounded typed strength candidates (including hold/reduce) | Change objectives, delete protected run, allocate entire calendar, approve |
| M03 | Running-specific starting reference, role/purpose, intensity anchor, steps and intervals, duration/frequency/quality/intensity operators, local adjustment | M02 intent and envelopes + actuals → bounded typed running candidates | Expand approved envelope, infer intervals from instructions, delete protected lift, approve |
| Joint planner | Candidate combination, discrete equipment, calendar placement, time and cross-boundary checks, simultaneous-change validation, deterministic selection, explanation and exact proposal | Context, approved block, local alternatives, common constraints → valid candidate(s) or named conflict/search limit | Override a restriction or silently renegotiate a goal; approve on behalf of athlete |
| Trusted command/persistence layer | Owner isolation, context and observation versions, immutable proposal/receipt, effective dates, correction lineage, stale checks, history replay | Exact sealed candidate and athlete's trusted decision | Generate physiological predictions or mark evidence approved |

**Initialization handshake:** M02 chooses desired allocation and outcome contract. M01/M03 each determine credible starting task structures and limits from actuals, including conservative introductory alternatives. The joint planner checks feasibility; M02 returns alternative allocations if it cannot fit. This is one bounded iteration over candidate choices, not a circular dependency or three solvers. For a new block, M02's proposed baseline is its exact initial approved nominal week, not the historical dose or a future aspiration; validate before approval. M01/M03 may decline numerical initialization when the starting reference is not credible.

Implement shared operations once: owner-scoped as-of snapshot, identity/units/coverage and comparison eligibility, outcome classification, feedback/attestation handling, reference selection with domain-specific predicates, objective and protection checks, baseline/predecessor arithmetic, typed delta classification, calendar search, rationale construction, review routing and approval. Domain methods contribute predicates and operators, not duplicated storage or approval paths. Each comparison names its task, purpose, role and required facts; a single generic numeric eligibility score cannot replace these.

The common block contract is a conceptual extension of M02, not a new schema mandate. For each objective retain stable key, ranked priority or unresolved tie, development/maintenance role, outcome/task and comparable reference, review opportunity and athlete-defined acceptable functional tradeoff; exposure commitments are separately specified by movement/run purpose, quantity and cadence; distinguish fixed dates from movable purposes. Specify floors/ceilings, restrictions, equipment, windows, phase intent, positive-change limits, initial and predecessor references, enabled operators and joint profile, method/evidence versions. Every protected outcome has separate adherence and outcome review; a missed exposure is not automatically a lost outcome and an unmeasured outcome remains unknown. A floor constrains proposed prescriptions, not the athlete's right to stop.

## 3. Common observation and execution contracts

### 3.1 Separate provenance from decision eligibility

| Layer | Minimum and use | Forbidden inference |
|---|---|---|
| Descriptive actual history | Valid owner/source, active support, units, dates and deduplicated identity. Keep inferred and confirmed counts separate; distinguish time conventions and estimated quantities. | Ended workout with positive reps proves actual working-set execution; absent import means no training |
| Initialization | Credible recent representative actual exposure, relevant task/load convention, current regime/restrictions, available schedule. Athlete report can corroborate selected history; uncertain imported history can prompt conservative familiar option, not unqualified exact capacity. | Peak historical PR or general athleticism sets current dose; old peak is safe on return |
| Positive progression | Action-specific demonstrated task execution, current target/role, relevant tolerance/context, credible current approved comparison and objective rationale. Apply local operator predicate; confirmed facts must cover the dimension being progressed. | Session-completed flag proves every set or interval; nominal instruction proves achieved pace; missing RPE equals low effort |
| Outcome review | Comparable actual task protocol, baseline/follow-up, conditions, measurement convention, exposure/coverage and relevant counterevidence. | Completion proves effectiveness, stable e1RM proves muscle retention, faster easy pace proves VO2max/economy |

Track execution for each elapsed logical slot: `completed`, `partial`, `missed` (explicitly known), `unknown`. Record actual work and deviations even when not compliant. A slot can be completed while a particular measurement is missing; a partial slot may supply valid actual sets/minutes but not a full success gate. Unelapsed slots are excluded. Adherence reports known-outcome coverage = known / elapsed, completion = completed / known; report unknown and partial explicitly. Neither denominator is imputed when zero. Summarize unplanned actual exposure separately; do not double count linked and imported activities. A confirmed missed session creates no repayment debt. A completed session outside target/cap is not a positive success merely because work was done.

**Eligibility ordering:** ownership, as-of availability and active source support → valid identity and measurements → relevant current context and task equivalence → specific actual/effort requirement → recency and stable tie-break. Filter before examining whether outcomes improved. Retain exclusions, denominators, context, uncertainty and multiple observations when conflicting. Use occurrence time for history ordering and matching the in-force approval; use availability/recorded time for what could have been known. A late observation can support today's decision but cannot enter a prior replay. A correction or tombstone invalidates current support; historical pinned facts remain reproducible and annotated. Recheck materially relevant source support at approval even when totals are numerically identical. Source correction is separate from scientific claim withdrawal: both can block a pending proposal, but they have different identifiers and reasons.

### 3.2 Low-burden targeted confirmation

Proposed minimal interaction: show 2–3 selected recent comparable workouts (date, mapped exercise/equipment, ordered working sets and values, provenance), plus a collapsed representative-week summary. Ask one scoped question: “Are the displayed working sets actual completed sets, with the listed reps and weights? Exclude anything not completed or not recorded correctly.” Athlete may attest selected workouts together, select exclusions, or answer uncertain. If a broad weekly report is all that is needed for initialization, ask instead for representative actual frequency/dose and relevant interruptions, without insisting on per-set confirmation. Do not prompt for all history or repeatedly confirm unchanged snapshots.

A batch affirmation expands into an immutable evidence attachment to **the exact displayed observation revision/content and relevant set identities**, with owner, confirmation time, scope, affirmative/excluded/unknown members, confirmed fields (completion only or completion + rep/load), actor, and context if supplied. It is distinct from the provider row. Never write provider completion timestamps or change `completion_inferred` to false. Report e.g. “imported/inferred, athlete-confirmed actual” for supported members. A workout-level blanket yes without a known set list confirms the outing, not ordinals; it cannot satisfy all-set progression. Changed child identities, movement mapping or values invalidate affected attestations until explicit reconfirmation; unchanged observations can reuse current support. A historical attestation need not match an approved slot if none existed; if a slot is claimed, explicitly attribute it to its in-force revision and time. No date/title auto-link. Confirmation is not approval of a plan.

For running, valid activity summary can establish actual outing time/distance for descriptive history and attributed continuous exposure. Athlete can confirm “all 3 × 6-minute work reps, two recoveries, last rep controlled, no unusual leg issue” once for the session; this is an attestation of structure and tolerance, not measured per-rep pace. An optional measured lap/time-distance source aligned to each rep can support pace decisions. Instructions, aggregate splits and whole-session HR cannot stand in for achieved reps. Do not ask for precise lap measurements when the only candidate is a familiar easy hold or controlled work-duration increase.

Ask only when the missing answer would change feasible options. Examples: “Were those sets performed?” for a possible rep increase; “Was the run conversational and did your next squat feel normal?” for a long-run extension; “Did you finish all work reps?” for quality duration; clarify pain/restrictions promptly. If no answer, choose a safe credible hold, reduction, or defer numeric advice, **after safety check**. Optional recovery observations can qualify a concern but cannot supply missing execution or clear restrictions.

### 3.3 Action-specific positive gates

| Operator | Minimum candidate support | Missing/contradictory fallback |
|---|---|---|
| Strength rep/load | Whole affected group actual ordered reps/load confirmed; correct variation and role; 2 comparable nominal successes without adverse context if RPE-free, or 1 strong fully confirmed manageable effort-aware success for ordinary familiar work (prefer 2 near limit); fixed-rep load or variable-rep all at top before load/reset; goal justifies change | Hold/ask; local reduction when difficulty clear; no numeric load transfer from unknown convention |
| Strength set trial | Representative actual weekly counts, ≥3 eligible exposures across ~2+ weeks, adequate opportunities yet insufficient progress for goal, confirmed tolerance and capacity for specific extra stimulus | Maintain productive dose; clarify poor adherence rather than add sets; no MRV diagnosis |
| Easy duration | Two confirmed comparable current-role outings, duration and completion, credible manageability (speech/effort/brief feedback), representative weekly exposure | Repeat credible familiar task; HR not mandatory |
| Long duration | Same plus actual recent long-task tolerance, subsequent relevant lower-body response and distance novelty/context | Hold or shorten; ask if recent long exposure cannot be bounded |
| Quality duration/count | Two confirmed current-structure completions including actual work durations/count and controlled effort, relevant next-session tolerance; aligned pace not necessary | Repeat only familiar structure or ask; no upward inference from instructions |
| Pace increase | Above quality gate as applicable, plus measured achieved pace at comparable conditions, effort, objective, current anchor; no automatic pace rise | Effort prescription or hold, not guessed pace |
| Frequency | ≥2 representative weeks at current frequency, actual tolerance, feasible redistribution, maintained protected purpose | Keep frequency; no free extra session |
| Run/walk fraction | Two comparable current pattern completions with actual running/walking durations and manageable response, representative exposure | Hold pattern or walk earlier if needed |
| Q0 entry | Separate gate and envelope (§4), current easy tolerance, explicit objective and joint review | Remain easy, no permanent bar to later introduction |

All positive gates also require no material unresolved local/general difficulty, valid current context, authorized method and operator, and joint validation. A scheduled intent is not evidence of execution capacity; it does not bypass a gate. A narrower explicitly reviewed phase/role gate may be used, with exact provenance. Safety reductions do not require two successes or quantified readiness. These proposed gates must not change the existing E1/E3 synthetic confirmation predicate.

## 4. Consolidated numerical configuration

### 4.1 Recommended profile, not athlete questionnaire

Use one reviewed default profile plus typed block-specific overrides. P = programming judgment; C = practical convention; E = engineering safeguard. None of the numerical defaults below is an empirically established optimum, minimum maintenance dose or safe physiological threshold. Empirical premises are separately cataloged (§10). Override requires a named reviewed configuration, credible context and athlete approval of the affected block; a tighter existing restriction always wins. Missing actuals never grant extra headroom.

| Configuration group | Recommended starting value | Scope, required facts and fallback |
|---|---|---|
| History H (P/C/E) | 3–4 representative completed weeks (prefer recent 28 days); 2–3 task exposures, most recent representative anchor; extend to ~56 days for low-frequency stable tasks with reason | Actual relevant dose, continuity and conditions; retain median/range and structure, not average incompatible weeks. After interruption re-anchor; one credible reference supports repeat, not trend. See §3. |
| Block horizon (P/C) | 6 weeks, ordinary range 4–8; midpoint ~3, end ~6; one detailed upcoming week, at most one provisional successor initially | Event, goal, time and context; review at next comparable exposure, every week, immediately for restriction or material correction. Shorter/longer when warranted. No mandated deload/taper/test. |
| Initialization/protection (P) | Preserve familiar productive actual dose; meaningful familiar task exposure opportunities at habitual cadence; retain secondary dose initially | Actual role, objectives, feasible allocation; reduce optional work for a reason; no universal frequency or percentage minimum. Example discretionary −1–2 sets or ~10–20% running only with suitable context and authorized alternative, not retention rule. |
| Strength reps (P) | Heavy/technique: +1 total eligible rep per movement review when variable, otherwise fixed reps and load branch. Moderate/accessory: same conservative default; optional uniform +1 each across **one** group of 2–3 sets (≤3 total) only as named role setting, demonstrated manageability, no other per-set/set rise | One group; preserve set ordinals and approved range. Reset to lower end after load step, fixed groups unchanged. For E4 first release use +1 total only; uniform variant is a reviewed convenience, disabled by default. |
| Strength load (P/E) | Smallest positive equipment step ≤2.5% upper, ≤5% lower, relative to exact predecessor; no minimum increment. Block cumulative ≤105% / 110% of initial group nominal, fixed rep envelope | Known discrete equipment total load and comparable group. Apply both caps and endpoints. No rounding up. If step unavailable, reps/hold; named explicit movement override if justified. Not a capacity estimate. |
| Strength sets (P/E) | +1 weekly set ≤floor(25% × predecessor count); movement ceiling initial +2 for each developing movement; aggregate ceiling initial total +2/week. Secondary count normally unchanged; −1 affected set initially if warranted | Check movement and aggregate separately, local role/time and actuals. At 1–3 sets no default rise. Set increase cannot combine with positive load/reps on same movement; after increase ≥2 comparable exposures and ≥1 completed representative week before another, aim ~2 weeks. |
| Strength effort/rest (C/P) | Heavy 7–8.5 / 3–5 min; moderate 7–8.5 / 2–3; technique 6–7.5 / 2–3; accessory 7–9 / 1–2. Explicit execution cap default 9 for familiar heavy/moderate/accessory if approved, 8 technique; block can tighten | Anchored set effort (not session RPE); target and cap separate. ~1 point shift is contextual flag only. If effort missing use §3 gate. Reduction: −1 affected rep or smallest decrement aiming ~2.5–5%, approved rest change, larger reduction/defer when needed. |
| Running initial role (P/C) | Familiar structure; low-history credible 2×15–20 min easy/run-walk as illustration, not mandatory floor. Easy RPE 2–4 conversational; recovery easy 1–3. Long familiar easy, no fixed fraction | Current running-specific exposure/conditions; no general athletic ability transfer. Unknown baseline → ask or familiar shorter option. No HR required. |
| Running quality (P/C) | Familiar cruise 2–3×5–8 min, RPE 6–7, 2–3 min between; sustained 12–20 min if familiar. Faster familiar 3–5×1–3 min at 7–8, roughly equal easy recovery where suitable. Usually one quality session in established 3–4-run hybrid week when relevant; majority easy purposes | Preserve actual familiar dose (may be lower or different); no compulsory threshold session. Work effort targets, separate explicit caps chosen for the task (default upper end for Q0 6, controlled 7, faster 8). Above target prompts slow/convert/stop as appropriate; not a physiological threshold. |
| Running time/long (P/E) | One ordinary easy OR long +≤5 min; weekly rise ≤min(600 s, floor(0.10 × predecessor seconds)); cumulative W0+20 min, long L0+10 min. Long +10 per review only explicit role exception, still weekly/cumulative caps | Two manageable role exposures, weekly context; inspect prior 30-day actual max distance if covered, flag novelty, no Frandsen-derived cap. Use integer seconds; smaller feasible step or hold. Distance-primary envelopes separately validated, no conversion from time to exact distance. |
| Frequency (P/E) | +1 easy outing, redistribute time initially (weekly time unchanged); cumulative F0+1; ≥2 representative weeks at current frequency | Preserve meaningful tasks and session floor; account for altered starts, time and fatigue. No combined quality rise. Unknown coverage → hold. |
| Run/walk fraction (P/E, new) | At fixed session elapsed and weekly total, replace ≤2 min walking by running per review in one familiar session, also ≤10 percentage points of that session's duration; choose uniform 15–30 s increments where practical. Cumulative +≤4 run min per named session AND +≤20 points relative to its initial fraction, unless explicitly reviewed. Count actual running separately from walking | Two confirmed manageable pattern exposures; both caps checked, minimum planned walking recovery respected. Example 4×(3 min run +2 walk) → 4×(3:30 run +1:30 walk) at 20 min (includes final walk); 12→14 run min, 60→70%. Never simultaneously extend elapsed time, increase intensity, or introduce quality. No forced removal of final walk. Crossing to continuous role requires separate reviewed transition. |
| Quality work rise (P/E) | +≤2 total demanding min, ordinarily +1–2; uniform 30–60 s changes or +1 familiar rep only when work cap fits. Cumulative D0+4 min for established work; count recovery changes in W; quality count stays fixed. Optional role-specific +3 only separate review | Confirm actual work structure, effort, tolerance. No pace measurement needed for duration branch. No intensity or reduced recovery simultaneously. Preserve warm-up/cool-down. |
| Pace/role change (P) | No automatic faster pace. Optional ≤5 s/km faster at fixed work/recovery/effort cap with current aligned measured reference and explicit envelope; effort-only controlled role transition separately reviewed | Missing reliable pace/HR → effort or hold. Different zone systems stay separate. HR optional, not suitable as short-rep governor. |
| Q0 entry (P/E) | ≥3 representative manageable easy-running weeks, ≥6 outings, ≥2 comparable continuous 25–30 min conversational tasks or reviewed equivalent. Start 10 easy +3×2 controlled at 5–6 +2×2 easy between +10 easy =30 min, 6 work min, replaces familiar 30-min session. Explicit entry envelope; **two total** eligible Q0 exposures then review, not automatic transition | Current tolerance, relevant next strength/run response, objective and no material restriction/unknown. No other positive lower-body or running axis at entry. Shorter reviewed structure if credible; otherwise wait. After two Q0 exposures can hold or explicitly transition at same duration/count/recovery to controlled role if authorized; new role then needs its own evidence before progression. |
| Joint profile (P/E) | Default `J-DEFAULT` (§5); optional `J-EASY-SMALL` disabled unless reviewed and block named | No generalized “one sport per week” rule, no hidden netting. Both independent eligibility checks and joint review. |
| Calendar/review (P/C/E) | Review prior/next 2 local days, neighboring week/block boundaries; only explicit spacing. Warm-up 10–15 and cool-down 5–10 min for quality as suitable; count all recoveries, rests, route/setup (e.g. 5 min if credible) | Use actual time/equipment and worst permitted endpoints; expand window for event/dense sport. Actual elapsed UTC for spacing. Review one adverse observation promptly, two comparable adverse observations → explicit protection review, sooner for material conflict. Not statistical threshold. |
| Local reduction/re-entry (P/E) | −5–10 min affected run or −1 work rep, familiar easy substitution if permitted; strength reduction above; material interruption selects credible familiar submaximal work and less exposure | Reason, retained actuals, symptoms, tolerance and availability. No mandatory restart percentage; stop/defer if safety uncertain; floor conflict requires block revision. |

### 4.2 Exact traceability crosswalk: all 55 predecessor parameters

This compact registry is the review checklist; §4.1 supplies concrete defaults. “Retain” preserves the substantive rule with shared representation, “revise” specifies integration delta, “restrict” narrows authorization, “defer” leaves optional advanced behavior unavailable in E4's first useful profile. No empirical record or original archive changes.

| ID | Integrated home | Disposition / difference |
|---|---|---|
| N01 | History H | Retain 2–3/28 days, justified 56-day extension |
| N02 | History H / anchors | Retain ordered actual vector, separate predecessor and baseline |
| N03 | §3 gates | Revise low-burden scoped attestation; effort-free branch unchanged in substance; E1 frozen |
| N04 | Strength reps | Revise role-specific optional uniform moderate/accessory progression; +1 default, fixed heavy unchanged |
| N05 | Strength load | Retain upper 2.5% exact maximum |
| N06 | Strength load | Retain lower 5%; joint exception tighter 2.5% |
| N07 | Strength load / validator | Retain exact discrete equipment, no upward rounding |
| N08 | Strength reps | Retain lower-end reset, one group, role floor |
| N09 | Strength effort/rest | Revise explicit target/cap separation and group scope |
| N10 | Strength effort/rest | Retain ~1 point flag only; cap breach is distinct |
| N11 | Local reduction | Retain one rep or smallest suitable decrement, safety first |
| N12 | History H | Consolidate 3–4 weeks actual counts |
| N13 | §3 gates | Retain set-trial gate; no increase from completion alone |
| N14 | Strength sets | Retain +1 and 25% floor; low-count exception explicit |
| N15 | Strength sets | Retain next exposure/weekly, 2 exposures +1 representative week before further rise |
| N16 | Calendar/review | Consolidate ±2 days and adjacent boundaries |
| N17 | Calendar/review | Consolidate next exposure/weekly/immediate review |
| B01 | Block horizon | Retain 6 weeks ordinarily 4–8 |
| B02 | History H | Consolidate actual representative weeks |
| B03 | History H | Consolidate 2–3 current references |
| B04 | Initialization | Retain familiar productive actual dose, no peak reset |
| B05 | Protection | Restrict secondary reduction to explicit justified allowed alternative; no minimum retention claim |
| B06 | Protection | Retain familiar task exposure opportunity at agreed cadence |
| B07 | Strength operator bounds | Revise references to integrated N04 profile, tighter joint bounds |
| B08 | Strength sets | Retain movement +2 cumulative, baseline pinned |
| B09 | Strength load | Retain 105/110% provisional per-group cap; role-specific explicit alternatives |
| B10 | Strength sets | Retain independent aggregate +2 |
| B11 | Running envelope | Revise via explicit new block envelope plus reviewed M03; otherwise hold familiar |
| B12 | Joint profile | Revise ambiguity into J-DEFAULT and optional J-EASY-SMALL; no implicit adoption |
| B13 | Local reduction/re-entry | Consolidate; safe stop and re-anchor |
| B14 | Block horizon | Consolidate weekly, mid/end and immediate |
| B15 | Calendar/review | Retain material adverse evidence review, repeated protection review |
| B16 | Calendar/review | Consolidate spacing and exact UTC/time arithmetic |
| B17 | Outcome review | Retain comparable assessment opportunity, optional max |
| B18 | Block horizon | Retain rolling one upcoming week, provisional nonauthority; new week approval |
| R01 | History H | Consolidate weekly actual history |
| R02 | History H | Consolidate task reference and recency |
| R03 | Running initial role | Retain low-history contextual option |
| R04 | Running initial role | Retain easy/recovery effort anchors |
| R05 | Running initial role/time | Retain familiar long and separate ceiling |
| R06 | Running quality/Q0 | Revise Q0 total-exposure interpretation; separate entry envelope |
| R07 | Running quality | Retain familiar faster roles, optional later operator |
| R08 | Running quality | Retain familiar demanding count, Q0 counts, no automatic addition |
| R09 | Running quality | Retain majority easy intent; separate session, work-time and HR denominators |
| R10 | Running time | Retain min absolute/relative administrative cap and smaller increments |
| R11 | Running time | Restrict novelty flag to context; no injury prediction |
| R12 | Frequency/run-walk | Revise add explicit run/walk fraction rule; frequency redistribution unchanged |
| R13 | Quality work | Retain uniform practical change, count recoveries, +2 default |
| R14 | Pace/role | Restrict measured pace rise to eligible aligned data; defer automatic pace in first E4 |
| R15 | §3 gates | Consolidate action-specific confirmations, no blanket telemetry |
| R16 | Local reduction | Retain stop/defer, floor conflict |
| R17 | Running cumulative | Retain W0+20, F0+1, L0+10, D0+4; Q0 own ceiling |
| R18 | Joint profile | Revise B12 integration and exception authority |
| R19 | Review/Q0 | Revise “two repeats” to two total eligible exposures; shared next exposure/weekly |
| R20 | Calendar/review | Retain exact recovery count and bounded time |

### 4.3 Configuration versus preferences versus invariants

Athlete chooses goals/ranking, meaningful protected task and tradeoffs, assessment preference, available windows, equipment, exercise preferences, and whether an independently reviewed optional profile is acceptable. Coach proposes a coherent configuration; athlete approves the actual block, not dozens of sliders. Role-specific targets, cumulative ceilings and per-review operator sizes are reviewed programming decisions with contextual overrides. Owner isolation, immutable lineage, exact arithmetic, nonnegative units, no unapproved mutations, current restriction recheck, explicit search exhaustion and no provenance laundering are engineering invariants, not configurable preferences. Empirical premises supply rationale only when reviewed and eligible, never parameter magic. A shorter maintenance block may use zero positive ceilings; dense running-emphasis may protect specific familiar squat loading and limit lower-body rises; sparse/re-entry history may use smaller time/rep increments and no quality until eligible. Do not allow a preference to loosen a safety rule.

## 5. Constraint and joint progression policy

### 5.1 Ordered validation and three distinct references

All hard constraints are conjunctive: order determines rejection and explanation, not which hard constraints may be waived. A safer action may still require block revision rather than violating an exposure floor. Report relevant conflicts, not merely the first if multiple can be established. Proposed evaluation order:

1. **Safety and authority:** owner and current context, new restriction or concerning symptom, affected task. Stop/defer affected work; seek appropriate professional guidance when warranted. No unsafe familiar hold, no override through athlete preference. Check whether safe unaffected work remains possible.
2. **Current context:** versioned goals, availability, equipment, event/date changes and preferences. A newer context invalidates a proposal that depends on the old one; reconcile before use. Fixed event dates and actual availability are hard. Do not move an event without explicit context revision.
3. **Block identity and protection:** exact approved (or proposed-for-approval) block version, phase, protected dates/purposes, agreed exposure floors/ceilings, outcome commitments and escalation conditions. If the proposed change needs to alter them, route to explicit block/context revision; actual performance cannot be guaranteed by a validator.
4. **Operator authorization and evidence eligibility:** reviewed method/rule version, approved profile and operator, current actual reference, required confirmation and purpose. A missing prerequisite blocks a positive change, not necessarily a safe repeat or reduction. Reviewed empirical dependencies must be eligible for operational reliance; otherwise separate reviewed judgment-only option or defer.
5. **Per-review bounds:** exact approved predecessor, affected nominal targets and permitted endpoints, equipment increments, one-group/one-axis rules. No stacking scheduled and adaptive positive changes; all deltas from predecessor count together. Multiple revisions to the same upcoming week must not ratchet per-review bounds: retain the original eligible predecessor at the opening of that review until a fresh actual review permits a new increment. Revisions within it consume the same budget.
6. **Cumulative bounds:** exact initial approved block baseline, movement/group and aggregate limits and role-specific running limits. Check independently of step caps. New calendar week or amended future schedule never silently reinitializes them.
7. **Joint-change policy:** classify every positive change, including changed execution ranges and coupled effects, without hiding an increase behind a decrease elsewhere. Reject unauthorized combinations.
8. **Equipment and calendar feasibility:** discrete options, worst permitted endpoints, durations, rests, setup/route, fixed purpose/date, all affected weeks and boundaries, explicit spacing. Validate exact times and resource restrictions. If cannot prove feasible, do not seal.
9. **Soft preferences:** only rank feasible candidates, with objective order, relevant uncertainty, adherence practicality and simplicity. A soft preference is not a hard veto unless athlete explicitly makes it one and the context is revised.

Let `I` be the pinned initial approved nominal vector, `P` the review's approved predecessor vector, `H` the eligible actual task reference(s), and `C` the candidate. Each vector contains the applicable role-specific quantities (not a scalar workload). `I` and `P` must have stable mappings to candidate role/movement/group and units. `H` constrains positive eligibility and credible initialization, not the numerical cap denominator. A candidate can be below the initial baseline, and its next eligible rise remains bounded by the smaller of the applicable predecessor and cumulative limits. Never substitute an actual missed set, failed rep or unknown run for `P` or `I`.

For a familiar positive-load group with upper/lower cap `p` and cumulative multiplier `k`, enforce `C.nominal <= min(P.nominal*(1+p), I.nominal*k, absolute_block_ceiling)` and `C.high <= min(P.high*(1+p), I.nominal*k, absolute_block_ceiling)` for a rise in that endpoint. Apply the cap even if another endpoint is unchanged; verify absolute and cumulative limits for all endpoints, including unchanged values. If `I.high` is greater than cumulative nominal-based ceiling, initial envelope itself must be corrected before approval; do not retroactively invalidate an old fixture. Exact discrete equipment grid and rounding down for upper bounds. For nonpositive/unknown external loads, percentages do not supply a valid numeric progression; use a separately reviewed task-specific convention or defer. Analogous positive checks apply to reps, counts and running time, on nominal and endpoint vectors. Respect all minima for proposals. Sum maximum sets/reps/time for simultaneous permitted options unless an explicitly enforced alternative constraint makes them mutually exclusive. Effort is an instruction; its cap is not a measurable guarantee of execution.

**Numeric examples:** upper-body I=80 kg, P=80, per-review +2%=1.6 if block tightens to 2%; default 2.5%=2 kg; cumulative maximum 84. A 2.5 kg step is invalid under either per-review cap. At P=83, default max=min(85.075,84)=84; only a feasible grid value ≤84. If P.high=84 and nominal remains 83, raising high to 85 is still invalid. If an athlete completes 75 instead of planned 83, 75 is evidence of current execution, not a new initial baseline or additional allowable gain. Review reason and capability; do not progress on shortfall. If an explicitly approved reduction lowers P to 75, the next discretionary rise is ≤76.875 under 2.5%, still subject to H and I; a faster restoration requires explicitly reviewed resumption policy, not automatic use of 83. Re-entry may preserve I or tighten the old ceiling; a genuinely new block or explicit material baseline revision needs documented rationale, credible actual H and approval. No revision solely to evade a cap; retain prior pins and show the reset's material effect.

Sets: initial priority press 8 and squat 6, total 23; predecessor press 9/squat 6/total 24. Individually +1 each fits 25% and each movement ceiling, but total would be 26 >25, reject combination. Removing a discretionary accessory may make total feasible only if its own purpose/floor and other rules permit; cannot bypass the movement ceiling or hide the two positive changes. Three weekly sets cannot become four under the default 25% rule (floor(0.75)=0).

Running: W0=140 min, P=155 min; ordinary weekly cap min(10,15.5)=10, but cumulative W0+20=160. One +5 ordinary easy fits; +6 does not (role +5, cumulative +5). At Wp=40 min, +5 fails weekly +4; 24+20=44 is eligible only with appropriate actuals. At 44 min weekly ceiling +4.4 (264 s); no round to +5. A missed long run is not 75 minutes of spare dose. With a reduced approved week, re-anchor on its actual relevant role before positive progression. In multiweek plans per-review budget follows the actual review sequence, not number of approvals; no prospective accumulation of unearned weekly increases.

### 5.2 Running envelope amendment and joint policy

**B11:** familiar-running hold remains the authorized behavior of an existing block unless (i) M03 method/operator and its configuration are independently reviewed and operationally authorized and (ii) athlete approves an explicit new M02 envelope. Reserved time (e.g. +10 minutes in M02) is not permission. Envelope includes F0/W0/L0/D0 and predecessor, frequency min/max, primary time or distance convention, individual session and long-run bounds, demanding count and actual work minutes, run/walk fractions if applicable, allowed role/intensity references and caps, per-review/cumulative limits, protected dates/purposes, permitted combinations and reassessment. Optional distance hard bounds must be enforceable at worst endpoints (otherwise constrain route/distance stop or conflict). Q0 gets a separately approved entry D ceiling, not automatic +6 from zero. A new envelope can enable reviewed future operators; it never constitutes approval of unspecified future workouts. Existing fixed running blocks remain unchanged until revision is approved.

**B12 integrated profiles:** classify each positive delta by movement, role, group, dimension and local burden; running axes include ordinary easy time, long time, frequency, run fraction, demanding duration/count/entry, pace/effort, reduced recovery or novel role. Work-duration increase mechanically adds total time and sometimes recovery; those coupled quantities must fit all caps, but are not independent operators. Frequency redistribution is a positive axis even at unchanged total. Upper/lower-body classification must reflect actual movement role (ambiguous multi-joint or local involvement → conservative classify or clarify). Positive strength reps/load are group-specific; sets are separate. For E4 initial profile default at most one positive lower-body group or one lower-body set trial per review, not a physiological limit. Upper-body progressions can coexist within movement/aggregate/time rules; keep changes small and purposeful.

| Combination | J-DEFAULT | Optional narrower exception / restriction |
|---|---|---|
| Upper-body rep/load + easy, long, frequency or quality | May combine if independently eligible, time and all protections fit, no material generalized difficulty | No automatic combination; upper-body set trial needs own rationale and aggregate cap; avoid extra set/per-set rise same movement |
| Ordinary easy duration + positive lower-body group | Choose one by objective; hold other | `J-EASY-SMALL`: only one ordinary easy session +≤5 min AND one familiar lower group +1 total rep OR smallest step ≤2.5%; two manageable exposures per role, representative joint history, no unresolved fatigue/secondary concern, no sets, no other positive running/lower axes, no effort-cap increase. Both caps and endpoints. Explicit reviewed profile and approved block required |
| Long extension, quality duration/count/entry/intensity, run fraction or novel density + positive lower-body | Reject default | Larger planned combinations deferred from first E4; independent coaching review, named exact coupled limits, actual history, explicit block authority before later consideration |
| Frequency redistribution + lower-body rise | Reject default even if weekly minutes unchanged | Later reviewed combination possible, not J-EASY-SMALL; time/starts/protection matter |
| Lower-body set increase + any running positive | Reject default | No exception in initial profile; reducing unrelated work does not change classification |
| Hold/reduce in one + positive other | May be feasible | Reduction must have justification and preserve hard commitments; possible deterioration of secondary outcome may require holding primary progression too |
| Productive hold both | Always a candidate when safe and feasible | New week still needs approval; no forced change |

Do not let an explicit athlete approval alone authorize an unreviewed combination. A jointly feasible candidate can be selected only after both independent domain predicates and joint profile pass, not after each method independently selects its favorite. If equal-ranked goals present meaningful tradeoffs, present alternatives with no fabricated preference. No arithmetic physiological workload score; this is an explicit conservative change-control policy. Review primary-specific benefits and costs, not arbitrary weighted utility.

### 5.3 Calendar domain and conflict semantics

Define finite search domain up front: exact candidate operator variants, logical slots, eligible local availability windows, allowed start grid (e.g. 5-minute grid as engineering convention with exact fixed starts separately included), equipment, placement/order options and any pruning proven sound. Include rest, warm-up, transitions/setup and longest allowed prescription duration. Check neighboring weeks and reserved future boundary windows; compute actual elapsed spacing from timestamps in correct IANA zone with ambiguous/nonexistent local instants handled explicitly. Only approved spacing constraints, not universal recovery hours. If a feasible candidate found, report that result; if search limited, don't claim optimality. If no candidate and fully exhausted, say “infeasible within stated domain” with exact named conflicts and requested versus available values; if stopped early, say “no feasible candidate among examined options; search incomplete,” offer broadened authorized domain or review. Do not equate discrete grid exhaustion with infeasibility of every continuous start time. Safety conflicts or contradictory hard bounds may be established directly without enumeration (explain proof). Protected date vs purpose: a movable run can shift within allowed future windows, but a fixed event cannot; no silently deleted purpose, floor or date. An approved execution choice explicitly representing alternative windows is distinct from a changed dated calendar proposal. E4 first useful profile need not support arbitrary alternative-window execution; use explicit moves with approval.

## 6. Integrated review workflow

1. Freeze current owner, time, context, approved head/block, evidence/rule versions and available observation support. Check new restrictions/symptoms, event and availability first. An incompatible active plan is preserved as history but flagged for review; stop/defer affected work, not automatic deletion or forced compliance.
2. Review elapsed logical slots and relevant unplanned activity (other sports included as context, not run mileage or equivalent strength sets). Report actual exposure, coverage, completion among known, deviations, relevant tolerance. Compare prescribed with actual, not assigned with assumed achieved. Identify omitted versus partially performed work and why if known.
3. Select task-specific actual references and compare strength/running separately: same variation/load convention/role, load-rep-effort and set order; same run purpose/duration/route/conditions/time convention and effort/valid HR where available. A relative improvement is observed performance, not proven physiological adaptation. Assess protected outcomes independently of adherence and each other. Long capability is not VO2max, squat retention is not hypertrophy, completion is not retention. Use observed improvement/deterioration, stable within available resolution, mixed or insufficient comparable evidence, not an invented personal MDC. A meaningful adverse observation prompts immediate clarification/local review; two comparable adverse observations prompt explicit protection review (not a statistical test). Unobservable secondary outcome remains unknown; maintain its agreed exposure, seek feasible assessment when needed, avoid progression that relies on an unverified protection claim.
4. Identify local versus generalized difficulty. Local legs sore after heavy lifting and easy run difficult → examine nearby sessions and actual effort, preserve unaffected upper work if safe. Temporal proximity is not causal proof. Generalized difficulty → clarify illness, stress, fueling, sleep and schedule where actionable; consider coordinated reduction or M02 review rather than one-metric cancellation. Optional verified HR/recovery data can refine, never replace current task evidence. HRV with unverified units/window is descriptive only. No readiness score.
5. Examine previous decisions and subsequent responses with Packet 009 context: recent actual dose, prior similar block, supporting and contradictory observations. A previously productive pattern is a candidate, not proof of cause or fixed athlete capacity. After travel/interruption, classify calendar loss, actual exposure loss and capacity uncertainty separately; skip missed work, re-anchor from retained actuals, choose credible conservative re-entry, no automatic restoration or repayment. Restrictions unresolved → defer affected work.
6. Decide whether current objective and envelope remain valid. Productive both → hold or specific justified reviewed increase; no forced specialization. Poor adherence → ask about time/preference, simplify or move; do not diagnose insufficient training stimulus. Repeated protected difficulty, incompatible floor/date, new priority or stale capacity outside envelope → explicit M02 review. New objective/availability/restriction needs current context revision as appropriate. End horizon → assess comparable outcomes if available, consider continuation/extension/transition/recovery; no compulsory maximal test/deload. An extension is not an automatic extra approved week; block dates and appropriate baselines must be explicit.
7. Generate local alternatives and jointly validate (§5, §8). Compare objective relevance and protected risks, present rationale, uncertainty, rejected options, coverage and exact changes. Retain current productive components. Do not optimize physiology.
8. Seal a new exact prescription for any new week or changed future prescription and obtain trusted athlete approval. Already approved same dated week unchanged: read-only review, no new approval required. Newly generated week with same nominal targets is still a new dated prescription, requires approval. Decline leaves head unchanged (flag current conflicts); no silent activation. Record actuals and review next comparable exposure/weekly, mid/end or earlier as appropriate.

| Action category | Authority / record |
|---|---|
| Read-only interpretation, targeted question or stop advice | No prescription mutation; safety guidance may be immediate |
| Execution flexibility | Already approved discrete choice/range; actual attributed to original prescription, deviations retained; stopping always allowed |
| Local future dose or calendar change | Exact weekly proposal, same block only if all contracts and dates permit; athlete approval |
| Changed envelope, protected purpose/floor, dates of block or phase, extension/transition | Explicit M02 block revision; validate affected future weeks and show tradeoff; approval |
| Changed goals, priority, restriction, material availability or athlete preferences | Current context revision through trusted athlete input; invalidate stale proposals; corresponding plan/block review and approval if affected |

**Future nutrition and recovery interface:** a later method can provide session fueling opportunities, reported intake context and relevant health restrictions; it must not infer energy availability/glycogen from weight/calorie summaries or convert wearable expenditure into automatic calorie compensation. Recovery observations can enrich task-specific feedback and coordinated adjustment, not silently mutate prescription or become universal progression prerequisites. Both consume the same context, approval and review workflow. Clinical concerns or unresolved safety restrictions take precedence; specialized nutritional/medical decisions require qualified review. Defer advanced physiological estimation here.

## 7. Resolved inconsistencies and remaining decisions

The following are recommended integration amendments, not edits to predecessor documents. Sources: curation index implementation-review questions, M01 §§4/7/10, M02 §§6–10 (especially program B), M03 §§3–8/10 and program D. Independent reviewers should accept/revise this bundle rather than reapprove 55 isolated settings.

| Issue | Disposition | Smallest change and rationale |
|---|---|---|
| M01 +1 total rep | Revise | Keep as first-release default for all roles; allow named moderate/accessory uniform +1 per set (one 2–3-set group, ≤3 total) only if reviewed. More convenient but larger work change. Heavy fixed reps unchanged; no rep rise after all sets at top without authorized load/reset. |
| Equipment step > percentage cap | Retain | Reject that step; smaller discrete step, rep option, hold, or explicit movement-specific revised profile and block. Never round up or call display rounding an exception. |
| Historical Hevy confirmation burden | Revise | Scoped batch attestation (§3) binds exact observations and fields; inferred provenance retained; no mass upgrade or requirement to confirm irrelevant old sets. Existing E1 predicate unaffected. |
| Group vs session effort deviation | Revise | Apply set cap/target to actual group and ordinal. A backoff deviation blocks progression of that group; another group may progress only if its own gate passes and deviation is credibly isolated (e.g. time-only missed accessory, not generalized fatigue). Unresolved same-movement high effort, pain, widespread difficulty or repeated deterioration blocks positive progression across related groups until reviewed. Session RPE cannot mark individual cap breaches; targeted clarification if material. |
| Cumulative load ceilings | Restrict | Retain 105/110% baseline-based defaults for first profile, not a requirement to reach ceiling or individual capacity. Permit tighter/specific reviewed group caps. Stable identity required for mapping; novel movement no inferred baseline. |
| Aggregate and movement set ceilings | Retain | Both initial +2 limits enforced independently; role-specific alternative later only after review. No summing independent movement allowances into aggregate permission; no low-count rounding exception. |
| M02 worked program B RPE 9 | Revise | Original target 7–8.5 alone does not establish cap violation. Recommend explicitly set execution cap 9 for familiar squat if independently approved; RPE 9 then meets cap but exceeds target, triggers hold/clarification with actual repeated high effort. RPE >9 would exceed cap. If a reviewer explicitly sets cap 8.5, RPE 9 is a cap breach. Do not retroactively imply the missing cap existed. |
| Q0 exposures vs repeats | Revise | M03 §§3.4 and program D say two eligible Q0 exposures, R19 says two repeats. Interpret as two total (initial + one repeat), both manageable plus relevant subsequent response and representative week; then review, not automatic advancement. A stricter three-exposure profile is possible after interruption/uncertainty. |
| Run/walk fraction | Revise | Explicit bounded operator in §4.1, not an unlimited change hidden under unchanged total time. Preserve actual running and walking ledgers, recovery and role. Transition to continuous separately reviewed. |
| Safety before hold | Retain / restrict | Every fallback passes safety and feasibility. If restriction conflicts with familiar work, stop/defer and identify protection conflict, even if old plan approved. |
| New-week approval | Revise | Clarify that continuing unchanged within already approved dated week is read-only; generating new week always seals and requires trusted approval even if nominal prescription identical. Future intent and planned increases not session authority. |
| Calendar bounded search | Revise | Record domain, examined choices, limit, sound prunes and completeness. No proof of infeasibility from incomplete search. Distinguish named hard contradictions from searched infeasibility. |
| Interval arithmetic | Retain / clarify | Explicit final recovery flag or expanded steps. For n reps of work w and between recovery r, total = warm + n*w + (n−1)*r + cool; if final recovery included, n*r. Current `Intervals` repeats every listed step including last recovery. Encode e.g. repeat work/recovery n−1 times then last work separately, or flat steps. Never shrink recovery silently. |
| Combined progression authority | Revise | J-DEFAULT + optional J-EASY-SMALL. Profile review + operational authorization + explicit M02 block amendment + exact week approval are distinct gates. No implicit replacement of B11/B12 or stacking individually valid changes. |
| Planner fit | Restrict | Extend existing types/commands via versioned new policy, not three new engines or replacing E1/E3. Generalized block, stable task identities and arbitrary weeks require implementation, not assumed. |

**Additional implementation-review decisions:** adopt time-primary running initially, effort-based sessions and optional measured pace review; defer automatic pace/HR-based progression, quantitative zones/HRV, novel recovery-density operators, flexible multi-block transitions beyond a documented versioned basic successor, and complex top/backoff coupling until justified. Provide basic group representation even if first progression operator supports only ordinary straight groups. Recommend independent coaching review of the proposed ceilings, one-lower-group default, uniform-rep option, Q0 gate, run/walk operator and J-EASY-SMALL before enabling them. Review whether aggregate set budget is too restrictive in actual use; prospective usefulness, adherence and protected outcomes matter more than maximizing increases.

## 8. Deterministic candidate procedure

Conceptual pseudocode, not executable application code or a new persistence API. Same frozen input and configuration produce equivalent semantic output (stable tie-breaks only among genuinely equivalent options). No private provider data used in these fixtures.

```text
review_or_generate(owner, request, as_of, expected_head):
    S = owner_scoped_snapshot(as_of, expected_head)
    check_identity_context_and_authority(S)
    safety = check_current_restrictions_and_concerning_feedback(S)
    if safety.affects_requested_work:
        return stop_or_defer_affected_work_with_conflicts_and_safe_alternatives(S)

    goals = current_confirmed_goals(S.context)
    if priorities_unresolved_and_material: return clarify_tradeoff(goals)
    H = project_eligible_history(S.observations, S.attestations,
                                 occurrence_cutoff=as_of, availability_cutoff=as_of)
    review = classify_actuals_and_outcomes(S, H)  # coverage + adherence + comparison
    block = S.active_block
    if request.new_block or review.requires_block_revision:
        options = M02.propose_contracts(goals, H, review, current_context=S.context)
        # M01/M03 give credible starting reference and local alternatives for each allocation
        if contract_change_not_authorized_yet: mark_options_as_block_proposals()
    else:
        options = [block]  # do not enlarge current contract

    candidates = []; diagnostics = []; search_records = []
    for contract in stable_order(options):
        if not safe_current_contract(contract, S.context): continue_with_conflict()
        I = pinned_initial_baseline_or_candidate_initial_week(contract)
        P = pinned_review_predecessor(S, contract)  # fixed through retries/revisions
        # New block initialization isn't an adaptive rise on old P. Validate starting dose
        # from H and document material change; no cap-evasion reset.
        L = M01.enumerate_local_alternatives(contract, H, review, I, P)
        R = M03.enumerate_local_alternatives(contract, H, review, I, P)
        # Include credible safe holds/reductions; no mandatory increase; if B11 unchanged,
        # R cannot expand running. Unsupported numeric reference -> clarify/defer.
        for pair in bounded_product(L, R):
            delta = classify_all_positive_and_negative_axes(pair, P)
            if not independent_action_gates(pair, H, review, contract): reject_with_reason()
            if not check_step_bounds_and_cumulative(pair, P, I, contract): reject_with_reason()
            if not check_all_protection_and_joint_profile(pair, delta, contract): reject_with_reason()
            placements, search = finite_calendar_search(pair, S.context, contract,
                                                        neighboring_intents_and_weeks=S.neighbors)
            search_records.append(search)
            for week in placements:
                # Validate full final combined candidate, not separate methods only.
                if full_validate(week, S, contract, I, P, H, delta):
                    candidates.append(week)
                else: diagnostics.append(named_conflicts)

    if not candidates:
        if material_missing_facts: return targeted_question_or_safe_defer(diagnostics)
        if hard_contradiction_proven or all_domains_exhausted(search_records):
            return named_infeasible_with_explicit_block_or_context_alternatives()
        return no_feasible_found_search_incomplete(search_records, diagnostics)

    ranked = compare_feasible_by_confirmed_priority_and_specificity(candidates)
    # Productive hold is preferred unless change has objective-directed justification.
    # Protect secondary commitments; prefer manageable/adherent simple choices and
    # reversible small changes. Do not rank tied goals on athlete's behalf.
    if meaningful_tradeoff_unresolved(ranked): return present_feasible_options_for_choice()
    selected = stable_tie_break_only_equivalent(ranked)
    rationale = freeze_actuals_exclusions_comparisons_coverage_and_uncertainty(
                 selected, S, H, I, P, review, search_records, rejected_alternatives,
                 exact_rule_profile_and_eligible_evidence_pins)
    if selected.same_already_approved_dated_week and no_contract_change:
        return read_only_review(rationale)
    return seal_exact_proposal(selected, rationale, expected_head, context_id,
                               observation_support_ids, block_version, policy_version)

trusted_decide(owner, proposal, decision, command_id):
    # Reuse existing owner/plan lock ordering, receipt idempotency and CAS head.
    # Check existing identical receipt first (historical retry, not reactivation).
    verify_exact_seal_and_base_context_and_current_rule_evidence_eligibility()
    if decision == approve:
        recheck_restrictions_dates_actual_support_and_full_validation()
        if stale_or_ineligible: return conflict_require_new_preview()
        atomically_record_receipt_and_advance_head()
    else: record_decline_without_head_change()

record_actual(owner, in_force_revision, logical_slot, observation, correction):
    explicitly_attribute_to_in_force_at_occurrence()
    preserve_original_provenance_and_correction_lineage()
    retain_unknown_partial_missed_completed_distinctions()
    # No automatic revised prescription or provider write.
    return read_only_review_or_request_next_approved_proposal()
```

Implementation must avoid a loophole in pseudocode shorthand: if a requested affected task is unsafe, a reduced *safe* alternative may be proposed only after safety/restriction validation, without relaxing other constraints. The stop/defer response itself is not an automatically activated calendar. Full validation also runs on an explicitly selected athlete alternative. Current evidence withdrawals and changed material observation support make new approvals stale, not historical approvals false. Replay uses original immutable pins, not current evidence or method defaults; annotate current eligibility separately. Existing command semantics govern idempotency and stale rejection, not a new rule engine.

## 9. Cross-method conformance cases

Synthetic cases; test recommendation quality as a set of defensible choices, not one magic optimum. Common required rationale: objective, current context and exact baseline/predecessor, relevant actuals and missingness, action gates and bounds, protection and calendar checks, rejected material alternatives and authority. All changed prescriptions and new weeks require approval; already approved same dated week unchanged is read-only; immediate stop advice is not a mutation. Tests below are specifications, not executed application tests.

| ID / scenario | Eligible response and required rationale | Prohibited inference / acceptance assertion |
|---|---|---|
| I01 Productive balanced: bench improving, 145 min running manageable, squat protected stable | Hold both or justify bounded goal-specific increase. Show comparable outcomes and adherence separately; seal next dated week even if unchanged. | Success requires escalation; holding means no new-week approval. |
| I02 Strength emphasis: incline 80 kg 3×6 easy enough, run 75 min protected | +1 total rep (7/6/6) or hold if productive; preserve run purpose and dose. | Reduce running automatically because strength priority. |
| I03 Running emphasis: 3×6 controlled confirmed twice, bench/squat protected | +30 s each rep at same effort if all gates; total work +90 s, time +90 s if recoveries unchanged; retain protected strength. | Quality success proves no interference. |
| I04 Upper + easy: bench +1 rep and ordinary easy 30→35, Wp=140 | May combine under J-DEFAULT with independent eligibility, protection/time. | One-sport-only prohibition, or automatic merge without validation. |
| I05 Small lower + easy: squat one +1 rep, easy +5 at Wp=140 | If J-EASY-SMALL reviewed/authorized and block named, both eligible with two manageable exposures each; otherwise choose one/hold. | Athlete approval of week alone enables optional profile; +sets or long run treated as easy exception. |
| I06 Competing demand: quality +2 work min and squat +2.5% load | Reject combined under default; rank priority, alternatives or block review. | Net reduction elsewhere eliminates classification. |
| I07 Aggregate vs movement: I total23 P24, press 9→10 and squat6→7 | Each step fits but total26>25; additionally default one competing lower-body change only relevant if more lower groups. Select one, or valid justified reallocation with own constraints. | Summed movement headroom overrides aggregate ceiling. |
| I08 Long extension + squat poorer 140×5 at RPE 9 repeatedly, cap9 target8.5 | Hold long extension despite W headroom, review squat/conditions and protected outcome; possible local adjustment or explicit revision. | RPE9 automatically exceeds 9 cap; causal running interference established. |
| I09 Q0: 3 weeks/6 easy outings, two 30-min conversational, current 60 min no quality | If suitable and new envelope approved, replace 30-min easy with Q0 30, D0→6 explicit entry. Two total manageable Q0 before role review. | +6 allowed by normal +2; current no-quality block authorizes entry; three exposures mandatory by ambiguous R19. |
| I10 Interval instructions 3×6; aggregate work split without aligned actuals | Ask if reps/durations completed and controlled; repeat familiar structure if safe. If confirmed, duration progression eligible subject to other gates; measured pace remains unknown. | Aggregate/instructions prove every interval target achieved. |
| I11 Hevy ended session positive reps, no completion times | Descriptive inferred; scoped batch attestation of exact values/sets can support new policy gate; existing fixture still holds on inference. | Rewriting provider provenance, automatic promotion of all workouts. |
| I12 Travel cancels 2 runs, squat actual retained light | Log explicit misses; conservative familiar re-entry based on credible current actuals; do not repay or restore peak automatically. | Missed work increases P headroom or establishes detraining percentage. |
| I13 New exclusion arrives before approval | Stop/defer affected task, current context invalidates candidate; no familiar unsafe hold; preserve approved history. | Athlete approval overrides restriction or late exclusion rewrites history. |
| I14 Protected hypertrophy unmeasured, lifts completed | Exposure adherence supported, hypertrophy unknown; retain commitment, seek appropriate assessment if relevant, avoid claiming maintenance. | Lifting frequency or e1RM proves hypertrophy. |
| I15 No available gym time for protected squat | If exhausted defined domain, named conflict and alternatives (date/equipment/explicit contract review). If search limit stops early, incomplete-search result. | Delete squat or claim global infeasibility from bounded search. |
| I16 Athlete changes primary 10-km to bench | Explicit context/goal revision and new block contract, retain former history, approve affected future weeks. | Local operator silently reorders priorities. |
| I17 Corrected set after proposal sealing, totals unchanged | Reject stale current approval if relied-upon support changed; fresh preview; exact old decision receipt replay allowed if already finalized. | Comparing only totals misses stale source. |
| I18 Historical replay after evidence withdrawal | Replay original exact rationale and pins, annotate withdrawn eligibility; new approval citing ineligible revision blocked. | Replace old rationale with current defaults, approve withdrawn evidence. |
| I19 E1/E3 regression: known fixture five press sets and two runs, all confirmed cap/feedback vs inferred | Preserve original 5→6 or hold, original 24h fixture spacing, prior evidence gaps and replay. New integration rules never applied retroactively. | New two-exposure gate/aggregate cap rewrites original synthetic rule. |
| I20 Discrete load: I/P80 upper, cap2.5%, equipment +2.5 only | Rep rise/hold; cap82, 82.5 invalid; if high endpoint alone raised to82.5 also invalid. | Round above bound or use stale PR. |
| I21 Repeated proposal ratchet: P80, candidate81 then amended82 then83 before new actual review | Reject 83 (original review cap82); cumulative initial84 also applies. Preserve review anchor across proposal retries. | Each approval resets per-review budget. |
| I22 Run/walk 4×(3+2) →4×(3:30+1:30) with final walk | 20 min both, +2 actual run min, +10 points; require eligible pattern and approved role; no joint duration rise. | Same total implies no demand change or no recovery after final rep. |
| I23 Recovery arithmetic: 4×1→5×1, 1 min between, warm10 cool8 | Initial 25 min; candidate27, +1 work +1 recovery. Check total and time at maximum. | Count four recoveries in four reps without final recovery, or omit added recovery. |
| I24 Group effort: successful top set, backoff exceeds cap, general leg fatigue unknown | Block backoff rise, clarify shared fatigue before top rise; isolated time-only accessory miss may allow independent unaffected group if eligible. | Average RPE hides deviation or every local issue implies systemic fatigue. |
| I25 Frequency redistribution: 2×30→3×20 with protected continuous 30 | Reject if protected 30 lost, even at 60 min. With no such floor and actual evidence, +1 may be allowed; no concurrent lower-body rise under default. | Redistribution physiologically free or protected purpose satisfied by total. |
| I26 Approved predecessor vs actual: P155 running, I140, actual partial90 | No automatic +65 to “catch up”; maintain credible safe plan or reduce, no positive rise from partial. Actual reference separate. | Actual partial resets cumulative or per-review ceiling. |

Additional transaction/integrity regression: cross-owner data rejection, stale head/context and restriction, competing approvals, exact receipt retry, observed/started slots immutable, late import across week/calendar move, source deletion and correction lineage, evidence eligibility revalidation, DST boundary and time precision, no provider writes, no future leakage, missing vs zero, stable semantic replay. Combine with existing A/C/D, M01 T, M02 B-T and M03 T cases as relevant, rather than reproducing them here. Conformance checks feasibility and quality of explanation, not physiological efficacy.

## 10. Implementation readiness and review boundaries

### 10.1 Actual repository capability at pinned main

Read-only source inspection (paths linked to exact commit). The implementation is not the generalized design described in `docs/training-plan-design.md`.

| File / capability observed | Minimum gap |
|---|---|
| [`planning/prescriptions.py`](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/backend/src/fitness_intelligence/planning/prescriptions.py): frozen `Target`, `SetGroup`, `Exercise`, `StrengthSession`, `RunStep`, `Intervals`, `RunSession`. `RunStep` uses duration+RPE; `Intervals` includes every step each repeat; `RunSession` sums low/nominal/high | Reuse typed structures. General group/ordinal IDs and explicit nominal vectors/cap versus target; run role and work/walk semantics, optional pace/HR reference tagged and dated only when needed. Do not overload session RPE into step effort. Exact endpoint validator. |
| [`planning/planner.py`](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/backend/src/fitness_intelligence/planning/planner.py): `Slot`, `WeekInputs` with `PressBlock`, `Exposure`, `WeekReview`, `_review`, `_dose`, `_schedule`, `generate_week`, `propose_move`, `change_run_commitment` | Existing fixture-specific generation and review. New versioned generic block + slots and operator enumeration; shared validator and conflict/search result. Maintain fixture rule path and replay. |
| [`db/plan_snapshot.py`](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/backend/src/fitness_intelligence/db/plan_snapshot.py): `PlanningContext`, `Generate.number: Literal[1,2]`, typed `Candidate`, snapshot and calendar projection | Arbitrary valid week numbers and versioned generalized snapshots, exact role/group and baseline links, review anchor. Separate proposed/approved block and provisional successor intent. No assumption multi-block manifests implemented. |
| [`planning/outcomes.py`](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/backend/src/fitness_intelligence/planning/outcomes.py): `Actual` manual, press-specific confirmation, `WorkingSet.ordinal`, `run_seconds`, `run_rpe`, press-only `manageable`, `SlotOutcome`, `WeeklyOutcomes` | General attributed working-group/ordinal actuals and optional scoped attestations; separate run purpose, manageability and completed work structure; optional measured aligned lap values. Current deviations compare first strength group and fixture easy-run logic; do not reuse as general group or interval adherence classifier. |
| [`db/plan_commands.py`](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/backend/src/fitness_intelligence/db/plan_commands.py): owner lock, capture context, create cycle, record outcome, weekly review, submit/preview/decide, stale checks, recorded-slot checks, rule version and evidence pins | Reuse trusted command boundary, versioned sealing/receipt/lineage, but extend validation and serialization for general payloads; inspect database migrations and transaction tests before altering schema. No new approval service. |
| Canonical data: [strength analytics](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/docs/strength-analytics.md), [endurance observations](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/docs/endurance-recovery.md), [adaptive cycle](https://github.com/dkiv/fitness-intelligence/blob/1eb7f169234b55d94a6e8c7f4d765cb3f03c4cdf/docs/adaptive-coaching-cycle.md) | Project dated owner-scoped actuals, explicit mapping, completeness and current support; Hevy inferred history marked; Garmin summaries plus athlete feedback sufficient for many initial decisions; instructions and aggregates not executed intervals. No live coverage verified. |

### 10.2 Incremental E4 sequence (proposal, not implementation authorization)

| Milestone | Deliverable and exit gate |
|---|---|
| E4.0 Contract/design freeze | Independent review of this integration and narrow profile, explicit evidence-use/operational gates, fixed synthetic fixtures, versioned request/snapshot design; inspect migrations and old replay tests. Decide scope and general block/goal representation before coding. |
| E4.1 General block + familiar week | Typed objectives, ranked priorities and protected outcome/exposure contracts, stable slot and movement/group IDs, initial/predecessor references, arbitrary weeks within block, time-primary runs and familiar strength groups. Generate one feasible first week from manual confirmed history, exact calendar/search diagnostics, seal and trusted approve using existing infrastructure. No positive adaptation yet; existing E1/E3 regressions pass. |
| E4.2 General execution and observation projection | General actual attribution, coverage and corrections, scoped batch attestation, canonical summary mapping, owner isolation, as-of snapshots and current source support; manual fallback. Read-only weekly review and comparable references; no FIT or detailed telemetry. Validate stale proposal and replay. |
| E4.3 Core local operators + joint validator | Enable reviewed hold, ordinary strength rep/load, reduction, ordinary easy duration, familiar long hold/extension if reviewed, local move; basic joint default, caps and endpoint arithmetic, no unauthorized B11/B12 change. Include actual-based positive gates, targeted feedback and explicit new-week approval. Implement `J-EASY-SMALL` only if reviewed, otherwise disabled. This is first useful integrated adaptive coach. |
| E4.4 Bounded extensions | Add set trials, frequency redistribution, run/walk and confirmed quality duration (manual count/time) plus Q0 as individually reviewed operators. Support ordinary familiar intervals as prescriptions before automatic progression; measure interval pace only if needed. General block revision/extension and successor lineage can start with explicit end-of-block transition, expand mid-block as needed; if protection conflict cannot be handled yet return explicit deferral rather than silently change block. |
| E4.5 Quality review | Golden integrated cases, fault/transaction/replay/regression tests, manual practical review of alternatives and rationales on synthetic then authorized personal use. Expand role options, arbitrary calendar flexibility, explicit coupled profiles or pace progression only where a demonstrated gap warrants them. |

A minimal planner needs a credible block, week, actuals, bounded ordinary adaptation and exact approval—not every future operator. Keep nutrition prescription, clinical return-to-training, advanced recovery/TDEE/fitness estimation, numerical readiness, FIT ingestion, automated publishing and event-specific taper optimization separate. Store only durable confirmed context, plans, actual attribution, decisions and frozen supporting facts; derive habitual summaries on demand. No requirement for a new scheduling optimizer or workflow platform.

### 10.3 Proportionate evidence, method and authorization pathway

No new scientific review was performed. All source/claim revisions remain pending as in their originating appraisal; J3I is not an evidence fragment. The J1 catalog's reviewed claim, method and release eligibility remains binding. Do not use pending citations as operational empirical support, or launder them as generic AI advice. A rule can be reviewed as explicit practical programming judgment without relying on a particular unresolved effect estimate **only if** the reviewer confirms the rule's rationale does not require that empirical premise and the project authorizes this mode; evidence gap must be shown. If the operational architecture requires an eligible reviewed method or release for that rule, defer until obtained. Existing synthetic fixture remains demonstration only.

| Decision family | Relevant pending empirical premise / exact traceability | Necessary vs independent judgment |
|---|---|---|
| Strength rep/load choice | `load-vs-repetition-progression@1`, `rpe-load-squat-strength@1`, `rpe-load-bench-strength@1`, `autoregulated-load-pooled-one-rm@1`, `predicted-rir-signed-error@1` | Need independent review before asserting these comparisons or RIR accuracy. Choice of +1 total rep, load cap/grid, two successes and no-RPE fallback are reviewable programming choices; do not assert superiority/equivalence, exact reserve, or independent corroboration of overlapping trials. |
| Maintain productive sets / set trial | `habitual-set-maintenance-strength@1` and proposed `@2`, `progressive-sets-trained-males@2`, `progressive-sets-trained-females@2`, `weekly-fractional-volume-strength@1` | Holding productive work can be a practical option without accepting unresolved Barsuhn estimates. Adding sets for a specific objective is judgment, not optimal dose inference. Any empirical claim on dose response needs its reviewed exact record. |
| Block structure and secondary protection | `periodized-vs-constant-strength@1`, `undulating-trained-strength@1`, `hift-conditioning-block-deadlift@1`/proposed `@2`, `soccer-weekly-strength-retention@1`/proposed `@2`, `young-reduced-dose-hypertrophy-retention@1`/proposed `@2`, `reduced-endurance-duration-long-endurance@1` | Six-week horizon and preservation of familiar actual exposure are programming decisions; evidence required for asserted superiority, retention fractions or transfer. No universal duration/maintenance minimum. Keep Bickel biopsy outcome and Hickson long vs VO2 endpoint distinction. |
| Joint scheduling / local fatigue | `same-session-trained-lower-body-strength@1`, `separate-session-trained-lower-body-strength@1`, `concurrent-trained-endurance-vo2max@1`, `acute-lifting-running-perceived-effort@1` | Review overlap and transfer before empirical claims. J-DEFAULT and optional small exception are explicit conservative conventions, not derived interference coefficients or mandatory spacing; no claim of demonstrated combination safety. |
| Running exposure / progression | `habitual-mileage-half-marathon@1`, `habitual-long-run-half-marathon@1`, `single-session-distance-injury-association@1`, `adaptive-running-ten-km-performance@1`/proposed `@2`, `adaptive-running-max-treadmill-speed@1`/proposed `@2` | Exact study claims need review. +5, +10/10%, Q0, run/walk and work-minute caps are independent practical choices; no injury prediction, adaptive-bundle replication, HRV necessity, or group effect as individual response. |
| Intensity and performance interpretation | `polarized-pooled-vo2peak@1`, `polarized-pooled-time-trial@1`, `intensity-classification-denominator@1`, `outdoor-five-km-typical-error@1`, `submaximal-hr-typical-error@1`, `trained-measured-one-rm-repeatability@1`, `trained-bench-relative-load-repetition-repeatability@1` | Need review to assert specific effects or error estimates; task comparability, effort cue prescription and uncertainty labeling are practical/measurement safeguards. No universal TID ratio, individual MDC or inferred lab endpoint. |

All earlier blockers preserved: Halperin full text; Barsuhn unmatched descriptive means and statistical uncertainty; Petré subgroup horizons and overlapping Huiberts/Schumann syntheses; Moesgaard abstract access/subgroups; Micke crossover/unmonitored lifting/multiplicity; Rønnestad small sample/turnover/frequency-dose confounding; Bickel recently trained population/pretraining biopsy comparator; Hickson abstract access and separate outcomes; Nuuttila endpoint denominators, exclusion, freshness, bundle, limited concurrent lifting, figure/supplement/missing-data verification; Fokkema observational associations; Frandsen complete table/supplement and causal limit; Oliveira outcome specificity; Seiler denominators; Hurst full text. Preserve exact pending revisions and original method references until separately reviewed. No comprehensive correction/retraction/rights or trial-overlap audit in this integration.

Recommended review gates, in order where dependent (some may run in parallel):

1. **AI-assisted factual appraisal** is already candidate input, not approval. Keep exact revisions, locators, limits and audit trail.
2. **Independent scientific review** accepts/revises/restricts only the empirical records actually needed for the intended operational evidence use, with exact version, transfer and rights decision. Never fabricate attestation. Do not hold practical discussion hostage to irrelevant deferred claims.
3. **Independent practical coaching-method review** of one consolidated profile: roles/history/attestation; bounds and Q0/run-walk; protection and joint profiles; review/transition and exception scope. Sports-science/qualified coaching expertise appropriate for training-method and population judgments, clinical/nutrition expertise for those boundaries. Decide which judgment-only actions can be authorized separately with explicit evidence gaps.
4. **Athlete configuration** confirms objectives, constraints, protected tradeoffs and preferences, selects among independently reviewed options. Does not confer scientific approval or override safety.
5. **Software conformance** implements versioned policy and tests exact cases/transactions/replay. Passing synthetic tests is not causal efficacy. Allow ordinary prospective usefulness review, compare simpler alternatives, monitor burden and repeated poor recommendations; no formal experiment prerequisite.
6. **Operational authorization** explicitly approves reviewed rule version, eligible release and dependency mapping, permitted actions, initial scope and fallback/withdrawal policy. Keep review and release separate as J1 requires. No auto-activation from staging this document.
7. **Specific plan approval** remains required for exact block and each newly generated/changed week through trusted athlete command. No autonomous approval, provider writes or changed past work.

**Remaining methodology work:** one narrow review pass on this profile and acceptance of the §7 amendments, with an explicit E4.0 contract and mapping of empirical versus judgment-only operators. Do not start another large literature tranche. For first useful training coach, prioritize familiar week construction, attribution, ordinary strength/easy-run bounded adaptations and joint feasibility. A subsequent compact nutrition/fueling and recovery interface review can be separate, driven by actual missing coaching decisions. Advanced models and automated delivery remain deferred.

**Limitations of this deliverable:** repository files inspected read-only at pinned main; predecessor archive hashes verified locally; M03 not assumed merged. No independent scientific review, source revision, code, migration, live provider coverage audit, actual application test execution, release, or operational authorization. Numerical settings, uniform-rep alternative, Q0 interpretation, run/walk caps, one-lower-group default and joint exception are proposed integration judgments, not empirically proven thresholds. Original archives unchanged.
