# B1 · Run the Garmin verification locally

This command reads a small sample of your own account and prints a JSON capability report
to your terminal. Only you run the personal-data probe. No live result has been recorded.
The [design and availability matrix](garmin-integration-design.md) describe what Garmin documents.

## Set up the key on macOS

1. Open **Keychain Access**. Select your **login** keychain. Choose **File → New Password Item**.
2. Enter **fitness-intelligence.garmin** as the keychain item name, **personal** as the
   account name and your Garmin Personal API key as the password. Select **Add**. Keep the
   key out of shell commands, environment files, chat and the repository.
3. To update an existing item, open it in Keychain Access, select **Show password**,
   authenticate if prompted, replace the entire password, and select **Save Changes**.
   The command uses the system Keychain helper with captured output. A locked keychain
   may ask you to allow access. Keychain access has a 30-second timeout.

Use the graphical password field for long API keys. The interactive
`security add-generic-password … -w` prompt uses macOS `getpass(3)`, which accepts only
the first 128 bytes on the tested system. Both confirmation prompts can agree on the same
truncated value. Both curl and Python will then read that value from Keychain.
[Apple's password prompt implementation](https://github.com/apple-oss-distributions/Security/blob/main/SecurityTool/macOS/keychain_add.c)

If a key entered through that prompt gets a 401, keep the current Garmin key and replace
the password in **Keychain Access** with the original saved at issuance. To check the repair
offline from `backend/`, run this block first. At the prompt, copy the original key from
your password manager and press Return in Terminal. The check prints only a comparison result.

```sh
uv run --no-sync python -c '
from secrets import compare_digest
from subprocess import run
from fitness_intelligence.adapters.garmin.verify import keychain_key

input("Copy the original Garmin key now, then press Return here: ")
original = run(["/usr/bin/pbpaste"], capture_output=True, check=True).stdout
stored = keychain_key().encode("ascii")
if not original:
    print("Clipboard empty.")
elif compare_digest(original, stored):
    print("Exact match.")
elif len(stored) == 128 and original.startswith(stored):
    print("Confirmed: Keychain contains only the first 128 bytes.")
else:
    print("Different values.")
'
```

## Run

From the feature worktree on your Mac, with Python 3.12+ and uv installed:

```sh
cd /private/tmp/fitness-intelligence-b1/backend
uv sync --locked
uv run --no-sync python -m fitness_intelligence.adapters.garmin.verify
```

The default anchors are yesterday on your Mac and 365 days earlier. Each anchor samples
one day of daily metrics and the seven local calendar days ending on that anchor for activity
search. For a more informative test, choose two dates when you know a wearable was synced,
a meal was logged or a weigh-in occurred. Substitute your own dates in this example:

```sh
uv run --no-sync python -m fitness_intelligence.adapters.garmin.verify \
  --recent 2026-11-20 --older 2025-11-20
```

Use dates at least seven days apart. Choose a week containing a run, squash match or ultimate
game if testing sport coverage. Keep the report local. It contains category counts and
availability. The command suppresses HTTP logging and needs no database configuration.

## What is bounded

- One current activity-type catalog and one current HR-zone configuration.
- Per window, at most two activity pages of three rows. At most one selected activity
  (prefer a sampled run) gets a detail read, a performed-workout read and an original-file
  GET that closes after checking the headers. No archive extraction or FIT decoding occurs.
- Seven single-day queries per anchor cover daily summary, HRV, sleep, heart rate,
  Body Battery, nutrition and weight. Goals, food media and generated default zones are
  disabled. Body Battery requests one interval.
- At most 27 HTTP requests under normal authentication, including token exchange, and 40
  including renewals or replay. Connect timeout is five seconds, read timeout ten seconds.
  A three-minute budget is checked before requests and while consuming response chunks.
  The cap is 2,000,000 bytes per JSON response and 16,384 bytes for token exchange.
  The token lives only in process memory. Redirects, environment proxies and compressed
  responses are disabled. A transport error or throttle stops the run.

## Read the report

| Report entry | Interpretation |
| --- | --- |
| `current` / `recent` / `older` | Current configuration, then the two independent samples. If an activity was unavailable, its dependent sections are omitted. |
| `status: complete` / exit 0 | The requested sampling sequence finished. Inspect each category to determine actual coverage. |
| `partial` / exit 1 | Inspect the endpoint status or top-level `stopped`. A failed request gives no coverage evidence. |
| `ok`, `records` | Successful response shape and count of top-level records. One daily envelope may contain only metadata. Zero rows or `no_content` describes only this sample. |
| `fields` | Each allowlisted path has counts of `present`, numeric `zero`, `null`, `missing`, `empty`, booleans or `invalid`. An empty count map has no applicable rows or children. Numeric zero means Garmin returned zero. Check the source data flag before interpreting it as measured intake. |
| `reading_states` | Counts of heart-rate or Body Battery values in the column identified by Garmin’s descriptors. `unresolved_column` means rows exist but the measurement column could not be identified. |
| `record_dates` | `matched` counts daily records labeled with the requested date. `unknown` means the response supplied no usable date evidence. `date_mismatch` invalidates historical attribution. |
| `sport_keys_in_sample` / `selected_sport_keys` | Fixed key matches in the catalog, the sampled history, or the selected activity. Unmatched names and private activity titles are never printed. |
| `archive_headers_received` / `fit_format_declared` | A compatible original-file response and a FIT declaration in detail metadata are separate checks. The actual file remains unexamined. |
| `myfitnesspal_markers` / `undocumented_source_fields` | Exact allowlisted marker counts only. Inspect the logged-event marker separately from food catalog source. The weight DTO does not promise a source label. An unmatched alias leaves attribution open. |

For `keychain_unavailable`, check the item name, account, unlocked login keychain and permission
prompt. If the token exchange fails, inspect the sanitized `token_http_status`:
401 indicates authentication was rejected; check the key's active status in Garmin Connect
and the password stored in the Keychain item. A 403 indicates access was refused; confirm the
account is enabled for the global Personal API server. For 5xx, wait and retry later.
A 2xx with `invalid_token_response` means the reply did not provide a usable token.
For other statuses, the integer and the `stopped` category are sufficient for troubleshooting.
For `rate_limited`, stop and wait for Garmin access to resume. A 403, 404, 5xx,
unrecognized shape or size cap leaves that check unresolved. Avoid repeated probing to
determine a limit.

## Decide what reached Garmin

For each anchor, privately compare with a known source day. Check Garmin Connect's own UI
against MyFitnessPal and RENPHO for the actual values and units. The report intentionally
shows only field states and counts.

- **Intake.** Check `daily.includesCalorieConsumedData` alongside `consumedKilocalories`
  and `food.dailyNutritionContent`. A calorie goal, expenditure or a default zero cannot
  establish a logged meal.
- **Meals and macros.** Check for logged foods and consumed meal calories, protein, carbs
  and fat. Meal definitions or daily totals alone leave meal coverage unresolved. Check
  original event source separately from a food item's catalog source.
- **Weight.** Check for a dated measurement on a known weigh-in day. Compare the displayed
  weight in kg and measurement time in the two apps. A matching value supports transfer
  on that day. Mark RENPHO attribution unknown unless there is independent origin evidence.
- **History.** Record a private conclusion per category and per window as observed, empty,
  unknown date, failed, or outside the published schema. Treat a nonempty field in a matched
  record as sample evidence. Two samples cannot establish continuity, an earliest date or
  complete transfer. Use the [B2/B3 decision criteria](garmin-integration-design.md#b2-b3-and-the-health-connect-decision)
  before retiring any Health Connect use case.
