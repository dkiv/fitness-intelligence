# Daily and weekly training, recovery, nutrition and weight

The internal report describes recorded training and health observations under the [longitudinal analytics design](unified-longitudinal-analytics-design.md). A trusted local caller supplies an already authorized owner, a PostgreSQL engine, a half-open calendar period and one Garmin weight account. Each date has a row, including dates with no observations.

```python
from datetime import date
from zoneinfo import ZoneInfo

from fitness_intelligence.adapters.hevy.analytics import HevyHistoryProfile
from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.analytics.weekly import aggregate_weeks
from fitness_intelligence.db.longitudinal import query_longitudinal

zone = ZoneInfo("America/Toronto")
report = query_longitudinal(
    engine,
    owner_id=authorized_owner.id,
    weight_account_id=garmin_account_id,
    expenditure_account_id=garmin_account_id,
    endurance_account_id=garmin_account_id,
    recovery_account_id=garmin_account_id,
    hevy_profile=HevyHistoryProfile(
        hevy_account_id,
        external_load_templates=reviewed_external_load_ids,  # frozenset of template IDs
        lower_body_templates=reviewed_lower_body_ids,
    ),
    period=Period(date(2025, 3, 3), date(2025, 3, 10), zone),
    source_zones={garmin_account_id: zone},  # Known provider calendar for these dates.
)
monday = report.days[0]
reported_kcal = monday.intake.metric.value
median_kg = monday.weight.metric.value
weigh_ins = monday.weight.measurements
weekly = aggregate_weeks(report, reference_date=date(2025, 3, 10))
week = weekly.weeks[0]
mean_reported_kcal = week.intake.calories.mean_per_eligible_date_kcal
```

The report opens its own read-only PostgreSQL REPEATABLE READ transaction. Pass an engine, keeping any application session or transaction outside the call. All selected domains, observation identities, provenance, issues and coverage use that snapshot. Owner and source-account UUIDs must come from the trusted caller. The weight account must have a resolved Garmin binding to that owner. A disconnected account can still supply retained records. The query requires no provider session or credentials.

## Reading a daily row

- **Calendar.** Garmin and intake use a provider-date spine. Hevy workouts use their start date in the report zone. The request's IANA zone controls the interpretation of an instant's report date. Supply an optional verified IANA zone per source account only when it applies to the whole period. Split the request across travel/regime changes. A single account's native daily total remains available with unknown zone and a null aligned date. Combining intake facts across accounts requires matching known source zone keys. A metric gets an aligned report date only when the calendars agree with the report zone. Each eligible weigh-in separately exposes its instant's report date, including a different date across midnight.
- **Intake.** The owner-day selector compares all source totals on the date. Agreement yields one value, disagreement or a retained disagreement issue withholds it. All contributing IDs, original reported totals, source fields, mapping versions, retrieval times, logging completeness, presence evidence and known writer are in `facts`. A true presence flag or the recognized Garmin food mapper's logged-food evidence supports explicit zero. Keep unsupported zeros visible as excluded facts. Missing intake and disputed intake both have null values and distinct reasons.
- **Weight.** The account-day selector withholds the whole day on any open weight issue. Held rows expose IDs and reasons in `excluded`. Eligible individual readings preserve canonical kg, original numeric value, interpreted and documented units, UTC instant and precision. A combined daily median requires one verified series. Different known writers yield a null median with `incompatible_weight_regimes`. When the series differ but continuity is unknown, the reason is `weight_comparability_unverified`. Missing writer metadata alone cannot identify a different scale. The `measurements`, supporting IDs and eligible observation count still include every individually eligible reading on a mixed day. The mean of the two central values is exact, including an extra decimal place when necessary.
- **Verification.** A recognized historical weight row carries the segment fingerprint assigned by the account/date-bounded writer. The report checks the reviewed mapping, field, time precision, units and conversion. A legacy bounded write carries the B3.2 mapper's independently chosen unit and can predate the segment column. Its complete producer signature is accepted on a day without historical acquisition, or before a failed historical attempt with no prior success. When the historical ledger leaves an unscoped row's origin ambiguous, its ID is retained with `unverified_weight_unit`. A plausible mass or the documented kg label cannot establish the wire unit. The report never reads private verification files.
- **Coverage.** Each account/category/date has its own latest status, attempt, last successful time/count, pass, policy, available source receipts, gap reason and open issue subjects/reasons. Intake includes the owner's Garmin accounts and any other intake contributors in the request. Weight has one source. `observations_without_coverage` distinguishes retained facts on a never-queried historical day. A successful empty lookup supplies no numeric zero. Retained verified facts can contribute after a partial or failed attempt. `metric.eligible_count` counts supporting identities and `retained_count` includes withheld rows. Two agreeing intake IDs still yield only one day of reported kcal.

- **Wearable expenditure.** Pass an explicit, resolved Garmin account owned by the same principal. It may differ from the weight account. Omit `expenditure_account_id` to keep the D1B query behavior. Each selected day has independent `total`, `active` and `basal` metrics. A value requires the corresponding accepted canonical kcal observation with method `wearable_estimate`. Each fact carries the original method, unit, field, observation ID, measurement window and available retrieval/mapping evidence. Unknown legacy provenance stays null. A category/day hold withholds all affected components. A component-specific issue only holds that field. Active and basal never supply a missing total.

