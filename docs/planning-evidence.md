# E4.2C · Unified planning evidence and frozen decision inputs

`query_planning_evidence(engine, scope)` reads normalized training observations, athlete confirmations and manual execution together. Its single PostgreSQL read-only, repeatable-read transaction sees committed changes consistently across those sources. The trusted local planning principal must be the reserved synthetic owner. The reader checks ownership, provider and binding for each selected account. It creates no database records. [Reader](../backend/src/fitness_intelligence/db/planning_evidence.py) · [Contract](../backend/src/fitness_intelligence/planning/evidence.py)

## Reading one week

In the synthetic rehearsal, supply the disposable PostgreSQL engine and IDs of the seeded source accounts. The stop date is exclusive. Omitting an account omits that source family. Manual reports are selected by actual instant in the report zone. Garmin day coverage and outings follow the selected provider calendar. An effective explicit link also brings in its manual assertion when the report-zone date falls outside the selected period.

```python
from datetime import date

from fitness_intelligence.db.planning_evidence import query_planning_evidence
from fitness_intelligence.planning.evidence import Scope

scope = Scope(
    start=date(2027, 1, 4),
    stop=date(2027, 1, 11),
    zone="America/Toronto",
    strength_account=hevy_account.id,
    endurance_account=garmin_account.id,
    recovery_account=garmin_account.id,
    endurance_zone="America/Toronto",
    recovery_zone="America/Toronto",
)
week = query_planning_evidence(engine, scope)
for performance in week.performances:
    for task in performance.tasks:
        for view in task.qualifications:
            print(view.purpose, view.eligible, view.missing, view.exclusions)
```

Supply source zones only when verified for that period. `week.scope` retains the selected accounts, calendars, Hevy template classifications and explicit comparison inputs. Each `NativeMember` carries the D1D fact and a digest of its normalized source content. To rehearse confirmation, inspect that member, supply a `StrengthContext` or `RunContext` bound to its account, canonical member and digest, then read again. The context names its authority, basis, version and comparison identity. The resulting `member.display` is the precise E4.2B input for that member. A reviewed mapping or athlete statement must actually establish the supplied dimensions. This interface trusts the synthetic caller for that context. The confirmation command and its receipts remain separate from the reader. [Confirmation guide](scoped-observation-confirmation.md)

## Reading the evidence

| Source | Retained information | Interpretation |
| --- | --- | --- |
| D1D strength | Owner, account, external ID and reference, workout, exercise and set IDs, order, raw kind, timestamps, repetitions, kg, recorded RPE, source mapping and content evidence | A timestamp supports execution. D1D can infer completion from an ended workout and positive recorded work. Empty workout/exercise placeholders remain descriptive. A template and a reviewed external-load designation alone cannot establish variation, equipment, per-hand versus total load, group or ordinal. |
| D1D endurance | Native sport/subtype and local date, UTC start and report date, metres, activity/moving/elapsed seconds, reported average speed, field provenance, instruction and split-summary positions with ordered content digests | A summary supports an outing. A source-bound running role and structure require independent context. Instructions, counts of summary rows and session averages supply no achieved repetitions, chronological work/recovery measurements or interval pace. Fractional durations remain exact on the native fact. Only whole seconds fit the E4.2B duration display. |
| D1D coverage and recovery | Daily category, account status, pass/policy, attempted and successful retrievals, retained count, empty scan start, discrepancies, open issue keys/digests/clocks, recovery cells with their statuses | A retained count may be a lower bound. An empty retrieval can leave full-day exposure unknown. D1D recognizes a source-specific zero only under its full-day scan, reconciliation and calendar rules. Even that zero describes this source. Recovery remains descriptive. |
| E4.2B member confirmation | Original command/member identities, displayed fact and digest, recorded instant, field mask, independent report, correction/withdrawal lineage, historical and effective attribution | Only a current matching source, mapping, comparison and receipt tip supplies its chosen fields. A changed member (including an instruction edited at the same index), a pending deletion or a changed mapping withholds import-backed support. Independent reports stay attached to the original member and receipt for review. |
| E4.2A manual execution | Cycle, block revision, week, slot, originating approved prescription, actual instant, effective approved head at that instant, assertion/command IDs, recording times and predecessor chain | Current actuals take their values from the tip. The approved prescription is tagged as instruction. A missed or unknown assertion records what the athlete reported about the occurrence. It contributes no performed session. |

