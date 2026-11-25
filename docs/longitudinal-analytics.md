# Daily reported intake and body weight

D1B implements the first slice of the [longitudinal analytics design](unified-longitudinal-analytics-design.md). A trusted local caller supplies an already authorized owner, a PostgreSQL engine, a half-open calendar period and one Garmin weight account. Each date has a row, including dates with no observations.

```python
from datetime import date
from zoneinfo import ZoneInfo

from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.db.longitudinal import query_longitudinal

zone = ZoneInfo("America/Toronto")
report = query_longitudinal(
    engine,
    owner_id=authorized_owner.id,
    weight_account_id=garmin_account_id,
    period=Period(date(2025, 3, 3), date(2025, 3, 10), zone),
    source_zones={garmin_account_id: zone},  # Known provider calendar for these dates.
)
monday = report.days[0]
reported_kcal = monday.intake.metric.value
median_kg = monday.weight.metric.value
weigh_ins = monday.weight.measurements
```

The report opens its own read-only PostgreSQL REPEATABLE READ transaction. Pass an engine, keeping any application session or transaction outside the call. Provenance, issues, coverage and both existing selectors use the same snapshot. Owner and source-account UUIDs must come from the trusted caller. The weight account must have a resolved Garmin binding to that owner. A disconnected account can still supply retained records. The query requires no provider session or credentials.

## Reading a daily row

- **Calendar.** The date spine and every daily value use provider-local dates. The request's IANA zone controls the interpretation of an instant's report date. Supply an optional verified IANA zone per source account only when it applies to the whole period. Split the request across travel/regime changes. A single account's native daily total remains available with unknown zone and a null aligned date. Combining intake facts across accounts requires matching known source zone keys. A metric gets an aligned report date only when the calendars agree with the report zone. Each eligible weigh-in separately exposes its instant's report date, including a different date across midnight.
- **Intake.** The owner-day selector compares all source totals on the date. Agreement yields one value, disagreement or a retained disagreement issue withholds it. All contributing IDs, original reported totals, source fields, mapping versions, retrieval times, logging completeness, presence evidence and known writer are in `facts`. A true presence flag or the recognized Garmin food mapper's logged-food evidence supports explicit zero. Keep unsupported zeros visible as excluded facts. Missing intake and disputed intake both have null values and distinct reasons.
- **Weight.** The account-day selector withholds the whole day on any open weight issue. Held rows expose IDs and reasons in `excluded`. Eligible individual readings preserve canonical kg, original numeric value, interpreted and documented units, UTC instant and precision. The daily median gives each eligible reading equal weight. The mean of the two central values is exact, including an extra decimal place when necessary.
- **Verification.** A recognized historical weight row carries the segment fingerprint assigned by the account/date-bounded writer. The report checks the reviewed mapping, field, time precision, units and conversion. A legacy bounded write carries the B3.2 mapper's independently chosen unit and can predate the segment column. Its complete producer signature is accepted on a day without historical acquisition, or before a failed historical attempt with no prior success. When the historical ledger leaves an unscoped row's origin ambiguous, its ID is retained with `unverified_weight_unit`. A plausible mass or the documented kg label cannot establish the wire unit. The report never reads private verification files.
- **Coverage.** Each account/category/date has its own latest status, attempt, last successful time/count, pass, policy, available source receipts, gap reason and open issue subjects/reasons. Intake includes the owner's Garmin accounts and any other intake contributors in the request. Weight has one source. `observations_without_coverage` distinguishes retained facts on a never-queried historical day. A successful empty lookup supplies no numeric zero. Retained verified facts can contribute after a partial or failed attempt. `metric.eligible_count` counts supporting identities and `retained_count` includes withheld rows. Two agreeing intake IDs still yield only one day of reported kcal.

## Synthetic seven-day example

This is the seven-day regression fixture, shown on the provider calendar. An em dash denotes an unavailable value. All seven dates are requested, including the March 9 clock change.

| Provider date | Selected kcal | Daily median kg | Evidence |
| --- | ---: | ---: | --- |
| Mar 3 | 2,100 | 70.0000000015 | Two agreeing intake facts on a partial acquisition day. Two segment-verified weigh-ins of 70.000000001 and 70.000000002 kg. |
| Mar 4 | 0 | 70.4 | Positive intake presence flag. One bounded weigh-in predating historical coverage. |
| Mar 5 | — | — | Unsupported intake zero. Two retained weights withheld for a possible retime. |
| Mar 6 | — | — | Both acquisitions completed empty. |
| Mar 7 | — | — | Conflicting intake totals. The stored historical mass lacks segment verification. |
| Mar 8 | — | 73 | A disagreement hold remains after the intake fields agree. Verified weight survives a failed refresh. |
| Mar 9 | 0 | 74 | A recognized food observation supports zero. The weight instant falls on March 8 in the report zone, so the provider-day median has no aligned report date. |

For March 3 the intake metric has two supporting identities and one selected value. For March 5 the weight metric has zero eligible readings out of two retained. Logging completeness is unknown throughout.

The immutable Python results record the request, source calendars, contract and policy versions. Historical calendar queries return the current accepted rows. Recorded availability is unknown for these mutable canonical measurements. A later correction can change the same query's result. Decision replay requires separately frozen facts, coverage and policy versions. The next D1 slice can build weekly intake and weight summaries over these daily values and denominators, then extend the same contracts to other domains.