## Weekly calculation

`aggregate_weeks(report, *, reference_date, weight_continuity=None)` is a pure function over the daily snapshot. The returned report retains the daily facts, period, zones, selected sources, policy, reference date and optional continuity evidence. The daily contract is `d1d-v1`. The new account selections are optional keyword arguments. Omitted domains have null report fields. Daily intake and weight use policy `intake-weight-v2` for the combined daily weight median. The weekly conventions use `nutrition-weight-weekly-v1`.

- **Calendar.** Weeks run from Monday to the next Monday, exclusive, using provider dates. `requested_dates` contains exactly the intersection with the half-open request. `fully_requested` means seven requested dates. `closed` means the following Monday is on or before the reference date. Supply the first date still potentially open across the contributing native calendars, using the earliest current local date if calendars differ. No system clock is read. Sunday as reference leaves that Sunday’s week open even if all seven dates already have observations. This parameter controls calendar closure only. Historical queries still use current accepted facts.
- **Calories.** For each metric, sum the non-null daily values and divide by the number of eligible dates for its observed-day mean. Intake counts one selected total per owner-day, including supported zeros. It also reports logging-completeness counts among selected dates. Total, active and basal each use their own eligible dates. With zero eligible dates both results are null. The exact subtotal and denominator remain available for repeating means, which use 38 significant decimal digits with half-even rounding. `incomplete_subtotal` identifies dates with missing values. `all_requested_dates` describes value presence within the request, including clipped or open weeks.
- **Support and coverage.** Each calorie sample carries dated cells, supporting IDs, retained and eligible observation counts, eligible/requested date counts and statuses such as missing, withheld and conflict. Acquisition counts and open-issue dates are tracked by account and category. A partial read can supply an eligible value. For intake selected on different dates from different accounts, a common verified provider calendar is required before combining dates. Otherwise both weekly numbers are null with `unverified_common_calendar`, while the daily facts and support remain visible. A common native calendar can differ from the report zone. Inspect each sample’s `report_calendar_aligned` before comparing across calendars.
- **Weight.** Each verified series gets one vote per measured date. Take the median of its eligible daily medians, retaining the actual dates, eligible readings, IDs and verification evidence. Reuse the existing daily median on a homogeneous date. If several regimes occur on one date, partition that date’s eligible readings by regime and take each subgroup’s median. A date with a withheld combined median can contribute eligible measurements to each verified series. A reconciliation hold withholds all measurements for that date. There is no pooling across series or interpolation across missing dates.
- **Comparability.** Within a single selected account, require matching source field, mapper, measurement method, interpreted and documented unit, and writer (including unknown). The default groups verified historical readings within their unit-verification segment and bounded readings within their verified day. Changed fingerprints alone leave continuity unknown. To combine scopes, the trusted caller may supply a `WeightContinuity` naming the exact source, half-open dates, allowed verification scopes (including `None` for reviewed bounded readings), and an evidence reference. That reference must support continuity of the scale, weighing protocol and unit interpretation over the specified interval. The report records the declaration and still separates different producer signatures. Scope fingerprints establish unit verification, and unknown writer does not identify a particular scale.
- **Observed weight change.** Compare each series only with its match in the adjacent preceding week in the request. Both calendar weeks must be fully requested and closed. Each needs at least three eligible measured dates, with at least three calendar days between first and last. Return the later median minus the earlier median in kg, both supporting series and their date/observation counts. Otherwise the change is null with reasons. These are descriptive reporting conventions.

## Synthetic seven-day example

This is the seven-day regression fixture, shown on the provider calendar. An em dash denotes an unavailable value. All seven dates are requested, including the March 9 clock change.

| Provider date | Reported kcal | Wearable total / active / basal kcal | Daily median kg | Evidence |
| --- | ---: | --- | ---: | --- |
| Mar 3 | 2,100 | 2,400 / 600 / 1,800 | 70.0000000015 | Two agreeing intake facts on a partial acquisition day. Two segment-verified weigh-ins. |
| Mar 4 | 0 | — / 400 / 1,700 | 70.4 | Supported intake zero. A bounded weigh-in. Both expenditure components are present and total is missing. |
| Mar 5 | — | — / — / — | — | Unsupported intake zero. A possible retime holds two retained weights. |
| Mar 6 | — | — / — / — | — | Intake and weight acquisitions completed empty. |
| Mar 7 | — | — / 200 / — | — | Conflicting intake totals. Historical weight verification is missing. |
| Mar 8 | — | 2,200 / — / — | 73 | An intake disagreement remains open. Verified observations survive failed refreshes. |
| Mar 9 | 0 | — / — / — | 74 | A logged-food event supports zero. The weight instant falls on March 8 in the report zone. |

With March 10 as the reference date, the March 3 week is fully requested and closed. Reported intake is 2,100 kcal over 3/7 selected dates (four source facts, two zero dates), averaging 700 kcal per selected date. All three have unknown logging completeness. Wearable total is 4,600 kcal over 2/7 dates (mean 2,300), active is 1,200 over 3/7 (mean 400), and basal is 3,500 over 2/7 (mean 1,750).

