# Research library

A research packet records what a research session found, what it could check, and which questions remain open. A reviewed J1 scientific claim describes a specific result in a defined population, comparison, outcome and time horizon. A programming policy describes a choice the coach could make. Accepting a claim does not establish when a planner should act on it.

## Packet 001

[Strength progression, longitudinal periodization and concurrent endurance maintenance](001-strength-progression-periodization.md) is the supplied Markdown from a separate ChatGPT scientific research session, dated 2026-11-24, revision 0.1, pending independent human review. The archive preserves the bytes of `fitness-intelligence-research-001.md` (SHA-256 `0b5497892f1242dfb768880f94f580ffa6f471837d634d7763238848e55189e6`). Its access notes, publication checks and proposed review dates report the originating session's work. The packet describes a targeted search and identifies which results came from abstracts or the existing catalog.

- The [research backlog](research-backlog.md) carries forward all 14 ranked questions. RT-02, working-set volume adjustment in trained lifters, is the proposed next investigation.
- The [draft evidence additions](drafts/001-evidence-additions.json) are the JSON fragment from section 5. They add seven sources (one pending, six screening), five pending claims, and one pending method. Two claims cite the existing screening source `moesgaard@1`. All proposed approvals are null and all proposed transfer lists are empty.
- The [six candidate policies](001-strength-progression-periodization.md#3-candidate-coaching-policies) cover load and repetition progression (RT-P01), working-set volume adjustment (RT-P02), protection of secondary qualities (CT-P01), concurrent-session organization (CT-P02), phase-aware adaptation (LP-P01), and protection of recovery, deload and assessment (LP-P02). Maintaining a productive dose is a legitimate option. Successful completion alone does not establish that increasing volume is optimal. The Enes trials compared groups with different cumulative doses, leaving the effect of escalation itself unresolved.

## Numbering and revisions

Assign the next unused three-digit number to each new research question or packet of related questions. Keep its number and filename stable across revisions. Cite the packet number, revision, section and Git commit when reviewing an extraction or proposing a rule. Evidence IDs such as E02 are local to their packet. J1 references use exact revision keys such as `moesgaard@1`.

Keep the supplied revision in Git history. For a correction or follow-up extraction, increment the packet revision, date it, and record what changed and why. Update the associated draft and backlog when affected. A change to a previously released catalog record needs a new J1 revision key.

## From packet to reviewed evidence

1. Extract proposed records into a fragment under `drafts/` and keep their source locators, access depth, uncertainty and screening dispositions. Validate the fragment in the context of its full target manifest, including existing relations and withdrawals.
2. Assign an independent human reviewer. For packet 001, use the [human review checklist](001-strength-progression-periodization.md#8-human-review-checklist). Check each result against its source, including the population, comparator, direction, units, interval and limitations. Review publication notices, reuse rights, overlapping trials, scope terms, provisional quality and any argument for transfer. Record unresolved issues with the affected record.
3. Record the designated reviewer's identity, role, date and explicit decision on each accepted revision in version control. A claim requires reviewed supporting sources. Operational eligibility also requires a reviewed release. A separately authorized release receives a new immutable manifest, registry entry and digest under the [J1 release procedure](../scientific-evidence-catalog.md#review-and-release-procedure).

### Checking the draft against J1

Run this from `backend/` in the project Python environment. The loader verifies the existing release pin. The example assembles the successor in memory and passes its JSON to the same strict model used by the loader.

```python
import json
from pathlib import Path

from fitness_intelligence.evidence import load_release
from fitness_intelligence.evidence.catalog import CorpusRelease

base = load_release("j1-screening-1").release
draft = json.loads(Path("../docs/research/drafts/001-evidence-additions.json").read_bytes())
manifest = base.model_dump(mode="json")
manifest["release_id"] = "j2a-packet-001-candidate"
assert set(draft) == {"sources", "claims", "methods"}
for group, records in draft.items():
    manifest[group].extend(records)

candidate = CorpusRelease.model_validate_json(json.dumps(manifest))
assert candidate.approval is None
assert candidate.relations == base.relations and candidate.withdrawals == base.withdrawals
```

Against `j1-screening-1`, the complete candidate passes schema version 1 with four questions, 13 sources, ten claims, one qualification, two methods and zero withdrawals. Revision keys are unique, and support and method references resolve. The claims reuse the registered questions `periodization` and `strength-dose`. J1 checks scope term syntax and uses exact matching for retrieval. New terms such as `at-least-one-year`, `trial-endpoint` and `one-rm-strength` still need semantic review for the intended queries.

## From candidate policy to planner rule

Review each method separately from the empirical claims it cites. Identify which choices reflect evidence, athlete preferences or engineering safeguards. Define eligible observations, alternatives (including holding the dose), parameters, authority to change a plan and conditions for deferring a decision. A reviewer must justify any proposed numeric threshold or transfer to an experienced hybrid athlete.

Before adopting a rule version, exercise the [synthetic evaluation cases](001-strength-progression-periodization.md#6-evaluation-cases) with pinned block, evidence and rule versions. Check acceptable alternatives, missing feedback, secondary objectives, protected assessments and declined changes. Record the policy decision, review and validation results with any later planner change so historical plans can be replayed with their original rules. Prospective effectiveness is a separate research question. Packet 001 and its draft remain research inputs. E1 continues to use its existing synthetic progression rules.
