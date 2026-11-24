# Scientific knowledge for planning and review

**Proposed MVP for workstream J.** A reviewer should be able to open a recommendation, select
one scientific assertion, see the exact supporting result and its limits, and reproduce why the
planner retrieved it. Start with a small, curated catalog in version control. Ship a validated,
immutable release with the planner and query it locally. A week can still be generated from
approved programming rules when the catalog returns a gap. The explanation must identify the
judgment involved. See the [coaching science requirements](coaching-science.md).

## What belongs in the catalog

| Record and key | Required content and relationships |
| --- | --- |
| SourceRevision (source ID, revision) | Authors, title, venue, year, DOI or stable URL, publication/version date, study design, access depth, correction/retraction check and date, source of that check. Include rights holder/license if known, permitted uses, permission record and review date. A DOI identifies the work. The revision identifies the edition examined. |
| ClaimRevision (claim ID, revision) | One answerable question and one empirical assertion in the curator's own words. Record population, training status and relevant exclusions, intervention/exposure and dose, comparator, outcome, follow-up, study design, direction/magnitude, unit, interval/precision and limitations. Mark unavailable fields explicitly. Document risk of bias, consistency, directness, confidence with reasons, reviewer and review date. |
| ClaimSupport | Connect a claim revision to one or more exact source revisions. Each edge names a result locator (table, figure, page/paragraph or labeled result), what it supports and any restriction. Where reviews overlap, record shared primary studies when known. A count of citations is a poor measure of independent evidence. |
| ClaimRelation | Typed, reasoned edge between exact claim revisions on a question. Use conflicts-with for materially incompatible results, qualifies for a boundary such as population or outcome, and supersedes for a replacement. Preserve direction on asymmetric edges. Record why apparent differences can or cannot be reconciled. |
| MethodRevision | An original description or permitted reference to a programming option, its assumptions, provenance and practical tradeoffs. It can link to reviewed claims for particular assertions about effects. A coach's template can explain why a week takes a given shape. |
| CorpusRelease | Immutable manifest of exact source, claim, relation and method revisions, question vocabulary, schema version, release ID, digest, review date and approver. Include review decisions and gaps for each in-scope question. Reject dangling references, duplicate keys, supersession cycles and unreviewed entries in the eligible set. |

Store these as structured, reviewable data files when J is implemented. Typed loaders validate
keys, units, enums and links. In-memory maps by question and ID are sufficient for this corpus.
Keep the fixture catalog under a separate test namespace with an explicit synthetic marker.
A release check must forbid synthetic sources or claims in an operational manifest.

Athlete observations, restrictions and free text belong in owner-scoped application storage.
The planner formulates a query using coarse population and training-context attributes in
memory. The shared catalog never receives a personal history. Each proposal saves its selected
evidence and athlete facts under that owner. Bibliographic metadata and original summaries are
the default. Do not commit PDFs, abstracts, tables, figures or proprietary program sequences.
A curator must document rights for the intended storage, display and deployment before approving
any additional use. A publicly readable article alone does not establish those rights.

## Screening queue for the first release

Choose questions that matter to the [two worked cycles](training-plan-design.md). These four
papers were located and their bibliographic records and abstract-level scope checked for this
design. They are **screening candidates**. Full result appraisal, publication-status review,
rights review and approval of individual claims are tasks for the first curator.