Of eight retained weigh-ins, five are eligible across four dates. The historical segment’s three daily medians are 70.0000000015, 73 and 74 kg, giving a weekly median of 73 kg from four measurements. The bounded series contributes 70.4 kg on one date. This example has no continuity review bridging the two series and no preceding requested week, so weight change is unavailable.

The immutable Python results record the request, source calendars, contract and policy versions. Historical calendar queries return the current accepted rows. Recorded availability is unknown for these mutable canonical measurements. A later correction can change the same query's result. Decision replay requires separately frozen facts, coverage and policy versions.

## Training and recovery selections

Supply one resolved, owner-bound account per selected domain. The three Garmin selections may use different accounts. The report records the source of each selection and the Hevy profile, including its reviewed template sets. A single report contains only the selected Hevy history. `day.strength`, `day.endurance` and `day.recovery` have the same exposure interfaces as their weekly counterparts. Weekly aggregation reads the daily facts in calendar order and performs no database queries.

| Projection | Daily and weekly metric | Denominator and evidence |
| --- | --- | --- |
| Hevy visits | Distinct workout IDs and distinct report dates, including open or empty workouts | `workouts` and `workout_dates` enumerate the two denominators. Historical acquisition completeness is unknown on every selected date. |
| Strength execution | Working sets include normal, drop and failure sets. A completion instant confirms a set. An ended workout with positive reps, distance or duration supports inference. | `working.confirmed` and `working.inferred` retain set IDs. Count each workout with confirmed work once, and count inferred-only workouts separately. Apply the same precedence independently to distinct dates. Warm-ups, executed sets of unknown kind, and unsupported sets have separate ID lists. |
| Strength movement and reps | Sum available recorded reps on evidenced working sets, with a null sum when none have reps. Report per-movement and explicitly classified lower-body subsets. | `recorded_reps` pairs each contributing set ID with its reps. A validated account/template supplies movement identity, otherwise the exercise occurrence stands alone. `unclassified_exercises` lists occurrences lacking reviewed body-region classification. Load convention requires its own reviewed mapping. |
| Running and other sports | Per sport, count eligible outings and distinct **provider dates**. Sum known metres, activity seconds, moving seconds and elapsed seconds independently. Inspect sessions through `endurance.days`. | Each subtotal supplies `eligible_count`, supporting workout IDs and IDs of eligible sessions missing that field. The session count supplies the denominator. The longest observed run uses greatest measured distance, earliest UTC start, then lowest workout UUID. Its own duration fields and speed-based pace stay attached. Other subtypes such as cycling have separate series. |
| Recovery | Each native date contains one cell for each sleep metric, resting HR and each HRV window. Weekly sleep and resting HR give median, observed minimum and maximum. | Each comparable series exposes `dates`, `sample_count` and contributing observation IDs in `facts`. Each needs matching account, metric, method, unit, field and mapping. Missing provenance, missing fields and reconciliation holds are visible by date. Light, deep, REM and awake are separate wearable classifications. Sleep duration uses its own reported value. |
| HRV availability | Count cells with a fact separately for the overnight and trailing-seven-day series. Inspect the original unit, window endpoints and acquisition state. | Each trailing observation is indexed by its end date. Overlapping windows share nights. D1D supplies source facts only for HRV, including values with unverified wire units. |

### Reading Garmin coverage

`endurance.days` pairs the native activity and running-instruction ledgers with the retained outings. Each ledger supplies its latest status, last successful time/count and open issue subjects and reasons. Activity counts are workouts. Instruction counts are step rows. A successfully completed positive enumeration reports the enumerated count at retrieval. Its immutable membership list is unavailable, even when the retained and enumerated counts match. Unknown sport can also leave the running count unresolved. Inspect each outing’s field receipts to see which retrieval and source revision supplied a measurement.

A measured subtotal with status `lower_bound` describes the nonnegative exposure supported by verified recorded outings. Missing fields, partial coverage and unclassified activities can leave more work uncounted. An empty refresh with retained rows, or another count discrepancy, changes the status to `observed_only`: the retained exposure has no defensible relationship to the current enumerated total. An activity-specific issue withholds the affected outing from the eligible count and all subtotals. The fact and reasons remain visible. An instruction-specific issue travels separately with its activity.

A clean empty activity lookup records `activities.last_success_count == 0` at retrieval. Inspect `activities.retained_count` for the current canonical count and `week.closed` for calendar closure. When full-day coverage is unproven, session count, distance and durations have status `empty_at_retrieval` and null exposure values. A failed, partial or never-queried date without eligible observations also has null values, with its own coverage status.

A full-day zero (`complete_empty`) requires an empty, issue-free listing with zero retained activities, a verified provider zone for that account and date, and evidence that the first scan started at or after the following native midnight. The `history-v1` writer records that UTC start in the existing coverage receipt when both activity listings converge on an empty date. The report exposes it as `ActivityDay.scan_started_at`. Older successes have only `attempted_at` and `last_success`, both stamped at completion. Their exposure remains null until a qualifying acquisition. A later `reference_date` can close a week but cannot change what the provider returned earlier.

