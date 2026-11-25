# B3.1 · Bounded local Garmin ingestion

B3.1 verifies the account behind the macOS Keychain credential, enrolls an active source
account, and imports one activity search page or one provider-local recovery day. Each command
runs in a trusted, single-owner terminal and exits. Automated validation uses invented
responses and disposable PostgreSQL. Live B1 availability checks and B3.1 enrollment
establish different facts. A personal B3.1 rehearsal still requires operator review.

## Evidence required for enrollment

Resolve the existing canonical athlete through the trusted local administration session.
Sign in to the intended Garmin Connect account independently of the Keychain credential.
Identify an owned activity, its numeric activity ID and its provider-local date. Obtain
provider-issued evidence linking that account to its numeric profile ID, and confirmation
that this identity is stable across credential changes and applies to the selected feeds.
An official export can help if it explicitly identifies the field. Keep the evidence local.

The Personal API documents an owner on each activity and profile fields on recovery DTOs.
The settings DTO supplies preferences and a display name. The contract reviewed for B1/B2
leaves the permanence of those numeric identifiers and their shared namespace unconfirmed.
An API key exchange and agreement among response fields verify access and consistency.
The independently established owner and profile give those comparisons their meaning.
The CLI treats independent evidence and durability as **operator attestations**.
[Garmin Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api/) ·
[B2 identity procedure](endurance-recovery.md#bounded-local-identity-verification-before-b3)

**If independent evidence is unavailable, leave enrollment unresolved.** A possible
single-owner alternative for review is to sign in to the intended account, issue a fresh
key in that session, independently select an owned activity and its local day in Connect,
and check that exact activity with the key. The operator would explicitly approve pinning
the profile first seen in its owner/detail fields and each matching feed. Future imports
and key replacements would have to pass the original pin and owned-activity checks.
This would establish a locally witnessed association with a residual risk of provider
identifier reuse or namespace change. It requires a separate policy decision. B3.1 has
no first-use enrollment switch.

## Prepare the rehearsal after review

1. Use the existing private workstation, macOS login Keychain item and a local PostgreSQL 17
   database under the athlete's control. Apply the established retention, backup, restoration
   and owner-erasure boundaries to the Garmin rows and binding file. Keep credentials, the
   database and its backups, and independent identity evidence outside Git and cloud sync.
   [Keychain setup](garmin-verification.md#set-up-the-key-on-macos) ·
   [Local storage and recovery](hevy-importer.md#storage-and-recovery-gates-before-a-personal-import)
2. Confirm the local owner UUID. Reserve a fresh local source account UUID for first enrollment,
   or use the existing active Garmin account UUID for this owner and profile. Reuse these
   same identifiers for every run. Enrollment can be replayed after interruption.
3. In a private directory owned by the OS operator (mode 0700), create `garmin.json` with
   mode 0600 using a private editor. The command checks file type, size, permissions and
   OS ownership on the opened descriptor and rejects a symlink. Start with the template below.
   Replace each placeholder locally. Supply the profile and activity IDs as **JSON integers**.
   Use `feeds: []` for activity-only verification, or select from `daily`, `sleep` and `hrv`
   for recovery. Choose an anchor with identity and date evidence for every selected feed.
   Set each confirmation to true only after obtaining the corresponding evidence.
4. From `backend/`, run `uv sync --frozen`. Inject `DATABASE_URL` from the local secret
   manager. Apply `uv run --frozen alembic upgrade head` through the administration role
   before rehearsal. Revision `b301` leaves retrieval and mapping provenance unknown for
   pre-existing B2 recovery rows. Its downgrade refuses to discard populated provenance.
   Use a read-only role with SELECT on users and source_accounts for verify-only. Switch
   to the trusted local import role for explicit enrollment and observation writes.

```json
{
  "user_id": "<existing local owner UUID>",
  "source_account_id": "<reserved or verified source account UUID>",
  "profile_id": null,
  "known_activity_id": null,
  "known_day": "YYYY-MM-DD",
  "feeds": ["daily", "sleep", "hrv"],
  "independent_profile_confirmed": false,
  "durability_confirmed": false
}
```

## Run one bounded rehearsal

Set `day` to the provider-local date you have approved. The anchor day is a convenient
first rehearsal because the importer reuses the verified responses. Run each command
individually and inspect the summary before continuing.

```sh
binding="$HOME/.config/fitness-intelligence/garmin.json"
day=YYYY-MM-DD
uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" verify-only
uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" enroll
uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" activities --day "$day"
uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" recovery --day "$day"
```

Verify-only reads the private configuration, local owner and any matching source account.
It exchanges the Keychain credential and searches the anchor day once with offset zero and
limit three. The known activity must appear. Its search owner, detail profile and echoed
activity ID must match. Each selected recovery feed must return its own profile and exact
provider calendar date. These checks take at most five logical reads. Missing evidence,
unknown owner, inactive account or mismatch stops the operation. Verify-only performs
zero database writes, including before first enrollment. Enrollment repeats verification
and commits only source-account metadata. Disconnection requires a separate local decision.

Both import commands repeat the anchor checks using the current credential. A rotated key
uses the original binding file. Failure leaves the account and existing observations intact.
Activity import fetches one page for the requested day and its associated details. Add
`--steps` to retrieve one performed-workout response per returned activity. Recovery
import reads one requested day per selected feed. On another day the largest activity run
uses five anchor reads, a search and up to three detail/step pairs. The existing transport
caps all attempts at 40 HTTP requests and three minutes, including exchange and 401 replay.
Each JSON response is bounded to 2 MB and fractional numbers decode directly to Decimal.

Repeat the same import command with the same options to reconcile that window. Summaries
contain fixed comparison outcomes or counts of observed, created, updated, unchanged,
older, unresolved or partial records. Identical source observations should report unchanged.
A page of three may have additional activities outside this rehearsal. An empty target
page means zero observed. HRV 204 on a target day after verification increments
`feeds_without_content` and retains prior HRV. Failed reads or mismatched responses stop
the operation. The anchor itself always requires positive evidence. CLI diagnostics suppress
HTTP, Keychain and SQL details. Use the exit status and summary without recording private
source values, IDs or dates.

## What commits

- The existing per-account PostgreSQL advisory lock covers verification, target reads and
  the commit. HTTP runs outside write transactions. The importer stages the entire requested
  operation, revalidates and row-locks the active account, then commits the complete page
  or recovery day atomically. An unsuccessful commit can be retried with the same window.
- The external workout key covers owner, provider, source account, entity type and Garmin
  activity ID. Edits reuse the workout, reference and first-import time. Other accounts have
  independent namespaces. Workouts are created with a fixed title. A time collision with
  a Hevy workout creates no link.
- The source projection stores normalized start, its precision, local date, sport, observed
  quantities as decimal strings, and supplied child collections. Alongside that merged state,
  the latest accepted retrieval retains only the typed search, detail and optional step inputs
  needed to rerun the mapper. Tagged decimals preserve their original precision. The replay
  function takes the owner and activity keys from the verified account and external reference.
  The mapper version, source
  field or collection path and retrieval time identify measurement provenance. Retrieved
  fields also retain their activity revision time when supplied. The reference carries the
  last accepted retrieval and the detail field `metadataDTO.lastUpdateDate`, interpreted as
  UTC. Missing revision evidence stays unknown. Coordinates, routes, private names, raw
  response objects, tokens and unrelated health fields have no place in the projection.
- Missing scalar fields preserve prior values and their recorded provenance. A coarser
  start that agrees at its own precision retains the finer instant. A missing collection
  or a group with missing steps retains the previous children. An explicitly empty
  collection clears that collection. Eligible changed collections replace their snapshots.
  Sparse child fields that would erase known values on the same instruction or split hold
  the collection and report a partial result.
- Older revisions are skipped. An undated response following a dated activity is unresolved.
  An equal revision with contradictory known values rolls back the page. When both revisions
  are unknown, serialized retrieval order determines the latest positively observed values.
  Garmin supplies no deletion evidence through this workflow. Failed lookups, empty pages
  and absent measurements leave prior records in place.
- Daily rows retain their UUID for the account, provider date and metric. Positive evidence
  includes an explicit zero. Each observed row carries its source field, mapper version and
  UTC retrieval time. The provider-local date describes attribution. GMT bounds describe
  the last known coverage window when supplied. Daily aggregates have no asserted point
  observation time. Seven-day HRV has no asserted UTC bounds, and both HRV metrics retain
  `source_unit_unverified`. Expenditure remains a wearable estimate. Omitted metrics retain
  their prior value and retrieval time. [Units and DTO definitions](endurance-recovery.md)

For erasure, disconnect and revoke the source, then follow the existing owner-scoped local
procedure. Include performed steps and splits before endurance parents, references and
workouts, and recovery rows before source accounts. Include the private binding, temporary
exports, backup expiry and reapplication of erasure after restore. Stop after the approved
page and day. Nutrition, body weight and historical synchronization are later milestones.
