# Data sources

Hevy has a private local read-only importer as of M2B.2; other integrations remain planned.
Hevy's official contract is verified against documentation; live account behavior remains
unverified. See [local synchronization setup and limitations](hevy-importer.md).

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

## Hevy M2A research

See the [proposed Hevy integration contract and synchronization design](hevy-sync-design.md)
for official sources reviewed on 2026-11-13, source-to-canonical mapping, unsupported child
identity continuity, account namespace migration, deletion limitations and M2B implementation
gates. The design uses only official schema examples and synthetic illustrations, not personal
workout responses. M2B.1 now implements the account schema and pure mapping foundation;
[architecture.md](architecture.md) defines the implemented JSON, timestamp and semantic hash
contracts. No live provider client or synchronization orchestration has been implemented.
