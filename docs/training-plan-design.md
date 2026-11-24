# Canonical training plans

**Proposed design for workstreams E and F, with J supplying evidence.** The first deliverable is a
seven-day prescription an athlete can enter manually, review and revise within a multiweek block.
Strength history and athlete feedback are sufficient inputs. PR #6 established this product
direction. M3A supplies internal strength reports. E1 implements the pure planner for cycle A weeks 1 and 2. Approval and endurance
ingestion remain future work. See the [vision](product-vision.md) and [roadmap](roadmap.md).

## What the athlete reviews

A cycle gives the plan a purpose and horizon. An ordered block gives a week its objective, such
as increasing exposure to a chosen lift while maintaining two runs. The block records how to
recognize progress, weekly dose bounds and when to recover or assess. Only the requested week
needs detailed sessions. The athlete sees seven local dates, the purpose of each session,
allowed execution choices, the week's contribution to the objective and any uncertainty.
Approval makes this exact prescription current. Publication to an external destination would be
a separate, later decision.

Represent **linear** progressions with a sequence of week targets, **undulating** prescriptions
with different targets on successive sessions or weeks, and **block** periodization with a
succession of emphases. These can coexist. Record which feasible approach was selected and why
its demands fit the goal, experience, preferences and event date. The MVP needs one deterministic
generator for a reviewed hybrid template and a schema that can express all three approaches.
Comparative optimization and a library of programs can follow.

## Storage and relationships

Use typed SQLAlchemy 2 models following the existing OwnedRecord pattern. The proposed relational
spine makes ownership, approvals and execution links enforceable in PostgreSQL. Small, ordered
prescription values live inside their immutable parent as schema-versioned JSONB, validated by
closed Pydantic schemas. This avoids a table per target type. Use canonical decimal strings for
quantities in JSON and parse to finite, bounded Decimal values in the domain. Reject unknown tags
and fields. Retain a reader for each stored schema version.

| Proposed model | Fields and relationships |
| --- | --- |
| AthleteContext | Immutable revision, unique (user, sequence). Ranked goals with stable keys, measure, target and horizon. Optional target events with key, local date, discipline and priority. IANA zone, availability windows and time budgets by weekday, dated overrides, equipment, excluded movements/activities, preferences and attributable feedback. Structured hard restrictions are separate from preferences. A context change creates a revision. |
| TrainingPlan | Stable cycle ID, owner and nullable approved revision head. Cycle title, date range, goal/event keys and priority belong to the revision. MVP has one scheduling cycle active per owner, enforced by a partial unique index on the active flag. |
| BlockVersion | Plan ID, stable block key, version ID, context ID, local dates, goal/event keys, objective and success measure, ranked emphases, method and selection rationale. Ordered week intents give exposure floors/ceilings, progression and autoregulation limits, specificity, spacing, phase and event constraints. Multiple blocks can advance the same cycle goal. |
| PlanRevision | Plan ID, expected base revision (null for first), context ID, cycle intent, immutable input snapshot, rule/corpus versions, recommendation and assertion-level rationale. Each submitted revision is a complete candidate. One revision can introduce a block and its first week. Derive proposal status from the decision and current head. |
| RevisionBlock | Calendar manifest for one revision. Ordered, nonoverlapping effective local week ranges reference exact BlockVersions of the same plan. A mid-block revision can keep earlier weeks on the original version. A future week with no detailed schedule still has a block intent. |
| PlanWeek | Revision, week start, manifest entry and exact block version, one-based index relative to the original block start, seven day states, contribution to objective. Each day is scheduled or explicit rest. An ungenerated week has no row. Each revision copies its generated weeks and sessions in full. |
| PlannedSession | Week, revision, stable plan-local slot key, day, order, time window, reserved duration, discipline, intent, structured prescription. The key survives a move and distinguishes two sessions on one day. The exact row identifies a prescription in one revision. A replacement with different intent gets a new key. |
| PlanDecision | One per submitted revision. Athlete acting through trusted owner context, decision (approve/decline), timestamp, optional reason, command ID and intent fingerprint. Approval history defines when each revision was in force. |
| SessionOutcome | Append-only athlete assessment or correction with recorded time, execution date/time if known, exact approved revision and slot, completion state, deviations, optional feedback and same-owner canonical workout ID. Record source and confidence. A correction names its predecessor. One current primary association per logical slot and per linked workout. |

