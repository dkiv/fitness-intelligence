# Daily and weekly intake, wearable expenditure and body weight

The internal report implements the daily nutrition and weight slices of the [longitudinal analytics design](unified-longitudinal-analytics-design.md). A trusted local caller supplies an already authorized owner, a PostgreSQL engine, a half-open calendar period and one Garmin weight account. Each date has a row, including dates with no observations.

```python
from datetime import date
from zoneinfo import ZoneInfo

from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.analytics.weekly import aggregate_weeks
from fitness_intelligence.db.longitudinal import query_longitudinal

zone = ZoneInfo("America/Toronto")
report = query_longitudinal(
    engine,
    owner_id=authorized_owner.id,
    weight_account_id=garmin_account_id,
    expenditure_account_id=garmin_account_id,
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

The report opens its own read-only PostgreSQL REPEATABLE READ transaction. Pass an engine, keeping any application session or transaction outside the call. Provenance, issues, coverage and both existing selectors use the same snapshot. Owner and source-account UUIDs must come from the trusted caller. The weight account must have a resolved Garmin binding to that owner. A disconnected account can still supply retained records. The query requires no provider session or credentials.

## Reading a daily row

- **Calendar.** The date spine and every daily value use provider-local dates. The request's IANA zone controls the interpretation of an instant's report date. Supply an optional verified IANA zone per source account only when it applies to the whole period. Split the request across travel/regime changes. A single account's native daily total remains available with unknown zone and a null aligned date. Combining intake facts across accounts requires matching known source zone keys. A metric gets an aligned report date only when the calendars agree with the report zone. Each eligible weigh-in separately exposes its instant's report date, including a different date across midnight.
- **Intake.** The owner-day selector compares all source totals on the date. Agreement yields one value, disagreement or a retained disagreement issue withholds it. All contributing IDs, original reported totals, source fields, mapping versions, retrieval times, logging completeness, presence evidence and known writer are in `facts`. A true presence flag or the recognized Garmin food mapper's logged-food evidence supports explicit zero. Keep unsupported zeros visible as excluded facts. Missing intake and disputed intake both have null values and distinct reasons.
- **Weight.** The account-day selector withholds the whole day on any open weight issue. Held rows expose IDs and reasons in `excluded`. Eligible individual readings preserve canonical kg, original numeric value, interpreted and documented units, UTC instant and precision. A combined daily median requires one verified series. Different known writers yield a null median with `incompatible_weight_regimes`. When the series differ but continuity is unknown, the reason is `weight_comparability_unverified`. Missing writer metadata alone cannot identify a different scale. The `measurements`, supporting IDs and eligible observation count still include every individually eligible reading on a mixed day. The mean of the two central values is exact, including an extra decimal place when necessary.
- **Verification.** A recognized historical weight row carries the segment fingerprint assigned by the account/date-bounded writer. The report checks the reviewed mapping, field, time precision, units and conversion. A legacy bounded write carries the B3.2 mapper's independently chosen unit and can predate the segment column. Its complete producer signature is accepted on a day without historical acquisition, or before a failed historical attempt with no prior success. When the historical ledger leaves an unscoped row's origin ambiguous, its ID is retained with `unverified_weight_unit`. A plausible mass or the documented kg label cannot establish the wire unit. The report never reads private verification files.
- **Coverage.** Each account/category/date has its own latest status, attempt, last successful time/count, pass, policy, available source receipts, gap reason and open issue subjects/reasons. Intake includes the owner's Garmin accounts and any other intake contributors in the request. Weight has one source. `observations_without_coverage` distinguishes retained facts on a never-queried historical day. A successful empty lookup supplies no numeric zero. Retained verified facts can contribute after a partial or failed attempt. `metric.eligible_count` counts supporting identities and `retained_count` includes withheld rows. Two agreeing intake IDs still yield only one day of reported kcal.

- **Wearable expenditure.** Pass an explicit, resolved Garmin account owned by the same principal. It may differ from the weight account. Omit `expenditure_account_id` to keep the D1B query behavior. Each selected day has independent `total`, `active` and `basal` metrics. A value requires the corresponding accepted canonical kcal observation with method `wearable_estimate`. Each fact carries the original method, unit, field, observation ID, measurement window and available retrieval/mapping evidence. Unknown legacy provenance stays null. A category/day hold withholds all affected components. A component-specific issue only holds that field. Active and basal never supply a missing total.

## Weekly calculation

`aggregate_weeks(report, *, reference_date, weight_continuity=None)` is a pure function over the daily snapshot. The returned report retains the daily facts, period, zones, selected sources, policy, reference date and optional continuity evidence. The daily contract is `d1c-v1`. Daily intake and weight use policy `intake-weight-v2` for the combined daily weight median. The weekly conventions use `nutrition-weight-weekly-v1`.

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

The immutable Python results record the request, source calendars, contract and policy versions. Historical calendar queries return the current accepted rows. Recorded availability is unknown for these mutable canonical measurements. A later correction can change the same query's result. Decision replay requires separately frozen facts, coverage and policy versions. The next D1 slice can extend these daily and weekly contracts to strength, running and recovery exposure.