For example, March 9, 2025 in Toronto ends at 04:00 UTC on March 10. A scan that starts at 03:59:50 and succeeds at 04:00:05 still leaves full-day exposure unknown. A new clean empty scan starting at 04:00:00 can establish zero for that provider date. The report uses the supplied provider zone even when the report zone differs. An unknown provider zone leaves the total unverified.

A weekly zero requires these conditions on **every requested date**, each earlier than the supplied reference date. Six verified full-day zeros and one retrieval-only empty date yield a null weekly total. A consumer selecting a representative week must require a fully requested, closed week and verified full-day coverage before using a zero. A provider-specific zero describes recorded exposure in that source. Other sport series are emitted when represented among retained facts.

The activity group stays on its provider date. Every outing also carries its UTC start and actual report date. A declared matching account zone plus agreement of all observed dates permits the group's `calendar_aligned` flag. A disagreement keeps the native coverage with its original date. Unknown or changing zone history requires parallel calendars or separately scoped requests. Recovery uses its provider date and any supported sleep-window endpoints.

### Synthetic cross-domain week, March 3–9, 2025

The cross-domain regression requests all seven dates, with Toronto as the report zone and March 10 as the closure reference. Each row below uses the stated domain calendar. A dash denotes a missing measurement. A blank Hevy day means zero retained workouts with unknown acquisition. All inputs are synthetic.

| Date | Hevy visits and sets | Garmin outing and activity acquisition | Sleep seconds / resting bpm / HRV availability | Reported intake / wearable total kcal / weight kg |
| --- | --- | --- | --- | --- |
| Mon 3 | Two visits. Squat 5 confirmed reps and 6 + 7 inferred reps. One warm-up and one unknown-kind set. | Run 101, 5,000 m, partial acquisition. Its UTC start falls on Sunday 2 in Toronto. One split summary and one instruction row, with an open instruction issue. | 24,000 / 54 / overnight and seven-day | 2,100 / 2,300 / 70 |
| Tue 4 | — | Runs 102 and 103, 5,000 m and unknown distance. Enumeration succeeded with count 2. Instructions queried empty. | 26,400 / 55 / seven-day | — / — / — |
| Wed 5 | — | Squash, 900 activity seconds. Enumeration count 1. | — / 59 / — | 0 with presence evidence / — / — |
| Thu 6 | One visit, 8 inferred working reps on an unclassified template. | Empty at retrieval, zero retained. The legacy receipt leaves full-day exposure unknown. | — / 90 withheld by an open issue / — | — / — / — |
| Fri 7 | One open visit, one unsupported set. | Acquisition failed, no retained outing. | — / — / — | — / — / — |
| Sat 8 | — | Cycling, 12,000 m and 2,700 activity seconds. Historical date never queried. | — / — / — | — / — / — |
| Sun 9 | One empty visit. | One outing with unknown sport and missing measurements. Enumeration count 1. | — / — / — | — / — / — |

- **Strength.** Five visits across four dates. One workout on one date has confirmed working sets. Two other workouts have inferred-only working sets, with one exclusively inferred date because Monday also contains confirmed work. Four eligible working sets contribute 26 reps, comprising one confirmed and three inferred sets. Reviewed squat accounts for one confirmed and two inferred sets, 18 reps. The other template contributes eight inferred working reps. Each of warm-up, unknown-kind and unsupported has one set.
- **Running.** Three identified sessions on two native dates. Recorded distance is 10,000 m (2/3), activity duration 4,000 s (3/3), moving duration 1,700 s (1/3) and elapsed duration 3,600 s (2/3). These are lower bounds on recorded exposure. The two longest measured runs tie at 5,000 m. Run 101 starts first and supplies 1,800 / 1,700 / 1,900 s and 250 s/km from 4 m/s. Squash contributes 900 activity seconds (1/1), cycling contributes 12,000 m and 2,700 activity seconds (1/1 each). Their moving and elapsed durations are missing. The unclassified outing supplies a count only. Instruction acquisition is partial Monday, empty Tuesday and unknown on the remaining five dates.
- **Recovery.** Sleep median 25,200 s, range 24,000–26,400, on Monday and Tuesday (2/7). Monday's wearable classifications are light 11,000 s, deep 6,000 s, REM 4,800 s and awake 1,300 s (1/7 each, so median, minimum and maximum coincide). Resting HR median 55 bpm, range 54–59 on Monday through Wednesday (3/7). Thursday's held reading remains inspectable. Overnight HRV appears Monday (1/7), trailing HRV Monday and Tuesday (2/7 ending dates), all source-only.
- **Nutrition, expenditure and weight.** Intake subtotal 2,100 kcal and observed-day mean 1,050 across Monday and Wednesday (2/7, both with unknown logging completeness). Wearable total is 2,300 kcal (1/7, mean 2,300). Active and basal have zero contributing dates and null results. One verified Monday measurement supplies the daily and weekly 70 kg median (1/7). The request supplies no adjacent earlier week for weight change.

### Observation handoff to E4.2C

A strength fact carries owner and account, workout, external reference and provider ID, exercise and set IDs and ordinals, occurrence and optional completion times, execution evidence, mapping, content hash and last retrieval/source update. Active exclusively supported workouts enter the projection. Provider corrections can replace exercise/set rows and their IDs. A deleted reference or workout removes support on the next read. The validated template and reviewed load convention bound any future comparison. Independent equipment, variation, role and tolerance evidence are generally unavailable. An absent set RPE stays unknown.

