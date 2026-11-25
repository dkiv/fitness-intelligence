# Scientific curation and candidate coaching methods

The [research packets](../README.md) identify candidate evidence and coaching decisions. J3A revisits selected results for one capability. J3B uses those appraisals to specify a practical method for review. The [standing methodology](../methodology.md) and [decision backlog](../research-backlog.md#j3-scientific-curation) apply throughout.

## Strength progression in an approved hybrid block

| Archive | SHA-256 of supplied bytes | Git blob |
| --- | --- | --- |
| [J3A.1 scientific appraisal](j3a-001-strength-progression-appraisal.md) | `1d32f0e663702eb6cd3fd3fd9688dc2107ab6f05ea30a598c2b28bfabc3b99f6` | `4f23093a61c5dba079f88e922a6fb57ab6f75520` |
| [J3B.1 proposed J3-M01, revision 0.1](j3b-001-strength-progression-methodology.md) | `8d25b228e109036e9524e7b2a91599ba712737d766cceaf3d57aaf906172d3c5` | `26c70ef07f83cd4687be684ae3a69ebd1e678bbd` |

### Scientific decisions awaiting independent review

The findings below describe the AI-assisted checks in J3A.1. Independent human scientific approval is outstanding for all six papers. Reviewers should verify versions, publication notices (including corrections and retractions), version-specific reuse rights and transfer to the intended athlete. The appraisal reports a direct Crossmark check only for Hickmott. [Source appraisals](j3a-001-strength-progression-appraisal.md#3-original-source-verification-and-scientific-appraisal)

| Source | Finding and remaining decision |
| --- | --- |
| Plotkin | Both progression arms improved on the Smith squat test. The adjusted load-minus-repetitions contrast was +2.0 kg (90% interval −2.4 to +7.8). Check attrition, test specificity and transfer before retaining the scoped claim. The trial leaves the choice of increment open. |
| Helms | Both groups improved. The percentage arm also progressed conditionally, and realized exposure differed. Check the narrative percentage-group bench post-test mean against Table 4, baseline and change before any secondary extraction. The two lift outcomes share participants. |
| Halperin | The abstract supports a pooled signed error in predicted repetitions to failure. Opposite errors can cancel. Obtain the final full text and check failure definitions, heterogeneity and exercise strata before quantitative use. Individual correction and sensitivity to change remain unverified. |
| Hickmott | The pooled load-autoregulation interval includes zero. Table 2 includes Helms, so counting both as independent corroboration would double-count participants. Review the fixed-effect pooling across lifts and populations. Velocity-loss comparisons address a separate question. |
| Barsuhn | Of 55 allocated, 29 finished. The control means were 161.90 kg at baseline (21 participants) and 193.70 kg at follow-up (10). Their roughly 32 kg difference **is not a matched-person change estimate**. The available-data mixed model included all 55. Its pooled time effect and group main effect answer different questions from a group-by-time contrast. A differential gain was not established. Reconcile missingness, baseline imbalance, unusually narrow intervals and discordant pairwise p-values before interpreting uncertainty. |
| Petré | The 6–21-week horizon describes the whole review. Reconstruct the trained timing subgroups, identify shared studies with Schumann and Huiberts, and assess transfer from chronic lower-body maximal strength. The subgroup comparisons leave the causal effect of spacing, upper-body outcomes and individual recovery times open. |

The [pending fragment](drafts/j3a-001-evidence-revisions.json) reproduces Appendix A exactly. `habitual-set-maintenance-strength@2` cites `barsuhn@2` at the existing DOI. Each has a null approval. Packet 002 retains its original source and claim. Any future replacement requires a separate decision on the exact revisions and a review of each dependent method. The candidate contains no supersession or withdrawal.

Five staged methods directly cite `habitual-set-maintenance-strength@1`. They are `working-set-volume-review@1`, `bounded-hybrid-review-transition@1`, `recovery-aware-set-dose-review@1`, Packet 009’s `contextual-decision-response-history@1` and Packet 010’s `rolling-horizon-block-intentions@1`. The appraisal also flags `task-specific-effort-adjustment@1` and `priority-aware-concurrent-calendar@1` for review of related effort and scheduling claims. The [combined manifest check](../README.md#checking-the-packet-and-curation-drafts-against-j1) verifies the direct references.

### Candidate methodology for review

| Bundle | Decisions preserved in J3-M01 |
| --- | --- |
| M01a · Movement prescription and progression | Select purpose-specific templates and comparable historical references. Distinguish confirmed and inferred sets. Review RPE-aware and RPE-free branches, straight sets, separate top and backoff groups, rep reset and equipment rounding. [Prescription](j3b-001-strength-progression-methodology.md#3-practical-prescription-methodology-m01a) · [Movement progression](j3b-001-strength-progression-methodology.md#4-movement-progression-m01a) |
| M01b · Working-set exposure | Reconstruct representative actual exposure. Review when to hold a productive dose, trial a set, reduce local burden or redistribute work, and how to evaluate the trial. [Working-set adjustments](j3b-001-strength-progression-methodology.md#5-working-set-exposure-adjustment-m01b) |
| M01c · Concurrent scheduling and constraints | Compare lifting demands with running commitments and athlete priorities. Review feasible slot moves, local changes and conflicts that require block review. [Concurrent scheduling](j3b-001-strength-progression-methodology.md#6-concurrent-scheduling-and-recovery-context-m01c) |

Sections 7–8 preserve all 17 proposed parameters (N01–N17), the exact load increment policy and the deterministic candidate procedure. Section 9 illustrates the decisions in seven worked examples (W1–W7) and sixteen additional acceptance cases (T01–T16). Section 10 assigns review questions to the coach, scientific reviewer, athlete, engineering reviewer and operational owner, and identifies gaps in implementation readiness at the archive’s pinned snapshot. The profile and all three bundles await independent review. Numerical choices are proposals. [Parameters](j3b-001-strength-progression-methodology.md#7-proposed-numerical-parameter-configuration) · [Exact increments](j3b-001-strength-progression-methodology.md#71-exact-increment-policy-and-examples) · [Procedure](j3b-001-strength-progression-methodology.md#8-deterministic-candidate-decision-procedure) · [Examples and acceptance cases](j3b-001-strength-progression-methodology.md#9-worked-examples-and-synthetic-evaluation-cases) · [Review packages and readiness](j3b-001-strength-progression-methodology.md#10-human-review-package-and-implementation-readiness)

### Additional implementation-review questions

1. **Rep progression.** Would a different increment better suit moderate-repetition or accessory work? Compare role-specific alternatives to the proposed +1 total repetition.
2. **Load increments.** When the smallest equipment step exceeds the applicable percentage cap, rounding above the cap remains ineligible. Review whether a movement warrants a separately documented exception with its own cap.
3. **Historical execution.** Many Hevy observations have inferred completion. Design a low-burden way for the athlete to confirm specific sets with attribution. Keep inference visible and require confirmation before using those observations in a positive progression gate.
4. **Scope of effort deviations.** Determine when a deviation affects an individual set group and when session-wide effort should constrain progression of another, otherwise successful group.
5. **Planner fit.** Inspect the current planner and its approval and persistence contracts before proposing new prescription fields, representations or stored state.

These questions belong to future method review. J3C.1 approval and operational release preparation are pending. Packet 010 closes scheduled preliminary collection. [Curation roadmap](../research-backlog.md#strength-progression-curation)

## Hybrid block construction and protected secondary outcomes

| Archive | SHA-256 of supplied bytes | Git blob |
| --- | --- | --- |
| [J3A.2 scientific appraisal](j3a-002-hybrid-block-appraisal.md) | `eed3155ff8b6c298a7ccf538d9f229a13d2430c06a27a11c11bb407556f68a3e` | `ee7f61addf5788d927f7d908cfbc70b27ada8d8b` |
| [J3B.2 proposed J3-M02, revision 0.1](j3b-002-hybrid-block-methodology.md) | `ee81af3b755d81cd352894126b78c9fe5a7f12f8bbf1b492a7f368c05c5b3347` | `d7bcc94c96ebadf0951020aae3462d272d8cd185` |

### Block evidence awaiting independent review

J3A.2 records AI-assisted factual checks. The table identifies what an independent reviewer still needs to establish before accepting a claim or transferring it to a hybrid athlete. Publication notices, corrections, retractions, source versions and reuse rights require independent verification. Earlier obligations, including the Petré subgroup horizons and Barsuhn statistics, remain open. [J3A.2 appraisals](j3a-002-hybrid-block-appraisal.md#3-original-source-verification-and-scientific-appraisal) · [J3A.1 outstanding reviews](#scientific-decisions-awaiting-independent-review)

| Source | Decision for the reviewer |
| --- | --- |
| Moesgaard | Obtain the updated full text, including the tables affected by the formatting update. Verify study membership, how volume was equated, subgroup interaction and sensitivity analyses. The trained subgroup estimate alone cannot establish a trained-specific advantage or a required phase sequence. |
| Micke | The crossover varied the timing of assigned conditioning. Actual lifting was unmonitored. The adjusted deadlift coefficient was +5.53 kg (SE 2.11 kg). Review realized exposure, period and sequence effects, carryover and multiple outcomes before interpreting the coefficient or applying it to block design. |
| Rønnestad | Verify the early-layout copy against the final article. The October 2011 issue is identifiable, but the stored day is a placeholder. Participant turnover changed the cohort between phases. Weekly versus alternate-week lifting varied both frequency and cumulative dose. Retrieve the direct between-arm half-squat 1RM change and its uncertainty before drawing a comparative conclusion. |
| Bickel | The young maintenance groups’ biopsy mean myofiber area remained above pretraining baseline. The older groups were no longer detectably above baseline at phase-two sampling. Exact retention of the original gain remains unresolved. Check imputed samples, attrition, age-by-dose cells, realized exposure and the journal-layout copy against the final version. The July 2011 publication day is a placeholder. |
| Hickson | Access was abstract-only. The shortest-duration group reportedly retained aerobic capacity while prolonged endurance declined. Obtain the original tests, group details, achieved exposure and direct contrasts with uncertainty. VO₂max alone cannot establish prolonged endurance retention. |
| Huiberts and reused Petré | Reconstruct study membership and overlap with Schumann before counting independent evidence. Keep lower-body strength, VO₂max, prolonged endurance and race performance distinct. Review task, training status, modality and horizon before transfer. Group and subgroup results do not quantify an individual interference effect or recovery interval. |

The evidence leaves universal maintenance doses, optimal block durations and compulsory phase sequences unresolved.

### Exact revisions and method dependencies

The [pending fragment](drafts/j3a-002-evidence-revisions.json) reproduces the JSON in J3A.2 Appendix A. Both revisions of each source identify the same DOI. Each new source and claim has null approval, and all three claims have empty transfer lists. Strict catalog validation accepts the revised scope terms. Independent review must assess their scientific meaning before any method can adopt them.

| Pending source and claim | Scope change from `@1` to `@2` | Only direct method citing the original claim |
| --- | --- | --- |
| `micke-hift-block@2`, `hift-conditioning-block-deadlift@2` | Identical scope. The revision adds the adjusted coefficient, SE and exposure limitations. | `hierarchical-hybrid-block-construction@1` |
| `ronnestad-soccer-maintenance@2`, `soccer-weekly-strength-retention@2` | Outcome narrows from `leg-strength` to `half-squat-one-rm`. | `outcome-specific-strength-maintenance@1` |
| `bickel-retention@2`, `young-reduced-dose-hypertrophy-retention@2` | Comparator changes from `end-of-development-reference` to `pretraining-baseline`. Outcome narrows from `muscle-hypertrophy` to `mean-myofiber-area`. | `outcome-specific-strength-maintenance@1` |

All three original claims still cite their original sources. Each proposed claim cites its corresponding revised source. The methods retain their exact original references pending explicit revision review and method approval. J3B.2 contributes only the candidate methodology. [Combined manifest check](../README.md#checking-the-packet-and-curation-drafts-against-j1)

### J3-M02 review bundles

| Bundle | Decisions preserved for review |
| --- | --- |
| M02a · Goals, archetype and historical reference | Rank objectives and define how each outcome will be assessed. Choose among strength emphasis, running emphasis, balanced development and transition. Select comparable historical observations with documented coverage. [Objective and reference methodology](j3b-002-hybrid-block-methodology.md#3-objective-archetype-and-reference-methodology-m02a) |
| M02b · Weekly structure, exposure bounds and protected outcomes | Start with familiar, tolerated actual exposure. Define protected outcomes, scheduled exposure and permitted adaptations separately. Detail the upcoming week, retain later weekly intents, and route calendar conflicts according to the approved constraints. Check per-review changes against the approved predecessor and cumulative changes against the initial block, including maximum permitted endpoints. [Rolling horizon](j3b-002-hybrid-block-methodology.md#4-initial-training-prescription-and-rolling-horizon-structure-m02b) · [Exact bound interactions](j3b-002-hybrid-block-methodology.md#52-exact-interactions-and-endpoint-validation) |
| M02c · Review, continuation and transition | Compare attributable execution with the exposure contract and comparable performance with the outcome contract. Review weekly adaptations, ordinary interruptions, resumption, continuation and explicit block transitions. A provisional successor requires a later approval decision. [Calendar and weekly review](j3b-002-hybrid-block-methodology.md#6-calendar-construction-feasibility-and-adaptation-m02bm02c) · [Block transition](j3b-002-hybrid-block-methodology.md#7-block-review-continuation-and-transition-m02c) |

J3-M02 revision 0.1 preserves B01–B18, the deterministic candidate procedure, three worked programs (strength emphasis, running emphasis and balanced development) and B-T01–B-T22. The archive records human review responsibilities, a code inspection pinned to `c56a05e` and engineering readiness by decision. All parameters await independent method review. [Parameter configuration](j3b-002-hybrid-block-methodology.md#5-contextual-exposure-envelopes-and-numerical-configuration-m02b) · [Decision procedure](j3b-002-hybrid-block-methodology.md#8-deterministic-candidate-decision-procedure) · [Worked programs and cases](j3b-002-hybrid-block-methodology.md#9-detailed-synthetic-worked-programs-and-conformance-cases) · [Review and readiness](j3b-002-hybrid-block-methodology.md#10-human-review-package-and-implementation-readiness)

### Block implementation-review considerations

1. Review cumulative load ceilings by movement. The proposed 5% upper-body and 10% lower-body block ceilings need movement-specific justification.
2. Assess the proposed aggregate ceiling of +2 weekly working sets across several developing movements. Keep separate movement and aggregate constraints and allow explicitly reviewed configurations for each.
3. Distinguish a target effort range from an approved execution cap. Worked program B calls RPE 9 a cap violation while specifying a 7–8.5 target without a separate cap. Resolve which limit governs the action before implementing it.
4. Record the calendar search domain and whether the search exhausted it. If a bounded search stops early, report that it found no feasible candidate among those examined. A claim of infeasibility requires exhaustion of the stated domain.
5. The planner is fixture-specific. General block representations, arbitrary weeks, movement groups and explicit block transitions need separate engineering work. Reuse the existing persistence and approval infrastructure and preserve replay of the original fixture.
6. Running time headroom reserves calendar space. Increasing prescribed running dose requires its own reviewed method and authority.

J3C.2 approval and operational release preparation are pending. J3A.3 turns next to running prescription and progression. Scheduled preliminary collection closed with Packet 010. [Curation roadmap](../research-backlog.md#hybrid-block-curation)
