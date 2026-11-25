# Fitness Intelligence — J3A.1
## Bounded resistance-training progression in a hybrid program

**Revision:** 0.1 · **Date:** 2026-11-25 · **Status:** AI-assisted appraisal and candidate methodology; pending independent human review. Not an evidence release, implementation specification or operational authorization.

## 1. Executive summary

The first useful coach can make a bounded recommendation about the next lifting exposure from actual completed work, a recent comparable reference, the block objective and the existing running calendar. Optional anchored set RPE improves context but should not become a mandatory physiological readiness measurement. Productive training does not require automatic escalation of set count.

Six publications were selected: Plotkin (progression), Helms (effort-based loading), Halperin (effort-estimation validity), Hickmott (load-autoregulation synthesis), Barsuhn (habitual set dose), and Petré (concurrent scheduling). Five were inspected in full article text (including a repository copy of the Barsuhn version of record); Halperin was verified at publisher abstract level only. The latter remains a full-text verification blocker. No new publication is necessary merely to formulate the candidate methodology. No source, claim, method or transfer has been approved.

Key curation findings:

- Plotkin's directional contrast and 90% interval are correctly recorded. Repetition progression is a plausible alternative to load progression, not proof of equivalence or of an optimal double-progression algorithm.
- Helms's comparator was conditional rather than immutable. Hickmott includes the Helms trial and cannot be counted as a separate replication. Neither establishes superiority or equivalence of RPE-based loading.
- Halperin's signed average error is not an individual error bound, correction factor, or reliability estimate.
- Barsuhn's full article is available from Auckland University of Technology despite the publisher's 403 response. Its analysis used available data from all 55 allocated participants, not just the 29 completers. Table 3 shows unequal pre/post denominators; the approximately 32 kg control change is a difference of descriptive means, not a matched-person estimate. Some reported confidence intervals and p-values appear discordant and require clarification before quantitative use. A new pending source and claim revision is proposed.
- Petré supports considering separation of demanding lower-body and endurance sessions when strength is prioritized, but does not establish a universal recovery interval or an acute running-to-lifting causal rule.

Recommendation for J3B: review a simple, movement-specific progression policy and conservative set-dose/calendar policy together, with explicit missing-data behavior and athlete approval. Do not require wearables, maximal testing, physiological fatigue estimation, or randomized individual experimentation.

## 2. Selected coaching capability and scope

### Repository verification

