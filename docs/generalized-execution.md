# E4.2A · Manual execution of a generalized week

An athlete can rehearse a manual report against a specific approved occurrence in a synthetic familiar week. Use the dedicated preview owner, the original trusted `PlanCommands` and the approved weekly prescription from [E4.1](generalized-familiar-week.md). Execution reports describe performed work. They neither amend the prescription nor feed a progression operator.

## Attribution and correction

Supply the cycle ID, **originating approved week revision**, week number, logical occurrence UUID, timezone-aware instant, typed actual and command ID to `record_outcome`. Obtain the occurrence from the exact approved week preview. The command obtains the owner from its trusted binding and finds the approved head in force at the reported instant. That head must contain the week directly or carry its origin in the flat calendar. The origin must contain the named occurrence in this cycle/block/week. A title or date match supplies none of those identities.

A performed session can move within its seven local planning dates. Store the actual UTC instant, including when a late report crosses an intervening approval. Explicitly missed and unknown reports use the elapsed scheduled instant. Recording time comes from the trusted clock. A block-only, unapproved, future or unrelated occurrence cannot receive a report. An unplanned outing has no E4.2A slot. Generalized imported workout links, split/combined attribution and successor or replacement blocks remain outside this contract.

The first report is a root assertion. To correct it, send the complete replacement report with a new command ID and the current assertion ID as `supersedes_id`. Corrections can change the reported time within the eligible week and re-resolve the in-force head. An identical retry returns the original ID, even after a correction. A reused ID with changed content, stale parent or second active attribution for the same owner's performance instant conflicts. The original report and its two instants remain visible.

## Synthetic examples

In the running-emphasis example the gym occurrence contains ordered press and squat exercises. The athlete reports three squat reps on the first primary set and explicitly records that set as partial. Its achieved effort and load remain unknown. A separate report of a completed press set can record five reps at 42 total external kg and RPE 9 even when the prescribed load is 40 kg and the cap is 8. The report shows both deviations.

```python
from uuid import uuid4
from fitness_intelligence.planning.familiar_outcomes import (
    RunExecution, SetExecution, StrengthExecution, render_execution_review,
)

actual = StrengthExecution(
    status="partial", manageable=False, feedback="Stopped after squat",
    sets=(SetExecution(movement="squat", variation="standing", equipment="barbell",
                       group="primary", kind="working", ordinal=1, status="partial", reps=3),),
)
command_id = uuid4()
with session.begin():
    observation = plans.record_outcome(
        cycle, week_revision, 1, gym.occurrence, actual,
        occurred_at=gym.start_utc, command_id=command_id,
    )
```

A strength set is addressed by movement, variation, equipment, group, warm-up/working kind and ordinal. Reps, kg, actual load convention and achieved set RPE have independent field scope. A reported load requires its convention. Compare numeric kg only when conventions agree. Performed work can fall outside the target. A completed session alone leaves its individual set ordinals unreported.

For the familiar controlled run, `RunExecution(status="completed", role="controlled", confirmed_outing=True, elapsed_seconds=1900, session_rpe=Decimal("6"))` describes an outing. Its three instructed work bouts remain unconfirmed. To confirm structure, supply the independently reported work repetition count and/or ordered-step identities. For example, expanded index 2 is the first work bout, 3 the between-repetition recovery and 4 the next work bout. Each may have its own completion, seconds and achieved RPE. Optional distance is in metres and moving time in seconds. No achieved interval pace is derived.

## Weekly review

Call `plans.weekly_review(cycle, number)` and pass the result to `render_execution_review`. The result includes the block identity and approval, originating week revision, calendar head at the cutoff, exact prescribed sessions and all manual assertions recorded through that cutoff. Every assertion includes its own in-force head, occurrence instant, recording instant, command and predecessor. The last assertion in each chain is effective. An optional aware `as_of` cutoff replays the manual report as known then. Use a PostgreSQL read-only, repeatable-read transaction when several reads must share one snapshot.

In the synthetic test, the gym session is partial, easy and controlled outings are completed, and the long run is explicitly missed. Known coverage is 4/4 elapsed and completion among known is 2/4. The athlete reports one completed warm-up and three working sets with actual work, one partial. The working-set rep subtotal is eight across two sets with known reps. The backoff set has unknown reps. The two reported outings contribute 3,100 elapsed seconds. Those facts establish adherence and observed exposure. Comparable strength or running performance direction remains unassessed.

Upcoming occurrences contribute to neither denominator. A supported early performance counts as elapsed once it has been reported. An elapsed occurrence with no report has unknown status and empty history. An explicit unknown retains its assertion. Empty denominators yield null ratios. Corrections replace effective exposure once and leave earlier rendering available.

## Storage and handoff

Migration `e421` follows `b330`. Existing rows take outcome version 1 and keep their original payloads, slot checks and E301 attribution trigger. Version 2 reuses `session_outcomes.slot` for the canonical occurrence UUID string, `revision_id` for the in-force head, and adds `origin_revision_id` for the originating approval. The sealed origin supplies the block key and block approval. Both revision FKs include owner, cycle and approving choice. The version-aware trigger resolves effective calendar membership, occurrence, local week, status anchor and correction scope under owner-then-cycle locks. The existing uniqueness constraints, immutability and truncate guards continue to protect the chain. The trusted command validates typed measurement content. Downgrade takes a writer-excluding lock and refuses to discard any generalized assertion or origin reference.

**E4.2B** now supports field-scoped batch confirmation of supplied synthetic observations. A confirmation can reference a performed manual assertion and its exact in-force attribution. An import confirmation adds no session to the weekly report. [Scoped confirmation guide](scoped-observation-confirmation.md)

**E4.2C.1** joins this manual lineage with current D1D source evidence and E4.2B member confirmations on the synthetic principal. A superseded manual assertion retains its historical links and releases its effective attribution. E4.2C.2 freezes and revalidates the complete decision scope, including newly inserted facts and issues. [Hybrid-week rehearsal and writer inventory](planning-evidence.md)

[Execution contract and report](../backend/src/fitness_intelligence/planning/familiar_outcomes.py) · [PostgreSQL rehearsals](../backend/tests/test_familiar_execution.py)
