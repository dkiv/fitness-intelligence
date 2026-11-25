# Roadmap

## Implementation history

| Milestone | Status and evidence |
| --- | --- |
| M0 · Project foundation | Complete. FastAPI health endpoint, PostgreSQL, user identity model, Alembic, tests and local Compose. |
| M1 · Canonical data model and ownership | Complete. Canonical strength records, database-enforced ownership links and synthetic constraint and migration tests. Authenticated access remains a public-release dependency. |
| M2A · Hevy API contract and synchronization design | Reviewed and approved with adjustments. Established mapping, identity limits, account namespaces and synchronization criteria. [Integration design](hevy-sync-design.md) |
| M2B.1 · Schema and pure mapping | Merged. Source-account migration, checkpoints, tombstones and strict mapping tested with synthetic data. |
| M2B.2 · HTTP client and transactional importer | Merged. Private read-only client and local CLI support account-serialized historical and incremental import, atomic snapshots and safe checkpoints. Distributed fencing and unattended synchronization are deferred. [Operating instructions](hevy-importer.md) |
| M2B.3A · Live verification readiness | Merged. A bounded read-only check matched the bound account and mapped one live workout sample. That observation covers identity and sample shape. |
| M2B.3B · Controlled contract probe | Merged. The tool and runbook cover synthetic create, edit, reorder and delete operations in a controlled account. The controlled live synthetic lifecycle rehearsal remains unverified. [Rehearsal and limits](hevy-sync-design.md#m2b3b-controlled-lifecycle-rehearsal) |
| M3A · Strength analytics foundation | Merged through PR #5. The internal, owner-scoped Polars reports cover exercise progression, weekly volume and training consistency. [Metric definitions](strength-analytics.md) [PR #5](https://github.com/dkiv/fitness-intelligence/pull/5) |
| E1 · Deterministic training planner | Merged through PR #8. Pure generation and move review for the first two weeks of synthetic cycle A. |
| E2 · Persistence and approval | Internal PostgreSQL commands seal, preview, approve or decline E1 revisions and recover historical prescriptions. [Scope and invariants](training-plan-design.md#e2-persistence-and-owner-review) |
| E3 · Execution and first adaptive cycle | Internal two-week synthetic workflow with durable outcomes, verified J1 retrieval and approval-time revalidation. [Demonstration and coverage](adaptive-coaching-cycle.md) |

On November 22, 2026, the personal historical Hevy import completed locally with 303 workouts,
1,618 exercise entries and 4,818 sets. A repeat reconciliation and a read-only integrity audit
both passed. The personal records are held outside Git. This evidence covers the local import
and its integrity. Production synchronization and public access still require separate validation
and the safeguards in workstream I.

## Delivery sequence

A–J identify workstreams that can advance in parallel. The first coaching milestone is an
athlete-reviewed seven-day plan using strength history and feedback. With the M3A foundation in place,
start E alongside the initial evidence and periodization work in J. Use both for the first review cycle in F. Neither milestone requires live Garmin data,
nutrition history, a dashboard or provider write access. Development and tests use synthetic histories.

Research Garmin read eligibility (B) and Training API eligibility (G) alongside A. Validate
on-device record availability (C) independently. D incorporates each validated source as it
arrives. F can then use those additional observations. G adds delivery of approved plans and H
evaluates their outcomes. Apply ownership and privacy controls throughout, with I as the gate
for public access. A and the E1–E3 slices have internal implementations. The remaining acceptance criteria describe planned capabilities.

## Workstreams and acceptance criteria

### A · Strength analytics MVP

Build on M1 canonical records and the M3A foundation. Acceptance requires reproducible
exercise-level estimated one-repetition maximum (1RM) progression, weekly volume and training
frequency from normalized sets. Synthetic histories must reproduce expected results for
comparable exercises, document units and eligibility rules, distinguish missing measurements
from zero and exclude another owner's records. The MVP is an internal query and report.

### B · Endurance and recovery ingestion

B1 delivers a [local verification command](garmin-verification.md) and a
[documented Personal API contract and B2/B3 proposal](garmin-integration-design.md).
The operator verified the two-window probe and default macOS Keychain lookup.
[B2](endurance-recovery.md) adds canonical endurance and recovery storage and pure Garmin
mapping. [B3.1](garmin-importer.md) adds private enrollment and bounded activity and recovery
ingestion. The controlled local rehearsal verified one activity with children and one day of recovery, including replay and preservation of existing Hevy history. Personal enrollment supports independent profile evidence or a locally witnessed,
explicitly approved profile pin. B3.2 covers nutrition and body weight. B3.3 covers historical and incremental sync.

Validate Garmin eligibility, permissions and terms separately for personal use and commercial
deployment. Record which activities, running metrics, sleep, HRV and resting heart rate each
authorized read path provides. Implementation depends on that access decision. Accept each
supported feed when replaying and updating a synthetic activity or recovery observation yields
one user-owned, provider-independent record with units, time and provenance. Document unavailable
fields so planning can proceed with partial coverage.

### C · Nutrition and body-weight ingestion

The nutrition MVP uses the Garmin Personal API through B3.2. Its inputs are reported daily
calories and individual weigh-ins. Preserve source and local date, distinguish unknown intake
from explicit zero, and reconcile overlapping totals once per day. Original writer and scale
attribution require evidence. Health Connect is an optional future source if Garmin coverage
or observation semantics prove insufficient. Meal records and macronutrients are optional
extensions. B3.3 historical and incremental ingestion depends on review and a bounded live
rehearsal of B3.2.

### D · Unified athlete analytics

D1 first provides read-only longitudinal intake and weight summaries with coverage. Wearable
energy expenditure is an estimate. Reported total expenditure already includes its documented
components. Logged maintenance intake and physiological TDEE are distinct estimands. Packet 007
Model B and any calorie-target adjustment require separate scientific and engineering review.

Start with A and extend the same reproducible analysis as B and C deliver normalized records.
Acceptance requires an athlete-scoped report showing strength and endurance progression,
training exposure and consistency, recovery relative to individual baselines, and calorie
intake alongside weight trends for available dates. Show coverage and distinguish measured
values from estimates. Flag possible strength/endurance interference as a hypothesis with
supporting observations and uncertainty. Sparse history must leave baselines unknown.

### E · Canonical training plan and scheduling

Begin after A, using J to define the active block behind each week. Capture goals, preferences, available days, injury constraints and exercise
preferences. Accept the first milestone when a deterministic planner produces a seven-day
plan of structured strength and running sessions with explicit progression limits from the
same inputs and rules. An infeasible schedule must surface the conflicting constraints.
Preserve the original prescription and each approved revision, link completed sessions to
the applicable version, and distinguish missed sessions from unknown completion in adherence.

**E4.0 · Generalized planner design.** The J3I.1 candidate is ready for design review. Before freezing the contract, review the initial profile and action-specific evidence requirements, resolve re-entry and joint progression bounds, specify scoped execution confirmation, and pin synthetic fixtures and versioned requests/snapshots. Inspect existing migrations, trusted approval commands and E1/E3 replay tests before proposing persistence changes. Keep research previews, operational rule authorization and approval of a specific plan separate. E4.1–E4.5 are proposed follow-on milestones. Synthetic strength-and-running implementation can proceed independently of nutrition/fueling and additional recovery methodology. [E4.0 review decisions](research/curation/README.md#decisions-for-e40-review) · [Proposed milestone sequence](research/curation/j3i-001-integrated-hybrid-methodology.md#102-incremental-e4-sequence-proposal-not-implementation-authorization)

### F · Adaptive coaching MVP

Depends on A, E and the initial reviewed claims and evaluation cases from J. Summarize the week from planned and completed sessions and athlete feedback.
Accept a full review cycle when the athlete can inspect a proposed adjustment to the next
seven days, see the evidence, uncertainty and exact changes, and approve or decline. Enforce
conservative limits on progression and schedule changes before approval. A declined suggestion
leaves the schedule intact. Record the recommendation, decision, resulting version and later
outcome. Demonstrate the cycle with strength data alone and missing recovery signals. Add
running load, recovery and fueling guidance as B–D supply evidence for them.

### G · Workout publishing integrations

Research Hevy routine write authorization and Garmin developer eligibility for the Training API
while A proceeds. Verify structured workout and training-calendar permissions separately from
activity read access. Publishing depends on E, explicit athlete approval of the exact version
and destination, and authorized APIs. Separate provider adapters handle Hevy routine creation
and updates and Garmin structured workout and calendar publishing.

Accept each adapter when retrying the same approved version avoids duplicates, an update maps
to its intended remote item, and a partial failure shows which items succeeded and which need
reconciliation before retry. Keep the canonical plan and per-version delivery status available
through failures. Where writes are unavailable, accept a manual or export path when an athlete
can enter the approved week using its dates, exercises, sets and running steps.

### H · Personalized modeling and evaluation

Depends on D for longitudinal observations and E–F for versioned decisions and outcomes.
Estimate individual performance and recovery responses and energy expenditure from weight
trends and available intake. Document assumptions and uncertainty. Evaluate nutrition
estimation bias and mean absolute error (MAE) only where independent labels exist. Acceptance
requires evaluation on held-out observations with coverage, sample size and baseline comparison.
Link coaching suggestions and decisions to subsequent adherence and performance. Report the
limits of attributing those outcomes to the recommendation. Use J’s offline evaluations alongside
these longitudinal measures when reviewing coaching quality.

### I · Public-release hardening

Start security and privacy work with each data flow. Before exposing health data or provider
credentials, resolve identity from authentication, scope every query by that identity and pass
cross-tenant access-denial tests. Before public release, verify OAuth or applicable provider
authorization, least-privilege scopes, revocation and secret storage for each enabled adapter.
Demonstrate user data export and deletion, documented retention and backup handling, operational
monitoring without health payloads or secrets, and review of provider terms for the intended
deployment. Enable only the integrations cleared for that use. Strava remains out of scope.

### J · Scientific knowledge and longitudinal periodization

Start with E on the strength foundation. Scope the first corpus release to questions needed to
generate and revise a week within a multiweek block. Accept it when a reviewer can trace each
scientific assertion in a sample recommendation to a reviewed claim and source, inspect its
applicability and competing findings, and reproduce the evidence selection from the pinned
release. Practical programs and individual observations must retain their distinct provenance.

Accept the planning milestone when two successive seven-day schedules advance the same block
objective toward an athlete's goal or event. Demonstrate an approved session adjustment that
preserves the objective and a conflict that requires explicit block revision. Before accepting
the first adaptive cycle in F, evaluate it against versioned synthetic cases with expected
decisions and rationales. Repeat the evaluation on corpus, planner and explanation changes.
The [coaching science specification](coaching-science.md) defines the review criteria.
