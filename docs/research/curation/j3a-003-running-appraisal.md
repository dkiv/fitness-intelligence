# Fitness Intelligence — J3A.3
## Practical running prescription and progression

**Revision:** 0.1 · **Date:** 2026-11-25 · **Status:** AI-assisted appraisal; all evidence, transfers, methods and numerical parameters remain pending independent human review. No operational authorization.

**Proposed method family:** J3-M03 (review identifier only, not a registered J1 method). **Dependencies:** J3-M01 local resistance prescription, J3-M02 block construction, Packets 003, 005, 006, 008, 009 and 010. This document is a review package for J3B.3, not an implementation specification or approved training plan.

## 1. Executive summary

A useful running coach need not estimate latent fitness, recovery capacity, tissue tolerance, physiological thresholds or injury risk. It must know what running the athlete has actually done, what outcome matters, which sessions are familiar, what the athlete can reasonably perform next, and which strength and running commitments cannot silently be sacrificed. Preserve productive exposure by default. Select changes to solve a specific problem, not because a calendar week elapsed or a device reports readiness.

Six existing publications were chosen: Nuuttila (adaptive program), Fokkema (habitual exposure and race performance), Frandsen (session-distance and injury associations), Oliveira (comparative intensity distribution), Seiler/Kjerland (intensity classification), Hurst/Board (field performance repeatability). No new publication is proposed. The first five were inspected beyond their abstracts to varying degrees; Hurst remains abstract-level. This is a focused appraisal, not exhaustive original-data reconstruction. Publication notices, supplements and some figure-level details remain open.

Principal conclusions:

- Nuuttila's matched-pair randomized trial supports considering individualized running programs, not copying its decision rules. The verified 10-km contrast favors individualized training; treadmill maximal speed has an uncertain between-group contrast. Recruitment was 40; the final analyzed sample was 30 for treadmill and 29 for 10 km, not 30 for both. Outside running, participants performed very little exercise. Prepare a new full-text source revision and two narrow claim revisions with explicit endpoint denominators and limitations. The source-access blocker is substantially resolved; figure-level verification and supplementary/missing-data details are not.
- Fokkema's reported mileage and longest-run associations concern preparation for a race. They support asking about actual volume and long-run history; they do not support a target mileage or mandatory over-distance run for an individual.
- Frandsen's distance association concerns a single session relative to its preceding 30-day maximum, not the conventional weekly 10% rule. Overuse injury is the modeled outcome (1,311 reports); 1,820 is the broader injury total including traumatic injuries. A large distance extension merits scrutiny, but neither staying below a category boundary nor using a weekly ratio proves safety.
- Oliveira's pooled comparison finds a small VO2peak advantage for polarized training and no demonstrated time-trial advantage. A majority-easy schedule with purposeful demanding work is a defensible starting convention, not a universal 80/20 optimum. Seiler shows the same work can yield strikingly different session-count and HR-time percentages; always name denominators.
- Hurst's repeated 5-km performances illustrate ordinary test variability. Repeat comparable tasks and distinguish observed change from sustained improvement; do not impose its group typical error as an individual progression threshold.

**Recommendation:** consolidate M03 into three review bundles: M03a — references, initialization and session prescription; M03b — exposure progression and execution-aware adjustment; M03c — concurrent protection and response review. J3B.3 should refine the parameters and exercise these bundles inside M02's existing block/weekly approval architecture. No FIT decoding or quantitative HRV is required for the initial useful coach. Novel running progression remains unauthorized until the relevant method, parameters and software path are reviewed.

## 2. Selected coaching capability and scope

### 2.1 Repository and predecessor verification

