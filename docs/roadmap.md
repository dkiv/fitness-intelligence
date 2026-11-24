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
| M2B.3B · Controlled contract probe | Merged. The tool and runbook cover synthetic create, edit, reorder and delete operations in a controlled account. The live rehearsal is pending. Personal historical import remains gated on review of the observations and separate operator authorization. [Rehearsal and limits](hevy-sync-design.md#m2b3b-controlled-lifecycle-rehearsal) |
| M3A · Strength analytics foundation | Implemented on a feature branch and under review at this roadmap revision. The internal, owner-scoped Polars reports are the foundation for A. [PR #5](https://github.com/dkiv/fitness-intelligence/pull/5) |

## Delivery sequence

A–I identify workstreams that can advance in parallel. The first coaching milestone is an
athlete-reviewed seven-day plan using strength history and feedback. Once A is available,
start E and deliver the first review cycle in F. Neither milestone requires live Garmin data,
nutrition history, a dashboard or provider write access. Synthetic histories support local
development while personal import gates are open.

Research Garmin read eligibility (B) and Training API eligibility (G) alongside A. Validate
on-device record availability (C) independently. D incorporates each validated source as it
arrives. F can then use those additional observations. G adds delivery of approved plans and H
evaluates their outcomes. Apply ownership and privacy controls throughout, with I as the gate
for public access. All capabilities below are planned except for the branch work identified above.

## Workstreams and acceptance criteria

### A · Strength analytics MVP

Build on M1 canonical records and the M3A foundation. Acceptance requires reproducible
exercise-level estimated one-repetition maximum (1RM) progression, weekly volume and training
frequency from normalized sets. Synthetic histories must reproduce expected results for
comparable exercises, document units and eligibility rules, distinguish missing measurements
from zero and exclude another owner's records. The MVP is an internal query and report.

### B · Endurance and recovery ingestion

Validate Garmin eligibility, permissions and terms separately for personal use and commercial
deployment. Record which activities, running metrics, sleep, HRV and resting heart rate each
authorized read path provides. Implementation depends on that access decision. Accept each
supported feed when replaying and updating a synthetic activity or recovery observation yields
one user-owned, provider-independent record with units, time and provenance. Document unavailable
fields so planning can proceed with partial coverage.

### C · Nutrition and body-weight ingestion

Validate what the upstream apps actually write and what Android Health Connect permissions and
history access allow. Accept the Kotlin bridge when permitted RENPHO-origin weight and
MyFitnessPal-origin daily calorie totals, where available, retain their dates, units and origin
across repeated syncs without double counting. Report days with missing intake as unknown.
The MVP reads existing records. Macronutrients are a later option conditional on availability.

### D · Unified athlete analytics

Start with A and extend the same reproducible analysis as B and C deliver normalized records.
Acceptance requires an athlete-scoped report showing strength and endurance progression,
training exposure and consistency, recovery relative to individual baselines, and calorie
intake alongside weight trends for available dates. Show coverage and distinguish measured
values from estimates. Flag possible strength/endurance interference as a hypothesis with
supporting observations and uncertainty. Sparse history must leave baselines unknown.

### E · Canonical training plan and scheduling

Begin after A. Capture goals, preferences, available days, injury constraints and exercise
preferences. Accept the first milestone when a deterministic planner produces a seven-day
plan of structured strength and running sessions with explicit progression limits from the
same inputs and rules. An infeasible schedule must surface the conflicting constraints.
Preserve the original prescription and each approved revision, link completed sessions to
the applicable version, and distinguish missed sessions from unknown completion in adherence.

### F · Adaptive coaching MVP

Depends on A and E. Summarize the week from planned and completed sessions and athlete feedback.
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
limits of attributing those outcomes to the recommendation.

### I · Public-release hardening

Start security and privacy work with each data flow. Before exposing health data or provider
credentials, resolve identity from authentication, scope every query by that identity and pass
cross-tenant access-denial tests. Before public release, verify OAuth or applicable provider
authorization, least-privilege scopes, revocation and secret storage for each enabled adapter.
Demonstrate user data export and deletion, documented retention and backup handling, operational
monitoring without health payloads or secrets, and review of provider terms for the intended
deployment. Enable only the integrations cleared for that use. Strava remains out of scope.
