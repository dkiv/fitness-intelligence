# E3 execution tracking and adaptive review

E3 runs the first two weeks of the synthetic eight-week press block through E1, E2 and
J1. The athlete can inspect the first prescription, approve it, record sessions, review the
next week's exact changes and approve or decline. Weeks 3–8 retain their block intents.
All numerical training parameters in the example belong to the fixture.

## Run the local demonstration

From the repository root, start an isolated PostgreSQL 17 instance. These commands use a
temporary container, a random loopback port and a dedicated database. Each demo invocation
creates a new synthetic owner and commits its decisions. The example clock advances from
January 2 to January 10, 2027. The normal command reads its clock from PostgreSQL.

```sh
docker run --detach --rm --name fi-e3-demo --publish 127.0.0.1::5432 \
  --env POSTGRES_HOST_AUTH_METHOD=trust --env POSTGRES_DB=fi_e3_disposable postgres:17
until docker exec fi-e3-demo pg_isready -U postgres -d fi_e3_disposable; do sleep 1; done
address=$(docker port fi-e3-demo 5432)
export TEST_DATABASE_URL="postgresql+psycopg://postgres@${address}/fi_e3_disposable"

cd backend
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic upgrade head
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic check
uv run python examples/adaptive_cycle.py --decision approve
uv run python examples/adaptive_cycle.py --hold --decision decline
uv run pytest
uv run ruff check .
uv run ruff format --check .
docker stop fi-e3-demo
```

The example reports two completed lifts, one partial 15-minute run and one unknown run.
Known coverage is 3/4 and completion among known outcomes is 2/3. All five prescribed press
working sets are independently attested at RPE 7. With positive feedback on both lifts,
Thursday changes from 2 × 6 to 3 × 6 at 30 kg. Monday stays at 3 × 5 at 30 kg. Both easy runs
retain their 20- and 25-minute prescriptions. Omitting Thursday's feedback holds the weekly
total at five. Declining leaves week 1 current.

## Command and data contracts

- Bind the synthetic owner in the trusted local process, as for E2. Use a short
  `Session.begin()` transaction for each operation. Start with `capture_context`,
  `create_cycle`, `submit(..., Generate(1))`, `preview` and `decide`.
- Call `record_outcome(plan_id, revision_id, week, slot, actual, occurred_at=...,
  command_id=..., workout_id=..., supersedes_id=...)`. The last two arguments are optional.
  `Actual` records an explicit outcome, athlete feedback, confirmed barbell press working-set
  ordinals, per-set RPE, optional repetitions and external kilograms, inferred counts, run
  duration in seconds and run RPE. The athlete identifies the logical slot and confirms the
  movement and equipment. Workout names, dates and imported counts never establish equivalence.
- The exact instant of performance selects the approving receipt in force in that cycle.
  An explicit miss or unknown uses the elapsed scheduled instant as its attribution anchor.
  A manual performance can deviate from scheduled time within the same local week. A supplied
  canonical workout must belong to the owner and have the reported start instant. Only one
  effective slot observation may use it. An identical performance instant also flags duplicate
  manual attribution. Split or combined sessions would need a separate identity model. Manual attestations supply the set and effort facts.
- `session_outcomes` stores the approved revision, logical week/slot, occurrence and recording
  instants, optional workout link and the version of the athlete report. Composite FKs enforce
  approved-decision lineage, correction lineage and workout ownership. A PostgreSQL trigger
  walks the approved ancestry at the occurrence instant. A later head, including a copied
  calendar, cannot steal an earlier execution. The owner lock orders competing writes.
- Retry the same command ID and intent to recover its original observation ID. A correction
  supplies a fresh command ID and the ID it supersedes. Unique root and successor constraints,
  a same-slot parent FK and immutability guards preserve a single append-only chain.
- `weekly_review(plan_id, week)` projects current observations across revision boundaries.
  It exposes the four slots, actuals, both timestamps, supporting observation and prescription
  IDs, the prescription in force at execution, evidence availability, elapsed flags and counts. A linked workout that has been deleted,
  lost all active source references or changed start time loses current support. Its observation
  remains available for historical replay. An athlete can supply an independent correction.
  The denominator for known coverage is elapsed slots. The denominator for completion is known
  outcomes, including partials and explicit misses. Upcoming sessions are displayed separately.