Relational keys use UUIDs. Every athlete-owned row, including association and decision rows,
has a non-null FK to users and a unique (user_id, id) target. Parent FKs also carry user_id.
Where a row names two ancestors, include the common lineage in a composite FK. For example,
a plan head and revision base target (user_id, plan_id, revision_id), a week targets its own
revision's manifest entry and exact block version, and an outcome targets (user_id, plan_id,
revision_id, slot_key). The workout target is (user_id, workout_id). Require the referenced
revision's approving decision for an outcome or head, using a composite FK to the decision
including the approved value. Enforce a unique (user_id, command_id) receipt and at most one terminal decision per candidate.
Serialize outcome recording and corrections on the same owner lock as approval. A correction can
supersede only the current outcome for the same slot. Maintain the current associations with
unique owner/plan/slot and owner/workout keys transactionally. Shared corpus references use release-scoped IDs. Filter every
read, history traversal, match, decision and write by trusted owner identity.

Enforce unique week starts per revision, logical slots per revision, and day/order per week.
Constrain positive durations, nonnegative positions, ordered dates and valid state tags.
Validate seven contiguous dates, containment in the effective block, unambiguous day/window
membership, phase coverage and complete payloads before sealing. For the MVP, blocks start on
local Mondays, contain whole weeks, and use half-open date ranges. Dated events may fall on any
day. Store approval and execution instants in UTC and keep the planning zone with the snapshot.
Resolve local windows to instants when checking hourly limits, including DST crossings. Surface
a missing or ambiguous wall time for review.

## Prescriptions and validation

| Value | Minimum contract |
| --- | --- |
| Strength exercise | Ordered plan-local movement key, display label, equipment and load convention. Ordered set groups have kind (e.g. warm-up, working), positive integer count, rep range, rest allowance and optional target effort on the 0–10 RPE scale. Allow absolute external kg, percentage of a pinned comparable reference with value/unit/measurement or estimation method, or effort alone. A working set contributes once to its movement's target. |
| Run | Ordered steps with purpose (warm-up, work, recovery, cool-down). Each step ends on one positive distance in metres or duration in seconds. An optional intensity range is tagged as seconds/km, bpm or perceived effort. Pace bounds use ascending numeric seconds/km, with the faster endpoint first. Interval groups repeat an ordered flat list a bounded positive number of times. Spell out whether a final recovery is included. |
| Execution bounds | Record nominal target and permitted interval for each adjustable dimension, plus a session cap and named block progression policy. A value within the approved range is an execution choice. The athlete can record actual work outside that range as a deviation. Changing the prescription, date, slot or range requires review. |
| Feasibility | Check exclusions, equipment, local time budgets including rests/transitions, collision and recovery spacing, weekly exposures, event protection and allowable change from the pinned baseline. Check worst permitted endpoints, including fastest pace and slowest duration for a distance target. If duration or a required baseline cannot be bounded, use a feasible time/effort prescription or return a conflict. |

Use a bounded set of named rules with typed parameters, units and versions. The block specifies
which metric drives each rule (for example, press working sets per week), the comparison window,
eligible observations, maximum positive change, combinations forbidden to rise together, approved
floor/ceiling, hold condition, and deload/taper exceptions. Compare the candidate with both its
approved predecessor and the available performance evidence. An increase requires the rule's
evidence preconditions. Check the permitted range against adjacent approved sessions and any
reserved boundary windows in neighboring block intents. When a neighbor has yet to be scheduled,
reserve the required spacing and recheck it on generation. A candidate that cannot satisfy a
hard rule returns the conflicting constraint IDs, requested and available values, and feasible
options where known. The athlete can review a change of objective separately. Hard restrictions
continue to apply.

## Inputs and domain interfaces

