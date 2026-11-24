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

## Hevy historical profile

Use `query_hevy_history` for imported history from a single source account. The mapper leaves
set completion timestamps empty. The profile counts a timestamped set as confirmed and infers
completion for an untimestamped set only when its workout has ended and the set has positive
repetitions, duration or distance. Weight alone is insufficient. The provider-independent
`query_strength` continues to require confirmed completion by default.

```python
from fitness_intelligence.adapters.hevy.analytics import HevyHistoryProfile, query_hevy_history

# Supply the internal source-account UUID and exact template IDs reviewed for this account.
profile = HevyHistoryProfile(account_id, external_load_templates=frozenset({"synthetic-press"}))
report = query_hevy_history(session, owner_id=owner_id, period=period, profile=profile)
```

Both query functions expose completion evidence. In weekly activity and volume, `inferred_sets`
is the subset of `completed_sets` counted by inference. Subtraction gives the confirmed count.
Each progression row carries a `completion_inferred` flag for the selected set. A week can have
a mix of both. Inference establishes eligibility for a report and never writes a completion time.

The profile reads an owner’s active workouts with exactly one workout reference, belonging to the
selected Hevy account. Shared references are ambiguous and the profile omits those workouts.
The reader retrieves canonical measurements and template metadata in a single PostgreSQL
statement so concurrent imports cannot mix snapshots. It recognizes the current importer and
hash-contract tags, matches the retained workout ID and checks exercise count, contiguous
canonical positions and increasing source indexes. The source index may have gaps. Its sorted
position identifies the exercise in the retained projection. A count or ordering mismatch, or
unrecognized metadata, leaves the whole workout occurrence-scoped. A missing template ID leaves
that exercise occurrence-scoped. Eligible sets in these cases still count toward activity and reps.

A longitudinal series uses the account UUID and the exact template ID. The same name can identify
different templates, and the same template string in a second account produces a distinct series.
Even a valid template identity establishes no load convention. The default empty allowlist gives
set and repetition totals. Only explicitly listed external-resistance templates can supply
kg·reps or Epley estimates. Leave bodyweight, assistance and uncertain conventions off the list.

The mapping relies on the importer's atomic paired snapshot. Manual edits to canonical exercise
order or provenance can invalidate it, and structural checks cannot detect every such edit. A
template reused for different equipment or loading practices can also break comparability.
There is no cross-account matching, name-based fallback or automatic equipment classification.
