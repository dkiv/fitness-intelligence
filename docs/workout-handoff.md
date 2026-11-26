# G1B · Deterministic workout handoff

Export one scheduled occurrence from its originating E4.1 familiar-week revision. The local result is either a strength manifest with Hevy preview arguments or a running worksheet for Garmin Connect. Both carry the original effort ranges and execution caps. The source is limited to E4.1's dedicated synthetic fixture owner. An operationally approved prescription requires a future authority model. [E4.1 plan and approval contract](generalized-familiar-week.md) · [Provider feasibility and rehearsal plans](workout-publishing-feasibility.md)

## Complete synthetic examples

These two files were exported from the same approved **balanced** fixture week in disposable PostgreSQL. The template IDs in the strength example are invented.

- [Hevy strength manifest, complete JSON](examples/g1b-hevy-manifest.json) · Monday, January 4, 2027 at 18:00 in Toronto. Standing barbell press then squat. Each exercise has one warm-up, two primary sets and one backoff set. The shared rest timer is unset because the rest after the final set differs. The exact per-set rests and RPE caps appear in the exercise notes.
- [Garmin controlled run, complete worksheet](examples/g1b-garmin-worksheet.txt) · Wednesday, January 6 at 18:00 in Toronto. Ten minutes warm-up, three four-minute work bouts, two two-minute recoveries, five minutes cool-down. The run takes **31 minutes**. Preparation takes three more minutes, for a **34-minute** calendar reservation.

## Read a sealed occurrence

Use an existing owner-bound `PlanCommands` in a short transaction, with the plan, **originating week revision** and occurrence UUID from its review. The source function reads the stored candidate, decision and original context. The current head may have advanced. Block-only and declined revisions cannot supply a handoff. A proposal awaiting a decision produces `unapproved-preview`. An approving fixture receipt produces `synthetic-approved-fixture`. Both carry `publication_authorized=false`. Delivery and execution evidence belong to separate workflows.

```python
from fitness_intelligence.handoff.prescription import from_revision
from fitness_intelligence.handoff.hevy import VerifiedTemplate, hevy_manifest
from fitness_intelligence.handoff.garmin import garmin_worksheet

strength = from_revision(commands, cycle_id, week_revision_id, gym_occurrence)
# Fixture demonstration only. For a real destination each entry needs independent verification.
mappings = (
    VerifiedTemplate(movement="press", variation="standing", equipment="barbell",
                     load_convention="total-external-kg", template_id="synthetic-press"),
    VerifiedTemplate(movement="squat", variation="standing", equipment="barbell",
                     load_convention="total-external-kg", template_id="synthetic-squat"),
)
manifest = hevy_manifest(strength, mappings)
print(manifest.canonical_json())

running = from_revision(commands, cycle_id, week_revision_id, run_occurrence)
print(garmin_worksheet(running).render())
```

The immutable source includes the fixture owner, cycle, block and week revision, rule, occurrence, UTC instant, local date/time with offset, IANA zone and typed prescription. The prescription SHA-256 covers the canonical prescription JSON. Identical content in two slots can share this digest. Use the owner, cycle, revision and occurrence to identify the scheduled prescription. The full export digest (`handoff.digest()`) covers the canonical UTF-8 JSON including identity, approval state, translation policy, instructions, warnings and mapped IDs. Re-exporting the same inputs yields the same bytes. A new receipt changes the export digest while preserving the prescription digest. For pre-correction v1 fixtures the handoff also flags the older effort-validation rule.

## Hevy integration decision

Fitness Intelligence owns the canonical prescription, its revision history and its progression constraints. A Hevy routine is a delivery copy. An athlete saving or editing it supplies no evidence of workout completion or authority to advance a load.

The backend uses its existing deterministic Hevy REST importer for reproducible historical acquisition and analytics. [Hevy importer](hevy-importer.md)

Hevy MCP is the preferred interactive integration for the conversational coaching agent. Use its connected tools for exercise discovery, routine preview, athlete-initiated save, separately authorized updates by routine ID, and delivery reconciliation. If a required capability is unavailable, document the limit and stop that operation. A custom REST publishing adapter is deferred unless a demonstrated MCP limitation warrants a separate design decision.

## How the coach can use the Hevy manifest