Use the existing owner-scoped query and its Polars outputs at the application boundary. Project
a small planning input with an as-of instant, Period and IANA zone, series/load mapping, completion
mode, working-set counts and measurement coverage. Preserve the selected values, comparable keys,
reference IDs and provenance used in the recommendation. The future replay uses this snapshot even
if an importer replaces child rows. A workout count can include an open or empty workout. The
Epley value is an estimate and inferred set completion is labeled. Missing comparable load,
running, recovery or feedback remains unknown. See [strength metric definitions](strength-analytics.md).

| Proposed internal interface | Result |
| --- | --- |
| capture_context(owner, inputs, expected_context) | Validated new context revision or stale input. Serialize context updates and approval on the same owner row. |
| propose_block(context, cycle, intents, rules, evidence) | Block candidate with objective, week envelopes, method rationale, alternatives and event constraints, or named conflicts. |
| generate_week(context, block, week_start, facts, neighbors, rules, evidence) | Pure candidate with seven dated days, structured sessions, exact totals, rationale or conflicts. Ordered template slots and stable tie-breaks resolve equally feasible schedules. Same inputs yield the same semantic content. |
| propose_change(approved, requested_delta, facts) | A session-only candidate retaining the block version, a block-plus-weeks candidate with the material effects, or a conflict. A structured review supplies the same inputs whether initiated by athlete feedback or a future conversation tool. |
| submit(owner, expected_head, candidate) / preview(owner, proposal) | Seal contents and return the exact before/after changes, prescriptions for manual use, retained objectives, rationale, limits and pinned inputs. Reference-only identity changes between two copied sessions do not appear as training changes. |
| decide(owner, proposal, expected_head, decision, command_id) | Single transactional decision. Reads current or historical weeks by owner, plan and revision. Only a trusted athlete action can invoke approval. |
| record_outcome(owner, approved_session, occurrence, assessment) | Athlete-confirmed match or attributed manual result, including a run. Unknown, missed, partial and completed remain distinct. Record the applicable revision and any later correction. |

These are internal domain and application contracts. A future synchronous FastAPI route would
resolve the principal, validate Pydantic input and delegate using a request-scoped session.
Authenticated isolation tests precede any health-data endpoint.

## Approval, revisions and execution

1. Build proposals against an explicit current head. The complete calendar is small enough to
   copy for a cycle. Reuse immutable block versions. Compare by logical key and show additions,
   removals, moves, target changes, block changes and affected future weeks. A block change
   that affects a scheduled future week must include its validated replacement or an explicitly
   displayed withdrawal. Previously started days and recorded outcomes retain their prescription.
2. Construct parent and children in one transaction. Lock the parent, validate the complete
   stored candidate, then seal. A database guard serializes
   child writes with sealing on the revision row and forbids subsequent child insert, update,
   delete or reparenting and edits to the sealed parent. Standalone context and block snapshots
   are insert-only. The head can reference only a sealed revision with an approving decision.
   Explicit owner erasure uses a separate privileged, audited path.
3. On decision, resolve owner, lock the owner and plan in a fixed order, check the command
   receipt first, then inspect the proposal. Require the exact sealed candidate and base. For
   approval, recheck current context, safety bounds, elapsed days, execution links and evidence
   withdrawals under the current release policy. A stale candidate or changed prerequisite
   returns a conflict and requires a fresh preview. Do not auto-rebase. Record a decline and
   optional reason without moving the head. An unreviewed proposal never expires into approval.
4. Insert the decision and compare-and-swap the head in one explicit transaction. A fault rolls
   both back. Serialize competing decisions, with at most one approved successor of a base.
   Retrying a command with identical intent returns its prior result. Reusing its ID with a
   different decision or deciding an already finalized proposal differently returns a conflict.
5. Match execution by the approval history in force at the execution instant and the stable slot.
   A late import never migrates an old outcome to today's head. When time, identity or match is
   ambiguous, request athlete attribution and keep adherence unknown. A source tombstone makes
   that observation unavailable for current reporting. Preserve the historical basis and flag
   it for review. An absent import alone cannot mark a session missed.

## Worked cycle A — eight-week press specialization

