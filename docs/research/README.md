# Research library

A research packet records what a research session found, what it could check, and which questions remain open. A reviewed J1 scientific claim describes a specific result in a defined population, comparison, outcome and time horizon. A programming policy describes a choice the coach could make. Accepting a claim does not establish when a planner should act on it.

## Packet 001

[Strength progression, longitudinal periodization and concurrent endurance maintenance](001-strength-progression-periodization.md) is the supplied Markdown from a separate ChatGPT scientific research session, dated 2026-11-24, revision 0.1, pending independent human review. The archive preserves the bytes of `fitness-intelligence-research-001.md` (SHA-256 `0b5497892f1242dfb768880f94f580ffa6f471837d634d7763238848e55189e6`). Its access notes, publication checks and proposed review dates report the originating session's work. The packet describes a targeted search and identifies which results came from abstracts or the existing catalog.

- The [research backlog](research-backlog.md) carries forward all 14 ranked questions. RT-02, working-set volume adjustment in trained lifters, was the proposed next investigation and is the focus of Packet 002.
- The [draft evidence additions](drafts/001-evidence-additions.json) are the JSON fragment from section 5. They add seven sources (one pending, six screening), five pending claims, and one pending method. Two claims cite the existing screening source `moesgaard@1`. All proposed approvals are null and all proposed transfer lists are empty.
- The [six candidate policies](001-strength-progression-periodization.md#3-candidate-coaching-policies) cover load and repetition progression (RT-P01), working-set volume adjustment (RT-P02), protection of secondary qualities (CT-P01), concurrent-session organization (CT-P02), phase-aware adaptation (LP-P01), and protection of recovery, deload and assessment (LP-P02). Maintaining a productive dose is a legitimate option. Successful completion alone does not establish that increasing volume is optimal. The Enes trials compared groups with different cumulative doses, leaving the effect of escalation itself unresolved.

## Packet 002

[Working-set volume adjustment in experienced resistance-trained athletes](002-working-set-volume-adjustment.md) continues RT-02. This is packet revision 0.1, dated 2026-11-24, from a separate ChatGPT scientific research session. The archive preserves the bytes of `fitness-intelligence-research-002.md` (SHA-256 `b561a54d773105cdd4894397e63717606708f10a4380c2c7eb9c1fce7f08b6c0`). Its preliminary appraisal is complete. Scientific verification remains open.

**Refinement of Packet 001.** Packet 002 reports that, in the female Enes manuscript, the smaller escalation arm began at 16 weekly quadriceps sets and accumulated **252 prescribed sets**. The constant arm accumulated **264**. The manuscript reports greater leg-press improvement in the smaller escalation arm. If confirmed, a greater cumulative prescribed set count alone cannot explain that contrast. Starting dose, preparatory exposure and final dose also differed, and the trial did not isolate an independent causal effect of escalation. Verify the schedule, assigned versus realized exposure, and result against the publisher's Methods, Fig. 4B and Table 2. Packet 001 retains its original abstract-based interpretation. [Protocol reconstruction](002-working-set-volume-adjustment.md#22-protocol-and-dose-reconstruction)

**RT-P02 revision 0.2** is the latest candidate methodology for discussion. It proposes maintaining a productive dose by default and considering an increase, reduction, redistribution or request for information in light of comparable performance, adherence, burden and competing objectives. Feedback-driven weekly set adjustment for strength in experienced hybrid athletes remains an open efficacy question. The experimental counts, fractional-volume estimates and effect sizes describe the research. The packet preserves [16 synthetic evaluation cases](002-working-set-volume-adjustment.md#6-evaluation-cases) and its [independent review checklist](002-working-set-volume-adjustment.md#8-human-review-checklist).

### Source access requiring review

The [Packet 002 fragment](drafts/002-evidence-additions.json) proposes `full-text` for all five source revisions. J1 permits only `full-text` or `abstract`. The packet reports the following access, with materially different implications for verification.

| Source revision | Access reported by the research session | Outstanding check |
| --- | --- | --- |
| `enes-males@2` | Journal text copy on ResearchGate | Compare protocol, figures and supplements with the publisher version. |
| `enes-females@2` | Manuscript text on Scribd, cross-checked against the publisher abstract | Verify the manuscript version, schedule and strength contrasts. |
| `pelland@2` | Typeset-text reproduction on Studylib, cross-checked against the publisher abstract | Confirm version, model, coding and uncertainty against the paper and OSF outputs. |
| `barsuhn@1` | Indexed passages from Methods, a baseline table and Discussion. Direct publisher access was blocked. | The proposed `full-text` classification overstates the documented access unless confirmed. Inspect the complete paper and adjudicate the field. |
| `enes-perceptual@1` | Publisher full text | Confirm shared cohort, outcome definitions and reuse rights. |

Aube was also appraised from indexed passages and has no proposed Packet 002 source revision. All access descriptions are attributed to the research session. Independent reviewers still need to check versions, publication notices, rights and locators.

## Numbering and revisions

Assign the next unused three-digit number to each new research question or packet of related questions. Keep its number and filename stable across revisions. Cite the packet number, revision, section and Git commit when reviewing an extraction or proposing a rule. Evidence IDs such as E02 are local to their packet. J1 references use exact revision keys such as `moesgaard@1`.

Keep the supplied revision in Git history. For a correction or follow-up extraction, increment the packet revision, date it, and record what changed and why. Update the associated draft and backlog when affected. A change to a previously released catalog record needs a new J1 revision key.

## From packet to reviewed evidence

1. Extract proposed records into a fragment under `drafts/` and keep their source locators, access depth, uncertainty and screening dispositions. Validate the fragment in the context of its full target manifest, including existing relations and withdrawals.
2. Assign an independent human reviewer. Use the review checklists in [Packet 001](001-strength-progression-periodization.md#8-human-review-checklist) and [Packet 002](002-working-set-volume-adjustment.md#8-human-review-checklist). Check each result against its source, including the population, comparator, direction, units, interval and limitations. Review publication notices, reuse rights, overlapping trials, scope terms, provisional quality and any argument for transfer. Record unresolved issues with the affected record.
3. Record the designated reviewer's identity, role, date and explicit decision on each accepted revision in version control. A claim requires reviewed supporting sources. Operational eligibility also requires a reviewed release. A separately authorized release receives a new immutable manifest, registry entry and digest under the [J1 release procedure](../scientific-evidence-catalog.md#review-and-release-procedure).

### Checking both drafts against J1

Packet 002 adds the `volume-burden` question, five source revisions, five pending claim revisions and one pending programming method. The combined candidate contains **5 questions, 18 source revisions, 15 claim revisions, 1 qualification relation, 3 programming methods and 0 withdrawals**. The 18 source revisions cover 15 distinct publication DOIs. The male Enes, female Enes and Pelland papers each appear at `@1` and `@2`. The Enes perceptual follow-up also reports on the male strength cohort, so distinct publications need not represent independent participants.

Both Enes strength claims retain their pending `@1` and `@2` revisions with their respective source references. Earlier screening dispositions remain recorded. The combined graph preserves the existing qualification and has no supersession edges. Reviewers still need to assess scope semantics, transfer and method support.

Run the following from `backend/` in the project Python environment. It verifies the registered base digest, validates the complete candidate in memory with J1 schema version 1, and exercises J1 retrieval for each exact claim scope and catalog question.

```python
import json
from hashlib import sha256
from pathlib import Path

from fitness_intelligence.evidence import load_release
from fitness_intelligence.evidence.catalog import CorpusRelease
from fitness_intelligence.evidence.retrieval import Catalog

base = load_release("j1-screening-1").release
manifest = base.model_dump(mode="json")
manifest["release_id"] = "j2a-packets-001-002-candidate"
for packet in ("001", "002"):
    path = Path(f"../docs/research/drafts/{packet}-evidence-additions.json")
    for group, records in json.loads(path.read_bytes()).items():
        manifest[group].extend(records)

data = json.dumps(manifest).encode()
candidate = CorpusRelease.model_validate_json(data)
assert candidate.approval is None
assert candidate.relations == base.relations and candidate.withdrawals == base.withdrawals
catalog = Catalog(candidate, sha256(data).hexdigest())
for claim in candidate.claims:
    assert catalog.ineligibility(claim.key) == "pending"
    result = catalog.retrieve(claim.scope)
    assert result.gaps and not result.matches
assert all(not catalog.methods(q.id) for q in candidate.questions)
```

## From candidate policy to planner rule

Review each method separately from the empirical claims it cites. Identify which choices reflect evidence, athlete preferences or engineering safeguards. Define eligible observations, alternatives (including holding the dose), parameters, authority to change a plan and conditions for deferring a decision. A reviewer must justify any proposed numeric threshold or transfer to an experienced hybrid athlete.

Before adopting a rule version, exercise the [synthetic evaluation cases](001-strength-progression-periodization.md#6-evaluation-cases) with pinned block, evidence and rule versions. Check acceptable alternatives, missing feedback, secondary objectives, protected assessments and declined changes. Record the policy decision, review and validation results with any later planner change so historical plans can be replayed with their original rules. Prospective effectiveness is a separate research question. Both packets and their drafts remain research inputs. E1 continues to use its existing synthetic progression rules.
