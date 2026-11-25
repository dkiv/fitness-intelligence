# Fitness Intelligence — J3B.1
## Practical resistance-training prescription and adaptation

**Revision:** 0.1 · **Date:** 2026-11-25 · **Status:** Candidate methodology for independent review. Not an approved scientific record, deployed rule, training recommendation to a specific athlete, or authorization to change a plan.

**Predecessor:** J3A.1, `fitness-intelligence-j3a-001.md`, revision 0.1, especially §§3–7 and Appendix A. **Method:** J3-M01, proposed refinement into M01a (movement prescription and progression), M01b (working-set exposure) and M01c (concurrent scheduling). These are review bundle identifiers, not registered J1 revision keys or new application interfaces.

## 1. Executive summary

A useful initial strength coach should start from the athlete's approved block, recent movement-specific performance and habitual actual exposure. It should make a small, understandable change when that change advances the objective, preserve productive work when it is already doing so, and protect the other training commitments. It should not translate every successful session into an increase, every difficult session into a deload, or every running session into interference.

**Recommended initial configuration:**

- Use the last 2–3 comparable movement exposures (normally within 28 days) and 3–4 representative completed training weeks for set-dose context. Use the most recent eligible comparable prescription/execution as the load anchor, not the highest lifetime lift. Extend the lookback only with a stated comparability reason.
- Prescribe sets, reps, load, optional anchored set RPE, rest and execution boundaries by movement and session purpose. Heavy work and technique work do not share the same progression trigger. Use recent work directly; estimated 1RM is a secondary descriptive proxy, never a required input.
- Use a deliberately conservative hybrid of planned progression and double progression. For unplanned progression, prefer one additional rep on one working set, or the smallest available load step with an appropriate rep reset. Typical proposed positive load caps are 2.5% upper body and 5% lower body, per eligible load group and relative to the approved predecessor; tighter block limits apply. These are reviewable choices, not physiological thresholds.
- Confirm two comparable successful exposures before unplanned upward progression when effort is absent or uncertain. One clearly eligible exposure with anchored effort and adequate context can justify a small planned or discretionary increase if the block permits. No inference-only record is sufficient on its own for progression. Inference can initialize a tentative reference to confirm with the athlete.
- Keep working-set counts stable when progress and tolerance are satisfactory. Test a change of one weekly movement-specific working set only for a concrete reason, within the block. Do not raise sets and per-set prescription demand simultaneously by default. A set increase is not the default remedy for stagnation.
- When local fatigue or scheduling threatens a protected run, prefer a feasible local or calendar adjustment over a whole-program reduction. Retain unaffected upper-body work. No mandatory recovery interval beyond existing approved constraints is introduced.
- Preserve the existing owner-approved plan revision, outcome attribution, frozen observation snapshot, evidence eligibility and deterministic validation/replay architecture. Any change to a future nominal prescription or its bounds needs athlete approval; a choice already inside an approved execution range does not.

The principal unresolved decisions are the scope of permitted progressions and reductions, how to initialize weakly documented movements, and how to prioritize conflicting but otherwise feasible options. The numerical configuration below is a proposed starting profile that a qualified coach can review and the athlete can contextualize. J3A.1's pending empirical claims remain pending. Existing E1/E3 rules are untouched.

## 2. Scope and scientific dependencies

### 2.1 Scope

Input: approved block and current plan head; ranked objectives, phase and protected slots; movement-specific prescriptions, bounds and restrictions; equipment increments and time budget; recent actual resistance training; relevant actual running and upcoming commitments; optional athlete feedback. Output: a hold, bounded next-prescription proposal, redistribution proposal, targeted question, defer/stop recommendation for affected work, or explicit block-review conflict. No new block construction, automatic running progression, rehabilitation, physiological readiness score, optimal volume estimator, nutrition prescription or autonomous execution is included.

A nominal prescription is the coach's future recommendation; an execution interval is a previously authorized choice during a session; actual work is an observation and can differ from either. A set-level stop for pain or unsafe technique does not require permission to stop; a replacement future prescription does require review. This distinction applies to every example below.

### 2.2 Scientific dependencies and limits

No new literature search was undertaken. This document relies on the J3A.1 appraisals rather than asserting new verification. Exact pending record links are given for traceability, not operational citations.