Read-only snapshot: [`8fd767770ebe253e55a44ac5474cb53711b37002`](https://github.com/dkiv/fitness-intelligence/commit/8fd767770ebe253e55a44ac5474cb53711b37002), verified as `main` through GitHub comparison of main against itself on 2026-11-25. The research index was read on main; relevant draft fragments were then retrieved at the pinned SHA. The index contains Packets 001–008, including 007 after 008; it reports the combined 56 questions, 79 source revisions, 104 claim revisions, four relations and 30 methods (76 DOIs). These are repository-reported counts; this session did not run the manifest validator or independently enumerate all DOIs. No PR merge status is inferred beyond the presence of these files on main. Packets 009–010 were not present in the inspected index and are not prerequisites for this tranche.

Repository documentation consulted (full research index; targeted sections of the other documents; not a line-by-line audit of each archive):

- [Research index](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/README.md), [backlog](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/research-backlog.md), [methodology](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/methodology.md).
- [Scientific knowledge design](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/scientific-knowledge-design.md), [J1 catalog](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/scientific-evidence-catalog.md), [training plan design](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/training-plan-design.md), [evaluation design](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/coaching-evaluation-design.md).
- Exact staged JSON fragments: [001](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/drafts/001-evidence-additions.json), [002](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/drafts/002-evidence-additions.json), [003](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/drafts/003-evidence-additions.json), [006](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/drafts/006-evidence-additions.json), [008](https://github.com/dkiv/fitness-intelligence/blob/8fd767770ebe253e55a44ac5474cb53711b37002/docs/research/drafts/008-evidence-additions.json). The registered `petre@1` source key is confirmed via Packet 003 claim support; its exact registered source metadata was not separately retrieved. The remaining registered release and its approval state were not revalidated.

### Decision boundary

Given an approved block and next resistance session, actual recent lifting exposure, relevant running history and future commitments, propose hold, change load/reps, adjust local sets, redistribute a session, or defer/clarify. Do not construct a new block, modify running objectives, infer nutrition adequacy, prescribe rehabilitation or decide whether to race. Preserve approved constraints, secondary performance objectives and protected assessment sessions. This consolidates backlog A9/A13 (comparable work), A2/A11 (bounded progression), A4/A15 (calendar), and A3/A10/A12/A16 (reduction, conflict and authority), without marking those entire priorities complete.

| Capability | Priority for initial coach | J3A.1 coverage |
|---|---|---|
| Multiweek blocks | Essential | Consume existing block; construction deferred to next tranche. |
| Strength prescription | Essential | Primary focus: movement-specific next-exposure review. |
| Running prescription | Essential | Consume existing schedule; independent progression deferred. |
| Integrated scheduling/maintenance | Essential | Local conflict avoidance; maintenance-dose derivation deferred. |
| Recovery/history | Essential | Comparable execution, adherence, optional feedback; no latent readiness. |
| Nutrition | Essential at qualitative level | Respect restrictions and surface relevant questions; separate evidence/safety review. |

Early extensions: richer history comparisons, running field tests, operational logged maintenance intake, return from interruptions. Defer quantitative HRV, velocity-loss prescriptions, physiological expenditure estimation and event-specific taper optimization until a concrete decision warrants them.

## 3. Original-source verification and scientific appraisal

### Verification conventions

All source checks dated 2026-11-25. DOI/title/journal matched against publisher or archived journal record. Targeted DOI correction/erratum/retraction searches were performed; no relevant correction surfaced in the returned results. Only Hickmott's [Crossmark record](https://crossmark.crossref.org/dialog/?doi=10.1186%2Fs40798-021-00404-9) was directly confirmed as current. Other Crossmark/Crossref update relations, comprehensive retraction and rights checks remain outstanding; absence of a search result is not certification. No raw data, full supplementary analyses or primary-study reanalysis performed. Numeric estimates below are published results, not newly calculated sampling distributions; arithmetic differences are marked. No independent human review implied.

### S1 — Plotkin et al. (2022) · `plotkin@1` (P001)

*Progressive overload without progressing load? The effects of load or repetition progression on muscular adaptations.* PeerJ 10:e14142. DOI [10.7717/peerj.14142](https://doi.org/10.7717/peerj.14142). [Journal full text, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9528903/), 30 Sep 2022, CC BY. Inspected Methods (participants, training and measurements), Results/Table 1, Fig. 1 description and strength discussion/Fig. 3A locator.

- Trial: 43 volunteers, 27 men/16 women, mean age 23.1 years, mean lifting experience 3.8 years (SD 4.0). Block randomization 22 LOAD/21 REPS; 21/17 finished. Completer attendance approximately 95% in each arm. Eight weeks, twice-weekly lower-body training, four sets each of four movements. Baseline 10RM informed load; free-weight squat training, Smith squat maximal testing. ANCOVA adjusted for baseline and sex; 90% compatibility intervals.
- `load-vs-repetition-progression@1` original: both approaches improved Smith squat 1RM; adjusted contrast modestly favors load with uncertainty. Verified LOAD − REPS +2.0 kg (90% CI −2.4 to +7.8); descriptive changes +21.8/+19.3 kg. Table 1 uses the reverse sign. No extraction error identified. Unequal attrition, test specificity, variable experience, no equivalence design. Training-exposure dose trajectories and raw data not independently reconstructed.
- **Disposition:** retain after human review, study-specific scope. Direct to trained lower-body lifting; indirect to press or hybrid athlete. Supports two progression axes; not a mandatory increase after success, a particular step size or equivalence. Choice of axis remains programming judgment.

### S2 — Helms et al. (2018) · `helms-rpe-loading@1` (P008)

*RPE vs. Percentage 1RM Loading in Periodized Programs Matched for Sets and Repetitions.* Front Physiol 9:247. DOI [10.3389/fphys.2018.00247](https://doi.org/10.3389/fphys.2018.00247). [Publisher full text](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2018.00247/full), 21 Mar 2018, CC BY reported. Inspected Methods/loading protocol, Tables 1–4, results and discussion including realized intensity and volume.

- Counterbalanced trained men, 21 analyzed (percentage n=11, RPE n=10), ages 19–35; three weekly squat/bench sessions, eight weeks, matched assigned sets/reps in undulating programs. Percentage arm conditionally progressed following successful completion; RPE arm selected/adjusted load, with protocol-specific 2% per half-point outside target range. Bench relative intensity and volume load were higher in RPE arm; actual exposure was not identical. Full allocation/attrition and adherence reconstruction remains open.
- `rpe-load-squat-strength@1`: original improvement in both arms, no statistically significant group difference. RPE +17.05 ±5.44 kg vs percentage +13.91 ±5.89 kg (SD); ES 0.50 ±0.63 (90% CL, endpoints −0.13/+1.13); p=.32. `rpe-load-bench-strength@1`: +10.70 ±3.30 vs +9.64 ±5.36 kg; ES 0.28 ±0.73 (90% CL, −0.45/+1.01); p=.52. Table 4 confirms both. The paper's narrative post-test percentage-bench mean appears inconsistent with its reported gain and baseline (possible copy error); use reported change and verify raw values before any secondary extraction.
- **Disposition:** retain both after human review, retaining comparator caveat. Small sample, uncertain effects, magnitude-based probability interpretation not used as evidence of superiority; endpoints share participants. Direct to trained men and the lifts tested; concurrent schedule transfer untested. Supports practical use of effort targets alongside a planned load; exact adjustment increment is not independently validated. No automatic percentage-to-RPE conversion.

### S3 — Halperin et al. (2022) · `halperin-rir-accuracy@1` (P008)

*Accuracy in Predicting Repetitions to Task Failure in Resistance Exercise: A Scoping Review and Exploratory Meta-analysis.* Sports Med 52:377–390. DOI [10.1007/s40279-021-01559-x](https://doi.org/10.1007/s40279-021-01559-x). [Publisher abstract and task-failure note](https://link.springer.com/article/10.1007/s40279-021-01559-x); online 20 Sep 2021. Subscription blocks the final article body. [Preprint](https://doi.org/10.31236/osf.io/x256f) located but not treated as version-of-record evidence. Rights unverified.

- Healthy participants predicted remaining reps in a set subsequently taken to task failure. 16 eligible publications; 13 publications/12 studies (414 participants; 262 effects across 12 clusters) synthesized. Mixed experience. Exact allocations, adherence, individual exercise/protocol strata and model specification beyond abstract are not verified.
- `predicted-rir-signed-error@1`: original average underprediction. Main multilevel result 0.95 reps (95% CI 0.17–1.73), I²=97.9%. Training-status moderator interval includes zero. Signed mean permits cancellation of errors; it is neither absolute error nor an individual prediction interval. Different failure definitions compound ambiguity. Abstract result accurate.
- **Disposition:** require additional verification before human approval; retain abstract-only access. Useful as measurement caution, not as a treatment effect, longitudinal sensitivity or reliability study. No +1 RIR correction. No requirement to train to failure to obtain routine feedback. Full-text acquisition and exercise-specific applicability review needed before stronger quantitative use. A qualitative missing/noisy-effort safeguard need not depend on an approved numerical claim.

### S4 — Hickmott et al. (2022) · `hickmott-autoregulation@1` (P008)

*The Effect of Load and Volume Autoregulation on Muscular Strength and Hypertrophy: A Systematic Review and Meta-Analysis.* Sports Med Open 8:9. DOI [10.1186/s40798-021-00404-9](https://doi.org/10.1186/s40798-021-00404-9). [Journal full text, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8762534/), 15 Jan 2022, CC BY 4.0. Abstract, statistical analysis, Tables 1–2, load results/Fig. 2, discussion inspected; velocity-loss results consulted only for exclusion. Crossmark current at check.

- Fifteen studies total, six load comparisons (three subjective, three velocity-based), nine velocity-loss volume comparisons. Load studies 6–12 weeks, 2–3 sessions/week, sets matched, reps matched in four; mixed lifts and populations including adolescent rugby players. Fixed-effect model pools kg differences. Primary study adherence, correlated outcomes and covariance handling were not independently reconstructed.
- `autoregulated-load-pooled-one-rm@1`: original pooled estimate favors autoregulation, interval crosses zero. MD +2.07 kg (95% CI −0.32 to +4.46), SMD 0.21, p=.09. Subjective subgroup +3.15 kg (−0.14 to +6.45); objective +0.88 (−2.59 to +4.34); subgroup difference p=.35. Table 2 explicitly includes Helms. Neither superiority nor equivalence established; pooled kg effects across lifts, fixed-effect assumptions and nonidentical exposures constrain generalization.
- **Disposition:** retain after human review with explicit overlap and model caveats. Supports considering autoregulated loading, not requiring it. The `lower-velocity-loss-one-rm@1` and `higher-velocity-loss-csa@1` claims are outside this decision; defer rather than reinterpret velocity loss as weekly set count or RIR. Do not add their weight to the load claim.

### S5 — Barsuhn et al. (2025) · `barsuhn@1` (P002)

*Training volume increases or maintenance based on previous volume: the effects on muscular adaptations in trained males.* J Appl Physiol 138(1):259–269. DOI [10.1152/japplphysiol.00476.2024](https://doi.org/10.1152/japplphysiol.00476.2024), online 12 Dec 2024. [AUT institutional record](https://openrepository.aut.ac.nz/items/87b4d27e-50d0-4dd4-b652-1cf456281ded) and [journal PDF](https://openrepository.aut.ac.nz/server/api/core/bitstreams/4f83ffc5-1aad-4dc8-92fb-1c28156b3211/content) inspected, publication pagination and download footer match journal; institutional metadata identifies CC BY 4.0. Publisher direct full text blocked (403); final publisher abstract accessible. Methods pp. 260–264, Fig. 1/Table 1 p. 261, Results p. 265, Table 3 p. 266 and Discussion inspected; page images checked for key tables/CONSORT.

- Counterbalanced randomization CON/G30/G60 n=21/16/18, completers 10/10/9; young trained men, ≥3 years lifting, squat ≥1.5× body mass. Three-week self-reported habitual quadriceps sets; twice-weekly eight-week squat/leg press/extension. Table 1 prior/protocol set means 12.05/12.10, 14.47/18.80, 16.11/25.22 weekly. Table uses all baseline participants; these are not complete individual realized attendance trajectories. Total volume-load differences not detected. Four study-related injury dropouts, many COVID restrictions. Available-data mixed models include all 55; attrition remains substantial. Test depth standardized; reported squat typical error 8.32 kg (study-specific).
- `habitual-set-maintenance-strength@1` original: trained men maintaining habitual sets improved squat; no established difference in gains vs increases. Core interpretation supported, but pooled modeled time effect is +21.47 kg (reported 95% CI 21.27–21.66); descriptive control mean 161.90→193.70 kg (21 vs 10 observations), not a paired +31.80 kg. No significant group×time interaction reported. Baseline differences, group main effect, unequal denominators and unusually narrow intervals/discordant pairwise p-values (e.g. CON vs G30 15.6 kg, CI 12.8–18.5, p=.09) preclude treating reported group comparisons as reliable change contrasts. Different multiplicity methods may partly explain discordance; do not resolve by guessing. No direct difference-in-change CI established here.
- **Disposition:** revise source and claim before human review (Appendix A); quantitative CI interpretation requires statistical clarification. Direct to highly trained men and habitual quadriceps volume, indirect to upper-body or concurrent athletes. Supports the plausibility of maintaining a productive set dose, not a universal minimum, superiority of maintenance, or a feedback-driven weekly set rule. Load can still progress while set count stays fixed.

### S6 — Petré et al. (2021) · `petre@1` (registered source; P003 claims)

*Development of Maximal Dynamic Strength During Concurrent Resistance and Endurance Training in Untrained, Moderately Trained, and Trained Individuals: A Systematic Review and Meta-analysis.* Sports Med. DOI [10.1007/s40279-021-01426-9](https://doi.org/10.1007/s40279-021-01426-9). [Publisher full article](https://link.springer.com/article/10.1007/s40279-021-01426-9); inspected Methods inclusion/training status, §§3.1–3.5, Figs. 3–4 result locators, discussion. Rights and version-update review outstanding; exact registered source metadata not inspected.

- Randomized and nonrandomized comparisons of lower-body RT plus running/cycling vs identical RT alone; healthy 18–40-year-olds, endurance ≥2 sessions/week and >70% HRmax per eligibility. 27 studies (7 untrained, 10 moderate, 10 trained), 6–21 weeks overall; endurance 12–260 min/week. Some duration and variance inputs reconstructed by authors. Study-level training status and spacing; actual adherence not systematically extracted here.
- `same-session-trained-lower-body-strength@1`: original favors RT alone in trained same-session subgroup. ES −0.66 (95% CI −1.08 to −0.25). `separate-session-trained-lower-body-strength@1`: original uncertain near-zero estimate; ES −0.10 (−0.43 to +0.23), p=.55. Correct direction and precision. Same session <20 min; separate >2 h; subgroup-specific duration range not independently verified (overall 6–21 weeks). Neither contrast is a randomized comparison of spacing strata. Small studies, mixed modality, training-status ambiguity, confounding by program and dose. Do not infer interaction from significance pattern or exact recovery time.
- **Disposition:** restrict scope/clarify horizon as overall review range pending subgroup reconstruction; retain estimates after human review. Closest direct hybrid context in this tranche, but only chronic lower-body maximal strength, not upper-body, acute fatigue, running performance or a particular individual's response. Use as a reason to consider schedule conflicts; not proof of a compulsory separation or running reduction. Map overlap with Schumann/Huiberts before comparative synthesis; not done here.

## 4. Existing evidence-record corrections and proposed revisions

| Record(s) | AI-assisted recommendation | Reason / next action |
|---|---|---|
| `plotkin@1`, `load-vs-repetition-progression@1` | Retain after human review | Correct direction, interval level and test; no equivalence. |
| `helms-rpe-loading@1`, `rpe-load-squat-strength@1`, `rpe-load-bench-strength@1` | Retain after human review | Existing limitations already recognize conditional comparator; add Table 4 to review notes, verify anomalous narrative post-test mean. |
| `halperin-rir-accuracy@1`, `predicted-rir-signed-error@1` | Require additional verification | Final abstract matches; full article inaccessible. No numerical personal correction. |
| `hickmott-autoregulation@1`, `autoregulated-load-pooled-one-rm@1` | Retain after human review | Add explicit Helms overlap and fixed-effect model caveat in review/new revision if accepted. |
| `barsuhn@1`, `habitual-set-maintenance-strength@1` | Revise before human review | Full version now inspected; separate model and descriptive means; statistical uncertainty unresolved. Appendix A. |
| `petre@1`, `same-session-trained-lower-body-strength@1`, `separate-session-trained-lower-body-strength@1` | Restrict scope / verify before acceptance | Existing intervals match; subgroup horizon, underlying trial composition and registered source metadata remain open. |

Do not create new approval statuses. Existing claims remain pending. Draft revisions preserve original keys; eventual approval changes also require new exact revision keys and review. J1 forward supersedes edges belong to an explicitly reviewed replacement process, not this appraisal. The draft intentionally contains no supersedes edges or withdrawals. Existing method references are unchanged; if a replacement is accepted, review dependencies including `working-set-volume-review@1`, `bounded-hybrid-review-transition@1`, `recovery-aware-set-dose-review@1`, `task-specific-effort-adjustment@1`, `priority-aware-concurrent-calendar@1`. Other claims in these methods remain unappraised. A method cannot acquire approval by association with selected claims.

## 5. Applicability and transfer assessment

| Decision | Evidence type/directness | Transfer assumption and boundary |
|---|---|---|
| Load versus reps | One randomized lower-body trial | Similar movement/task and progression context; press transfer plausible, untested. |
| RPE-guided load | Small trained-male trial + overlapping synthesis | Anchored set effort, comparable execution and a usable planned target; no proven universal superiority. |
| Effort interpretation | Measurement signed-error synthesis, abstract | Subjective reserve is noisy; no personal calibration, repeatability or change threshold. |
| Maintain habitual set count | Trained-male randomized trial with attrition and statistical ambiguity | Habitual exposure is actually productive and tolerable; not a universal dose or a proof of no benefit from extra sets. |
| Protect concurrent quality | Chronic lower-body synthesis | Demanding local exposures may compete; schedule relevance and actual response matter. Not acute causal evidence. |

No full prospective trial establishes the integrated policy. These evidence types answer different questions. Do not count Helms plus Hickmott as two independent trials or squat and bench as independent cohorts. Do not combine pooled effect sizes across disparate estimands. Barsuhn is newer than Hickmott and addresses weekly set count, not velocity-loss-based intraset volume. The earlier Enes/Pelland dose claims remain relevant to later dose increases but not required to permit a hold; positive group results and a productive individual dose can coexist. This tranche does not establish physiological recovery time, optimal set count, causal fatigue, or a safe medical threshold.

## 6. Candidate practical coaching methodology

**Candidate J3-M01 v0.1**, pending, consolidating RT-P01, RT-P02 rev 0.2, CT-P01/02 rev 0.2, CT-P05, the phase-aware context of P006 and the recovery-aware workflow of P008. Not a J1 method record yet: a single programming design for J3B review, not a new operational rule. Three separable components: M01a movement progression, M01b set dose, M01c calendar/constraints.

### Observations, validity and readiness

| Observation | Minimum or optional | What it can establish / limitations |
|---|---|---|
| Approved plan version, block goal, priority/secondary outcomes, restrictions, next session and protected runs | Minimum | Decision authority and intended exposure, not actual work. |
| Dated actual sets, repetitions, external load/unit, movement variation/equipment, set kind and execution status | Minimum for quantitative lifting review | Observed external performance; not exact muscle stimulus or maximal strength. Normalize units and load convention; exclude warmups, duplicates and mismatched movements. |
| Recent comparable reference and recent completed exposure | Minimum for progression | Repeated comparable results are descriptive evidence of task performance. Effort, technique, rest, order, fatigue and context may confound. |
| Relevant running actual exposure and calendar | Minimum for integrated review; coverage qualified | Duration, distance, purpose/intensity if known and scheduling proximity; not physiological fatigue. Do not infer interval completion from summary or missing run as rest. |
| Anchored set RPE/RIR, rest, technique, local soreness, reason for incomplete work | Optional or targeted when decision changes | Subjective effort and context; RPE is not precisely known reserve, reliability or physiological readiness. Session exertion is not interchangeable with set RPE. |
| Standardized 1RM, validated velocity, detailed running intervals, sleep and fueling context | Optional, decision-specific | Potentially improves comparison; not required to recommend hold or modest progression. No wearable readiness score. |

Prescription: conditionally feasible from minimum canonical records (provider coverage and identity not verified in this session). Adherence: requires actual sets and matched plan version, plus reason when uncertain; distinguish confirmed/partial/missed/unknown. Effectiveness: later comparable performance, exposure, run quality and confounders; a before/after observation cannot isolate causal policy benefit. Scientific readiness: preliminary pending; operational readiness: deferred until reviewed method, evidence, validation and authority exist. Hevy/Garmin are possible provider inputs, not assumptions of complete data.

### Decision workflow

1. Pin approved plan, context, restrictions, evidence and eventual rule versions. Confirm session purpose (heavy, volume, technique, taper, recovery) and permitted changes. Stop or defer unsafe/excluded movements, new concerning symptoms or incompatible constraints; do not diagnose. A clinical restriction is not a generic fatigue signal.
2. Match actual sets to intended working sets using canonical movement/equipment, load convention, rep range, tempo/ROM, session role and order. Distinguish top set and backoffs. Verify duplicate-free units, completion and known rest differences. Unmatched or partial records can support descriptive context but not assumed full adherence.
3. Select most recent comparable exposures in the same phase; prefer last 2–3 usable exposures over an all-time best. Retain dates and explain exclusions. Use older recent exposure only if comparable, with declining relevance after interruptions. Do not use flat bench for incline, assisted reps for unassisted, different machines or all-time PR as current capacity. If no reference, request one or propose conservative re-entry under explicit bounds.
4. Compare matched set groups: at same load, reps and comparable effort; at same reps, load and comparable effort; or at same load/reps, change in anchored effort. Keep ordered set pattern and missed sets visible. Estimated 1RM, if separately reviewed, may be a secondary descriptive estimate with formula, rep/effort range and uncertainty, not a measured max or default.
5. Classify observations as compatible with improvement, stable/productive, uncertain, or possible deterioration. Lower effort on one day is suggestive; repeated comparable performance is stronger. A planned heavy/volume change is not a regression. A single miss can warrant a local conservative change without diagnosing fatigue. Ask why work was missed when it matters (time, equipment, pain, effort, logging).
6. Review actual completed working-set exposure over representative weeks, not merely prescribed volume. Count sets by movement and relevant muscle group separately; avoid assigning every compound set multiple additive totals without a reviewed counting convention. Compare with historical productive dose, adherence, performance direction and burden. Hold set count if progress is satisfactory. Consider a small set addition only if plateau against objective, sufficient completed exposure, tolerance, time and running priority permit; no requirement to add sets after success. Redistribute or reduce local exposure when burden/poor performance and schedule justify it.
7. Review actual recent and protected future running, local overlap (hard intervals, hills, long run vs squat/deadlift), timing, and athlete feedback. A run preceding a difficult squat is contextual, not causal evidence. Preserve important runs; prefer shifting/adjusting lower-body lifting or optional accessories rather than deleting a run. If primary/secondary goals conflict within all feasible alternatives, propose explicit block review, not unilateral sacrifice. Do not reduce upper-body work solely because a run was hard.
8. Select one primary change axis where feasible: hold, load, reps, sets, local reduction, redistribution. Prefer the smallest plausible intervention that fits the block. For absent RPE use demonstrated performance and conservative steps; if no evidence of spare capacity and next target exceeds demonstrated work, hold or ask. Missing RPE alone is not a failure signal. For actual safety concerns, defer affected exercise and suggest appropriate professional input.
9. Produce an explainable recommendation: baseline and matched observations; what changed and what did not; exact proposed delta and alternatives; uncertainty/missing observations; effect on commitments; rationale class (empirical premise, programming judgment, athlete preference, safeguard); follow-up observation. Separate observed facts from inferred explanations. Do not claim approved evidence for pending records.
10. Keep current prescription unchanged until trusted athlete approval of the specific new prescription. Allowed execution choices already within an approved range are recorded as execution, not a new plan. Protected-commitment changes require explicit block revision; restrictions and evidence eligibility are rechecked at approval. Decline, stale context or withdrawn support leaves current plan intact (flag any newly unsafe conflict). Record subsequent actual response and review, never retroactively alter historical execution links.

### Action selection

| Condition | Reasonable action | What not to infer |
|---|---|---|
| Consistent successful work, room within effort/rep range | Hold or modest progression of one axis | Exact strength gain or mandatory progression. |
| Comparable work improves at existing set count | Hold sets; progress load/reps if appropriate | Need for more sets, maximal adaptive stimulus. |
| One unusually high-effort session or missed rep | Hold, reduce local load/reps, or ask about cause | Global overtraining or need for deload. |
| Repeated local deterioration with confirmed adherence and contextual burden | Reduce local set count/load or redistribute; review if persistent | Causal running interference or exact recovery duration. |
| Plateau with good adherence, tolerability and no calendar conflict | Try modest load/reps change or small set addition, with review | Scientifically optimal dose, inevitable benefit. |
| Poor adherence or uncertain comparability | Resolve feasibility, simplify or hold | Physiological nonresponse from absent stimulus. |
| New restrictions, unsafe symptoms, conflicting constraints | Defer affected change; professional review if indicated | Diagnosis or clearance. |

Example: an athlete completed incline press 3×6×80 kg twice at reported last-set RPE 8, then 3×6×80 at RPE 7, with comparable technique/rest. A protected interval run and long run remain unchanged. A 1–2.5 kg total-load increment or holding at 80 kg to confirm are both reasonable candidates if in bounds; no extra pressing set is required. If RPE was unanchored, emphasize completed work and uncertainty. This example is synthetic, not personalized advice or an efficacy demonstration.

## 7. Proposed contextual numerical parameters and unresolved programming choices

All values are proposed initial **engineering/programming choices for J3B review**, not findings, universal thresholds or active rules. Select by block, movement, athlete's history and available equipment. A planned exposure, explicit restrictions and tighter approved bounds override these examples. No new physiological parameter is required.

| Parameter | Candidate starting choice | Justification, change trigger and limitations |
|---|---|---|
| Comparable history | Last 2–3 usable exposures, usually within 2–4 weeks; habitual sets from 3–4 representative completed weeks | Balances recency and sparse training; extend if low frequency, invalidate after major phase/equipment change or interruption; no minimum detectable change established. |
| Progression confirmation | Two comparable successful exposures preferred before increasing if effort missing/noisy; single clear success may justify already-planned progression | Conservative design, not a trial-derived gate. Do not force a wait if the approved plan specifies a suitable progression. |
| Load increment | Smallest available step, typically 1–2.5% for upper and 2–5% for lower movement, total external load; never round above cap | Practical increments, adjustable for heavy loads, microplates, rep targets and equipment; use reps or hold if smallest increment too large. Example 2.5 kg on 80 kg = 3.1%, not within a 2.5% cap unless explicitly authorized. |
| Repetition increment | +1 rep on one or selected working sets, within prescribed rep range | Preserve quality and rest; do not automatically increase all sets; at top of range consider load instead. |
| Effort target | Athlete/block-specific; example working range RPE 7–8, heavy exposure may have other approved range | Use an anchored set scale (10≈no reps left under intended execution); a ≥1-point repeated change is a contextual signal, not a validated MDC. No compulsory effort rating or exact RIR conversion. |
| High-effort/missed-rep fallback | Hold or decrease load by one available step (illustrative 2.5–5%) or one rep, within allowed bounds; consider stopping affected set if unsafe | Reversible local response; severe mismatch requires larger replan/deferral, not mechanical percentage reduction. No requirement to make up work. |
| Set adjustment | Hold by default when productive; candidate ±1 relevant working set/week after review, not automatic | More conservative than experimental 30–60% shifts; reassess after roughly 1–2 weeks for tolerability and several comparable sessions for performance; no dose efficacy claim. No increase if constraint or adherence problem dominates. |
| Calendar | Prefer different sessions/days for demanding lower-body and protected runs when feasible; inspect 24–48 h around key sessions as a scheduling window only | Not a minimum safe gap or individual recovery estimate. Adjust with schedule and actual local response, retain unaffected work. |
| Reassessment | Next comparable lift plus weekly block check; after any proposed change compare completion, performance and key run execution | Not a causal estimate. Avoid extrapolating across noncomparable work; revert/review if adverse or inconsistent response. |

J3B should specify approved units, rounding direction, movement-specific caps, effort anchors, minimum evidence for each change, time budget, calendar constraints, and a human-visible reason for exceptions. No universal weekly workload increase limit is asserted. Parameters should be versioned and evaluated against cases, then amended with review rather than silently learned from noisy observations.

## 8. Synthetic evaluation cases

All cases are artificial. Common constraints: approved block, no new injury except explicitly indicated, unchanged running commitments, one authorized owner, versioned plan. Every changed future prescription needs athlete approval (Y); hold without change does not (N). An already-approved execution range is not a new prescription. All cases require traceable baseline, reasoning class, uncertainty, scope and constraints. Test accepted action sets, not exact numerical optimization.

| ID / observations | Acceptable actions | Prohibited inferences | Required explanation / constraints | Approval |
|---|---|---|---|---|
| J3-01: 3×6×80 kg press at last RPE 8 twice, now 7; same rest/technique | Hold or small permitted load/rep increment | Exact +1 RIR or e1RM improvement | Cite comparable sets and effort uncertainty; protect planned runs and set count | Y if change |
| J3-02: 3×5 squat completed but RPE 9.5 vs target 7–8; no symptoms | Hold progression, local reduction or ask context | Systemic fatigue or required deload | Explain effort mismatch and compare recent exposures; keep other lifts unchanged | Y if change |
| J3-03: no RPE, 3×8×60 kg twice at top of approved 6–8 range; known completion | Hold or smallest bounded load increase with rep reset | RPE=0, exact reserve or refusal solely from missing RPE | Demonstrated work is usable, effort unknown; equipment rounding cap | Y if change |
| J3-04: press load improving for 3 weeks on 10 sets/week, run quality stable | Keep set count, maintain or progress load/reps | More sets required because adapting | Productive completed dose; extra sets not necessary for present objective | Y if change |
| J3-05: target 3×5, actual 5/5/3 at same load; last set stopped for effort | Hold or reduce local load/reps, ask if reason uncertain | All sets completed, failure always RPE 10, causal fatigue | Record partial completion and actual reps; no compulsory repayment | Y if change |
| J3-06: hard hill run yesterday, squat poor vs recent references, protected threshold run tomorrow; athlete reports local soreness | Move/reduce squat or accessories; preserve run; hold upper work | Proven interference, exact recovery hours, mandatory run cancellation | Local context vs chronic evidence; verify calendar constraints | Y if change; protected change requires block revision |
| J3-07: only one of three planned lifting days done for work travel; comparable completed set stable | Simplify/redistribute or hold; clarify availability | Nonresponder, low physiological capacity, double workload to catch up | Adherence problem not evidence of ineffective dose | Y if change |
| J3-08: old squat PR 180 kg, current repeated 5×130 kg after break; no recent max | Base on recent work, conservative resumption or ask targeted feedback | PR as current 1RM, exact percentage of current max | Explain staleness and phase difference; don't require max test | Y if change |
| J3-09: new painful press restriction since candidate generated | Defer affected press; offer review of permitted alternative or professional assessment | Diagnose injury or override restriction because old performance was good | Recheck current context at approval; stale candidate cannot activate | Y for feasible new plan; no approval for invalid candidate |
| J3-10: same-day key run and squat with no feasible separate slot; both protected, athlete declines proposed move | Hold current safe plan with conflict flag, offer explicit block review | Silently downgrade running or claim 2 h universally sufficient | Name incompatibility, preserve historical version and decline record | Y for any revised plan/block |

Additional regression assertions: duplicate import cannot double set exposure; kg/lb conversion must be explicit; missing execution cannot become zero; same record cannot be used as both a new observation and independent corroboration; changed restrictions, withdrawn dependencies, expired slots, and stale plan heads block activation; replay retains old evidence/rule/context versions; explanation must survive unavailable optional provider data. These cases test conformance and recommendation quality, not prospective physiological efficacy.

## 9. Human review decisions required

Use three grouped reviews rather than asking an athlete to adjudicate every record individually. Exact keys below are the traceability set; an independent qualified reviewer must record explicit revision-level decisions separately from athlete preferences and software authority.

| Review bundle | Empirical premises | Practical/numerical decisions | Limitations and unauthorized actions |
|---|---|---|---|
| M01a movement progression | `load-vs-repetition-progression@1`, `rpe-load-squat-strength@1`, `rpe-load-bench-strength@1`, `autoregulated-load-pooled-one-rm@1`; `predicted-rir-signed-error@1` only after additional verification | Comparable anchors, RPE optionality, rep/load bounds, confirmation and rounding | No superiority/equivalence claim, exact reserve, automatic changes, max prescription or failure tests. |
| M01b set dose | `habitual-set-maintenance-strength@1` / proposed `@2`, supported by respective `barsuhn` revision; other volume claims deferred | Hold productive sets, local reduction/redistribution, small set trial, review window | No universal set minimum/optimum, no causal fatigue diagnosis or +30% default; resolve uncertainty reporting first. |
| M01c concurrent context | `same-session-trained-lower-body-strength@1`, `separate-session-trained-lower-body-strength@1`, `petre@1`; use timing as context | Identify protected commitments, feasible spacing, local overlap, priority tradeoff and conflict handling | No universal spacing, no running deletion, no acute causal inference, no change of protected objectives without explicit block review. |

Factual verification tasks: compare DOI/version, result locator, signs, uncertainty, exact denominator and comparator; complete publication notices and rights; obtain final Halperin full text; verify Barsuhn statistical discrepancies and Petré subgroup composition; assess shared outcomes/trials. These are not athlete preference questions.

Scientific judgment: designated independent reviewer assesses claims, quality and explicit transfer to experienced recreational hybrid athletes; seek sports-science expertise for complex statistical interpretation, effect transfer and unresolved contradictory findings. A strength/endurance coach with relevant experience should review method choices, progression bounds, conflict handling and realistic examples. Athlete may choose objectives, preferred increments, schedule, feedback burden, and approve individual feasible prescription changes. A clinician should evaluate new concerning symptoms/injury restrictions; a sports dietitian or clinician should review nutritional safety and energy-availability boundaries in the nutrition tranche. Technical expertise can verify implementation and reproducibility but does not itself confer clinical or sports-science qualification.

Release sequence: factual verification → independent source/claim/transfer review with exact revision attestation → separate method and parameter review → full candidate manifest validation → synthetic case validation and approval-integrity tests → explicit operational authorization of immutable release/rule → athlete approval of specific future prescription. No attestation, release, repository modification or operational authorization has occurred here. If the Halperin numerical record cannot be approved, retain general measurement uncertainty as a conservative methodology decision without citing it as reviewed empirical evidence. If Barsuhn quantitative uncertainty remains unresolved, do not activate that quantitative claim; a separately reviewed practical choice to hold the dose can still be evaluated as such.

## 10. Recommended next curation tranche

**J3A.2: block construction and protected secondary outcomes.** Appraise only the smallest set needed to choose a block objective and maintain secondary exposures while developing the primary one. Start with Packet 006's outcome-specific maintenance candidates and Packet 003's scheduling context; choose sources after checking actual program comparators and habitual training. Include one direct acute local-fatigue comparison if it materially improves scheduling, with direction of exposure and measured endpoint explicit. Resolve overlap with Petré/Schumann/Huiberts if combining their claims. Avoid turning taper optimization into a prerequisite.

In parallel, J3B can prepare the three M01 review bundles and parameter decisions now, subject to open evidence checks. Then prioritize running progression/comparable outcomes (P005), nutrition/fueling (P004) and operational intake adaptation (P007); incorporate P009–010 when staged. Do not hold the full product hostage to advanced models. Do not treat this document as completion of the entire J3 backlog.

## Appendix A — Pending J1 draft fragment

This is a proposed additive fragment using the observed staged JSON field structure. Earlier revisions remain intact. No new source DOI, relation, withdrawal, approval or method record. The changed Barsuhn source has a new revision key; the changed claim links to it. The claim retains the original question/scope. The fragment is structurally modeled on the exact Packet 002 records but has **not been validated against the full `CorpusRelease`** or registered release. Check key availability and schema in the pinned candidate before integration. Do not activate the proposed records or edit existing methods to reference them without the review process.

```json
{
  "questions": [],
  "sources": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted J3A.1 appraisal)",
      "status": "pending",
      "approval": null,
      "key": "barsuhn@2",
      "citation": "Barsuhn A et al. Training volume increases or maintenance based on previous volume: the effects on muscular adaptations in trained males. J Appl Physiol. 2025;138(1):259–269.",
      "doi": "10.1152/japplphysiol.00476.2024",
      "record_url": "https://openrepository.aut.ac.nz/items/87b4d27e-50d0-4dd4-b652-1cf456281ded",
      "published_on": "2024-12-12",
      "design": "Counterbalanced randomized parallel-group trial",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Institutional copy of paginated journal article and publisher abstract checked. Direct publisher full text returned 403. No correction surfaced in targeted search; comprehensive notice check remains outstanding.",
      "rights": "Institutional metadata reports CC BY 4.0. Confirm version-specific and deployment rights; retain metadata, links and original summaries.",
      "appraisal": "Methods, Fig. 1, Tables 1 and 3, Results and Discussion inspected. 55 allocated, 29 completed; available-data mixed models included 55. Group main effect is not difference in change. Unusually narrow reported intervals and discordant pairwise p-values require clarification.",
      "next_review": "2027-02-24"
    }
  ],
  "claims": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted J3A.1 appraisal)",
      "status": "pending",
      "approval": null,
      "key": "habitual-set-maintenance-strength@2",
      "scope": {
        "question": "strength-dose",
        "objective": "strength-development",
        "population": "trained-adult-males",
        "experience": "trained",
        "intervention": "maintain-habitual-weekly-sets",
        "comparator": "increase-habitual-weekly-sets",
        "outcome": "back-squat-one-rm",
        "horizon": "eight-weeks",
        "block_context": "resistance-training"
      },
      "assertion": "In the trial of trained men, reported squat strength increased during the intervention including the habitual-set maintenance arm; a differential change between maintenance and volume increases was not established.",
      "limitations": "55 allocated and 29 completed; differing pre/post denominators; baseline imbalance; no significant group-by-time interaction reported; uncertainty reporting requires clarification; not equivalence, optimal dose or hybrid transfer.",
      "quality": "low",
      "assessment": "Full journal copy inspected. Retain qualitative interpretation provisionally; verify mixed-model uncertainty, missingness and pairwise contrasts before approval.",
      "transfers": [],
      "support": [
        {
          "source": "barsuhn@2",
          "locator": "Results, Maximum Strength and Strength Endurance, p. 265; Table 3 p. 266; Discussion pp. 266–267; Fig. 1 p. 261",
          "result": "Reported model time effect +21.47 kg (95% CI 21.27 to 21.66, as printed; requires clarification). Control descriptive means 161.90 to 193.70 kg with n=21 and n=10 respectively. No significant group-by-time interaction reported. Direct difference-in-change interval not verified.",
          "restriction": "Descriptive means with unequal denominators are not paired individual changes. Do not infer superiority or equivalence, individual set threshold or quantitative prescription."
        }
      ]
    }
  ],
  "relations": [],
  "methods": [],
  "withdrawals": []
}
```

**Open validation items:** confirm revision keys are unused; validate strict manifest with registered release and all staged fragments; verify source notices and rights; adjudicate statistics; review transfer and dependent methods. No automatic supersession.
