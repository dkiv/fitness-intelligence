# E4.1 · Synthetic familiar-week planner

E4.1 validates supplied session templates against one selected representative week of synthetic, confirmed history and places those sessions on a calendar. The caller supplies the block, its phase intentions and the selected observations. The three examples each use a six-week block. Finding an optimal block or constructing a personalized program automatically from imported training history remains outside this slice. The supported block length is 1–52 weeks. Each week has a phase intention, seven local dates and its own approval. A future intention has no executable prescription. [E4.0 design](generalized-hybrid-planner-design.md)

## Try the three histories

From the backend directory, run any of these database-free examples. Each prints the seven dated days with exact canonical prescriptions.

```sh
uv run python -m fitness_intelligence.planning.familiar_examples strength
uv run python -m fitness_intelligence.planning.familiar_examples running
uv run python -m fitness_intelligence.planning.familiar_examples balanced
```

| Ranked objective | Familiar week beginning January 4, 2027 in Toronto | Protection |
| --- | --- | --- |
| Strength first | Mon/Thu gym, Tue 20-minute easy run, Sun 30-minute continuous long run | Same-course, comparable-effort long run |
| Running first | Mon gym, Tue easy, Fri controlled intervals, Sun long run | Comparable squat at the same load and depth |
| Equal priority | Mon/Thu gym, Tue easy, Wed controlled intervals, Sun long run | Both comparison protocols |

Each gym visit reserves 26 minutes for preparation, transitions, ordered press and squat warm-ups and working groups, execution and rest. The controlled run takes 31 elapsed minutes plus three minutes to prepare. It has a ten-minute warm-up, three four-minute work bouts, two two-minute recoveries and a five-minute cool-down. A separately specified final recovery adds its full duration. [Runnable fixtures](../backend/src/fitness_intelligence/planning/familiar_examples.py)

## Inputs and placement

A context ranks outcomes, declares an IANA zone, equipped weekday windows, optional preferred weekdays, unavailable dates, fixed local session starts, fixed events and current task exclusions. Choose one complete synthetic representative week starting 7–28 days before the block. Each baseline template needs one distinct confirmed and manageable observed occurrence, with a support key, date, role and actual work. For strength the ordered actuals must match movement, variation, equipment, load convention, group, kind, ordinal, reps and kg. For runs the actual expanded step purposes and elapsed seconds must match. Inferred observations, missing members and ambiguous repeats fail initialization. An optional wider upper endpoint requires explicit confirmation of that jointly familiar upper workload in the synthetic report. The first slice accepts one representative week and a fixed baseline for the block.

**Effort support.** Each numeric prescription needs an athlete-confirmed familiar instruction for the same template and running role or strength task. The confirmation identifies the exact low, nominal and high RPE and the explicit execution cap. Strength matches each exercise, group and working or warm-up ordinal. Running matches each position in the expanded work/recovery sequence, including an explicit final recovery. An athlete can affirm the listed instructions together without supplying achieved RPE measurements. The synthetic fixtures specify those confirmations independently of the proposed instructions.

An optional observed RPE describes the effort actually reported for that set or step. It cannot establish the familiar target or stop cap. A reported effort above the cap blocks a repeat for that task under this rule. Manageability supplies tolerance feedback. If either the numeric instruction or its cap lacks support, the planner identifies the affected set or step and rejects the numeric proposal. Qualitative-only effort prescriptions remain deferred.

A block pins its key, start, phase per week, protected outcome protocols, exposure floors, optional elapsed start-to-start spacing and exact baseline templates. Count working sets and elapsed running seconds at the minimum permitted endpoints when testing floors. Strength targets include discrete load convention/increment, per-set maximum execution-time allowance, rest after each ordinal, preparation and transition allowances. Running reservations sum the maximum expanded step durations and preparation. Session and exercise notes remain on the canonical prescription. The program records protected opportunities. E4.2A reports completed work and deviations. Comparable outcome direction remains deferred.

Placement considers a five-minute local grid plus exact fixed starts. It resolves windows to UTC, places higher-ranked disciplines first, tries preferred and habitual weekdays, checks fixed events, equipment, restrictions, overlaps and declared elapsed spacing, and backtracks when necessary. It checks approved previous weeks and fixed future occurrences. Gaps in the spring clock change and ambiguous unqualified starts are ineligible. A fixed start in a repeated hour can supply its fold. Ambiguous window boundaries require an unambiguous replacement window. The default search stops after 20,000 examined placement options. A feasible result carries exact starts. A `PlacementFailure` reports the domain, examined count, limit, reasons and whether search was incomplete. A proved contradiction or exhausted finite domain can establish infeasibility within those constraints.

Each reservation must fit an equipped window, including preparation, transitions, rests and the largest allowed execution duration. Several disjoint reservations may fit the same day. Aggregate daily or weekly minute budgets, daily session-count limits, travel between locations, shared-equipment capacity and date-specific replacement windows remain deferred. The represented availability is weekly recurring windows, whole unavailable dates, fixed local starts and blocked event intervals.

## Trusted proposal, approval and replay

