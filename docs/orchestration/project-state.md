# Fitness Intelligence project state

**Checkpoint · 2026-11-26.** Verified through [main at `14c0740`](https://github.com/dkiv/fitness-intelligence/commit/14c07400ac0ad4f049cdde53b7cc3ea64a7d6cd7), after D1F and E4.2C.1 integrated. **E4.2C.2 is the next engineering milestone.** In parallel, prepare D1V and arrange independent review of the first practical coaching actions. No personal prescription has reached operational approval.

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
| G1C.2B · Garmin delivery decision | [#45 · `e858a7b`](https://github.com/dkiv/fitness-intelligence/pull/45) | Only open implementation-workstream PR at the checkpoint. Previously recommended for merge as the record of the stopped manual rehearsal. Reconcile the later web-interface rehearsal below before using its verification statements as current. |

## Workstream matrix

| Stream | What the next orchestrator can rely on | Next activity or dependency |
| --- | --- | --- |
| A · Strength | M0–M3A merged. Historical Hevy import, repeat reconciliation and local integrity audit completed. Current freshness and unattended edit/delete synchronization remain unverified. | Use supported comparable sets and field-level confirmation for planning. [Strength analytics](../strength-analytics.md) |
| B · Endurance and recovery | B1–B3.3B merged. Bounded live runs exercised import, interruption, resume, repair and incremental refresh. Historical activity coverage remains partial after the tied-start fix and a rate-limit stop. | B3.3D.2 diagnostic belongs to the existing B session. Await its sanitized result before proposing a repair or broader acquisition. [Sync contract](../garmin-historical-sync-contract.md) |
| C · Intake and weight | B3.2 and D1B/C support reported daily intake and individually verified weigh-ins. Daily totals reconcile across sources. Food-logging completeness, original writer and scale attribution require separate evidence. | Use available coverage for D1V. Consider Health Connect or meal-level data only for a decision the existing observations cannot support. [Analytics contract](../longitudinal-analytics.md) |
| D · Longitudinal analytics | D1A–F merged. The integrated report exposes coverage, comparable tasks, individual references and descriptive strength/run proximity with evidence lookups. | D1V needs exact operator approval for a private read-only interval, accounts, calendars, mappings, recipient and retention. [D1V procedure](../longitudinal-analytics.md#d1v-proposal-for-separate-operator-authorization) |
| E · Planning | E1–E3 and E4.0 through E4.2C.1 merged. The generalized planner accepts supplied block intent and familiar templates. Its evidence reader reconciles current observations, manual actuals and scoped confirmations for the synthetic principal. | C.2 seals decision inputs and coordinates writers at approval. E4.3 adds bounded adaptation. E4.4 adds optional operators and E4.5 evaluates practical choices. [Planner design](../generalized-hybrid-planner-design.md) |
| F · Adaptive coaching | E3 demonstrates the first synthetic approval, execution and adaptive review cycle. E4 supplies the generalized workflow. | Close F through E4, D and J. Demonstrate the real two-week approval and outcome loop below. [Adaptive cycle](../adaptive-coaching-cycle.md) |
| G · Delivery | G1A/B and G1C.1/.1B/.2A merged. One synthetic Hevy routine completed save, readback, update and cleanup. Hevy MCP is preferred for interactive delivery. REST owns historical ingestion. | Reconcile #45, then pursue G1D availability input and approved reservations in Google Calendar. Garmin structured publishing has a separate access and lifecycle dependency. [Workout handoff](../workout-handoff.md) |
| H · Personal evaluation | D1E supplies task comparisons and individual reference windows. E records decisions and outcomes. | For the pilot, compare adherence, coverage, feedback and comparable performance with a familiar hold. Predictive modeling and logged maintenance intake estimation can follow. [Evaluation design](../coaching-evaluation-design.md) |
| I · Privacy and release | Local owner/account isolation, synthetic fixtures, private storage and scoped operations apply to personal use. | Maintain those controls for the pilot. Public release separately requires authentication, cross-tenant denial tests, provider permissions, credential lifecycle, export/deletion and monitoring. [Architecture](../architecture.md) |
| J · Evidence and methods | J1 catalog implemented. Packets 001–010 closed preliminary collection. J3I.1 integrated M01/M02/M03 into candidate `J3I-HYBRID-0.1`. The J1 screening release has five pending claims and one pending method. | Select qualified independent reviewers for the pilot methods and their actual empirical dependencies. No Packet 011 is scheduled. [Catalog](../scientific-evidence-catalog.md) · [Curation and dispositions](../research/curation/README.md) |

## Session ownership and pending decisions

Use the existing Codex sessions below. Titles are resumption aids. GitHub and the checked-in contracts remain usable without access to chat history.

| Codex chat | Last known handoff |
| --- | --- |
| **Reconstruct Fitness Intelligence state** | Primary orchestration and independent implementation review. Earlier orchestration decisions are in **Integrate Training Data**. |
| **E. Design generalized hybrid planner** | #47 integrated. Next PR is C.2, starting from merged main. |
| **D. Design unified longitudinal analytics** | #48 integrated. Prepare the six-week D1V scope for the operator. Personal validation results are outstanding. |
| **B. Implement Garmin bounded ingestion** | The session reported a one-time runner for the bounded pagination diagnostic. Check its existing result and scope before taking action. A runner being scheduled establishes no diagnostic outcome. |
| **G. Investigate workout publishing** | Reconcile the browser rehearsal and outstanding watch check. G1D can proceed independently of Garmin Training API access. |

**Garmin delivery evidence.** The manual worksheet rehearsal stopped at preparation. Later, in a separate personal Connect **web-interface** rehearsal, the athlete confirmed the original 17-minute workout's step order and effort cue on the Forerunner 955. The G session reported an in-place edit to 18 minutes and a single Connect calendar occurrence. Propagation of the added final recovery to the watch remains unverified. The athlete prefers target pace ranges assuming flat ground for future coached runs, when supported. Automatic approved structured-workout delivery remains the goal. The Personal API supports the acquisition path. An authorized publishing API and its lifecycle still need verification.

**Coaching authority.** Engineering review establishes software behavior. Independent scientific review accepts particular empirical claims and their applicability. Independent practical review accepts a versioned method, bounds and fallback. Operational release enables specific reviewed actions for a defined scope. The athlete then approves the exact block and each new or changed week. A judgment-only action needs an independently accepted basis and visible evidence gaps. The scientific chats **Research review fitness intelligence** and **Scientific Coaching Method** supplied candidate material archived in the [research library](../research/README.md).

## Dependencies and first personal cycle

```text
D1F (merged) ──► approved D1V scope ──► private validation of selected observations
E4.2C.1 (merged) ──► C.2 frozen inputs and writer coordination ──► E4.3 core adaptation
J3 candidate ──► independent practical and applicable scientific review ──► scoped rule release
Validated inputs + conformant, released rules + athlete context ──► first approved block and week
Approved week ──► execution and feedback ──► next-week review and athlete decision ──► follow-up
```

**Engineering priority.** For C.2, freeze the complete scope, including omissions, coverage, issues, mappings, confirmations and manual lineage. Recheck it in the approval transaction with the relevant writers coordinated. Prove that a newly inserted workout or issue can stale a proposal even when every previously selected row is unchanged. Exercise rollback, retry and historical replay on disposable PostgreSQL. Use the [writer inventory](../planning-evidence.md#writer-inventory-and-e42c2). D1V preparation, focused J review, B diagnosis and G scheduling can proceed alongside this work.

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
