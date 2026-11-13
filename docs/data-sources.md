# Data sources

These are intended sources, not implemented integrations or verified API access contracts.

| Source | Intended data | Planned boundary |
| --- | --- | --- |
| Hevy | Workouts, exercises, sets, reps, weights | Backend provider adapter |
| Garmin Personal API | Running, sleep, HRV, resting heart rate | Backend provider adapter; verify access and terms before implementation |
| Android Health Connect | RENPHO-origin body weight; MyFitnessPal-origin calorie intake | Later Kotlin bridge reads permitted on-device records and uploads normalized data |
| Strava | None | Explicitly out of scope |

Health Connect is the transport for weight and calorie intake, not a direct RENPHO or
MyFitnessPal backend connection. Availability depends on upstream apps actually writing the
required records, device support, history access and granted permissions; validate these before
committing to ingestion behavior. Record original source attribution to prevent duplicate imports.

Future ingestion must be idempotent, user-scoped and explicit about units, UTC timestamps,
time zones, provenance, updates and deletions. Preserve missing values. Use synthetic fixtures.
No provider credentials or real source exports belong in this repository.
