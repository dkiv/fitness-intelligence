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

These questions belong to future method review. J3C.1 approval and operational release preparation are pending. Packet 010 closes scheduled preliminary collection. J3A.2 and J3B.2 will address multiweek block construction, protection of secondary outcomes and the corresponding practical method in a separate curation PR. [Curation roadmap](../research-backlog.md#strength-progression-curation)