| Evidence from J3A.1 | What it supports in principle | What it does not establish |
|---|---|---|
| Plotkin, [10.7717/peerj.14142](https://doi.org/10.7717/peerj.14142), `plotkin@1`, `load-vs-repetition-progression@1` | Both load- and rep-progression arms improved the measured lower-body outcome. Rep progression is a plausible option when load jumps are unsuitable. | Equivalence, superiority, exact rep-reset logic, optimal progression or transfer to an incline press in hybrid athletes. |
| Helms, [10.3389/fphys.2018.00247](https://doi.org/10.3389/fphys.2018.00247), `helms-rpe-loading@1`, `rpe-load-squat-strength@1`, `rpe-load-bench-strength@1` | Anchored RPE can be used for load selection in a periodized lifting program. | A uniquely effective RPE target or adjustment step. The percentage comparator included conditional progression and adjustments; actual intensity/tonnage differed. |
| Hickmott, [10.1186/s40798-021-00404-9](https://doi.org/10.1186/s40798-021-00404-9), `hickmott-autoregulation@1`, `autoregulated-load-pooled-one-rm@1` | Autoregulated loading is a plausible method; pooled estimate uncertain. | Guaranteed benefit, equivalence or an RPE-only rule. Includes Helms: do not double-count the trial or treat its two outcomes as independent replications. Velocity-loss claims are not required here. |
| Halperin, [10.1007/s40279-021-01559-x](https://doi.org/10.1007/s40279-021-01559-x), `halperin-rir-accuracy@1`, `predicted-rir-signed-error@1` | Reason to avoid treating predicted reserve as exact. | Individual agreement, correction factor, longitudinal sensitivity or a calibrated RPE threshold. Final full text not verified in J3A.1. No quantitative dependence on the pooled signed error. |
| Barsuhn, [10.1152/japplphysiol.00476.2024](https://doi.org/10.1152/japplphysiol.00476.2024), `barsuhn@1`, `habitual-set-maintenance-strength@1`; J3A.1 proposes `barsuhn@2`, `habitual-set-maintenance-strength@2` | Context for maintaining a habitual dose rather than assuming escalation is required. | Optimal or equivalent dose. Descriptive pre/post means are not matched-person changes; 55 allocated/29 completed, unequal denominators, statistical reporting uncertainty remains. Proposed revisions are not integrated or validated. |
| Petré, `petre@1`, `same-session-trained-lower-body-strength@1`, `separate-session-trained-lower-body-strength@1` | Reason to consider scheduling demanding lower-body and endurance work separately where feasible. | Universal hours of recovery, acute causal interference or direct randomized comparison of spacing. Study-level subgroups mix modalities. |

Publication notice, correction/retraction and rights checks remain incomplete as described by J3A.1. Its proposed records and transfers are not reviewed or released. Empirical relevance is distinct from eligibility for operational use. If a pending result is withheld by a reviewer, the qualitative choice to retain a demonstrably productive prescription, choose a small feasible equipment step, use feedback as context, or respect a protected calendar remains independently reviewable as programming judgment. Do not fabricate a scientific support link for that choice. A future rule must pass the separate methodology, evidence and operational gates.

### 2.3 Read-only repository snapshot

Verified `main` at [`8fd767770ebe253e55a44ac5474cb53711b37002`](https://github.com/dkiv/fitness-intelligence/commit/8fd767770ebe253e55a44ac5474cb53711b37002) on 2026-11-25 using the GitHub comparison endpoint (main against itself); same head as J3A.1. Inspected relevant sections of the following files at that SHA:

- [Canonical training plans](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/training-plan-design.md), especially lines 69–142, 187–240: prescriptions, execution bounds, proposal/approval and synthetic E1 gate.
- [E3 adaptive coaching cycle](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/adaptive-coaching-cycle.md): manual `Actual`, slot attribution, review denominators, frozen rationale, current release eligibility.
- [Strength analytics](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/strength-analytics.md), lines 32–113: identity, load convention, completion, Epley proxy, weekly volume, Hevy history profile.
- [Endurance and recovery](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/endurance-recovery.md), lines 9–65 and relevant recovery sections: canonical activity summary, performed step/split limitations.
- [Coaching evaluation](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/coaching-evaluation-design.md): golden cases, current review/approval, evidence and safety release gates.
- [Repository README](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/README.md): existing analytics milestone and workflow context.

This is a documentation-level contract inspection, not an audit of implementation classes, migrations or live provider data. No tests or code changes were made. Where current representation of proposed features is not confirmed, §10 records a gap rather than presuming an API exists.

## 3. Practical prescription methodology (M01a)

### 3.1 Prescription object and meaning

Use the existing movement and set-group representation. For each future movement, specify:

| Dimension | Candidate methodology |
|---|---|
| Movement | Stable plan-local key linked to an explicitly reviewed comparable series; variation, equipment, grip/angle, ROM or pause where material, load convention. Display name alone is not identity. |
| Purpose | Priority heavy strength, moderate-repetition development, technique/practice, accessory/support or approved assessment; indicate phase and intended adaptation. |
| Ordered groups | Warmup, top, backoff or straight working groups. Top/backoff are semantic roles; they may be represented as ordered working groups plus explicit role metadata if supported by future reviewed representation. Each working set counts once. |
| Set count and reps | Nominal positive count and per-group rep target/range. Do not treat an omitted set as zero effort or make all sets interchangeable. |
| Load | Prefer nominal comparable external load in kg internally with athlete-friendly display; explicit eligible discrete options/range. Use per-side/total or assistance convention only when confirmed. Effort-only or rep-only if no defensible external load. |
| Effort | Optional set RPE band and an execution cap when approved. Athlete should understand the anchor; no inferred RPE from completed reps. |
| Rest | Practical planned rest allowance with minimum or permitted range when relevant; count transitions and warmups in the time budget. |
| Flexibility | Approved discrete load/rep options, permitted rest and optional-set/stop policy if actually represented and authorized; changes outside those choices are deviations or future proposals. |

The progression policy compares both nominal targets and permitted maxima/minima. Widening a range is a prescription change even if the nominal value stays fixed. A candidate must fit the approved floor, ceiling, per-change bounds, exposure limits, scheduling constraints, exercise exclusions and available equipment. Worst permitted endpoints must be feasible. An effort cap is an instruction to stop/adjust, not permission to train through symptoms; a safe stop can occur outside any planned minimum.

### 3.2 Suggested prescription templates

All values are practical starting conventions, **not findings or universal optimal ranges**. They are selected within the approved objective and recent tolerable exposure; no obligation to use every template in a week. Count is per movement per session, not weekly muscle volume. The rep range is an envelope; a nominal target can be a specific rep vector within it.

| Purpose | Illustrative sets × reps | Optional anchored RPE | Rest allowance | Progression emphasis / flexibility |
|---|---|---|---|---|
| Heavy strength (priority) | 2–4 × 3–5, or top 1 × 3–5 + 2–3 × 4–6 backoffs | 7–8.5, cap 9 only if specifically approved | 3–5 min | Maintain specificity; fixed reps or narrow rep range. Small load step once demonstrated; backoffs separately calibrated. No compulsory grinders. |
| Moderate-repetition work | 2–4 × 6–10 | 7–8.5, cap 9 if approved | 2–3 min | Rep progression is natural; load increase with rep reset after top of range. |
| Technique / paused work | 2–4 × 3–6 | 6–7.5, cap 8 if approved | 2–3 min | Preserve tempo, pause, range and execution quality. Hold unless quality and intended practice stimulus are maintained; not a volume or load race. |
| Accessories | 1–3 × 8–15, optionally 10–20 for suitable movement | 7–9, default cap 9 | 1–2 min | Progress reps first; consider machine/dumbbell granularity. Lower priority accessories are first candidates for local redistribution/reduction if the athlete agrees. |

RPE 10 is the athlete's perception that no additional intended-quality repetition remains; roughly 9/8/7 correspond to about one/two/three remaining, not measured reserve. An RPE anchored to entire session effort, pain or cardiovascular strain is not interchangeable with set RPE. Do not require reporting all set efforts to perform a reasonable already-approved session. No instruction to deliberately test failure to calibrate RPE.

### 3.3 Initialize a prescription from history

1. Identify the objective, variation and intended role. If no suitable variation is approved, propose a feasible one and seek athlete confirmation of equivalence or treat it as a new series. Do not assume incline barbell, dumbbell and machine presses share loads; paused and touch-and-go may have distinct anchors.
2. Resolve explicit movement mapping and comparable load convention; select actual working sets with correct role, reps, technique and rest context. Exclude warmups from working exposure; track drop/failure sets separately for prescription comparison even when they count as working sets in analytics. Normalize units without silently doubling per-side weights or adding body mass.
3. Anchor primarily to the **most recent confirmed, representative successful exposure** with similar rep band and role, retaining its entire ordered rep/load vector, not just its best set. Review 1–2 preceding comparable exposures for variability. If last work was atypical due to an explicit interruption, deload or changed protocol, mark it atypical rather than cherry-picking a record high. Use a nearby successful anchor conservatively and explain why. A recent poor exposure remains relevant to risk and cannot be ignored by selecting an older best.
4. Choose a load that has demonstrated the required work, using the recent achieved load and reps. If the new rep target differs materially, prefer direct comparable history at that target or a conservative effort-guided introductory exposure. If only inferred historical evidence is available, use it to discuss a tentative starting value, obtain athlete confirmation or propose a low-demand calibration within explicit reviewed bounds; do not call the inferred sets confirmed. If no reference exists, ask what is normally used or use a technique/effort prescription with explicit approved load ceiling and stop criteria; no new percentage-of-PR estimate is necessary.
5. Initialize working sets from the approved intent and habitual **completed** exposure (see §5). Do not use the highest set-count week as the initial dose. Respect the weekly total across all slots and a change of phase. For an existing productive block, prefer its current prescription rather than reinitialize each week.
6. Set practical rest and effort bands with the athlete. Record relevant changes in apparatus, setup, exercise order, sleep, nutrition, pain or other training as context when available. Never infer physiological reserve or readiness from silence. A single best Epley estimate may be displayed with its model and inputs, but is not a prescription baseline unless separately reviewed and pinned.

### 3.4 Comparability and data eligibility

Separate identity, execution confidence and comparison quality. An eligible set has owner and time attribution, active evidence, known movement and purpose, and actual reps/load with appropriate units for the particular comparison. Confirmed actual execution for the planner requires its independently supported ordinals or athlete attestation, not simply a date/name match. Source timestamps may support descriptive strict analytics; they do not automatically establish a match to a prescribed slot. Partial completion can supply valid individual set observations but cannot count as a fully successful session.

Classify a comparison **strong** (same role/variation/load convention, similar rep target/rest/order/phase, confirmed actuals); **qualified** (some context unknown, enough for descriptive comparison but not the claimed precision); or **ineligible** (identity/units unresolved, stale or incompatible phase, unusable actuals). Missing effort makes a strong load-rep comparison possible, not a strong effort comparison. If an RPE is reported but its anchor or association is uncertain, treat it as optional narrative context, not a numeric trigger. Track each measurement's provenance and known missingness. Comparison quality is decision-specific, not a numeric readiness score.

## 4. Movement progression (M01a)

### 4.1 Review actual work

Compare the most recent eligible exposure against its **prescription in force at execution** and the approved next prescription. Record each intended working ordinal with actual rep/load/RPE if known, completion status, deviations and reasons. Full completion means all required working sets meet the nominal target or permitted execution criteria; intentionally using a permitted lower endpoint is compliant but is not necessarily progression-ready. If RPE exceeds the cap despite rep completion, label the effort deviation separately. A missed set is not a missed rep; a planned optional set intentionally omitted inside authorized flexibility is neither. Unknown is not failed. A reported session-completed flag alone is not confirmation of all set ordinals.

Evidence of improvement can include more achieved reps at the same load and comparable conditions, the same target at lower reported effort, or more load at matched reps/effort. More reps accompanied by much higher effort may simply reflect a different task; repeated lower RPE is suggestive, not proof of physiological adaptation. A decline may reflect technique, rest, local running fatigue, adherence or illness; do not diagnose cause. Treat a single anomalous exposure as a reason to clarify or make a reversible adjustment, not to permanently rewrite the block.

### 4.2 Decision matrix

Rules below refer to the proposed future nominal target unless execution flexibility is explicitly mentioned. In every row hold remains a reasonable choice if the objective is being served, data are uncertain or the next scheduled phase requires it. If progression is already explicitly scheduled and authorized, no new adaptive increase is needed; review for conflicts before generating any new future prescription. Do not apply an extra discretionary increase on top of a scheduled one.

| Observed state | RPE-aware candidate | RPE-free or uncertain-RPE candidate |
|---|---|---|
| Full target at expected effort | Hold as default; advance if the next block intent calls for it and eligibility is met. For discretionary progression require clearly manageable work and objective rationale. | Hold; after two eligible comparable successes at nominal target (or confirmed planned criterion), consider one rep within range. At all-set top of range consider load + rep reset. |
| Full target below expected effort | If every required set is confirmed, ratings anchored/representative, no conflict and effort is materially lower or comfortably inside range, propose one rep or bounded load step according to role; one strong exposure can qualify. Repeated evidence preferred if near boundary. | No conclusion about reserve. Compare demonstrated load-rep work and use the two-success branch. Targeted question if it would distinguish hold from progression. |
| Full reps above intended effort, especially last set | Hold progression; if repeated or clear cap violation, reduce load or reps within bounds, or increase rest if feasible and already approved. Check whether effort report is set-level. | No effort diagnosis. If technique/recovery or manageability feedback is poor, consider conservative local fallback; absent evidence, hold or ask. |
| Rep target missed on a confirmed set | No upward change. If near cap or unexpectedly difficult, propose a local rep/load reduction; if isolated and explained by an external interruption, hold/retry rather than infer diminished capacity. | Same, using actual missed reps and reason. No automatic estimate of RPE=10. |
| Required set missed, or unknown completion | For explicit miss, identify reason; simplify or hold if time/adherence. If performance-limited, reduce affected work. If unknown, seek attribution or hold pending; do not treat silence as a miss. | Same; missing optional RPE does not alter completion status. |
| RPE rises across ordered straight sets | Some rise may be ordinary. If final effort exceeds cap, or sharp repeated escalation accompanies missed targets, consider longer permitted rest, local load/rep reduction or clarification. Do not use mean RPE to hide cap violations. | Examine rep falloff, rest, technique or actual stop; distinguish planned descending reps from unplanned deterioration. |
| Exercise mapping, context or history incomplete | Only use supported dimensions; if load identity uncertain, no numeric load progression. Seek confirmation or select an already-approved conservative option. | Same. Inferred-only history cannot satisfy the upward trigger; lack of recent comparable sessions is not evidence of poor response. |
| New pain, acute concerning symptoms, unsafe technique or restriction | Stop/defer affected work as appropriate; no adaptive loading through symptoms. Seek qualified assessment where warranted. Preserve other safe work only if feasible. | Same; no need for RPE to stop. |

### 4.3 Load and repetition rules

- **Straight sets:** keep load constant for a rep increase. Allocate +1 total repetition to the first eligible set below its permitted maximum (default earliest ordinal; skip any set with observed difficulty or role restriction). Example: 6/6/6 → 7/6/6, not automatically 7/7/7. At the top of every required set's range, a load step with rep reset may be considered. Confirm the entire set sequence, not just the top set. If per-set targets cannot be represented, use separate ordered groups or retain a uniform target until a reviewed representation exists.
- **Fixed-rep heavy work:** once all prescribed reps are demonstrated with manageable effort or two confirmed repeat successes without contradictory context, a small bounded load step at the same reps may be reasonable; no requirement to first increase reps if the approved role prohibits it. Without RPE, a planned heavy load increase is conditional on confirmed repeated target performance and any required athlete feedback. If a heavier target cannot be justified, hold.
- **Rep reset:** on a load increase in a variable-rep group, reset nominal reps toward the lower approved endpoint; default use the lower endpoint for all affected sets unless comparable history at the new load justifies a different target. Check the resulting prescription and ranges against both block bounds and demand caps. This is an intentional single progression action, not an added load-plus-rep increase. If reset would violate minimum strength specificity or volume, use another candidate. Do not apply an automatic e1RM equation.
- **Top set + backoffs:** evaluate the top group and each backoff group separately with their own history, intended effort and rep bands. A top-set success cannot authorize heavier backoffs if their performance is poor. Default change at most one load/rep group per movement per review. Keep backoffs at demonstrated loads unless their own progression or a specifically reviewed relative-load policy warrants a change. If a backoff percentage is explicitly approved, recompute within equipment and bounds, and validate it as an additional coupled demand change; otherwise hold backoffs.
- **Technique work:** keep the same movement, quality criteria and practice purpose. A higher load is not progress if the pause/ROM/tempo criterion is lost. Without reliable quality context, favor hold.
- **Reduction:** if a missed rep or high effort is meaningful, reduce nominal reps by one on the affected group (not below floor), or load by the smallest feasible decrement targeting roughly 2.5–5% when appropriate. Choose rep reduction if it preserves intended heavy load and remains feasible; load reduction if the rep range/technique must be preserved. If a small fallback would not make the session defensible, stop/defer or seek a revised prescription. Never mechanically compel a small decrement when safety is in doubt. No missed work repayment rule.

### 4.4 Execution vs future adaptation

Before the next exposure the coach can recommend an already-approved option and explain its purpose. During execution, if effort is above the instruction or technique is failing, the athlete may choose an allowed lower load/rep option, take allowed extra rest, or stop. Record actuals and any deviations; do not retrospectively revise the approved prescription. The proposed next session may differ from the actual reduced session only with approval. A hard safety restriction blocks an unsafe candidate even if the athlete wants it; the system must not present an unsafe unchanged prescription as the fallback. A new restriction invalidates a conflicting pending proposal.

## 5. Working-set exposure adjustment (M01b)

### 5.1 Establish the dose and its meaning

Use the current approved weekly working-set count for the mapped movement and the actual counts in the last 3–4 representative completed weeks. Preserve the set type, intended role, session allocation, rep/load and effort context. Show prescribed, confirmed completed, inferred and unknown counts separately. A recorded set can be valid descriptive evidence without being progression-eligible. Do not sum across different movements into a muscle-equivalent dose without an explicitly reviewed mapping; compound exercises are not independently counted twice toward the same movement goal. Time and local overlap from other movements are context, not fractional physiological volume calculations. Use the median completed weekly count as a descriptive habitual anchor when coverage is good; with partial coverage, show observed counts and range, not an estimate of unlogged training. Do not substitute tonnage for stimulus or compare tonnage across incompatible series.

Assess exposure against **task-specific** comparable performance, the intended block objective and burden. A strength-maintenance objective can be met by stable performance; a technique objective can be met without heavier loading. If the plan intentionally phases volume up/down, compare to the week intent rather than judging any reduction to be deterioration. No claim of maximum recoverable, minimum effective or optimal volume is made.

### 5.2 Select the dose action

| State | Candidate action | Rationale and limitations |
|---|---|---|
| Productive current exposure: objective advancing or maintenance achieved, acceptable tolerability, key runs protected | Keep weekly count. Consider movement progression independently. | Current exposure is working in the practical sense; extra sets are not necessary merely because the athlete adapts. No causal or optimal-dose claim. |
| Apparent stagnation, but few comparable sessions, variable exercise setup, or incomplete history | Hold, improve comparability or ask. | Absence of observed progress is not established lack of adaptation. |
| Poor adherence (time, schedule, missed sessions) | Address feasibility, simplify or redistribute within bounds; reduce low-priority work when required. | Do not increase prescribed sets to make up for undercompletion. No nonresponder label. |
| Local fatigue or repeated performance-limited shortfalls | Consider one fewer affected working set/week, reduce local load/reps, or redistribute the same count. | Prefer the least disruptive adjustment that addresses the specific problem; preserve unrelated work and commitments. Do not claim running caused fatigue. |
| Generalized burden across multiple tasks, athlete reports poor manageability | Hold all progression, consider coordinated reduction or block review; ask targeted questions, respect safety. | A shared pattern is context, not a diagnosis. Larger reductions or changes to objectives need explicit reviewed proposals. |
| Candidate insufficient stimulus: at least 3 eligible exposures spanning roughly 2+ weeks without objective-relevant improvement, current targets actually achieved, adequate adherence and reported tolerance, no phase/measurement/availability explanation | Consider trial +1 weekly movement set only if movement progression is not a better next step, athlete wants that objective advanced, and time and protected commitments are feasible. Hold is still valid. | “Insufficient stimulus” is a hypothesis, not an inferred physiological fact. Prefer one change at a time. If load/reps are clearly underchallenging, adjust those rather than volume. |
| Changed objective or phase, or chronic conflict with other commitments | Follow already approved phase intent; otherwise explicit block review. | A dose selected for development need not be suitable for maintenance or assessment. Do not silently repurpose the block. |

### 5.3 Size, allocation and review

Proposed default dose trial: add or remove **one relevant working set per movement per week**, allocated to the best existing slot based on purpose, confirmed tolerability and time. A single added set is 50% of a two-set week: where the relative change is substantial or a block percentage cap would be exceeded, hold/redistribute or request an explicit reviewed exception; no automatic exception. A provisional default positive set-change ceiling is the lesser of one set and 25% of the approved movement's weekly count, rounded down to whole sets. Thus a count of 3 has zero discretionary increase under this default; a count of 4 can add one. The 25% is a conservative programming choice, not a physiological threshold. A newly introduced exercise is initialization, not division by zero; it requires a reviewed block/slot allocation. Negative changes respect floors; for safety, stop affected work even when the floor cannot be met and surface conflict.

Choose a lower-priority set first for reduction if it overlaps the problem; do not remove a priority top set simply because it comes first. For an addition, select the feasible existing slot with least threat to protected work; default to the slot with most remaining approved time, then earliest stable slot order, provided burden and role match. Redistribution preserves total sets and may change local burden; validate both sessions and neighboring slots. Do not convert one weekly dose adjustment into one added set per session. Do not increase load/reps and weekly sets on the same movement in a review by default; a separately approved explicit phase progression may specify coupled changes. Set redistribution is a different change class; avoid simultaneous discretionary load increase if redistribution materially changes exposure comparability. Evaluate every permitted endpoint and actual calendar duration.

Reassess at the next comparable exposure and weekly review. After a set addition, keep the trial count for at least two comparable exposures and one completed representative week before another discretionary increase, if safe and tolerable. Seek a roughly 2-week response window if frequency allows; reduce/stop earlier when needed. Track adherence, burden, objective performance and secondary run quality. If no benefit is observed, do not infer that the dose was ineffective from a short trial; hold, revert or review after enough comparable observations. No unapproved permanent update or learned “optimal volume” from a single outcome.

## 6. Concurrent scheduling and recovery context (M01c)

### 6.1 Observe the relevant calendar

Review the approved seven-day plan, adjacent boundary commitments and recent actual runs. Classify planned purpose from approved session metadata (easy, threshold, intervals/hills, long, event/assessment), not from speed alone. For actual runs, use dated duration, distance, sport/subtype, elevation and optional athlete-reported effort, terrain and local symptoms; classify a run as demanding relative to its purpose and habitual exposure only when the context supports that label. Missing RPE/HR or a generic activity summary does not establish an easy run. A performed-workout instruction is not achieved interval execution. Include other local sport exposure where it is available and relevant. Do not require wearables, quantitative HRV or a composite recovery score.

Inspect the previous and next two local calendar days around a demanding lift or protected run, plus farther commitments when the block requires them. This is a practical review window, not a prescribed 48-hour separation, a statement about clearance of fatigue or a new scheduling constraint. The current block's explicit spacing/reserved windows remain binding even if the observation window is shorter. Review time from actual starts/ends when known, avoid overlaps and preserve neighboring approved sessions. Use the planning zone and existing date/time validation; no changes to started days or observed slots.

### 6.2 Decide by priorities, local overlap and feasibility

1. If the present plan fits the block, time and protected objectives and there is no convincing local problem, maintain it. Do not move work just because running and lifting are adjacent.
2. Where demanding running and lower-body lifting overlap and athlete-reported local soreness or a comparable lower-body decrement threatens a specific key session, prefer avoiding additional discretionary progression in that region. Clarify uncertain demanding exposure or symptoms if it would change the proposal. Temporal proximity suggests a plausible explanation, not causation. Consider preserving the approved load or key strength stimulus while reducing low-priority accessories or the locally affected reps/sets. Keep unrelated upper-body work if no general restriction or burden evidence affects it.
3. Consider moving the lifting slot to an available day/time when that preserves both goals, feasible recovery spacing, other commitments and required session content. Alternatively move a lower-priority run only if its approved protection allows a date change and its purpose/exposure are preserved. A protected run cannot be moved merely because it inconveniences a lift; distinguish a protected date from a protected purpose with an explicitly allowed alternate window. Any future date change needs approval.
4. If relocation is infeasible or imposes more disruption, propose a local reduction (accessories first when compatible with goals; otherwise reduce an affected group) within weekly and session bounds. Local muscular fatigue is not a reason to cancel unaffected work or infer that an easy run should be replaced.
5. If both objectives are protected and no within-block alternative satisfies them, return named conflicts, the requested vs available values, and explicit alternatives requiring block review. Do not silently reduce protected running distance, intensity, frequency, or priority, or violate strength floors. Do not give a scheduling threshold such as a universally sufficient 2-hour gap. If a restriction makes existing work unsafe, defer affected work rather than recommend keeping it; report the resulting exposure conflict.

### 6.3 Candidate preference in conflicts

The athlete's approved rankings govern. Within them, first preserve protected commitments and hard constraints, then preserve priority movement purpose and required exposure. For a specific risk, prefer the smallest reversible effective local adjustment or feasible move; use the athlete's stated calendar preference to choose between equivalent local alternatives. When a protected run has an immutable date and strength purpose is preserved by relocating, moving the lift is generally preferable to lowering its primary stimulus. If time and burden cannot support both, a reduction in explicitly discretionary accessories can be preferable to relocating an entire session. This preference is contextual, not an estimated physiological utility. If constraints bind in opposite directions and none of the allowed actions is defensible, surface the conflict for a block decision.

## 7. Proposed numerical parameter configuration

These values are proposed starting configurations, not empirical thresholds or active rules. Each parameter is typed, scoped to a movement/role or block and versioned. **P** = programming judgment; **C** = practical convention; **E** = engineering safeguard. No quantitative parameter below is claimed to be empirically validated by J3A.1. The evidence informs plausibility and limitations only. Existing approved bounds and rule semantics take precedence; absence of a required bound does not imply unlimited authority. “Override” means documented, appropriately reviewed configuration or a narrower already-authorized choice, not unilateral runtime escalation.

| ID | Proposed value / type | Context and override | Observations and fallback | Interaction with block |
|---|---|---|---|---|
| N01 History count/window | 2–3 comparable exposures, prefer ≤28 days (P) | Extend for low frequency (e.g., up to 56 days with unchanged variation/phase and continuity); after interruption use cautious resumption instead | Known dates, role and conditions; if insufficient, hold/clarify, or conservative initialization | Phase and movement-specific reference rules override; never select a stale PR automatically |
| N02 Anchor | Latest representative confirmed success, full ordered vector; inspect 1–2 prior (P/E) | Use older qualified anchor only with explicit reason and current capacity check | Known loads/reps and comparable task; inferred-only is tentative, ask confirmation | Also pin approved predecessor as cap reference; historical anchor cannot enlarge permitted change |
| N03 Confirmation | 2 confirmed comparable successes for discretionary RPE-free rise; 1 strong anchored effort-aware success if clearly manageable and no contradiction (P) | Narrow further for heavy/new/stale tasks; scheduled progression may have different approved eligibility | Confirmed ordinals and nominal target; effort branch needs anchored representative set RPE and feedback where material; hold if insufficient | Existing progression gate remains unchanged until replacement approved; no inference substitution |
| N04 Rep increment | +1 total rep on one eligible working set per movement review (P) | First eligible ordinal, unless explicit role or another set is safer; fixed-rep heavy group uses load-only branch | Comparable reps and load, actual execution; hold if range exhausted and no load step | Respect per-set range, total demand caps and approved specificity |
| N05 Upper-body load rise | smallest equipment step; typical target ≈1–2.5%, ceiling 2.5% (P) | May be smaller than 1%; different reviewed cap by role/equipment; no forced minimum | Known discrete equipment and comparable total load; if no feasible step, reps/hold | Limit = min(profile cap, approved positive change limit); apply to affected group nominal and any raised permitted endpoints |
| N06 Lower-body load rise | smallest feasible step; typical ≈2–5%, ceiling 5% (P) | Smaller increments allowed; use more conservative cap for uncertain effort or technique | Same as N05; no automatic increase merely because larger cap | Same rule, respect upcoming runs and combination restrictions |
| N07 Equipment rounding | Enumerate allowed discrete values in canonical units; never round a rise above cap (E) | Use exact implementable plates/machine increments, athlete units; no rounding exception without explicit reviewed cap | Known equipment and load convention; if unknown, ask, rep change or hold | Candidate must belong to approved discrete options/ranges; round display only after exact checks |
| N08 Rep reset | lower approved endpoint for variable-rep group after load rise; fixed group unchanged (P) | Use higher demonstrated target only if separately justified and no simultaneous demand escalation | Prior rep band and appropriate history; if reset infeasible, hold | Respect floors, role and total repetitions/demand restrictions |
| N09 Effort and rest | heavy RPE 7–8.5 / 3–5 min; moderate 7–8.5 / 2–3 min; technique 6–7.5 / 2–3 min; accessory 7–9 / 1–2 min (C/P) | Use athlete history, role and time; cap usually ≤9 (technique ≤8) if approved; assessment may differ under explicit policy | Anchored set effort if used; missing RPE uses N03, rest unknown qualifies comparison | Approved ranges, session time cap, no overriding restrictions; no RPE-derived exact RIR |
| N10 Effort change signal | approximately 1 reported RPE point on comparable work as a contextual flag, or any confirmed cap breach (P) | Repeated observation preferable; don't use as MDC or trigger from average RPE alone | Comparable anchored effort and set order; absent/uncertain effort use reps and feedback | Cap violation is deviation; nominal target mismatch is contextual, not hard physiological boundary |
| N11 Local fallback | −1 rep on affected group (not below floor), or smallest feasible decrement aiming ~2.5–5%; rest increase if authorized (P) | If too small for mismatch, larger reviewed reduction/defer; do not require decrement for time-only miss | Actual shortfall/effort or safety feedback; unclear reason → hold/ask unless safety conflict | Keep bounds, priorities and floor; safe stop always allowed, unresolved floors become conflict |
| N12 Habitual sets | 3–4 representative completed weeks; median and range of actual confirmed counts (P/E) | Adjust window for low frequency/phase; inferred counts shown separately | Coverage, movement mapping, actual set kind; insufficient → no numeric escalation from dose history | Compare approved weekly count and floors/ceilings independently |
| N13 Set increase gate | ≥3 eligible exposures spanning ~2+ weeks, objective not improving despite target completion, sufficient coverage, reported tolerance, explicit objective rationale (P) | This is minimum opportunity to consider, not stagnation diagnosis; longer window if noisy/low frequency | Actual exposure + performance + tolerability + no conflicting priorities; missing tolerance or weak coverage → hold/ask | Phase may prescribe different approved changes; no unplanned added set when per-set demand also rising |
| N14 Set increment | +1 weekly set, at most floor(0.25 × approved weekly count), and no more than approved cap; reduction −1 weekly set initially (P) | At 1–3 sets/week positive step needs reviewed exception; greater burden can justify larger explicit reduction or block review | Known weekly count/actual adherence, local burden and time; unknown count → no addition; safety defer if needed | Enforce floor/ceiling and combination restrictions, validate all slots; no catch-up dose |
| N15 Set trial review | next exposure, weekly check, before further increase ≥2 comparable exposures and ≥1 representative completed week; aim ~2 weeks for context (P) | Earlier review on adverse effects; extend when frequency low | Subsequent comparable work and run completion; unknown → retain/defer rather than escalate | Planned next phase and safety constraints prevail |
| N16 Calendar window | previous/next 2 local days plus adjacent block boundaries (P/E) | Expand for events, dense schedule, relevant prior work; no minimum physiological gap | Dates/times, purpose, actuals and constraints; missing run coverage → manual context and protect commitments | Existing spacing/reserved windows and protected dates remain binding |
| N17 Reassessment | next comparable exposure + weekly review; immediately at relevant restriction/correction (P/E) | Deload/interruptions may need explicit resumption policy | Actual execution, feedback and current plan identity; missing → no inferred outcome | Existing stale-candidate and approval logic; review only unstarted future work |

### 7.1 Exact increment policy and examples

Let `L0` be the approved predecessor's nominal positive external load for the affected group, `H` the latest comparable demonstrated load for the intended role, `c_profile` the scoped proposed cap, `c_block` the approved relative cap and `d_block` any approved absolute cap. A load-rise candidate must be a discrete feasible equipment value `L1 > L0`, pass `L1 − L0 ≤ min(L0*c_profile, L0*c_block, d_block)` for applicable caps, and be credible given `H` and achieved reps. Also validate allowed ranges against predecessor allowed maxima, approved absolute load bounds, other combined-demand constraints and nominal target eligibility. If the block defines a different reference metric, validate that independently; do not replace it with `H`. Require the observed successful reference to support the intended target, not merely an old higher load. A missing required cap/reference is not treated as infinity; defer that action until resolved. Use exact decimal unit conversion and comparison, not rounding to a percentage displayed to the user.

- 80 kg upper-body group: 2.5% × 80 = 2.0 kg. With 0.5 kg plates on each side, a 1 kg total increment to 81 is feasible; with only 1.25 kg plates on each side, 82.5 is a 3.125% increase and fails. Use an allowed rep increment if available; otherwise hold or explicitly review equipment/cap exception. No rounding to 82.5.
- 90 kg upper-body group: 2.5% cap = 2.25 kg, so a 2.5 kg increment remains ineligible. 100 kg group: 2.5 kg equals the cap if all other constraints pass.
- 140 kg lower-body group: 5% cap = 7 kg. With 2.5 kg total steps, choose 142.5 rather than 145 or 147.5 absent a separately justified need. A 2% tighter block cap is 2.8 kg, still permits 142.5. A 1% cap permits none. For dumbbells, compare per-dumbbell load only if that convention is explicit and stable; do not invent a total external load. Equipment inventory is required for precise suggestions.
- Positive cap is not a reduction cap. A reduction must pass its own approved rules and safety conditions. If the athlete stops early, record a deviation rather than falsifying approval to satisfy the floor.

## 8. Deterministic candidate decision procedure

### 8.1 Conceptual procedure (not executable application code)

Reuse the existing versioned plan/context, proposal, validator and trusted owner decision contracts. The following names denote steps, not new service interfaces or a separate engine. A policy module could eventually feed the existing planner with a small set of candidate deltas and structured rationale; the planner remains the source of calendar feasibility and persistence.

```text
review(as_of, owner_context, approved_head, block, requested_future_scope,
       frozen_observations, policy_version, evidence_pin):
    0. require owner-scoped inputs, explicit head, active context,
       reviewable future scope, rule and evidence version
       if scientific/method/operational prerequisites not met:
           return research-only review or named authorization gap (never activate)

    1. identify restrictions, protected objectives, phase, all hard bounds,
       allowed exercise/role mapping, equipment, neighboring slots, time budget
       if new safety concern conflicts with affected work:
           flag affected work stop/defer; no unsafe hold or rise
       if head/context/required data invalid: return conflict/clarification

    2. project owner-scoped evidence as of as_of:
       active identity, units, exact source/observation versions, slot attribution,
       separate confirmed / inferred / unknown actuals, comparable series & roles
       retain coverage, source deletion/correction flags, exclusions and reasons
       select recent comparable history per N01–N02 and actual weekly dose per N12
       label strength of comparison separately for load/reps and effort

    3. review execution in original approved prescription:
       compare ordered required sets to nominal targets and execution intervals
       distinguish completed, partial, explicit miss, unknown, optional omission
       derive actual set/rep/load and effort deviations and reasons
       review planned vs actual running separately; upcoming slots are not missed

    4. assess task-specific trends (not latent state):
       productive / stable-for-maintenance / ambiguous / possible deterioration
       mark effort context if anchored and associated, otherwise unknown
       identify adherence vs possible performance limitation vs unknown reason
       identify local overlap, athlete feedback, burden and objective mismatch

    5. generate bounded candidate deltas in stable order:
       safe unchanged plan/authorized execution choice where feasible
       if safety issue: affected work defer/stop, feasible unaffected work,
           targeted clarification/professional review; do not generate rise
       else if hard conflict or local problem: local reduction, redistribution,
           permitted slot moves, hold progression, targeted clarification
       else if phase requires reviewed change: exact phase delta if eligible
       else if confirmed progression conditions met and objective calls for rise:
           rep +1, or smallest legal load step + appropriate rep reset,
           or fixed-rep load step; do not add discretionary rise on planned rise
       if dose review conditions met: hold / one-set trial / one-set reduction /
           redistribution as independent candidates; exclude prohibited combinations
       if needed observation unavailable: ask one decision-relevant question
           or use separately defensible conservative fallback
       retain no-change as alternative unless incompatible with constraints/safety

    6. validate every candidate using existing planner contracts:
       exact owner, head, block/phase, future slots, approved movement and restrictions
       nominal AND permitted endpoints, discrete equipment, reference and change caps,
       working-set floors/ceilings, combination limits, all priority commitments,
       time (warmup/rest/transitions), calendar overlaps, spacing, boundaries
       record constraint IDs / requested / available for rejected deltas
       do not use missing required input to pass a hard constraint

    7. choose among feasible, defensible candidates using §8.2
       if none: return named conflict or defer, explain explicit block review choices
       if hold/authorized execution option: render without mutation
       else: build exact before/after delta via existing planner, seal preview,
             freeze rule/context/head/evidence/observation IDs and rationale

    8. render decision and alternatives, coverage, uncertainty, empirical premises
       (only eligible evidence as operational citations), programming judgment,
       expected objective, kept commitments, changed slots and next review
       no unsupported causal or physiological inference

    9. athlete approves/declines through existing trusted command:
       recheck active head/context/observations, withdrawals, restrictions,
       elapsed slots, evidence and exact candidate; stale => regenerate, not rebase
       approval atomically advances head; decline preserves current head and conflict
       no automatic provider writes

   10. at next actual exposure and weekly review:
       attribute execution to approval in force, freeze actuals and corrections
       assess adherence separately from subsequent comparable performance
       record response and alternatives; do not infer policy efficacy from one change
```

In research mode, step 0 does not prevent producing hypothetical recommendations for review; it prevents those recommendations from being submitted as an authorized coaching rule. After appropriate authorization, only eligible scientific assertions may appear as operational evidence. If a programming choice is authorized without relying on an unresolved empirical claim, record the choice, its assumptions and its independent rationale; do not disguise it as scientific support. A safety deferral and a factual report remain available even where a progression method is not authorized.

### 8.2 Deterministic preferences (lexicographic, not an optimizer)

Use explicit objective and athlete-confirmed preferences. First eliminate invalid candidates and candidates with insufficient evidence for their claimed change. Determine a decision class from review facts: safety/conflict, known performance or adherence limitation, explicit phase change, productive/maintenance, eligible development, or unresolved. Do not select a safe-but-unhelpful hold ahead of every clearly requested feasible phase change; likewise do not select progression merely because it is feasible.

| Decision class | Default ordering among defensible alternatives |
|---|---|
| Safety/conflict | Defer affected unsafe work; preserve other safe work; feasible lower-impact alternative or block review. No unsafe unchanged plan. |
| Local problem | Protect binding commitments; if a permitted move preserves priority work with reasonable time and preferences, consider it; otherwise smallest local reduction that addresses identified issue. Hold if manageable and no conflict. Prefer removing a low-priority accessory over a priority stimulus when both address problem. |
| Adherence/time | Simplify or move feasible low-priority work before adding any dose; hold where schedule is now feasible. No catch-up. |
| Explicit phase intent | Exact eligible planned transition; hold/defer and explain unmet prerequisites if not feasible. No extra discretionary increase. |
| Productive or maintenance | Preserve dose and schedule; hold if no advancement requested; eligible per-set progression only when objective calls for it. |
| Eligible development | Variable-rep role: rep step before load until all required sets at upper endpoint. Fixed-rep role: bounded smallest load step if eligible. If already at top and no load step, hold. Set trial only with distinct §5 rationale and no simultaneous per-set escalation. |
| Unresolved | Hold safely, ask a decision-changing question, or defer precise prescription. |

If multiple moves/reductions preserve the same priorities, prefer the athlete's stated option, then fewer materially changed slots, lower-priority affected work, smallest applicable delta within the same change class, earliest feasible slot by existing stable order, and stable movement/group/ordinal key. Do not compare kg, sets, minutes and effort as if commensurate. If the remaining alternatives trade off protected goals or meaningful athlete preferences, present them for review rather than force a numeric ranking. Document any unresolved tie requiring athlete input; stable tie-breaks are for semantically equivalent options. A candidate rationale includes the rejected material alternative and why it was not selected. No LLM is required to decide eligibility or validate bounds; an optional renderer can summarize frozen facts, not invent new ones.

### 8.3 Invariants for future conformance

One set counted once; no inferred-to-confirmed promotion; no unknown-as-zero or unknown-as-missed; no display-name load equivalence; no silent rounding above caps; no current-head attribution of earlier actuals; no unapproved change of nominal targets, ranges, dates or commitments; no unauthorized source/claim/method citations; no stale approval; no unsafe fallback; same input snapshot yields same semantic candidate/alternatives and rationale facts. No physiological latent variable required.

## 9. Worked examples and synthetic evaluation cases

All examples are invented, not observations of the project owner. Assume the policy has been appropriately authorized for the purpose of simulation; it is not authorized in reality. Unless specified, the approved block permits the nominal changes, discrete equipment, rep/effort ranges and schedule described; actual sets are independently confirmed, prior exposure is comparable, no new restriction exists and no other constraints bind. RPE denotes set effort. Loads are total external kg. Each changed future target needs athlete approval. The preferred action is one defensible default, not the only acceptable coaching choice.

### W1 — Incline bench: repetition progression and a feasible load increase

**Intent:** priority press development, moderate-rep volume session; 3 working sets; permitted reps 6–8 per set; RPE 7–8.5; cap 9; 3 min rest; 2.5% upper-body cap. No planned dose increase; run commitments remain stable.

| Exposure | Nominal prescription | Confirmed work | Set RPE |
|---|---|---|---|
| Prior 1 | 80 kg × 6/6/6 | 6/6/6 | 7.5/8/8 |
| Prior 2 | 80 kg × 6/6/6 | 6/6/6 | 7/7/7 |

**Candidate:** 80 kg × 7/6/6, rest and set count unchanged. Previous exposure met target and last-set reported effort is lower; one additional rep on the first set is an understandable next development step. Do not claim an exact reserve increase. Holding 80 × 6/6/6 is also defensible if the block emphasizes consolidation. A load increase now is not preferred because reps remain below the top of the approved range.

Later, suppose separately approved progression yields two confirmed 80 kg × 8/8/8 sessions at RPE ≤8. With microplates giving 1 kg total steps, propose 81 kg × 6/6/6 (+1.25% load, reset reps) without changing sets. With only 2.5 kg total steps, 82.5 kg exceeds the 2 kg cap: hold at 80 kg × 8/8/8 or seek an explicitly reviewed exception. No automatic rounding and no expansion beyond the rep range. **Next review:** compare achieved vector and effort at the next volume exposure, retain key run plan. **Approval:** Y for each changed nominal target.

### W2 — Top set and backoffs are separate decisions

**Intent:** heavy incline press; top group fixed 1 × 4 at 90 kg, target RPE 7.5–8.5; backoffs 2 × 5–6, nominal 77.5 kg × 5/5, target RPE 7–8.5. All rests 4 min, cap 9, microplates allow 1 kg total steps. Top and backoffs have separate load anchors. Block allows 2.5% rise and forbids discretionary increases in two groups at once.

| Group | Previous confirmed actual | Latest confirmed actual | Review |
|---|---|---|---|
| Top | 90 × 4 @8.5 | 90 × 4 @7.5 | Meets target with manageable effort |
| Backoff | 77.5 × 5/5 @8/8.5 | 77.5 × 5/5 @8/9 | Completed but second set above target band |

**Candidate:** 91 kg × 4 top, 77.5 kg × 5/5 backoffs unchanged, provided athlete confirms the backoff effort was manageable and no meaningful local deterioration threatens the session. This is +1.11% relative to top load, below cap. Hold the top too if backoff difficulty is unexplained or repeated; consider lowering backoff demand if local shortfall emerges. Do not raise backoffs automatically to keep a fixed percentage of top load. No new set and no RPE conversion to an exact 1RM. **Next review:** top and backoff outcomes separately. **Approval:** Y for 91 kg; N for an unchanged feasible prescription.

### W3 — Squat: unexpected high effort

**Intent:** heavy squat, fixed 3 × 5 at 140 kg, optional approved execution loads 135–140 kg in 2.5 kg steps; nominal target RPE 7–8, cap 9; rest 4 min. Last two exposures were 140 × 5/5/5 at approximately 7.5–8. Latest 140 × 5/5/5 at 8.5/9/9.5, no pain, athlete reports unexpectedly difficult final reps; same setup. No hard running conflict.

**Candidate:** no progression. At next session use 137.5 kg if that already-approved execution option is appropriate (−1.79%; the smallest available decrement; not a forced 2.5% minimum). If athlete reports marked difficulty, 135 kg (−3.57%) is another permitted option. Retain reps and set count; if effort cap still cannot be respected, stop or reduce further only within allowed execution choices, otherwise record deviation. If making 137.5 the new nominal target, seek approval. It is also reasonable to hold nominal prescription and clarify whether sleep, rest or other changes explain the unusual exposure. **Not allowed:** claim systemic fatigue or delete all lower-body training, average away the last-set cap breach, increase load because reps were completed. **Next review:** compare the next eligible squat exposure; further reductions or block review only with context.

### W4 — Progression without RPE

**Intent:** moderate-rep press, 60 kg × 8/8/8, approved 6–8 rep band, 2 min rest, total load step 1 kg, 2.5% cap. Two confirmed consecutive comparable sessions at 60 × 8/8/8; no RPE recorded, athlete confirms execution, same rest and no reported restriction or contradictory feedback. All relevant calendar bounds satisfied.

**Candidate:** 61 kg × 6/6/6, same count and rest; +1.67% and lower rep endpoint. The policy proposes this from demonstrated performance, not a guessed RPE or proof that the new load will be manageable. If either exposure is inferred-only, does not include actual ordinals, or is not comparable, hold or ask for confirmation; no RPE alone is not a blocker to the proposed branch when other eligibility is met. With 2.5 kg equipment steps, the first step exceeds 1.5 kg cap; hold at the top of range. **Approval:** Y for the changed target. **Next review:** actual reps and any optional effort, not a maximal test.

### W5 — Productive program, no need for additional sets

**Intent:** priority incline development; 10 weekly working sets (Monday 4, Wednesday 3, Friday 3); two approved runs. Three representative weeks confirm 10 sets each; comparable Friday fixed-rep top group progressed 85 → 86 → 87 kg × 4, with manageable effort and similar rest; backoffs and other work achieved. Running commitments completed as planned, athlete reports manageable workload.

**Candidate:** preserve 10 sets and current allocations, with movement progression reviewed separately. Do not propose 11 sets merely because training is going well (even though the +1 increment could pass the dose cap). If objective requires further development and heavy-group evidence is eligible, consider a separate small load step or hold, but do not raise the dose too. If later three comparable exposures stall while work is achieved, investigate effort, adherence, phase and competing goals; a one-set trial may then become a candidate, not a required response. **Approval:** N for retaining an already approved count/schedule; Y for load or set changes. **Next review:** weekly actual exposure, comparable Friday performance and run adherence.

### W6 — Demanding running and local lower-body fatigue

**Intent:** protected Thursday threshold run on an immutable date, Monday upper, Wednesday lower, Friday upper. Tuesday athlete completed a 60-minute hilly run, reported demanding effort and local quadriceps soreness; Wednesday pre-session feedback and the recent comparable squat exposure indicate unusual local difficulty, no concerning symptoms. Wednesday's future plan (reviewed before session start) is squat 3 × 5 at 135 kg, RDL 3 × 8 at 90 kg, leg extension 2 × 12 at 50 kg. Block requires 3 squat sets, permits 1–2 weekly leg-extension sets, and allows local load changes; time and calendar make moving the whole lower session difficult. Upper work unaffected.

**Candidate:** Wednesday squat 3 × 5 at 132.5 kg (one permitted decrement, −1.85%), RDL unchanged if unaffected and feasible, leg extension 1 × 12 at 50 kg **instead of** 2 if local burden and time warrant both changes; keep Thursday run and Friday upper. A smaller alternative is to remove one leg-extension set and hold squat nominal, using its authorized lower execution option if available. Prefer one local adjustment first if adequate; the prohibition on simultaneous discretionary *increases* does not forbid two distinct local reductions when justified. If a feasible Saturday lift preserves all relevant commitments and approved spacing, moving the lift without lowering priority work may be preferable. No assertion that Tuesday caused the difficulty or Thursday will be recovered by a fixed hour. If symptoms become concerning, stop affected work and seek assessment. **Approval:** Y for changes to future targets/counts/date; N for a safe previously allowed execution option. **Next review:** actual squat and Thursday run, local athlete feedback; no inference of chronic interference.

### W7 — Schedule conflict requires block review

**Intent:** approved Saturday lower-body strength session (squat 3 × 4, 145 kg, minimum 3 priority sets) and Sunday protected long run (90 min, immutable date), with explicit block constraint of different available calendar windows and a required spacing that cannot fit after an availability change. Athlete reports Saturday is no longer available; Sunday has only enough time for the run; all other eligible windows unavailable. Assume both work items are still in the future, no safety issue.

**Candidate:** no feasible within-block complete week. Show requested squat slot, available windows (none), required 3 sets and the protected 90-minute run. Retaining the previous calendar as the approved historical head is not a claim that the now-conflicted plan is executable. Offer explicit block-review alternatives: obtain another available window; athlete considers changing the protected run date only through block revision if genuinely possible; or explicitly revise strength exposure for this week. No automatic downgrade of the run, no forced missed-work repayment, no fabricated 2-hour physiological rule. **Approval:** explicit approved block-plus-future-week change, not merely a local override; decline preserves prior head and visible conflict. **Next review:** availability and approved priorities, not new physiological measurements.

### 9.1 Focused acceptance tests

Pin policy version, block/context/head, time zone, owner, approved prescription, exact observation revisions and evidence pin for each test. Expected action sets allow multiple defensible recommendations; deterministic fixture preferences can assert a particular preferred output when inputs remove material ambiguity. In addition to W1–W7:

| Case | Required behavior | Prohibited inference / regression | Approval boundary |
|---|---|---|---|
| T01 All required sets complete at expected effort, next intent maintenance | Hold, or explain exact preapproved phase transition | Automatic rise on every success | No change N; changed future Y |
| T02 Fixed-rep top group strong; backoffs cap breach | Hold or progress top only if other evidence supports and no conflict; consider backoff fallback | Top result authorizes every group; mean RPE hides violation | Y for future change |
| T03 Actual 5/5/3 of 3 × 5; stopped due to effort | Partial; no rise; local fallback or retry after context | RPE 10 imputed; all target reps completed | Y for future change |
| T04 Two sets absent; athlete says gym closed | Explicit time-related miss if attested; no physiological inference; simplify/reschedule | Replace unknown with missed, add catch-up sets | Y for move/change |
| T05 Hevy ended workout with reps, null timestamps; full RPE | Descriptive inferred history, ask attestation, no discretionary rise | Inferred ordinals become confirmed; existing E1/E3 gate weakened | N for question; Y for later change |
| T06 Same exercise name, changed equipment/per-side convention | Separate series or clarify mapping; no numeric load comparison | Assume equal resistance or silently multiply | Y for new prescription |
| T07 180 kg old squat PR; current confirmed 130 × 5 after interruption | Use recent reference, conservative hold/intro; do not prescribe from PR | Old maximum treated as present capacity | Y for changed target |
| T08 Weekly 3 sets, otherwise candidate set-add gate satisfied | +1 exceeds default 25%; hold/redistribute/explicit exception review | Round 0.75 up to one automatically | Y for redistribution or authorized exception |
| T09 10 weekly sets productive; set trial +1 combined with load rise | Reject simultaneous discretionary increases; retain dose or select one action | Feasibility alone authorizes compound progression | Y for chosen change |
| T10 Garmin aggregate split/step target with no achieved intervals | Use actual summary only; adherence unknown unless attested; protect run | Step instructions establish actual intensity/interval completion | N for factual review |
| T11 Relevant new movement exclusion or source correction after preview | Block approval; regenerate exact proposal; affected work defer if unsafe | Auto-rebase, accept same totals despite corrected observation IDs | Existing stale proposal cannot activate |
| T12 Missing RPE; two confirmed successful exposures; 80 kg load cap 2.5%, equipment step 2.5 kg | RPE-free branch permits rep step if in range; reject 82.5 kg; hold at top | RPE imputation, cap rounded upward | Y for rep target change |
| T13 Athlete declines a move; no remaining feasible schedule | Keep head, record decline and explicit conflict | Quietly change protected objective | Y for separate block proposal |
| T14 Replay older approval after import deletion/claim withdrawal | Historical rationale retained, current support/eligibility flagged; block new approval if dependency invalid | Rewrite past decision or use withdrawn claim | Existing historic approval unchanged |
| T15 Repeated stall but only partial week coverage and weak mapping | Hold/clarify; no set increase based on absence of data | Infer insufficient stimulus or maximum recoverable volume | N for hold/question |
| T16 An affected lift becomes painful before execution | Stop/defer affected work and offer assessment as appropriate; preserve safe work only | Unsafe hold forced by floor; injury diagnosis | Stop needs no permission, future replacement Y |

For every case require an explicit comparison, relevant provenance/coverage, rationale class, action and alternatives, constraint check, retained commitments and next review. Reuse existing golden cases A1/A2/A3/A6/C2/C3/D1/D2 and transaction tests as regression obligations. The test cases evaluate software correctness and recommendation quality, not causal physiological efficacy.

## 10. Human review package and implementation readiness

### 10.1 Review the three bundles together, not 17 isolated parameter votes

Recommended review configuration is §§3–8, including N01–N17 as a single candidate profile with role-specific overrides. Human reviewers should be able to accept a subset, reject a parameter, or require an explicit exception without losing exact traceability. These are proposed review decisions; no human attestation is supplied.

| Bundle | M01a — movement prescription and progression |
|---|---|
| Empirical premises | Pending Plotkin, Helms, Hickmott claims and sources in §2.2; Halperin signed error remains deferred as quantitative dependency. Practical principle: use reported effort as uncertain optional context. |
| Practical decisions | Recent comparable reference, purpose-specific templates, separate group progression, rep-first variable range, fixed-rep load option, conservative high-effort/miss fallback, RPE-free branch with two confirmed successes. |
| Numerical review | N01–N11, N17; specifically role bands, increments/caps, one-rep allocation, effort anchoring, reset and confirmation. |
| Limitations | No optimal algorithm, equivalence, exact reserve or validated RPE change threshold; no duplicate corroboration; no inferred completion in positive gate. |
| Human judgments | Qualified strength/hybrid coach reviews role specificity, effort bands, fallbacks, sufficiency of comparability and acceptable increase policy. Athlete confirms goals, variation/equipment, preferences, feedback burden and execution flexibility. Technical reviewer confirms representation, decimal rounding, data provenance and deterministic validation. |
| Permitted after authorization | Propose hold, one bounded rep/load change, reset, local reduction or clarification; recommend already-authorized execution option. |
| Deferred | Automatic prescriptions from Epley/old PR, failure tests, RPE calibration model, inference-only escalation, novel movement equivalence, unrestricted load ranges. |
| Conformance | W1–W4, T01–T07, T11–T12, T16; existing A1/A2/D1/D2 and approval replay. |

| Bundle | M01b — working-set exposure |
|---|---|
| Empirical premises | Pending Barsuhn existing/proposed exact revisions (§2.2); unresolved quantitative result not required to select a pragmatic hold-productive-dose rule. Enes/Pelland and velocity-loss evidence deferred for this profile rather than silently accepted. |
| Practical decisions | Keep productive count, investigate adherence and measurement before adding, one-set trial only with concrete rationale, local reduction/redistribution, no simultaneous discretionary rise in per-set demand. |
| Numerical review | N12–N15, N17; proposed +1 and 25% ceiling with floor rounding, minimum trial review opportunities. |
| Limitations | No causal attribution, optimal/marginal dose, universal volume threshold or maximum recoverable volume; Barsuhn uncertainty and denominators unresolved. |
| Human judgments | Coach reviews dose/change caps, rationale for testing an addition, and when local or coordinated reductions are appropriate; athlete reviews priority, burden and schedule; engineering reviewer ensures unique count, coverage and grouping. |
| Permitted after authorization | Propose stable set dose, local ±1 count or redistribution within bounds; explicit review for larger or coupled changes. |
| Deferred | Automatic volume escalation, muscle fractional-dose estimator, fatigue-triggered optimal dose, inference-only volume increase. |
| Conformance | W5–W6, T04–T05, T08–T09, T15–T16; A1/A2 and complete/partial/unknown denominators. |

| Bundle | M01c — concurrent scheduling and constraints |
|---|---|
| Empirical premises | Pending Petré timing claims and source (§2.2); qualitative context, not a quantitative spacing prerequisite. |
| Practical decisions | Honor approved objectives/constraints, distinguish local and general issues, move or reduce affected work where feasible, preserve unaffected work, escalate unresolved tradeoff. |
| Numerical review | N16/N17 review windows, use existing approved spacing and time bounds rather than new minimum hours; local fallback from N11/N14. |
| Limitations | No causal inference from proximity, no universal gap, no proof of recovery, no claims about actual intervals from targets. |
| Human judgments | Hybrid coach reviews priority tradeoffs/local reductions and symptom escalation; athlete confirms protected date vs purpose, availability and calendar preferences; technical reviewer verifies boundary conditions, identities and exact approval semantics. Clinician assessment is appropriate for relevant injury, concerning symptoms or restrictions beyond coach scope. |
| Permitted after authorization | Propose feasible future slot moves and local modifications, retain unaffected work, flag conflict/defer; explicit review for changed protected objectives. |
| Deferred | New running program, taper optimization, quantitative recovery scores, automatic changes to protected runs, diagnosis of overtraining or interference. |
| Conformance | W6–W7, T10–T11, T13–T14, T16; A3/A5/A6/C3, scheduling and transaction tests. |

### 10.2 Decisions that actually need review

1. **Coach/sports-science reviewer:** approve or revise the initial role templates, progression conditions, conservative dose-change policy and priority resolution. The critical choices are whether one strong RPE-aware success may justify discretionary progression, whether to use two confirmed RPE-free successes, and whether the +1/25% volume cap is appropriate for low-volume or specialization roles. Recommendation: retain these conservative starting choices, permit specifically reviewed role-level exceptions, and evaluate the outcomes prospectively. A sports-science reviewer separately adjudicates the exact pending source/claim revisions, transfer and rights; no need for the athlete to determine each statistical claim.
2. **Athlete:** confirm intended goals, movement preferences, equipment, acceptable effort and feedback burden, schedule, protected commitments and willingness to try small adjustments. Confirm actual execution when source data are ambiguous. Approve the exact future prescription, not a general permission to change everything. A coach's review is not the athlete's authorization and vice versa.
3. **Engineering reviewer:** choose explicit typed representations, exact unit conversion and role/ordinal mapping, deterministic candidate order, observation freeze and conformance harness. Minor stable tie-breaks and formatting defaults need not become separate athlete decisions; document and test them. No separate physiological optimizer or new planning engine required.
4. **Operational owner/release reviewer:** integrate and validate any separately approved evidence records/releases and versioned method/rule; ensure unresolved claims not depended upon are not cited as support. Authorize a named implementation milestone only after review, then exercise conformance and replay before use. Do not replace the current E1/E3 synthetic rule implicitly.

### 10.3 Observation and engineering readiness at pinned repository snapshot

| Capability | Current documented contract | Proposed gap / next engineering validation |
|---|---|---|
| Movement-specific actual reps/load/set kind | Canonical strength analytics include set rows, explicit series/load eligibility, 1–10-rep Epley descriptive estimates, known measurement coverage; `top_only=False` exposes all qualifying progression rows | Use all relevant actual ordered sets, not only maximum estimate; confirm availability of full set-level projection for ordinals outside 1–10, warmups, partials and rep-only groups. No need to change Epley math. |
| Identity and equivalence | Explicit mapping required; reviewed Hevy template IDs and conventions can group eligible occurrences; edits can replace child IDs | Durable reviewed series association to plan-local key, role, equipment, rest/technique where material; do not assume importer names or template equivalence beyond review. Freeze IDs/values and mapping version. |
| Confirmed vs inferred completion | Strict `query_strength` requires timestamps; `query_hevy_history` can infer ended workout with positive reps/duration/distance; flags provenance; E3 `Actual` manually attests ordinals and effort with optional reps/load | Need scoped attribution of real movement groups/ordinals beyond synthetic press and independent confirmation path. Inference is descriptive, not adherence or positive gate. Verify live historical coverage before relying on it. |
| RPE-aware vs RPE-free branch | Canonical set RPE can be null; E1/E3 synthetic fixture requires every confirmed prescribed set measured RPE within cap, zero inferred, manageable feedback, no deviations | New reviewed rule version to support RPE-free movement progression, group-level effort mapping and optional feedback semantics. Never weaken fixture. Distinguish session RPE from anchored set RPE. |
| Prescription representation | Plan design specifies ordered set groups, count, rep range, optional target effort, load modes, rest allowance, nominal/permitted bounds | Verify implemented support for arbitrary movements, separate nominal rep vectors and top/backoff roles, explicit equipment increments, optional set policy, load-range endpoints, multi-group deltas and positive caps. Add only needed semantics at later milestone. |
| Set-dose history | Weekly category counts, measured-rep/load coverage and inferred count available; open/empty workouts can appear in activity frequency | Need representative completed-week coverage and actual vs prescribed movement mapping; confirm aggregation over all slots, avoid double-counting, preserve partial weeks. No muscle-dose model required. |
| Running context | B2 summaries store dated sport/subtype, times, distance, speed, elevation and HR where provided. E3 manual actual can include run duration/RPE; step targets and split aggregates do not establish execution | Confirm actual provider ingestion/coverage and mapping to approved commitments; athlete report sufficient for purpose and local fatigue. Do not require chronological telemetry for calendar context; use richer observations only for separate running performance decisions. |
| Calendar and authority | Existing block/context/slots and feasibility, E2 sealed proposals, E3 outcome attribution/corrections, approval revalidation, frozen rationale and evidence pins | Verify general movement constraints, cross-week time windows, protected-purpose vs immutable-date distinction, approved simultaneous-change rules. Extend within planner, not separate scheduling engine. |
| Evidence and evaluation | J1 separates eligible claims and methods; current E3 demonstration uses synthetic progression with `j1-screening-1` and evidence gaps | Human review + release/authorization independent of engineering. Add versioned evaluation fixtures and regressions; pending J3A revisions not yet schema validated or approved. No tests run in this curation session. |

**Data readiness by decision:** qualitative history review and conservative initialization discussion are feasible from eligible current reports plus athlete confirmation; exact movement progression is conditionally feasible with explicit mapping, complete confirmed actual ordinals and implementable targets; exact dose addition requires representative actual exposure and tolerance; calendar review is conditionally feasible with approved commitments and relevant manual/summary run context. Actual adherence requires attributed execution; effectiveness requires subsequent comparable performance and context. Scientific and operational readiness remain pending for all new rules regardless of data coverage.

### 10.4 Suggested implementation milestone after review (not an instruction to implement now)

Freeze the accepted methodology profile, exact evidence dependencies and authorization boundary. Begin with one priority movement and ordinary straight sets, explicit canonical external load, known equipment step, manual actual attribution and existing run commitments. Add the RPE-free branch and group distinction only under a new version after demonstrating existing fixture behavior unchanged. Implement candidate deltas through the current planner/validator and sealed proposal flow, with no provider writes. Validate rounding, unknown/partial execution, role mapping, stale observations, source withdrawal, conflict handling and replay. Expand to top/backoff, volume trials and generalized local calendar adaptation only as their representation and conformance are reviewed. This is incremental sequencing, not a reason to discard the integrated methodology.

### 10.5 Remaining blockers and next curation tranche

J3A.1's Halperin full-text verification, Barsuhn denominator/statistical clarification, comprehensive correction/retraction/rights checks, and population-transfer reviews remain outstanding. Its pending draft evidence fragment was not integrated or schema-validated here. This session inspected the J3A.1 deliverable and pinned repository documentation, not implementation source or live Hevy/Garmin records; no claim is made that every proposed field already exists. No repository modification, code, test run, evidence release or approval occurred. All numerical defaults, set-trial percentage cap, candidate preference and role templates are proposed judgment requiring review, not selected by an empirical optimizer.

**Proceed next to J3A.2 — multiweek block construction and protection of secondary performance outcomes.** Appraise a focused set of existing evidence relevant to block objectives, phase structure, outcome-specific maintenance and preservation of running/strength commitments. Then alternate into J3B.2 to propose practical multiweek block methods. M01 remains the local next-exposure methodology that consumes an approved block; the next tranche should define how that block's intent and protected bounds are chosen, not retroactively authorize the present profile.
