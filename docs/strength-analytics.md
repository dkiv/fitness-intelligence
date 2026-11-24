# Strength analytics foundation

The internal Python API returns three chronologically ordered Polars tables. A trusted caller
supplies the owner and a SQLAlchemy session. The PostgreSQL reader projects canonical IDs, names,
timestamps and measurements in one statement. It scopes workouts, exercises, sets and references
to that owner. A UUID by itself grants no access. Analytics can also run in memory on normalized
`Observation` rows from one owner. Supply each set once, plus a placeholder for each childless
workout or exercise. A repeated in-range set ID raises an error.

```python
from datetime import date
from decimal import Decimal
from zoneinfo import ZoneInfo

from fitness_intelligence.analytics.strength import ExerciseSeries, Period
from fitness_intelligence.db.strength_analytics import query_strength

# The caller has resolved owner_id and identified two comparable exercise occurrences.
series = {
    first_press_id: ExerciseSeries("barbell-bench", external_load=True),
    later_press_id: ExerciseSeries("barbell-bench", external_load=True),
}
report = query_strength(
    session,
    owner_id=owner_id,
    period=Period(date(2025, 1, 1), date(2025, 2, 1), ZoneInfo("America/Toronto")),
    series=series,
    rpe_range=(Decimal("8"), Decimal("9")),
)
```

## Window, identity and completion

- Dates use the supplied IANA zone (UTC by default), inclusive start and exclusive stop. Each
  workout belongs to its start day, including every set in sessions that cross midnight. Weeks
  start Monday at local midnight. Boundary weeks cover only the requested days.
- Canonically deleted workouts and workouts whose references are all source-deleted are excluded.
  An unreferenced workout is active. A shared workout with an active reference remains eligible
  unless canonically deleted. Pending source events take effect once canonical deletion is resolved.
- Names are display snapshots. By default each exercise occurrence has a distinct key. An explicit
  mapping can combine equivalent occurrences across sessions or within a session. Use a distinct
  key for each equipment/load convention. The schema has no movement taxonomy. Imported edits
  can replace occurrence IDs, so refresh mappings when snapshots change.
- Strict completion requires a set completion timestamp. Some historical sources omit it. Use
  `infer_completion=True` to also accept sets in ended workouts with positive reps, duration
  or distance. This proxy cannot distinguish prescribed from performed values. Default strict
  reports can show workouts with zero qualifying sets.
- All formulas use canonical kilograms and repetitions. Only a series designated
  `external_load=True` qualifies for load arithmetic. This designation means that the recorded
  kilograms are comparable external resistance for a repetition-based movement. Leave bodyweight,
  assistance, unknown weight conventions and other unsupported movements unclassified for load.
  Their completed sets and recorded reps still contribute. Positive distance or duration excludes
  a set from load calculations. No body mass, per-side multiplier or inferred resistance is added.

## Output tables

**Progression** contains Epley estimated 1RM in kg, computed as
`weight_kg × (1 + repetitions / 30)` uniformly for 1–10 reps, inclusive. This modelled value
can differ from a measured maximum, particularly at submaximal effort. Eligible sets are
completed normal, failure or drop sets with positive external load. Unknown RPE is eligible
by default. An inclusive RPE interval requires a known matching value on the canonical 0–10
scale. The interval filters estimates only and makes no adjustment for reps in reserve.
By default each workout and exercise key contributes its highest unrounded estimate.
Ties use ascending canonical set UUID. Output includes the selected set, source exercise
occurrence, kind, weight, reps and RPE. Set `top_only=False` for all qualifying sets.
Results use decimal arithmetic and round half-even to 0.01 kg after selection.

**Weekly volume** has one row per observed week, exercise key and category. Normal, drop and
failure sets are working sets. Warmups and unrecognized kinds each have their own category.
Each row reports completed sets, distinct workouts, observed display names, recorded repetitions
and the sum of `weight_kg × repetitions` (kg·reps). Superset membership adds no sets.
Known zero values contribute zero. Missing measurements contribute nothing to the corresponding
sum, which is null if no qualifying value exists. `sets_with_reps` and `sets_with_load` give
the coverage of each subtotal. Sum category rows to combine sets, reps or load. Distinct workout
counts can overlap across rows.

**Weekly activity** includes every intersecting week, including zero-activity weeks. Frequency
counts distinct active workouts starting in the period, including open and empty workouts.
Exercises performed counts distinct exercise keys with at least one completed set. The volume
table identifies those exercises by week. Completed sets include every category. Workout change
is the signed difference from the preceding displayed week, null for the first. Partial weeks
are compared using their observed counts. A zero records absence of eligible observations.
