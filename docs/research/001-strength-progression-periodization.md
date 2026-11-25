# Fitness Intelligence — Research packet 001

**Strength progression, longitudinal periodization and concurrent endurance maintenance**  
Date: 2026-11-24 | Revision: 0.1 | Status: **Draft — pending independent human review**  
Repository: [dkiv/fitness-intelligence](https://github.com/dkiv/fitness-intelligence)  
Research questions: RT-01, RT-02, LP-01; contextual evidence from CT-01 and CT-02.

## 1. Executive summary

**Purpose.** Consolidate the initial research discussion into a reviewable specification input for Fitness Intelligence, an adaptive strength-and-running coach. The first coach must generate and revise seven-day prescriptions within a multiweek block, preserve secondary training objectives, explain decisions and obtain athlete approval. This packet concerns experienced recreational resistance-trained athletes with endurance training histories, initially considering 6–12-week strength-specialization blocks. The horizon is a research scope, not a validated prescription. Primary outcome: strength in the prioritized lift. Secondary outcomes: endurance retention, non-priority strength retention, adherence and fatigue burden.

**Main findings and proposed implications:**

- Periodized training may modestly improve maximal strength relative to constant training at equivalent volume. Undulating programming is plausible for trained lifters, but the subgroup estimate is imprecise and the overall finding is sensitive to study composition. A broader 2026 ACSM overview does not find consistent effects of periodization across outcomes. Do not hard-code one optimal periodization scheme.
- Load and repetition progression both improved strength in a small randomized lower-body study; the between-group advantage for load progression was uncertain. Permit either as a candidate action, while retaining movement-specific heavy exposure when justified by the strength objective.
- Fixed increases in weekly set volume improved lower-body strength compared with constant volume in two small trials of trained adults. Higher cumulative dose was not isolated from the progression pattern. Dose-response models suggest diminishing returns. None of this validates an automatic feedback-triggered increase in sets; maintaining a successful dose must be an available decision.
- Concurrent-training effects depend on the population, outcome and protocol. A mixed-population meta-analysis found a near-zero mean maximal-strength difference, while a trained lower-body subgroup showed smaller gains with concurrent training. Do not generalize either result to all running/press combinations or infer a universal spacing interval.
- Endurance maintenance is an outcome, not a session count. Reduced-dose maintenance evidence in general populations is indirect for experienced athletes. Initialize secondary training goals using the athlete's own history and monitor the outcome of interest.
- Subjective monitoring and nocturnal heart-rate observations provide context, not validated adjustment triggers. A cessation-style deload trial does not establish the effectiveness of reduced-volume deloading or event tapering.

**Repository implications.** Retain the separation between empirical claims, methods, individual observations, constraints and engineering safeguards. Keep the planner deterministic and the LLM explanatory; never allow an LLM to approve a revision. The existing `j1-screening-1` release contains six sources, five pending claims, one qualification and one pending method; no independently approved claims. Its operational retrieval gap is intentional. E1/E2's five-to-six-set progression, 24-hour spacing and prohibition on simultaneous load/set increases are synthetic parameters, not evidence-based defaults. Do not replace them with new unvalidated numerical thresholds.

**Provenance and review boundary.** This is a consolidation, not a new systematic review. The preceding targeted search (2026-11-24) used PubMed, publishers and accessible original-paper copies; search concepts covered load versus repetitions, weekly set progression, volume-equated periodization, dose-response, maintenance, concurrent training and deloads. The original discussion reported full-text access for Moesgaard and Plotkin; this packet rechecked the J1 manifest and schema and selected bibliographic/result details for the same publications only. Plotkin's table and the abstracts of the Enes trials, Pelland, Currier 2026, Spiering and Coleman were checked; Moesgaard's reported subgroup values were checked against the abstract, not its updated full-text tables. Existing J1 results are carried forward from the catalog rather than independently re-extracted here. No comprehensive search update, duplicate extraction, formal risk-of-bias appraisal or complete publication-status/rights check was performed. Confidence ratings below are provisional judgments, not formal GRADE ratings. No human approval, repository changes or operational release are implied.

Repository references: [product vision](https://github.com/dkiv/fitness-intelligence/blob/main/docs/product-vision.md), [coaching science](https://github.com/dkiv/fitness-intelligence/blob/main/docs/coaching-science.md), [knowledge design](https://github.com/dkiv/fitness-intelligence/blob/main/docs/scientific-knowledge-design.md), [catalog guide](https://github.com/dkiv/fitness-intelligence/blob/main/docs/scientific-evidence-catalog.md), [training plan design](https://github.com/dkiv/fitness-intelligence/blob/main/docs/training-plan-design.md), [evaluation design](https://github.com/dkiv/fitness-intelligence/blob/main/docs/coaching-evaluation-design.md).

## 2. Scientific evidence table

### 2.1 Strength and periodization

Each row is a distinct finding or review-level conclusion, not a prescription. CI = confidence interval; CrI = Bayesian credible interval; ES/SMD = standardized effect size/mean difference; 1RM = one-repetition maximum. Abstract locators identify exactly the accessible result but do not substitute for full-text appraisal. A missing effect estimate is deliberately not imputed. Evidence IDs (E01–E14) are local packet references, not catalog keys.

| ID / scientific claim | Publication and DOI | Exact result locator / access | Population; intervention vs comparator; horizon | Effect and uncertainty | Limitations | Applicability to experienced hybrid athletes | Proposed confidence / review status |
|---|---|---|---|---|---|---|---|
| E01 — Heavy multiset resistance training improved strength compared with inactivity. | Currier et al. 2023, *Br J Sports Med*, 57:1211–1220. [10.1136/bjsports-2023-106807](https://doi.org/10.1136/bjsports-2023-106807) | Results, Fig. 3A, HM3 vs CTRL (existing J1 extraction). | Healthy nonathlete adults, mixed experience; supervised heavy (≥80% 1RM), multiple sets, ≥3 days/week vs no exercise; ≥6 weeks. | Posterior SMD 1.60 (95% CrI 1.38–1.82). | Indirect network contrasts; within-study bias; most active comparisons less clearly distinguishable. | Indirect; cannot select starting load, frequency or increments for an experienced athlete. | Moderate for contrast; low for transfer. Existing pending claim; appraise, lower implementation priority. |
| E02 — Volume-equated periodization favored 1RM strength compared with non-periodized training. | Moesgaard et al. 2022, *Sports Med*, 52:1647–1666. [10.1007/s40279-021-01636-1](https://doi.org/10.1007/s40279-021-01636-1) | Abstract, Results, first comparison; prior review identifies §3.2.1. Full-text locator/updated tables require confirmation. | Mixed training experience; periodized vs non-periodized, volume equated; intervention endpoints (contrast-specific duration range outstanding). Review included 35 studies overall. | ES 0.31 (95% CI 0.04–0.57). | Heterogeneous protocols, trial quality, endpoint specificity; equating volume does not equate all other training features. | Indirect; supports considering variation but not a particular block sequence. | Low for hybrid transfer; pending draft. |
| E03 — Undulating vs linear programming favored 1RM in the pooled estimate and trained subgroup, with uncertainty. | Moesgaard et al. 2022, same DOI as E02. | Abstract, Results, LP vs UP and training-status subgroup; prior review identifies §3.3.1 and Fig. 4 (figure number not reverified). | Mixed and trained/untrained subgroups; volume-equated undulating vs linear programs; trial endpoints, exact subgroup durations outstanding. | Overall ES 0.31 (95% CI 0.02–0.61); trained 0.61 (0.00–1.22); untrained 0.06 (−0.20–0.31). Prior appraisal reports I²=70% overall; excluding one influential study reduced ES to 0.15 and I² to 0% (verify full-text sensitivity analysis). | Small/imprecise subgroup; heterogeneity; mean modified PEDro score previously reported as 4.8 (verify scale and extraction). No pooled block-periodization comparison in prior appraisal. | Indirect; trained subgroup is relevant but no demonstrated hybrid-specific advantage; subgroup significance is not evidence of interaction. | Low; pending draft; sensitivity and subgroup extraction need review. |
| E04 — Across a broad overview of reviews, periodization did not consistently influence training outcomes. | Currier et al. 2026, ACSM position stand, *Med Sci Sports Exerc*, 58:851–872. [10.1249/MSS.0000000000003897](https://doi.org/10.1249/MSS.0000000000003897) | Abstract, Results, concluding sentence on prescription variables. [Original record](https://pubmed.ncbi.nlm.nih.gov/41843416/). | Healthy adults; 137 systematic reviews of RT vs inactive or alternative RT programs overall; trials 6–52 weeks. Search through Oct 2024. | No single periodization effect estimate in abstract; inconsistency is not equivalence. | Broad population and outcome aggregation; overlap with Moesgaard; review-level quality and exact comparison-specific results need appraisal. | Contextual counterweight to E02–E03, not an independent replication or categorical refutation. | Low for hybrid-specific decision; screening. |
| E05 — Both load and repetition progression improved Smith-machine squat 1RM; the comparative advantage was uncertain. | Plotkin et al. 2022, *PeerJ*, 10:e14142. [10.7717/peerj.14142](https://doi.org/10.7717/peerj.14142) | Results, Strength; Table 1, squat 1RM row; Fig. 3A. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9528903/). | 43 randomized, 38 completed (21 LOAD, 17 REPS); ≥1 year consistent lower-body RT; load progression at constant repetition range vs repetition progression at constant load; two lower-body sessions/week, 8 weeks. | Unadjusted changes +21.8 kg LOAD, +19.3 kg REPS. Adjusted LOAD minus REPS +2.0 kg (90% CI −2.4 to +7.8); Table 1 uses the opposite sign. | Small study, unequal attrition, short follow-up, no equivalence test, movement-specific outcome, no controlled endurance co-intervention. | Indirect; supports considering both strategies, not a double-progression trigger or a press-specific increment. | Moderate for study-specific estimate, low for policy transfer; pending draft. |
| E06 — Prescribed increases in weekly sets produced greater back-squat 1RM improvements than constant sets in trained men. | Enes et al. 2024, *Med Sci Sports Exerc*, 56:553–563. [10.1249/MSS.0000000000003317](https://doi.org/10.1249/MSS.0000000000003317) | Abstract, Methods and Results, 1RM comparisons. [PubMed](https://pubmed.ncbi.nlm.nih.gov/37796222/). Full-text results outstanding. | 31 trained men, mean experience 5.1 years; +4 or +6 weekly lower-limb sets every two weeks vs constant sets; 12 weeks. | Both progression arms favored over constant (reported p=0.023 and p<0.0001, respectively); numerical magnitude/CI not extracted. Hypertrophy differences uncertain. | Small groups; cumulative dose differs; fixed schedules, not adaptive increases; hypertrophy endpoints distinct. | Indirect for press specialization and concurrent running; trial doses are not recommendations. | Low; screening-level evidence; pending claim draft only. |
| E07 — Set progression improved leg-press 1RM relative to constant sets in trained women. | Enes et al. 2025, *J Sports Sci*, 43:381–392. [10.1080/02640414.2025.2459003](https://doi.org/10.1080/02640414.2025.2459003) | Abstract, 1RM comparison results. [Publisher](https://doi.org/10.1080/02640414.2025.2459003). Full-text results outstanding. | 30 trained women, mean experience 2.1 years; +2 or +4 weekly sets every two weeks vs constant sets; 12 weeks. | Both progression arms favored over constant (p=0.032 and p<0.001); between progression arms p=0.118. Magnitudes/CIs not extracted. Hypertrophy findings varied by measurement. | Small groups; cumulative dose differs; different lift and cohort from E06; no equivalence inference from non-significant contrast. | Indirect; does not establish an individualized volume algorithm or sex-specific rule. | Low; screening-level evidence; pending claim draft only. |
| E08 — Dose-response models suggest greater strength and hypertrophy gains with higher volume, with diminishing returns more pronounced for strength. | Pelland et al. 2026, *Sports Med*, 56:481–505. [10.1007/s40279-025-02344-w](https://doi.org/10.1007/s40279-025-02344-w) | Abstract, Results, volume marginal slope and best-fit model statements. [PubMed](https://pubmed.ncbi.nlm.nih.gov/41343037/). | 67 studies / 2,058 participants overall; meta-regression across different weekly doses, accounting for training status and duration; direct/indirect sets distinguished. | Positive marginal slope supported by fitted models; numerical curve estimates and uncertainty at particular doses not extracted. | Study-level dose associations, heterogeneity, model/measurement assumptions; no individual optimum or fatigue-cost curve established. | Indirect; useful for framing dose tradeoffs, not for choosing set ceilings or increases. | Low for individual policy; screening. |

### 2.2 Concurrent training, maintenance and recovery

| ID / scientific claim | Publication and DOI | Exact result locator / access | Population; intervention vs comparator; horizon | Effect and uncertainty | Limitations | Applicability to experienced hybrid athletes | Proposed confidence / review status |
|---|---|---|---|---|---|---|---|
| E09 — Mean maximal-strength gains were close between concurrent and strength-only training in mixed samples. | Schumann et al. 2022, *Sports Med*, 52:601–612. [10.1007/s40279-021-01587-7](https://doi.org/10.1007/s40279-021-01587-7) | Results §3.2, Fig. 2, pooled random-effects result (existing J1 extraction). | Healthy adults, mixed experience; supervised aerobic + resistance vs identical resistance alone; ≥4 weeks; 37 studies for maximal strength. | SMD −0.06 (95% CI −0.20 to 0.09). | Mean PEDro 4.3/10 per J1; protocol heterogeneity; small adverse effects compatible; equivalence not tested. Explosive strength is a separate endpoint. | Indirect; cannot infer absence of interference for a specific athlete or prescribe timing. | Moderate for pooled contrast; low for individual transfer; existing pending claim. |
| E10 — Trained subgroup showed smaller lower-body 1RM gains when endurance was added. | Petré et al. 2021, *Sports Med*, 51:991–1010. [10.1007/s40279-021-01426-9](https://doi.org/10.1007/s40279-021-01426-9) | Results §3.4, Fig. 2, trained subgroup (existing J1 extraction). | Healthy adults 18–40, structured training; running/cycling >70% HRmax ≥2 times/week plus RT vs identical RT alone; 6–21 weeks overall. | ES −0.35 (95% CI −0.59 to −0.11). | Small short studies, some nonrandomized comparisons, study-level training classifications, shared trials with E09. | More relevant for demanding lower-body concurrent training; indirect for easy runs, upper-body presses or elite athletes. | Low; existing pending claim; appraise jointly with E09. |
| E11 — Narrative review suggests some performance qualities can be preserved at reduced dose if intensity is maintained. | Spiering et al. 2021, *J Strength Cond Res*, 35:1449–1458. [10.1519/JSC.0000000000003964](https://doi.org/10.1519/JSC.0000000000003964) | Abstract, general-population maintenance findings and statement of insufficient athlete-specific data. [PubMed](https://pubmed.ncbi.nlm.nih.gov/33629972/). | General populations; reduced exercise volume/frequency with intensity retained vs prior training exposure, across varying durations and outcomes. | No single pooled comparative effect or interval; individual protocols not extracted. | Narrative synthesis; limited data for athletes; VO₂max, threshold, economy, race performance and tolerance of long runs not interchangeable. | Indirect only; no universal minimum dose for experienced hybrid athletes or particular non-priority lifts. | Low; screening/contextual synthesis, not an individual dose claim. |
| E12 — Subjective well-being measures worsened with acute increases in training load. | Saw et al. 2016, *Br J Sports Med*, 50:281–291. [10.1136/bjsports-2015-094758](https://doi.org/10.1136/bjsports-2015-094758) | Results, Table 7, acute-load-increase column and accompanying result (existing J1 extraction). | Athletes, mixed experience; acute load increase vs prior load; variable durations. | Moderate-to-strong impairment evidence for 13 subjective measures under review's rating scheme; no common effect estimate. | Measures are not independent studies; instruments and sports vary; confounding by other stressors. | Supports gathering subjective feedback; does not validate deload triggers. | Low; existing pending claim. |
| E13 — Nocturnal HR changes differed between post hoc overload-response groups. | Nuuttila et al. 2024, *Eur J Sport Sci*, 24:857–869. [10.1002/ejsc.12115](https://doi.org/10.1002/ejsc.12115) | Results §3.3, Fig. 3C, baseline to overload week 2 (existing J1 extraction). | Recreational runners; running overload; overreached vs responder groups; two-week overload. | Between-group change p=0.002; opposite mean directions, no significant within-group HR change; magnitude/CI not extracted. | Small subgroups, readiness used in classification, dropout/unclassified finishers, no prospective predictive validation. | Indirect; no individual nightly HR threshold or demonstrated benefit of adjustment. | Low; existing pending claim; defer trigger development. |
| E14 — One week of resistance-training cessation mid-program yielded smaller lower-body strength improvements than continued training. | Coleman et al. 2024, *PeerJ*, 12:e16777. [10.7717/peerj.16777](https://doi.org/10.7717/peerj.16777) | Abstract, Results, isometric and dynamic lower-body strength comparisons. [PubMed](https://pubmed.ncbi.nlm.nih.gov/38274324/). | Resistance-trained participants; cessation for one week midway through a nine-week program vs continuous training. | Direction favors continuous training; magnitude/CIs not extracted in this packet. | Cessation differs from reduced volume or intensity; no evidence here for readiness-triggered deloads or pre-event tapering. | Indirect; cautions against assuming every planned deload is beneficial, not against all deloads. | Low for hybrid/other deload strategies; screening. |

**Synthesis constraints:** E02 and E03 share studies and E04 includes overlapping syntheses; do not count them as independent votes. E09 and E10 share primary trials (including Robineau et al. 2016, per J1); retain `trained-subgroup-boundary@1` as a qualification, not a contradiction or pooled re-estimate. Study outcomes, intervals and confidence labels are not interchangeable. E06/E07 cannot distinguish added cumulative volume from escalation as a temporal strategy. None of E01–E14 validates the full adaptive policy below.

## 3. Candidate coaching policies

**Common contract.** All policies are unapproved candidates, not executable operational parameters. Required shared inputs: confirmed goals and ranked objectives, block phase and horizon, dated restrictions, availability/equipment, approved prescription and execution bounds, comparable performance with provenance, adherence/coverage, athlete feedback, secondary exposures, applicable evidence/review state. Missing records are unknown, not zero or missed. Hard restrictions and safety constraints override progression. New/worsening pain, illness or incompatible restrictions require appropriate review and possibly deferral rather than routine escalation. Every proposal must be feasible, versioned, attributable to rule/parameter and evidence versions, and explicitly approved by the athlete; permitted in-session choices within the approved range are distinct from a prescription revision.

### RT-P01 — Load and repetition progression

| Field | Specification |
|---|---|
| Decision | Increase load, increase reps, hold, or reduce difficulty on a comparable movement. |
| Required inputs | Confirmed completed sets, movement/equipment/load-convention identity, actual load/reps, prescribed rep range and effort target, reported RPE/RIR and reliability, recent comparable performance, smallest available load increment, phase and bounds. |
| Proposed logic | Check restriction, data quality and phase first. If comparable work is successfully completed within intended effort and progression advances the objective, consider reps within the prescribed range; when the upper rep target is achieved at target effort, consider the smallest feasible load increment and appropriate reps within approved limits. Recognize progress at unchanged load; if effort exceeds target or response is uncertain, hold, reduce or request feedback. Do not increase by default. |
| Supporting evidence | E05 supports viability of either progression strategy, not the branch logic. E01 is contextual evidence for heavy training, not a direct active-dose comparison. |
| Programming judgment | Double progression, retaining periodic heavy movement-specific exposure, effort-based eligibility, increments and comparison windows. |
| Assumptions / limitations | RPE/RIR and movement mapping are reasonably comparable; gains in reps can reflect factors besides strength; no validated optimal progression trigger or effort tolerance. |
| Do not apply | Incompatible equipment/load mapping, inferred-only or missing completion, unreliable effort ratings, relevant injury/illness, phase-specific assessment/taper restrictions, increments outside the envelope. |

### RT-P02 — Working-set volume adjustment

| Field | Specification |
|---|---|
| Decision | Increase, maintain or reduce the priority movement's exposure. |
| Required inputs | Prior and recent confirmed working-set counts and definitions, direct/indirect exposure, adherence, performance trend and uncertainty, effort, fatigue feedback, secondary training exposure, objective, phase, time and approved bounds. |
| Proposed logic | If current dose supports progress and goals, maintaining it is admissible. If a credible plateau occurs despite adherence, comparable measurements and tolerable recovery, evaluate additional volume as one option alongside specificity and exercise selection. If fatigue or other commitments constrain the objective, consider holding/reducing or revising schedule. Do not treat positive feedback or a plateau alone as sufficient for escalation. |
| Supporting evidence | E06–E08 suggest dose can matter; fixed escalation trials do not isolate adaptive escalation or cumulative dose. E12 contextualizes feedback collection. |
| Programming judgment | Favor smallest feasible changes when warranted; avoid unnecessary work; decide how to count direct/indirect sets and manage competing training. A restriction on concurrent set/load increases is an optional engineering safeguard, not an empirical finding. |
| Assumptions / limitations | No established individual optimal volume, marginal recovery cost, plateau duration, increment, ceiling or escalation frequency. Adherence and fatigue may be confounded. |
| Do not apply | Insufficient exposure data, noncomparable set definitions, poor adherence, new restrictions, or a protected peak/taper when increasing work would violate the objective. |

### CT-P01 — Protect non-priority qualities

| Field | Specification |
|---|---|
| Decision | Set and revise secondary endurance and lifting exposure during strength specialization. |
| Required inputs | Historical modality, duration, intensity, frequency, endurance performance measures and conditions; non-priority lift exposure/performance; goal hierarchy, constraints, current strength load, feedback and event calendar. |
| Proposed logic | Define the actual performance quality to retain. Initialize a conservative, feasible secondary prescription relative to established exposure; preserve approved exposure constraints and monitor performance with uncertainty. If secondary outcome declines credibly, investigate causes and propose a schedule or block review rather than silently abandon it. If history is missing, request context or label a provisional rules-only plan. |
| Supporting evidence | E09–E11; maintenance evidence is indirect and interference outcomes differ. |
| Programming judgment | Which qualities to maintain, intensity exposure, tradeoff with specialization, floor/ceiling, how to monitor retention. |
| Assumptions / limitations | No validated minimum endurance or non-priority lifting dose for the target population; maintaining session count need not maintain performance. |
| Do not apply | No feasible way to honor competing objectives; secondary race goal is incompatible with strength emphasis; unreliable outcome measurements or injury restrictions. Escalate for explicit objective review. |

### CT-P02 — Concurrent-session organization

| Field | Specification |
|---|---|
| Decision | Retain or move a run/lift when a scheduling conflict or repeated performance concern appears. |
| Required inputs | Session modality, intensity and timing, objective priority, comparable lifting/running outcomes, athlete-reported interference, available alternative slots, approved spacing and event restrictions. |
| Proposed logic | Prefer feasible arrangements that protect high-priority work; if a demanding run repeatedly precedes poorer lower-body lifting with attributable feedback, consider moving it as a trial while retaining the block's objectives. Record before/after schedule, hypothesis and planned observations. If no feasible arrangement exists, report the conflict. |
| Supporting evidence | E09–E10 suggest outcome- and population-specific concurrent effects; neither establishes individual timing or causation in observational histories. |
| Programming judgment | Schedule selection and priority protection; any spacing parameters are separately approved constraints. |
| Assumptions / limitations | Schedule changes may affect sleep, nutrition, adherence or other confounders. No universal hour-based spacing rule. |
| Do not apply | Single noisy observation as sole justification, incomparable performance, infeasible alternative, or a change that violates protected days/secondary commitments without block review. |

### LP-P01 — Phase-aware adaptation

| Field | Specification |
|---|---|
| Decision | Determine whether to progress, maintain, reduce or revise a week/block relative to its purpose. |
| Required inputs | Approved cycle, block objective, current week intent, assessment/event dates, progression envelope, preceding approved prescriptions, outcomes and athlete feedback. |
| Proposed logic | Evaluate restrictions and reliable exposure first. During accumulation consider productive exposure; during intensification consider specificity/load; during fatigue reduction or peak avoid unnecessary additional work. Retain the objective if feasible. A changed goal or phase intent requires explicit block revision. |
| Supporting evidence | E02–E04 support considering structured variation, but do not establish the exact phase transitions. E05 informs candidate progression mechanisms. |
| Programming judgment | Selection of phase, length, emphasis, and weekly progression; multiple feasible methods are acceptable. |
| Assumptions / limitations | Block dates and measures are agreed; fixed phase timing is not empirically validated; a dedicated peak is optional for long-term general strength. |
| Do not apply | New event priority, injury or infeasible objective invalidates block assumptions; do not force a scheduled phase transition or rewrite completed prescriptions. |

### LP-P02 — Recovery, deload and assessment protection

| Field | Specification |
|---|---|
| Decision | Hold, reduce or defer work, or preserve planned recovery/assessment intent. |
| Required inputs | Recent comparable performance, effort/adherence, subjective fatigue and symptoms, available recovery signal coverage, upcoming assessment/event and approved constraints, athlete feedback. |
| Proposed logic | Distinguish planned recovery, reactive fatigue management, cessation and tapering. Missing or isolated noisy recovery observations do not themselves authorize a change. If fatigue concerns converge, investigate and consider a conservative reduction or feedback request. Do not automatically catch up missed work before protected assessment days. |
| Supporting evidence | E12–E14. E14 tests cessation rather than lower-dose deloads; none validates a trigger or taper protocol. |
| Programming judgment | Which training component to reduce, whether to retain intensity, duration and return strategy; assessment protection is an objective-based safeguard. |
| Assumptions / limitations | Fatigue cannot be reliably identified from a single signal; deload timing and magnitude remain unresolved. |
| Do not apply | As an automated clinical diagnosis or as a generic readiness threshold; severe/persistent symptoms, restrictions, or uncertain safety require separate review. |

**Implementation boundary:** These policies are semantic proposals, not fully specified deterministic functions. Exact effort targets, increments, observation windows, dose floors/ceilings, spacing, taper and deload parameters require separate review and versioning. Do not translate qualitative conditions into arbitrary constants or let a language model choose them silently. A rules-only draft must disclose an evidence gap; a recommendation requiring an empirical premise must defer when no eligible claim supports it.

## 4. Periodization methodology

**Evidence vs methodology.** E02–E04 motivate comparison of structured variation against constant/alternative programming, with uncertain relative benefits. Linear progression across weeks and undulating session exposures can coexist inside a block with changing priorities. The evidence does not show that a particular eight-week sequence, weekly split, escalation curve or phase-transition schedule is optimal. Concurrent-training and maintenance evidence (E09–E11) qualifies secondary-objective choices without defining a running-development or maintenance algorithm.

### 4.1 Candidate eight-week strength-specialization block (illustrative only)

| Phase (example timing, not a threshold) | Priority strength | Endurance and non-priority lifting | Adaptation / transition |
|---|---|---|---|
| Weeks 1–3, accumulation | Establish tolerable exposure, comparable observations and work capacity; vary session emphasis if useful. | Maintain agreed secondary exposure relative to history; assess feasibility. | Progress or hold as warranted; do not require automatic set increases. |
| Weeks 4–6, intensification | Increase movement specificity and relative loading where justified; adjust volume to observed response. | Protect the agreed maintenance objective and manage scheduling conflicts. | Use comparable performance/effort, not calendar alone, to assess whether change is appropriate. |
| Week 7, fatigue reduction | Avoid unnecessary fatigue; retain relevant movement exposure if appropriate. | Adjust only within the approved objective/constraints or seek explicit revision. | A planned reduced-dose phase is a method, not established by cessation evidence. |
| Week 8, assessment | Standardized performance assessment, or ordinary training review if no peak is needed. | Record retention measures and uncertainty; avoid conflicting demands when possible. | Evaluate outcome, adherence, costs and next block objective. |

Illustrative press-specialization week from the original discussion: Monday priority press volume; Tuesday lower-body maintenance; Wednesday easy run; Thursday heavy press; Friday rest; Saturday run with suitable intensity exposure; Sunday rest or low-fatigue accessories. It is a feasible example only, conditional on availability, history and approved constraints. Two runs are not a universal maintenance dose. The coach should not convert this example into a mandatory schedule.

### 4.2 Longitudinal state and revisions

Store a stable cycle objective and horizon, ranked block objectives, method and rationale, phase-specific week intents, exposure bounds, progression/effort constraints, secondary-outcome targets, protected recovery/assessment dates and uncertainty. Detailed prescriptions are generated one week at a time; future weeks retain intents without fabricated workouts. A schedule-only change can retain the block version, but modifying a priority, phase, exposure commitment or block horizon requires review of the block and affected future weeks. Preserve elapsed prescriptions and exact execution/approval lineage. A missed session does not automatically carry over as extra work.

Endurance-development blocks, precise taper prescriptions, reactive deload parameters and return-from-interruption plans remain separate questions; no new prescriptions are introduced here. A strength-focused block should still explicitly track endurance outcome and exposure. If there is no credible baseline, the coach cannot assert maintenance.

## 5. Evidence catalog additions

**Target:** J1 schema version 1, existing `j1-screening-1` manifest, [catalog.py](https://github.com/dkiv/fitness-intelligence/blob/main/backend/src/fitness_intelligence/evidence/catalog.py), [manifest](https://github.com/dkiv/fitness-intelligence/blob/main/backend/src/fitness_intelligence/evidence/releases/j1-screening-1.json) (blob SHA `4fea4c2821ba7711ee44e1df11cf4e7bfd4ac98c` at inspection).

The schema uses strict `SourceRevision`, `ClaimRevision`, `Scope`, `Support`, `Relation`, `MethodRevision` and `CorpusRelease` records. The following JSON is an **additions fragment**, not a complete release or a registered manifest. All new claims are `pending`, all approvals are null, synthetic is false, and transfers are empty. The Enes claims are abstract-derived drafts held for further screening, not ready for human acceptance until full-text extraction. Existing source `moesgaard@1` remains screening; the new claims refer to its abstract result rather than silently changing its access/status. Reuse existing `strength-dose` and `periodization` questions. Scope terms are proposed exact-match terms, not existing approved retrieval vocabulary; review their semantics before integrating. A lower-case valid term is not itself an applicability judgment. J1's `quality` is provisional; detailed uncertainty is recorded in `assessment` and `support`. No additional quantitative schema fields are invented.

```json
{
  "sources": [
    {
      "key": "plotkin@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "citation": "Plotkin D et al. Progressive overload without progressing load? The effects of load or repetition progression on muscular adaptations. PeerJ. 2022;10:e14142.",
      "doi": "10.7717/peerj.14142",
      "record_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9528903/",
      "published_on": "2022-09-30",
      "design": "Randomized parallel-group trial",
      "access": "full-text",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Open access CC BY as stated in article; catalog use limited to metadata, links and original factual summaries; confirm deployment rights.",
      "appraisal": "Table 1 and strength result checked. Small study and unequal attrition; no equivalence test.",
      "next_review": "2027-02-24"
    },
    {
      "key": "enes-males@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "screening",
      "citation": "Enes A, De Souza EO, Souza-Junior TP. Effects of Different Weekly Set Progressions on Muscular Adaptations in Trained Males: Is There a Dose–Response Effect? Med Sci Sports Exerc. 2024;56(3):553–563.",
      "doi": "10.1249/MSS.0000000000003317",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/37796222/",
      "published_on": "2023-10-05",
      "design": "Randomized parallel-group trial",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Reuse rights not verified; metadata, links and original factual summaries only pending rights review.",
      "appraisal": "Abstract confirms direction of strength contrast. Extract magnitude, uncertainty, accumulated dose, protocol and bias from full text before acceptance.",
      "next_review": "2027-02-24"
    },
    {
      "key": "enes-females@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "screening",
      "citation": "Enes A et al. Does increasing the resistance-training volume lead to greater gains? The effects of weekly set progressions on muscular adaptations in females. J Sports Sci. 2025;43(4):381–392.",
      "doi": "10.1080/02640414.2025.2459003",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/39869076/",
      "published_on": "2025-01-27",
      "design": "Randomized parallel-group trial",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Reuse rights not verified; metadata, links and original factual summaries only pending rights review.",
      "appraisal": "Abstract confirms direction of leg-press contrast. Full-text magnitude, uncertainty, dose and risk-of-bias extraction outstanding.",
      "next_review": "2027-02-24"
    },
    {
      "key": "currier-acsm@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "screening",
      "citation": "Currier BS et al. American College of Sports Medicine Position Stand. Resistance Training Prescription for Muscle Function, Hypertrophy, and Physical Performance in Healthy Adults: An Overview of Reviews. Med Sci Sports Exerc. 2026;58(4):851–872.",
      "doi": "10.1249/MSS.0000000000003897",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/41843416/",
      "published_on": "2026-03-05",
      "design": "Overview of systematic reviews / position stand",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Article states CC BY-NC-ND 4.0; confirm intended use and licensing before deployment; metadata, links and original factual summaries only.",
      "appraisal": "Broad synthesis; periodization results and overlap with Moesgaard require detailed appraisal.",
      "next_review": "2027-02-24"
    },
    {
      "key": "pelland@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "screening",
      "citation": "Pelland JC, Remmert JF, Robinson ZP, Hinson SR, Zourdos MC. The Resistance Training Dose Response: Meta-Regressions Exploring the Effects of Weekly Volume and Frequency on Muscle Hypertrophy and Strength Gains. Sports Med. 2026;56(2):481–505.",
      "doi": "10.1007/s40279-025-02344-w",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/41343037/",
      "published_on": "2025-12-04",
      "design": "Systematic review and multilevel meta-regressions",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Reuse rights not verified; metadata, links and original factual summaries only pending rights review.",
      "appraisal": "Dose-response direction and diminishing returns in abstract; inspect models, uncertainty, set definitions, population and overlap.",
      "next_review": "2027-02-24"
    },
    {
      "key": "spiering@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "screening",
      "citation": "Spiering BA, Mujika I, Sharp MA, Foulis SA. Maintaining Physical Performance: The Minimal Dose of Exercise Needed to Preserve Endurance and Strength Over Time. J Strength Cond Res. 2021;35(5):1449–1458.",
      "doi": "10.1519/JSC.0000000000003964",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/33629972/",
      "published_on": "2021-05-01",
      "design": "Narrative review",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Reuse rights not verified; metadata, links and original factual summaries only pending rights review.",
      "appraisal": "General-population maintenance synthesis; athlete-specific evidence insufficient. Primary studies and outcome-specific effects need appraisal. Publication date is issue date.",
      "next_review": "2027-02-24"
    },
    {
      "key": "coleman@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "screening",
      "citation": "Coleman M et al. Gaining more from doing less? The effects of a one-week deload period during supervised resistance training on muscular adaptations. PeerJ. 2024;12:e16777.",
      "doi": "10.7717/peerj.16777",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/38274324/",
      "published_on": "2024-01-22",
      "design": "Comparative resistance-training intervention",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic publication record inspected; comprehensive correction/retraction and rights checks outstanding.",
      "rights": "Reuse rights not verified; metadata, links and original factual summaries only pending rights review.",
      "appraisal": "Cessation intervention differs from reduced-dose deloads or tapering. Full-text estimates and appraisal outstanding.",
      "next_review": "2027-02-24"
    }
  ],
  "claims": [
    {
      "key": "periodized-vs-constant-strength@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "scope": {
        "question": "periodization",
        "objective": "strength-development",
        "population": "resistance-training-participants",
        "experience": "mixed",
        "intervention": "volume-equated-periodized",
        "comparator": "volume-equated-nonperiodized",
        "outcome": "one-rm-strength",
        "horizon": "trial-endpoint",
        "block_context": "resistance-training"
      },
      "assertion": "The pooled 1RM change estimate favored periodized over nonperiodized resistance training when volume was equated.",
      "limitations": "Heterogeneous protocols and methodological quality; exact contrast durations and updated tables require review. Does not establish an optimal block structure.",
      "quality": "low",
      "assessment": "Small pooled standardized estimate; uncertain directness to experienced hybrid athletes. Abstract-level extraction.",
      "transfers": [],
      "support": [
        {
          "source": "moesgaard@1",
          "locator": "Abstract, Results, periodized vs nonperiodized 1RM comparison",
          "result": "ES 0.31 (95% CI 0.04 to 0.57).",
          "restriction": "Volume-equated studies; no hybrid-specific transfer approved."
        }
      ]
    },
    {
      "key": "undulating-trained-strength@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "scope": {
        "question": "periodization",
        "objective": "strength-development",
        "population": "resistance-training-participants",
        "experience": "trained",
        "intervention": "volume-equated-undulating",
        "comparator": "volume-equated-linear",
        "outcome": "one-rm-strength",
        "horizon": "trial-endpoint",
        "block_context": "resistance-training"
      },
      "assertion": "The pooled trained-subgroup 1RM estimate favored undulating over linear periodization, with substantial uncertainty.",
      "limitations": "Subgroup duration range outstanding; imprecise, heterogeneous evidence. Overall sensitivity and trial quality need full-text confirmation. No proof of interaction or block sequence superiority.",
      "quality": "low",
      "assessment": "Interval reaches zero at reported precision. Abstract-level subgroup extraction; directness to hybrid training low.",
      "transfers": [],
      "support": [
        {
          "source": "moesgaard@1",
          "locator": "Abstract, Results, LP vs UP, trained subgroup",
          "result": "ES 0.61 (95% CI 0.00 to 1.22).",
          "restriction": "Trained subgroup only; no approved hybrid transfer."
        }
      ]
    },
    {
      "key": "load-vs-repetition-progression@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "scope": {
        "question": "strength-dose",
        "objective": "strength-development",
        "population": "lower-body-resistance-trained-adults",
        "experience": "at-least-one-year",
        "intervention": "load-progression",
        "comparator": "repetition-progression",
        "outcome": "smith-machine-squat-one-rm",
        "horizon": "eight-weeks",
        "block_context": "resistance-training"
      },
      "assertion": "Both strategies improved Smith-machine squat 1RM; adjusted between-group estimate modestly favored load progression with uncertainty.",
      "limitations": "Small sample and unequal attrition; short duration; specific lower-body program; no equivalence test or controlled concurrent endurance intervention.",
      "quality": "moderate",
      "assessment": "Moderate provisional confidence in study-specific estimate; low for transfer to upper-body or hybrid programming.",
      "transfers": [],
      "support": [
        {
          "source": "plotkin@1",
          "locator": "Results, Strength; Table 1, squat 1RM row; Figure 3A",
          "result": "Adjusted LOAD minus REPS 2.0 kg (90% CI -2.4 to 7.8); unadjusted mean changes 21.8 and 19.3 kg. Table 1 expresses REPS minus LOAD.",
          "restriction": "Study-specific effect; 90% interval; not a validated double-progression policy."
        }
      ]
    },
    {
      "key": "progressive-sets-trained-males@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "scope": {
        "question": "strength-dose",
        "objective": "strength-development",
        "population": "trained-adult-males",
        "experience": "trained",
        "intervention": "scheduled-weekly-set-increases",
        "comparator": "constant-weekly-sets",
        "outcome": "back-squat-one-rm",
        "horizon": "twelve-weeks",
        "block_context": "resistance-training"
      },
      "assertion": "In a randomized trial of trained men, both fixed set-progression arms improved back-squat 1RM more than the constant-volume arm.",
      "limitations": "Small groups; cumulative volume differs; fixed rather than adaptive increases. Numerical contrast magnitudes and intervals outstanding.",
      "quality": "low",
      "assessment": "Abstract-derived draft held for further screening; no full-text appraisal or approved transfer.",
      "transfers": [],
      "support": [
        {
          "source": "enes-males@1",
          "locator": "Abstract, Results, 1RM multiple comparisons",
          "result": "Reported p=0.023 for +4 sets vs constant and p<0.0001 for +6 sets vs constant; magnitude and CI not extracted.",
          "restriction": "Specific lower-limb program and doses; no individual increase rule established."
        }
      ]
    },
    {
      "key": "progressive-sets-trained-females@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "scope": {
        "question": "strength-dose",
        "objective": "strength-development",
        "population": "trained-adult-females",
        "experience": "trained",
        "intervention": "scheduled-weekly-set-increases",
        "comparator": "constant-weekly-sets",
        "outcome": "leg-press-one-rm",
        "horizon": "twelve-weeks",
        "block_context": "resistance-training"
      },
      "assertion": "In a randomized trial of trained women, both fixed set-progression arms improved leg-press 1RM more than the constant-volume arm.",
      "limitations": "Small groups; differing cumulative dose; fixed increases; exact contrast magnitudes and intervals outstanding.",
      "quality": "low",
      "assessment": "Abstract-derived draft held for further screening; not evidence of optimal dose or sex-specific policy.",
      "transfers": [],
      "support": [
        {
          "source": "enes-females@1",
          "locator": "Abstract, 1RM comparison results",
          "result": "Reported p=0.032 for +2 sets vs constant and p<0.001 for +4 sets vs constant; magnitude and CI not extracted.",
          "restriction": "Specific lower-limb program; no approved hybrid transfer."
        }
      ]
    }
  ],
  "methods": [
    {
      "key": "phase-aware-undulating-specialization@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction)",
      "approval": null,
      "status": "pending",
      "question": "periodization",
      "description": "Candidate strength-specialization method with changing phase emphasis and undulating session prescriptions, retaining agreed secondary training objectives and reviewing one week at a time.",
      "provenance": "Original programming proposal in research packet 001, sections 3 and 4.",
      "tradeoffs": "Exact phase lengths, dose, progression and assessment strategy not empirically established. Feasibility and non-priority outcomes constrain adjustments.",
      "claims": [
        "periodized-vs-constant-strength@1",
        "undulating-trained-strength@1"
      ]
    }
  ]
}
```

**Integration instructions for Codex:** The fragment is structurally aligned with J1's field definitions and references the existing Moesgaard source. Append to a proposed successor of the complete manifest (preserve existing records, relations, withdrawals and question IDs); do not overwrite the immutable release. Review proposed exact-match scope terms, provenance and source access before merging. Keep the successor unapproved. The example `next_review` date follows the existing J1 cadence and is a proposed administrative date, not a training parameter. Validate using the actual `CorpusRelease` loader and tests; pin a new release digest only if the human reviewer authorizes publication. This packet does not claim that the repository loader was executed.

**Deliberately not extracted as new claims yet:** E04 (ACSM overview), E08 (Pelland models), E11 (Spiering narrative maintenance review) and E14 (Coleman cessation trial) have screening-source records but require more exact outcome-specific appraisal before assertion-level catalog extraction. Do not create claim records by converting author recommendations into intervention evidence. Preserve existing E01, E09, E10, E12 and E13 claims rather than duplicating them. Review ACSM/Moesgaard overlap before adding an explicit claim relation; preserve the existing Schumann/Petré qualification. No new `supersedes` edge is warranted; J1 requires an approved later revision to supersede a claim.

## 6. Evaluation cases

These are invented cases, not athlete data, evidence of effectiveness or new thresholds. Before running a candidate, pin the fixture clock, context, observation provenance/coverage, approved head, block, rule and corpus versions and define acceptable alternatives, forbidden actions, rationale, uncertainty and expected writes. Use synthetic fixture evidence for positive retrieval tests; real pending claims must remain ineligible.

| Case | Synthetic observation / perturbation | Acceptable decision and required explanation | Forbidden behavior | Policy |
|---|---|---|---|---|
| RT-A1 | Comparable lift: same load, more reps and lower reported effort. | Recognize improved task performance; maintain or propose permitted rep/load progression if warranted. | Mandatory set increase; assertion of measured latent strength. | RT-P01/P02 |
| RT-A2 | All sets completed but above approved effort target. | Hold, reduce or elicit feedback; disclose effort mismatch. | Automatic escalation merely because work was completed. | RT-P01 |
| RT-A3 | Credible improving strength trend at stable volume. | Maintaining volume is admissible; explain objective and opportunity cost. | Treat absence of volume escalation as failure. | RT-P02 |
| RT-A4 | Apparent plateau accompanied by worsening adherence. | Investigate adherence/coverage and comparable exposure first. | Diagnose inadequate stimulus and add sets without evidence. | RT-P02 |
| RT-A5 | Apparent plateau with rising subjective fatigue. | Hold/reduce or request feedback; distinguish competing hypotheses. | Automatic additional volume or categorical overtraining diagnosis. | RT-P02/LP-P02 |
| CT-A1 | Experienced runner begins a press block; compare established endurance history with missing history. | Define maintenance outcome and exposure relative to available history; ask for information or label provisional plan when missing. | Claim that two easy runs universally preserve endurance. | CT-P01 |
| CT-A2 | Demanding intervals precede repeated poorer squat sessions; athlete reports tired legs; feasible alternate slot. | Consider move or retain with rationale; protect secondary exposure; state a hypothesis and follow-up observations. | Assert causal interference or impose a universal spacing rule. | CT-P02 |
| LP-A1 | Same favorable performance/effort facts, accumulation vs protected peak. | Phase-appropriate hold/progress decisions; no extra work that conflicts with assessment. | Ignore phase or rewrite block automatically. | LP-P01 |
| LP-A2 | Accessory or interval session missed before a protected assessment. | Preserve assessment constraints; record deviation; propose feasible alternative only if warranted. | Catch-up dose violating recovery or approved phase. | LP-P01/P02 |
| LP-A3 | Priority strength improves but comparable endurance outcome declines. | Surface secondary-objective concern and alternative explanations; seek schedule/block review. | Declare success on priority strength alone or silently abandon endurance. | CT-P01/LP-P01 |
| Coverage pair | Replace confirmed comparable sets with inferred or incomparable sets; replace a low recovery observation with missing data. | No ungrounded progression; explain coverage; ask for clarification when needed. | Treat missing as zero, missed, or recovered; use incomparable estimates as evidence. | Common contract |
| Authority/evidence pair | Same case with a synthetic eligible result vs a real pending or withdrawn result; athlete declines candidate. | Disclose gap or defer empirical-dependent decision; retain approved head on decline; annotate historical pin if withdrawn. | Use pending evidence, invent transfer, or mutate approved schedule without consent. | Common contract |

**Evaluation design.** Compare paired scenarios with exactly one relevant change (phase, adherence, data quality, training experience or goal priority). Score assertion accuracy, locator validity, applicability, uncertainty and conflict disclosure independently of action quality. Validate feasibility, approval, immutability and replay against existing E/F/J gates; reject any safety or authority violation. Do not treat passing golden cases as evidence of improved athletic outcomes.

**Prospective effectiveness (later).** Compare a fixed periodized baseline, conventional double progression with effort constraints, and the adaptive policy. Track priority strength, retention of predefined secondary outcomes, adherence, time, fatigue and coverage. Separate standardized actual tests from estimated 1RM, reps at fixed load and subjective effort. Use comparable within-athlete observations, measurement noise and regression-to-mean safeguards. A conceptual model `observed performance = underlying capacity − transient fatigue + error` is not identifiable without sufficient observations and assumptions; do not implement a complex personalized state model merely because it is plausible. Prospective evaluation must consider confounding, time trends and carryover; observational improvement alone is not causal evidence.

## 7. Research backlog

P0 = first credible strength-focused coach; P1 = longitudinal extension; P2 = additional domains. Ordering is a proposed engineering/scientific dependency priority, not a ranking of health importance. No research beyond the initial scope has been performed for queued questions.

| Rank | ID / question | Priority / status | Starting evidence | Remaining question / implementation implication |
|---|---|---|---|---|
| 1 | RT-02: When should working-set volume change? | P0 / preliminary | E06–E08 | Is escalation superior to matched cumulative constant dose? What roles do previous dose, adherence, fatigue and objective play? Appraise trials before adapting E1. |
| 2 | RT-01: How should load/reps progress? | P0 / preliminary | E05 | Confirm comparative outcomes and applicability; choose reviewable effort/rep logic, not automatic increases. |
| 3 | LP-01: How should specialization blocks be organized? | P0 / preliminary | E02–E04 | Appraise subgroup, sensitivity, overlap and actual block comparisons. Select candidate method without asserting optimal phases. |
| 4 | CT-01: Which endurance dose retains defined qualities? | P0 / screening | E09–E11 | Outcome-specific maintenance studies in trained athletes; define secondary objectives/exposure, not fixed run counts. |
| 5 | RT-03: RPE/RIR autoregulation | P0 / queued | E05/E12 contextual only | Reliability, applicability and intervention effects; effort eligibility rules. |
| 6 | LP-02: Non-priority strength maintenance | P0 / queued | E11 | Outcome-specific dose and specificity; preserve other lifts. |
| 7 | CT-02: Concurrent sequencing and spacing | P0 / screening | E09–E10 | Trained athletes, modality and outcomes; avoid universal intervals. |
| 8 | LP-03: Deload benefits and prescription | P1 / screening | E12–E14 | Reduced-dose vs cessation; planned vs reactive; no readiness trigger yet. |
| 9 | LP-04: Taper and assessment | P1 / queued | None appraised | Define appropriate assessment and protect performance without arbitrary taper parameters. |
| 10 | EV-01: Detect real individual progress | P1 / queued | Conceptual evaluation only | Comparable metrics, error, prospective evaluation and baseline policies. |
| 11 | LP-05: Return from interruptions | P1 / queued | None appraised | Resumption policies without assuming missed work must be repaid. |
| 12 | EN-01: Running-development progression | P2 / queued | None appraised | Intensity distribution, progression, events and running-specific prescriptions. |
| 13 | RE-01: Recovery-guided vs performance-guided adjustments | P2 / queued | E12–E13 | Prospective value of signals and interventions; no threshold from subgroup correlations. |
| 14 | NU-01: Energy availability and nutrition constraints | P2 / queued | None appraised | Investigate nutrition and safety constraints in a dedicated packet. |

**Next packet:** RT-02, restricted to trained-lifter volume adjustment, cumulative-dose comparators, prior exposure and the applicability of evidence to strength-focused hybrid athletes. This is a proposed next task, not completed research.

## 8. Human review checklist

### Evidence and interpretation

- [ ] Confirm citations, DOI, publication edition/date, full-text access and correction/retraction status for every source before approving a revision; document permitted use and rights. Review proposed next-review cadence and assign a designated independent reviewer.
- [ ] E01: Confirm network contrast, credible interval and nonathlete scope. Decide if a comparison against inactivity is useful for the initial coach or should remain lower priority.
- [ ] E02/E03: Check updated Moesgaard full text, exact figure and section locators, trial durations, training-status definitions, volume matching, effect direction, influential-study sensitivity, heterogeneity, risk of bias, and whether subgroup effects support interaction. Do not approve an optimal block schedule from these results.
- [ ] E04: Appraise 2026 ACSM overview's periodization-specific comparisons, overlap with Moesgaard and outcome/population differences before interpreting agreement or discrepancy.
- [ ] E05: Confirm Smith-machine outcome, unadjusted vs adjusted effects, reversed table sign, 90% interval, attrition and protocol. Decide whether study-specific claim quality `moderate` is warranted. Do not treat no clear difference as equivalence or validate exact load progression.
- [ ] E06/E07: Obtain full text, extract effects and intervals per contrast, starting and cumulative sets, adherence, randomization, attrition and dose differences. Decide whether claim-level appraisal is justified and retain limits on adaptive or upper-body transfer. Do not use reported set increments as policy defaults.
- [ ] E08: Check the dose-response model, uncertainties, set definitions, training status, dependence and overlap. Do not derive an individual optimum, exact set rule or recovery-cost function from aggregate curves.
- [ ] E09/E10: Verify maximal-strength outcome and trained subgroup; compare overlapping studies, protocols, population definitions and endpoint differences. Review `trained-subgroup-boundary@1`; no equivalence or mandatory spacing inference.
- [ ] E11: Inspect primary maintenance studies and the population/outcome distinctions; verify whether any athlete-specific transfer is defensible. Do not claim a universal maintenance dose.
- [ ] E12/E13: Confirm that monitoring results support observation, not causal adjustment; verify outcome definition, response classification and measurement coverage. No individual readiness trigger.
- [ ] E14: Verify exact intervention, outcome estimates and population, distinguish cessation from reduced-dose deload and competition taper. Do not generalize to all deload methods.

### Programming and product decisions

- [ ] Approve or revise RT-P01/P02's action hierarchy, eligible observations, rep/load progression, volume-hold behavior and conservative constraints; define exact parameters separately with a rationale and evaluation plan.
- [ ] Approve or revise CT-P01/P02: explicit secondary outcomes, baseline/coverage, feasible scheduling, and criteria for block review. Identify which decisions are athlete preferences vs evidence vs safeguards.
- [ ] Approve or revise LP-P01/P02: phase purposes, optional assessment/peak, handling missed work, recovery vs cessation and safety escalation. Confirm the illustrative eight-week template is only a candidate.
- [ ] Decide what constitutes comparable observations, meaningful progress/plateau, sufficient adherence and reliable feedback; do not silently convert qualitative wording into numeric thresholds.
- [ ] Review the JSON fragment, source/claim statuses, scope terms, confidence labels, source links, exact locators, relations and empty transfers. Add any reviewed transfer only with an explicit argument. Validate a complete proposed manifest with the actual J1 loader and tests, not merely syntax checks.
- [ ] Review synthetic case labels before implementation; allow multiple defensible actions. Ensure pending/withdrawn claims, missing data and denied approval are tested. Separate offline correctness from prospective effectiveness.
- [ ] Record independent human attestations on accepted revisions and release only; document unresolved questions and review cadence. Until then, all new claims remain pending and the corpus must not be used as eligible empirical support.

**Release disposition:** Draft research packet only. No scientific or programming approval is requested by implication. No repo modifications, new operational evidence release, independently approved claims, or validated numerical training parameters. The next action is human appraisal and selection of the next focused research question.
