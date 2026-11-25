# Research Packet 009 — Learning from Individual Training History

**Fitness Intelligence** · Revision 0.1 · 2026-11-25 · Pending independent human review  
**Scope:** Experienced recreational hybrid athletes; initially a single-user personal coach.  
**Repository:** <https://github.com/dkiv/fitness-intelligence>  
**Dependencies:** Packets 001–008 and the standing observation-aware methodology. No prior packet, registered evidence release, schema or operational rule is changed by this document.

## 1. Executive summary

The practical objective is to improve the next prescription using the athlete's own relevant history, not to identify their optimal physiological response function. An athlete's accumulated history is useful because it contains demonstrated performance, actual exposure, preferences, practical constraints, and context-specific tolerance. It is not a controlled experiment.

Three levels of personalization must remain distinct:

| Level | What it enables | Initial priority |
| --- | --- | --- |
| Contextual personalization | Match training to goals, constraints, preferences, recent capacity and habitual exposure. | Essential |
| Feedback-driven adaptation | Review what was actually done and propose bounded changes based on comparable performance and tolerance. | Essential |
| Individual physiological modeling | Estimate personal dose-response functions, adaptation rates, latent fitness/fatigue or recovery constants. | Optional; not an MVP dependency |

**Main recommendations (candidate methodology, not approved rules):**

- Use recent *comparable* performance as the prescriptive reference; preserve historical bests as achievements and context. A recent noncomparable result is not automatically more useful than an older comparable one.
- Distinguish an observed improvement from evidence of a durable trend, a latent physiological adaptation, and a causal effect of a program. Repeated eligible observations improve the basis for a directional judgment, without guaranteeing causality.
- Use confirmed actual exposure and reported tolerance to inform baseline-relative prescriptions. A completed dose is not necessarily a well-tolerated dose, a productive dose, a maximum tolerable dose, or an optimal dose.
- Record the objective, approved change, expected benefit, actual execution and subsequent relevant observations. Recurring patterns may justify low-cost reversible scheduling preferences, while retaining alternative explanations.
- Do not disrupt a productive program just because the athlete has new data. Revisit a particular constraint or dose only when the decision warrants it. Missing optional RPE, HRV or nutrition information does not block every useful recommendation.
- Retain facts and confirmed preferences explicitly; compute most exposure and performance summaries on demand. Store consequential hypotheses with supporting references, context, limits, and conditions for reconsideration. Do not build a permanent responder label or athlete embedding.

The new literature appraisal is deliberately small: repeatability of measured maximal strength and standardized repetition-maximum performance, plus the statistical distinction between observed change and individual training response. Existing evidence from running, nutrition, concurrent programming, maintenance and autoregulation is reused rather than reappraised wholesale. No direct trial validating the complete history-selection, pattern-retention and revision workflow in experienced hybrid athletes was identified in this targeted search. Such validation is not a prerequisite for an ordinary, explicitly qualified and athlete-approved coaching decision.

The deliverable extends Packet 006's block construction and Packet 008's recovery review with a history-selection and learning step. It does not create a parallel adaptive planner. Software conformance, recommendation quality and personal usefulness are evaluated separately. Extensive experiments, population causal inference, advanced N-of-1 designs, reinforcement learning and physiological state modeling remain deferred.

## 2. Scientific evidence table

### 2.1 Search and review scope

**Question:** Which evidence makes ordinary within-athlete comparisons more defensible or changes how a personal coach should use historical observations? Population: trained adults and runners where available; outcome: repeatability of task performance, directional changes and relevance of actual exposure; horizon: repeated assessments, sessions and blocks. No assumption of direct hybrid-athlete transfer.

Targeted search on 2026-11-25 using PubMed-indexed records and journal full text: `test retest reliability one repetition maximum trained`, `repetition maximum bench press test retest trained`, `individual response exercise training within subject variability repeated observations`, `athlete monitoring typical error`. Prior packet Markdown and J1 fragments were inspected locally to avoid duplicate publications. Selected two new empirical measurement papers and two methodological references. This is not a comprehensive or registered systematic search; no formal duplicate extraction or fresh review of all earlier sources. New source version/rights and publication-status checks are preliminary, not a comprehensive correction or retraction audit. All provisional assessments are pending independent review.

### 2.2 New findings: directly relevant measurement evidence