A Garmin outing identifies its exact owner/account/workout/reference and external activity. It carries session measurements, source revision, per-field receipts, issue scope and split/step availability. Split positions and instruction (workout index, step index) pairs identify retained children within that workout and revision. A null collection means availability is unknown, while an empty tuple records an explicitly supplied empty collection. Re-read keys and content after a revision. They establish neither achieved intervals nor chronological laps. Daily recovery facts use the canonical observation ID with account, provider date, metric, value, method, unit and measurement window. Missing sleep endpoints and unknown availability remain explicit. The report can describe recorded effort where a set has measured RPE. It supplies no activity-level tolerance or automatic attribution to a planned occurrence.

These are current accepted facts from one read transaction. Occurrence, upstream revision and latest retrieval have different meanings. A retrieval timestamp cannot reconstruct the first instant at which a corrected field was available. E4.2A implements manual execution against a named approved occurrence. Future imported-data attribution, field-level confirmation, decision-time freezing and transaction-consistent revalidation against inserts, edits, deletions and issues belong to E4.2. The consumer must retain the original evidence tier and separately establish prescription identity and decision eligibility. [Generalized execution contract](generalized-execution.md)

## D1E performance comparisons and individual references

`analyze_performance(weekly, ...)` is a pure extension of the D1D weekly result. It returns the original report, source selections, provider and report dates, reference date, exact contributing facts and the policy version `comparable-performance-v1`. All inputs describe the latest accepted snapshot. Task reviews apply to exact set or outing facts from that snapshot. An out-of-scope, changed or deleted fact invalidates a supplied review. Supply new reviews only after inspecting the current evidence.

```python
from decimal import Decimal
from fitness_intelligence.analytics.performance import (
    Review, RunningTask, StrengthTask, analyze_performance,
)
from fitness_intelligence.analytics.references import RecoveryRegime
from fitness_intelligence.domain.endurance import DailyMetric

# The caller selects actual facts from weekly and supplies its reviewed context.
squat = StrengthTask("squat", "high bar", "barbell", "external_kg", "primary", "paused")
loop = RunningTask(Decimal("5000"), "park loop", "elapsed_s", "reported RPE 6",
                   "dry and calm", "uninterrupted")
regime = RecoveryRegime(weekly.daily_report.recovery_source, DailyMetric.RESTING_HR,
                        weekly.period.start, weekly.period.stop,
                        "same device and resting protocol", "synthetic device review")
performance = analyze_performance(
    weekly,
    strength_reviews={fact: Review(squat, "synthetic set review") for fact in reviewed_sets},
    running_reviews={fact: Review(loop, "synthetic outing log") for fact in reviewed_outings},
    recovery_regimes=(regime,),
)
rep_changes = performance.fixed_work_comparisons("load")
load_changes = performance.fixed_work_comparisons("repetitions")
modeled_changes = performance.successive_estimates
run_changes = performance.successive_runs
recent_running = performance.running_references(comparison_monday)
resting_hr = performance.recovery_reference(comparison_date, DailyMetric.RESTING_HR)
```

### Strength and running comparisons

Strength points expose UTC workout start, exercise/set order, recorded kg and reps, optional achieved RPE, execution tier, template and mapping evidence. A comparison series requires the same owner/account, validated template, reviewed movement, variation, equipment, external-load convention, set kind, role, protocol and evidence tier. Set ordinal is matched by default. A review can explicitly declare ordinals interchangeable with `match_ordinal=False` for the workout's best eligible estimate. The automatic fixed-load and fixed-rep views still match canonical exercise and set positions. Display names supply no identity.

Signed differences are later minus earlier. Reps require equal recorded load. Kilograms require equal recorded reps. The default effort basis requires equal, known achieved RPE. To compare a standardized task whose review independently establishes the protocol, use `effort_basis="reviewed_protocol"`. Such a difference describes recorded work, and missing RPE remains visible. At fixed reps and load, the report can show an achieved-RPE difference even when the effort mismatch withholds the performance difference. Use `compare_strength(earlier, later)` or `compare_running(earlier, later)` to inspect a specific pair, including the reasons a metric is unavailable.

The existing strength selector computes Epley estimates on positive reviewed external kg for working sets of 1–10 reps with no positive time or distance. Its valid-RPE rules and optional inclusive `rpe_range` apply to estimates only. The original set retains its estimate even if the caller has supplied no comparison review. Within each reviewed workout/series, select the highest unrounded eligible estimate separately for confirmed and inferred execution, use the lowest set UUID on ties and report kg rounded half-even to 0.01. Each successive difference points to both winning sets. A modeled change in kg has no progression authority.

Running points retain the original D1D outing and native-day coverage, including the three duration fields, average speed, derived pace, field receipts, revision and instruction issues. A signed time difference requires the same source, mapping, subtype, positive recorded and reviewed distance, reviewed course or protocol, timing field, effort, material conditions and restrictions or interruptions. The selected time must be present and positive on each outing. Activity holds and acquisition discrepancies withhold comparison. Partial enumeration alone can still support comparison of two individually verified outings. A running instruction supplies no achieved-interval or effort evidence.

