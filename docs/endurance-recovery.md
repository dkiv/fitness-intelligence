# B2 · Canonical endurance and recovery

B2 supplies PostgreSQL storage and pure in-memory mapping for synthetic Garmin Personal API
v1 responses. The mapper has no transport, database write path or public route. B1 verified
the read path, including default macOS Keychain retrieval. Two sampled windows establish
availability on those dates only. A sport in the catalog establishes a possible classification.
Historical coverage, continuity and upstream origin each need separate evidence.

## Activity identity and measurements

One activity uses one `Workout`. Its existing `started_at` stores the UTC instant. The external
workout reference resolves the stable key `(user_id, provider, source_account_id, 'workout',
external_id)`. The mapper renders a positive int64 activity ID as canonical decimal text.
The `endurance_activities` primary key is the workout ID itself. A composite FK pins the
measurement snapshot to the exact reference, owner and workout. This lets B3 reuse a workout
with other references while identifying which account supplied these measurements. An equal
activity ID in another account resolves independently. Time, sport and distance are unsuitable
for automatic cross-source matching.

`map_activity` accepts a search row, optional detail and an optional performed-workout
response. `map_activities` checks one collection for repeated IDs. Replaying the same
input yields the same scoped identity and snapshot. The search owner and detail owner must
match the bound profile and detail must echo the requested activity ID. The performed array
has no echoed parent or account ID. The caller must attach its original request account and
activity ID at the transport boundary, even when fetching multiple activities concurrently.

| Canonical input | Source and interpretation |
| --- | --- |
| UTC start | Detail GMT, epoch milliseconds or search GMT. The mapper checks overlapping representations at their common resolution. Only named GMT strings can supply UTC without an offset. |
| Local date | The date of the documented source-local wall clock. Detail and listing local times must agree when both exist. A repeated autumn clock hour can identify two different UTC instants. |
| Sport, subtype | Running and supported running subtypes, squash and ultimate frisbee map by source key. Unknown keys remain available verbatim under `other`. A missing key remains null. |
| Distance, speed, elevation | Metres, metres/second, ascent and descent in metres. |
| Times and heart rate | Activity, elapsed and moving durations in seconds are separate fields. Average and maximum HR use bpm. |
| Running pace | `running_pace()` returns seconds/km from 1000 divided by reported positive average m/s, rounded half-even to 0.001. An explicit zero speed or distance, or a different sport, makes running pace inapplicable. Absent speed on an otherwise eligible run gives missing pace. |

For scalar measurements, the listing takes precedence and detail fills missing fields. The
projection identifies the source DTO and field for each populated value in
`Activity.measurement_sources`. B3 can store this allowlist and the mapping version in
`ExternalReference.sync_metadata`. A null measurement means unavailable. An explicit zero
is stored. Negative, nonnumeric, nonfinite or out-of-range inputs reject the snapshot.
Quantities use decimal half-even rounding to nine places, rejecting a positive value that
would round to zero. Units are independent of device display preferences.

### Splits and performed steps

`activity_split_summaries` stores each aggregate's source position, type, represented split
count, duration, distance and average speed. Detail splits take precedence over listing
splits, so the two versions never contribute twice. One row can represent several splits.
Positions are meaningful only within the current snapshot.

`activity_performed_steps` stores indexed steps from the activity's performed-workout
endpoint. Indexes are unique within the attached workout group. A target describes the
step instruction and supplies no evidence of achieved speed, time in zone or adherence.
Steps neither create plan sessions nor expand into inferred laps.

| Instruction | Supported interpretation |
| --- | --- |
| TIME, DISTANCE, REPS | Seconds, metres and integer repetitions respectively. |
| REPEAT_UNTIL_STEPS_CMPLT | Return-to step index and repeat count. Neither value contributes elapsed time. |
| HEART_RATE, SPEED, CADENCE, POWER zone | A positive integer target selector identifies the zone. Zone boundaries remain unknown. |
| Custom range (selector zero) | Speed in m/s, running cadence in steps/min and cycling cadence in rpm. Heart-rate bounds use percent of maximum or the documented bpm-plus-100 encoding. Mixed encodings and reversed bounds fail validation. |
| OPEN or unsupported instruction | Preserve the category. Numeric interpretation is deferred for other repeat forms, power ranges, swim targets and unknown encodings. |

A missing split or step collection leaves coverage unknown. A supplied empty collection
is distinct in the mapped snapshot. B3 must preserve that coverage when reconciling children
and must retain its prior snapshot if a performed-workout group omits its steps.

## Daily recovery and expenditure

`map_day` requires the requested provider calendar date and checks each contributing DTO's
date and source identity. Each observed metric becomes one `daily_recovery_observations`
row per owner, provider, source account, date and metric. PostgreSQL constrains metric,
unit and method combinations. A missing endpoint, null value or absent metric contributes
no row. A reported zero contributes a row with value zero.

| DTO | Measurements and window |
| --- | --- |
| UserDailySummaryDto | Resting HR in bpm. Total, active and basal kcal have method `wearable_estimate`. Total already includes the components. Preserve the first and last wellness timestamps when supplied as coverage bounds for the provider day. |
| DailySleepDTO | Total seconds asleep excluding naps, plus light, deep, REM and awake seconds. Preserve confirmed sleep GMT bounds and Garmin's assigned date across midnight. Sleep duration and its breakdown are separate metrics. |
| HrvChartDTO.hrvSummary | Preserve last-night and trailing-seven-day averages as two metrics. Chart GMT bounds describe overnight coverage. The weekly metric is indexed by its ending provider date and has no asserted UTC endpoints. |