- `submit(plan, head, Generate(2))` supplies E1 with a derived review. Both whole press slots
  must be complete, every prescribed working ordinal independently confirmed with measured RPE
  within the fixture cap, and both lifts explicitly manageable. Inference, reported deviations
  and reported work outside the prescribed rep/load range prevent progression. Run completion
  contributes to adherence. A missing run report leaves its status unknown. Free-text feedback
  is displayed verbatim. Use structured fields for manageability, effort and deviations.
- Inspect `render_review(commands.preview(plan, proposal))`. It prints each local date,
  strength and running targets, actual reports and coverage, the week-to-week dose comparison,
  changes against the approved calendar, E1 findings, applicability and evidence gaps.
  `InfeasiblePlan.conflicts.findings` identifies blocked slots and the requested and available
  values. Losing both weekend windows leaves one available running day against two required.
- Submit, record, correct and decide acquire the E2 owner lock before the plan lock. Approval
  rechecks the frozen review, including the identities of observations, the current support for
  linked workouts and their references under row locks, the active context, head, dates and
  E1 replay. A relevant correction requires a fresh proposal even when totals stay the same.
  A move preserves its logical slot. An observed slot and an already-started day are protected.
  An approving receipt advances the head atomically. Declines and exact decision retries retain
  E2 semantics. SQL enforces lineage and immutability. Trusted commands perform domain validation.

## Evidence and historical replay

Migration `e301` adds a nullable sealed rationale to E2 revisions and the outcome table.
The E2 wire representation remains readable. New submissions reject external citation lists
and derive the press review from outcomes. Legacy context reviews remain decodable. Pending
legacy week-2 candidates and legacy candidates carrying unverified references need resubmission.
The E3 downgrade checks for stored rationales and observations before dropping either.

Each new rationale freezes its version, review facts, the J1 release ID, exact byte digest,
retrieval algorithm, structured query, ordered matches, related claims, result locators, gaps
and programming options. The operational query compares an extra weekly press set with holding
dose. Population and experience are unknown. Release `j1-screening-1` has zero approved claims.
The report explicitly identifies the evidence gap. Neither the one-set increment nor the
24-hour start-to-start rule has scientific validation here.

Approval repeats retrieval using the pinned release, verifies the exact stored selection and
checks every referenced claim revision against the current catalog's eligibility policy.
Historical previews render the frozen selection and annotate later ineligibility.
`commands.citing(claim_revision)` returns affected revisions for the bound owner.
The local process uses a single packaged release policy. To switch releases, finish outstanding
transactions and restart all local command processes with the new package. Concurrent deployment
of different policies and live corpus activation are outside this milestone.

## Evaluation and limits

| Cases | Exercised through the internal workflow |
| --- | --- |
| A1, A2 | Exact five/six set decision, both runs, per-set effort and workload, incomplete or inferred observations, missing feedback, known denominators and deterministic historical rendering |
| A3, A6 | Move, decline, later approval, retained Saturday conflict, new movement exclusions, insufficient running days and preserved heads |
| C2, C3 | Isolated invented intensity query, direct/indirect transfer, conflicting findings and locators, programming preference, gaps, withdrawal, reverse lookup and historical approval retry |
| D2, D3 | Ambiguous workouts, explicit attribution, late reports on either side of a move, source deletion, correction chains, cross-owner workouts and cross-plan or unapproved revisions |

PostgreSQL tests also cover transaction failure and competing writers. The C2 fixture tests the
selection and rendering machinery using invented studies about intensity. It supplies no evidence
for changing weekly press volume. These cases evaluate software behavior. Coaching effectiveness,
a public multi-user service, automated exercise matching, multi-block reprogramming (full A4),
event tapering (B1), recovery-signal coaching (C1) and longitudinal load equivalence (full D1)
remain deferred. E1's pure schedule-boundary and dose checks continue to cover A5.