### Reference windows and consistency

| Result | Window and eligibility | Returned evidence |
| --- | --- | --- |
| Representative running | For a requested Monday week, inspect exactly the four preceding Monday weeks. Each contribution requires seven requested, closed provider dates for the selected account, defensible enumeration and complete measurement support for that metric. Take the median of at least two qualifying weeks independently for sessions, metres, activity seconds, moving seconds and elapsed seconds. | Each candidate Monday retains its D1D observed value, supporting and missing workout IDs, and exclusion reasons. Outside-request and clipped weeks remain visible. Current positive enumeration stores counts without immutable membership. Only D1D's verified complete empty weeks can presently supply an exact total. Retrieval-only empties and lower bounds contribute no numeric sample. |
| Individual sleep duration and resting HR | For provider date D, inspect `[max(request.start, D − 28 days), D)`. Require at least 14 distinct eligible dates **and** last date minus first date ≥ 14 days. Use a reviewed account/metric device-and-protocol interval covering D. Within it, use the latest continuous matching unit, method, field, mapping and writer. A change, even one followed by a return to the old mapping, breaks the series. | The result includes regime/evidence, effective n, contributing facts and dates, missing dates, and excluded cells with reasons. Return median/minimum/maximum only when both thresholds hold. D’s target cell supplies comparison provenance. Its value stays outside the sample. A missing D observation can still have a historical reference. HRV remains available as D1D source facts only. |
| Observed strength consistency | Denominator is every fully requested, closed report-zone week for the selected Hevy account. Numerators count weeks containing any confirmed working set, and any confirmed **or** inferred working set, respectively. | Exact fractions, numerator/denominator Mondays and clipped/open exclusions. No denominator gives a null fraction. Historical daily acquisition remains unknown, including a week with zero recorded sets. |

### Synthetic examples

| Evidence | Supported result | Withheld result |
| --- | --- | --- |
| Primary squat at RPE 7 goes from 60 kg × 5 to 60 kg × 6, then 65 kg × 6 | +1 rep at 60 kg, then +5 kg at six reps. The first two confirmed estimates are 70.00 and 72.00 kg. | A same-workout inferred 70 kg × 5 gives 81.67 kg in its own tier. It cannot displace the confirmed best. A change of barbell to machine breaks the series. |
| Repeat 60 kg × 6 at RPE 8 after an RPE 7 set | +1 recorded RPE at the same work | Default matched-effort difference is unavailable. An absent RPE also leaves effort unknown. |
| Same reviewed 5 km loop, effort and conditions. Elapsed 1,700 → 1,640 s, moving 1,500 → 1,450 s, activity 1,600 → 1,610 s | Respective signed differences under separate timing reviews are −60 s, −50 s and +10 s. | Unknown course, effort, timing or material conditions leaves the outings visible without a directional comparison. |
| Four preceding weeks contain two post-closure verified empty weeks, a partial week and a positive enumeration with matching counts | Reference is zero on two contributing weeks for each metric. | Replacing one verified week with a legacy empty receipt leaves one qualifying week and an unavailable median. |
| Fourteen comparable resting-HR dates spanning 14 days, seven at 54 bpm and seven at 58 bpm | Median 56 bpm, range 54–58, n = 14. | Fourteen consecutive observed dates span only 13 days. A new measurement regime at D also withholds the old reference. |
| Four fully requested closed Hevy weeks, one with confirmed work and another with inferred-only work | Confirmed observed consistency 1/4, confirmed-or-inferred consistency 2/4. | The remaining weeks have unknown acquisition completeness. The fraction measures recorded history, with no plan-adherence denominator. |

E4.2B confirmations carry field-specific assertions. A D1E task review cannot promote an inferred set or attribute an outing to a prescription. E4.2C owns decision-time freezing and support revalidation. [Scoped confirmation contract](scoped-observation-confirmation.md)

## D1F integrated report

`integrate(performance)` takes an existing D1E result. The returned `IntegratedReport` holds that result and its cross-domain pairs in memory. A consumer can read one focus week, follow an evidence identity and discard the report. All views use the same owner-scoped, read-only D1 snapshot.

```python
from fitness_intelligence.analytics.integrated import integrate, report_json

report = integrate(performance)
summary = report.summary()                   # Week of the last requested date
text = report.render(focus_date)             # Short human-readable view
payload = report.to_json(focus_date)         # Deterministic summary
day = report.inspect_day(focus_date)         # Exact daily cells and coverage
for pair in report.summary(focus_date)["proximity"]["pairs"]:
    evidence = report.inspect_pair(pair.strength_workout_id, pair.running_workout_id)
    pair_payload = report_json(evidence)     # Only this pair and its supporting observations
```

The versioned summary includes the half-open reporting period, zone, reference and focus dates, all requested Mondays, selected accounts, policy versions and observation state. Its week uses the requested dates in that Monday week. Changing the focus selects another week and the target date for recovery references. The reference date evaluates closure. The snapshot represents the latest accepted evidence, so choosing a past focus date does not reconstruct what a decision-maker knew then.