This invented fixture has a primary press assessment in week 8 and a secondary goal of retaining
two easy runs each week. Availability is Mon/Thu 40 minutes for strength, Tue/Sat 30 minutes
for running, with Sun 30 minutes as a fallback. Wed/Fri are unavailable. All windows start at
09:00 local time. The prior synthetic week contained five confirmed press working sets at a
known, tolerated load. The athlete prefers the same exercise and reports both lifts manageable.
The following limits belong to the fixture. They require separate review before operational use.

| Week | Block intent | Press working sets | Running commitment |
| --- | --- | --- | --- |
| 1 | Establish comparable press exposures | 5 over two days | 20 + 25 min easy |
| 2–3 | Accumulate, holding load when adding a set | 5–6, at most one additional set per week | Same two runs |
| 4 | Deload | 4 at reduced effort | Two 15-min easy runs |
| 5–6 | Emphasize assessment movement | 5–6 over two days, same increase cap | Two 20-min easy runs |
| 7 | Reduce volume before assessment | 4 | Two 15-min easy runs |
| 8 | Repeat a submaximal press assessment in the second exposure | 3 including assessment, record load/reps/effort | Two 15-min easy runs outside the assessment window |

The generator first fills week 1. After reviewing its outcomes, it fills week 2 under the same
block version. Each lift reserves 40 minutes, includes one easy warm-up set of five and allows
up to 3 minutes between working sets. The athlete's comparable working load in this fixture
is 30 kg. Use 15 kg for the warm-up. All working sets below use that load and an effort cap of RPE 7. The run steps use
effort bounds of 2–4/10. Warm-ups and cool-downs are included in the listed time.

| Local date (week 1 / week 2, 2027) | First approved week | Candidate for week 2 |
| --- | --- | --- |
| Mon Jan 4 / 11 | Press 3 × 5 | Same |
| Tue Jan 5 / 12 | 5 min warm-up, 10 min easy, 5 min cool-down | Same |
| Wed Jan 6 / 13 | Rest | Rest |
| Thu Jan 7 / 14 | Press 2 × 6 | Press 3 × 6 if both exposures were completed within cap and feedback supports it, else retain 2 × 6 |
| Fri Jan 8 / 15 | Rest | Rest |
| Sat Jan 9 / 16 | 5 min warm-up, 15 min easy, 5 min cool-down | Same |
| Sun Jan 10 / 17 | Rest | Rest |

The proposal resolves the Thursday condition **before** review. With the qualifying week 1
observations the athlete sees six working sets, unchanged load and 45 minutes of running.
With missing feedback they see five working sets and an explanation of the hold. If Saturday
becomes unavailable, moving its 25-minute run to Sunday fits this fixture's windows and a
24-hour start-to-start spacing rule before Monday strength. The preview shows “January 16 →
January 17, 09:00, 25 minutes easy” with the three run steps intact. The diff moves one slot and retains
the block. Declining keeps Saturday scheduled and flags the availability conflict. If both weekend windows disappear, the only
remaining running slot has a 30-minute cap. Return a conflict between two required run days
and one available day. Reducing the maintenance commitment requires a block proposal.

## Using the E1 domain planner

From the backend environment, pass frozen values to the internal Python API. Select week 1
as the predecessor and pass a normalized review of its two logical press slots. Each effort
entry represents one confirmed prescribed working set. Use `None` for a confirmed set with
unknown effort. Inferred sets have their own count. The caller supplies the attribution,
completion status and as-of instant. The review is scoped to the predecessor's block version
and local week start.

```python
from datetime import UTC, datetime
from decimal import Decimal

from fitness_intelligence.planning.planner import (
    Exposure, WeekInputs, WeekPlan, WeekReview, generate_week,
)
from fitness_intelligence.planning.press_block import Availability, PressBlock

block, calendar = PressBlock(), Availability()
first = generate_week(WeekInputs(block, calendar, 1))
assert isinstance(first, WeekPlan)
review = WeekReview(
    block.version, block.start, datetime(2027, 1, 10, 18, tzinfo=UTC),
    Exposure(completed=True, confirmed_rpes=(Decimal(7),) * 3),
    Exposure(completed=True, confirmed_rpes=(Decimal(7),) * 2),
    both_manageable=True,
)
second = generate_week(WeekInputs(block, calendar, 2, previous=first, review=review))
assert isinstance(second, WeekPlan)
assert (second.press_sets, second.running_seconds) == (6, 2700)
```

