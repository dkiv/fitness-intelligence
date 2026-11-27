# B3 · Bounded local Garmin ingestion

B3.1 verifies the account behind the macOS Keychain credential, enrolls an active source
account, and imports one activity search page or one provider-local recovery day. Each command
runs in a trusted, single-owner terminal and exits. Automated validation uses invented
responses and disposable PostgreSQL. Live B1 availability checks and B3.1 enrollment
establish different facts. The controlled B3.1 rehearsal verified the enrolled account, bounded activity and recovery writes, and identical replay. B3.2 adds a separate [intake and weight workflow](#intake-and-body-weight).

## Evidence required for enrollment

Resolve the existing local athlete in the trusted administration session. Independently sign
in to the intended Garmin Connect account, select an owned activity there, and privately
record its numeric activity ID and provider-local day. Choose an anchor day with identity
and date evidence for each selected wellness feed.

| Evidence type | What the operator establishes | What the importer checks |
| --- | --- | --- |
| `independent` | Provider-issued evidence identifies the account's numeric profile and confirms its scope and stability across credentials. An official export may help when it explicitly identifies the field. | The activity owner in search, the echoed detail ID and profile, and each selected feed's profile and date must match the independently supplied evidence. The operator attests to durability before writing. |
| `locally_witnessed` | In the independently authenticated Connect session, the operator issues a Personal API key, places it in the designated Keychain item, and identifies the owned activity and day from Connect. | Verify-only derives a candidate profile from that exact activity, checks every search owner, its detail identity, and each selected feed's profile and date. Enrollment requires explicit approval of that candidate. |

A locally witnessed enrollment establishes a single-owner association at the time of the
ceremony. Identifier reuse, changes across credentials and feed namespace changes remain
provider uncertainties. Each import repeats the comparisons against the approved identity.
The enrollment record preserves which evidence type was used. [Garmin Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api/)

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
   Replace each placeholder locally. Supply numeric IDs as **JSON integers**.
   Use `feeds: []` for activity-only verification, or select from `daily`, `sleep` and `hrv`
   for recovery. Choose an anchor with identity and date evidence for every selected feed.
   Set each confirmation to true only after obtaining the corresponding evidence.
4. From `backend/`, run `uv sync --frozen`. Inject `DATABASE_URL` from the local secret
   manager. Apply `uv run --frozen alembic upgrade head` through the administration role
   before rehearsal. Revision `b301` leaves retrieval and mapping provenance unknown for
   pre-existing B2 recovery rows. Its downgrade refuses to discard populated provenance.
   Revision `b302` stores enrollment evidence alongside the source account and guards it
   on downgrade. Existing Garmin accounts that predate this table continue to require the
   independent path. Use a read-only role with SELECT on `users`, `source_accounts` and
   `garmin_enrollments` for verify-only. Switch to the trusted local import role for explicit enrollment and observation writes.

```json
{
  "user_id": "<existing local owner UUID>",
  "source_account_id": "<reserved or verified source account UUID>",
  "evidence_type": "independent",
  "profile_id": null,
  "known_activity_id": null,
  "known_day": "YYYY-MM-DD",
  "feeds": ["daily", "sleep", "hrv"],
  "independent_profile_confirmed": false,
  "durability_confirmed": false
}
```

For the witnessed path, keep the UUIDs, known activity ID, day and feeds. Replace the
four independent-path fields (`evidence_type`, `profile_id`, `independent_profile_confirmed`,
`durability_confirmed`) with these fields. Set the two attestations to true after completing
the corresponding steps in Connect.

```json
{
  "evidence_type": "locally_witnessed",
  "key_issued_in_authenticated_session": false,
  "owned_activity_confirmed": false,
  "approved_pin": null
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
```

On first witnessed verification the private terminal displays an opaque `candidate_pin`
after all comparisons pass. It binds the candidate profile, local owner and account,
evidence type, anchor activity/day and selected feeds. To approve that exact association,
copy the receipt into `approved_pin` in the mode-0600 file and run `enroll`. Keep the
receipt out of reports, command arguments and logs. A missing or different receipt stops
enrollment. The independent path can proceed directly from successful verification.

```sh
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

All import commands repeat the anchor checks using the current credential. A rotated key
uses the original binding file. For witnessed enrollment, issue the replacement in the
intended signed-in session and repeat verify-only. Replacing the key still requires the
original approved profile, anchor and selected feeds to match. If that anchor is deleted,
falls off the bounded page or becomes unavailable, imports stop. A future anchor change
would need a separate operator-approved procedure verifying fresh independent activity
evidence against the existing profile. Editing the anchor or evidence type cannot replace
a witnessed pin. Failure leaves the account and existing observations intact.
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
  The mapping version, source path and retrieval time identify measurement provenance.
  Activity fields and splits retain their observed activity revision. The reference carries
  the last accepted retrieval and the detail field `metadataDTO.lastUpdateDate`, interpreted as
  UTC. Missing revision evidence stays unknown. Coordinates, routes, private names, raw
  response objects, tokens and unrelated health fields have no place in the projection.
- Missing scalar fields preserve prior values and their recorded provenance. A coarser
  start that agrees at its own precision retains the finer instant. A missing collection
  or a group with missing steps retains the previous children. An explicitly empty
  collection clears that collection. Eligible changed collections replace their snapshots.
  Sparse child fields that would erase known values on the same instruction or split hold
  the collection and report a partial result.
- Older revisions are skipped. An undated response following a dated activity is unresolved.
  A later response for the same revision can replace a scalar or split collection carried
  forward from an older revision. A contradiction with a value already observed at that
  revision rolls back the page. The separately fetched performed-workout response has no
  established revision. Complete step collections therefore follow serialized retrieval
  order, including when the activity revision stays the same. A stale enclosing activity
  still skips the entire snapshot. Older B3.1 step metadata may carry the enclosing
  activity timestamp, which has no ordering authority for steps. When both activity
  revisions are unknown, serialized retrieval order determines the latest observed values.
  Garmin supplies no deletion evidence through this workflow. Failed lookups, empty pages
  and absent measurements leave prior records in place.
- Daily rows retain their UUID for the account, provider date and metric. Positive evidence
  includes an explicit zero. Each observed row carries its source field, mapper version and
  UTC retrieval time. The provider-local date describes attribution. GMT bounds describe
  coverage for the accepted value. A changed measurement takes only the bounds in its reply.
  An unchanged measurement can retain earlier bounds when all supplied bounds agree.
  A different partial window keeps only its supplied bound. Daily aggregates have no
  asserted point observation time. Seven-day HRV has no asserted UTC bounds, and both HRV metrics retain
  `source_unit_unverified`. Expenditure remains a wearable estimate. Omitted metrics retain
  their prior value and retrieval time. [Units and DTO definitions](endurance-recovery.md)

For erasure, disconnect and revoke the source, then follow the existing owner-scoped local
procedure. Include performed steps and splits before endurance parents, references and
workouts. Erase daily recovery, intake and body-weight rows for the specified owner and source account before deleting that account. Erasing a source account cascades to
its enrollment evidence. Include the private binding, temporary
exports, backup expiry and reapplication of erasure after restore. Stop after the approved
page and day.

## Intake and body weight

B3.2 imports an exact provider-local day per invocation. The active account, original anchor
and selected recovery feeds must still verify. The Personal API key grants access to the
individual's own Connect data. The daily summary echoes the pinned profile. Food logs and
weight entries rely on the authenticated account scope and their own returned local dates.
Neither DTO documents a profile field. The importer keeps the same bearer from the anchor
checks through these target reads. Expiration or a 401 stops the operation so the next attempt
starts with verification. Account locking, the 40-request/three-minute budget, 2 MB JSON
limit, staging and commit-time active-account revalidation apply to both operations.
[Garmin Personal API FAQ](https://developer.garmin.com/gc-developer-program/personal/personal-faq) ·
[Official OpenAPI operations and DTOs](https://developer.garmin.com/gc-developer-program/personal/swagger-docs)

### Bounded provider evidence

| Source | Evidence from the approved samples | Interpretation |
| --- | --- | --- |
| Daily summary | One known food-logging day returned a positive decimal `consumedKilocalories`, a true `includesCalorieConsumedData`, and the expected profile and date. | Reported kcal. Garmin defines the flag as presence of intake data. Meal coverage and upstream writer remain unknown. |
| Food logs | The same day returned an integer `dailyNutritionContent.calories`. Its `mealDate` and total agreed with the daily summary. No profile echo or positive MyFitnessPal event marker was observed. | This field also reports kcal. Agreement on one day does not establish equivalent sources across history. Meal and catalog metadata cannot establish the sole writer of a daily aggregate. |
| Weight/all | One known weigh-in day returned one entry with a decimal `weight`, an integer 13-digit `timestampGMT` and the matching `calendarDate`. No stable record ID, profile echo or original scale/writer was identified. | The published DTO labels weight in kg and GMT time in epoch ms. A private comparison against the displayed weigh-in confirmed that **grams** reproduced the sampled weight. The wire value has no unit tag. |

The diagnostic used one single-day request per target feed. The unit cross-check reused the
approved weight day. Older history, multiple entries on a real day, empty/zero response conventions
and provider edit behavior remain unverified beyond these samples. Historical summary v2
was unnecessary for the approved scope. Local synthetic tests cover the corresponding
reconciliation cases. Garmin's published terms describe individual personal access and require
acceptance at key creation. The signed-in agreement governs use of that key. Its detailed
retention and onward-transfer clauses have not been independently verified. Keep personal
payloads in the local process. External AI processing and multi-user use require separate
review. [Personal API setup](https://developer.garmin.com/gc-developer-program/personal/personal-api/) ·
[Garmin Terms of Use](https://www.garmin.com/en-US/legal/terms-of-use/)

### Canonical observations

- **Daily intake.** The owner, provider, source account, local day and source field identify
  each reported total. A positively supplied amount updates that field in serialized retrieval
  order. Garmin supplies no comparable revision. Each row records kcal, UTC retrieval,
  mapping version, available source presence flag and completeness. Missing feeds, omitted or
  null amounts and empty food logs leave earlier evidence in place. With the same amount an
  omitted flag can retain earlier supporting evidence. A correction takes its own available
  flag. A false flag with a positive summary total is contradictory and stops the transaction.
- **Zero and completeness.** A zero with a true summary presence flag, or a zero food total
  with a logged food event, is an explicit zero. The importer skips an unsupported zero.
  A day with no qualifying observation is missing. Partial-day logging requires affirmative
  evidence of partial coverage. Both sampled DTOs leave completeness unknown. The canonical
  model can distinguish partial and athlete-confirmed completeness. The existing planner
  feedback does not attest to complete-intent food logging.
- **Analytical selection.** `select_daily_intake` reads only one owner's requested day across
  sources, returns the supporting observation IDs, and emits at most one reported value.
  Equal totals count once. Disagreement preserves the individual rows and yields a conflict
  with no selected value. This includes a corrected total that disagrees with an earlier
  retained sparse source. Partial coverage remains labeled. Future analysis must expose
  completeness alongside intake.
- **Weigh-ins.** Each source entry with an eligible identity retains its canonical kg, original
  numeric value, operator-verified interpretation (`g` or `kg`), documented provider unit
  (`kg`), field, mapping version, UTC retrieval and local date. The UTC instant uses integer
  epoch milliseconds with 1,000 µs resolution. The weight command requires an explicit
  source unit checked against Connect or the originating app for the requested data. Verify
  that the interpretation applies to the entries in the response. If units are mixed or
  unresolved, defer the import. The local-calendar `date` number is never used as UTC.
- **Weight identity.** Garmin's DTO has no established stable ID or original device. An exact,
  unique GMT instant within the account provides a limited replay key. Distinct instants
  remain distinct even if weight is identical. Same-instant entries within a response
  (including identical entries), dated-only values and changed mass, unit or day at a
  previously seen instant yield unresolved counts. Existing records survive. Moving an
  upstream instant can appear as a new observation. No source deletion or timestamp
  correction can be inferred. The canonical table also permits a source with an established
  upstream ID to represent a measurement with unknown time.
- **Privacy and retention.** The two tables contain typed measurements and provenance. Meal
  details, food names, images, macros, body composition, device guesses, credentials and
  raw DTOs are excluded. Upstream writer stays unknown for these Garmin fields. The local
  retention policy and encrypted backup, expiry and restore/erasure procedures apply to
  both tables. Scope deletion by trusted owner, provider and source account. Revision
  `b320` adds the two tables and rejects a downgrade while either contains observations.

### Operator rehearsal after review and merge

1. Confirm the existing private backup and owner, apply the reviewed migration, and run
   verify-only with the existing binding. Keep its approved anchor and selected feeds intact.
2. Use one previously approved food-logging day and one weigh-in day with a confirmed wire
   unit. Run from `backend/` with private local shell variables. For weights the verified
   unit refers to the API number, independently of the user's display preference.

   ```sh
   uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" intake --day "$food_day"
   uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" weight --day "$weight_day" --weight-unit "$wire_unit"
   ```

3. Repeat both commands with identical options. Compare stable row IDs, one analytical
   intake value or a labeled conflict, exact mass conversion, local dates, unknown writers,
   absence of duplicates/orphans, and the existing Hevy and Garmin fingerprints. Publish
   only counts and outcomes. B3.3 needs separately reviewed historical coverage, correction,
   ambiguous weight identity and incremental reconciliation policies.

## Historical synchronization

Run these commands locally against an already enrolled account. Each command takes inclusive provider-local dates and an explicit category list. The original anchor checks still run once per invocation. The published contract records the observed DTOs, sampling limits and request-cost assumptions. [Historical contract](garmin-historical-sync-contract.md)

| Operation | Which dates it processes |
| --- | --- |
| `backfill` | Outstanding category-days within the requested range. Repeat the same invocation to resume. Completed days are skipped. |
| `incremental` | Outstanding days plus a configurable recent overlap ending on the specified day. Seven days is an initial operating choice. Older corrections can fall outside it. |
| `repair` | Re-read every selected day, including completed days. Use this for older corrections or source comparisons. |

From `backend/`, use private shell variables for the binding, dates and approved weight segment. For an interruptible refresh, choose a UUID before starting and keep it with the local run notes. Use the same UUID and options to resume. A fresh incremental or repair pass needs a new UUID. Backfill has a stable default. A batch can commit progress even when the command exits nonzero.

```sh
garmin() { uv run --frozen python -m fitness_intelligence.adapters.garmin.cli --binding "$binding" "$@"; }
garmin backfill --start "$first" --end "$last" --categories activities running_steps sleep hrv
garmin backfill --start "$first" --end "$last" --categories expenditure resting_hr intake weight --weight-segment "$segment"
garmin incremental --start "$first" --end "$through" --overlap 7 --categories activities sleep hrv intake --pass-id "$refresh_id"
garmin repair --start "$older_first" --end "$older_last" --categories intake --pass-id "$repair_id"
```

The account advisory lock covers verification, staging and writes. Every transaction rechecks the active enrollment against the verified profile. One bearer serves identity checks and account-scoped requests for the entire invocation. The default limit is 40 HTTP attempts, including token exchange, verification, empty terminal pages and failed reads. Lower it with `--request-limit`. The existing three-minute deadline and 2 MB JSON limit apply. No invocation creates another client to continue past a limit. Size an authorized window to the available budget and repeat the command as needed.

### Outstanding dates and repair

An isolated unavailable day remains failed or partial. The importer proceeds to later eligible dates under the same bearer and budget. A day-specific 404, an undocumented 204, or a server error can leave such a gap. Two consecutive unavailable dates or windows pause that category group for the invocation. A transport error or a server error on a multi-day range pauses the group immediately. Each attempted gap gets one turn. A context, account, authorization, rate-limit, schema or unit-verification failure stops the invocation.

On resume, the importer processes new work before previously unavailable dates and retries those gaps in single days, least recently attempted first. Known weight-unit holds within the requested range take priority. Use a narrow `repair` to retry a particular gap immediately. Dates beyond a gap can complete independently. The private report's `completed` counts those successes, `completed_through` gives the contiguous frontier from the requested start, `resume` identifies the earliest outstanding date, and `gaps` lists the remaining inclusive intervals. A null frontier means the first date is still outstanding. A run that retained a gap exits nonzero even if it completed later dates.

### Endpoint and refresh policy

- **Activities and running steps.** Search parent activities in windows of up to seven days, ascending by provider-local start. A single-day window requests 99 rows per page. Multi-day windows request 10. Check the owner and date of every row. Within and across pages, start times may be equal but must never decrease. Each activity ID must occur only once per scan. A repeat from an earlier page records `duplicate activity ID across pages` and leaves that window outstanding for retry. Each scan must reach a short page, including an empty terminal read after an exact multiple of 99 or 10. Retrieve details per identity and optional workout steps for running activities. A successful detail transaction records a temporary receipt. On resume, retry partial days from offset zero. Reuse a receipt only for the same scoped identity, pass, listing signature and step option. Close coverage only after detail reconciliation and a second complete scan with identical activity IDs and allowlisted listing content for each ID. Tied activities may trade positions, including across a page boundary. Repeated IDs, decreasing starts, or a difference in identity or content between scans leave the window outstanding. Even agreeing offset scans can both omit the same activity or miss a concurrent edit, including a detail-only edit during interruption. They provide no point-in-time snapshot. A fresh repair reads details again. The original field-revision and child reconciliation rules still apply. Performed workout instructions provide no evidence that a target was achieved.
- **Daily summaries.** Request up to 28 days of v2 rows. Check each supplied profile and calendar date. Use integer Garmin-sourced expenditure and positive intake with their v2 field paths. Missing expenditure components can use the single-day summary. Resting HR uses the single-day field because v2 may substitute a daily minimum. A shared daily fallback serves all requested categories for that day. A missing, duplicate or differently sourced v2 day, an unsupported zero, a retained disagreement, or an explicit intake repair triggers the daily-summary and food-total comparison. An unavailable v2 route can fall back to validated daily reads. Each intake source keeps its own value. Overlapping equal totals select once. A conflict leaves the analytical total unavailable. Missing responses retain prior evidence. A positive total establishes neither complete logging nor the original writer.
- **Sleep and HRV.** Read sleep in windows of up to 28 days and HRV in windows of up to seven. Missing range days require a daily confirmation. A documented HRV 204 covers the requested range. Validate bounds actually supplied with sleep. Range HRV has unverified quantitative units and no exact overnight bounds. An equal value can retain a better-supported chart observation with its original provenance. A changed range value carries the bounds available with that new value. Oversized summary ranges can split within the same request budget.
- **Weight.** Read all entries in windows of up to 28 days under the same verified bearer. A dated decimal and an exact integer GMT epoch-millisecond instant are the sampled forms. A verified grams segment yields canonical kg by exact division by 1,000. The original value, interpreted g, documented kg, UTC instant, local date, resolution, retrieval time and segment fingerprint are retained. Separate instants remain distinct. A same-instant collision or changed value holds reconciliation. A disappearance plus a new instant can indicate a retime and holds the day's analytical series. Absence never deletes a weigh-in.

For intake, each validated total commits with its own field provenance before the next targeted request. `day_status(..., Category.INTAKE, day)["sources"]` shows outcomes for v2, daily summary and food logs. `observed` includes a supported explicit zero. `no_eligible` describes a successful response that supplied no eligible total, including an unsupported zero. `unavailable` records a failed source read. A missing key means the current receipt has no outcome for that source. Coverage from earlier versions may have no receipts.

A targeted comparison with an unavailable source stays partial and is retried on resume. Independently observed totals remain available when they agree and there is no open disagreement. Once a disagreement opens, analytical selection stays on hold until a completed comparison positively confirms every retained contributing field at the same total. A source that goes offline while the stored values happen to agree leaves the hold open. Logging completeness and original writer still require their own evidence.

### Private weight segment

Create an operator-owned, mode-0600 JSON file beside the private comparison evidence. Set `user_id` and `source_account_id` from the enrolled binding, `approved` to true, `unit` to `g`, and `start` and `end` to the approved inclusive local dates. Supply a `references` array with one object per independently compared Connect entry. Each object contains its ISO local `date` and `verified_grams` as a decimal string. Keep the underlying display, precision, conversion, available clock and time-zone qualification with those private references. Include the interior reference when available. Approval applies to Garmin weight/all on this account within the reference bracket.

The loader requires at least two distinct reference dates surrounding the approved interval. The private file's SHA-256 fingerprint identifies its interpretation policy. Keep a copy of each approved version under the existing retention policy. The consistency screen flags a changed numeric form, unexpected source/device/type marker, unsupported time encoding, or a mass outside one-half the smallest to twice the largest reference. This broad screen catches gross scale changes and can miss subtler ones. It cannot establish units. A unit exception holds all weight writes for that day and pauses the batch. Empty retries leave the hold open. Obtain a targeted independent comparison and narrow or split the approved segment before continuing.

### Coverage, issues and erasure

Migration `b330` adds `garmin_history_coverage`, `garmin_history_issues` and nullable weight `verification_scope`. Coverage is keyed by owner, provider, account, category and local day. An absent row means historical acquisition has never been recorded, including days with earlier bounded imports. Empty means a completed acquisition yielded no eligible input. Observed, failed and partial are distinct. The last successful timestamp and count survive a failed refresh. Reconciliation is tracked separately. A day can have returned entries and still have open issues. Empty intake coverage provides no evidence of zero consumption or adherence.

For weight, `eligible_count` counts distinct instants whose canonical observation was accepted (created or positively matched) in the last **completed** acquisition of that day. It excludes collisions, missing instants, ambiguous corrections and unit exceptions. A response with only disputed weigh-ins can therefore be observed with count zero. A partial or failed attempt retains the previous successful count and timestamp, both unknown before the first success. For example, a day returning three entries with one accepted instant and a two-entry collision has count one. Its open issue withholds the entire day from analytical use. `select_weight_day` supplies that current analytical status. Returned entries, accepted observations and available analytical measurements can all have different counts.

The private CLI summary includes bounds, pass UUID, per-category completed and remaining days, earliest outstanding date, open issues, fixed endpoint attempt counts, and committed reconciliation counts. Keep dates in local output. Publish only aggregate counts and comparison outcomes. A successful acquisition can require issue review even when remaining days is zero.

Use `day_status` for internal category/day coverage and issue reasons. `select_weight_day` returns retained observation identities and withholds masses from analytical use while any scoped weight issue is open. `select_daily_intake` continues to expose disagreement across retained source totals. Repair can close a same-instant weight issue when the provider positively supplies a unique, compatible measurement. A retime can close when all retained instants reappear together. An intake issue can close when positive evidence reconciles the retained sources. A dated-only measurement, an unidentifiable unit exception, or a contradictory same-revision activity can need explicit investigation. Keep these issues open when subsequent evidence is insufficient. An empty response cannot clear them.

Protect coverage, partial activity receipts and issue keys as health metadata. They contain dates, scoped identifiers, fixed reasons and evidence digests. Historical state stores no raw responses, meal details, private titles, body-composition data or GPS. Include both new tables in the existing encrypted backups and retention policy. For authorized erasure, remove their rows by trusted owner, provider and source account before removing the source account. Include private segment files, comparison notes, temporary exports, backup expiry and re-erasure after restore. Downgrade to `b320` refuses to discard populated historical tables or weight verification provenance.

### Proposed B3.3C controlled rehearsal

1. Obtain approval for one representative segment, categories and request budget. Verify the encrypted backup and restore procedure. Capture counts, identities and content fingerprints for existing Hevy, Garmin and planning records.
2. Apply reviewed migration `b330`. Run verify-only against the existing enrollment. Confirm the source and independently bracket the weight interpretation for this segment.
3. Run the approved backfill with a small request limit. Stop after a committed unit and inspect partial coverage, retained identities, attempts and the resume position.
4. Resume with the same bounds and options. Replay the completed segment with a fresh repair pass. Compare corrections, unchanged observations, open issues and stable identities.
5. Audit duplicate keys, orphan references, attribution, timestamp precision, unit scope, intake selection, privacy and the pre-existing fingerprints. Retain only sanitized rehearsal results. Decide on any wider scope after the audit.