The summary retains per-category acquisition counts and issue dates, workout and comparison identities, field-specific measurement denominators, evidence tiers and exclusions. Recovery, endurance, strength and expenditure are optional selections. JSON encodes an unavailable value as `null`, an eligible count as an integer, decimals as exact strings, dates as ISO dates and instants in UTC. A supported zero survives serialization. The following lookups resolve evidence from the same in-memory result.

| Inspection | Evidence returned |
| --- | --- |
| `inspect_day(date)` | Original daily cells and accepted observations, including intake logging evidence, weight identities, acquisition, reconciliation holds and source-only HRV. |
| `inspect_workout(id)` | A selected canonical workout, its sets or outing, source and revision evidence, review and comparison exclusions. Strength evidence includes actual set completion and achieved RPE where recorded. |
| `inspect_pair(strength_id, running_id)` | Both canonical workout IDs, the exact qualifying lower-body sets, the running outing, independent duration fields, instruction issues, reviewed effort, conditions and restrictions. Tolerance stays unknown without evidence. |
| `inspect_running_reference(monday, metric)` | Four candidate weeks with their native-date acquisitions, supporting and missing workout IDs, independent metric values and reasons for exclusion. |
| `inspect_recovery_reference(date, metric)` | Target cell, reviewed regime, contributing observation identities and values, excluded cells and reasons. |

### Calendar proximity and elapsed time

Strength membership comes from the selected account’s explicitly reviewed lower-body templates and D1D’s eligible working sets. Each selected running outing can pair once with each eligible strength workout whose aligned report date is the same or one calendar day away in either direction. Multiple qualifying exercises or sets contribute their own identities and repetitions to that one pair. Missing repetition measurements have no numeric contribution. An inferred-only workout yields a tentative pair. Mixed workouts retain separate confirmed and inferred lists.

Strength dates use the recorded start in the report zone. The selected provider calendar must be verified and aligned, and the running outing’s provider date must agree with its start in that zone. An activity hold or acquisition discrepancy withholds the flag and preserves the outing, its dates and reason. A partial activity enumeration can still support an individual outing. An instruction issue remains visible independently. The search covers the whole requested period, including adjacent Monday weeks. Each pair appears in the focus week of its run. Unrequested dates supply no pairing evidence.

The timing record gives start order, absolute start-to-start seconds, and signed later start minus earlier recorded workout end. A positive gap measures the observed interval between sessions. Zero denotes touching endpoints. A negative gap puts the later start inside the earlier session. Two recorded positive spans establish overlap. If the later end is missing, the report can still say that it started during the earlier session. An unknown earlier end leaves the interval null. Simultaneous starts have zero start separation and no ordered end-to-start interval. All subtraction uses UTC instants, including across DST. A set completion time marks that set alone. Moving time, elapsed time, scheduled reservations and individual set timestamps supply no workout end.

The view describes recorded scheduling. A missing workout leaves rest and exposure unknown. Proximity supplies no basis for attributing a performance change, estimating fatigue or choosing a recovery duration.

### Five-week synthetic example

The database-backed fixture selects one synthetic owner, a Hevy account and a Garmin account. Both calendars use `America/Toronto`. The request covers February 10 through March 16, 2025 inclusive, with March 17 as the reference date. The focus is March 16. Extra workouts sharing external IDs on other accounts and under another owner provide isolation checks.

| Monday | Recorded strength and running | Evidence used for the March 10 running reference | Pairs attributed to the run week |
| --- | --- | --- | ---: |
| Feb 10 | No recorded lift. Verified complete empty scans on seven closed provider dates. | Exact zero | 0 |
| Feb 17 | No recorded lift. Seven more verified complete empty dates. | Exact zero | 0 |
| Feb 24 | Feb 25 inferred squat, seven reps. Feb 26 recorded 5 km run. | Partial enumeration. One observed session and 5,000 m. | 1 |
| Mar 3 | Mar 8 recorded 3 km run. Mar 9 confirmed squat, 60 kg × 5. | Positive enumeration lacks immutable membership. One observed session and 3,000 m. | 1 |
| Mar 10 | Three strength visits. Three eligible runs over 9 km, one additional held outing and one squash session. | Target week | 3 |

| Strength / run dates | Start separation | Signed end-to-start | Supporting evidence |
| --- | ---: | ---: | --- |
| Feb 25 / Feb 26 | 24 h, strength first | +23 h 30 min | Inferred-only lower-body execution. |
| Mar 9 / Mar 8 | 23 h, run first | Unknown | Both start at local noon across the spring clock change. The Saturday run has no recorded end. |
| Mar 9 / Mar 10 | 24 h, strength first | +23 h | Sunday’s workout ends at 13:00 EDT. Monday’s run starts at noon. |
| Mar 10 / Mar 10 | 15 min, strength first | −20 min | Strength 15:45–16:20 UTC, run 16:00–16:30 UTC. The recorded sessions overlap. |
| Mar 13 / Mar 13 | 1 h, strength first | Unknown | The strength set has a completion timestamp. The session end is unknown. |

An excerpt from `report.render()` shows both the sampled reference and the exposure left outside it.

