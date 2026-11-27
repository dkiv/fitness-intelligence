# G1D · Google Calendar availability and workout reservations

FI uses its owner-bound plan revision, occurrence, IANA time zone and full reserved duration to schedule time. The offline rehearsal uses real FI proposal and approval transactions in disposable PostgreSQL. Two synthetic Google calendars run behind an HTTP test double. No Google account, credentials or network transport participate.

## What the rehearsal demonstrated

| Operation | Result in America/Toronto |
| --- | --- |
| Review before approval | The proposed Saturday, January 9, 2027 run at 09:00 overlapped a 09:05–09:15 busy interval. The preview returned the interval and made zero event writes. |
| Approve a free slot | The planner generated a new proposal for Saturday at 10:00. After approval, one reservation existed. Reading the event by its calendar ID and event ID returned Saturday 10:00–10:25, UTC−05:00, zone America/Toronto. |
| Approve a revision | The athlete's synthetic decision moved the same logical slot to Sunday, January 10 at 09:00. Before approval the update was refused. After approval a conditional patch and an independent GET returned Sunday 09:00–09:25 in the same zone, under the original Google event ID. Exactly one event remained. |
| Retry and reconciliation | The double committed the initial insert and dropped its response. Looking up the same ID recovered the reservation. Replaying the approved move read the event again. The complete sequence issued one insert and one patch. |
| G1B handoff | A second test read the sealed familiar-week running occurrence. Its event ran from January 6 at 18:00 to 18:34. That included 31 minutes of running prescription and three minutes of preparation. |

The rehearsal checks provider readback of the ID, start and end instants, both zone names, the generic title, FI revision marker and ETag. The receipt computes elapsed duration from the readback. The Google event ID is derived from the FI cycle, logical occurrence and destination. It stays stable across approved revisions. Its identity is scoped to the Google calendar. Garmin definition IDs, Garmin schedule IDs and device receipts play no part in this workflow. [Implementation](../backend/src/fitness_intelligence/handoff/google_calendar.py) · [Executable rehearsal](../backend/tests/test_google_calendar.py)

The approval check reads the current plan head through owner-scoped commands. The pre-write free/busy check covers the selected availability calendar and the destination for the entire proposed interval. A busy destination prompts a bounded lookup of overlapping IDs and transparency so an existing reservation can move without masking another event in the same slot. Incomplete availability blocks the write. A changed ETag or missing prior event requires reconciliation. Free/busy and the write are separate requests, so concurrent external bookings can still race. The double establishes FI behavior. Google acceptance, granted permissions and live readback remain open. [Google free/busy](https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query) · [Event insert](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert) · [Event patch](https://developers.google.com/workspace/calendar/api/v3/reference/events/patch) · [Event get](https://developers.google.com/workspace/calendar/api/v3/reference/events/get)

Run from `backend` with `TEST_DATABASE_URL` pointing to a disposable PostgreSQL database.

```sh
uv run pytest -q tests/test_google_calendar.py
```

## Proposed live rehearsal for separate approval

Use a designated test account, one availability calendar containing an operator-prepared synthetic busy interval, and one dedicated empty destination calendar. Confirm the account, calendars, approved access mechanism and exact future windows privately before access. The proposed times below use America/Toronto.

1. Read free/busy only for the January 9, 2027 09:00–09:25, January 9 10:00–10:25 and January 10 09:00–09:25 windows. Confirm the prepared conflict in the first window and availability in the others. Check the destination for existing test entries.
2. With approval for the free Saturday slot and named destination, create one private timed event titled **FI synthetic workout reservation**, with no invitees or reminders. Read back the Google calendar/event ID, local date, start, end, zone and 25-minute duration.
3. With approval of the Sunday revision, update that event by its verified ID and ETag. Read it back and check both windows for one destination event at the intended time. Stop on a changed precondition, an ambiguous write or conflicting readback.
4. Retain only the synthetic times and sanitized outcome in Git. Keep the provider receipt private. Offer cleanup of that one event under separate deletion approval and verify absence if authorized.

This proposal requests no access to personal event titles, primary calendars, Garmin or workout history. The operator can select different future dates before authorizing the rehearsal.