Each result is a candidate or a set of named conflicts. Day entries carry the local date and
ordered sessions, with an empty tuple for rest. Run steps use seconds and perceived effort.
Every step in an interval group repeats, including a final recovery if listed. Strength
sessions reserve the full fixture allowance including warm-up, rests and transitions.
Prescriptions use absolute external kilograms. The fixture assumes a barbell press and uses
America/Toronto as its default IANA zone. Each permitted day has one local start and a
duration budget. A dated override takes precedence over the recurring window.

The generator tries Saturday for the longer run and uses Sunday when Saturday is
unavailable for running. `propose_move` reviews one slot against the updated calendar and
returns its old and new date/time in the rationale. The neighboring Monday uses its local
strength window, or the template's 09:00 reservation. Supply `fixed_next_monday_start` to
pin an already scheduled neighbor. Week 2 rechecks the actual week 1 run dates against
its first press. `change_run_commitment` identifies the affected block intents and detailed
weeks for review. Pass any generated later weeks with `later_weeks`.

All progression bounds belong to this synthetic fixture. The standard generator only adds
the conditional Thursday set. An explicit week 2 Thursday dose is checked against the same
evidence, the predecessor and the entire approved rep/load range. Structured rationale
pins the synthetic rule version and reports the observations and bounds used. Weeks 3–8
carry intents only. Approvals, ingestion and evidence-backed programming remain later work.

## Worked cycle B — event and taper

A second invented cycle lasts four weeks and prioritizes a Sunday 5 km event in week 4. Its
first three weeks use one maintenance lift and two runs. One run in week 2 has a 5-minute
warm-up, three repeats of (2 minutes work, 2 minutes easy) and a 5-minute cool-down, totaling
22 minutes. In week 4 the event counts as one run. Reserve the final two days before the event
for recovery, and use one short easy run earlier in the week. A missed interval session in week
3 is recorded against its original prescription. Adding it on Friday of week 4 violates the
reserved days. The review can retain the taper and explain the deviation. Changing the event
or its priority would change the block. Neither an HR baseline nor provider delivery is needed.

## Implementation and acceptance

1. **Pure domain slice.** Type the context, block envelope, strength/run prescriptions, seven-day
   result and conflict result. Generate the first two weeks of cycle A from frozen inputs. Accept
   when totals, bounds, dates, hold path, manual-entry detail and infeasible fallback reproduce
   the [evaluation cases](coaching-evaluation-design.md).
2. **Persistence and review.** Propose additive Alembic revisions for context, cycle, block and
   candidate/calendar tables, then decisions, guarded heads and outcomes. Resolve circular FKs
   after table creation. Existing workout rows require no backfill. Downgrade in reverse
   dependency order, removing heads/guards before their targets. Preflight nonempty plan history
   before destructive downgrade and document export/erasure handling. Verify prior-head → head
   → prior-head → head with synthetic owners on disposable PostgreSQL, including faults, retries,
   sealing, cross-owner and wrong-plan links.
3. **Evidence and first coaching cycle.** Use the [knowledge contract](scientific-knowledge-design.md)
   and reviewed initial claims alongside the rule/template release. Show a versioned proposed
   adjustment, a decline, a later approval, and a manual running result linked to the prescription
   in force. Release requires the [golden case gates](coaching-evaluation-design.md#release-gates).

**Later and unresolved.** Decide with reviewed cases which numerical caps, progression baselines
and autoregulation bounds are fit for each population. Calibrate estimated duration for more
complex sessions. Split/combined completions, travel across time zones, overlapping cycles and
midweek block switches require additional semantics. Canonical endurance ingestion, provider
publishing, optimization across many templates and conversational explanations can follow the
manual review cycle independently.