Use the existing local `PlanCommands` with an operator-bound owner and short `Session.begin()` transactions. For a persistence rehearsal provision the dedicated `db.familiar_snapshot.PREVIEW_OWNER` fixture user in a disposable migrated database and bind `FITNESS_PLANNING_OWNER_ID` to it. The normal command clock comes from PostgreSQL. For a dated rehearsal choose a future block start whose representative week has finished by today. The runnable examples above have a fixed synthetic clock-independent calendar.

```python
from uuid import uuid4

from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning.familiar import FamiliarWeek, ProposeBlock
from fitness_intelligence.planning.familiar_examples import example

block, context = example("balanced", start=next_monday)
with session.begin():
    plans = PlanCommands(session)
    context_id = plans.capture_context(context, expected_context=None)
    cycle = plans.create_cycle(block)
    opening = plans.submit(cycle, None, ProposeBlock())
    print(render_review(plans.preview(cycle, opening)))

# Retain command IDs with their complete intents for an exact retry.
block_decision, week_decision = uuid4(), uuid4()
with session.begin():
    plans.decide(cycle, opening, expected_head=None, choice="approve", command_id=block_decision)
    week = plans.submit(cycle, opening, FamiliarWeek(number=1))
    print(render_review(plans.preview(cycle, week)))

with session.begin():
    plans.decide(cycle, week, expected_head=opening, choice="approve", command_id=week_decision)
    assert plans.replay_familiar(cycle, week) == plans.current(cycle).candidate
```

Each eligible next week requires its own sealed proposal and simulated receipt, even if the targets repeat exactly. Generate contiguous weeks through the block’s final week. The command rejects started local weeks, holes, replacements and successor blocks. Historical `preview` reads the original payload and receipt. `replay_familiar` regenerates against the original context and approved base. The latest candidate stores references to earlier originating week revisions, plus the new week detail. Session occurrence UUIDs derive from cycle, block, week and stable template key. Load an earlier reference with `preview(cycle, ref.revision)` to recover its exact originating prescription.