1. Use FI’s own export or compare the received manifest with its independently retained export digest. Read the classification, blockers and limitations. A blocked manifest has `preview_arguments=null`. Supply independently verified destination-template mappings for the exact movement, variation, equipment and weight-entry convention. Missing, conflicting or reused IDs block the whole routine. Name similarity supplies no mapping.
2. For a separately authorized future handoff, show the athlete the destination and any manual cues. Pass **only** the existing `preview_arguments` object unchanged to `render_hevy_routine`. Keep FI identifiers, receipts and canonical history local. Treat notes as prescription text. Preserve the exercise and set sequence. Do not make up an ID, adjust a target, create a custom exercise, or invoke a direct save.
3. The athlete compares the preview and chooses whether to save. The current fixtures are for local inspection. For a later live rehearsal, independently review the write scope and obtain explicit authorization for the destination, single object, update, readback and cleanup. Reconcile the saved routine by provider ID and content. A displayed preview or ambiguous save cannot establish delivery. [Official preview tool](https://mcp.hevy.com/docs)

The field-level policy preserves kg using the verified template's convention, including per-hand kg with no doubling and bodyweight with no external weight entry. A variable rep target uses the MCP rep range and puts its nominal value in the notes. A load range blocks preview because Hevy offers a single weight per set. A uniform rest maps to the timer. Different rests require per-set notes and an unset timer. Set execution allowances, group effort and caps, transitions, preparation and supplied free text remain visible. G1B uses the `exact`, `usable-with-disclosed-limitations` and `blocked` vocabulary. Every supported E4.1 session has numeric effort instructions that need visible manual cues, so a successful provider translation in this version carries limitations.

## G1C.1 · One athlete-saved synthetic Hevy routine

In a single authorized Codex rehearsal, account preferences and template search established the destination, display unit and two standard barbell templates. The structured result of `render_hevy_routine` agreed with every submitted field. The athlete confirmed the widget save by finding the routine in My Routines. The render result supplied no saved routine ID, and FI received no post-click receipt. After confirmation, paginated `get_user_routines` returned one routine with the rehearsal markers in both exercise notes. Its provider ID, template sequence and set contents established the saved object's identity.

| Field | Saved routine readback | Athlete's saved-routine view |
| --- | --- | --- |
| Title, exercises and sets | Title matched. Press preceded squat, each with the expected template, a warm-up and a normal set in order. | Same exercise order. The warm-up rows were marked W. |
| Weight and reps | Press returned 20 kg × 5 and 25 kg × 5–7. Squat returned 20 kg × 5 and 30 kg × 6. Fixed targets omitted the exported null range. | Weights appeared in rounded pounds. Squat showed both fixed rep counts. Press used a REP RANGE column showing a dash for the fixed warm-up and 5–7 for the working set. Its notes showed the five-rep warm-up and nominal six-rep working target. |
| Rest and effort | Press timer was null, squat timer was 60 s. Both exercise notes matched exactly, including per-set rests, nominal targets, permitted ranges and RPE caps. | Press notes gave 45 s and 0 s rest. Squat showed a one-minute timer. Effort cues were visible in both notes. |
| Routine notes | The routine-list response omitted this field. | The preparation, reservation and synthetic inspection text were visible. Exact string equality could only be checked in the structured preview. |

For this handoff, retain the G1B translation. Compare both the set table and the notes when fixed and ranged sets share an exercise. After athlete confirmation, identify a unique saved object by content and provider ID, verify structured fields and ask the athlete to check routine notes in the app. Stop on ambiguity before another submission.

## G1C.1B · Controlled update and cleanup

Before the write, the agent rechecked the destination account and paginated the routine list. The saved ID, original timestamp, exercise markers, template order and comparable prescription fields matched the previously verified object. Under separate athlete authorization, the agent submitted one `update_hevy_routine` call for that ID. It built the routine body from the original validated manifest, including both levels of notes, changing the squat working-set load from 30 to 32.5 kg. For fixed-rep sets the update schema accepts an omitted optional range.

An independent, paginated `get_user_routines` readback returned the same routine ID. A comparison of every returned field found changes only to the intended weight and Hevy's update timestamp. The six-rep target, all other sets, template mappings, exercise notes and timers matched. The complete set of routine IDs was identical before and after the update. The update response and routine list both omitted routine-level notes. In the athlete’s post-update view, the notes still displayed the fixture status, scheduled time and zone, 60-second preparation, 405-second reservation, test marker and inspection-only instruction. The squat working row showed 71.65 lb × 6, consistent with the 32.5 kg readback.

The athlete manually deleted the test routine in Hevy after checking the notes. The connected MCP tools exposed no routine deletion. After the athlete confirmed deletion, the agent rechecked the destination account and read every page of its routine list. The previously verified provider ID was absent. No listed routine had the exact test title or the rehearsal marker in its exercise notes. [Hevy manual cleanup](https://help.hevyapp.com/hc/en-us/articles/38030200802583-How-to-Delete-Comments-Sets-Workouts-Routines-Your-Hevy-Account)

## Entering the Garmin worksheet

If the athlete chooses manual entry, use the expanded rows and their effort cues in the Run workout builder. Each repeat instruction states the work count, between-bout count and presence of an explicit final recovery. A fixed duration can use a time endpoint. For a permitted time range, preserve the choice with manual lap advance and the displayed nominal/range cue. Leave intensity open and interpret RPE and the cap manually. Keep preparation outside workout elapsed time. Schedule the approved local date, sync and verify the calendar and cues on the target watch before use. For a separately authorized API rehearsal, obtain independent scope review, an authorized future occurrence and explicit athlete consent. Check both Connect placement and on-watch steps, including the final recovery on an authorized update. The operator has deferred Garmin Business Starter and Training API access.