| Planning question | Starting source and result to inspect | Transfer question before use |
| --- | --- | --- |
| How do load, sets and frequency relate to strength and hypertrophy? | Currier et al., 2023, network meta-analysis. Compare the separate outcome networks in Results and Figure 3. [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10579494/) | How comparable are healthy adult trial participants, doses and endpoints to this athlete's press assessment? A network ranking alone cannot determine an individual's starting load. |
| Which periodization comparisons inform this block objective? | Moesgaard et al., 2022, volume-equated resistance training. Inspect the strength and hypertrophy comparisons and training-status subgroup in Results. [Article](https://link.springer.com/article/10.1007/s40279-021-01636-1) | Did the comparison include the approach, population and outcome at issue? Record gaps for untested block arrangements and precision of subgroup estimates. |
| Would a proposed run/lift arrangement compromise the chosen outcome? | Schumann et al., 2022, concurrent aerobic and strength training. Inspect the separate maximal strength, explosive strength and muscle-size results and timing subgroups. [Article](https://link.springer.com/article/10.1007/s40279-021-01587-7) | Do the aerobic protocol and endpoint match this week? A group-level timing subgroup cannot set an individual's mandatory spacing in hours. |
| How should the coach use a report of fatigue alongside sparse measurements? | Saw, Main and Gastin, 2016, review of athlete monitoring. Inspect the acute training-load comparisons for subjective and objective measures. [Article](https://bjsm.bmj.com/content/early/2015/09/30/bjsports-2015-094758) | Does the study address monitoring, or actually test the effect of a deload? Keep the latter question open until a relevant intervention is reviewed. |

For each question, log the search date, search terms, inclusion/exclusion reasons, relevant
newer or contrary studies and the curator's selection. Start with pertinent systematic reviews
of controlled trials for intervention effects, inspect primary studies when subgroup or protocol
details decide applicability, and use observational evidence for descriptive questions. Admit a
small set of claims that can actually justify a sentence in the review flow. Leave unfilled
questions visible. Numerical policy defaults, especially safety or progression caps, require
their own approval and evaluation even when a related finding is available.

## Retrieval contract

**retrieve(release_id, question, population, intervention, comparator, outcome, horizon,
block_context)** returns a stable list of eligible claim revisions with source locators,
applicability (direct, indirect with transfer argument, or unknown), uncertainty, material
counterevidence and gaps. It also returns exclusion reasons and the retrieval algorithm version.
A separate method lookup returns labeled programming options. Neither interface writes a plan.

1. Resolve the pinned manifest and verify its digest. Validate vocabulary and select candidates
   by question, design, comparator and outcome. If the outcome differs, label the mismatch.
2. Compare population, training age, dose, follow-up and block context. An unknown athlete
   characteristic remains unknown. For indirect matches require an explicit transfer argument
   before using one in an explanation. Rank using documented categorical criteria for directness
   and reviewed quality, with stable claim ID and revision as the final tie-break.
3. Expand each selected finding to its material conflicts and qualifications, even if that
   exceeds the requested number of matches. Include the reasons and outcome differences. Return
   an explicit gap if no eligible result supports the assertion.
4. Record the normalized query, release digest, retrieval version, ordered selection, conflict
   revisions and applicability judgments. The same pinned inputs must reproduce the selection.
   An unavailable or invalid catalog permits only a clearly labeled rules-only draft. A
   recommendation requiring a particular empirical premise cannot proceed without eligible support.

## From a result to a decision

A rationale contains typed statements. An **empirical statement** stores assertion text,
claim and source revision(s), locator, applicability and uncertainty. A **programming choice**
cites a rule and parameter version or method revision and its assumptions. An **athlete
observation** cites the dated owner-scoped input, coverage and measurement/inference status.
A **preference or restriction** cites the applicable context revision. A proposed action
identifies which of those statements it uses and remains subject to deterministic validation
and athlete approval. The template renderer can display every item without an LLM.

For example, an athlete reports tired legs after a run. A run-day move can cite that dated
report, the available Sunday slot, and the block rule preserving two weekly runs. The rationale
can say the athlete is trying a different day and will compare next week's feedback. To add
a sentence about effects on explosive strength, retrieval would need an approved claim for
that outcome and a defensible transfer argument. With neither, omit the sentence and retain
the practical rationale. See the [approval contract](training-plan-design.md#approval-revisions-and-execution).

## Publication, correction and audit

A curator screens a source, verifies its publication and correction status, examines the
specific result, drafts an original claim and documents limitations and rights. A designated
reviewer accepts, requests changes or excludes it. Publish only after manifest validation and
the [evaluation gates](coaching-evaluation-design.md#release-gates). New reviews and corrections
produce new revisions. Record what changed, why, when and which rule or claim it affects.

Keep a current withdrawal list keyed by exact revision, distributed with the active reviewed
release. The application pins that active release and withdrawal generation during validation
and approval. A release switch and an approval must have a defined order, for example a shared
lock on the local release head during approval and an exclusive lock during activation.
A newer ordinary release can prompt reevaluation. A withdrawn premise blocks new advice and
approval of dependent outstanding proposals. If current withdrawal status cannot be established,
defer approval of advice relying on the affected evidence.

Use an index or owner-scoped scan of saved rationale references to find affected rules,
proposals and current prescriptions. Flag an approved plan for review and generate a new
proposal if a change is warranted. Historical replay uses the original manifest, pinned
selection and allowed provenance, with a visible correction or withdrawal annotation. If rights
change, remove restricted display material through the applicable rights process and retain the
permitted bibliographic pointer, revision and audit reason.

## Delivery and open decisions

- **First implementation.** Define the release/claim loader and retrieval against an invented
  catalog with two conflicting claims, an indirect population match, one method and one gap.
  Accept when repeated queries produce the same ordered evidence, both sides of the conflict
  are visible and an unreviewed claim cannot enter an empirical rationale.
- **First operational release.** Assign curator and reviewer, appraise the screening queue and
  publish the first narrow manifest. Accept when a reviewer can follow each scientific sentence
  in a generated week to its result, replay it across a corpus update, and identify pending
  proposals affected by a withdrawal. Review on corrections or retractions and set a dated
  next review for every included source.
- **Unresolved.** Select review ownership and cadence, criteria for an acceptable transfer
  argument, and the handling of disputes between reviewers. Expand the queue for taper or
  recovery interventions before making claims about their effects.
- **Later.** Add search infrastructure only when a measured retrieval failure on reviewed
  questions justifies it. Automated literature ingestion, embeddings, a vector database and
  model-written summaries have no role in the first release.