| ID / scientific claim | Publication, DOI and result locator | Population and comparison | Result and uncertainty | Limitations, applicability and provisional confidence |
| --- | --- | --- | --- | --- |
| I01 — Measured 1RM has generally high relative repeatability, but absolute within-person variation is not negligible. | Grgic J, Lazinica B, Schoenfeld BJ, Pedisic Z. *Test–Retest Reliability of the One-Repetition Maximum (1RM) Strength Assessment: a Systematic Review*. Sports Med Open 2020;6:31. [10.1186/s40798-020-00260-z](https://doi.org/10.1186/s40798-020-00260-z). Results, Overall Reliability; Reliability in Relation to Training Status and Familiarization; Table 3/Fig. 2. Full-text publisher page. | 32 studies, total 1,595 participants; 14 studies included participants with prior resistance training. Repeated measured 1RM, varied exercises/protocols. | Overall median ICC 0.97 and CV 4.2%; experienced subgroup median ICC 0.98 and CV 3.3%, ranges 0.64–0.99 and 0.5–7.8% respectively. These are descriptive summaries of study estimates, not pooled confidence intervals. | COSMIN-rated moderate/excellent studies per review; heterogeneity, varying familiarization and between-person dispersion, no hybrid-specific reliability. High ICC does not imply small individual error. Moderate confidence for protocol-specific repeatability, low for translating these CVs to a particular athlete's estimated 1RM. Pending. |
| I02 — Repetition-maximum performance is variable even under a standardized bench-press protocol. | Mitter B, Csapo R, Bauer P, Tschan H. *Reproducibility of strength performance and strength-endurance profiles: A test-retest study*. PLoS ONE 2022;17:e0268074. [10.1371/journal.pone.0268074](https://doi.org/10.1371/journal.pone.0268074). Abstract Results; Methods, Experimental approach/Procedures; Results Table 1 and Fig. 2. Publisher full text. | 24 trained adults (15 men, 9 women), at least one year of bench training. Repeated tests separated by one week, at 90%, 80%, 70% of each visit's measured 1RM; standardized pin-supported technique and test conditions. | At 90% 1RM, SEM 0.7 repetitions (90% HDI 0.5–0.9), ICC 0.65 (0.39–0.83). At 70%, SEM 1.1 repetitions (0.8–1.4), ICC 0.86 (0.71–0.93). | Small sample, relative load re-established each visit (not a fixed absolute load), effort to momentary failure, descending loads and long rests, bench-specific. Moderate for this protocol; low transfer to habitual submaximal sets, other lifts or concurrent fatigue. Neither interval is a personal minimum detectable change. Pending. |

**Interpretation for coaching:** A single extra repetition is a real recorded performance difference if the set is verified; it is not necessarily evidence of changed underlying capacity. There is also no basis for ignoring every change smaller than a published CV. A sequence of comparable submaximal observations, actual effort and training context can make a directional inference more credible. The coach need not schedule maximal or failure testing simply to obtain these data.

### 2.3 Methodological evidence (not treatment-effect claims)

| ID | Source and access | Relevance and limitation |
| --- | --- | --- |
| I03 | Hecksteden A, Kraushaar J, Scharhag-Rosenberger F, Theisen D, Senn S, Meyer T. *Individual response to exercise training – a statistical perspective*. J Appl Physiol 2015;118:1450–1459. [10.1152/japplphysiol.00714.2014](https://doi.org/10.1152/japplphysiol.00714.2014). Publisher text, Background: Random variation and Within-subject variability. | Distinguishes measurement variability, repeatability of response and genuine subject-by-training interactions. Repeated measurements help reduce random error under appropriate assumptions; a single before/after difference cannot isolate a treatment response. This is methodological reasoning, not an efficacy result; no J1 intervention claim or requirement to repeat whole blocks experimentally. |
| I04 | Hopkins WG. *Measures of reliability in sports medicine and science*. Sports Med 2000;30:1–15. [10.2165/00007256-200030010-00001](https://doi.org/10.2165/00007256-200030010-00001). Abstract only. | Separates typical error, systematic change and retest correlation. Use absolute and relative variation, not correlation alone. Abstract-level methodological context; no new numerical claim or general readiness threshold. |

For illustration, if two measurements of an unchanged task have independent zero-mean errors of variance σ², their difference has variance 2σ². Averaging n independent observations of an unchanged task gives error variance σ²/n. These are conditional statistical identities; serial correlation, genuine adaptation, changing effort, and protocol changes can invalidate the simple averaging argument. Ordinary training logs are not independent replicate laboratory tests. Do not estimate a confidence interval from a handful of heterogeneous working sets as though each were an independent repeat of the same capacity.

### 2.4 Reused evidence (existing claims remain pending)

This is a decision-oriented index, not a new extraction or approval. See earlier packets for source versions, population definitions, exact protocols, comparators, bias, review obligations and rights. Existing IDs and their scoped meanings are unchanged. Confidence below refers to the narrow finding, not the proposed personal-history policy.

| Packet / exact claim | Source, DOI and locator | Relevant finding | Implication and uncertainty |
| --- | --- | --- | --- |
| P002 `habitual-set-maintenance-strength@1` | Barsuhn et al., [10.1152/japplphysiol.00476.2024](https://doi.org/10.1152/japplphysiol.00476.2024), Results/Discussion maximal strength and baseline table. | Trained men, eight weeks, habitual weekly sets maintained versus increased; no significant group-by-time interaction. | Maintaining a productive dose is defensible as a candidate option. Attrition and baseline imbalance; not superiority/equivalence; source access remains unresolved. Low. |
| P003 `same-session-trained-lower-body-strength@1` | Petré et al., [10.1007/s40279-021-01426-9](https://doi.org/10.1007/s40279-021-01426-9), Results §3.5/Fig. 3. | Trained lower-body same-session concurrent versus strength-only subgroup ES −0.66 (95% CI −1.08 to −0.25). | Consider session proximity when reviewing recurrent lower-body difficulty; subgroup not a direct randomization of timing, no universal spacing rule. Low. |
| P004 `athlete-logged-intake-dlw-disagreement@1` | Capling et al., [10.3390/nu9121313](https://doi.org/10.3390/nu9121313), Abstract Results, DLW comparison studies. | Reported intake versus expenditure: mean underestimation 19%; pooled ES −1.006 (95% CI −1.3 to −0.7). | Logging is not true intake; energy imbalance can contribute to disagreement. Cannot retrospectively correct an individual's logs with group mean. Moderate. |
| P005 `outdoor-five-km-typical-error@1` | Hurst & Board, [10.1080/1091367X.2016.1233421](https://doi.org/10.1080/1091367X.2016.1233421), Abstract Results. | 15 runners, repeated competitive outdoor 5 km: TE 14.7 s (95% CI 11.3–21.4); CV 0.95% (0.59–1.31). | Compare similarly performed tests, not arbitrary training runs. Protocol-specific error, not a universal minimum meaningful change. Low. |
| P005 `submaximal-hr-typical-error@1` | Shushan et al., [10.1186/s40798-023-00564-w](https://doi.org/10.1186/s40798-023-00564-w), Table 5, reliability TE. | Pooled TE 1.6 percentage points (95% CI 1.4–1.9; PI 0.9–3.0) of HRmax in team-sport submaximal tests. | Standardization matters; not bpm, running economy, or athlete-specific change cutoff. Moderate, indirect. |
| P005 `adaptive-running-ten-km-performance@1` | Nuuttila et al., [10.1249/MSS.0000000000002968](https://doi.org/10.1249/MSS.0000000000002968), Fig. 3, T1 to T3. | Recreational runners, individualized versus predefined program: 10 km change −6.2±2.8% versus −2.9±2.4%, ES 1.23 (95% CI 0.42–2.02). | Actual adaptive intervention supports studying feedback-driven programs; small, bundled intervention with different exposure. Not validation of the historical-pattern method, nor direct hybrid transfer. Moderate. |
| P006 `short-detraining-vo2max@1` | Zheng et al., [10.1155/2022/2130993](https://doi.org/10.1155/2022/2130993), Results 3.3. | Detraining versus pre-detraining trained state, short horizon ES −0.62 (95% CI −0.94 to −0.31). | Past performance may cease to be prescriptive after interruption; not a rate of loss for a given runner or lift. Low. |
| P007 `morning-mass-variability-active-men@1` | Cheuvront et al., [10.1123/ijsnem.14.5.532](https://doi.org/10.1123/ijsnem.14.5.532), Abstract Results. | 65 active men, 4–15 days under fluid-replacement guidance; daily variability 0.51±0.20 kg, CV 0.66±0.24%. | Weight observations need context; no tissue change or deficit inference from a single reading. Moderate, indirect. |
| P007 `calerie-weight-model-intake-change-agreement@1` | Sanghvi et al., [10.3945/ajcn.115.111070](https://doi.org/10.3945/ajcn.115.111070), Table 1/Fig. 3. | CALERIE model versus DLW/DXA intake-balance changes: individual RMS disagreement 215 kcal/day. | Historical targets may guide conditional reported-intake recommendations, not identify true TDEE. Moderate, indirect. |
| P008 `predicted-rir-signed-error@1` | Halperin et al., [10.1007/s40279-021-01559-x](https://doi.org/10.1007/s40279-021-01559-x), Abstract Results. | Mean underprediction 0.95 repetitions (95% CI 0.17–1.73), I²=97.9%. | RIR is an estimate; no individualized correction from pooled signed bias. Low. |
| P008 `autoregulated-load-pooled-one-rm@1` | Hickmott et al., [10.1186/s40798-021-00404-9](https://doi.org/10.1186/s40798-021-00404-9), Abstract Results, load contrast. | Autoregulated versus percentage loading in trained individuals MD +2.07 kg (95% CI −0.32–4.46). | Supports considering alternative adjustment methods, not universal superiority or a specific progression rule. Low. |

Also retain J1 `load-and-wellbeing@1` (Saw, [10.1136/bjsports-2015-094758](https://doi.org/10.1136/bjsports-2015-094758), Table 7) and `nocturnal-heart-rate@1` as reviewed-in-draft monitoring context, not validated decision thresholds. P004's energy adequacy/referral and P008's local/general fatigue distinctions apply throughout. None of these findings supports a permanent personal trait or optimal historical dose estimate.

### 2.5 Measurement and proxy applicability

| Decision-relevant construct | Reference versus field observation | Granularity and eligibility | Main limitation / fallback |
| --- | --- | --- | --- |
| Exercise-specific maximal strength | Standardized measured 1RM versus observed load/reps, reported effort or estimated 1RM | Same movement, equipment, load convention, ROM, comparable set purpose/order and technique; confirmed working sets. Same estimation formula and relevant rep range for e1RM. | Effort, fatigue, rep range and technique influence estimate; do not equate e1RM to measured 1RM. Can use verified same-load reps when RPE unavailable, with narrower interpretation. |
| Repeated-set capacity | Standardized repeated work versus achieved sets/reps at known loads, rest and effort | Set sequence, completion, rest context and comparable intended work | More total reps may reflect more sets, longer rest or higher effort. Compare like exposures; missing rest/effort reduces specificity. |
| Running performance | Comparable timed distance test versus race, time trial or field run | Distance, elapsed/active time semantics, route, terrain, effort, conditions, sensor quality; achieved intervals require actual interval data or athlete report | Pace at HR is not economy or VO2max; weather, surface and HR error can dominate. Exclude or qualify comparisons. |
| Running-specific tolerance | Actual running frequency, duration, distance, long-run and quality exposure plus athlete report | Distinguish running from other sport; exposure window and coverage | Completion alone is not tolerance; other sport not equivalent running mileage. Ask about soreness, pain and subsequent function if decision-sensitive. |
| Recovery and burden | No single comprehensive reference; performance and subjective feedback plus optional sleep/RHR/HRV | Timing, relevant local task, protocol/units and baseline verified | Unknown HRV units, changed device or one low value cannot establish readiness; use task-specific evidence and P008 fallback. |
| Energy balance/weight trajectory | Reference energy expenditure/controlled intake versus reported intake and standardized body mass | Date alignment, comparable weigh-in regime, logging completeness and representative exposure | Water/glycogen, tissue partitioning and changing reporting bias; true TDEE not necessarily identifiable. Use P007 only under its assumptions. |
| Adherence and preference | Approved prescription versus actual matched outcome; athlete-confirmed preference | Exact prescription version, occurrence, coverage and actual completion; explicit correction | Inferred sets/absence of logs are not confirmed adherence or miss; preference is not physiological restriction. |

The current integration inventory is mutable. Provider identities and device-specific fields are irrelevant to the empirical claims and canonical policies. Historical strength records and running aggregates can support many comparisons; actual achieved interval data, RPE, nutrition coverage, comparable HR protocol, and some contextual variables are conditional. Aggregate running splits may not provide ordered paired HR/speed; performed workout instructions do not prove achieved intervals. Unknown units and noncomparable regimes must remain explicit. Future observations can improve a specific comparison without changing the underlying evidence.

## 3. Candidate coaching policies

All six additions are documentation-level extensions of existing policies, revision 0.1, pending independent review. They organize historical reasoning; they do not grant authority to change a prescription. Feasible/conditionally feasible/qualitative only/deferred describe data support for the stated action, not scientific approval. For all policies, the current approved plan, restrictions, objectives and approval gate take precedence. Quantitative changes must use separately reviewed contextual parameters and the existing block envelope. Do not create universal recency windows, effort corrections or progression thresholds.

### IA-P01 — Select relevant historical comparisons (extends EN-P07, RT-P01, RE-P08)

| Field | Specification |
| --- | --- |
| Decision and construct | Which past observations represent a reasonable reference for current task performance? Exercise- or task-specific demonstrated capacity, not latent fitness. |
| Scientific support | I01/I02, P005 repeatability and P008 RIR findings; relevance ranking itself is engineering/programming judgment. |
| Ideal/minimum/optional inputs | Ideal standardized repeated task tests and context. Minimum current decision purpose, dated eligible actual task observation(s), comparable identity, units and completion. Optional effort, technique, rest, route, environment, phase, fueling. |
| Prescription / adherence / effectiveness | Prescription: current context plus eligible recent reference or conservative fallback. Adherence: matched actual to approved prescription with coverage. Effectiveness: subsequent comparable outcome and context. |
| Scientific / data readiness | Narrow measurement results pending; selector not validated for benefit. Selection feasible for documented comparable history, conditionally feasible when exercise or running conditions unclear; effectiveness conditional. Authorization: none. |
| Logic | Partition observations into comparable, contextual-only, excluded, or uncertain. Prefer recent eligible same-task observations; use multiple where meaningful. Explain exclusions and conflicting evidence. Prior records may be context even if incomparable. |
| Missing data / fallback | If effort missing, compare actual load/reps narrowly or ask only if effort changes choice. If equipment unknown, avoid numerical load transfer. If no current reference, ask for familiar recent exposure or propose a conservative approved assessment. |
| Assumptions / prohibited inferences | Same label need not imply same exercise. Old PR is not current capacity; slower hot run not necessarily regression. Do not cherry-pick best outcomes, substitute unknown effort, or silently infer missing execution. |
| Richer-data extension | Verified technique/equipment history, actual interval traces, repeated field tests, contextual observations when incremental decision value warrants. |

### IA-P02 — Interpret individual performance trends (extends EN-P07, RE-P08, HP-P09, EE-P03)

| Field | Specification |
| --- | --- |
| Decision and construct | Is observed task performance improving, stable within available resolution, deteriorating, mixed, or insufficiently observed? |
| Scientific support | I01–I04 and P005/007/008 measurement results. Descriptive summary and decision labels are candidate methodology, not validated change detectors. |
| Ideal/minimum/optional inputs | Ideal repeated standardized outcomes with known error. Minimum eligible repeated observations, date range, task and objective; for a single result report change only. Optional effort, conditions, individualized repeatability, fatigue and nutrition context. |
| Prescription / adherence / effectiveness | Prescription: direction plus exposure/tolerance and approved bounds where relevant. Adherence: actual matched completed work. Effectiveness: subsequent comparable observations with coverage and context; no causal attribution. |
| Scientific / data readiness | Measurement evidence pending; no universal threshold. Descriptive trend feasible when observations comparable; quantitative individual inference conditional; latent physiological modeling deferred. Authorization: none. |
| Logic | Report raw reference values, eligible count, spread, change direction and competing explanations. Use robust summary/trend only within a comparable regime; compare against objective and practical relevance, not a test of significance alone. Keep tasks separate. |
| Missing data / fallback | Report insufficient comparison, mixed evidence or observation uncertainty. Continue/hold if feasible, ask targeted feedback or reassess. No forced increase or reduction on an isolated result. |
| Assumptions / prohibited inferences | Recorded performance is not underlying capacity; stable observed results do not establish equivalence or lack of adaptation; no inference of VO2max/economy from pace-HR, tissue composition from scale or recovery capacity from HRV. |
| Richer-data extension | Validated within-person repeatability estimates and prospective comparison of trend rules; optional standardized tests. |

### IA-P03 — Use demonstrated historical tolerance to initialize and bound exposure (extends RT-P02, CT-P05, HP-P02, RE-P04/09, EN-P01/02)

| Field | Specification |
| --- | --- |
| Decision and construct | What starting or adjusted exposure is credible under the current goals and combined burden? Distinguish exposure, tolerance and outcome response. |
| Scientific support | P002 habitual-volume comparison, P003 interference/timing, P005 running exposure, P006 maintenance/detraining, P008 recovery. No trial identifies personal dose ceilings from routine logs. |
| Ideal/minimum/optional inputs | Ideal complete actual exposure and comparable outcomes/feedback across recent blocks. Minimum dated actual exposure by discipline with coverage, goal, schedule, restrictions and known interruptions; minimum tolerance evidence for calling it tolerated. Optional effort, session placement, subjective burden, sleep/fueling. |
| Prescription / adherence / effectiveness | Prescription: representative actual recent exposure plus current capacity/constraints; conservative fallback if uncertain. Adherence: actual sets, load, frequency, duration, intensity/effort as applicable. Effectiveness: outcomes and burden in both disciplines. |
| Scientific / data readiness | Indirect empirical premises pending; baseline-relative envelope and candidate adjustments require separate review. Feasible or conditional depending on completeness and feedback; optimal dose estimation deferred. Authorization: none. |
| Logic | Summarize assigned, observed, completed-with-acceptable-tolerance, and associated-with-improvement separately. Do not treat unattempted exposures as demonstrated. Anchor to recent representative context; retain older productive dose as an option, not a cap or prescription. Check shared scheduling and fueling; compare hold, redistribute, increase or decrease. |
| Missing data / fallback | Unknown tolerance stays unknown. When exposure is incomplete or regime changed, request a recent representative week or select a conservative provisional start; never fill missed records with zero. |
| Assumptions / prohibited inferences | Tolerating a dose once does not establish indefinite safety, benefit or maximum capacity. Best-performing block does not identify the optimal personal set count. Previous exposure does not guarantee suitability after interruption. |
| Richer-data extension | Confirmed session outcomes, context-specific long-run tolerance, structured feedback; no automatic learned physiological response coefficients. |

### IA-P04 — Review previous prescription changes and subsequent response (extends CT-P02/05, HP-P09, RE-P11, EE-P07)

| Field | Specification |
| --- | --- |
| Decision and construct | Is a previously attempted programming choice worth retaining, revisiting or avoiding given current context? |
| Scientific support | P003 timing, P005 adaptive-program trial, I03 statistical caution; the decision-log and pattern use are practical judgment. |
| Ideal/minimum/optional inputs | Ideal matched decisions, actual execution and comparable subsequent outcomes with concurrent changes recorded. Minimum previous prescription/change, date, actual execution status, relevant outcome/feedback and current objective. Optional repeated similar decisions, adherence, fuel, sleep, life context. |
| Prescription / adherence / effectiveness | Prescription: relevant earlier outcome and feasible reversible alternative, or ordinary current policy without learned preference. Adherence: approved revision matched to actual. Effectiveness: prospective relevant response and burden; compare descriptively to similar past context. |
| Scientific / data readiness | No validated causal history-learning algorithm. Conditional on reliable revision/execution linkage and feedback. Qualitative if only athlete recollection. Authorization: none. |
| Logic | Reconstruct the change and its expected outcome, confirm implementation, inspect relevant outcomes and alternative explanations. Repeated context-specific problems may justify a scheduling preference. Prefer low-cost reversible changes within bounds when tradeoffs acceptable; continue if already productive. |
| Missing data / fallback | If actual implementation unknown, label response attribution unknown. Ask targeted feedback; if no decision changes, defer further data collection. |
| Assumptions / prohibited inferences | Regression to mean, selection bias, changing training phase and multiple simultaneous changes. Never infer causality or rank a program by its largest historical before/after gain. No formal experiment required for ordinary reversible decisions. |
| Richer-data extension | Lightweight follow-up reminders attached to review records, prospective shadow comparison where useful, better matching of actual execution; not an experimental platform requirement. |

### IA-P05 — Reassess historical relevance after changed circumstances (extends HP-P02/09, EN-P06/10, EE-P08, RE-P01)

| Field | Specification |
| --- | --- |
| Decision and construct | Which past references remain prescriptive, and which become context-only after a change in state, goal or observation regime? |
| Scientific support | P006 detraining and outcome-specific retention, P007 logging/weight regimes, P005/008 measurement limitations. No universal forgetting function. |
| Ideal/minimum/optional inputs | Ideal dated comparable exposure/outcomes before and after regime change. Minimum current context revision and known changes (interruption, equipment, goal, restrictions or measurement); optional new assessments and athlete feedback. |
| Prescription / adherence / effectiveness | Prescription: current eligible reference, or conditional conservative re-entry. Adherence: new prescription/actual linkage. Effectiveness: within-new-regime repeated observations. |
| Scientific / data readiness | Empirical findings pending; staleness logic is engineering/programming judgment. Feasible if change known; conditional when metadata missing. Physiological decay estimation deferred. Authorization: none. |
| Logic | Segment history by material changes; do not concatenate incompatible series. Retain original observations and historical bests. Re-evaluate derived references and patterns on relevant change; allow older same-regime context when useful. No automatic expiry by age alone. |
| Missing data / fallback | Unknown regime equivalence stays uncertain; ask or retain contextual-only. If current capacity unknown, avoid prescriptive extrapolation from old PR. |
| Assumptions / prohibited inferences | A new restriction overrides old success; a newer estimate is not inherently better; descriptive rolling averages or exponential smoothing are not physiological decay models. |
| Richer-data extension | Explicit equipment/protocol changes, interruption context and new assessments; compare windowing methods only if a concrete error emerges. |

### IA-P06 — Retain and update individual coaching knowledge (extends HP-P09, RE-P10/11 and EE-P04/08)

| Field | Specification |
| --- | --- |
| Decision and construct | Which athlete facts, summaries, preferences and provisional patterns should be retained or recomputed? |
| Scientific support | I03 and prior observation-aware framework constrain interpretation; structured record design, persistence and invalidation are engineering decisions. No empirical efficacy claim. |
| Ideal/minimum/optional inputs | Ideal provenance-linked actuals, context revisions, decisions and subsequent outcomes. Minimum attributable fact or preference, as-of context, date and source; for inferred pattern, supporting eligible observations and alternative explanations. Optional athlete confirmation. |
| Prescription / adherence / effectiveness | Prescription: retrieve only relevant current context/patterns, then apply ordinary reviewed policy. Adherence: verify actual against exact approved prescription, not against inferred knowledge. Effectiveness: inspect later evidence and whether the contextual preference helped usability/outcome. |
| Scientific / data readiness | Method-only; feasible for explicit facts/preferences, conditional for patterns, physiological trait inference deferred. Authorization: none. |
| Logic | Separate observed, derived, reported, hypothesized, generally reviewed and approved records. Compute summaries on demand. Persist consequential context-specific hypotheses with status and support; allow correction, contradiction, retirement and as-of replay. Athlete confirmation of experience does not establish causality. |
| Missing data / fallback | Do not persist a speculation as a fact; omit or mark unsupported. If evidence disappears or is corrected, flag dependent pattern for review; retain historical rationale. |
| Assumptions / prohibited inferences | No permanent responder label, learned embedding, physiological trait, hidden causal model or authority to change plan. Private history remains owner-scoped; it is not added to J1. |
| Richer-data extension | Add record types only if existing structured records cannot meet a demonstrated coaching or audit need; prefer retrieval over materialization. |

## 4. Individual training-history and adaptation methodology

### 4.1 Integration into the existing block review

The block objectives, weekly intent, actual outcome matching, nutrition and recovery review remain those of P006/P008. The following sequence is the history reasoning component of that process. It uses the smallest adequate change level, respects hard constraints before preferences and objectives, and never creates an independent authority to revise a plan.

| Step | Operation and required inputs | Optional evidence / judgment and output |
| --- | --- | --- |
| 1 | Load as-of approved block, prescription, goal, constraints and review question. | Current priority, assessment date, secondary commitments; state decision scope. |
| 2 | Retrieve historical observations for that task, prior relevant blocks and changes. | Filter by canonical identity, time and context, not app-specific identifiers. |
| 3 | Audit actual/confirmed status, provenance, units, coverage and comparability. | Separate actual, inferred, partial, missed and unknown. List exclusions and ambiguity. |
| 4 | Describe recent actual exposure by discipline and task. | Report windows, eligible observations, unknown exposure; avoid pooling sets and running km. |
| 5 | Compare eligible performance with recent references; contextualize older blocks/PRs. | Raw values, direction, variability and effort/conditions; no unsupported physiological state. |
| 6 | Identify recurring tolerance or scheduling patterns only if observations support them. | Retain counterexamples, uncertain matches and changing context. No required recurrence count. |
| 7 | Separate facts from reports, summaries and hypotheses. | Cite observation IDs and context; mark causality unresolved. |
| 8 | Check material regime changes, restrictions, goal and phase. | Old successful dose may become context-only; current safety constraints dominate. |
| 9 | Review relevant previously approved changes, actual adherence and response. | Note simultaneous changes and observation gaps; do not infer treatment effects. |
| 10 | Generate feasible alternatives using existing policies. | Hold, bounded load/reps/dose change, redistribute, reduce local burden, change fueling, ask, assess, defer or explicit block revision. |
| 11 | Compare alternatives against objectives, feasibility, burden, uncertainty and reversibility. | No arbitrary scalar readiness/utility score; explain why one option is reasonable, and alternatives rejected or retained. |
| 12 | Freeze rationale, eligible and excluded observations, uncertainty and proposed diff. | Pin as-of time, context, prescription, data snapshot and applicable reviewed policy/evidence versions. |
| 13 | Present proposal for athlete decision if prescription changes. | Execute inside existing approved bounds without silent revision; new target/range/slot requires approval, objective change requires block review; safety restriction can block activation. |
| 14 | Review subsequent actual exposure and comparable outcomes. | Update contextual preference/pattern only when justified; retain previous records and uncertainty. |

All steps after literature-supported measurement premises are candidate practical methodology and engineering safeguards. No step depends on population causal inference. If an ordinary choice is supported by the current reviewed program and observations, lack of optional history need not cause deferral. If the action requires empirical support which is still pending or inapplicable, do not present it as reviewed science; only a separately authorized rules-only proposal may proceed, where appropriate.

### 4.2 Selecting historical references

Use an explicit eligibility pass before recency or ranking. The decision defines the reference task and outcome (e.g., first working set of paused barbell bench press at comparable effort, not all pressing movements). Verify load convention (external load, per-side load, assistance, bodyweight), exercise variation, equipment, technique/ROM, and actual set completion. For running verify time/distance meaning, task purpose, route/conditions, and actual achieved work. Exclude impossible values and ambiguous identity; keep them available for investigation rather than delete history.

| Comparison strategy | Best use | Failure mode / handling |
| --- | --- | --- |
| Last comparable session | Immediate load or repetition choice | May be unusually fatigued or excellent; check additional references where available. |
| Several recent comparable sessions | Direction and variability | Mixed phases, selection bias and autocorrelation; summarize range and context rather than average incompatible sessions. |
| Prior block | Familiar program structure, previous exposure and response | Starting state, assessment timing, concurrent demands and adherence differ; not a randomized comparison. |
| Historical PR | Achievement, long-run goal setting and context | Not current demonstrated ability or safe starting prescription. |
| Similar emphasis or schedule | Context-specific tolerance and planning options | Context similarity is incomplete; explicitly note differences and counterexamples. |

Candidate ordering: strict eligibility for the intended comparison, current regime relevance, task/purpose similarity, comparable effort and measurement context, recency, and stable tie-breaks for reproducibility. This is a proposed descriptive selection hierarchy, not a validated learned weighting function. If criteria conflict, retain multiple relevant references and explain the tradeoff instead of manufacturing a score. Avoid outcome-dependent selection: define the filter before inspecting whether the result improved. Record the eligible denominator and exclusions. Keep prior snapshots recoverable even if an observation is corrected or removed from current support.

### 4.3 Directional assessment and recency

For a narrow comparable task, store the ordered eligible raw observations with units and dates, and report the current versus reference contrast (e.g., +1 rep at the same external load, or −15 s over the same timed route). Use a recent median or range where appropriate; for monotonic trends, show actual dates and slope only if enough comparable observations and reasonable assumptions. Use labels: **observed improvement**, **observed deterioration**, **stable within available resolution**, **mixed**, **insufficient comparable evidence**. Distinguish an isolated observed difference from an inferred sustained direction. A stable classification is not statistical equivalence; a plateau label requires adequate opportunity, exposure and comparable data, not a missing test or flat e1RM line.

If a historical summary is useful, choose its window from block intent, data availability, regime stability and decision horizon. A rolling or exponentially weighted summary is a *descriptive engineering convention*, not physiological memory. Do not prescribe a universal number of sessions, weeks, decay constant or personal minimum detectable change. Sensitivity-check the conclusion by reviewing recent eligible observations and an alternative defensible summary if the action depends on it. If conclusions differ materially, disclose that and choose a reversible alternative or defer. A coach may make ordinary adjustments without establishing a formal statistically significant difference.

Recency is contextual: after interruption or changed equipment, old capacity is not a current anchor; an older well-standardized test may still be useful as context against recent confounded efforts. Within an unchanged maintenance block, prior performance may remain a useful target. Retain all original dates and context. Do not automatically reset history on a new block or expire a preference based solely on time.

### 4.4 Continue or reconsider: practical decision branches

| Observed situation | Candidate response and why | Avoid |
| --- | --- | --- |
| Progress at acceptable burden and secondary outcomes supported | Continue current exposure or reviewed bounded progression if goal/phase warrants. | Add volume solely because completion was successful. |
| Stable maintenance outcome, acceptable burden | Retain exposure and verify retention at appropriate opportunity. | Treat frequency alone as maintenance proof. |
| Slow progress but poor adherence | Clarify execution, schedule, preferences; consider simplifying or redistributing. | Diagnose inadequate physiological stimulus from assigned work. |
| Slow progress and sufficient comparable exposure, acceptable burden | Review specificity, priority and actual stimulus; consider a small reversible contextual change or continue for more data. | Assume a plateau establishes a specific cause or demands more sets/km. |
| Rising burden or deterioration | P008 local/general fatigue review; evaluate sleep, illness, fueling, context and measurement; hold progression or reduce/redistribute relevant burden where warranted. | Causal diagnosis or blanket reduction across modalities from one indicator. |
| Secondary objective deteriorates | Verify comparability, evaluate tradeoff and retention commitment; protect secondary outcome or propose explicit priority revision. | Silently drop the secondary objective. |
| New goal, restriction or infeasibility | Update context; if needed propose block revision, retain history. | Reuse prior success to override a current restriction. |

### 4.5 Minimal individual coaching profile (conceptual representation, not a new schema)

Use the existing approved plan/context/revision and actual-outcome histories wherever they suffice. Compute deterministic summaries on demand; cache only if performance/reproducibility requires it, and invalidate or version against underlying observations. Persist decisions and attributable preferences because they cannot be recovered reliably from workout logs alone.

| Information | Category | Retain or compute | Required provenance and update condition |
| --- | --- | --- | --- |
| Current ranked objectives, target dates, preferences, schedule, restrictions | Confirmed athlete context | Persist authoritative revisions | Athlete confirmation, effective time, explicit correction or supersession; restrictions separate from preferences. |
| Current approved block/week/session | Approved prescription | Persist existing immutable lineage | Revision, approval time, constraints, actual execution linkage. |
| Historical strength, runs, nutrition and feedback | Observed / reported facts | Retain canonical source records under owner scope | Source, occurrence, observation/availability time, measurement protocol, completion/quality and corrections. |
| Recent comparable performance references and exposure distributions | Descriptive summary | Compute at decision time; freeze selected inputs with rationale | As-of, filter/version, eligible IDs, excluded reasons, coverage, units and applicable regime. |
| Previously tolerated schedule/dose and productive block summary | Descriptive plus athlete feedback | Compute when needed; retain consequential referenced review | Actual exposure, explicit tolerance evidence and later outcomes, context, gaps. |
| Earlier decision, expected benefit and actual response | Decision/outcome records | Persist approved version and review | Before/after, rationale, evidence, actual adherence, observed outcomes, simultaneous changes. |
| Recurring contextual pattern or preference | Hypothesis or confirmed preference | Persist sparingly if future decisions benefit | Supporting and contradictory IDs, date range/context, uncertainty, status, confirmation and invalidation conditions. |
| Possible physiological explanation | Hypothesis | Usually keep in relevant review, not a permanent trait | Alternative explanations; not a diagnosis or empirically verified mechanism. |
| General evidence and methodology | Shared reviewed science / programming | Refer to exact versioned J1 and rule records | Review status, scope, transfer and source locator; no private athlete history in shared corpus. |
| Known observation limitations / unresolved questions | Quality context | Derive from coverage; persist material user-supplied clarifications | Unverified units, exercise mapping, logging gaps, regime changes; update when resolved. |

Illustrative *human-readable* pattern record (not an API or schema proposal):

```text
Pattern: Prefer hard running away from the priority squat session, when feasible.
Type: contextual scheduling hypothesis; athlete-confirmed preference if explicitly confirmed.
Support: dated, comparable squat sessions S21/S25/S29 with demanding prior runs;
         contextual notes and contrasting sessions S23/S27 without those runs.
Context: same squat variation, current lower-body emphasis and running demands.
Limits: sleep/rest/effort/fueling incomplete; not a causal or universal spacing claim.
Status: tentative; eligible for discussion, not an approved prescription.
Revisit: training phase or run intensity changes; conflicting comparable sessions;
         athlete correction; new restriction or lost observational support.
```

An athlete's confirmation of a preference may justify honoring it, even without confirming the mechanism. Preserve both supporting and disconfirming observations. Correct or retire the pattern rather than overwrite prior decision rationale. Distinguish recorded historical knowledge from what the coach knew at the time: a late import may improve today's recommendation but must not retroactively enter a historical decision snapshot. Use occurrence time **and** data-availability/as-of time when replaying. If source correction, deletion or restriction invalidates current support, mark it and re-evaluate; do not erase the historical prescription and authorized rationale, subject to applicable privacy/erasure requirements.

### 4.6 Four synthetic worked examples

All values below are invented fixtures, not personal records, empirical thresholds or approved prescriptions. Each candidate numerical change would need existing contextual rule authorization and athlete approval where it changes a prescription. Assume no current contraindications except where stated. Do not use these values to calibrate universal defaults.

**A — Strength progression across blocks.** Objective: increase paused bench performance; retain running. Historical completed blocks: A, 10 bench working sets/week and 18 km running/week, best measured 1RM 120 kg; B, 14 bench sets and 25 km running, 100 kg × 6 at reported RPE 9 followed by an estimated 1RM improvement; current C, 8 bench sets and 24 km running, same bar/bench/pauses, first working set at 95 kg × 5 (RPE 8), then × 6 (RPE 8), then × 6 (RPE 8). All three are confirmed actual sets; some accessory rest times missing. Old block A was months earlier with different concurrent dose; B changed both sets and running. Current results show improved observed same-load repetitions, not proof of a measured 1RM increase or best dose. Options: hold 95 kg at prescribed reps, allow approved repetition progression, or propose smallest feasible contextual load increase when the approved rep/effort target warrants it. Maintain current set count unless another reason justifies change. If RPE unavailable, compare achieved reps but qualify effort. Do not initialize from 120 kg PR or infer 14 sets/week optimal. Follow up on comparable first working sets, secondary running outcome and burden. Approved week remains in force until a changed proposal is approved.

**B — Running progression during changing strength emphasis.** Objective: return to 10 km development without abandoning squat strength. Historical race 44:00, previous completed 35–42 km/week; recent strength-emphasis weeks 16, 18 and 17 km, with two easy and one quality session each, comparable easy route around 5:45/km at reported conversational effort. One hot run 6:05/km with uncertain optical HR. Old 44:00 is context for long-term goal; recent exposure informs starting dose and current field performance, not exact threshold pace. Options: maintain recent running schedule while reintroducing suitable specificity, redistribute sessions to protect squats, or propose bounded increase only when current tolerance, constraints and outcome warrant. Do not prescribe 40 km or race-derived old intervals solely from historical peak. A new standardized assessment may be useful when safe and relevant; no compulsory maximal test. Monitor actual running duration/effort, lower-body tolerance and comparable timed performance. Any changed scheduled week requires approval.

**C — Recurring scheduling difficulty.** Objective: squat strength in a balanced block. Three confirmed squat sessions after demanding prior-day runs: 120 kg × 5 at RPE 9, 120 × 4 at RPE 9.5, 120 × 5 at RPE 9; two comparable sessions with easier preceding days: 120 × 5 at RPE 8 and 120 × 6 at RPE 8. Same equipment and set order; rest and fueling incomplete; one demanding-run day followed poor sleep. Repeated pattern supports a tentative scheduling preference, not proof of interference or a universal required rest interval. Alternatives: move the hard run, move squat while preserving priority quality, reduce a specific local burden, or leave schedule and address fueling/sleep if those are stronger constraints. Propose moving the hard run if feasible without compromising the running objective; hold dose initially to simplify interpretation, not as a mandatory experimental design. Record reason, context, alternative explanations and later comparable performance. A counterexample after a later demanding run weakens the pattern; revise/retire it rather than ignore it. Athlete approves changed slots; preserve original schedule and rationale.

**D — A previously productive strategy stops appearing productive.** Objective: balanced strength and 5 km improvement. Prior block: 12 lower-body sets/week, 28 km/week, improved squat repetitions and timed performance at acceptable reported burden. Recent approved block same nominal exposure, but actual weeks are 12/11/8 sets and 28/24/19 km; one missed interval, two shorter lifts, reported fatigue higher, comparable squat 115 × 5 at RPE 9 versus prior 115 × 6 at RPE 8; recent 5 km assessment absent and easy pace comparison affected by heat. Food logs partial; new work schedule and worse sleep reported. Actual dose/adherence has changed; evidence of strength task difficulty, but no defensible running plateau or calorie adequacy inference. Options: clarify schedule, symptoms and fueling; hold progression and redistribute or simplify relevant burden; if persistent concerning general symptoms refer for qualified assessment per P004/P008; block priority revision only if objectives infeasible. Earlier productive block is useful as a reference under its context, not proof the same dose remains optimal. Evaluate subsequent matched exposure, comparable lifts/running, subjective burden and practical adherence. Changes require approval; if declined, retain current authorized plan unless restrictions block safe execution, in which case flag and defer affected work.

### 4.7 Proportionate evaluation for a single-user coach

**Software correctness** (deterministic and replayable): fixture calculations and unit conversions; eligibility and observation matching; as-of and availability cutoffs; missing vs zero; no unapproved change; new restrictions invalidate stale proposals; repeated frozen inputs reproduce semantic result; previous revisions and rationale recoverable. Test changed source/provider with equivalent canonical observations, and opposite cases with materially different provenance/quality. Use expected admissible choices rather than exact load or pace where several reasonable answers exist.

**Recommendation quality** (human inspection): Is the proposed decision appropriate for the athlete's stated objective and available time? Does it protect secondary commitments, cite eligible history, disclose exclusions and uncertainty, avoid unnecessary changes, and compare feasible alternatives? Does the coach distinguish preference, engineering safeguard, reviewed evidence and observation? Can the athlete accept, decline or change the proposed intent? Record a short accepted/declined/revised reason if the athlete wishes, not a mandatory questionnaire.

**Personal usefulness** (lightweight follow-up): During normal weekly/block review, inspect completed versus planned work, practicality, burden, comparable outcomes, recurring errors, and whether retrieval of past context changed the recommendation for the better from the athlete's perspective. Note the denominator of known outcomes and missingness. If useful, compare a history-aware proposal in shadow mode against the existing simple policy (e.g., repeat last comparable prescription with bounded progression); freeze both before outcome, never execute the shadow plan or claim its counterfactual outcome. Record decision differences and human preference; assess burden and unnecessary changes. No need to run formal randomized trials, estimate treatment effects or build multi-athlete infrastructure. Retrospective improvement and satisfying personal use do not establish general efficacy. If simple policies are adequate, defer complexity.

## 5. Draft J1 evidence catalog additions

Narrow additions only. Two new sources, two measurement claims and two candidate methods are proposed. No new intervention-effect record is necessary for the historical reasoning workflow. The methodological references I03/I04 and statistical identities remain narrative, not empirical treatment effects. J1 can represent the two measurement findings with explicit repeat-test comparator, outcome and horizon; it does not encode a personal pattern, latent state, uncertainty distribution or methodological proof as a scientific claim. Future representation for personal observations belongs outside shared J1; no schema changes proposed.

The JSON below is an additive fragment (not a release). Uses J1 schema v1 field names, exact prior claim keys for method support, and new question IDs. All approvals null, all new sources/claims/methods pending, empty transfer lists; no approval attestation, supersession or withdrawal. Source checked dates denote this targeted inspection, not completed rights or correction verification. Review dates proposed for scheduling, not approvals. Confirm full graph with the current registered loader and staged fragments before integration. New records are not eligible for operational retrieval.

```json
{
  "questions": [
    {
      "id": "individual-strength-repeatability",
      "description": "How repeatable is measured exercise-specific strength or repetition-maximum performance under standardized repeat tests?",
      "gap": "Ordinary submaximal training-set and e1RM repeatability in experienced hybrid athletes remains context-dependent; no individual threshold approved."
    },
    {
      "id": "individual-history-review-methodology",
      "description": "How can comparable historical actuals and prior decisions inform bounded personal coaching choices?",
      "gap": "No direct validation of the complete candidate history workflow; contextual programming judgment and separate review required."
    }
  ],
  "sources": [
    {
      "key": "grgic-one-rm-repeatability@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction; Packet 009)",
      "status": "pending",
      "approval": null,
      "citation": "Grgic J, Lazinica B, Schoenfeld BJ, Pedisic Z. Test–Retest Reliability of the One-Repetition Maximum (1RM) Strength Assessment: a Systematic Review. Sports Med Open. 2020;6:31.",
      "doi": "10.1186/s40798-020-00260-z",
      "record_url": "https://link.springer.com/article/10.1186/s40798-020-00260-z",
      "published_on": "2020-07-17",
      "design": "Systematic review of test-retest reliability studies",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Publisher full-text article and bibliographic record inspected; dedicated correction/retraction audit remains outstanding.",
      "rights": "Open-access publisher article. Catalog use limited to metadata, links and original factual summaries; independent rights review outstanding.",
      "appraisal": "32 studies, total n=1595; 14 studies included previously trained participants. COSMIN appraisal reported moderate or excellent quality; varied tests and descriptive aggregation; ICC is not absolute agreement.",
      "next_review": "2027-02-25"
    },
    {
      "key": "mitter-bench-repeatability@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction; Packet 009)",
      "status": "pending",
      "approval": null,
      "citation": "Mitter B, Csapo R, Bauer P, Tschan H. Reproducibility of strength performance and strength-endurance profiles: A test-retest study. PLoS ONE. 2022;17(5):e0268074.",
      "doi": "10.1371/journal.pone.0268074",
      "record_url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268074",
      "published_on": "2022-05-05",
      "design": "Test-retest laboratory measurement study",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Publisher full-text article and bibliographic record inspected; dedicated correction/retraction audit remains outstanding.",
      "rights": "Creative Commons Attribution license stated on publisher page. Catalog use limited to metadata, links and original factual summaries; independent rights review outstanding.",
      "appraisal": "24 trained adults, standardized pin-supported bench press; repetition tests at relative loads derived from each visit's measured 1RM. Bayesian estimates, short horizon and small sample; no evaluation of coaching policies.",
      "next_review": "2027-02-25"
    }
  ],
  "claims": [
    {
      "key": "trained-measured-one-rm-repeatability@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction; Packet 009)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "individual-strength-repeatability",
        "objective": "assess-measurement-quality",
        "population": "adults-with-prior-resistance-training",
        "experience": "mixed-trained",
        "intervention": "standardized-measured-one-rm",
        "comparator": "repeat-measured-one-rm",
        "outcome": "one-rm-repeatability",
        "horizon": "study-specific-test-retest",
        "block_context": "resistance-assessment"
      },
      "assertion": "Measured 1RM assessments in studies including previously resistance-trained participants generally had high reported relative repeatability with variable absolute relative error.",
      "limitations": "Fourteen studies with previously trained participants; mixed exercises, protocols, training experience and retest intervals. Descriptive medians and ranges, not pooled CIs.",
      "quality": "moderate",
      "assessment": "Moderate for the reported study summaries; low directness for habitual submaximal sets, e1RM or any specific hybrid athlete threshold.",
      "transfers": [],
      "support": [
        {
          "source": "grgic-one-rm-repeatability@1",
          "locator": "Results: Reliability in Relation to Training Status and Familiarization; Table 3 and Fig. 2.",
          "result": "ICC median 0.98 (range 0.64–0.99); CV median 3.3% (range 0.5–7.8%).",
          "restriction": "Measured one-repetition maximum repeatability only; no individual change criterion or treatment effect."
        }
      ]
    },
    {
      "key": "trained-bench-relative-load-repetition-repeatability@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction; Packet 009)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "individual-strength-repeatability",
        "objective": "assess-measurement-quality",
        "population": "resistance-trained-adults",
        "experience": "trained",
        "intervention": "bench-repetition-maximum-relative-load",
        "comparator": "repeat-bench-repetition-maximum-relative-load",
        "outcome": "repetitions-to-failure-repeatability",
        "horizon": "one-week-test-retest",
        "block_context": "resistance-assessment"
      },
      "assertion": "Repetitions to momentary failure at the tested relative bench-press loads exhibited nonzero test-retest error.",
      "limitations": "24 adults; at least one year bench training; loads recalculated from visit-specific 1RM; standardized technique/rest; not ordinary submaximal working sets.",
      "quality": "moderate",
      "assessment": "Moderate for protocol-specific posterior estimates; low directness to a personal absolute-load working set or hybrid fatigue context.",
      "transfers": [],
      "support": [
        {
          "source": "mitter-bench-repeatability@1",
          "locator": "Abstract Results; Results Table 1 and Fig. 2; Methods Experimental approach.",
          "result": "SEM at 90% 1RM 0.7 repetitions (90% HDI 0.5–0.9), ICC 0.65 (0.39–0.83); at 70% 1RM SEM 1.1 (0.8–1.4), ICC 0.86 (0.71–0.93).",
          "restriction": "Relative loads and failure tests; interval is not an individual minimum detectable change, adjustment increment or causal effect."
        }
      ]
    }
  ],
  "relations": [],
  "methods": [
    {
      "key": "context-eligible-individual-history-review@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction; Packet 009)",
      "status": "pending",
      "approval": null,
      "question": "individual-history-review-methodology",
      "description": "Select task- and context-comparable historical actuals as of the decision, separate current demonstrated performance from historical records, summarize exposure and observed direction, and disclose exclusions and uncertainty before ordinary bounded planning.",
      "provenance": "Original candidate programming/engineering methodology, Packet 009 sections 3–4; not a tested intervention.",
      "tradeoffs": "Requires comparable observations or conservative fallback; selection and window choices need review; no universal recency weight, optimal dose or latent fitness inference.",
      "claims": [
        "trained-measured-one-rm-repeatability@1",
        "trained-bench-relative-load-repetition-repeatability@1",
        "outdoor-five-km-typical-error@1",
        "predicted-rir-signed-error@1",
        "morning-mass-variability-active-men@1"
      ]
    },
    {
      "key": "contextual-decision-response-history@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction; Packet 009)",
      "status": "pending",
      "approval": null,
      "question": "individual-history-review-methodology",
      "description": "Retain earlier approved changes and actual response; review supporting and contradictory observations in context; use tentative patterns only for relevant, feasible, reversible proposals and update on new evidence.",
      "provenance": "Original candidate programming/engineering methodology, Packet 009 sections 3–4; not a tested intervention.",
      "tradeoffs": "Observed association does not establish causality. Requires attributable decision and actual execution or qualified recollection; current restrictions and athlete approval govern any change. No physiological parameter estimation.",
      "claims": [
        "habitual-set-maintenance-strength@1",
        "same-session-trained-lower-body-strength@1",
        "adaptive-running-ten-km-performance@1",
        "short-detraining-vo2max@1"
      ]
    }
  ],
  "withdrawals": []
}
```

## 6. Synthetic evaluation cases

Twenty cases target historical reasoning rather than specific numeric prescriptions. All histories and values are synthetic. Use frozen as-of context, prior approved prescription, rule/evidence versions and known coverage. A reviewer defines admissible alternatives before testing. **R** = read-only explanation or feedback request, **W** = proposed week/session change, **B** = explicit block revision. Every W/B requires athlete approval and revalidation of current restrictions; R cannot mutate prescriptions. In all cases preserve historical approved versions, actuals, original rationale, observation snapshots, acceptance/decline history and any later corrections. A new restriction may block unsafe execution without silently activating an alternative. Pending evidence is not eligible operational support.

| Case / policy | Synthetic history and eligibility | Admissible decision and approval path | Prohibited inference / required explanation and preservation |
| --- | --- | --- | --- |
| I-A01 · IA-P01/05 | Old bench 1RM 125 kg; current verified comparable 95 × 5; intervening interruption. | R current anchor; W conservative contextual prescription if changed. | No prescription from PR alone; retain old achievement, current reference and interruption. |
| I-A02 · IA-P01/02 | Same lift, equipment/order/effort; actual 90 × 5 then × 6 and × 7. | R directional improvement; W bounded rep/load option or hold. | No proven 1RM gain or mandatory increase; show dates and actual effort. |
| I-A03 · IA-P02 | One comparable set in current phase, no assessment; previous sets incompatible. | R insufficient evidence; W maintain or relevant assessment. | No plateau diagnosis, manufactured trend or compulsory test; record exclusions. |
| I-A04 · IA-P01/05 | Same exercise label; different machine leverage or ROM. | R distinguish series; W use new equipment anchor or effort-based alternative. | No numeric conversion from unverified equivalence; preserve old series and mapping change. |
| I-A05 · IA-P01/02 | Verified same-load reps improve; RPE missing. | R observed reps change; W hold or progression if independent approved rule suffices. | No invented RPE, no blocking all coaching; disclose reduced effort comparability. |
| I-A06 · IA-P01/02 | Slower run on hotter, hillier route; average HR higher. | R qualify/exclude comparison; W retain plan or conditions-based adjustment. | No aerobic regression claim; retain conditions and HR limitations. |
| I-A07 · IA-P03/05 | Old 10 km PR and 40 km/week; recent confirmed 16 km/week. | R contextualize; W initialize from current exposure, protect lifting. | No race-PR-derived mileage or threshold pace without current evidence. |
| I-A08 · IA-P03/05 | Former 14-set dose; prolonged break and no recent comparable lift. | R ask/review restrictions; W conservative re-entry under reviewed bounds. | No inference old dose remains tolerated; preserve last actual and gap. |
| I-A09 · IA-P03/04 | Current familiar dose associated with continued progress and acceptable tolerance. | R retain; W only if separately justified by phase/objective. | No automatic additional volume; distinguish current dose from maximum/optimal. |
| I-A10 · IA-P03/05 | Same nominal past dose; current comparable deterioration and rising reported burden. | R check exposure and P008 causes; W hold/reduce/redistribute; B if objective infeasible. | No permanent intolerance or one-cause diagnosis; record changed context. |
| I-A11 · IA-P04/06 | Repeated poor squats after demanding prior runs; matched contrasting sessions, fueling incomplete. | R tentative preference; W move a session if feasible. | No causal proof or universal spacing; retain counterexamples and missing factors. |
| I-A12 · IA-P04 | Added sets, removed intervals and increased calories at once; strength improves. | R descriptive joint response; W retain or change for current reasons. | No attribution to added sets alone; record all simultaneous changes. |
| I-A13 · IA-P03/04 | Assigned sessions stable; only half confirmed, some explicitly missed, others unknown. | R differentiate execution/coverage; W simplify schedule or clarify. | No ineffective program conclusion from nominal exposure; show denominators. |
| I-A14 · IA-P04/06 | Increased reported target followed by better lifts; sleep and training specificity also changed. | R association; W retain nutrition if appropriate per P007. | No true TDEE or nutritional causal claim; preserve co-changes and coverage. |
| I-A15 · IA-P05/06 | Changed logging app/practice and weigh-in timing; apparent abrupt trend. | R flag regime; suspend recalibration or seek clarification. | No pooled historical maintenance estimate across incompatible regimes; preserve both. |
| I-A16 · IA-P06 | Previously inferred run-before-squat pattern; new comparable successful instances. | R weaken/review hypothesis; W if current decision warrants. | No cherry-picking or immutable trait; record contradiction and new status. |
| I-A17 · IA-P06 | Athlete corrects past stated preference for morning sessions. | R update current preference through existing context process; W/B only if schedule/objective changes. | No overriding explicit correction with inferred history; preserve previous context revision. |
| I-A18 · IA-P05/06 | New movement restriction after a proposal relying on historical success. | R block stale proposal, flag current affected work; W safe alternative if feasible or defer, B if objective changes. | No automatic approval or unsafe reuse; preserve original candidate and restriction event. |
| I-A19 · IA-P01/06 | Workout occurred before review but imported after it; later assessment improves. | R replay using only facts known at original cutoff; new review can use new data. | No retrospective leakage or rewriting rationale; distinguish occurrence and availability timestamps. |
| I-A20 · IA-P01/06 | Same canonical verified actuals from different providers; one paired case has unknown units. | R/W same semantic decision for truly equivalent data; qualify or defer changed-quality case. | No provider-brand-based conclusions or assumption equivalent when units/provenance differ; retain source identifiers and semantic projection. |

Additional cross-cutting acceptance: no synthetic fixture or pending source becomes an operational empirical claim; no exact answer required when several reasonable proposals respect the objectives and bounds. Decline leaves approved prescription unchanged; revision rechecks context and preserves previous decision history. Passing cases establishes software/policy conformance only, not actual coaching efficacy.

## 7. Research backlog

### 7.1 Identifier reconciliation and remaining questions

Use `P009/IA-01` through `P009/IA-07` for research questions; IA-P01–06 are candidate policy IDs, not questions or J1 vocabulary terms. Retain original EV-01 (detect meaningful individual progress) from P001, EV-02/03 (individual adaptation and prospective multi-objective evaluation) from P003, and EV-02a (feedback-based concurrent decisions). The original broader research questions stay open; this packet narrows the product work to single-user practical historical reasoning and proportionate evaluation, not a silent redefinition.

| Question | Earlier dependency / policy | Priority and outstanding work |
| --- | --- | --- |
| P009/IA-01 Meaningful progress | EV-01; EN-P07, RE-P08, EE-P03 | P0 practical comparison; independently verify measurement error and protocol transfer; no universal change cutoff. |
| P009/IA-02 Historical comparison relevance | EV-01/02; RT-P01, EN-P07 | P0; review eligibility, phase and effort context, actual-match semantics. |
| P009/IA-03 Recency and regime | LP-05, HP-P02/09, EE-P08 | P0; verify changed context and current reference. Re-entry detail P010. No decay model. |
| P009/IA-04 Historical tolerance | RT-P02, CT-P05, HP-P02, RE-P04/09 | P0; preserve exposure/tolerance/outcome distinctions; no personal dose ceiling. |
| P009/IA-05 Earlier decisions | EV-02/02a; CT-P02, HP-P09 | P0 decision trace; causal efficacy remains open. Lightweight follow-up rather than experimental infrastructure. |
| P009/IA-06 Continue/reconsider | EV-02/03; HP-P09, RE-P11, EE-P07 | P0; validate objective tradeoffs, bounded choices and adherence-aware review. |
| P009/IA-07 Coaching knowledge | EV-02/03; existing context and prescription revisions | P0 minimal retrieval/persistence; defer richer profile until concrete need. |
| Original EV-02/03 and P008/RE-10/11 broader questions | Individual causal response, fitness-fatigue modeling, incremental data value | P2/deferred research; not closed or required for single-user MVP. Optional shadow comparison only when decision value is unclear. |

All unresolved questions and independent review requirements from Packets 001–008 remain in force. P010 (longer-term planning, interruptions, resumption and adherence) is next. J3 curation may proceed independently; do not wait for all research before reviewing the small set of policies needed for useful initial coaching.

### 7.2 Narrow extension of J3 curation shortlist

Carry forward the earlier shortlist from P006/008/007 unchanged. Three additions address historical reasoning specifically; all methods and sources remain pending. Prior source/claim review is reused, not repeated approval.

| Decision | References | Independent verification / transfer and numerical guidance | Data feasibility, method review and consequence of deferral |
| --- | --- | --- | --- |
| Choose current comparable strength/run references | I01 `grgic-one-rm-repeatability@1`, `trained-measured-one-rm-repeatability@1`; I02 `mitter-bench-repeatability@1`, `trained-bench-relative-load-repetition-repeatability@1`; P005 `outdoor-five-km-typical-error@1`, P008 `predicted-rir-signed-error@1` | Verify exact protocols, CV/SEM/ICC/HDI definitions and limits; no direct transfer to ordinary submaximal sets or wearable scores. No numeric threshold required for directional observations. | P0, conditionally feasible with canonical history and context. Review IA-P01/02 and `context-eligible-individual-history-review@1`. Deferral: use conservative explicit current references and no automatic trend inference. |
| Initialize/revise exposure after context changes | P002 `habitual-set-maintenance-strength@1`, P006 `short-detraining-vo2max@1`, existing P003/P005/P008 policies | Confirm previous dose and detraining/maintenance endpoint; population and modality transfer needed for empirical assertions. Contextual dose and bounds separate programming approval, no new universal values. | P0, conditional on actual exposure and restrictions; review IA-P03/05. Deferral: conservative starting prescription and direct athlete feedback, no reliance on outdated peak. |
| Retain useful decision-linked contextual patterns | P003 `same-session-trained-lower-body-strength@1`, P005 `adaptive-running-ten-km-performance@1`; I03 narrative and existing revision framework | Verify source scope, no conversion of association to causal history or mandatory spacing. No recurrence threshold; review criteria, alternatives, contradictions and authorization. | P0 minimal trace/retrieval, conditional on execution linkage. Review IA-P04/06 and `contextual-decision-response-history@1`. Deferral: manual contextual notes and ordinary weekly review; no model prerequisite. |

### 7.3 Engineering implications (proposals, not implementation instructions)

Prefer existing actual history, context revisions, approved prescription lineage and deterministic summaries. Verify whether they expose task identity, comparable load convention, actual/confirmed status, outcome links, provenance, corrections, and both occurrence and availability timestamps. If these are incomplete, identify the narrowest engineering gap before adding fields or persistence. A short decision-linked note with supporting observations may be adequate for repeated scheduling preferences; a comprehensive knowledge graph, vector search, athlete embedding, or physiological state model is not justified by this packet.

Essential: contextual personalization, comparable actuals, history-aware bounded choices, transparent as-of reasoning and reviewability. Useful extension: selectively retained recurring context, feedback on previous decision usefulness and optional prospective shadow proposals. Deferred: formal N-of-1 experiments, group comparisons, population causal inference, personalized decay constants, advanced state models, reinforcement learning and large-scale validation infrastructure. Upgrade complexity only for a demonstrated unmet decision requirement, with appropriate validation. No new software schema or code is proposed here.

## 8. Human review checklist

**New evidence and measurement**

- [ ] Grgic: confirm 32 studies and 1,595 participants, subgroup of 14 studies including participants with prior training, reported descriptive medians and ranges, COSMIN appraisal and exact Table 3/Fig. 2 locators. Check whether the reported CV definitions are consistent enough for the narrow assertion; no athlete-specific cutoff.
- [ ] Mitter: confirm participant eligibility, pin-supported technique, relative loads recalculated each visit, test/rest timing, Table 1 SEM/ICC and 90% HDIs. Confirm estimates are not fixed-load or ordinary submaximal training repeatability. Verify exact source versions, corrections/retractions and licensing for both new sources.
- [ ] Check I03/I04 methodological statements and the independence/unchanged-task assumptions of the illustrative error formulas. Do not encode them as treatment effects.
- [ ] Review prior source/claim citations against P001–008; preserve all existing review obligations and scope restrictions. No approval implied by reuse.

**Historical reasoning and coaching methodology**

- [ ] Agree on current task identity, load convention, measurement/effort comparability, eligible actuals, coverage and exclusion rules. Review how to handle missing optional RPE and confounded running comparisons.
- [ ] Confirm that historical PRs and prior tolerated doses remain useful context without automatically setting current capacity, dose, safe limits or maintenance success. Review interruptions and changed regimes separately.
- [ ] Review trend labels, descriptive summaries, contextual recency and acceptable fallback. No fixed historical expiration, universal cutoff or physiological decay constant introduced. Any later quantitative parameter requires separate contextual justification and validation.
- [ ] Review exposure, tolerance, adherence and outcome distinctions; confirm hold is a legitimate choice. Review cross-discipline consequences and current constraints for candidate changes.
- [ ] Review decision history and tentative recurring patterns: supporting/counterexamples, context, uncertainty, explicit preference corrections, invalidation, no causal claim or permanent trait.
- [ ] Verify prescription/adherence/effectiveness requirements independently; optional tracking must not unnecessarily block useful coaching. Confirm scientific readiness, data readiness and authorization are separate.
- [ ] Confirm athlete approval, stale proposal and restriction behavior, historical replay, source corrections and owner-scoped observation handling. No changes to current planner or schema authorized.

**Integration and practical evaluation**

- [ ] Validate the additive J1 fragment against the actual current registered release plus all staged packets; review new scope vocabulary, exact references and quality ratings. Sources, claims, methods and manifest remain unapproved; require separate review before eligibility. Do not synthesize attestations.
- [ ] Review the 20 synthetic cases and admissible alternatives before testing. Verify as-of time leakage prevention and provider-independent canonical equivalence; review errors, uncertainty disclosure, and whether the coach avoids unnecessary changes.
- [ ] Assess actual personal usefulness through routine follow-up and optional shadow decisions. Do not confuse software tests, favorable personal experience or historical improvement with demonstrated physiological efficacy.
- [ ] Keep P010 next and preserve open original EV questions. Defer advanced physiological modeling and population research until the product has a demonstrated unmet need.

**Completion boundary:** This is a standalone research draft. The targeted literature appraisal is not an exhaustive search; the reused evidence has not been independently reverified here. JSON syntax, local prior-fragment uniqueness and references are checked in the delivery process; integration against the current registered loader remains outstanding. No previous packet, repository file, application code, planner rule, registered release or approval was modified.
