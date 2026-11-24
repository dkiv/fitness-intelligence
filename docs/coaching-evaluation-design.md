# Evaluating a coaching decision

**Proposed acceptance specification for the first E/F/J review cycle.** Given a block, a
history and an athlete request, a reviewer must be able to predict which changes are allowed,
inspect the rationale, decline the change, and verify the exact prescription still in force.
Run the evaluation offline with synthetic owners, a fixture clock and a pinned catalog. The
first release uses deterministic rules and a template explanation.

## What each layer can decide

| Layer | Responsibility in the evaluation |
| --- | --- |
| Observation projection | Read the owner's normalized strength report and freeze the facts used. Include window/zone, as-of instant, exercise mapping, external-load eligibility, confirmed/inferred sets, sets with measured load/reps and estimate provenance. Run observations may consist solely of athlete reports. |
| Planner and validator | Apply confirmed goals and hard restrictions, named progression rules, availability, block envelope, recovery periods and event schedule. Emit a feasible seven-day candidate or explicit conflicts. Revalidate every proposed change regardless of its origin. |
| Knowledge and explanation | Retrieve from the pinned release, group material conflicts, link each scientific assertion to an applicable result and label programming judgment and private observations. Render a specific before/after diff, rationale and uncertainty. |
| Athlete review and persistence | Only the trusted owner command can approve or decline the sealed candidate. Recheck the base and current restrictions before activation. Preserve the historical approval, prescription and execution link. |
| Optional future LLM | Extract a proposed preference for athlete confirmation, invoke scoped read/proposal tools or explain their structured results. It has no authority to compute observed analytics, loosen bounds, invent evidence, approve or publish. The same validator and evaluation cases apply to model output. |

The [strength report](strength-analytics.md) counts some open/empty workouts in activity and
distinguishes inferred completion from confirmed completion. An exercise name alone cannot
establish comparability. A missing Epley estimate, recovery signal or activity import is
insufficient to conclude that a session was missed or that the athlete can tolerate an increase.

## Golden case format

A case manifest includes case ID and revision, fixture owner, frozen local date/time and IANA
zone, normalized input facts and coverage, prior approved plan and decisions, requested
action, and exact versions of rules, evaluator, corpus and renderer (model/prompt or none).
Store a semantic expected result or predicates, admissible alternatives, forbidden changes,
required rationale statements, allowed evidence IDs/locators, expected uncertainty, expected
writes and unchanged records. Use invented evidence in distinctly marked test releases. A
reviewer sets and versions these expectations **before** running a candidate.

Run from three entry points. Pure domain cases compare ordered semantic values, excluding
generated UUIDs and audit clocks. Repository cases drive the same internal proposal/decision
commands against disposable PostgreSQL and inspect the rows and head. Explanation cases
render the saved rationale and score its individual statements. Compare the same input across
rule, catalog or renderer versions with a per-case diff.

## Initial case set

