# J1 scientific evidence catalog

Release `j1-screening-1` contains six published sources, five empirical claim drafts,
one qualification linking two drafts, and one original programming option. Five sources
await independent review and one is still in screening. All five claims and the method
are pending. A matching operational query therefore returns an evidence gap. The
invented C2 release exercises the positive retrieval path in tests.

## Coverage and search record

On 2026-11-24, the four design candidates were checked by title and DOI. Targeted
searches extended the queue. This was a focused screen, without systematic coverage
or independent duplicate extraction. The [manifest](../backend/src/fitness_intelligence/evidence/releases/j1-screening-1.json)
contains the citations, study populations, comparisons, horizons, locators, access
depth, bias assessments, rights and dated publication checks.

| Question and search terms | Selection and transfer limits |
| --- | --- |
| Strength dose · “resistance training prescription”, “weekly set progressions” | Currier Figure 3A supplies one contrast against inactivity. Figure 3B measures hypertrophy. Comparing weekly set increments requires an active comparator. Enes et al. is a primary trial to appraise for that separate question. [Currier full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10579494/) · [Enes trial](https://pubmed.ncbi.nlm.nih.gov/39869076/) |
| Periodization · “volume equated”, “block vs weekly undulating”, “trained women” | Moesgaard's abstract reports a pooled 1RM advantage over constant programming. The publisher recorded a table-format update on 2022-02-04. Duration by contrast, trial quality and the updated tables still need inspection. No claim extracted. The narrower Bartolomei comparison is a lead for block selection. [Publisher record and change history](https://link.springer.com/article/10.1007/s40279-021-01636-1) · [Primary comparison](https://pubmed.ncbi.nlm.nih.gov/25807030/) |
| Concurrent training · “trained lower body strength”, “concurrent endurance resistance same session” | Schumann's pooled maximal-strength estimate spans modest effects in either direction. Petré found smaller lower-body 1RM gains in trained participants with more narrowly defined endurance doses. The analyses share trials and use different definitions of training status. The qualification edge preserves both populations. The explosive-strength and timing analyses do not establish a mandatory interval between an easy run and a press. [Schumann §3.2–3.3](https://link.springer.com/article/10.1007/s40279-021-01587-7) · [Petré §3.4–3.5](https://link.springer.com/article/10.1007/s40279-021-01426-9) |
| Monitoring · “acute training load subjective measures”, “monitoring fatigue intensified training recreational runners” | Saw Table 7 concerns changes in questionnaire measures. The draft uses only the acute-load-increase finding. Nuuttila Figure 3 concerns a nocturnal measurement over an overload week. Subjective readiness contributed to subgroup assignment, which limits claims about independent prediction. Neither study compared adjusting workload in response to one reading with retaining the plan. [Saw full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4789708/) · [Nuuttila §3.3](https://doi.org/10.1002/ejsc.12115) |

Europe PMC MED records supplied the DOI, authors, journal, pagination, first publication
date and available license metadata. PubMed XML publication types and linked notices
were checked for all six. No retraction or erratum was indexed on those records at the
check. PubMed links an accompanying commentary to Currier. Publisher and open full-text
records supplied the results for five sources, including Saw via Europe PMC full-text
XML. Only the abstract and publisher change history were examined for Moesgaard.
Publication notices can arrive after a release. [Currier commentary record](https://pubmed.ncbi.nlm.nih.gov/37407091/)

## Calling the catalog

Use the internal Python interface from the backend environment. Pass the release ID
and exact lower-case vocabulary terms from the relevant claim scope. `mixed` describes
a pooled sample. Use `unknown` for missing experience. A caller must have a basis for
choosing a more specific category. No personal identifiers or free-text observations
are needed.

```python
from fitness_intelligence.evidence import Scope, load_release

catalog = load_release("j1-screening-1")
query = Scope(
    question="concurrent-strength",
    objective="strength-development",
    population="healthy-adults",
    experience="mixed",
    intervention="supervised-aerobic-plus-strength",
    comparator="identical-strength-only",
    outcome="maximal-strength",
    horizon="at-least-four-weeks",
    block_context="concurrent-training",
)
selection = catalog.retrieve(query)
assert selection.matches == () and selection.gaps
assert catalog.ineligibility("pooled-concurrent-strength@1") == "pending"
```

The loader checks SHA-256 over the exact bundled JSON bytes against the release registry
and validates the complete graph. Unknown IDs and invalid releases raise an error.
Records and returned sequences are immutable. The result pins the release ID, digest,
algorithm version and structured query, with ordered matches, exclusions and gaps.

Selection requires exact agreement across the requested dimensions. A population or
experience difference needs an explicitly reviewed transfer to that target pair. Other
mismatches and unknown dimensions exclude the claim from the primary selection. Direct
matches precede indirect matches, then higher reviewed quality and lexical revision key.
Each match carries its original assertion, scope, limitations, assessment, source citation
and result locator. Related findings carry the reason and direction of the edge. A related
finding with different scope is labeled `context-only`. An unavailable related revision
produces a gap. The question's cataloged coverage limit accompanies an empty result.

`catalog.methods(question)` returns eligible programming options separately. The E1
planner's `Finding` records and synthetic rule version continue to describe rule decisions.
E2/E3 can consume an evidence selection independently. An objective, workload or schedule
change still goes through the planner's validator.

## Review and release procedure

1. For each proposed assertion, open the linked result. Check direction, comparator,
   units, precision, training status, dose, duration and outcome against the original.
   Record access depth, bias, exclusions and contrary findings. Review overlapping
   trials when comparing syntheses. Keep recommendations from the discussion in the
   methodology record when appropriate. Use a screening disposition for unresolved
   source appraisal.
2. A designated independent human reviews source, claim, transfer arguments, edges,
   rights and method references in version control. Record their identity, role, date
   and explicit attestation on each accepted revision and on the release. The JSON
   represents that decision. The review trail establishes who made it. Model-generated
   extractions remain drafts until that review occurs. Fixture attestations simulate
   this workflow using invented reviewers.
3. Publish a new immutable file and append a release ID and digest to the registry.
   Allocate a new revision key to any changed record, including changes to its review.
   Preserve earlier files and pins. Use a forward `supersedes` edge for replacements
   and a dated withdrawal for a discredited exact revision. Carry prior withdrawals
   forward. Recheck every relation when its endpoint changes. Verify the release with
   the portable suite, including the citation mapping in the C2 case.
4. Replay with the original pin. To check whether a cited revision can still be used,
   ask the current catalog for `ineligibility(key)`. It returns a reason for withdrawn,
   superseded, pending or absent revisions. C3 tests historical replay and this current
   check. E2/E3 owns the current-release selection, atomic decision and proposal lookup.
5. Store only bibliographic data, links and original summaries. Each source records its
   licensing limits. Any additional reuse of text, tables, figures or program material
   needs a rights decision for the intended deployment.

The initial next-review dates are proposed for 2027-02-24. Review ownership, cadence,
acceptable transfers and resolution of disagreements need a human decision. Priority
gaps include progression increments, fatigue-guided deloads, taper effects and timing
in trained hybrid athletes. The [design](scientific-knowledge-design.md) and
[evaluation cases](coaching-evaluation-design.md) describe their downstream use.
