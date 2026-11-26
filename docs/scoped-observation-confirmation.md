# E4.2B · Confirming displayed training observations

The trusted preview owner can confirm selected fields from several synthetic workouts in one action. The input is a supplied normalized projection for one owner and source account. Historical confirmation works before a plan exists. Each strength member uses the canonical workout, exercise and set UUIDs. A running outing uses the endurance activity's canonical workout UUID. Neither command reads from a provider or edits canonical workouts. [Typed contracts](../backend/src/fitness_intelligence/planning/confirmation.py)

## Preview and submit

Call `PlanCommands.preview_observations(account, facts)` on the dedicated synthetic binding used by E4.1. Each member carries its source, optional external reference and revision, workout start, mapping version, comparison key, completion provenance and exact displayed values. The ordered offers enumerate the canonical member, SHA-256 content digest and eligible fields. The batch digest seals the version, owner, account, ordered members and offers. Duplicate canonical members and duplicate ordinals in one exercise group are rejected.

For strength the athlete sees movement, variation, equipment, load convention, group, ordinal, repetitions and kg. The `completion` offer asks whether the athlete completed that specific set. The original provider completion timestamp may remain null. For running, outing, elapsed time, moving time, independent distance and reported work-repetition count have separate masks. Where achieved steps exist, masks identify each expanded step's status, duration and RPE separately, for example `step.2.elapsed_seconds`. Instructions are display context only. A 2,400-second outing with instructions for three six-minute efforts and session RPE 6 can establish the outing, selected summary fields and the separately reported session effort. The instructed repetitions, work durations and achieved step effort remain unknown.

### Two-workout rehearsal

The synthetic example uses three standing barbell press working sets at 40 total external kg and five reps in each of two workouts. Both workouts have historical completion inference and missing provider completion timestamps. The projection already supplies the UUIDs and original values. The athlete selects a common mask and reviews three exceptions.

| Workout | Primary group ordinal | Selection | Effective displayed fields |
| --- | --- | --- | --- |
| Feb 3, 2025 | 1 | Confirm displayed work | Completion, 40 kg, 5 reps |
| Feb 3 | 2 | Confirm completion only | Completion |
| Feb 3 | 3 | Confirm displayed work | Completion, 40 kg, 5 reps |
| Feb 5 | 1 | Confirm displayed work | Completion, 40 kg, 5 reps |
| Feb 5 | 2 | Exclude | None |
| Feb 5 | 3 | Uncertain | None |

With `source_sets` containing the six normalized facts, a trusted session and `plans = PlanCommands(session)`, the interaction is:

```python
from decimal import Decimal
from uuid import uuid4
from fitness_intelligence.planning import confirmation as c

display = plans.preview_observations(account, source_sets)
a, b, changed_later, d, excluded, uncertain = display.members
intent = c.prepare(display, ("completion", "kg", "reps"), exceptions=(
    c.Answer(member=b.member, disposition="confirm", fields=("completion",)),
    c.Answer(member=excluded.member, disposition="exclude"),
    c.Answer(member=uncertain.member, disposition="uncertain"),
))
# Show intent.display.members, intent.display.offers and intent.answers together.
batch_id = uuid4()
with session.begin():
    first = plans.confirm_observations(batch_id, intent, current=source_sets)

single = plans.preview_observations(account, (a,))
answer = c.Answer(
    member=a.member, disposition="confirm", supersedes=batch_id,
    fields=("completion", "kg"), reported=c.AthleteReport(reps=4, set_rpe=Decimal("7")),
)
with session.begin():
    plans.confirm_observations(uuid4(), c.prepare(single, (), exceptions=(answer,)), current=(a,))

revised = changed_later.model_copy(update={"reps": 3})
with session.begin():
    review = plans.confirmation_review(batch_id, current=(a, b, revised, d, excluded, uncertain))
    assert review[0].independent_report.reps == 4 and len(review[0].history) == 2
    assert review[2].state == "stale" and review[2].confirmed == {}
    assert review[3].confirmed["reps"] == 5
    assert plans.confirmation_receipt(batch_id) == first
```