The Personal API v1 schema declares `DailySleepDTO.sleepStartTimestampGMT` and
`sleepEndTimestampGMT` as date-time strings and describes the confirmed sleep bounds as
UTC milliseconds. A bounded read of one verified sleep summary returned both as 13-digit
JSON integers. Both matched the requested day’s vicinity when interpreted as milliseconds
since the Unix epoch. The sleep mapper accepts that integer form using exact UTC millisecond
arithmetic, alongside the existing GMT strings (offsetless, `Z`, or numeric offset).
Missing bounds remain unknown, reversed bounds fail validation, and Garmin’s
`calendarDate` remains the observation date even across midnight. Other integer widths,
quoted numbers and fractional numeric tokens remain unsupported. [Garmin Personal API schema](https://developer.garmin.com/gc-developer-program/personal/swagger-docs/)

Garmin describes device HRV in milliseconds. The Personal API v1 summary fields omit a unit.
B2 records their numbers with `source_unit_unverified`. D1 must exclude these rows from
millisecond-based comparisons until the API scale is confirmed. Individual HRV readings,
daily HR series, unclassified sleep, proprietary scores, zones, GPS, FIT and prescribed
workouts are deferred. [Personal API contract](https://developer.garmin.com/gc-developer-program/personal/swagger-docs) · [Garmin HRV documentation](https://www.garmin.com/en-GB/garmin-technology/health-science/hrv-status/)

## Bounded local identity verification before B3

Authentication with Keychain proves possession of a working key. The published settings DTO
contains display preferences and a display name. It exposes no documented immutable account
identifier. The strongest candidate is activity detail `userProfileId`, documented as the
activity owner's identifier. Search `ownerId` identifies an activity owner. Daily
`userProfileId`, sleep `userProfilePK` and HRV `userProfilePk` are separate fields whose
shared namespace and stability across credential changes still need verification. An activity
ID or UUID identifies an activity. JWT expiry is used only for token renewal.

Use this separate operator procedure before enabling any personal observation writes.

1. Resolve the local owner through the trusted operator session. In a separately authenticated
   Garmin account, identify an owned activity and obtain independent, provider-issued evidence
   of the numeric profile identifier (for example an official account export **if it identifies
   that field**). Keep this evidence local. If Garmin cannot establish the identifier or its
   durability, leave enrollment unresolved and seek provider confirmation.
2. On a known activity day, use the B1 in-memory client and the default Keychain lookup.
   Request one activity search page (`start=0`, `limit=3`, both local dates set to that day).
   Require the known activity ID on that page. Fetch that activity's detail once and verify
   the echoed ID. Compare the detail profile ID and listing owner ID as positive int64s against
   the independently established profile in memory.
3. For each intended wellness feed, fetch at most one daily summary (`calendarDate`), sleep summary
   (`date`) and HRV chart (day in the URL) on that day. Check the exact calendar date and respective identity field above.
   Missing or contradictory identity leaves that feed unresolved. Inspect only equality
   outcomes. Skip activity workouts, archives, GPS, nutrition and weight.
4. Make five logical reads at most. With a valid key this normally takes one exchange and
   five GETs. The client allows one re-exchange and replay per rejected GET, with a global
   three-minute budget. Stop on a returned error or mismatch. Disable HTTP logging, keep
   payloads and credentials in memory, and close the client.
   Record only pass, mismatch or insufficient evidence per comparison. Matching several
   response fields alone cannot establish that the account belongs to the intended owner.
5. In B3, enroll through the trusted operator transaction only after confirming the scope
   and stability of the provider identity. Use the existing active Garmin `SourceAccount`
   with its immutable provider identity. On a subsequent key change, repeat the comparisons
   against the original identity before resuming. A disconnected or unresolved account
   fails closed. B2 exposes no enrollment command.

The [B3.1 operator workflow](garmin-importer.md) covers this independently confirmed path and the authorized locally witnessed enrollment alternative.

## B3 importer boundary

Start with one bounded activity page for a verified account, associated detail and optional
performed steps, plus one requested calendar day per verified wellness feed. Stage the whole
response in memory. Decode fractional JSON numbers directly to Decimal at ingestion.
Use the existing account and external-reference uniqueness constraints
for retries and concurrent inserts. Commit each complete activity and its eligible child
snapshots atomically. Retain the original canonical workout ID across edits. Upsert observed
daily values by their scoped metric key. Record retrieval time separately from measurement
and coverage windows. Sparse replies, an empty page, 204 and failed lookups supply no deletion
evidence. Compare repeated and changed windows on synthetic data before expanding the range.

D1 can project normalized rows by authenticated owner and preserve units, coverage and
measurement method. The strength reader excludes endurance-only sessions from strength
frequency while retaining workouts that actually contain strength exercises.

## Intake and body weight

B3.2 adds owner-scoped daily reported kcal by source field and individual weight observations
with source value and unit, canonical kg, provider-local date, timing precision and retrieval
provenance. The day selector exposes missing intake, explicit zero, completeness and conflicts.
Weight identity is limited to eligible source evidence. Similar values alone cannot establish
a shared event. Original writer, scale and historical coverage remain unverified. Meal records
and macronutrients are optional future extensions.
[Verified field behavior, units and reconciliation](garmin-importer.md#intake-and-body-weight)