Each resolved task field retains all current claims with their source or assertion ID, value, evidence tier and resolution reason. A scoped independent report of four reps can correct a recorded five while leaving kg source-only. Two disagreeing current independent assertions produce a conflict with no selected value. Replacing a manual assertion or receipt makes its predecessor historical. An effort claim applies only to its set, indexed step or session. Manageability and prescribed RPE never supply measured RPE. Daily running counts are explicitly derived. Unmeasured values stay unknown. [Reconciliation](../backend/src/fitness_intelligence/planning/evidence_reconciliation.py)

The reader groups canonical source members by workout. A current explicit, one-to-one E4.2B outcome link joins the manual performance. A strength set additionally needs its own exact prescribed ordinal before its two sets of field claims can join. Extra recorded sets remain visible. Competing ordinal links retain both members and their confirmations, with attribution withheld. Unlinked same-sport imports and performed manual reports on the same report-zone day receive reciprocal potential-duplicate IDs. That flag is a review aid with limited recall. Similarity never creates a link or a combined count.

Workout creation and first import of the external reference have their own timestamps. First availability of the exact current set or activity revision is unknown. Latest retrieval, upstream revision, occurrence, confirmation and manual recording retain their own meanings. For a replaced member with no current source row, the reader can still find historical confirmations by the frozen workout instant in the report zone. The result describes currently accepted evidence. Arbitrary historical knowledge states require previously frozen inputs.

## Eligibility by decision

| Evidence view | Required inputs | What can remain unknown |
| --- | --- | --- |
| Descriptive exposure | Retained observation or performed manual report. For a reported strength set, its own completed or partial status establishes performed set exposure. | Completion, exact identity for comparison, dose or effort. Field status still applies. |
| Confirmed execution | Direct source evidence of execution (timestamp or retained outing) or scoped athlete evidence of completed/partial work | Dose, intensity and task comparison. An inferred completion alone is insufficient. Conflicting execution, unresolved activity support and potential double counting limit this view. A native-day enumeration discrepancy excludes execution supported solely by the import. An explicit outing confirmation or performed manual report can independently support that outing. |
| Comparable strength | Execution, individually supported movement, variation, equipment, load convention, group and ordinal, independent reps and kg | Achieved set RPE is optional. A kg value with a different convention stays separately labeled. |
| Comparable running | Execution, supported running task and known role, independent elapsed duration. Intervals require a reported work count and aligned achieved durations covering the prescribed work steps and every reported completed work repetition. | Session RPE and pace are optional. Partial coverage limits whole-period conclusions even if a single task is comparable. |
| Familiar-dose input | Comparable actual dose, completed task, explicit positive manageability | Optional achieved RPE stays unknown. A single eligible task is one input to a later baseline review. |
| Progression-review input | Comparable actual dose and an independent tolerance report | Negative tolerance is eligible information for review. It grants no increase. |

Every qualification exposes required, optional, missing and excluded inputs. A reviewed display can contain an unknown role or strength dimension. The missing dimension appears by name while confirmed execution, dose and tolerance retain their original support. A report of four work repetitions with three aligned timings retains all four repetitions and all three timings. Comparison, familiar-dose and progression review identify the timing shortfall.

The outing carries its native day's enumeration discrepancies separately from its receipt content. A partial acquisition permits individual outing review. A retained outing after an empty scan remains descriptive with a day count labeled `observed_only`. If execution relies on that import, the dependent qualifications carry `retained_after_empty`. The athlete's elapsed-time mask and tolerance statement remain visible. An explicit confirmation of the outing supplies independent execution evidence for that task while the day discrepancy remains open.