```text
Observed strength weeks · 2/5 confirmed, 3/5 confirmed or inferred
Running · at least 3 sessions, at least 9000 m
Squash · at least 1 session, distance unavailable
Reviewed run · elapsed time change -60 s
Sampled running sessions/week · median 0 from 2/4 preceding weeks. Habitual exposure unknown.
Excluded weeks, observed sessions · 2025-02-24 1 (lower bound), 2025-03-03 1 (lower bound)
Aligned strength/run pairs · 3, including 0 tentative
```

The focus week has the following supporting results.

- **Strength.** Three visits have five confirmed working sets and one inferred working set. Recorded consistency across the five closed weeks is 2/5 with confirmed work and 3/5 with confirmed or inferred work. The reviewed high-bar squat at achieved RPE 7 changes from five to six reps at 60 kg, with estimated 1RM from 70.00 to 72.00 kg. The unclassified exercise contributes to recorded strength exposure only.
- **Running and squash.** Three eligible running outings supply at least 9,000 m. Activity time totals 2,830 s from 3/3 outings, moving time 2,020 s from 2/3 and elapsed time 2,910 s from 3/3. Squash supplies one session and 900 activity seconds. Its distance is unavailable. The reviewed 5 km loop at recorded RPE 6 in dry, uninterrupted conditions changes from 1,700 to 1,640 elapsed seconds, a difference of −60 s. Outings without comparable task evidence retain their observations.
- **Running reference.** For each of sessions, metres, activity seconds, moving seconds and elapsed seconds, the sampled median is zero on 2/4 qualifying weeks. The two excluded weeks contain a recorded 5 km and 3 km run. Habitual training exposure remains unknown.
- **Recovery.** Sleep duration is 24,000 s on five eligible focus-week dates, with one missing date and one held date. Its March 16 prior reference has median 24,000 s on 26 dates. Resting HR is 59 bpm in the new reviewed regime. Six preceding dates in that regime leave the reference unavailable. Overnight HRV and trailing weekly HRV each have one source-only observation.
- **Intake, expenditure and weight.** Eligible reported intake of 2,100 and zero kcal yields 2,100 kcal total and 1,050 kcal per eligible date. Wearable expenditure on one date is 2,300 total and 500 active kcal. Basal expenditure is unavailable. The eligible weight median is 71 kg on three dates, up 1 kg from 70 kg on three dates in the preceding week. A separate held measurement stays inspectable.

For an evidence lookup, select the March 10 same-date pair from the summary and call `inspect_pair` with its two IDs. The result identifies the squat and lunge exercise IDs, two confirmed sets (six and four reps), and one inferred drop set (five reps). This accounts for all 15 recorded lower-body reps. The unclassified 20-rep set belongs to the workout and is visible through `inspect_workout`. The run records 5,000 m, 1,610 activity seconds, 1,450 moving seconds and 1,640 elapsed seconds. Partial acquisition and an instruction issue remain visible with the accepted outing. Tolerance is null. The March 12 provider-date outing starts on March 11 in Toronto, so its 2 km contributes to native-date exposure with a withheld proximity flag. A March 14 activity hold excludes a retained 9 km outing from both the eligible subtotal and proximity. Its original measurement and issue are available by workout ID.

### D1V proposal for separate operator authorization

1. Before any private read, the operator approves **one owner**, the exact Hevy account and each Garmin account selected for the requested metrics, the owner-day intake source scope, calendar evidence, report recipient and retention period. Enter real identifiers locally. Choose a recent representative six-week interval within the requested four-to-eight-week range. Record its inclusive Monday start, exclusive Monday stop and reference date after the last requested date has closed in each known calendar.
2. Record the report IANA zone and independently verified provider zone for each selected account. Record travel, device and timezone changes. Split the validation into reviewed intervals or leave the relevant alignment unknown. Review Hevy template IDs, movement, variation, equipment, load interpretation, lower-body membership, set role, ordinal and achieved effort. Review run distance, course or protocol, timing field, effort, conditions and interruptions. Record sleep and resting-HR regime intervals, measurement units and weight writer evidence. Leave unsupported attributes unknown.
3. Use local read-only access to an approved stable database snapshot and the existing repeatable-read report selector. Independently count owner/account-scoped active workout references, unique workouts, exercises and sets by evidence tier, native-date outings by sport, eligible/missing observations by metric and day, and category/date activity receipts and open reconciliation issues. Record those expected counts locally before comparing the report. Include any additional same-owner intake contributors in the approved scope. Resolve a scope mismatch before reading further.
4. Reconcile canonical identities, native and report dates and per-field denominators against those counts. Inspect one selected pair of each available evidence tier, an unmatched workout, and available held, partial or empty dates. Check the UTC start order and signed gap against recorded endpoints. Check that a complete zero has a verified post-closure scan, excluded positive weeks retain their recorded runs, and missing or held values stay unavailable. Reconcile comparison keys, recovery-regime boundaries, weight series and confirmed/inferred consistency denominators. Record a limitation if the interval contains no example of a case.
5. Keep report output, evidence identities and review inputs local with operator-approved access and encrypted storage. Display only the evidence required for each check. Share aggregate pass/fail counts and non-identifying limitations only with the approved recipient. Exclude payloads, account IDs, credentials, connection strings and personal measurements from logs, source control and PRs. Remove any retained private output at the agreed deadline. D1V authorizes no acquisition, reconciliation writes, migrations or coaching actions.