Generalized proposals also seal the selected planning evidence. Pass `evidence_scope=` to `submit` for an explicit selection or use the representative-week default. Read `preview.candidate.decision_inputs` for the exact reviewed qualifications, missing support and assertion history. Approval rereads the entire selected scope under the owner lock. A new workout or issue on a previously empty day requires a fresh proposal. Historical replay retains the original inputs. [Frozen review contract](planning-evidence.md#writer-inventory-and-e42c2)

The v2 discriminator uses the existing immutable JSONB context/block/revision columns. Approval rechecks current head/context, retained future conditions, date and exact replay under the existing owner-then-cycle locks. The original receipt, decline and rollback semantics apply. V1 decoding, E1 rules, E2 approval and E3 attribution stay on their original path. E4.1 required no migration. E4.2A adds versioned manual execution through migration `e421`. Generalized requests on other principals are rejected. A request cannot select operational mode. Approval on the reserved synthetic principal simulates approval only. Explicitly adding reviewed operational rule authorization is future work. [Execution and correction guide](generalized-execution.md)

**Rule and replay compatibility.** New proposals pin `synthetic.familiar.hold.v2`. A sealed proposal under `synthetic.familiar.hold.v1` can reproduce its original dose-only result. Its pending approval requires a fresh proposal with the corrected rule and supported effort. An already approved block with missing effort support keeps its sealed baseline. Continuing with newly confirmed instructions requires a new synthetic cycle because E4.1 has no block-revision command. An exact retry of an existing receipt returns its original result. The schema and the separate E1/E2/E3 fixture path are unchanged.

### Rolling horizon still to implement

The domain tests exercise independent valid week numbers. The persistence test seals, approves and replays all six consecutive weeks under one synthetic clock to check serialization, dated receipts and earlier prescription identities. A phase intention or that fixture’s six approvals supplies no operational authority to prescribe six future weeks from stale history.

Later slices must restrict executable detail to the upcoming review window, keep subsequent weeks provisional, and pin the approved predecessor and the decision-time cutoff. Before generating or approving the next detailed week, recheck recent comparable actual work, source support, tolerance, interruptions, current restrictions and calendar commitments. Missing or stale evidence must limit the available actions, with a fresh review and a separate athlete decision for each dated week. Operational rule authorization remains a separate prerequisite.

## Archived conformance cases

The columns use the original case numbers from [M01](research/curation/j3b-001-strength-progression-methodology.md), [M02](research/curation/j3b-002-hybrid-block-methodology.md), [M03](research/curation/j3b-003-running-methodology.md) and [J3I](research/curation/j3i-001-integrated-hybrid-methodology.md). **I** identifies an implemented behavior. **P** marks a partially implemented case. **D** marks a deferred case. **X** marks a disabled operator or authorization. With E4.2C.2, the 94 archived cases have 22 implemented, 24 partial, 18 deferred and 30 disabled dispositions. Rejection of an unsupported command does not exercise a later operator’s eligibility test.

| Number | M01 T | M02 B-T | M03 T | J3I I |
| --- | --- | --- | --- | --- |
| 01 | I · familiar hold with confirmed group/ordinal effort and cap | I · balanced familiar week | I · familiar hold with confirmed effort and cap on each expanded step | P · balanced hold works, comparable outcome review deferred |
| 02 | P · top/backoff deviations scoped by ordinal, response deferred | I · strength emphasis with protected running | I · reject stale or absent running history | X · upper rep increase |
| 03 | P · set exposure follows each reported ordinal in a partial session, fallback programming deferred | D · outcome comparability | D · run/walk ledger | X · increase controlled work |
| 04 | P · explicit misses distinguished from unknown, rescheduling deferred | D · decline in protected performance | X · weekly duration increase | X · upper plus easy increase |
| 05 | I · scoped athlete confirmation preserves original inference and hold | X · set trial | X · long extension | X · optional joint exception |
| 06 | I · require matching equipment and load convention, withhold set comparison for unknown dimensions | X · load progression | D · distance novelty review | X · combined quality and lower increase |
| 07 | P · recent baseline enforced, restoration deferred | X · cumulative load change | X · work rep or duration change | X · aggregate set trial |
| 08 | X · low-count set trial | X · joint increase | P · exact recoveries implemented, additional rep operator disabled | D · adverse squat review |
| 09 | X · simultaneous set/load increase | I · reserved time grants no extra work | P · known role and aligned timing for every reported work repetition required, follow-up deferred | X · Q0 entry |
| 10 | P · partial-day outings supported, contradictory enumeration withholds import-only execution, protected-run decision deferred | P · fixed versus movable placement works, post-approval moves deferred | X · quality-duration progression | P · reported count and timed work preserved with explicit shortfalls, quality operator disabled |
| 11 | I · restriction or corrected source stales approval and requires fresh review | I · adjacent elapsed spacing | X · easy-duration progression | P · current projection retains inference and masks, joins each linked ordinal once, policy gate deferred |
| 12 | X · RPE-free progression | P · D1D inference stays descriptive, scoped athlete actuals support review, automatic baseline selection deferred | D · HR/conditions | D · re-entry after travel |
| 13 | P · decline and conflict supported, moves deferred | P · closure conflict and immutable execution supported, block revision deferred | D · pace comparability | I · restriction invalidates proposal and blocks affected work |
| 14 | P · frozen replay supported, withdrawal deferred | D · interrupted baseline | P · manual partial work and tolerance visible, adaptive review deferred | P · adherence/exposure visible, comparable outcome direction deferred |
| 15 | X · stall-driven set trial | I · reject stale context/restricted session | D · subsequent lower-body tolerance | I · finite exhaustion versus incomplete search |
| 16 | P · explicit exclusions enforced, symptom intake deferred | D · successor block | X · joint load/quality rise | D · goal revision and successor |
| 17 | — | D · context change stales approval, block amendment deferred | X · optional lower/easy rise | I · corrected set with identical totals stales approval, exact receipt replay preserved |
| 18 | — | I · late import and source correction checked under owner lock, frozen review retained | X · frequency redistribution | D · operational evidence withdrawal |
| 19 | — | D · preference tradeoff alternatives | X · first quality entry | I · legacy E1/E2/E3 regression |
| 20 | — | P · decline works, withdrawal deferred | X · uncertain Q0 entry | X · discrete load rise |
| 21 | — | I · elapsed coverage and known completion denominators | P · actual deviations available, comparable protected outcome review deferred | X · adaptive review budgets |
| 22 | — | D · block revision | I · adherence reported, comparable outcome remains unknown | X · run/walk fraction change |
| 23 | — | — | I · new restriction blocks approval | P · final/between arithmetic implemented, increasing rep count disabled |
| 24 | — | — | I · changed provider evidence requires fresh review, original evidence replays | P · scoped effort repeat checked, local versus shared difficulty review deferred |
| 25 | — | — | D · interruption/resumption | X · frequency redistribution |
| 26 | — | — | I · fixed start versus protected floor/window conflict | P · partial actual kept separate from approved target, adaptive review deferred |
| 27 | — | — | D · alternative proposals across competing goals | — |
| 28 | — | — | X · cumulative progression | — |
| 29 | — | — | P · upper duration/time checked, adaptive weekly ceiling deferred | — |
| 30 | — | — | I · existing fixture replay | — |

E4.2A implements generalized in-force attribution, append-only manual corrections and descriptive weekly review. E4.2B implements scoped batch confirmation and correction on supplied synthetic observations. E4.2C.1 joins D1D observations to effective confirmations and manual executions in one synthetic read transaction. E4.2C.2 seals the complete selected projection and revalidates it at approval under the shared owner lock. [Evidence rehearsal and writer inventory](planning-evidence.md) · [Execution guide](generalized-execution.md) · [Confirmation guide](scoped-observation-confirmation.md) · [Planning regressions](../backend/tests/test_familiar.py)

For local Hevy manifests and manual Garmin worksheets derived from sealed occurrences, see [G1B workout handoff](workout-handoff.md).