A partial strength session can contain completed, partial, explicitly unperformed and unknown sets. Each reported ordinal keeps its status and assertion identity. Only a completed or partial ordinal qualifies as performed set exposure.

Each view applies at task scope. Unresolved attribution, stale support or contradictory actuals can withhold task comparison while leaving the original observations available. Selecting representative history, determining outcomes, allocating a new dose and authorizing changes require later reviews.

## Synthetic hybrid week

The integration test reads the running-emphasis fixture for January 4–10, 2027 in Toronto. Four approved occurrences have manual reports. Acquisitions for other days remain unknown. [Executable rehearsal](../backend/tests/test_planning_evidence.py)

| Day | Current evidence | Resolution |
| --- | --- | --- |
| Mon 4 · gym | Partial manual session. Press warmup 5 × 20 kg, primary 5 × 42 kg at achieved set RPE 9, completed backoff with unknown dose, partial squat with 3 reps. The import supplies an inferred primary press of 5 × 42 kg and an extra 8-rep set. The press receipt confirms completion and kg, independently reports 4 reps and explicitly links the primary ordinal. | One gym performance, five task records. The linked press has one identity, 42 kg, RPE 9 and unresolved reps. The extra set remains source-only. The athlete reported that the session was unmanageable. |
| Tue 5 · easy | Manual completed, manageable outing of 1,250 s. Separate native outing of 2,300 m, 1,200 activity s, 1,150 moving s and 1,250 elapsed s. | Both records remain visible as potential duplicates. The native role is unknown. The isolated manual report supplies a comparable continuous dose with unknown session RPE. |
| Wed 6 and Thu 7 | No selected report or outing. | No inference of inactivity. |
| Fri 8 · controlled | Partial outing, 1,400 elapsed s and session RPE 6. The prescription includes three work intervals. | Actual work count, achieved interval durations and step RPE remain unknown. |
| Sat 9 | No selected report or outing. | No inference of inactivity. |
| Sun 10 · long | Explicitly missed, outing false. | The report remains visible with no performed long run. |

The week yields five performance records including the miss and both Tuesday records. Their count cannot answer how many workouts the athlete performed. A subsequent manual correction reports the primary press as partial for four reps. It preserves the original assertion and releases the old effective link. Its apparent agreement with the independent four-rep report cannot establish a new link.

## Writer inventory and E4.2C.2

### Review and approval

Every generalized block or familiar-week proposal stores a versioned `decision_inputs` object beside its prescription in the immutable revision. The cutoff is the proposal clock under the owner lock. The object captures the complete accepted projection at that instant, including the trusted owner, binding and status of each selected account, dates and calendars, classifications and comparison context, evidence and D1D contract versions, claims, qualifications, exclusions, missing fields, daily coverage, open issues, confirmation masks and manual assertion chains. It also stores the exact selected Garmin acquisition receipts as canonical JSON. The revision already identifies the approved base and immutable planning context.

Pass the same `Scope` used by the standalone reader when the athlete selects a particular period, source family, verified calendar or mapping. Without an explicit scope, the command selects the seven days starting at the context’s representative history start, in the planning zone. It selects the unique bound Hevy account and both training families of the unique bound Garmin account when available. Multiple bound accounts for a provider require an explicit selection. Unverified provider zones and comparison dimensions remain unknown. Approval repeats automatic account selection, so a newly bound source can invalidate a proposal even on an empty day.

```python
with session.begin():
    pending = plans.submit(cycle, head, FamiliarWeek(number=1), evidence_scope=scope)
    review = plans.preview(cycle, pending)
    print(render_review(review))
    inputs = review.candidate.decision_inputs  # Exact claims and reasons for each task.

with session.begin():
    receipt = plans.decide(cycle, pending, expected_head=head, choice="approve", command_id=key)
```

