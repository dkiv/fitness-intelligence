# Fitness Intelligence project state

**Checkpoint · 2026-11-27.** Verified through [main at `f89415f`](https://github.com/dkiv/fitness-intelligence/commit/f89415f50f6f077bfdd9e1d55f528d4292064915). B’s reviewed single-day pagination fix merged and G confirmed the revised workout on the watch. **E4.2C.2 passed independent review in [#54](https://github.com/dkiv/fitness-intelligence/pull/54). Synthetic E4.3 core adaptation is next after merge.** D has prepared the D1V approval form. In parallel, arrange independent review of the first practical coaching actions. No personal prescription has reached operational approval.

Use this file to resume coordination. The [roadmap](../roadmap.md) owns the A–J objectives and long-term acceptance criteria. The linked contracts own field definitions, policies and test cases.

## Integration and review

These are the commits relevant to the current integration boundary. Review here means the orchestrator inspected the indicated changes. GitHub records the merge separately.

| Milestone | Reviewed head | GitHub disposition at checkpoint |
| --- | --- | --- |
| D1D · training exposure | [#40 · `fc1d0e9`](https://github.com/dkiv/fitness-intelligence/pull/40) | Merged at `33a8831`. Verified empty-day rules distinguish acquisition timing from calendar closure. |
| E4.2B · scoped confirmations | [#41 · `1b2e538`](https://github.com/dkiv/fitness-intelligence/pull/41) | Merged at `b691aa7`. Ambiguous prescribed ordinals keep the source evidence and lose the effective link. |
| D1E · comparable performance | [#46 · `75aaaa1`](https://github.com/dkiv/fitness-intelligence/pull/46) | Merged at `70bf942`. Positive running weeks without immutable enumeration membership supply observed exposure only. |
| D1F · integrated report | [#48 · `9f267f3`](https://github.com/dkiv/fitness-intelligence/pull/48) | Merged at `8b172c2`. Reviewed rendering distinguishes zero observed pairs from outings withheld from assessment. |
| E4.2C.1 · planning evidence | [#47 · `a5de018` correction, `8b7c720` integration](https://github.com/dkiv/fitness-intelligence/pull/47) | Merged at `14c0740`. Final head and merge both match independently tested tree `f8f9b82c250d4f8c19c4c81f52a035cfb5764b25`. All 795 synthetic PostgreSQL tests passed. Ruff and Alembic round trip through `e422` passed. |
| G1C.2B · Garmin delivery decision | [#45 · `e858a7b`](https://github.com/dkiv/fitness-intelligence/pull/45) | Merged at `5a23b82`. The subsequent Connect and watch readback merged in [#50](https://github.com/dkiv/fitness-intelligence/pull/50) at `f89415f` with reviewed head `787da2b`. |
| E4.2C.2 · frozen decision inputs | [#54 · `a930aa8`](https://github.com/dkiv/fitness-intelligence/pull/54) | Open, recommended for merge. Independent review passed all 807 backend tests on disposable PostgreSQL 17, including both writer races. An extra check showed that a second same-provider binding staled automatic selection while the explicitly selected account still approved. Ruff and the Alembic round trip through `e422` passed with no drift. |
| G1D · calendar rehearsal | [#53 · `ab0cc9a`](https://github.com/dkiv/fitness-intelligence/pull/53) | Corrections requested. Both supplied PostgreSQL tests passed. Independent synthetic checks produced an event after rolling back approval and a new receipt for an externally changed ETag on same-revision replay. Recheck both cases before merge. Live calendar access requires separate approval. |
| B3.3D.2 · single-day pagination | [#52 · `e1012a6`](https://github.com/dkiv/fitness-intelligence/pull/52) | Merged at `7ce8362` with the reviewed head as second parent. Independent checks passed all 47 Garmin history tests on disposable PostgreSQL 17, Ruff lint and formatting, and the whitespace check. B reported 797 backend tests passed. |

## Workstream matrix

| Stream | What the next orchestrator can rely on | Next activity or dependency |
| --- | --- | --- |
| A · Strength | M0–M3A merged. Historical Hevy import, repeat reconciliation and local integrity audit completed. Current freshness and unattended edit/delete synchronization remain unverified. | Use supported comparable sets and field-level confirmation for planning. [Strength analytics](../strength-analytics.md) |
| B · Endurance and recovery | B1–B3.3B merged. B3.3C verified bounded sync and replay. B3.3D.2 reproduced cross-page duplication on one partial day. Retained activities support individual observations. Counts and workload on partial days are lower bounds. | Seek separate approval to validate one blocked day. D1V scope approval and E4.2C.2 can proceed in parallel. [Sync contract](../garmin-historical-sync-contract.md) |
| C · Intake and weight | B3.2 and D1B/C support reported daily intake and individually verified weigh-ins. Daily totals reconcile across sources. Food-logging completeness, original writer and scale attribution require separate evidence. | Use available coverage for D1V. Consider Health Connect or meal-level data only for a decision the existing observations cannot support. [Analytics contract](../longitudinal-analytics.md) |
| D · Longitudinal analytics | D1A–F merged. The integrated report exposes coverage, comparable tasks, individual references and descriptive strength/run proximity with evidence lookups. | The D1V form is prepared. Operator approval of the private read-only scope, recipient and retention is pending. [D1V procedure](../longitudinal-analytics.md#d1v-proposal-for-separate-operator-authorization) |
| E · Planning | E1–E3 and E4.0 through E4.2C.1 merged. The generalized planner accepts supplied block intent and familiar templates. Its evidence reader reconciles current observations, manual actuals and scoped confirmations for the synthetic principal. | After #54 merges, E4.3 uses frozen decision inputs for bounded adaptation. E4.4 adds optional operators and E4.5 evaluates practical choices. [Planner design](../generalized-hybrid-planner-design.md) |
| F · Adaptive coaching | E3 demonstrates the first synthetic approval, execution and adaptive review cycle. E4 supplies the generalized workflow. | Close F through E4, D and J. Demonstrate the real two-week approval and outcome loop below. [Adaptive cycle](../adaptive-coaching-cycle.md) |
| G · Delivery | G1A/B and G1C.1/.1B/.2A merged. One synthetic Hevy routine completed save, readback, update and cleanup. Hevy MCP is preferred for interactive delivery. REST owns historical ingestion. | Garmin documentation #50 merged. Correct the approval and replay behavior in #53, then re-review the synthetic rehearsal. Garmin structured publishing has a separate access and lifecycle dependency. [Workout handoff](../workout-handoff.md) |
| H · Personal evaluation | D1E supplies task comparisons and individual reference windows. E records decisions and outcomes. | For the pilot, compare adherence, coverage, feedback and comparable performance with a familiar hold. Predictive modeling and logged maintenance intake estimation can follow. [Evaluation design](../coaching-evaluation-design.md) |
| I · Privacy and release | Local owner/account isolation, synthetic fixtures, private storage and scoped operations apply to personal use. | Maintain those controls for the pilot. Public release separately requires authentication, cross-tenant denial tests, provider permissions, credential lifecycle, export/deletion and monitoring. [Architecture](../architecture.md) |
| J · Evidence and methods | J1 catalog implemented. Packets 001–010 closed preliminary collection. J3I.1 integrated M01/M02/M03 into candidate `J3I-HYBRID-0.1`. The J1 screening release has five pending claims and one pending method. | Select qualified independent reviewers for the pilot methods and their actual empirical dependencies. No Packet 011 is scheduled. [Catalog](../scientific-evidence-catalog.md) · [Curation and dispositions](../research/curation/README.md) |

## Session ownership and pending decisions

Use the existing Codex sessions below. Titles are resumption aids. GitHub and the checked-in contracts remain usable without access to chat history.

| Codex chat | Last known handoff |
| --- | --- |
| **Reconstruct Fitness Intelligence state** | Primary orchestration and independent implementation review. Earlier orchestration decisions are in **Integrate Training Data**. |
| **E. Design generalized hybrid planner** | #47 integrated. C.2 passed independent review at `a930aa8`. Verify #54 merges at the reviewed head before branching for E4.3. |
| **D. Design unified longitudinal analytics** | #48 integrated. The six-week D1V form is prepared. Before sign-off, make the owner-wide account metadata lookup explicit (account ID, provider and status for binding checks). Health observations remain limited to the approved sources, owner-day intake and period. Personal validation is pending. |
| **B. Implement Garmin bounded ingestion** | B3.3D.2 complete. #52 merged at its reviewed head. Prepare the scope for one blocked-day live validation and obtain operator approval. See the acceptance criteria below. |
| **G. Investigate workout publishing** | #45 and #50 merged. Use the existing G chat to correct #53. Preserve same-event creation, move and recovery after a lost acknowledgement. |

**Garmin ingestion decision.** On the diagnosed day, each size-10 scan repeated an identity across pages. Two size-99 scans returned the same distinct identities and listing signatures. In #52 single-day enumeration requests 99 rows, multi-day windows retain 10, and cross-page duplication leaves coverage outstanding. Both scans retain duplicate rejection, nondecreasing start times, identity and signature comparison, and the terminal read after a full page. [Reviewed enumerator](https://github.com/dkiv/fitness-intelligence/blob/e1012a65fa40428bb817a9f5b63aed23535a1469/backend/src/fitness_intelligence/adapters/garmin/history_activities.py)

Seek separate approval for one blocked day. Require matching scans, preservation of existing workout identities, and complete coverage for both activities and running instructions. Broader repair of recent partial days is a later operator decision. The private audit reported no duplicate canonical identities, orphan references or open activity reconciliation issues. Older history and unverified weight dates can wait. D1V can use eligible observations within its approved scope.

**Garmin delivery evidence.** The manual worksheet rehearsal stopped at preparation. Later, in a separate personal Connect **web-interface** rehearsal, the athlete confirmed the original 17-minute workout's step order and effort cue on the Forerunner 955. The G session reported an in-place edit to 18 minutes and a single Connect calendar occurrence. The athlete confirmed all eight revised steps on the watch, including the added recovery. PR #50 records the device readback. The athlete prefers target pace ranges assuming flat ground for future coached runs, when supported. Automatic approved structured-workout delivery remains the goal. The Personal API supports the acquisition path. An authorized publishing API and its lifecycle still need verification.

**Coaching authority.** Engineering review establishes software behavior. Independent scientific review accepts particular empirical claims and their applicability. Independent practical review accepts a versioned method, bounds and fallback. Operational release enables specific reviewed actions for a defined scope. The athlete then approves the exact block and each new or changed week. A judgment-only action needs an independently accepted basis and visible evidence gaps. The scientific chats **Research review fitness intelligence** and **Scientific Coaching Method** supplied candidate material archived in the [research library](../research/README.md).

## Dependencies and first personal cycle

```text
D1F (merged) ──► approved D1V scope ──► private validation of selected observations
E4.2C.1 (merged) ──► C.2 frozen inputs and writer coordination (#54 reviewed, merge pending) ──► E4.3 core adaptation
J3 candidate ──► independent practical and applicable scientific review ──► scoped rule release
Validated inputs + conformant, released rules + athlete context ──► first approved block and week
Approved week ──► execution and feedback ──► next-week review and athlete decision ──► follow-up
```

**Engineering priority.** After #54 merges, implement synthetic E4.3 against the [planner design](../generalized-hybrid-planner-design.md). Use the sealed evidence to choose a familiar hold, defer, re-entry or a bounded rep, load or easy-duration change. Preserve protected tasks and the shared review anchor. Repeat proposals against the same evidence must preserve the allowance. Keep the [owner-lock protocol](../planning-evidence.md#writer-inventory-and-e42c2) when adding decision-relevant writers. D1V scope approval, focused J review, B validation planning and G scheduling can proceed alongside this work.

**Personal MVP acceptance**

1. The athlete confirms objectives, protected outcomes, constraints, familiar training and actual availability. The coach can explain which recent observations qualify and ask for missing information.
2. The athlete reviews a feasible multiweek block and an exact seven-day strength/running prescription. An infeasible week exposes the conflict. Approval preserves the precise version, applicable rules, reasoning and supporting inputs.
3. The approved week is usable in the athlete's existing workflow. Publication requires approval for the destination and exact version. Calendar reservation and structured device delivery have separate receipts. Manual Garmin transcription is optional for pilot acceptance.
4. Actual training and feedback are attributed to the in-force prescription. Partial, missed, unplanned and unknown work remain distinguishable. The athlete can inspect coverage and correct a specific reported field.
5. The athlete reviews and approves or declines an exact next-week change or familiar hold. Both prescriptions and the decision remain traceable. Subsequent adherence, comparable outcomes and practical usefulness are recorded with their limitations.

## Checkpoint maintenance and handoff

The primary orchestrator refreshes this page when a merge changes the critical path, independent review changes a disposition, a live rehearsal establishes a new capability, or an operator decision changes scope. At each such checkpoint, verify remote main, all open PRs, relevant merged heads and the owning session's latest result. Replace superseded status in place and link the evidence. Keep personal measurements, identifiers, credentials and private operating instructions outside Git. A recorded past approval grants no new live access.

**Starter prompt**

> Continue as the primary Fitness Intelligence project orchestrator. Read [the repository](https://github.com/dkiv/fitness-intelligence), this project-state checkpoint, the [roadmap](../roadmap.md) and [AGENTS.md](../../AGENTS.md). Reconcile the checkpoint against current main and every open PR. Recover relevant prior orchestration decisions where available. Continue coordinating implementation, independent review, scientific methodology and the critical path toward personal operational coaching. Resume existing work and verify specific authorization before live operations.