Cases A1–A6 use the [eight-week press specialization fixture](training-plan-design.md#worked-cycle-a--eight-week-press-specialization).
All limits below are test inputs. Each row gives an observable pass condition.

| Case and perturbation | Expected decision and rationale | State or evidence check |
| --- | --- | --- |
| A1 · Produce weeks 1 and 2, no endurance feed | Week 1 places five press working sets and two runs totaling 45 minutes across seven local dates. After two confirmed lifts within the effort cap and positive feedback, week 2 has six sets and the same two runs. The extra set advances the press objective within its cap. | Weeks pin the same block and distinct frozen inputs. Week 2 becomes scheduled only when approved. Weeks 3–8 retain their intents without fabricated detailed schedules. The manual view preserves dates, effort, units, set counts and ordered run steps. |
| A2 · Remove week 1 feedback, then substitute an open/empty workout or inferred sets only | Hold at five sets under this rule. State which completion or effort evidence is missing. | An activity count, inferred completion or missing estimate cannot satisfy the confirmed-exposure predicate. No automatic load increase. |
| A3 · Saturday unavailable, Sunday still available | Offer to move the 25-minute run to Sunday. Show the date delta, weekday time budget and 24-hour start-to-start check through Monday. The rationale identifies the availability change and continued two-run commitment. | Before review the head is unchanged. Decline leaves Saturday current, shows its availability conflict and records one decision. On a fresh proposal, approval changes one logical slot's date, preserves the block version, and keeps the old calendar readable. |
| A4 · Remove the Sunday fallback as well | Return the conflict between two distinct running days and one permitted day. Reducing the running commitment needs a block revision. | The athlete must see every affected generated future week in the block diff. Inject failure before the head switch and verify every previous week remains current. |
| A5 · Boundary or dose violation | Allow a 10:00 Sunday start in the case context, then propose it with Monday fixed at 09:00. Reject 23 hours against the fixture's 24-hour minimum. Try a sixth set **and** a load increase in week 2. Reject the combined change even if each component would pass alone. | Report the violated rule and affected sessions. Repeat with an allowed rep/load interval whose upper bound breaches the envelope. The validator must catch the endpoint. |
| A6 · New movement exclusion arrives after preview | A pending press candidate cannot be approved. Surface the new restriction and require review of a feasible alternative or an explicit objective change. | The old approval is retained for audit. Flag the affected active plan for review and show the current restriction alongside it. An approval retry cannot activate the stale candidate. |
| B1 · Missed intervals before the event in cycle B | Respect the two protected pre-event days. Keep the taper or offer a feasible, explicitly reviewed alternative. | Preserve the missed result. No Friday catch-up session, no silent block change. Three repeats in the original interval run must render as 22 minutes including recoveries. |
| C1 · Low, missing and noisy recovery inputs with otherwise identical history | Retain the approved week or ask for feedback under the fixture rule. Explain the coverage difference. | No block rewrite, causal fatigue diagnosis or invented recovery baseline. A missing reading cannot be converted to zero. |
| C2 · Competing claims and a preferred program | Retrieve both applicable fixture claim revisions and their result locators. Explain disagreement and uncertainty. Label the method preference. | A program reference cannot fill an empirical citation. Swap the population for an indirect match, then remove the applicable claims. The explanation must disclose transfer limits or the gap. |
| C3 · Withdraw a cited claim after submission | Replay the old rationale using its pinned release and annotate the withdrawal. Block new approval relying on that claim. | A reverse lookup finds the affected proposal. Re-evaluation can open a new review. The historical approval stays intact. |
| D1 · Unknown exercise equivalence or direction of load | Two same-name occurrences have incompatible equipment or unknown external resistance. Allow supported repetition/count observations, decline numeric load progression based on their comparison. | Preserve series mapping, coverage and uncertainty. Replacing an imported exercise/set cannot alter a frozen prior explanation. |
| D2 · Late, ambiguous or source-deleted actual | Late manual run feedback pins the approved session in force at execution. Ambiguous matches remain unknown pending athlete review. A source-deleted workout loses current observational support. | No inferred miss from absent records, automatic link by date, or relink to the latest head. Keep the original evidence and distinguish any later correction. |
| D3 · Tenant or lineage mismatch | Use two synthetic owners and two plans of the same owner. Try to read, preview, decide, link a workout or reference another plan's week/head. | Owner-scoped command denies unauthorized access. Direct SQL composite FKs reject mismatched links. Future authenticated routes must pass equivalent read and write isolation tests before exposure. |

## Transaction and integrity tests

Drive each test through the [approval contract](training-plan-design.md#approval-revisions-and-execution)
and check persisted state after reconnecting. For concurrency, use independent database
sessions and a barrier before decision. Each test starts from a known approved head.

- Approve two candidates with the same base concurrently. Exactly one becomes current. The other
  returns stale and requires a new preview. A simultaneous approve/decline on one candidate yields
  one terminal decision. The loser sees the outcome or a conflict.
- Retry the identical successful or declined command after losing the response. Expect the
  recorded result and no new decision. Reusing the command ID with different intent conflicts.
- Fail after writing the decision but before advancing the head. Neither write survives. A retry
  can complete normally. Repeat for a block change spanning multiple generated weeks.
- Through direct SQL attempt to edit and delete a sealed revision, append a new session to its
  week, reparent an existing session, or assign the head to a declined revision. Each operation
  fails. Race a child insert with sealing to test both orderings.
- Approve a schedule, record a completed slot, then approve an edit to a future slot. Reload the
  earlier version, its execution link, and the proposal diff. The completed prescription and
  rationale must match the original.
- Run comparable checks for initial approval with a null base, dated exceptions, DST transitions
  and permissions to record manual running feedback. A day containing two sessions must fit the
  combined time budget.

## Release gates

| Gate | Measure and acceptance |
| --- | --- |
| Safety, privacy and authority | Zero hard-rule violations, cross-owner disclosures, unapproved mutations, broken historic links or provider writes. Any occurrence blocks release. |
| Domain correctness | All required fixture predicates and transaction invariants pass. Repeat runs produce identical semantic schedules, conflicts, evidence selection and structured diffs. A reviewer may specify several acceptable decisions for a case. |
| Evidence and explanation | For each scientific assertion separately, score factual accuracy, valid release/claim/source locator, entailment and applicability. Count omitted material conflicts per eligible question. Record required rationale elements present/expected, unsupported assertions and coverage disclosures. Use N/A with a denominator of zero. Any fabricated citation or unsupported empirical assertion in the initial release cases blocks release. |
| Change review | Report numerator, denominator and case IDs for each metric, before and after the change. Review every newly failing case and every changed expected result. Agree broader quantitative targets with a reviewer on held-out cases before the first pilot. |
| Outcome reporting | For elapsed approved slots report completed, partial, explicitly missed and unknown counts plus coverage. With 2 complete, 1 missed and 1 unknown out of 4, known-outcome coverage is 3/4 and completion among known outcomes is 2/3. Always display both denominators. Report deviations, effort and assessment change with alternative explanations. |

Passing offline cases establishes conformance to these decisions and safeguards. Assess coaching
effectiveness separately across observed blocks, with adherence, baseline comparability and
coverage visible. Sparse or selected outcomes cannot establish the causal benefit of a change.

## Implementation sequence and open questions

Begin with A1, A2, A4 and A5 as a pure domain slice. Add database and isolation cases with
the proposal/approval migrations, then run the evidence cases and full review cycle against a
narrow reviewed release. Repeat the suite on every change to rules, corpus, projection or
explanation. Keep the renderer deterministic for the first operational review.

Decide who approves golden labels and how reviewer disagreement is adjudicated, how much
inferred history suffices for later progression rules, and how to weight partial outcomes once
there are enough observations. A future LLM adds paraphrase, factual drift and unauthorized tool
attempts to the same evaluation. Larger simulations, personalized effect estimates and provider
delivery tests belong to later workstreams.