The command takes the owner row lock first and the cycle lock second. In the same PostgreSQL read-committed transaction, it checks the head and context and rereads every selected day, family and effective assertion using the current decision policy. The original cutoff labels the frozen read. The approval read includes evidence received since that cutoff. Any difference in the canonical decision inputs, including a source revision with identical totals, changed retrieval evidence, or a new issue on a previously empty day, requires a fresh proposal and athlete review. A failed approval writes no receipt and leaves the approved head in place. A successful receipt and its head advance commit together. An exact retry of a finalized command returns the original receipt.

Historical preview returns the original decision inputs. Replay regenerates the prescription from the pinned context, rule and base and verifies it with those same stored inputs. A pending proposal from before C.2 needs a fresh review. Archived proposals and finalized receipts retain their original representation. The cutoff and saved facts reproduce this particular review. The database cannot reconstruct an arbitrary earlier source state. [Command implementation](../backend/src/fitness_intelligence/db/plan_commands.py) · [Decision regressions](../backend/tests/test_frozen_planning_evidence.py)

### Writers participating in the owner lock

| Writer | Transaction boundary |
| --- | --- |
| Hevy initial history, incremental sync and reconciliation | The account advisory lock spans the run. Each workout upsert and each pending or resolved deletion takes the owner row lock before checking the binding and reading or mutating the reference, parent, children or tombstone. Checkpoints only record sync progress and supply no selected evidence. Provider reads and detail retries occur outside the owner-locked transaction. [Importer](../backend/src/fitness_intelligence/adapters/hevy/importer.py) |
| Garmin bounded import and enrollment | After provider verification and fetches, the account-locked importer takes the owner lock in its write-side binding resolution. Enrollment, activity and child replacements, and daily observations commit inside that transaction. The shared bounded path also covers intake and weight writes. [Importer](../backend/src/fitness_intelligence/adapters/garmin/importer.py) · [Binding](../backend/src/fitness_intelligence/adapters/garmin/binding.py) |
| Garmin historical import, coverage and reconciliation | Each `HistoryRun.write()` reacquires the owner lock under the session-level account lock. This covers activity and child saves, daily observations, coverage including empty scans and failed/partial acquisitions, and issue creation, update, reopening and resolution. Network calls occur between these transactions. [History](../backend/src/fitness_intelligence/adapters/garmin/history.py) · [Coverage and issues](../backend/src/fitness_intelligence/adapters/garmin/history_state.py) |
| Confirmations and manual executions | The trusted command takes the owner lock before checking effective support or appending a confirmation, correction or withdrawal. Manual execution and correction use owner then cycle, preserving original assertions and predecessor links. [Confirmations](../backend/src/fitness_intelligence/db/confirmations.py) · [Execution](../backend/src/fitness_intelligence/db/execution.py) |
| Planning context and plan decisions | Context capture takes the owner lock. Proposal and decision commands also lock the selected cycle. A competing writer for this owner waits through commit or rollback. Different owners use different rows. [Commands](../backend/src/fitness_intelligence/db/plan_commands.py) · [Owner lock](../backend/src/fitness_intelligence/db/owner_lock.py) |
| Bindings, mapping and source selection | The current source writers above cover changes to source content and adapter versions. Explicit classifications, verified zones and member comparison inputs are supplied for review and pinned to the proposal. Changing them requires a fresh proposal. There is no mutable comparison registry. Future registry, administration and direct SQL writers affecting existing owners must follow the same owner-lock protocol. |

Separate PostgreSQL connections exercise both lock orders through the Hevy importer and the planning command. Tests also exercise Garmin enrollment, a historical partial acquisition, and a new issue as the only change on an empty day. The richer projection informs the synthetic review. The familiar-week generator still uses the supplied representative baseline. Adaptive dose selection and operational coaching remain separate milestones.
