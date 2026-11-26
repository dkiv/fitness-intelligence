# E4.2C.1 · Unified planning evidence

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
| Descriptive exposure | Retained observation or performed manual report | Completion, exact identity for comparison, dose or effort. Field status still applies. |
| Confirmed execution | Direct source evidence of execution (timestamp or retained outing) or scoped athlete evidence of completed/partial work | Dose, intensity and task comparison. An inferred completion alone is insufficient. Conflicting execution, unresolved activity support and potential double counting limit this view. |
| Comparable strength | Execution, supported movement/variation, equipment, load convention, group and ordinal, independent reps and kg | Achieved set RPE is optional. A kg value with a different convention stays separately labeled. |
| Comparable running | Execution, supported running task/role, independent elapsed duration. Intervals also require actual work count and aligned durations for the prescribed work steps. | Session RPE and pace are optional. Partial coverage limits whole-period conclusions even if a single task is comparable. |
| Familiar-dose input | Comparable actual dose, completed task, explicit positive manageability | Optional achieved RPE stays unknown. A single eligible task is one input to a later baseline review. |
| Progression-review input | Comparable actual dose and an independent tolerance report | Negative tolerance is eligible information for review. It grants no increase. |

Every qualification exposes required, optional, missing and excluded inputs. Unresolved attribution, stale support or contradictory actuals can withhold task comparison while leaving the original observations available. These views assess individual task evidence. Selecting representative history, determining outcomes, allocating a new dose and authorizing changes require later reviews.

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

The read transaction supplies a coherent rehearsal. An approval transaction needs stronger coordination because a source writer can commit after the read.

| Writer | Present transaction and locking boundary |
| --- | --- |
| Hevy initial history, incremental sync and reconciliation | One session-level advisory lock serializes a source account across commits. Upserts run per workout. Parent and reference changes and replacement of changed exercise/set children commit together. Metadata-only updates can retain child IDs. A separate deletion transaction records a pending or timestamped tombstone and, when resolved, marks the reference and workout deleted. Checkpoint and reconciliation transactions are separate. [Importer](../backend/src/fitness_intelligence/adapters/hevy/importer.py) · [Account lock](../backend/src/fitness_intelligence/adapters/local_account.py) |
| Garmin bounded import and binding | The account advisory lock spans verification and the bounded write. The write transaction rechecks binding with a row lock where applicable and saves the selected activities, children or daily observations. Accepted updates can replace split/step collections. Sparse or conflicting children follow the retention and reconciliation rules. [Importer](../backend/src/fitness_intelligence/adapters/garmin/importer.py) · [Persistence](../backend/src/fitness_intelligence/adapters/garmin/persistence.py) |
| Garmin historical import, coverage and issues | The same account lock spans multiple database transactions. Individual activity saves, daily feed writes, partial/failure flags and final converged listing coverage can commit at different times. Issue creation, reopening, digest updates and resolution use the calling transaction. An issue or empty-scan receipt can change eligibility without changing an existing workout. [History](../backend/src/fitness_intelligence/adapters/garmin/history.py) · [Activity windows](../backend/src/fitness_intelligence/adapters/garmin/history_activities.py) · [Coverage and issues](../backend/src/fitness_intelligence/adapters/garmin/history_state.py) |
| Mapping, comparison and source selection | Importers write adapter versions and source evidence in their canonical-data transactions. D1D template classifications, verified source zones and C.1 comparison mappings are inputs supplied per query. There is currently no comparison registry writer. A later change in the selected inputs or mapping policy can change eligibility with identical canonical values. |
| Athlete confirmations | The trusted command locks the owner, validates current member tips and explicit links, and inserts one immutable receipt. PostgreSQL indexes member/predecessor edges in the same transaction. Corrections and withdrawals append receipts. [Commands](../backend/src/fitness_intelligence/db/plan_commands.py) · [Member support](../backend/src/fitness_intelligence/db/confirmations.py) |
| Manual execution, context and plan decisions | Trusted planning commands take the owner row lock and then the cycle lock where applicable. Execution corrections append assertions with predecessor, origin and effective head. Approval changes the head and records its receipt atomically. Ingestion currently uses its own account lock. [Execution](../backend/src/fitness_intelligence/db/execution.py) · [Approval](../backend/src/fitness_intelligence/db/plan_commands.py) |

**Proposed C.2 protocol.** Reuse the existing owner row lock for each transaction that mutates selected evidence, binding, coverage, reconciliation, mappings, confirmations, manual outcomes or plan context. An importer that needs the account advisory lock acquires it first, then locks the owner before reading for mutation or writing in each database transaction. Planning commands lock owner before cycle. Hold the owner lock through commit and keep provider I/O outside the owner-locked transaction. Any future writer affecting the same scope must participate.

At proposal, freeze the decision cutoff, selection policy and versions, trusted owner, accounts, period, verified calendars, comparison inputs and Hevy classifications. Seal exact eligible and excluded facts, IDs and clocks, support digests, missing categories, coverage receipts and open issues, confirmation commands/field masks and manual assertion lineage with approval identities. Keep the original sealed input with the decision for replay.

At approval, acquire the owner lock first in a read-committed transaction. After acquisition, reread **the entire selected scope** on that transaction, including previously empty days and source families, and compare it with the frozen inputs. Check current mapping/policy versions and the existing plan head and context in the same transaction. On a material change, require a fresh proposal and review. A writer committing before lock acquisition is visible to the reread. A later writer waits until the decision commits. Hashing only the previously returned rows would miss a newly imported workout, a newly opened issue or a new confirmation.

C.2 owns this protocol, frozen decision inputs and approval-time revalidation. Operational rule release, adaptive progression and physiological estimation remain outside C.1. D1E retains ownership of performance analytics.