The first member retains confirmed completion and displayed kg. Its corrected four reps and set RPE 7 have independent athlete provenance. The changed third member loses its import-backed support. The remaining members keep their answers. The original six-member receipt still shows exactly what was presented. The executable regression supplies the normalized facts and verifies the full workflow. [Synthetic rehearsal](../backend/tests/test_observation_confirmation.py)

## Receipts and current support

The command checks the trusted actor, expected predecessor per member, exact displayed digest, full current content and selected mask. A new command with any mismatch fails the whole batch. Replaying the same command and intent returns the sealed receipt after later corrections or source changes. A different intent under that ID conflicts. A correction provides the complete replacement answer for each affected member only. A withdrawal identifies its current predecessor and its original display, so it can succeed even when that source member is gone.

`confirmation_receipt` reads an immutable historical intent. `confirmation_review` follows the displayed members' correction chains to their current tips and compares them to supplied current facts. Each result includes the original facts, source hashes, masks, timestamps, links and answers. The current confirmed map contains only exact selected values. Unknown source fields are null on the original fact, and omitted eligible fields appear in `unconfirmed`. Exclusion, uncertainty and withdrawal are distinct. An independently reported value remains identifiable even if its import support becomes stale.

Content comparison is deliberately at member scope. A changed value, child, external reference, revision, mapping or comparison invalidates that member's import-backed mask. Deleted workouts, inactive references and absent members also lose support. A new displayed answer can confirm the revised facts. A replacement canonical child needs its own assertion. An old receipt always retains its original identities.

A confirmation can explicitly name a current, performed E4.2A outcome assertion. Its workout start, sport and prescribed set identity or running role and steps must agree. The link retrieves owner-bound cycle, week, occurrence, originating approval, in-force head and execution instant through E4.2A. Within that occurrence, each prescribed movement, variation, group and set ordinal accepts one source set. The command checks the entire proposed batch and existing effective member assertions. Repeated imported exercises and extra sets can be confirmed independently as historical training. A second workout cannot occupy the same linked performance. Linking writes zero execution assertions and contributes zero additional sessions to weekly adherence. Superseding the manual assertion ends the effective link while preserving the historical reference. A correction can remove or transfer an ordinal link in one batch. Withdrawal releases the ordinal. If older receipts already link two members to the same prescribed ordinal, review flags both with `ambiguous_set_link` and withholds their effective links until the ambiguity is resolved. Both members retain their independent confirmed fields and original receipts. [Manual execution contract](generalized-execution.md)

## Storage and E4.2C handoff

Alembic `e422` follows `e421`. One owner-bound receipt stores the verified actor, database recording time, command ID, intent digest and versioned JSONB display and answers. An insert trigger indexes the member and predecessor edges in the same statement. Foreign keys, unique roots and successors, the owner lock, and update, deletion and truncate guards protect history. The optional outcome FK retains its manual execution anchor. The downgrade locks both tables and refuses to discard confirmation history. Source IDs and the displayed evidence are frozen in the receipt so later canonical replacement or deletion cannot erase its meaning. [Migration](../backend/migrations/versions/e422_scoped_observation_confirmation.py)

E4.2C.1 now builds the displayed synthetic members from real D1D projection types. It reads current support and superseded receipts in the same read-only transaction as the canonical observations and manual outcomes. A changed mapping, invalidated source or withdrawn answer withholds the affected support. Historical independent reports remain attached to their original member.

E4.2C.2 must freeze the selected facts and exclusions, source scope, coverage, mappings, confirmation lineage, manual attribution and decision cutoff. Approval must revalidate that complete scope while coordinated with every relevant writer, including writers of new rows and newly opened issues. [Unified evidence and proposed coordination protocol](planning-evidence.md)
