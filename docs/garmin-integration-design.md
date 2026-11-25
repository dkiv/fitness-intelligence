# B1 · Garmin Personal API integration

**Status, 2026-11-24.** The contract below comes from Garmin's published Personal API
documentation, OpenAPI 3.0.1 specification (API version 1.0.0) and official Python client.
The local verifier has synthetic coverage. Account-specific observations are pending the
operator's [two-date probe](garmin-verification.md).

## Credentials, permissions and transport

The API key belongs to one Garmin Connect account. Its owner chooses 30, 90, 180 days or
one year at creation. Garmin displays it once. Deleting it invalidates associated tokens.
The global server is `https://personal.connectapi.garmin.com`. The specification also lists
a China server. B1 targets the global server only. Send an empty POST to
`/personalapitoken-service/personal-api/personal-api-key/token` with
`Authorization: ApiKey <key>` and `Accept: */*`. Garmin's reference client reads a JWT
from the response text and uses its numeric `exp` claim for expiry. Resource GETs use
`Authorization: Bearer <token>`. A token lasts at most 24 hours, capped by key expiry.
Renew by exchanging the key again. There is no refresh token.
[Setup](https://developer.garmin.com/gc-developer-program/personal/personal-api/) ·
[FAQ](https://developer.garmin.com/gc-developer-program/personal/personal-faq) ·
[Reference authenticator](https://github.com/garmin/connect-personal-api-python/blob/main/src/garmin_personal_api/auth.py)

Garmin describes personal exploration and analysis of one's own data and pull-only delivery.
The individual accepts additional terms at key creation. The acceptance screen requires sign-in.
Its precise terms for onward transfer, retention, use with an LLM and use of derived data remain
unverified here. Review the accepted version in Connect alongside the general Terms of Use before
moving data outside the personal application. A public code repository with synthetic tests
can be reviewed independently of operating a service that handles other people's credentials.
Commercial or multi-user service operation requires a separate program and applicable agreement.
B1 establishes no permission for hosted inference, model training, third-party disclosure or
workout/calendar publishing. Keep model inputs synthetic pending a use-specific terms review.
[Program comparison](https://developer.garmin.com/gc-developer-program/overview/) ·
[Personal key and accepted terms](https://connect.garmin.com/app/settings/personalApiToken) ·
[General Terms of Use](https://www.garmin.com/en-US/legal/terms-of-use/)

The activity APIs specify 400, 401, 403 and 500 on multiple operations, and 404 on activity
detail/workouts. HRV documents 204. Some operations document only 200. A universal error
envelope, throttle threshold, Retry-After guarantee and service-wide request quota are
unpublished in the reviewed specification. The verifier stops on 429, checks expiry in
memory, and permits one re-exchange and replay per rejected GET on 401. It never follows a
redirect or retries token failures. See the [operation schemas](https://developer.garmin.com/gc-developer-program/personal/swagger-docs).

## Availability matrix and proposed canonical mapping

Each row describes documented fields and the evidence B1 can collect. **Live coverage is
unknown for every row.** A nonempty response may contain only metadata. Inspect the specified
measurement fields and date evidence before promoting a category to ingestion.

| Category | Documented representation | What the local sample can establish | Proposed normalization |
| --- | --- | --- | --- |
| Activity history and identity | Search returns an array, each with int64 `activityId`, owner ID, UTC epoch-ms `beginTimestamp`, GMT/local start strings and an activity type. Detail has `activityId`, `activityUUID`, `userProfileId`. | Two seven-day windows, up to six activities per window. Detail must echo the selected ID. Owner-field presence alone cannot verify the account. | Owner + bound Garmin source account + activity ID for identity. Preserve UTC start and source local date. Keep provider UUID as optional metadata. |
| Running and other sports | Activity type key, type ID and parent type ID, plus the simple key/parent catalog. Distance in metres, duration/elapsed/moving time in seconds, average speed in m/s, average and max HR in bpm. | Catalog and sampled activities report running, squash and ultimate-key matches separately. Detail reports whether speed permits a pace calculation. Other type keys remain private. | Preserve type/subtype hierarchy, map known keys, keep unknown sport. For positive average speed derive s/km as 1000 divided by m/s. Label the time basis if deriving pace from distance and duration instead. |
| Laps, splits and workouts | Lap count, aggregate split summaries, performed workout records with steps. | Per-window detail, split/step presence and linked workout count. Individual lap telemetry and complete prescribed workouts remain unresolved. | Separate split aggregates and performed steps from the activity. Distinguish count, aggregate and individual lap. |
| Original files | GET serves a ZIP containing the original activity format. Detail metadata can identify FIT or another format. | Response headers and FIT format declaration separately. Neither inspects archive membership or contents. | Defer binaries, decoding, trackpoints and GPS. |
| HR zones | Sport-specific zone floors and training method. Search rows can carry time in zones 1–5. | Current configured zones with generated defaults disabled. Time-in-zone field coverage on both sampled periods. | Store config separately from activity-specific zone durations. Historical threshold values and change dates remain unknown. |
| HRV, resting and daily HR | Overnight summary/readings, resting/min/max HR, timestamped daily HR arrays with column descriptors. | HRV summary and individual value presence, resting/min/max fields and counts of readings in the descriptor-identified column. HRV supports no-content responses. | Keep overnight and weekly aggregates distinct. Confirm HRV units before importing. Use bpm for heart rate and retain series descriptors and verify sentinel semantics before mapping. |
| Sleep | Daily summary, sleep seconds excluding naps, stage/awake seconds, scores, SpO₂, respiration and sleeping HR. | Presence by metric on each anchor date. | Attribute sleep to Garmin's calendar date, preserving GMT window boundaries. Keep intranight wake time distinct from duration asleep. |
| Expenditure and Body Battery | Daily total, active and BMR kcal. Body Battery daily reports have charged/drained values and interval extrema. | Independent daily fields and one Body Battery interval per sampled day. | Separate kcal components and the vendor-specific Body Battery scale. Avoid summing total and components. |
| Calorie intake | Daily summary has consumed kcal and an intake-data flag. Food logs contain a daily consumed-nutrition object. | Compare flag, reported numeric zero/null, and presence of daily food totals separately. | One daily intake estimate per source/day. Preserve energy intake separately from expenditure and goals. |
| Meal logs and macros | Meal details with logged foods, per-meal content, daily kcal and grams of carbs, fat and protein. Food events have `logSource`; catalog metadata has `source`. | Presence of meals, logged foods, consumed nutrients and fixed MyFitnessPal source markers. A food catalog attribution does not establish who logged the meal. | Model daily totals and meals at different grains. Store event origin separately from food catalog provider. Never add daily totals to underlying meals. |
| Body weight and RENPHO | All-entry response contains weight (documented kg), GMT epoch milliseconds and local calendar date. The published row has no original device or writer field. | Measurement presence and date match. Three explicitly exploratory source labels can detect a literal RENPHO marker. An unmarked measurement leaves origin unknown. | Store kg, UTC measurement instant, original unit evidence and upstream origin when established. Check scale/unit against the source app before ingestion. |

### Endpoint inventory

The rows below give the actual GET paths and successful response shapes in the reviewed
specification. Brackets denote an array. The full field definitions and parameter descriptions
are available in [Garmin Swagger](https://developer.garmin.com/gc-developer-program/personal/swagger-docs).

| Path | Response shape |
| --- | --- |
| `/activity-service/activity/activityTypes/simple` | `[SimpleActivityTypeDTO]` |
| `/activity-service/activity/{activityId}` | `ActivitySummaryDTO` |
| `/activity-service/activity/{activityId}/workouts` | `[ActivityWorkoutDTO]` |
| `/activitylist-service/activities/search/activities` | `[SummarizedActivityDTO]` |
| `/biometric-service/heartRateZones/v2` | `[HeartRateZonesDTO]` |
| `/download-service/files/activity/{activityId}` | `original-format archive` |
| `/fitnessage-service/fitnessage/v2/{calendarDate}` | `[FitnessAgeDTO]` |
| `/goal-service/goal/user/effective/weightgoal/{startDate}/{endDate}` | `UserGoalsRangeDTO` |
| `/hrv-service/hrv/{calendarDate}` | `HrvChartDTO` |
| `/hrv-service/hrv/daily/{fromDate}/{toDate}` | `HrvDailySummaryDTO` |
| `/metrics-service/metrics/maxmet/daily/{startDate}/{endDate}` | `[MaxMetDTO]` |
| `/nutrition-service/food/logs/{date}` | `DailyNutritionSummaryDTO` |
| `/periodichealth-service/menstrualcycle/summary/{calendarDate}` | `MenstrualCycleSummaryDTO` |
| `/periodichealth-service/menstrualcycle/dayview/{calendarDate}` | `DetailedMenstrualCycleDayDTO` |
| `/sleep-service/sleep/dailySleep` | `DailySleepDTO` |
| `/sleep-service/sleep/dailySleepSummariesByDate` | `[DailySleepDTO]` |
| `/userprofile-service/userprofile/settings` | `UserSettingsDTO` |
| `/usersummary-service/stats/hydration/daily/{startDate}/{endDate}` | `[UserDailyHydrationDTO]` |
| `/usersummary-service/stats/steps/daily/{startDate}/{endDate}` | `[StepsDailyStatDTO]` |
| `/usersummary-service/stats/stress/daily/{startDate}/{endDate}` | `[MultiValueWellnessChartItemDTO]` |
| `/usersummary-service/usersummary/daily` | `UserDailySummaryDto` |
| `/usersummary-service/v2/dailysummaries` | `ApiDocumentListUserDailySummaryV2DTO` |
| `/weight-service/weight/all/{startDate}/{endDate}` | `[DateWeightDTO]` |
| `/weight-service/weight/range/{startDate}/{endDate}` | `WeightRangeDTO` |
| `/wellness-service/wellness/bodyBattery/reports/daily` | `[BodyBatteryDailyReportDTO]` |
| `/wellness-service/wellness/daily/spo2acclimation/{calendarDate}` | `DailySpO2AndAcclimationDTO` |
| `/wellness-service/wellness/dailyHeartRate` | `DailyHeartRateDTO` |
| `/wellnessactivity-service/activity/summary/range/{fromDate}/{untilDate}` | `[WellnessActivitySummaryDTO]` |

### Ranges, history and changes

Activity search uses a zero-based `start` offset and `limit` (default 99). Start and end are
inclusive activity-local dates. The response is a bare array. Total count, stable snapshot
and maximum historical depth are unspecified. B1 uses pages of three and stops after a short
page or two pages. Duplicate IDs, excess rows or dates outside the requested window invalidate
that page. A full second page leaves possible additional records unexamined.

Range limits vary by resource. Steps and stress allow up to 28 days. Sleep summaries, hydration
and Body Battery allow up to 31 days. Daily summary v2 allows up to one year. Weight `all`
allows up to 364 days, inclusive by local calendar. Weight `range` can include adjacent
measurements outside the range, so B1 uses `all`. Food logs use the user's local day.
A query-span limit places no lower bound on the age of retrievable records. Different
devices, permissions, upstream writers and actual recording days can affect both samples.
No retention horizon is established by the documentation or synthetic tests.

The specification describes `metadataDTO.lastUpdateDate` as UTC without a trailing offset.
A local wall-clock activity timestamp alone is ambiguous during DST transitions. Use explicit
GMT/epoch fields for instants and keep local dates for daily grouping. Verify series timestamps,
units, unavailable-value sentinels and day attribution by metric before mapping.

Personal API delivery is pull-only. No documented change cursor, deletion event, tombstone,
write endpoint or guarantee of stable per-meal/split identity was found. A failed lookup,
empty day or missing search row is insufficient evidence of deletion. A source update time
on one activity provides no guarantee that an ordered listing captures every edit.

## B2, B3 and the Health Connect decision

1. **B2 · Activity mapping and binding.** First establish a trusted owner-to-source-account
   binding. The settings DTO offers a display name and preferences. Activity and wellness DTOs
   expose candidate IDs in different contexts. Verify a durable identity independently and
   test those relationships before writing any rows. Never bind by display name, arbitrary
   JWT claims or caller-provided owner ID. Start with a pure synthetic endurance mapper for
   one activity summary/detail and known sport types. Extend the existing workout and
   owner-scoped external-reference patterns for endurance metrics. Keep optional measurements
   nullable and use canonical inputs for Polars. Validate positive pace denominators, units,
   offset handling and duplicate activity IDs.
2. **B3 · Bounded ingestion of verified categories.** Once binding and retention decisions
   exist, add an idempotent local activity importer and selected date-based observations with
   composite ownership constraints, explicit transactions and replayable date windows.
   Distinguish measurement time, collection day and retrieval time. Replace changed snapshots
   only with positive evidence. Preserve existing records across ambiguous absences. Include
   cross-owner, retry, sparse-day and revision tests before expanding history. Defer nutrition
   and weight until source, unit, granularity and deduplication decisions are resolved.
3. **Keep Health Connect on the roadmap.** If known MyFitnessPal logging days yield attributable
   intake and macros at the needed grain, Garmin could cover those categories. If known
   weigh-ins appear at both ages with correct units, Garmin could cover a weight trend while
   original scale provenance remains unknown. Retain the bridge for any required gap,
   particularly writer/device attribution and meals. Confirm the Android writers, permissions
   and available history in their own right. If both paths carry a record, designate one
   authoritative source per category and retain the other as corroboration. Similar totals
   alone cannot justify merging individual records.