Read-only `main` verified at [`0c96d39ee3596a8304c63cda59335c73d6d2b00e`](https://github.com/dkiv/fitness-intelligence/commit/0c96d39ee3596a8304c63cda59335c73d6d2b00e), 2026-11-25. The [research index](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/research/README.md) now includes Packet 010 and J3A.1 and reports 61 questions, 85 source revisions (81 distinct DOIs), 111 claim revisions, four relations, 35 methods and zero withdrawals in the combined candidate. These are repository-reported counts, not a fresh execution of the catalog validator. No claim that separate J3A.2/J3B.2 staging branches have merged; use the local predecessor deliverables as candidate methodology.

Inspected exact [005](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/research/drafts/005-evidence-additions.json), [008](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/research/drafts/008-evidence-additions.json), [009](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/research/drafts/009-evidence-additions.json), 006 and 010 draft method references, [005 measurement appraisal](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/research/005-running-development-measurement.md#28-dedicated-measurement-and-proxy-validity-assessment), [008 protocol audit](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/research/008-integrated-recovery-autoregulation.md#detailed-protocol-audit-f1921-not-a-deployable-rule), and current endurance and planner outcome contracts (section 5.3). Reviewed prior M02 envelope examples from the supplied J3B.2 document. J3A.1 Petré and J3A.2 Hickson/Huiberts findings are reused as previously appraised pending context, not reverified or counted as new studies.

### 2.2 Decision scope

Given an approved block, its ranked outcomes, named exposure floors and ceilings, dates/purposes, local lifting schedule, constraints, recent running exposure and performance, and optional feedback: propose a feasible upcoming running prescription, review actual execution, and recommend hold/progress/reduce/redistribute/defer or explicit block reconsideration. Preserve prior approvals. An execution choice inside an approved interval is different from a changed future prescription. M03 must not independently expand M02 bounds or override M01 strength commitments. It produces structured candidates for the existing planner and validator, not a parallel engine.

Initial running capability should work for recreational runners with regular recent training, hybrid athletes with modest running-specific history, or a lifter returning from interruption. General aerobic capacity, old personal bests, strength experience and other sports do not establish recent running exposure. Beginners need a separate conservative initialization branch; elite high-volume templates do not transfer automatically. Clinical diagnosis, rehabilitation clearance, overtraining diagnosis, race taper optimization, numerical readiness and physiological state estimation are deferred.

### 2.3 Source selection

| Publication | Essential decision | Why selected | Access this review |
|---|---|---|---|
| Nuuttila | Is adaptive endurance programming defensible? | Direct intervention in recreational runners; explicit outstanding J1 access issue | Original article text (PMC indexed and publisher excerpts, tables/captions; journal PDF text); figure image and supplements not verified |
| Fokkema | What habitual exposure context matters? | Recreational race-specific dose and long-run associations | Publisher HTML Methods/Results/Table 3 and participant flow excerpts |
| Frandsen | How should unusual individual-session extensions be reviewed? | Large prospective cohort with recorded session distances | Publisher original indexed Methods/Results excerpts; direct fetch blocked; tables/supplements not fully inspected |
| Oliveira | Is one intensity distribution demonstrably superior? | Comparative synthesis, distinct endpoints | Publisher HTML Methods/Results §§3.4–3.8, abstract, figure captions; supplements not fully inspected |
| Seiler/Kjerland | Which intensity denominator is valid? | Direct same-training classification comparison | Publisher original article excerpts, Tables 1–2 context and Fig. 3 results text |
| Hurst/Board | What can a field test establish? | Practical repeatability of a comparable run | Publisher abstract; full report not verified |

Do not broaden into a new review of threshold estimation, injury prevention, wearable sensors or endurance periodization. Defer Filipas/Rosenblat until a concrete distribution choice requires distinguishing direct trained-runner comparisons from mixed-mode syntheses; Buist/Ramskov are useful next checks if a novice or injury-policy intervention is proposed, not prerequisites for holding familiar work. Galbraith, Shushan, Molina-Garcia and Smyth stay pending as Packet 005 measurement context. None of the latter is newly appraised here. Advanced model parameters and lactate/ventilatory testing are optional specialized extensions.

## 3. Original-source verification and scientific appraisal

### 3.0 Verification conventions

Reviewed 2026-11-25. DOI and bibliographic identity checked against publisher or indexed original publication. Targeted correction/retraction searches returned no identified correction or retraction of the six selected reports in the retrieved results; this is **not** a complete Crossmark, publisher-notice or retraction-database audit. Publisher access varied, and article-level text access does not imply full figure or supplement inspection. Retain metadata, result locators and original factual summaries only; verify intended-use rights before release. The original evidence records are pending; all dispositions below are recommendations only. No human approval is implied.

### 3.1 Nuuttila et al. — individualized endurance training

**Source:** `nuuttila-adaptive-running@1`. O-P Nuuttila, A Nummela, E Korhonen, K Häkkinen, H Kyröläinen. Individualized Endurance Training Based on Recovery and Training Status in Recreational Runners. Med Sci Sports Exerc. 2022;54(10):1690–1701. [DOI 10.1249/MSS.0000000000002968](https://doi.org/10.1249/MSS.0000000000002968); [PMC9473708](https://pmc.ncbi.nlm.nih.gov/articles/PMC9473708/); [PubMed 35975912](https://pubmed.ncbi.nlm.nih.gov/35975912/). Online 17 August 2022, October issue; CC BY 4.0 stated. Original article text retrieved independently through indexed PMC and publisher passages; Methods Participants, Study/Training protocol, Table 1, Table 2, Figure 1 caption, Training/recovery monitoring, Statistical analysis, Results Training characteristics, Performance/laboratory tests, Table 3, Figures 2–4 captions and corresponding prose inspected. Direct PMC re-open produced a challenge; DOI direct fetch was blocked. A journal-layout [PDF text copy](https://0rir.fr/wp-content/uploads/2024/10/msse-54-1690.pdf) was available via indexing, but screenshot retrieval failed (404). Do not claim visual confirmation of the flowchart arrows or full supplementary audit. No supplement was independently retrieved. Publisher Crossmark and rights verification remain open.

#### Population, allocation and analyzed denominators

40 recreational endurance-trained adults recruited, 20 women and 20 men, healthy, already running at least four times weekly; screening included ECG reviewed by a cardiologist. Planned sample size 15/arm using prior treadmill-speed effect assumptions. After three-week preparation, matched pairs on sex, treadmill/10-km performance and training volume, then randomized. Seven dropouts (three during volume, four during interval); PD four (two illness, two lower-extremity injury); IND three (personal reason, illness, lower-extremity injury). Three further finishers excluded (PD: low main-session adherence below 90%, illness lasting more than two weeks around final tests; IND: interruption over two weeks in interval phase). Arithmetic if all reported recruits were allocated: 20 per arm implied by final plus losses; not a separately verified allocation-flow count. Final 14 PD (7 women) and 16 IND (8 women); one additional PD participant lacked final 10-km test after becoming ill. Thus 13 PD versus 16 IND for 10 km, 14 versus 16 for treadmill. See Participants and Table 1. Mean ages 34 and 37 years, mean baseline VO2max 45.7 and 46.5 mL/kg/min respectively. Specific allocation concealment, exact randomization sequence and missingness handling not independently established. Analyzed sample is not a demonstrated intention-to-treat estimate. Attrition/exclusion could bias estimates, especially if tolerability differs; injury counts cannot support relative safety inference.

#### Assigned programs and tests

Three-week PREP, then 6-week VOL and 6-week INT; T0 before PREP, T1 after PREP, T2 after VOL, T3 after INT. Usual frequency/duration in early PREP, mostly low-intensity running plus one moderate session/week; final PREP week reduced by 25%. First two weeks provided the volume baseline. PD is baseline-scaled, not a generic fixed mileage plan. Table 2 reconstructs VOL weekly duration multipliers relative to baseline: 1.10, 1.20, 0.75 times preceding week, 1.30, 1.40, 0.75 times preceding week. Other sessions include basic low-intensity 30–90 min, longer low-intensity >90 min and a 30-min moderate component. Laboratory lactate thresholds determine the HR bands, not a generic HRmax percentage. INT: prescribed three HIT sessions in intensive weeks and one in recovery weeks, with 25% volume reduction in recovery weeks. Each HIT session has six 3-min maximal sustainable work intervals and 2-min recoveries between them, plus warm-up/cool-down. These are descriptions of assigned research work, not recommendations. IND used similar frequency and placement structure but varied duration in VOL and HIT frequency in INT. Participants could retain familiar other activities; reported other exercise was only 0.2 ± 0.3 sessions/week. Diet/fluid habits were not standardized by instruction.

The test week placed treadmill testing before the 10-km field test with at least 48 h between days; matched time of day within ±2 h, preceding rest day, no HIT or long runs on the two preceding days. The field test used a flat 1.6-km asphalt circuit with an extra 400 m, standardized 15-min warm-up with accelerations, and small-group running. Treadmill maximal speed is protocol-specific; it is not 10-km pace or VO2max. PD's programmed recovery week and IND's adaptive recovery arrangement differed; final IND review capped HIT before testing. Test freshness may contribute to observed differences; the authors explicitly discuss this possibility. Do not attribute the full effect to chronic fitness change or require maximal testing for M03.

#### Adaptive intervention reconstruction (descriptive only)

| Element | Independently supported original-text detail | Review limit |
|---|---|---|
| Schedule | Monday and Thursday evaluation, governing next 3–4 days, rest or active recovery on review days | Not a universal frequency or recovery requirement |
| Volume | Initial 1.10 times baseline session duration; progress by 0.05 times baseline (additive on baseline coefficient), hold current level, or reduce current volume by 25% | Not 5% compounding; not the conventional weekly 10% rule |
| Interval | Start with one HIT per review block; increase number up to schedule-dependent maximum two or three, or remove HIT and reduce volume 25% | No automatic interval prescription for a lifter |
| Recovery return | Return to previous level or next VOL level according to markers; INT restarts with one HIT; last review caps HIT at one | Exact complete Figure 1 branching not visually verified; do not reconstruct unknown branch precedence |
| Nocturnal HRV | Polar wrist PPG, four-hour segment starting 30 min after detected sleep onset; average RMSSD log-transformed; 3-day HRV quantity appears in analysis; rolling four-week mean ±0.5 SD; either tail outside range adverse in this study | Exact boundary averaging/update inclusion and minimum valid nights need final figure/protocol check; not interchangeable with Garmin unverified overnight/weekly values |
| Subjective recovery | Daily morning 1–7 scale anchored at 4 normal; lower-limb soreness, fatigue, sleep quality, stress collected. Soreness/fatigue used for decision assessment; values >5 adverse in stated convention | Exact joint item aggregation and decision lookback not established here; no universal fatigue cutoff |
| HR–running-speed index | Prefer 5–10 min warm-up on flat ground (≤5 m ascent/descent), manually checked; move continuous segment or use eligible ≥2-min interval segment if necessary. Individual reference from previous two weeks; decrease beyond 0.50 adverse | Requires comparable paired HR and speed, protocol and valid anchors; no inference from whole-run means |
| Missing observations | Authors describe replacing noneligible segment with eligible alternative where available; not a demonstrated general missing-signal decision rule | Missing-data branch, valid-day denominator and raw algorithm remain unresolved. Never code a guessed branch. |

For traceability, the HR–speed index is speed minus `(HRavg − HRstanding)/k`; `k = (HRmax − HRstanding)/Speak`. Standing HR was estimated as PREP mean nocturnal resting HR +26 bpm. Maximal HR and peak speed from T1 treadmill testing. A 0.50 decrease is expressed in the paper as roughly 3–4 bpm at the same speed; the relationship is athlete/protocol dependent. This formula and all study values are **not candidate M03 thresholds**. The trial used HR chest sensor during running and manual segment screening, not a simple consumer daily score. The threshold references are individualized by protocol. The figure caption describes a two-thirds-normal return condition, but the entire three-factor voting logic, subjective grouping and missing-marker handling are not independently established; this remains an algorithm-replication blocker, not a blocker to a narrow endpoint claim.

#### Achieved exposure and adherence

Original Results Training characteristics and Figure 2 prose: total VOL+INT duration PD 56.9 ± 13.0 h, IND 54.7 ± 9.0 h; sessions PD 52 ± 11, IND 53 ± 7. PD weekly frequency PREP/VOL/INT 4.2 ± 0.9 / 4.5 ± 1.0 / 4.3 ± 0.9; IND 4.2 ± 0.6 / 4.4 ± 0.6 / 4.3 ± 0.6. HIT sessions in INT PD 13.6 ± 0.5 (13–14), IND 15.8 ± 4.3 (10–25); Discussion says 15.6 rather than 15.8, so use Results and flag discrepancy. IND adjustment proportions were 55% ± 12% hold, 35% ± 10% increase, 10% ± 8% reduce. Average distribution and total training exposure did not show statistically significant group differences; not dose equivalence. Variation between individuals and week structure differed. Achieved total sessions are not proof of perfect adherence; the exclusions above and absence of a fully reconstructed per-participant adherence denominator remain relevant. No independent participant-level data audit.

#### Endpoint appraisal

| Claim revision | Original extracted claim | Independent finding and uncertainty | Disposition |
|---|---|---|---|
| `adaptive-running-ten-km-performance@1` | Individualized program improved 10-km performance more than predefined | T1→T3: IND −6.2 ± 2.8%, PD −2.9 ± 2.4% (SD); between-group ES 1.23, 95% CI 0.42–2.02, p=.002; group-time interaction p=.006. n=16/13. Descriptive difference −3.3 percentage points is not the adjusted contrast or individual gain. Results Performance and laboratory tests, Fig. 3 | Revise to @2, exact denominator, attrition and comparator/testing context; retain magnitude |
| `adaptive-running-max-treadmill-speed@1` | Both programs improved; between-group contrast uncertain | IND +4.0 ± 1.9%, PD +3.0 ± 2.4%; between-group ES 0.46, 95% CI −0.27–1.18, p=.322, n=16/14. Results Performance and laboratory tests, Table 3 | Revise to @2, new source link and denominator; retain uncertainty |

Analysis: repeated-measures ANOVA for time/group interaction, within-group Bonferroni comparisons, simple between-group contrasts; T0 performance used as covariate for between-group analysis. Reported ES are Cohen's d (Table 3 entries are within-group values; use Results prose for between-group changes). No isolated component contrast; several outcomes and time comparisons, limited sample, possible post-randomization selection and test-day fatigue confounding. The final field-test contrast is promising, treadmill estimate compatible with a range of effects. Neither the absence of an endpoint difference nor similar average exposure demonstrates equivalence. Categories of response use T0-to-T1 variability after PREP, not a stable untreated repeat-test estimate. Do not classify a permanent responder phenotype or import a personalized threshold.

**Applicability:** strong relative directness to recreational runners with four runs/week; low directness to substantial concurrent lifting or low-running-exposure athletes. No trial of M01+M02+M03, performance-only comparison, HRV ablation, or validation of each adjustment increment. Supports considering individualized adjustments, including holds; does not establish the necessity of any input, specific marker, threshold, review schedule or progression step. Independent reviewers may accept a narrowly scoped result without approving the complete algorithm. Exact pending replacement candidates in Appendix A.

### 3.2 Fokkema et al. — habitual exposure and race performance

**Source:** `fokkema-running-dose@1`. T Fokkema et al. Scand J Med Sci Sports. 2020;30:1692–1704. [DOI 10.1111/sms.13725](https://doi.org/10.1111/sms.13725), online 18 May 2020; [publisher original](https://onlinelibrary.wiley.com/doi/full/10.1111%2Fsms.13725). Inspected Methods/Results, Fig. 1 flow as reported, Tables 1–3, particularly Table 3 adjusted contrasts. License and correction status need final review.

Observational analysis nested in INSPIRE trial; training exposure not randomized. 997 of 1,336 long-distance registrants responded to the first follow-up questionnaire: 556 half-marathon and 441 marathon; 432 and 341 finished respectively. Excluded 339 (25.4%); included participants differed in age, BMI, experience and club membership. Mean age 42.2 years, 65% male, median experience about five years. Reported preparation volume, pace and longest run collected by questionnaire in the pre-event period, not prescribed by investigators. Multiple linear/logistic regression with age, sex, BMI, experience, prior injury and training characteristics; exact regression complete-case denominators not independently reconstructed.

`habitual-mileage-half-marathon@1`: >32 versus 20–32 km/week, adjusted finish-time coefficient −4.19 min (95% CI −6.52 to −1.85). `habitual-long-run-half-marathon@1`: >21 versus 15–21 km longest run, −3.87 min (−6.31 to −1.44). Table 3 confirms both. Injury odds for these categories were 0.97 (0.63–1.50) and 0.83 (0.52–1.30), respectively; imprecise observational contrasts, not evidence of no risk. No claim that increasing an individual's volume would save four minutes. Selection among finishers, reverse direction of causation (fitter athletes can run more), self-report error, pace/ability, changing load and unmeasured concurrent training constrain transfer. Retain both existing claims after human review; no numerical correction required. Use the actual habitual dose and race-specific duration when planning. Do not use category boundaries as minimums, require exceeding race distance, or infer injury safety.

### 3.3 Frandsen et al. — individual session distance and overuse injury

**Source:** `frandsen-session-distance@1`. JSB Frandsen et al. Br J Sports Med. 2025;59:1203–1210. [DOI 10.1136/bjsports-2024-109380](https://doi.org/10.1136/bjsports-2024-109380); online first 7 July 2025 (issue publication August); [publisher original](https://bjsm.bmj.com/content/59/17/1203), [PubMed 40623829](https://pubmed.ncbi.nlm.nih.gov/40623829/). CC BY-NC stated. Retrieved original abstract and indexed Methods Exposure, Confounding, Results and Limitations passages; direct publisher re-open blocked (403). Full Table 1–3 and Fig. 3 visual and supplements not independently inspected. Retain abstract access classification conservatively until complete record audit; do not misstate the extent of text inspection.

Prospective 18-month cohort of device-using adult runners. 5,205 included; mean age 45.8 (SD 10.4), 22.1% women, median 9.5 years running experience (IQR 4–20); 588,071 sessions. 1,820 participants reported injury; 1,311 overuse (primary outcome) and 509 traumatic (competing risk). No training assignment. Exposure is current session distance divided by longest session distance in preceding 30 days, expressed as relative change; closely spaced recorded runs (pause <15 min) were joined, including interval sessions. Injury self-report assigned to most recent run up to 10 days before report. Multistate Cox models use running sessions as time scale; baseline previous problems, BMI, sex, age and experience included as confounders. Cohort selection, missing reports, activity coverage, timing assumptions, prior symptoms, time-varying load/terrain/intensity and competing risks limit causal interpretation. No analysis validating personalized effect modifiers or exact hybrid strength context.

`single-session-distance-injury-association@1` correctly reports the hazard-rate ratios for overuse outcome relative to regression or ≤10% increase: >10–30% 1.64 (95% CI 1.31–2.05), >30–100% 1.52 (1.16–2.00), >100% 2.28 (1.50–3.48). The middle point estimate is below the smaller-spike estimate; do not assert a strictly monotone dose response from these bins. Weekly ACWR association was inverse; week-to-week ratio showed no association. The reference category includes reductions and small increases; it is not a zero-risk control. Do not interpret HRR as absolute injury probability. The paper itself calls for causal prevention validation. The authors' proposed cutoff is an interpretation, not a validated intervention effect.

**Disposition:** retain existing scoped claim pending full source and model verification; no numerical change. Distinguish primary overuse outcome from all injuries in review notes. A larger-than-familiar distance is a contextual prompt to review route, intensity, other running, strength and tolerance. A missing preceding maximum is unknown, not zero; not a license to progress. Repeated increments, even below 10%, may be inappropriate. No automatic safe or unsafe classifier, weekly rule, ACWR prescription, or injury diagnosis. Review exposure grouping and zero-history handling before any literal reproduction of the study calculation.

### 3.4 Oliveira et al. — polarized versus other distributions

**Source:** `oliveira-polarized@1`. P Silva Oliveira, G Boppre, H Fonseca. Sports Med. 2024;54:2071–2095. [DOI 10.1007/s40279-024-02034-z](https://doi.org/10.1007/s40279-024-02034-z), [publisher version](https://link.springer.com/article/10.1007/s40279-024-02034-z), online 8 May 2024, CC BY 4.0. Inspected Methods/Results §§3.4–3.8, including Figs. 4/5 results and Table 2–3 subgroup discussion. Supplementary RoB/GRADE and individual trial achieved doses not independently audited.

17 studies, 437 subjects, ≥4-week interventions, mixed endurance sports/training levels, randomized and nonrandomized designs, random-effects standardized change synthesis. Comparators combine threshold, pyramidal, HIIT and other approaches. Assigned and achieved distribution definitions are not interchangeable; trial-level dose/adherence heterogeneity requires separate extraction if adopting a specific distribution. Review rates certainty high, but randomized trials largely have some risk-of-bias concerns. Do not promote this grade to high certainty for hybrid transfer. Sex subanalysis not possible; subgroup results depend on study-level classification. Search ended October 2022.

`polarized-pooled-vo2peak@1`: 11 studies, n=284, SMD +0.24 (95% CI 0.01–0.48), I²=0%. `polarized-pooled-time-trial@1`: n=221, SMD −0.01 (−0.28–0.25), I²=0%. Both match Results §§3.5.1–3.5.2. Highly trained subgroup VO2peak SMD 0.46 (0.10–0.82) and short-duration subgroup 0.40 (0.08–0.71) do not alone establish effect modification; do not interpret their significance as proof of subgroup differences. No demonstrated advantage in time trial, time to exhaustion or threshold speed/power outcomes; no equivalence proof. Direction coding of standardized TT not a predicted number of seconds. Retain both after human review with outcome-specific scope. Rosenblat/Filipas and other reviews may share trials; no independent corroboration claim here. No universal polarized prescription, 80/20 ratio, or superiority for an experienced strength athlete training three days/week. Pragmatic majority-easy sessions with a familiar demanding stimulus remain reviewable independently of the VO2peak claim.

### 3.5 Seiler and Kjerland — denominator and session purpose

**Source:** `seiler-kjerland-classification@1`. KS Seiler, GØ Kjerland. Scand J Med Sci Sports. 2006;16:49–56. [DOI 10.1111/j.1600-0838.2004.00418.x](https://doi.org/10.1111/j.1600-0838.2004.00418.x), publisher first published 27 October 2004. [Publisher original text](https://doi.org/10.1111/j.1600-0838.2004.00418.x); [PubMed 16430681](https://pubmed.ncbi.nlm.nih.gov/16430681/). Abstract, training characteristics, HR analysis and Fig. 3 prose inspected. Rights and full table/figure checks pending.

Eleven nationally competitive junior male cross-country skiers, 32 days, laboratory VT1/VT2 defined three HR bands. 384 total sessions (347 endurance, 37 strength); 318 endurance sessions had complete HR and session RPE for the comparison. No experimental allocation or outcome comparison; 60 consecutive sessions also had lactate observations. Training differed from recreational running (sport, frequency, age, mode, session length). `intensity-classification-denominator@1` reports 91/6.4/2.6% HR time below/between/above thresholds versus 75/8/17% session-goal categories (session means ± SD 3/3/4 percentage points). Text confirms the values. Distinct denominators and HR lag/recovery account for differences; no universal individual agreement or optimum. Retain after review, explicitly name the complete-record denominator and keep classification separate from physiological intensity. M03 should count intended and confirmed session purpose and, separately, actual demanding work minutes when observed; only report time in zone when contemporaneous boundaries and valid time data exist. Do not call a three-run week with one quality session 33% high-intensity time.

### 3.6 Hurst and Board — field performance repeatability

**Source:** `hurst-board-5k@1`. P Hurst, L Board. Measurement in Physical Education and Exercise Science. 2017;21:10–14. [DOI 10.1080/1091367X.2016.1233421](https://doi.org/10.1080/1091367X.2016.1233421), [publisher abstract](https://www.tandfonline.com/doi/full/10.1080/1091367X.2016.1233421), online 28 September 2016. Full report not independently accessible in retrieved results; abstract-only. No rights or final protocol verification.

15 endurance runners (mean age 29.5 ± 4.3 years, lifetime 5-km best 19:13 ± 1:13), two outdoor competitive 5-km trials across two weeks. No assigned intervention. Mean times 1,217 ± 85 and 1,216 ± 79 s, p=.855. Typical error 14.7 s (95% CI 11.3–21.4); CV 0.95 ± 0.65% (interval 0.59–1.31). `outdoor-five-km-typical-error@1` matches abstract. Do not interpret no mean difference as perfect repeatability. Course/timing, participant details, exact CV calculation, training between tests, exclusions and environmental control not verified. Disposition: retain narrow extraction pending full text. Typical error is not a confidence interval for a single athlete's change, a personal minimum detectable change, or a performance response to a training intervention. A 15-second change can be meaningful in context but not automatically classified as physiological improvement. Use task-specific repeat observations and conditions; avoid compulsory tests or comparing GPS moving time to official elapsed time.

## 4. Existing evidence-record corrections and proposed revisions

### 4.1 Revision ledger

| Existing exact revision | Proposed disposition | Reason / next check |
|---|---|---|
| `nuuttila-adaptive-running@1` | Prepare `nuuttila-adaptive-running@2` (pending) | Full article text located and key protocols/results verified independently. Figure image and supplement remain incomplete. Source access field may be full-text with these qualifications; no claim of complete verification. |
| `adaptive-running-ten-km-performance@1` | Prepare `adaptive-running-ten-km-performance@2` (pending) | Existing numerical result verified; explicitly specify 13 PD /16 IND, comparator and analyzed-sample limitations. |
| `adaptive-running-max-treadmill-speed@1` | Prepare `adaptive-running-max-treadmill-speed@2` (pending) | Existing effect verified; use new source link, 14 PD /16 IND, same cohort and endpoint-specific interpretation. |
| `habitual-mileage-half-marathon@1`; `habitual-long-run-half-marathon@1` | Retain pending | Table 3 contrast matches. No intervention interpretation. |
| `single-session-distance-injury-association@1` | Retain pending; restrict use | Numeric HRRs verified; complete original figure/table and supplementary verification still required. Reference is not proven safe; injury totals must not be confused. |
| `polarized-pooled-vo2peak@1`; `polarized-pooled-time-trial@1` | Retain pending | Correct endpoint-specific contrasts, trial membership/achieved exposure and overlap review outstanding. |
| `intensity-classification-denominator@1` | Retain pending | Correct classification contrast, not efficacy; skiing sample and denominator remain explicit. |
| `outdoor-five-km-typical-error@1` | Additional full-text verification | Abstract supports numeric result, full protocol and statistics unverified. |

Appendix A contains the exact additive J1 candidate fragment. Retain all previous records, source links, review statuses and existing method references. No supersedes or withdrawal edges proposed at this stage; such a change would require the existing J1 review/release process. Null approval and empty transfers for claims are intentional. `quality` remains provisional, not a validated risk-of-bias rating. No new method records are necessary before M03 practical programming review.

### 4.2 Dependency crosswalk

The following methods continue referencing the original exact Nuuttila claim revisions; any eventual migration is an explicit separate review decision, not a find-and-replace:

- Packet 005 `baseline-relative-running-dose-review@1` → 10-km claim.
- Packet 006 `hierarchical-hybrid-block-construction@1` and `bounded-hybrid-review-transition@1` → 10-km claim.
- Packet 008 `recovery-aware-priority-session-review@1` → both claims; `bounded-recovery-review-and-approval@1` → 10-km claim.
- Packet 009 `contextual-decision-response-history@1` → 10-km claim.

The earlier Packet 005 `running-intensity-purpose-and-anchor@1`, `comparable-running-performance-review@1` and `running-durability-descriptive-review@1` remain pending and retain their own exact claims. Packet 009 `context-eligible-individual-history-review@1` uses the 5-km repeatability claim plus nonrunning/measurement findings. These links are not scientific approval. No downstream method relies on a verified individual HRV threshold merely because the Nuuttila source access changes.

### 4.3 Unresolved audit details that should not be inflated into an efficacy blocker

The narrow endpoints can be reviewed without reproducing every branch. The exact Figure 1 decision tree, observation aggregation, missingness behavior, trial registration/allocation concealment, raw-data denominators and actual adherence distribution, trial/supplement completeness and bibliographic notices remain targeted checks. A full-text source access revision is justified by original-text protocol and endpoint inspection, but access does not equal source approval. If a reviewer requires complete figure-level inspection to classify access as full-text, retain `@1` and treat Appendix A as a draft until that check; do not falsely mark the replication audit complete. Resolve the HIT-count discussion discrepancy (15.6 vs 15.8) against Results, not by averaging them. No exact phase parameters are operationalized here.

## 5. Applicability, measurement and transfer assessment

### 5.1 Population and modality transfer

| Context | What transfers reasonably as a candidate method | What does not transfer without review |
|---|---|---|
| Experienced recreational runners with consistent actual exposure | Nuuttila supports considering adaptation; Fokkema supports reviewing distance and longest-run history; familiar task performance helps choose starting work | Exact trial program or effect size, required four runs/week, mandatory threshold tests, injury prediction |
| Recreational hybrid athlete with several lifts and runs | Same running observations and conservative history-aware candidates, combined with explicit M02/M01 commitments | Treating the 10-km trial as a hybrid intervention; ignoring local lifting burden or assuming endurance-specific recovery constants |
| Experienced lifter with little running | Existing goals, calendar and conservative effort-based initiation; optional run/walk | Prescriptions based on strength PR, VO2 estimate, other sport minutes or a former running PR; using the experienced-runner study volume |
| Elite/skier/cyclist cohort | Denominator distinctions and general observation quality lessons | Population training hours, optimal intensity ratios, cross-sport pace/threshold or maintenance equivalence |
| Athlete returning after interruption | Packet 010 re-entry and current reference principles | Universal detraining fraction or automatic restoration of old workload |

M03 requires a running-specific reference independently of the athlete's lifting ability. Current run experience is a regime description: regular recent running, intermittent, recently interrupted, or no credible running baseline. Historical experience informs context; it cannot repair missing current exposure. Track indoor/outdoor, surface, grade and timing convention where relevant. A long easy run, a 10-km race, running economy, VO2max and ability to sustain long-duration work are distinct outcomes. J3A.2 Hickson retained VO2max despite a decline in long endurance with larger duration reduction (abstract-level result); therefore M02 protection must specify the actual outcome. J3A.1 Petré and J3A.2 Huiberts inform scheduling caution, not a universal interference penalty. Their shared primary trials and Schumann overlap remain unquantified; do not count these appraisals as independent replications. Packet 008 acute lifting/run RPE result (`acute-lifting-running-perceived-effort@1`) is pending and not reappraised here. Acute fatigue does not establish chronic loss of adaptation.

### 5.2 Intensity and performance anchors

Definitions below are operational distinctions for M03, not newly validated equivalences. Packet 005 §2.8 and Packet 009 supply measurement methodology; relevant individual source claims not selected above remain pending. Prescription can be feasible with limited data; adherence and effectiveness may not be.

| Observation / reference | Appropriate ordinary use | Validity, reliability and confounding | Do not infer |
|---|---|---|---|
| Athlete-reported effort (anchored 0–10 scale) | Prescribe effort band; record segment effort separately from session RPE, with timing/scale | Subjective, affected by heat, fatigue, novelty, reporting practice; compare like prompts | Exact lactate threshold or interchangeability with lifting RIR |
| Conversational running | Practical cue: can speak comfortable full sentences during easy running; slow or walk when necessary | Speech comfort affected by respiratory conditions, gradient, environment; no formal talk-test validation newly appraised here | A precise physiological threshold, mandatory pace or exact HR band |
| Pace / speed | Useful for familiar flat continuous runs and repeats with comparable measurement; choose conservative band from achieved work | Grade, wind, surface, temperature, GPS, treadmill calibration, pauses, elapsed vs moving time | Faster pace at any effort = aerobic improvement; exact interval execution from whole-run mean |
| Measured exercise HR | Contextual constraint/check for steady comparable effort when sensor and anchors credible | Motion artifact, lag, heat, drift, caffeine, medication, hydration, prior work; wrist and chest readings not automatically equivalent | A high HR proves poor recovery; a low HR proves readiness |
| % HRmax | `100 × HR / HRmax`, useful as a tagged relative measurement with dated credible same-mode max anchor | Age formula and observed peak do not establish true maximum; cross-sport maxima may differ | Physiological zones without validated boundary model |
| HR reserve | `100 × (HR − HRrest)/(HRmax − HRrest)`; requires valid resting and maximum protocol | Error propagates from both anchors, posture/time/measurement mode matter | Same percentage equals %HRmax or threshold percentage |
| LTHR-relative intensity | Use only a dated, specified estimate or measurement with protocol and versioned bands; validate plausible relation to observed work | Different thresholds, field protocols and device estimators; stale/auto-updated values; method uncertainty | Automatic equivalence of LTHR %, HRmax %, HRR % or three-/five-zone labels |
| Field performance test | Actual task-specific elapsed time or achieved speed; repeat conditions and effort | Repeatability is finite; course, weather, pacing, time of day, lifting proximity and preparation matter | A single PR or a small change is a direct estimate of VO2max/threshold |
| Critical speed | Distance-time model from multiple valid maximal efforts with different durations; optional specialized reference | Model/protocol fit, residuals, pacing and uncertainty; D-prime less stable in some protocols; Galbraith claim remains pending | Critical speed equals lactate threshold or is automatically valid from casual GPS best efforts |
| Physiological threshold measurements | Laboratory gas-exchange/lactate protocol, when qualified and useful; preserve threshold definition and date | Protocol, criteria, stage duration, sampling and modality matter; even laboratory constructs differ | Fixed blood lactate concentration or one wearable estimate universally identifies individual boundaries |
| Device VO2max, readiness, HRV, sleep stage | Optional contextual observation with provenance/coverage; no initial quantitative readiness rule | Agreement is not responsiveness; unverified HRV units prevent quantitative use | Measured VO2max, complete recovery or cancellation instruction |

**Intensity model policy:** Store nominal session purpose, prescribed target type and values, actual achieved work, actual reported effort, and observed HR response as separate facts. If target HR is used, pin zone model, anchors, method, date and values in force; if pace, pin seconds/km (smaller is faster); if effort, pin scale and anchor. A coach can use duration plus conversational/effort cue without laboratory calibration. For quality work, use a recent comparable repetition or controlled threshold-like effort rather than force exact pace from an unrelated maximal test. Multiple cues are complementary, not independent requirements; if a valid pace target conflicts with effort or restrictions, permitted execution flexibility and safe reduction take precedence. HR lag in short reps makes HR alone an unsuitable target validator. Distinguish threshold-like sustained work from a lab-confirmed threshold. Do not create new universal HR, pace or lactate-zone numerical conversion tables. A user-selected zone label without its definition cannot support exact comparison.

**Distribution:** Report planned counts by purpose; separately report confirmed executed counts and unknown. Quality minutes are actual work intervals, not total warm-up/recovery/cool-down; long easy time remains easy if observed/confirmed as such, but do not equate all long runs with low total burden. HR time-in-zone requires segment/time coverage and boundaries in force; unknown minutes remain unknown. Example (synthetic): three runs, 30 easy + 40 quality including 12 demanding minutes + 60 long = 130 total minutes. One of three intended sessions is quality; if all 12 work minutes confirmed, 12/130 = 9.2% actual planned-equivalent demanding-work duration. Neither value is a physiological time-in-zone percentage. If achieved intervals unknown, even 9.2% is only a planned fraction. Select distribution to serve goals and feasible workload rather than optimize a ratio.

### 5.3 Canonical observation contract and implementation readiness

Pinned [endurance/recovery contract](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/docs/endurance-recovery.md), [planner outcomes source](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/backend/src/fitness_intelligence/planning/outcomes.py), [snapshot source](https://github.com/dkiv/fitness-intelligence/blob/0c96d39ee3596a8304c63cda59335c73d6d2b00e/backend/src/fitness_intelligence/db/plan_snapshot.py) inspected read-only. M02's prior source inspection established synthetic `PressBlock` and narrow `Generate` support; the current snapshot still declares `Generate.number: Literal[1, 2]`. Existing outcome fields include `run_seconds` and `run_rpe` with manual athlete status; they do not establish arbitrary achieved interval observations. Do not treat design documents as evidence that a general planner is implemented. No live API, historical coverage or provider validity audit executed.

| Canonical observation | Supports | Limits / minimum extension |
|---|---|---|
| Activity identity, dates, sport, distance, activity/elapsed/moving duration, average speed, mean/peak HR, elevation where present | Distinct actual running activity, representative frequency/time/distance and long-session reference if coverage and identity valid | `running_pace()` derives pace from reported positive average speed; not necessarily official elapsed performance. Deduplicate, preserve time zone and source semantics. Unknown sport/zero/inconsistent fields cannot support a numeric prescription. |
| Aggregate split summaries | Descriptive distance/duration/speed of source aggregate; may represent several splits | Not ordered individual work and recovery segments; do not reconstruct chronological repeats, drift or achieved targets from aggregates |
| Performed-workout steps | Instruction (time/distance, target, repeat index/count) | Does not prove execution; zone selector is not historical boundary. Repeats are not achieved laps. |
| Actual achieved intervals | Work/recovery identity, achieved durations/distances and eligible effort/pace (optional HR) aligned to planned ordinals | Not established by aggregate or instructions. Smallest extension: athlete-confirmed completed repetitions and deviations; quantitative pace compliance requires per-interval achieved measurement. |
| Athlete-confirmed purpose/effort and restrictions | Intended/actual purpose, session/segment feedback, completion and meaningful deviations | Voluntary and attributed, not a physiological measurement; whole-session RPE cannot validate individual intervals. Existing manual outcome is limited; general role/ordinal projection needed. |
| Comparable assessment record | Task, distance and elapsed time, course/protocol, conditions and intended effort; pinned date/reference | Race results/manual entry possible; verify actual identity and comparable task. Generalized assessment semantics need review. |
| Optional HR/pace/cadence traces and HRV | Specific analyses when measurement protocol and quality validated | FIT is one future input, not MVP dependency; `source_unit_unverified` HRV must not drive quantitative decisions. No reconstructing decoupling from means. |

Minimum/optional observations by decision (P = prescription, A = adherence, E = effectiveness). All depend on current approved M02 contract, restrictions and availability. Scientific readiness pending across all rows; data readiness is conditional rather than verified for this athlete/provider.

| Decision | P minimum | A minimum | E minimum | Optional / missing fallback |
|---|---|---|---|---|
| Initialize familiar weekly exposure | Recent actual dated running time or distance, frequency, representative longest exposure and current restrictions; athlete report accepted | Session matches and actual exposure by same units, known coverage | Later comparable running/tolerance and secondary strength assessment | Pace/HR, prior blocks; if history absent ask targeted feedback or conservative introductory effort-based work only |
| Easy/long prescription | Familiar duration or distance and effort cue, current schedule and local tolerance | Actual duration/distance + purpose or confirmation as needed | Comparable subsequent task/effort; separate long-duration outcome | HR optional; without effort, report work only and seek feedback if progression depends on it |
| Quality prescription | Familiar repeat/session structure, purpose, current relevant effort/pace reference and feasibility | Athlete-confirmed work/recovery completion or aligned achieved intervals | Repeat comparable work at similar effort or goal-specific test | HR/interval traces optional; if no achieved intervals, do not quantify pace compliance; retain familiar prescription or defer increase |
| Dose change | Sufficient credible actual exposure/tolerance, specific objective, approved bounds and neighboring strength | Exact changed exposure and adherence/deviations | Later comparable response and strength protection | Recent trends and optional feedback; uncertainty → hold, smaller change or ask; no missing=success |
| Recovery/scheduling | Local symptoms/effort, actual adjacent sessions, upcoming priorities, availability | Attributed changed session and observed execution | Subsequent task performance/tolerance | Sleep/RHR/HRV optional context only; no missing or abnormal score alone cancels |
| Assess running improvement | Dated baseline and follow-up comparable actual task | N/A unless assessing prescription match | Same measurement basis, adequate effort/conditions and context | Repeated standardized submaximal task; if incomparable, descriptive observation only |

Record observation IDs, provenance, actual occurrence and available-at time, comparison eligibility and missingness. Packet 009 requires eligibility before recency, no hindsight leakage and old PRs as context, not current capacity. Packet 010 is now present on main; no automatic missed-work debt or peak-workload restoration. Keep explicit elapsed-slot denominator: e.g. two complete, one partial, one unknown = known coverage 3/4, full completion among known 2/3. Missing activity is not a miss. Use athlete-attributed corrections, preserve historical links and invalidate stale proposals; no auto-join by date/name. Future engineering should generalize current planner/observations, not create provider-specific coaching engines.

## 6. Candidate practical running methodology

### 6.1 Interface and decision hierarchy

M02 owns priorities, exposure commitments, phase intent, calendar and permissible adaptation envelope. M01 owns local lifting prescription and changes. M03 owns proposed running prescription and running-specific changes. The existing planner combines proposals, checks feasibility and approves the exact version with the athlete; a local candidate never has independent write authority. Running-emphasis alone does not activate new running bounds: J3B.2 examples currently hold familiar running exposure. A separately reviewed M03 rule and explicitly approved updated block envelope are required before positive running progression. If a block forbids change, M03 returns hold or named block-review requirement, not an implicit override.

Proposed three bundles:

- **M03a — Initialize and prescribe:** current references, representative exposure, session purpose and context-eligible intensity target.
- **M03b — Progress and adjust:** review actual completion/effort and tolerance; choose bounded single-dimension positive change, hold, local reduction, redistribution or defer.
- **M03c — Protect and evaluate:** coordinate M01 and M02, compare subsequent outcomes, distinguish local adjustment from explicit block/context revision.

### 6.2 Reference selection and initial exposure

1. Validate context: primary/secondary outcome rankings, running purpose, event dates, protected dates versus protected purposes, time/equipment, restrictions. Preserve explicit hard constraints and athlete-defined tradeoffs. If conflict cannot be resolved, return named conflict and choices.
2. Verify actual history: partition eligible, contextual-only, uncertain and excluded runs; resolve duplicates and time/distance definitions. Select recent representative completed weeks rather than maximum mileage week or scheduled target. Summarize individual weeks (not just mean): distinct actual sessions/days, total duration/distance where valid, longest representative completed session, highest recent credible single-session distance, number/purpose of demanding sessions and observed demanding-work minutes if known. Keep incomplete weeks separate; never treat absent data as zero.
3. Use task-specific current references: easy/long durations and conversational effort; comparable familiar quality structure, actual repetition pace/effort or recent appropriate field performance; current restrictions and interruption history. For a runner with regular productive exposure, initially maintain it. For sparse running history, select familiar low-demand exposure or introductory run/walk from credible recent work. If no credible running reference, ask about recent comfortable running/walking and symptoms, or offer qualitative conservative introduction pending confirmation. Do not transfer gym conditioning or other sport minutes into running dose.
4. Choose purposes consistent with M02. Easy work supports sustainable running exposure; long work develops/preserves duration-specific capability; demanding work targets a relevant controlled performance demand. Maintenance or transition may use familiar work without obligatory quality. A long session is a local burden even when conversational; no fixed percentage of weekly mileage. For a short-week or interruption, prioritize the agreed outcome and feasibility, not repayment of missed distance.

### 6.3 Prescribing sessions

| Purpose | Contextual candidate prescription (not an empirical optimum) | Execution flexibility and progression evidence |
|---|---|---|
| Easy / recovery-oriented | Familiar continuous or run/walk duration, conversational full sentences, low effort; optional pace band from comparable easy history | Slow/walk/shorten within approved ranges if local fatigue or heat. Never chase a pace on a difficult day. Progress duration only with credible current tolerance. |
| Long easy | Familiar duration substantially longer than ordinary easy run, easy effort; appropriate route, time, access to fluid/fueling | Choose representative longest successful exposure, not necessarily historical maximum. Consider time-on-feet and actual distance; protect outcome not just number of long runs. |
| Controlled threshold-like | Familiar sustained controlled repetitions, e.g. warm-up 10 min, 3×6 min comfortably hard with 2 min easy between, cooldown 8 min (40 min total) | Work effort steady and repeatable, not all-out; optional current pace band; no claim of lab LT. Use achieved reps + effort to progress only one parameter. |
| Faster intervals | Familiar repeatable demanding work, e.g. 12 min easy, 4×2 min controlled hard with 2 min easy between, 10 min cooldown (36 min) | No requirement to reach target HR in short reps. Stop/defer affected work if pace/effort materially deteriorates or symptoms arise. Progress work duration OR reps OR target, not all. |
| Assessment | Agreed task-specific elapsed time or controlled repeated submaximal task, matched conditions and preparation | Optional, not obligatory race/max test; account for adjacent lifting and protected events. No automatic progression merely because test completed. |

Examples assume prior familiarity and approval. In quality examples recoveries occur **between** repetitions only; extra post-final recovery would change total. Distinguish warm-up and cool-down in prescription, include them in time budget. Easy sessions can be prescribed by duration with a generous effort range; distance targets use conservative slow-end time for feasibility. If duration is the principal target, distance remains an observed/estimated secondary exposure, not a hidden second mandatory target. For a no-history athlete, a quality session is deferred, not generated from generic fitness. Any pain that alters gait, worsening focal pain, chest pain, fainting, severe breathlessness or other concerning symptoms warrants stopping affected exercise and appropriate qualified assessment (urgent/emergency if acute/severe). Do not diagnose from data or use normal HR as clearance. For sustained restriction or illness, route to context/block review; clinical return-to-training protocols out of scope.

### 6.4 Execution review and progression logic

Evaluate elapsed prescribed slots against actual work in comparable units. Distinguish full, partial, explicit miss and unknown. Record actual purpose, duration/distance, interval repetitions and deviations if available, reported effort/ability to complete and relevant local symptoms. Separate adherence and quality from direction of adaptation. Improvement at familiar dose supports retaining that dose. A hard session was not necessarily unproductive if it felt hard as intended; conversely a successful completion at unexpectedly high effort is not automatic grounds to increase.

| Situation | Candidate action | Avoid |
|---|---|---|
| Productive schedule, appropriate effort and tolerance | Hold; progress only if objective/phase warrants a specific change and observations support it | Automatic weekly escalation |
| Two credible comparable manageable sessions at current dose, need more easy exposure | Small additional easy duration or redistribution; maintain pace/quality structure | Increase distance, target pace, frequency and long run together |
| Long-duration goal not yet served, familiar long runs manageable | Extend one long run within weekly and session-specific bounds; retain easy effort and review estimated distance as well as duration | Use a group injury HRR as a hard physiological boundary or require over-distance |
| Familiar quality work fully confirmed, appropriate work effort and subsequent tolerance, specific progression need | Change one of rep count, work duration or target; prioritize additional controlled work at same intensity before faster targets, where appropriate; keep total session/time feasible | Add repeats and speed simultaneously or count planned steps as completed |
| Unexpectedly high effort/local fatigue | Hold next progression; slow/shorten affected easy work, reduce reps or replace demanding work with approved easier alternative, move session if feasible; ask targeted context | Diagnose overtraining, injury or a universal recovery delay |
| Missing RPE but task and completion known | Compare actual work descriptively; repeat known prescription if reasonable. For positive change obtain credible manageability/tolerance or another explicitly reviewed fallback; no HR-only success rule | Fill RPE from HR, infer reserve or assume unknown tolerance is good |
| Incomplete historical coverage or unknown outcome | Ask targeted confirmation if decision changes; retain or qualitative fallback; defer quantitative increase | Treat absence as detraining or zero exposure |
| Adherence issue due to logistics | Address time, preference, route or schedule; simplify/redistribute within bounds; no catch-up | Conclude poor adaptation or insufficient physiological stimulus |
| Local restriction or generalized concerning burden | Stop/defer affected work; preserve unrelated feasible work when appropriate; review current restrictions, seek professional help when indicated | Override restriction or diagnose from a wearable |

Before any positive change evaluate local recent/adjacent lifting (movement, load/sets, effort where credible), demanding runs, sports and next protected sessions. Use actual leg demand rather than a combined workload score. A priority run can be preserved by moving an eligible discretionary lift, reducing lower-body accessory work via M01, or changing the calendar; a protected squat assessment may require holding run progression or moving the demanding run. Upper-body work need not be automatically reduced for isolated leg fatigue. If generalized difficulty spans multiple tasks, consider coordinated hold/reduction and context review, without diagnosis. No fixed physiological spacing derived from Petré. Approved spacing constraints are hard scheduling rules, not claims about universal recovery. Optional sleep, HRV and resting HR can prompt questions; never automatically cancel a session solely from a score.

### 6.5 Review procedure and authority (preliminary pseudocode)

```text
review(M02_approved_block, M01_lifting_candidate_or_plan, actuals, context, as_of):
    pin owner, current head, rule/evidence versions, context, observations available at as_of
    if new restriction or concerning symptoms: defer affected work; surface conflicts/referral
    classify actuals and coverage; select comparable task references before viewing outcomes
    build current running exposure and neighboring strength context
    if no credible baseline: clarify or offer conservative qualitative/introductory candidate
    otherwise construct familiar hold candidate; assess objective-specific need for change
    generate single-axis positive changes only when execution/tolerance and reviewed rule permit
    generate eligible local reductions, redistribution, or deferral when needed
    validate all candidates against M02 floors/ceilings, local bounds, protected dates/purposes,
         time including warm-up/rest/transitions, equipment, adjacent-week spacing and M01 changes
    discard candidates with missing essential evidence or violating hard restrictions
    if none feasible: return named conflict + block/context review alternatives (no auto-relaxation)
    select by confirmed priorities, preserving productive work, lowest justified change,
         athlete preferences and stable deterministic tie-breaks; expose alternatives
    render previous vs proposed exact prescription, observed facts, uncertainty,
         programming rationale distinct from empirical citations and approval needed
    unchanged = read-only review; within approved execution range = execution choice
    changed future week = proposal; changed commitments/bounds/objective = explicit block/context revision
    submit/preview/seal/approve through existing owner-authorized commands; recheck stale inputs
    record actual outcomes against in-force approval; compare subsequent task and protection outcomes
```

This is conceptual, not code or a new algorithm approval. A held current plan can still be unsuitable if new restrictions make it unsafe; do not imply it should be executed. If an objective remains unknown because no comparable outcome occurred, report unknown, not maintained or deteriorated. Retain useful contextual patterns with counterexamples and validity conditions, not physiological constants. At mid-block/end review, consider continuation, change or transition with M02; no compulsory taper or test. Scientific source approval and operational rule approval are independent from athlete approval of a particular plan.

## 7. Proposed contextual numerical parameters and unresolved programming choices

These are **candidate starting values for J3B.3**, not empirical optima, injury thresholds or currently authorized rules. P = programming judgment; C = practical convention; E = engineering safeguard. All require context-specific M02 envelope and appropriate review. A stricter approved bound always wins. No number below is inferred from Nuuttila's trial or Frandsen's hazard ratios. Candidate caps constrain *proposed* planned exposure; actual deviations remain observable, not invalid records. No positive running rule may activate in current M02 examples without separately reviewed explicit bounds.

| ID / parameter | Candidate starting configuration / classification | Required observations and scope | Override / fallback |
|---|---|---|---|
| R01 habitual window | 3–4 representative completed weeks, ordinarily last 28 days (C/P) | Running-specific coverage; keep each week, partial weeks separate | Extend under stable regime for sparse history; shorten after interruption; if none ask targeted feedback |
| R02 performance reference | Last 2–3 eligible comparable exposures; recent representative one anchors immediate prescription (C/P) | Purpose, actual work, context/effort as required | One reference tentative for familiar repeat, not sustained trend; old PR context only |
| R03 initial frequency/dose | Keep representative actual frequency and total minutes where productive. For sparse history with credible recent tolerance, e.g. two 15–20 min easy run/walk opportunities (P) | Recent running/walking exposure, absence of unresolved restriction, current availability | No minimum for all; if not plausible choose shorter/qualitative or defer; no automatic quality |
| R04 easy effort | Anchored 0–10 RPE 2–4, conversational full sentences (C/P) | Athlete understands scale and purpose; reported speech/effort | Slower/walk or shorter in heat/fatigue. No mandatory HR target; do not equate range with physiological zone |
| R05 long effort | Same easy conversational intent, familiar representative duration (P) | Completed long exposure and tolerance; time/fueling context | No fixed fraction of weekly dose. If long history absent, ordinary easy work first |
| R06 controlled quality | Work effort about 6–7/10, repeatable, familiar 2–3 × 5–8 min, recovery 2–3 min easy where already tolerated (P/C) | Prior comparable quality, athlete-confirmed manageable effort, relevant goals | Start at known lower familiar structure or defer; no exact LT mapping |
| R07 faster quality | Work effort about 7–8/10, controlled, familiar 3–5 × 1–3 min with easy recovery of similar duration where appropriate (P/C) | Same task history and ability to recover/complete; calendar and strength | No all-out requirement or automatic selection from race PR; reduce reps/pace or omit |
| R08 quality frequency | Initially retain familiar count; when introducing reviewed quality, ordinarily one session/week for established 3–4-run hybrid schedule (P) | Current running tolerance, objective and M02 allocation | Zero for sparse exposure; more only if habitual, specifically justified and approved; no universal quality count |
| R09 easy distribution | Majority of sessions easy/long-easy as a starting convention; no exact ratio (P) | Session purpose counts, actual work time where known | Different goal/phase may warrant different allocation; report denominator; missing purpose stays unknown |
| R10 positive duration increment | One ordinary easy run +5 min, long run +5 min (may consider +10 if familiar larger session and reviewed bound); total weekly increment no more than +10 min per review **and** <=10% of current nominal weekly minutes as administrative cap (P/E) | Credible current actual tolerance, approved predecessor and initial envelope; check expected distance separately | If 5 min exceeds cap, use smaller feasible increment or hold. Not 10% safety rule; no compounding beyond cumulative bound |
| R11 single-session distance check | Inspect representative longest run plus preceding 30-day maximum where coverage verified; flag planned/expected distance materially beyond familiar exposure (E/P) | Valid distance and session grouping/coverage; duration alone cannot guarantee distance | No mandatory 10% threshold, unknown max → don't calculate ratio; use conservative familiar duration/route or ask |
| R12 frequency change | At most +1 easy session per review; redistribute existing weekly duration first (P) | Consistent current schedule, athlete preference and repeated tolerance; suitable time | Split 2×30 into 20+20+20 if appropriate, not automatic added dose; no simultaneous quality progression |
| R13 quality increment | +1–2 min total demanding work, or +1 repetition if within that amount and existing approved time; for longer repeats extend one rep rather than add whole rep (P/E) | Confirmed achieved work and appropriate effort/tolerance; not inferred instructions | Hold if increment would exceed weekly or role-specific bounds; alternatively reviewed pace change at fixed work. No adding speed and work together |
| R14 pace progression | No default automatic sec/km increment; anchor to actual recent comparable work. If separately reviewed, a small contextual change e.g. 5 s/km faster at same structure and effort (P) | Comparable achieved intervals/effort, reliable timing and task; actual improvement or explicit specificity rationale | Do not infer from HR alone or stale threshold; keep same pace/effort when uncertain; smaller/familiar option |
| R15 progress eligibility | Prefer at least two comparable confirmed manageable exposures at current role/dose plus representative week/context (P/E) | Actual execution, tolerance and absence of relevant conflicting commitments | Not a universal adaptation window. Missing RPE can be replaced by credible athlete-confirmed manageability, not imputed HR; without tolerance hold/clarify |
| R16 local reduction | Reduce affected easy duration by 5–10 min or remove one quality repetition / replace with familiar easy work, depending on symptoms/context (P) | Affected task, current restrictions, protected purpose and approved flexibility | Greater reduction or stop when appropriate; no minimum training through concerning symptoms; if outside approved floor escalate |
| R17 cumulative block ceilings | Review explicit M02 running envelope; illustrative initial +20 min/week cumulative and +1 session over six-week baseline for development, no automatic quality-count increase (P/E) | Current actual reference, block dates/objectives and reviewed rule; both weekly and session caps | Tighter athlete-specific floor/ceiling, retained purpose or running-hold block wins. No implied authorization or universal optimal dose |
| R18 simultaneous changes | At most one positive running-demand axis per review; no positive running demand plus positive lower-body demand by default (P/E) | Both M01 and M03 deltas, objective priority and calendar | Frequency redistribution may change distribution without total minutes rise but still review; an explicit jointly reviewed exception is needed for dual increases; upper-body changes not automatically barred |
| R19 reassessment | Next comparable session and weekly review; mid-block/end aligned with M02 (C) | Subsequent actual and feedback; comparable assessments when meaningful | More immediate review for restrictions or concerning response; no compulsory maximal test |
| R20 time budget | Illustrative 10–15 min quality warm-up, 5–10 min cool-down, planned between-rep recovery and explicit transitions (C/P/E) | Actual familiar session, route/setup and available minutes | Shorten discretionary work rather than omit essential preparation; different reviewed structure permitted; evaluate worst permitted duration |

Reconcile examples: 130 min/week baseline, +5 min to one easy session = 135 min (3.85%), within illustrative weekly +10 and 10% ceilings if approved. 40 min/week baseline, +5 = 12.5%, exceeds proposed cap; select +2–4 min or hold, not round up. 3×6 min work = 18 min; adding a full 6-min rep violates R13; 7+6+6 =19 min can be considered with same intensity and adjusted time budget, provided familiarity and all bounds. Adding work may mechanically increase total duration; that incidental change must fit total caps but is not permission to increase separate easy dose or pace. Similarly duration extension can increase actual distance; review expected distance with uncertainty, never claim safety from either cap. M02's cumulative ceiling and M01's per-review bounds both remain binding. A quality-target pace decrease in sec/km means faster, not slower; validate units and endpoint ordering. R10's arithmetic ceiling is administrative and adjustable by reviewed rule; it must not be justified as Frandsen's distance exposure or a universal weekly rule. J3B.3 should consider whether absolute time increments alone are easier to review for very low-dose schedules; do not automatically escalate introductory training under the experienced-runner defaults.

Unresolved decisions for J3B.3: precise effort anchors and feedback schema, eligibility for pace-only fallback (recommend no positive quality increase without tolerance evidence), rounding to practical minutes, quality templates by role, whether work minutes substitute for easy minutes to retain a time ceiling, cumulative ceilings per protected outcome, joint change selection with M01, and how to operationalize exposure without complete interval traces. These are implementation/programming reviews, not calls for broad new literature search. An empirical association does not have to be accepted to choose a conservative scheduling convention.

## 8. Synthetic evaluation cases

All examples are invented and unapproved. Conformance tests evaluate recommendation quality and authority, not physiological efficacy. All cases pin M02, M01, rule/context versions, owner, dates, restrictions, actual provenance and as-of time. Report known-outcome denominators where relevant. In table, **proposal** means new future prescription requires athlete approval; **block** means explicit block/context revision and approval; **review** means unchanged plan/read-only or already approved execution choice. A stopped/unsafe task is not forced pending approval.

| Case | Relevant observations and constraints | Acceptable decisions | Prohibited inferences / required explanation | Authority |
|---|---|---|---|---|
| R-T01 productive experienced runner | 4 representative weeks 3 runs, 130–140 min, easy/quality/long familiar, improving comparable 5 km and stable squat; block permits hold | Retain productive dose; if specific development need and eligibility, one small positive change | No obligation to escalate because improved. Explain actual dose, both outcomes and objective | Review or proposal |
| R-T02 experienced lifter, little running | Strong squat, cycling/field sport, only two short recent 12–15 min easy runs; no unresolved symptoms; 10-km goal | Confirm current running tolerance, repeat short easy/run-walk sessions, defer quality and long extension; if baseline unknown clarify | Strength/general fitness/old PR do not establish running tolerance; explain running-specific reference | Proposal; block if current floor incompatible |
| R-T03 easy run unexpectedly hard | Familiar 35 min at RPE 3; now RPE 6 at slower pace after demanding work, hot day possible, no urgent symptoms | Ask about context; hold progression, slower/shorter easy within range or defer affected work; check next comparable task | No overtraining diagnosis or causal attribution to heat/lifting; one observation not sustained decline | Review inside range; proposal if future changed |
| R-T04 long-run progression | Two confirmed 60-min easy runs with manageable effort, 130 total min/week, long capability objective, approved maximum 65 min and weekly 140 | Propose 65 min at same easy effort, total 135; or hold if strength context/uncertain distance | Explain 5-min choice, estimated distance uncertainty and prior longest reference; no safety guarantee | Proposal |
| R-T05 quality progression | 3×6 min controlled threshold-like work confirmed at RPE 6–7 with stable subsequent squat, 10-min warm-up, 2-min between, 8-min cooldown | Hold or 7+6+6 min at same target, 41 min total if approved; add no separate easy/pace demand | Do not add 6-min full rep under R13 or prescribe faster speed as well; confirmation is not measured LT | Proposal |
| R-T06 uncertain pace/HR comparison | Hilly hot route with high HR vs flat cool prior run; device changed, timing convention differs | Descriptive report, select matched task, prescribe effort/conversation, seek useful context | No running economy, threshold shift or regression inference from incomparable means | Review or proposal |
| R-T07 missing RPE/unreliable HR | Actual easy duration known; watch HR suspected artifact, no effort report | Repeat familiar time with conversation cue; ask whether manageable before positive increase; optionally obtain valid sensor data | No cadence-lock diagnosis solely from summary, imputed effort or exact zones | Review or proposal |
| R-T08 instructions not achieved intervals | Device steps show 6×3 min, aggregate split group, run duration; actual reps not independently confirmed | Report planned structure and observed whole-run work; ask completed work/recovery and deviation; hold; no interval pace compliance claim | Aggregate count or instruction is not achieved interval; explain missing data and required granularity | Review; proposal only on supported alternative |
| R-T09 local leg fatigue, protected run | Hard squats/RDL yesterday, athlete reports leg fatigue, upcoming priority quality run, upper work unaffected; no hard injury restriction | Consider moving quality within approved purpose window; use M01 to reduce discretionary lower accessories or hold; easier alternative if justified | No universal 24/48h recovery interval, no automatic upper-body reduction or HRV cancellation | Proposal for changes; block if protected date/purpose changes |
| R-T10 strength protection conflict | Running emphasis seeks more demanding work; two comparable squat sessions worse at similar effort; protected squat outcome/floor; no additional feasible slot | Verify comparability, hold run increase, redistribute or reduce discretionary work within bounds, M02 review if conflict persists | No proof running caused strength decline, no silent change to protected squat floor; report outcome evidence separately from adherence | Proposal or block |
| R-T11 interruption and unknown | Seven-day travel, two reported short easy runs, no gym, incomplete imports; next block originally planned long progression | Confirm retained actual exposure/current restrictions, conservative familiar return, no catch-up, reassess | Missing record not a missed session, elapsed time not fixed loss or recovery; old maximum not current anchor | Proposal; block if bounds conflict |
| R-T12 outcome unobservable | All prescribed runs confirmed, race postponed, no comparable 10-km assessment | Record adherence success, outcome unknown; agree later test or continue/transition based on context | Do not claim race improvement or maintenance from exposure or wearable VO2 | Review; proposal/block for changed assessment commitment |

Additional technical assertions: same frozen input yields same semantic recommendation and rationale; no fabricated scientific citation; ineligible/pending claims cannot appear as approved empirical support; changed observations or restriction invalidate a stale candidate; no cross-owner evidence, no retroactive reattribution, no duplicate run counting; decline preserves prior head; explicit missed sessions are never turned into repayment debt; count vs time vs distance denominators stay distinct. A future implemented rule must pass these cases plus existing E1/E3 regression and persistence/transaction tests. Accept more than one defensible recommendation if constraints and rationale are satisfied. Do not score hypothetical efficacy as observed.

## 9. Human review decisions required

Consolidate into the following three bundles; exact claim revision traceability remains necessary for any eventual attestation, but do not make the athlete review redundant individual claims for each coaching parameter. Scientific review, methodology review, parameter configuration, implementation validation and operational authorization are separate. The athlete alone approves their specific plan within reviewed safe constraints.

| Bundle | Empirical premises (all pending) | Practical decisions / numerical parameters | Data and fallback | Required human judgments / actions |
|---|---|---|---|---|
| M03a references, initialization, prescription | Fokkema's two association claims; Oliveira's endpoint-specific claims; Seiler denominator; Hurst repeatability; Packet 005 measurement context | R01–09, R20; history-first initialization; familiar session roles; optional HR/pace anchors; preserve easy work | Actual recent running exposure, current goals/restrictions, schedule; optional effort/HR/terrain; unclear baseline → clarify or introductory qualitative choice | Sports-science/coaching reviewer checks roles, effort anchors, population transfer and prescriptions. Athlete selects priorities/preferences and familiar context. Engineer validates unit/target/denominator and unknown handling. After authorization can propose familiar/introductory appropriate sessions; no lab-zone inference or automatic elite template. Cases R-T01/02/06/07/08/12. |
| M03b exposure progression and local adjustment | Nuuttila `@2` candidate endpoints and source; Frandsen association; Fokkema contextual only; no isolated intervention effect of exact increments | R10–16, R19; one-axis small reversible change; observed tolerance; familiar hold; reduction or deferral | Confirmed task execution and credible tolerance for increase; optional aligned intervals/HR; if missing, hold/clarify; no inferred compliance | Expert reviews caps, progression and fallback, including novice/resumption scope and clinical boundaries. Athlete confirms tolerance and acceptable tradeoffs. Engineer checks arithmetic, no catch-up, exact actual vs planned. After authorization propose bounded changes; no injury risk scoring, universal ramp, or HRV algorithm. Cases R-T03/04/05/07/08/11. |
| M03c concurrent protection and evaluation | Reuse pending Petré, Huiberts, Hickson and Packet 008 acute effort; Nuuttila limited hybrid exposure; Hurst and Packet 009 comparison context | R17–19; M02 protected outcomes, M01 coordination, joint positive-demand prohibition, local/global routing, comparable outcome assessment | Current lifting/run actuals and constraints, assessment references; optional recovery observations; outcome absent → unknown | Expert reviews concurrent allocation, meaningful outcome and limitations; athlete sets priority ranking, dates/purposes, accepts block tradeoffs; clinician where restriction/symptoms warrant; engineer validates hard constraints, stale proposals, snapshots and unchanged current fixtures. After authorization bounded proposals and explicit block review; no automatic secondary reduction, physiological spacing or diagnosis. Cases R-T01/09/10/11/12. |

Scientific factual checklist: verify Nuuttila figure/supplements, exact missingness and allocation/endpoint counts, results/Discussion HIT discrepancy, publisher version/notices and rights; Fokkema regression denominators and selection; Frandsen full figures/tables/model/supplement, injury type and grouping; Oliveira study overlap, achieved doses, bias/supplements and transfer; Seiler exact complete denominator/method; Hurst full text and computation. Verify no overlapping trials are treated as separate corroboration. Pending claims cannot become operational through this document. No human attestations have been fabricated. An appropriately qualified running coach/sports scientist should review practical progression and session intensity choices; clinical referral and nutritional safety boundaries need qualified professional review as appropriate. The technically experienced athlete can inspect original results, verify preferences and approve feasible plans, but is not required to serve as clinician or independent sports-science reviewer.

Implementation prerequisites: a generalized running prescription/actual outcome representation with exact task roles and target types, canonical owner-scoped observation projection with coverage, contextual M02 run envelope, general week generation and joint M01/M03 validation, exact approval snapshots and replay, tests for missing data and alternatives. Start with activity summary and athlete-confirmed completion/effort/interval-count deviations; do not require new telemetry infrastructure or a second planner. Richer traces/field tests only when concrete decision needs warrant them. Source eligibility and J1 release validation are separate from M03 engineering. Current synthetic E1/E3 progression is unchanged; do not silently extend its rule or declare these cases implemented.

## 10. Recommended next curation tranche

Proceed to **J3B.3 — Practical running prescription and progression**, not a broader literature survey. Refine M03a–c into deterministic proposal rules and concrete parameters within M02. Construct worked examples for three-run strength emphasis, four-run running emphasis, balanced development and low-running-history re-entry. Include complete session prescriptions and arithmetic, actual/unknown interval observations, progressions in duration vs quality, conflicting strength outcomes and a block revision case. Explicitly define how M03 integrates with M01's positive-change caps and M02's running-hold default. Verify all time budgets, running units and approval authority. Keep separate any new operational milestone that generalizes the current fixture planner. No broad new literature is necessary for ordinary reviewable programming judgments; perform targeted verification only if a concrete decision requires it. Nutrition/fueling and broader recovery integration remain next capabilities after running methodology; advanced physiological modeling, quantitative HRV, formal experiments and event-specific taper optimization remain deferred.

**Limitations and validation status:** This is a read-only scientific and practical appraisal. The original Nuuttila article text, relevant Methods and Results, table contents and figure captions were independently retrieved, but direct re-open and figure screenshot access failed; no supplement or raw participant data audit. Other source access limits are specified above. Correction/retraction and rights checks are incomplete. The proposed JSON below uses observed catalog field structure; only JSON syntax and local reference consistency are checked, not strict combined `CorpusRelease` validation or repository tests. No application logic, repository file, approval status, provider data or registered release was changed.

## Appendix A — Exact additive pending J1 fragment

Preserves existing keys and method references. This is a draft, not a registered release. Source access `full-text` denotes original article text inspection with explicit figure/supplement limitations, not final independent verification. Proposed review dates are administrative reminders only. `scope` values match existing exact claims; no new controlled vocabulary or approved transfer is added. Merge only in the existing staging/review workflow and validate against the full pinned catalog before considering a release.

```json
{
  "questions": [],
  "sources": [
    {
      "key": "nuuttila-adaptive-running@2",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.3)",
      "status": "pending",
      "approval": null,
      "citation": "Nuuttila OP, Nummela A, Korhonen E, Häkkinen K, Kyröläinen H. Individualized Endurance Training Based on Recovery and Training Status in Recreational Runners. Med Sci Sports Exerc. 2022;54(10):1690–1701.",
      "doi": "10.1249/MSS.0000000000002968",
      "record_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9473708/",
      "published_on": "2022-08-17",
      "design": "Matched-pair randomized parallel endurance-training intervention after preparation",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Bibliographic record and original article text independently inspected via indexed PMC and publisher passages; journal-layout PDF text consulted. Direct PMC/DOI re-open and figure screenshot failed. Complete Figure 1 graphical branches, supplemental materials, notices and correction/retraction audit remain outstanding.",
      "rights": "CC BY 4.0 stated in original article; metadata, links and original factual summaries only pending intended-use rights review.",
      "appraisal": "Forty recruited; seven dropouts and three excluded finishers. Final treadmill sample PD 14, IND 16; final 10-km sample PD 13, IND 16. Comparator baseline-scaled with scheduled volume/interval changes. Adaptive multivariable bundle; minimal concurrent other exercise. Verified key protocol and endpoint text, not complete algorithm or missing-data behavior. Results versus Discussion HIT count discrepancy requires review. No component effect or hybrid transfer established.",
      "next_review": "2027-02-25"
    }
  ],
  "claims": [
    {
      "key": "adaptive-running-ten-km-performance@2",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.3)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "running-adaptive-programming",
        "objective": "running-performance",
        "population": "recreational-runners",
        "experience": "recreational",
        "intervention": "multivariable-adaptive-endurance-program",
        "comparator": "predefined-endurance-program",
        "outcome": "ten-km-running-time",
        "horizon": "twelve-weeks-after-preparation",
        "block_context": "endurance-training"
      },
      "assertion": "In the analyzed recreational runners, the multivariable individualized program improved 10-km running time more than the baseline-scaled predefined program from T1 to T3.",
      "limitations": "Forty recruited; seven dropouts and three excluded finishers, one additional PD endpoint unavailable. Endpoint n=13 PD and 16 IND. Small bundled intervention, possible post-randomization selection and test timing/freshness differences; very little other training. No isolated effect of a marker or adjustment rule.",
      "quality": "moderate",
      "assessment": "Original Results and Figure 3 caption verified in article text. Promising direct recreational running comparison with limited precision and hybrid applicability; independent review and complete protocol/notice checks outstanding.",
      "transfers": [],
      "support": [
        {
          "source": "nuuttila-adaptive-running@2",
          "locator": "Methods Participants and Study protocol; Results Performance and laboratory tests, Fig. 3 and accompanying text, T1 to T3",
          "result": "IND −6.2 ± 2.8% (n=16), PD −2.9 ± 2.4% (n=13), mean ± SD; between-group ES 1.23 (95% CI 0.42–2.02), p=.002; group-time interaction p=.006.",
          "restriction": "Six-week volume and six-week interval periods after preparation; analyzed endpoint only, not an intention-to-treat estimate established here. No individual marker attribution, dose rule, or approved hybrid transfer."
        }
      ]
    },
    {
      "key": "adaptive-running-max-treadmill-speed@2",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.3)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "running-adaptive-programming",
        "objective": "running-performance",
        "population": "recreational-runners",
        "experience": "recreational",
        "intervention": "multivariable-adaptive-endurance-program",
        "comparator": "predefined-endurance-program",
        "outcome": "maximal-treadmill-speed",
        "horizon": "twelve-weeks-after-preparation",
        "block_context": "endurance-training"
      },
      "assertion": "Both programs improved maximal treadmill speed from T1 to T3 in the analyzed recreational runners; the between-group contrast was uncertain.",
      "limitations": "Same small trial as the 10-km endpoint, not an independent replication. Endpoint n=14 PD and 16 IND; post-randomization losses/exclusions; protocol-specific treadmill outcome and little concurrent other exercise. Interval permits a range of effects; no equivalence test.",
      "quality": "low",
      "assessment": "Original Results text and Table 3 context inspected. Between-group estimate is from Results prose rather than within-group Table 3 effect sizes. Independent verification and transfer review outstanding.",
      "transfers": [],
      "support": [
        {
          "source": "nuuttila-adaptive-running@2",
          "locator": "Methods Participants; Results Performance and laboratory tests, T1 to T3 between-group contrast in prose and Table 3 context",
          "result": "IND +4.0 ± 1.9% (n=16), PD +3.0 ± 2.4% (n=14), mean ± SD; between-group ES 0.46 (95% CI −0.27–1.18), p=.322.",
          "restriction": "Maximal speed of incremental treadmill protocol, not race performance or VO2max; no component attribution or approved hybrid transfer."
        }
      ]
    }
  ],
  "relations": [],
  "methods": [],
  "withdrawals": []
}
```
