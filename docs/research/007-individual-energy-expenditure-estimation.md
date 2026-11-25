# Research Packet 007 — Individual Energy Expenditure Estimation and Nutritional Adaptation

**Fitness Intelligence | 2026-11-25 | revision 0.1 | AI-assisted research draft; pending independent human review.** Repository: [dkiv/fitness-intelligence](https://github.com/dkiv/fitness-intelligence). Packet 008 was intentionally completed before 007. This packet preserves 001–006 and 008; it does not authorize a release, implement an estimator, change a planner, or prescribe a diet for the reader. Target population: experienced recreational adult athletes who both lift and run. Clinical populations, minors, pregnancy, active eating disorders and medically managed weight changes need separate professional assessment. The scientific findings below are independent of providers; current integration feasibility is a dated contextual assessment.

## 1. Executive summary

**Recommendation:** the first useful estimator should be a conservative longitudinal *reported-intake/weight-response* review (Model B), initialized by an existing tolerated target or a simple population/wearable reference (Model A). An absolute physiological TDEE estimate must be explicitly conditional on assumptions or independently anchored. A richer activity-conditioned model (C) should compete prospectively with A and B, not replace them because it fits historical weight better.

- True energy balance constrains change in stored chemical energy, not kilograms on a scale. Weight can remain stable while tissue composition, water, intake and expenditure change. A stable body mass is not evidence of adequate energy availability or absence of REDs. See Packet 004 and NU-P01/06/07/08; keep their clinical boundaries.
- Absolute intake bias and absolute expenditure are structurally confounded by ordinary free-living observations. Even perfectly recorded scale weight and mutually agreeing biased calorie measurements do not identify both. A stable logging process can make an operational reported-calorie maintenance target useful without identifying true expenditure. The invariance proof in §4 is a mathematical result under a stated observation model, not an empirical finding.
- Athlete-specific resting expenditure equations can be useful starting priors, but do not estimate TDEE without an activity/other-component model. Wearable energy estimates are fallible, activity- and algorithm-dependent proxies, not independent daily ground truth. One recent female-runner study found an accelerometer TEE overestimate of approximately 12% (E08); do not apply its mean correction to another device or person.
- Longitudinal body-weight models have actually been evaluated against DLW/DXA intake-balance methods in CALERIE. They estimate **changes in intake**, not an independently identified absolute TDEE. Group agreement is better than individual agreement (E14). This is encouraging for modeling but not direct validation in hybrid athletes or validation of a target-adjustment policy.
- A weight goal is subordinate to safety and explicitly agreed performance priorities. Increasing running demand, worsening recovery, poor fueling or unintentional loss can warrant contextual investigation or protection of training before calorie arithmetic. Holding a productive target is a legitimate choice. Do not automatically repay wearable exercise calories or remove them on rest days.
- There is no reviewed universal adjustment size, minimum logging-day count, fixed smoothing window, tissue energy density or reassessment interval for this use case. §4 defines how to choose and validate contextual parameters instead of inventing defaults. Model uncertainty must include missingness, bias and structural ambiguity, not just residual variance.

**Readiness:** initial qualitative fueling guidance can be generated without food logs. Numerical population estimates are conditional on context and suitable anthropometrics. Operational maintenance estimation requires representative intake and weight histories plus logging-completeness context. Absolute daily physiological expenditure, decomposition into latent components, and individual energy availability are generally deferred. None of the proposed methods is operationally authorized.

## 2. Scientific evidence table

### 2.1 Question registry and search method

Packet-qualified identifiers P007/EE-01–13 are used throughout. This is a targeted review, not a registered systematic review, duplicate extraction or comprehensive search. On 2026-11-25 searched PubMed, PMC-indexed content and publisher sites for combinations of `athlete resting metabolic rate prediction equations accuracy`, `doubly labeled water athlete validation`, `wearable energy expenditure metabolic chamber free living`, `dietary intake athletes doubly labeled water`, `daily body mass variability active men`, `glycogen body water`, `Hall dynamic energy balance weight`, `Sanghvi validation free living intake`, `intake balance weight maintenance`, `exercise compensation E-MECHANIC`, `resistance exercise energy expenditure methods`, `athlete weight loss rates`, `running energy cost slope`. Prioritized criterion agreement and prospective/intervention designs over correlations; retained relevant older methodological studies and contemporary athlete-specific evidence. Source links are durable DOI or PubMed records, with result locators below. Full-text access is marked only where relevant Methods/Results or publisher sections were inspected; indexed passages are identified separately. Several PMC opens were blocked by reCAPTCHA; abstract-level extractions must not be considered full appraisal. No comprehensive Crossmark/retraction, supplement, license or independent duplicate-extraction audit was performed. New sources remain pending human review even where full text was accessible. Provisional confidence refers to the narrowly scoped result, not the efficacy of a coach.

| Question | Scope | Evidence IDs / analytical sections |
|---|---|---|
| P007/EE-01 | Components and variability | E01–03, E15–16; §4.1 |
| P007/EE-02 | Reference measurement | E02–04; §2.3 |
| P007/EE-03 | Equations and baselines | E05–06; §4.3 |
| P007/EE-04 | Wearable agreement | E07–09, prior Packet 004 |
| P007/EE-05 | Intake reporting | E10, E03, E14 |
| P007/EE-06 | Weight observation | E11–12; §2.3 and §4 |
| P007/EE-07 | Dynamic models | E13–14, E17 |
| P007/EE-08 | Identifiability | §4.2 mathematical analysis; not a treatment effect |
| P007/EE-09 | Operational intake | E03, E10, E14; §4.3 |
| P007/EE-10 | Candidate estimators | §4.3; E05–09, E13–14 |
| P007/EE-11 | Activity covariates | E08–09, E15–16, E18–19 |
| P007/EE-12 | Nutrition adjustment | E20–23, Packet 004/006/008 |
| P007/EE-13 | Incremental value and evaluation | §4.8, §6; direct hybrid trial gap |

### 2.2 Evidence findings

All rows are **pending independent appraisal**; “context” means narrative only, “draft” means proposed J1 claim in §5, not eligibility. Unreported intervals are marked rather than reconstructed from significance tests. Measurements and protocol numbers are not approved defaults. RMR/REE terminology follows the source. kcal/day denotes metabolizable energy or expenditure per day, not a unit of body weight.

| ID / finding and type | Source and exact locator / access | Population, comparison, time horizon | Result and uncertainty | Limitations, hybrid transfer and confidence / disposition |
|---|---|---|---|---|
| E01. Expenditure varies widely across sports; population ranges are not individual requirements. Descriptive review. | Jesus et al., 2025, *Isotope Dilution for Measuring Total Energy Expenditure, Water Turnover, and Total Body Water in Athletes*, [10.1123/ijsnem.2024-0225](https://doi.org/10.1123/ijsnem.2024-0225), abstract Results. | 121 studies, 3,244 measurements across age, sex, sport and tier; 75 studies reporting TEE, varied measurement windows. | Reported TEE across studies 1,939–10,070 kcal/day. Range is not an individual prediction interval. | Measurement counts not unique athletes; heterogeneous sports and time periods; female and elite representation limited. Moderate for descriptive range, low for individual prescription. Context. |
| E02. Subtraction to estimate activity expenditure amplifies error and includes non-activity physiology. Methodological review. | Speakman & Pontzer 2023, [10.1097/MCO.0000000000000937](https://doi.org/10.1097/MCO.0000000000000937), abstract Summary. | Method analysis of TEE from DLW, basal expenditure and estimated TEF; no training intervention. | Authors describe substantially worse precision for residual PAEE (about 3-fold vs TEE; 25–35-fold vs BEE). Not a universal error bound. | Depends on component errors and assumptions; residual also includes thermoregulation and diurnal/stress effects. Moderate methodological warning; context, not a coaching coefficient. |
| E03. Even controlled weight-maintenance intake is only an approximate individual reference. Validation. | Heymsfield et al. 2017, [10.1186/s13104-017-2546-4](https://doi.org/10.1186/s13104-017-2546-4), Results and Fig. 3 (publisher and indexed full-text Results). | Six non-obese adults, inpatient, 3-day adjustment then 10-day constant metabolizable intake with weight constrained within ±1 kg; compare with DLW TEE. | Intake 2390 ± 543 vs TEE 2373 ± 713 kcal/day; ratio 1.03 ± 0.15 (range 0.87–1.27); p=0.96 for mean difference; SDs, not equivalence margins. Weight CV 0.38 ± 0.10%. | Small selected sample, controlled food and environment; no app logs or dual training; group similarity not individual equivalence. Moderate for contrast, low transfer. Draft. |
| E04. DLW reference itself has error. Criterion validation. | Schoeller et al., 1986, *Energy expenditure by doubly labeled water: validation in humans and proposed calculation*, [PMID 3085521](https://pubmed.ncbi.nlm.nih.gov/3085521/), abstract Results. DOI pending exact verification, not staged. | Human chamber validation, isotope dose comparisons; exact n/duration not extracted. | At low dose difference +8 ± 9% SD, range −7 to 22%; moderate dose +4 ± 5%, range 0–9%. | Historical method and dosing, not current universal DLW precision or athlete data. Low-to-moderate contextual confidence. |
| E05. RMR equations differ in group accuracy and individual prediction precision. Meta-analysis. | O'Neill, Corish & Horner 2023, [10.1007/s40279-023-01896-z](https://doi.org/10.1007/s40279-023-01896-z), §3.4.3 Fig. 2; §3.4.6 Table 3 (publisher full text). | 29 studies, 1,430 adults in mixed sports; prediction vs indirect calorimetry. Ten-Haaf age/height/weight accuracy subset 4 studies, 7 comparisons, n=204. | Ten-Haaf standardized mean difference 0.04 (95% CI −0.16–0.23), I²=0%; 80.2% within ±10% for precision subset. Cunningham 1980 LBM 0.15 (−0.26–0.57), Harris-Benedict 1918 −0.14 (−0.52–0.25); I²=93% each. Other precision estimates 40.7–63.7%. | Different subsets; locally derived models can inflate apparent performance; calorimetry preparation heterogeneous; no daily TEE. Moderate for group results, low for ranking in dual-trained adults. Draft two claims (accuracy and within-bound fraction). |
| E06. Population equation is an REE estimate, not TDEE. Derivation / local validation. | Mifflin et al. 1990 [10.1093/ajcn/51.2.241](https://doi.org/10.1093/ajcn/51.2.241), abstract; ten Haaf & Weijs 2014 [10.1371/journal.pone.0108460](https://doi.org/10.1371/journal.pone.0108460), abstract and publisher Results context. | Mifflin: 498 healthy normal-weight/obese adults age 19–78, measured REE by indirect calorimetry; ten Haaf: recreational athletes age 18–35. | Original Mifflin regression R²=.71. Ten Haaf study reports general equations including Mifflin and Harris-Benedict less than 50% within its accuracy criterion; own equation derived locally. | R² not individual agreement; derivation and evaluation overlap; exact independent-validation performance must be reviewed. Context; overlaps E05; moderate methodological confidence. |
| E07. Wrist-device EE error can greatly exceed HR error. Criterion agreement. | Shcherbina et al. 2017 [10.3390/jpm7020003](https://doi.org/10.3390/jpm7020003), abstract Results; publisher article. | 60 diverse volunteers, seven wrist devices, sitting/walking/running/cycling vs indirect calorimetry; laboratory bouts. | No device median EE error below 20%; six devices median HR error below 5% during cycling. No daily TEE agreement derived. | Older devices, not resistance training or daily free living; error metric not signed correction. Moderate for study result, low device transfer. Draft. |
| E08. High TEE correlation can coexist with substantial bias in actual runners. Criterion agreement. | Ma et al. 2026 [10.1007/s00421-026-06458-5](https://doi.org/10.1007/s00421-026-06458-5), Methods (DLW and triaxial accelerometer), Results Fig. 2B-2 (publisher full text). | 16 elite female university runners age 20 ±1, waist triaxial accelerometer vs 7-day DLW, measured vs predicted BMR. | Estimated TEE exceeded DLW by 416 ±242 kcal/day (~12.5%); r=.828; limits of agreement −59 to +891 kcal/day. BMR Cunningham bias ~1.6%, r=.728. | One device/method and female elite cohort; no repeat-change validation or mixed training. Moderate for direction and magnitude, low for correction of other devices. Draft TEE claim. |
| E09. PAEE from consumer monitors varies by reference and environment. Criterion agreement. | Murakami et al. 2019 [10.2196/13938](https://doi.org/10.2196/13938), abstract Methods/Results and indexed original text. | 19 healthy adults, 12 devices, one chamber day and 15 free-living days; PAEE reference = TEE minus BMR and assumed 10% TEF. | DLW-derived PAEE 728.0 ±162.7 kcal/day; 10/12 devices significantly underestimated, two non-significant contrasts (not equivalence); Pearson r=.46 and .48 for two significantly positively correlated devices. | Residual reference itself noisy; small sample, outdated devices, multiple comparisons; no universal longitudinal reliability. Moderate for studied devices, low for individual coaching. Draft. |
| E10. Reported intake often differs from expenditure; missingness and bias matter. Existing review. | Capling et al. 2017 [10.3390/nu9121313](https://doi.org/10.3390/nu9121313), Packet 004 `capling-diet-validity@1`, `athlete-logged-intake-dlw-disagreement@1`, abstract Results (11 DLW comparisons); carried forward, not re-extracted. | Athlete dietary assessments vs DLW; heterogeneous windows. | Packet 004 records mean underestimation 19%; pooled ES −1.006 (95% CI −1.3 to −0.7). | Intake vs expenditure difference includes actual energy imbalance, so not pure reporting error. Group bias is not personal correction. Moderate for caution; existing pending claim. |
| E11. Morning scale weight still varies without long-term tissue change. Retrospective observation. | Cheuvront et al. 2004 [10.1123/ijsnem.14.5.532](https://doi.org/10.1123/ijsnem.14.5.532), abstract Results. | 65 active men exercising in heat, prescribed fluid replacement, first-morning weights over 4–15 days. | Daily variability 0.51 ±0.20 kg, CV 0.66 ±0.24% (SDs). | Not a minimum detectable tissue change or longitudinal calorie estimator window. Specific hydration protocol, no women, no training intervention. Moderate for variability; low transfer of magnitude. Draft. |
| E12. Glycogen-associated water can confound short-term weight interpretation. Controlled sequence, physiological study. | Olsson & Saltin 1970 [10.1111/j.1748-1716.1970.tb04764.x](https://doi.org/10.1111/j.1748-1716.1970.tb04764.x), abstract. | 19 subjects after prolonged heavy exercise, 3 days fat/protein diet followed by 4 days carbohydrate-rich diet. | Weight +2.4 kg, estimated total body water +2.2 L over carbohydrate phase; muscle glycogen increased. No interval extracted. | Sequence without independent controls; historical methods, assumed glycogen mass and water relationship; do not infer fixed ratio in free-living athlete. Moderate for possibility, low quantitative transfer. Context. |
| E13. Dynamic expenditure and tissue composition affect mass response. Mechanistic mathematical model. | Hall et al. 2011 [10.1016/S0140-6736(11)60812-X](https://doi.org/10.1016/S0140-6736(11)60812-X), model description, Fig. 5C and abstract (author manuscript indexed). Hall 2008 [10.1038/sj.ijo.0803720](https://doi.org/10.1038/sj.ijo.0803720), abstract/model. | Adult metabolism models informed by controlled weight-loss data and population studies; not an athlete trial. | Model predicts slower response than a static rule and energy density dependent on initial adiposity and amount lost; average modeled half-time ~1 year for permanent intake change in population model. | Not an individual adaptation time constant or athlete dosing formula; tissue partitioning assumptions and activity changes. Moderate conceptual support; context only. |
| E14. Longitudinal weight-based model estimates **change in intake** under assumptions. Model validation. | Sanghvi et al. 2015 [10.3945/ajcn.115.111070](https://doi.org/10.3945/ajcn.115.111070), publisher Methods/Results and Discussion, Table 1 and Fig. 3 (accessible indexed passages; PMC direct open blocked). | 140 participants in CALERIE restriction arm, four intervals over 2 years; demographic and repeated-weight model vs DLW/DXA intake-balance. | Group mean ΔEI differences within 40 kcal/day; overall individual root mean square deviation 215 kcal/day; authors report most ΔEI estimates within 132 kcal/day; three-quarters within 250; Discussion reports total LoA span ~800–1000 kcal/day. Not a prediction interval for hybrid athletes. | Reference uses derived intake, shared weight/composition context; not independent daily TEE, calorie-log bias or hybrid athlete validation. Moderate for aggregate agreement, low for individual transfer. Draft. |
| E15. Increased activity need not yield equal increases in TEE. Observational model. | Careau et al. 2021 [10.1016/j.cub.2021.08.016](https://doi.org/10.1016/j.cub.2021.08.016), Summary (publisher). | 1,754 free-living adults with TEE and BEE in database, between-person analysis. | Model estimated average compensation ~28%; variation by composition. | Residual activity term shares variables with TEE/BEE, confounding and cross-sectional identification; does not establish within-person causal compensation or an eat-back percentage. Low for causal transfer. Context. |
| E16. Weight compensation may involve appetite/intake, not necessarily reduced activity or metabolism. Randomized trial. | Martin et al. 2019 E-MECHANIC [10.1093/ajcn/nqz054](https://doi.org/10.1093/ajcn/nqz054), abstract Methods/Conclusions. | 198 overweight/obese adults randomized to control, 8 or 20 kcal/kg/week supervised exercise, 24 weeks. | Authors attributed compensation mainly to increased intake/appetite, not observed RMR/non-exercise activity changes. Exact group estimates not extracted. | Not trained hybrid athletes; mechanisms assessed with imperfect estimates, no universal compensation. Low transfer; context. |
| E17. Weight-based estimates become more precise over longer windows under specified assumptions. Model simulation and inpatient test. | Hall & Chow 2011 [10.3945/ajcn.111.014399](https://doi.org/10.3945/ajcn.111.014399), abstract Design/Results. | Controlled inpatient weight-loss data and simulated free-living individuals with realistic water/intake variation. | Authors report >28 days of daily weights needed in their simulations for a 95% CI of <300 kcal/day for ΔEI. Verify exact interval convention before implementation. | Simulation-dependent noise and model; not minimum logging window, not absolute TDEE, not athlete validation. Moderate for study-specific result. Context. |
| E18. Running cost depends on gradient and economy; distance × mass is contextual. Physiological comparison. | Minetti et al. 2002 [10.1152/japplphysiol.01177.2001](https://doi.org/10.1152/japplphysiol.01177.2001), original abstract/publisher record. | 10 runners on treadmill, slopes −0.45 to +0.45. | Level running cost 3.40 ±0.24 J/kg/m (~0.81 kcal/kg/km by unit conversion); +0.45 slope 18.93 ±1.74, −0.20 slope 1.73 ±0.36 J/kg/m. Dispersion definition and gross/net protocol require verification; not a universal coefficient. | Not free-living TEE; speed, gradient, surface, economy, gross/net definition and post-exercise contribution matter. Moderate for dependence, low for individual conversion. Context. |
| E19. Lifting expenditure is difficult to quantify even in laboratory studies. Scoping review. | Mitchell et al. 2024 [10.1007/s40279-024-02047-8](https://doi.org/10.1007/s40279-024-02047-8), Results, §§4.1–4.2 publisher text. | 166 resistance-exercise studies, varying protocols; 136 used indirect calorimetry, 31 wearables, 76 postexercise measurements. | Review highlights incomplete quantification of glycolytic cost by gas exchange alone. Counts not independent effect sizes. | No universal conversion of load × reps to energy; heterogeneous exercises and recovery periods. Moderate methodological confidence; context. |
| E20. Slower planned loss supported better lean-mass response in a small athlete trial. RCT. | Garthe et al. 2011 [10.1123/ijsnem.21.2.97](https://doi.org/10.1123/ijsnem.21.2.97), abstract Results. | 24 elite athletes randomized 13/11, usual sport plus 4 resistance sessions/week, target 0.7 vs 1.4% body mass/week, durations 8.5 ±2.2 vs 5.3 ±0.9 weeks. | Achieved losses ~0.7 ±0.8 vs 1.0 ±0.4%/week; LBM +2.1 ±0.4 vs −0.2 ±0.7% (between-group p<.01); intake reduction 19 ±2 vs 30 ±4%. Dispersion notation as abstract; verify SD/SE. | Different durations/exposure and actual rates; DXA lean mass influenced by water; no direct running outcomes; not a universal safe rate. Moderate for contrast, low for individual hybrid targets. Draft. |
| E21. Longer-term follow-up does not establish lasting superiority of slower loss. Follow-up. | Garthe et al. 2011 [10.1123/ijsnem.21.5.426](https://doi.org/10.1123/ijsnem.21.5.426), abstract Results. | 23 athletes at follow-up 6/12 months; related intervention lineage, verify overlap. | No significant between-group composition/performance differences at 12 months. | Attrition, different follow-up analysis; no equivalence test. Low for long-term comparison. Context. |
| E22. Energy restriction can attenuate lean-mass development while strength findings remain uncertain. Existing meta-analysis. | Packet 004 `murphy-koehler-energy@1`, [10.1111/sms.14075](https://doi.org/10.1111/sms.14075), `energy-deficit-rt-lean-mass@1`, `energy-deficit-rt-strength@1`. | Resistance training with vs without deficit across study windows. | Carry forward exact estimates in Packet 004; no new extraction. | Lean-mass gain not the same as strength; deficit meta-regression not an individual safe target; hybrid endurance and LEA not inferred. Existing pending. |
| E23. Surplus and low availability have distinct tradeoffs. Existing trials. | Packet 004 `helms-energy-surplus@1` [10.1186/s40798-023-00651-y](https://doi.org/10.1186/s40798-023-00651-y), `oxfeldt-lea@1` [10.1113/JP284967](https://doi.org/10.1113/JP284967), `caldwell-lea@1` [10.1096/fj.202401780R](https://doi.org/10.1096/fj.202401780R). | Trained resistance and combined-exercise interventions; exact protocols in 004. | Reuse `surplus-body-mass-skinfold@1`, `lea-combined-myofibrillar-synthesis@1`, `lea-endurance-time-trial-power@1`. No new estimate. | Body composition, synthesis and performance are different endpoints. No universal surplus or diagnostic cutoff. Existing pending. |
| E24. Wearable brand-level validation does not identify current athlete-specific error. Existing review. | Packet 004 `fuller-wearable-validity@1` [10.2196/18694](https://doi.org/10.2196/18694), `wearable-energy-expenditure-validity@1`. | Mixed devices, outcomes and protocols; literature through May 2019. | No brand satisfied review's EE accuracy assessment; no new pooled estimate. | Verify EE denominator, tested models and definitions; group evidence does not certify or invalidate every current device. Existing pending. |

### 2.3 Measurement and proxy-validity appraisal (provider independent)

The following is a methodological synthesis, not additional empirical claims. Precision means repeatability under a specified protocol, not correctness. Agreement means closeness to a reference; neither implies sensitivity to change. A predictor may be useful without being unbiased if its error structure is stable and incremental value is prospectively demonstrated. Bias stability is an assumption, not a property of all devices or loggers.

| Construct / reference | Field observation and units / granularity | Validity, error and confounders | Comparison requirements, predictive value, MVP and richer data |
|---|---|---|---|
| Mean free-living TEE / DLW | isotope elimination difference estimates CO2 production then energy via substrate/RQ assumptions; typically days to weeks; kcal/day mean | isotope sampling, background enrichment, water turnover, fractionation, RQ/food quotient assumptions; high flux can alter optimal window. Not daily decomposition. | Match exact DLW period with same-day total estimates and time boundaries; repeat DLW windows to validate change. Not MVP; research calibration subset only. |
| RMR or BMR / indirect calorimetry | measured VO2/VCO2 at rest, kcal/day extrapolation; predicted equation if no test | BMR stricter fasting/rest/thermal conditions than RMR; recent exercise, stimulants, illness, energy restriction, FFM error; equation group bias and individual error (E05). | Standardized repeat testing required for change; population estimate feasible with appropriate covariates; not direct suppression or LEA inference. |
| Day-specific EE / whole-room calorimetry | gas exchange over controlled day; wearable daily total, kcal/day | chamber controls activity and food but alters habitual life; gas conversion assumptions; device algorithms and nonwear. | Daily chamber comparisons useful for protocol-specific error, not field generalization; DLW validates average only. Wearable qualitative/contextual unless calibrated. |
| Exercise EE / exercise calorimetry | HR, distance, duration, modality; kcal/session estimate | gross vs net cost, movement economy, incline, heat, anaerobic contribution and postexercise recovery (E18/19). Lifting tonnage is not metabolic work. | Match exercise protocol/definition; no universal per-set or per-distance coefficient. Modality-specific covariates feasible conditional on completed exposure; laboratory calibration optional. |
| NEAT / residual energy or monitored movement | steps, occupation, standing, other activity; count/time | steps do not measure metabolic expenditure; residual conflates thermogenesis and BMR error. Exercise may alter appetite/activity. | Use as contextual change signals if comparable; no component identification. Detailed movement and repeated references needed for richer model. |
| TEF / controlled meal calorimetry | intake composition and timing; kcal/day estimate | composition, processing and fed-state response; commonly assumed proportion is not measured individual TEF. | Optional future macros; do not require for basic coaching or add TEF twice when total estimate already includes it. Deferred component inference. |
| True metabolizable intake / controlled weighed food with waste, energy composition | logged kcal/day, completeness flag, source/timestamp | portion, restaurant/database errors, selective omission, intentional restriction, reactivity, duplicated synced records; even weighed food is not perfect metabolizable energy. | Representative weekdays/weekends and stable logging regime; no missing-as-zero. Conditional for operational target; true intake deferred without anchor. Controlled feeding/independent audits useful but burdensome. |
| Intake-balance reference / DLW plus body energy stores | weight + body composition over matched windows | both reference components noisy; DXA lean hydration and tissue-energy assumptions; shared variables can correlate errors. | Research comparison not direct observation of intake; distinguish validation of ΔEI from absolute TEE. Deferred in MVP. |
| Scale mass / calibrated scale | kg, timestamp, conditions, repeated within day | scale resolution/offset, clothing, time, hydration, sodium, gut contents, exercise inflammation, glycogen, creatine, menstrual-related shifts, travel, alcohol; not all attributable to water. | Compare similar morning post-void conditions when acceptable; no forced daily weighing; group duplicate observations by protocol, preserve raw records. Conditional trend; repeated comparable measurements improve precision, not tissue identification. |
| Fat/lean mass / DXA or multicomponent model | scale trend, optional body composition estimate | hydration alters lean estimates; consumer impedance depends on fluid and algorithms. Fat mass loss can coexist with lean gain. | No tissue partition from scale alone. Repeated standardized composition may narrow uncertainty; not necessary to prescribe general fueling. Deferred tissue-energy inference. |
| Energy availability / intake minus exercise EE per FFM | intake, training, weight and reported symptoms | uncertainty in all terms; stable weight and adequate-looking calories do not establish availability or REDs status. | Clinical assessment appropriate for persistent or concerning signs; never automate diagnosis. Qualitative only. |
| Operational maintenance logged intake | mean eligible intake associated with stable mass and representative activity; kcal/day | logging bias may be stable, change with food choices or goal, or be non-additive; nonrandom missing days; apparent stability may mask composition change. | Define regime and window, uncertainty and conditionality; no true TEE claim. Conditional MVP. Repeated prospective target changes and audit improve utility. |
| Performance and recovery | comparable load/reps/effort and run outcomes; feedback | acute fatigue, terrain, motivation, illness, sleep and fueling; missing data vs actual missed sessions. | Use Packet 005 and 008 comparison rules; not a direct assay of energy adequacy. Conditional for contextual review; labs not required for useful decisions. |

**Time alignment and validity requirements:** calendar day in athlete's recorded zone, actual consumption day rather than sync time, units and day completeness, actual session occurrence, version/provenance and deduplication. Midnight totals may be partial; travel and time-zone changes need reconciliation. Preserve date range, denominator (eligible vs expected), reason for exclusion, last verified timestamp and uncertainty in each estimate. Compare across repeated, similar regimes rather than infer trends across a scale or logging discontinuity. Ask targeted feedback (e.g., “were these weekend logs complete?”) only if it could change the decision. Missing observations are unknown, not zeros.

### 2.4 Interpretation, gaps and transfer

- RMR evidence is more direct for recreational athletes than general-population derivation, but not necessarily for dual-experienced athletes; 2023 reviews overlap, and Ten-Haaf derivation must not be counted again as independent validation. Accuracy at rest cannot be propagated as a fixed TEE uncertainty without uncertainty in PAL and their covariance.
- DLW is a strong multi-day reference, not per-day truth; chamber data are more temporally resolved but less ecologically representative. Controlled feeding and DXA support different estimands. The 2017 maintenance study is not validation of free-living app logs. CALERIE's change estimates are promising but do not estimate a logging offset or validate individual TDEE at arbitrary training loads.
- Activity compensation evidence is mixed in design and outcome: Careau's cross-sectional decomposition and E-MECHANIC's intervention do not estimate the same quantity. Distinguish appetite-mediated intake changes from changes in expenditure. No 28% compensation multiplier, 12% wearable correction or 19% food-log correction should be used automatically.
- Absolute error and repeatability must be separately established for a particular device and protocol. Higher correlation or stable weekly averages do not prove a stable bias. Validation against DLW averages cannot establish day-level dynamic fidelity. Wearable data can be optional context without being necessary for calorie advice.
- No direct comparative validation was identified in this targeted search for a logging-adjusted hybrid-athlete coaching policy, or for incremental benefit of activity-conditioned latent TDEE modeling versus simple feedback in this population. This is an evidence gap, not proof of no benefit. Additional intake-specific validation (restaurant/database errors, logging reactivity, missing-not-at-random patterns), menstrual/creatine and hydration-specific quantitative data, modern device-specific longitudinal studies and direct prospective athlete outcomes remain outstanding. No exhaustive review of these mechanisms is claimed.

## 3. Candidate coaching policies

All policies revision 0.1, pending independent human review; no authority to mutate an approved prescription. Existing NU-P01 (nutrition-aware progression), NU-P02–05 (daily/session nutrition and double sessions), NU-P06 (body composition), NU-P07 (clarify/protect/refer) and NU-P08 (data integrity) remain intact. HP-P09 and RE-P10/11 provide longitudinal review and conflict resolution. These new EE policies specify the estimation dependency rather than replacing those decisions. Scientific readiness (SR) describes support and unresolved decision efficacy. Data readiness (DR) is assessed separately for recommendation (R), adherence (A), effectiveness (E), and calibration (C). Feasible = minimum data obtainable in context, not approval; conditional = coverage or feedback needed; qualitative only = no supported individualized quantitative inference; deferred = required evidence or inputs absent. Calibration is distinct from monitoring. All uncertainty statements apply to a particular estimand, regime and horizon.

### EE-P01 — Nutrition observation eligibility (extends NU-P08)

- **Decision / construct / estimand:** determine which reported intake, mass and activity observations support a specified window estimate, not whether the person ate enough. Target is eligible observed exposure and coverage by regime. E02, E09–11, E24 support measurement caution; exact inclusion procedure is engineering judgment.
- **Ideal / minimum / optional:** ideal controlled intake and calibrated standardized mass with exact timestamps; minimum canonical type, units, occurrence day, source lineage, record status, relevant completeness and comparison protocol. Optional volunteered explanation of unlogged meals, scale change, unusual weigh-in, food composition and travel.
- **R:** qualitative advice can proceed without any calorie/weight records; quantitative review requires aligned eligible observations. **A:** actual reported intake with completeness and target in force; absence is unknown. **E:** comparable repeated mass and performance/context. **C:** paired independent reference, if claiming physiological accuracy; not required for ordinary quality filtering.
- **SR:** strong rationale for separating measured/estimated and missing/zero; no validated optimal eligibility threshold. **DR R/A/E/C:** feasible for reporting provenance when present; conditional for quantitative coverage, adherence and trends; deferred for independent calibration.
- **Logic:** deduplicate synced events only with reliable lineage; distinguish absent, explicitly zero, partial, unknown completeness and reported-complete days. Quarantine incompatible units or overlapping day totals; display counts, reasons and coverage by day type. Select representative contiguous regime only if appropriate. Never exclude because a value disagrees with the desired trend. Ask a targeted question if it could change action.
- **Assumptions, missingness and uncertainty:** partial/unknown days can describe some recorded food but not complete intake; selection may bias sample even after filtering. Carry prior safe target or qualitative guidance, suspend numerical recalibration if not representative. Confirm explicit zero and safety context without treating as normal. No inference of macro intake or adherence from kcal alone. Richer data: meal provenance, duplicate resolution, voluntary completeness confirmation, independent weighed records. No automatic clinical diagnosis. Review status pending.

### EE-P02 — Initial energy reference (extends NU-P02)

- **Decision / construct / estimand:** choose initial reference: existing tolerated reported target, measured/predicted RMR × contextual PAL, or device total EE estimate. Estimands are distinct: operational target or conditional mean physiological TEE prior. E03, E05–09, E24; selecting among references is judgment.
- **Ideal / minimum / optional:** repeated representative DLW window and controlled intake with relevant training; minimum goal, constraints, habitual activity and current intake target if available. For equation branch require appropriate age, mass, height and any sex/FFM covariate used by the specific equation (do not infer sensitive/unknown values). Optional measured RMR, historical mass and feedback, versioned wearable totals.
- **R:** current tolerated target or population reference with declared uncertainty; **A:** reported-complete intake and target dates; **E:** trend and both disciplines' performance; **C:** independent reference and repeat tests for claims of absolute accuracy.
- **SR:** moderate for selected RMR prediction studies, low for individualized TEE or target efficacy; all pending. **DR R/A/E/C:** conditional numerical, qualitative otherwise / conditional / conditional / deferred absent references.
- **Logic:** prefer relevant history over unnecessary reinitialization when reliable and goal-compatible. If no history, choose a reviewed equation appropriate to population with plausible activity scenario; present broad conditional estimate rather than spurious precision. Wearable total may serve as alternative prior, not sum with exercise calories. Keep competing estimates visible; do not average them assuming independence. Retain reference if new evidence insufficient.
- **Uncertainty/fallback:** equation residual and PAL uncertainty, unobserved TEF and spontaneous activity; no universal PAL, error percentage or athlete correction. Ask about training and non-exercise activity or defer numeric target. More data: measured RMR, calibrated PAL, matched DLW. No diagnosis from RMR ratio or estimated deficit. Pending.

### EE-P03 — Body-weight trend and transient-shift review

- **Decision / construct / estimand:** assess observed mass trajectory and its uncertainty, not tissue change. E11–14, E17; robust trend and selection are statistical engineering choices.
- **Ideal / minimum / optional:** standardized repeated measurements and context; minimum timestamps, calibrated or consistent scale/protocol, enough comparable spread in time for identifiable trend. Optional repeated within-day checks, hydration/travel/creatine/carbohydrate/sodium context, menstrual-related context voluntarily provided, body composition reference.
- **R:** trend with data quality and direction or inconclusive; **A:** actual weigh-in observations only, no assumption of daily weighing; **E:** later comparable trend and training outcomes; **C:** test within-person noise and method change; tissue validation needs independent composition.
- **SR:** moderate that short-term fluctuations are material; no validated universal trend window or smoothing choice. **DR:** conditional trend / feasible observed measurements only / conditional / conditional for scale repeatability, deferred for tissue.
- **Logic:** preserve raw measurements; use comparable protocol, select or aggregate same-day replicate by predefined rule (never choose lowest). Fit robust slope on elapsed days, compare alternative smoothers/windows, examine residuals and regime breaks. If abrupt shift plausibly transient, mark event and defer recalibration rather than automatically deleting it. Report uncertainty including autocorrelation and missingness. If persistent, revisit hypothesis; do not label it water with certainty.
- **Fallback / prohibited / extensions:** insufficient data → no slope or wide uncertainty; optional standardized weigh-ins if desired, preserve current safe plan. No daily fat mass or energy deficit inference. Richer data include repeat composition, controlled hydration and more representative measurement. Pending.

### EE-P04 — Logging-adjusted maintenance reference (Model B)

- **Decision / construct / estimand:** estimate expected reported kcal/day associated with approximately stable observed mass within a named logging and activity regime. Not physiological TDEE. E03/E10/E14 motivate method; exact operational construct and feedback policy are candidate statistical/practical judgment.
- **Ideal / minimum / optional:** representative repeated stable intervals with verified logging and comparable mass; minimum eligible complete-intent intake coverage, comparable weight trend, current goals and representative completed activity, no unresolved discontinuity. Optional logging audit, current target history, expenditure context, body composition.
- **R:** stable mass trajectory with uncertainty and representative intake, or explicitly conditional slope-corrected scenario; **A:** complete-intent intake against approved target; **E:** later independent weight/performance/adherence, not the fitting window; **C:** prospective behavior validation; true TEE calibration separately anchored.
- **SR:** model-based intake-change evidence indirect; no direct proof of operational-target efficacy. **DR:** conditional / conditional / conditional / conditional for predictive calibration, deferred physiological absolute without anchor.
- **Logic:** if weight approximately stable in practically acceptable bounds, use representative mean logged kcal with uncertainty as operational maintenance reference for this regime. For nonzero slope, optionally calculate sensitivity scenarios using justified energy-density and bias assumptions (§4), but if sign/magnitude uncertain or unstable, prefer directional target review. Distinguish current target from realized logged mean. Re-estimate on justified new representative interval, not overlapping noisy daily changes.
- **Uncertainty/fallback:** stable offset not guaranteed; missingness may be informative; weight stability not tissue-energy stability. If log regime changes or body-mass shifts are unresolved, suspend or expire estimate, retain previous reference labeled stale, avoid new calorie restriction. No automatic underreporting correction. Richer data: weighed food subset, reference windows, repeated observed response. Pending.

### EE-P05 — Physiological expenditure estimation and model escalation

- **Decision / construct / estimand:** determine if absolute mean TEE or change in TEE can be estimated conditional on defensible anchors; choose whether activity-conditioned or latent-state model adds value. E02–09, E13–17; §4 nonidentifiability result. Do not use predictive fit to claim physiological identification.
- **Ideal / minimum / optional:** for absolute calibration, matched DLW or independently quantified intake and tissue-energy change; minimum for operational Model C is quality-aligned longitudinal observations plus repeated activity variation and stable logging regime; explicit model assumptions and estimand. Optional body composition, measured RMR, activity covariates, repeated reference windows.
- **R:** report only estimand supported; **A:** target adherence separate; **E:** held-out weight prediction and performance; **C:** independent reference for physiological claims, repeated regimes for activity coefficients.
- **SR:** physical identity valid; exact statistical model unvalidated, low confidence in individual dual-athlete physiological decomposition. **DR:** deferred for absolute TEE without anchor; conditional research-only predictive modeling / conditional / conditional / deferred absolute calibration.
- **Logic:** inspect rank/invariance and sensitivity before fitting; choose identifiable net quantity if possible; specify priors from independent sources and expose prior dependence; compare simple baselines prospectively, reject extra complexity if it adds no material decision value or undermines calibration. Never narrow uncertainty by imposing an unacknowledged zero-bias prior.
- **Fallback / prohibited / extensions:** use Model A/B or qualitative guidance; report partial identification and scenarios not false precision. No day-specific true TEE, TEF/NEAT or metabolic adaptation inferred from residual. Additional reference measurements or randomized controlled changes may improve identification; telemetry alone does not solve confounding. Pending.

### EE-P06 — Activity-conditioned nutritional guidance (extends NU-P02/03/05, CT-P06)

- **Decision / construct / estimand:** whether changed planned or completed activity justifies revised fueling opportunities/day allocation or average target review. Construct: demand, energy flux, carbohydrate availability, recovery; estimand may be relative change in activity exposure, not a measured kcal cost. E08–09, E15–19; Packet 004 carbohydrate evidence.
- **Ideal / minimum / optional:** ideal calibrated session expenditure and representative activity/food observations; minimum actual/planned duration, modality, priority, intensity/effort context and current plan; optional distance, terrain, verified device totals, steps, appetite/fueling feedback and macros.
- **R:** session-specific qualitative guidance from planned workload; numerical day targets need reviewed contextual energy reference. **A:** actual session and reported fueling/intake; **E:** session quality, tolerance, both discipline trends and mass if relevant; **C:** repeated representative changes with matched references for kcal claims.
- **SR:** moderate for workload-specific fueling principles, low for conversion to individualized TEE or feedback increments. **DR:** feasible qualitative, conditional quantitative / conditional / conditional / deferred without reference.
- **Logic:** compare new and habitual exposure, separately by modality; identify key sessions and between-session feeding; consider food access and appetite. Treat wearable total as inclusive if semantics verified; active and recorded exercise are not additive to total. Consider practical increased fueling on demanding days even before mass trend clarifies, if appropriate to safety/goals. No exact wearable eat-back. Review weekly average if sustained shift and data support it.
- **Fallback / prohibited / extensions:** if device semantics unclear ignore kcal totals, use training context; no equivalence between running, lifting and intermittent sport via kcal/HR. Additional activity history or individualized reference may improve predictions but must add prospective value. Pending.

### EE-P07 — Conservative target review and adjustment (extends NU-P06)

- **Decision / construct / estimand:** retain, raise, lower, redistribute or defer an approved **reported-calorie target**, given desired and observed trajectory and performance constraints. E03/E13/E14/E20–23; control rule is practical judgment, not trial-validated.
- **Ideal / minimum / optional:** reliable realized intake, trend, goal and target history, representative activity and health context; minimum approved objective/target and sufficient credible response for proposed quantitative change; optional macros, meal timing, appetite, composition and reference expenditure.
- **R:** credible deviation from agreed trajectory plus adherence/context; **A:** realized intake relative to current approved target; **E:** subsequent eligible mass and performance/tolerance plus adherence; **C:** prospective prediction and action evaluation.
- **SR:** evidence for nutrition-performance tradeoffs, low direct evidence for adjustment policy. **DR:** conditional / conditional / conditional / conditional for policy feedback, deferred absolute physiology.
- **Logic:** safety and agreed performance commitments first. If trajectory acceptable and burden tolerable, hold even if estimate shifts. If discrepancy persists, verify actual target adherence and reporting regime, compare alternative explanations and fueling distribution. If supported, propose smallest contextually useful reviewed adjustment or redistribution with bounded change and review plan; do not stack changes while previous response unresolved. If target was not followed, address feasibility rather than automatically changing it. Changes require athlete approval and versioned rationale.
- **Fallback / uncertainty:** if sparse/discordant observations, ask or defer; if concerning unintentional loss or symptoms, protect and refer (EE-P09). Do not calculate exact daily deficits or mandate weight loss, fixed increments, windows or rates. Richer data may narrow response uncertainty, not eliminate causal confounding. Pending.

### EE-P08 — Logging/measurement regime changes and selective missingness

- **Decision / construct / estimand:** detect discontinuity that invalidates comparability; estimate eligible regime-specific mean, not bias itself. E10–12/E24; change-point review is engineering method.
- **Ideal / minimum / optional:** source histories, protocol dates and confirmation; minimum observed timestamp/provenance and enough context to establish comparison; optional meal or food-type audit, travel, device/firmware change, logging burden feedback.
- **R:** classify data eligibility, **A:** coverage separate from true consumption, **E:** post-change comparable trend, **C:** overlapping old/new protocol or independent anchor.
- **SR:** moderate measurement rationale, low evidence for automated change-point triggers. **DR:** feasible known changes; conditional ambiguous changes / conditional / conditional / conditional for overlap only.
- **Logic:** preserve prior observations and estimate as historical; split regimes on known changes, flag uncertain shifts rather than infer a cause; no zero imputation or complete-case estimate labeled full-week average if weekends absent. Report missing pattern, sensitivity to plausible missing-day intake only as scenarios. Require justified new representative evidence before recalibration.
- **Fallback / prohibited / extensions:** carry safe target with explicit uncertainty, qualitative fueling, ask targeted clarification; no bias magnitude from disagreement. Richer provenance, overlap and voluntary logging-completeness tags. Pending.

### EE-P09 — Body-composition/performance conflict and referral (extends NU-P01/06/07 and RE-P10/11)

- **Decision / construct / estimand:** whether to protect training, pause pursuit of weight change, adjust fueling, revise objectives or refer. Construct: performance, energy adequacy and health; no clinical estimand from logs. E20–23 and Packet 004 IOC consensus appraisal; Packet 008 task-specific recovery.
- **Ideal / minimum / optional:** clinician/dietitian assessment when indicated; minimum known goals, symptoms/restrictions if offered, actual performance/burden and feedback; optional intake/mass/meal context and medical assessment if voluntarily provided.
- **R:** qualitative support and safety triage without calories; **A:** actual training/fueling and target adherence where known; **E:** comparable strength/running, symptoms/tolerance and relevant professional follow-up; **C:** not a diagnostic model; clinical evaluation independent.
- **SR:** appropriate clinical boundaries and indirect nutrition effects; no individualized diagnostic or threshold policy. **DR:** feasible qualitative, conditional quantitative / conditional / conditional / deferred for diagnosis.
- **Logic:** investigate alternative explanations (illness, sleep, accumulated load, insufficient stimulus, pain, measurement error, adherence, fueling). If concerning symptoms, persistent unintentional loss, recurrent injury, disordered eating concern or persistent multi-domain deterioration, pause automated restrictive advice and seek qualified assessment; acute severe symptoms require urgent care as appropriate. No assumption weight stability is reassuring. If ordinary manageable conflict, discuss priority tradeoffs and propose conservative fueling or workload changes through approval.
- **Fallback / prohibited / extensions:** no diagnosis of LEA/REDs, eating disorder, metabolic suppression or medical clearance. Do not require full tracking to refer or give safe guidance. Optional clinician advice may establish restrictions to preserve; consent and owner scope required. Pending.

### EE-P10 — Value of information and prospective model review (extends RE-P10)

- **Decision / construct / estimand:** choose the next useful observation or model and assess incremental prediction/decision utility, not maximize data collection. E05–09/E14/E17 motivate uncertainty and validation; comparative benefit in hybrid athletes unknown.
- **Ideal / minimum / optional:** prospectively held-out histories and reference substudy; minimum proposed decision, uncertainty source, expected decision consequence and observation burden; optional more frequent comparable weights, completeness feedback, measured RMR/DLW, training covariates.
- **R:** ask only if result could materially change decision; **A:** whether requested observation was voluntarily supplied, not a requirement for unrelated advice; **E:** future prediction calibration, action appropriateness, athlete burden and joint outcomes; **C:** independent reference and temporally held-out validation.
- **SR:** statistical rationale strong, coaching efficacy untested. **DR:** feasible qualitative choice, conditional prospective comparison / feasible observed response / conditional / deferred reference if unavailable.
- **Logic:** compare holding target to alternatives across plausible scenarios; if same action robust, don't request expensive data. If disagreement matters, select least burdensome informative observation; e.g., ask about missing restaurant logs before requesting wearable telemetry. Compare A/B/C in shadow mode; promote complexity only after reviewed prospective criteria. No use of future logs in past decisions.
- **Fallback / prohibited / extensions:** maintain/qualitative guidance, defer if essential input absent. No assumption richer data resolve structural nonidentifiability or that accuracy equals efficacy. Extensions: independent calibration substudy and Packet 009 policy comparison. Pending.

## 4. Periodization and estimation methodology

### 4.1 Physiological accounting and estimands

TEE is the total metabolic energy expenditure over a stated interval. A practical accounting convention partitions it into resting/basal expenditure, thermic effect of food, exercise expenditure (increment above baseline), and nonexercise activity/other expenditure. Definitions differ: thermoregulation, recovery after exercise, adaptive changes and diurnal rest expenditure may be allocated differently. Avoid overlap; a residual is not pure NEAT. Daily expenditure varies with mass, composition, exercise, spontaneous activity, feeding, recovery, illness and environment. RMR is measured under defined resting conditions; BMR uses stricter conditions. Extrapolating a short resting measurement to a day does not measure full daily expenditure. PAL is a ratio of average TEE to a compatible basal/resting denominator, not a measured exercise multiplier. A MET is a population/reference metabolic cost multiple; converting duration to kcal requires correct resting reference and gross/net treatment, not universally 1 kcal/kg/hour as an individual's true resting metabolism.

Define day index t, I_t true metabolizable intake (kcal/day), E_t true TEE (kcal/day), U_t stored chemical energy (kcal), W_t measured mass (kg), L_t reported intake (kcal/day), V_t wearable total estimate (kcal/day), x_t activity covariates. Distinguish Ē over a stated interval from daily E_t, desired intake, logged target T_L, and the operational reference M_L. Energy availability (EA) is conventionally estimated from intake less exercise expenditure divided by fat-free mass, not TEE or energy balance; individual EA estimation requires reliable inputs not available here.

**Physical identity** (integrated over a day of length Δt=1 day):

`U_(t+1) - U_t = (I_t - E_t) Δt`.

Over interval H: `Ē_H = Ī_H - (U_end - U_start)/H` (physical identity / algebraic consequence; H in days). This is not a weight equation. U includes energy of tissue and other stored substrates; fluid and gastrointestinal contents change measured mass without a commensurate tissue-energy change. Even stable W does not imply stable U if composition changes. For an exact identity boundary, energy absorption/excretion must be consistently reflected in metabolizable intake and energy loss; no device component is separately identified by the identity. A conventional decomposition `E = R + TEF + net exercise EE + other nonexercise EE` is an **accounting convention / modeling assumption** for nonoverlapping terms, not four independently observable latent variables.

**Target estimands:**

| Quantity | Definition | Identification / usage |
|---|---|---|
| Physiological mean TEE Ē_H | Average true expenditure in specified window | DLW or controlled intake-balance plus storage; uncertain. Not ordinary app-log result. |
| Conditional TEE estimate | Ē_H under declared intake-bias, tissue and/or wearable-calibration assumptions | Report scenario/assumption sensitivity; no claim of unique true value. |
| Operational maintenance M_L(r,x) | Expected reported daily intake associated with a practically stable observed mass trajectory in regime r and representative activity x | Candidate empirical target, conditional on stable reporting and no unresolved shift; not necessarily stable U. |
| Recommended reported target T_L | Athlete-approved intended reported intake compatible with goals, feasibility and safety | Decision, not a measurement or parameter estimate; may differ from M_L. |
| Observed response | Trend in measured mass and comparable training outcomes | Descriptive, not causal, not direct tissue composition. |

### 4.2 Structural and practical identifiability

**Statistical modeling assumptions** (simple additive error model, not established physiology):

```
L_t = I_t - b_t + ε^L_t             (b > 0 denotes underreporting)
V_t = E_t + c_t + ε^V_t             (c > 0 denotes wearable overestimation)
W_t = F_t + N_t + Q_t + ε^W_t       (fat, other structural mass, transient mass)
U_t = u(F_t, N_t, stored substrates) (unknown tissue/storage map)
```

Here F and N denote nonoverlapping structural compartments defined so transient water/glycogen/gut mass Q is not counted twice. U may change with glycogen despite part of glycogen/water mass being assigned to Q. Bias b and c may depend on food choices, activity, time, device and reporting behavior; errors may be correlated. Missingness indicators R^L,R^W are observations of reporting/measurement, not true zero values; probability of missing can depend on true intake, travel, weight or stress. Neither missing at random nor independent residuals can be assumed.

**Mathematical nonidentifiability result for this model:** for any constant d compatible with feasible positive I,E, transform I'_t=I_t+d, E'_t=E_t+d, b'_t=b_t+d, c'_t=c_t−d, leave U and W unchanged. Then L and V predictions unchanged and energy balance unchanged. This is an exact likelihood invariance even with infinite noiseless observations and known U changes. If b,c can vary freely, d_t can vary too. If they are constant, relative changes may be identified under additional restrictions but absolute offset is not. With known constant c and reliable V, the symmetry is broken; uncertain calibration only partially anchors it. A prior penalizing b or c selects among equivalent explanations; the data did not identify the selected value. Two biased measurements may be strongly correlated or identical without identifying truth. For example, the equations only constrain b+c when L−V and true storage change are known. Under stable U, L−V=−(b+c)+noise. Independent error assumptions without known bias do not resolve the location ambiguity.

A second ambiguity concerns tissue partition. In a simplified two-compartment local approximation (statistical assumption): `ΔU ≈ ρ_F ΔF + ρ_N ΔN + ΔU_substrate`. `ΔW ≈ ΔF+ΔN+ΔQ`. Given only ΔW, infinitely many decompositions produce different ΔU. Even if ρ values known, without measured F,N,Q or independent storage assumptions, the map is underdetermined. Weight-stable recomposition (fat loss, lean gain) is a counterexample. Use **no fixed coefficient** as an exact stored-energy equation. For finite data, noisy slope, nonrepresentative coverage, autocorrelated fluid changes, changing activity and collinear covariates also create practical weak identification. An apparent state drift can be intake-bias drift, device drift, tissue adaptation, water or true expenditure change.

| Target | Structural constraint | What could improve inference |
|---|---|---|
| Absolute I and E | common offset symmetry | independently measured DLW average, controlled feeding plus independent tissue energy change, or externally justified bias bounds |
| b and c separately | only combinations observed | matched independent reference(s) and logging validation; repeated calibration if bias varies |
| Average E minus additive b | conditional on ΔU and complete L | weight-stable energy assumption or independent composition; uncertainty remains |
| Day-to-day E | time-varying b/c/fluids confound, even DLW averages don't resolve days | calorimetry or externally validated activity-response model; repeated daily reference under protocol |
| Change in E | can compare under stable biases, storage assumptions and activity context | repeated matched reference intervals; change in logging/device may invalidate |
| Tissue-energy change | mass not composition; Q not observed | repeated composition/controlled hydration plus tissue model; imperfect |
| BMR/TEF/NEAT adaptation | many decompositions same total | standardized RMR, measured activity/feeding response, explicit nonoverlap; never infer by residual alone |
| M_L | stable reporting and activity; mass stability with uncertainty | representative complete-intent days, comparable weights, repeated response at same/changed targets |

**Sensitivity rather than fake confidence:** if external bounds on mean bias b, storage change ΔU and reference error c are defensible, propagate all feasible combinations to conditional Ē. E.g. `Ē = L̄ + b̄ − ΔU/H` (identity + assumed measurement equation, ignoring mean-zero random error for illustration). If b∈[b_min,b_max] and ΔU/H∈[u_min,u_max], identified set under these bounds is `[L̄+b_min−u_max, L̄+b_max−u_min]`, before sampling uncertainty. Bounds are scenario assumptions unless independently validated. Intersect wearable-derived range only when its error bounds are justified and period matched. If incompatible, investigate assumptions rather than force narrow posterior. If no informative bounds, explicitly report unidentifiable. Do not claim a calibrated CI merely from a chosen set. Prior sensitivity, model misspecification, selection and correlated errors must be disclosed separately from conditional sampling uncertainty.

### 4.3 Candidate estimator designs

#### Model A — Minimal baseline (several simple comparators, not one fused estimate)

**Estimands:** A1 conditional average TEE from RMR × PAL; A2 wearable-estimated mean total EE; A3 historical mean reported maintenance reference if appropriate; A4 carry-forward existing approved reported target. Keep types separate. A1 may use Mifflin, Harris-Benedict, Cunningham or athlete-specific Ten-Haaf equations depending on applicability; equations are not interchangeable. For example, original simplified Mifflin (empirically derived population regression, E06): `R̂=10*m_kg + 6.25*h_cm −5*a_year + s`, where s=+5 for males and −161 for females as coded in the study. Cunningham 1980 conventional form `R̂=500+22*LBM_kg` (population equation; review original LBM definition and units before use). Ten-Haaf weight/height/age equation is a promising athlete-specific reference (E05/E06); verify exact coefficients/units and independent validation before selecting. Harris-Benedict (original vs revised versions differ) is another comparator, not preferred by default. No need to compute FFM-based equation with unreliable consumer body-fat estimates. No unreviewed anthropometric assumptions.

`Ê_A1 = R̂ * PAL` (**candidate engineering approximation**; PAL is compatible total/rest ratio). Use a reviewed contextual PAL scenario with uncertainty, not a universal multiplier; do not add exercise or TEF to an already all-inclusive estimate. `Ê_A2 = mean(V_t over eligible representative days)` (**descriptive estimator**, conditional proxy). `M̂_A3 = mean(L_t over stable representative regime)` (**descriptive estimator**, not unbiased TEE). A4 returns previous T_L plus age/status of evidence. Preserve errors/coverage and estimate type, units and version. Do not average A1/A2/A3 merely because they are numerically similar.

Pseudocode-level method:

```
Check safety, goal, current target and context.
If existing tolerated goal-compatible target and no credible new reason to change: retain A4.
If credible stable-history intake and weight: propose A3, labelled operational.
Otherwise, if appropriate demographics and activity assumptions available: report A1 scenario.
If verified semantics and coverage of total estimates: also report A2 as optional context.
If inputs absent or estimates incompatible: qualitative advice or targeted clarification.
Do not relabel proxy as measured TEE; do not make a target change without review.
```

Complexity low; no fitting beyond means or equation. Missing intake/weight doesn't prevent general fueling or A1, but prevents calibration to response. Validation: cross-person mean error, MAE/RMSE and bias vs DLW for TEE estimands; calibration and held-out future trend for operational target; prospective efficacy separate. Retain A4 as comparator especially during interruptions, productive trajectory or logging changes. RMR residual and PAL uncertainty are correlated; equation R² is not a CI. Model A does not remove structural ambiguity or determine adequacy.

#### Model B — Longitudinal operational maintenance and target feedback (recommended first research design)

**Estimand:** `M_L(r,x)` and defensible next reported target direction in a relatively stable logging regime r and representative activity x. Estimate observed mass trajectory, not underlying tissue change. Keep T_L separate from observed L̄. Use only observations eligible for specific inference; no fixed count threshold.

**Candidate statistical model** for comparable weights at elapsed days d_i: `W_i = α + g*d_i + η_i`, where g kg/day is local descriptive trend, not tissue rate. Robust slope via median of pairwise slopes (Theil–Sen) or Huber loss; compare against simple rolling mean/endpoints and linear slope; with irregular timestamps use actual time differences, not row index. Theil–Sen is a proposed statistical tool, not validated athlete model. Same-day replicates use predefined aggregation for comparable conditions or separate protocols. Residuals may be autocorrelated; use block bootstrap or time-series robust uncertainty only if effective sample and assumptions support it; no iid confidence interval when serial correlation dominates. Compare windows aligned to stable regimes and test sensitivity to plausible transient shifts. Insufficient data → no robust slope or broad uncertain direction. EWMA optional (`s_t=λ_t W_t+(1−λ_t)s_previous`, statistical smoothing assumption, λ_t tied to elapsed time); descriptive, not latent tissue estimator. Do not use future observations to smooth decision-time state. Missing days not automatically interpolated as facts.

`L̄_r = Σ L_t / n_eligible` (**descriptive estimator**, conditional on representative days). This is not a full-window mean when nonrandom missingness remains. Stratify weekday/weekend or day type only if observed enough to support it; otherwise report partial mean and sensitivity to missing-days scenarios; don't invent meal calories. A weighted day-type mean is a statistical approximation only if coverage and conditional representativeness hold. Explicitly record denominator.

**Near stable mass branch:** if slope and its uncertainty are consistent with agreed practical weight stability and other data support representative exposure, label `M̂_L≈L̄_r` (**candidate engineering approximation**). Do not equate failure to reject nonzero slope with maintenance; uncertainty may be too large, in which case label inconclusive. Practical stability band defined jointly with athlete/qualified reviewer for the goal, not a universal numerical cutoff. If composition or activity changed substantially, reassess regime.

**Nonzero trend branch:** optional scenario for a local tissue-like slope g* under assumptions about composition and water: `M̂_L(ρ) = L̄_r − ρ*g*` (candidate engineering approximation in kcal/day). Derivation: if additive constant reporting bias and expenditure stable and ΔU/H≈ρ*g*, true E≈L̄+b−ρ*g*, operational logged maintenance E−b≈L̄−ρ*g*. If multiplicative reporting L≈aI, correction is instead `aρg*`; unknown scale a is not identified. If stable L−I bias changes with intake, even the direction of correction needs qualification. This calculation is a sensitivity tool, not an approved calorie target algorithm. It assumes locally stable expenditure, which may change following target adjustments (TEF, body mass, activity). If desired trajectory g_goal and assumptions credible, an illustrative target reference is `T_L^scenario = M̂_L + ρ*g_goal` (same approximation). Do not use the static 3,500 kcal/lb rule as exact; vary defensible ρ scenarios chosen by qualified reviewer based on plausible tissue composition, or omit if no basis. For pure operational feedback, no ρ is needed: compare direction of g vs acceptable trajectory and adherence, select reviewed modest contextual target adjustment after safety check. A proportional control policy `T_next=T_current+K*(g_goal−ĝ)` (candidate engineering approximation; K units kcal/kg, not assumed tissue energy density) is optional research comparator, not recommended operational default. K and update horizon would be tuned only with independent evidence and prospective calibration; avoid oscillation from measurement noise and delayed response. No numeric K, cap or window approved here.

Pseudocode-level design:

```
Freeze as-of date, approved goals/target and eligible canonical observations.
Reject automatic numerical revision on safety concerns; protect/refer as indicated.
Partition measurement and activity/logging regimes; show coverage and gaps.
Estimate local observed mass trajectory with protocol/time sensitivity.
If representative intake unavailable, slope inconclusive, or unresolved shift:
    preserve safe target or ask high-value question; no new maintenance estimate.
Else if practical stability supported:
    store M_L with uncertainty and representative context.
Else:
    optionally show conditional slope-correction scenarios; do not assert tissue rate.
Compare actual intake with approved target and desired trajectory.
Compare hold, practical fueling redistribution, target change, workload/goal review.
If productive/acceptable or change not justified, hold.
Else propose bounded contextually reviewed change and planned reassessment.
Record alternative explanations, approval, version, and future evaluation criteria.
```

Complexity low-to-moderate, transparent; error from slope and systematic bias, coverage and regime shifts, not just regression SE. Missingness and outliers: preserve all raw data, quarantine only documented quality defects, stratify/sensitivity rather than deleting real shifts. Drift: historical estimate remains correct for old regime, marked stale for new regime. Calibration: held-out prediction and empirical interval coverage of observable mass under comparable reported target/exposure; cannot calibrate true TEE without reference. Evaluate whether action improves outcome rather than overfit to noisy slope. No individual physiological decomposition is attempted.

#### Model C — Activity-conditioned longitudinal or latent-state model (research-only)

Two distinct paths. C1 predicts observable response in logging coordinates; C2 attempts conditional physiology with independent anchors. Do not combine them under one output label. C1 is preferable as first extension if B misses meaningful predictable demand changes.

**C1 statistical modeling assumptions:**

```
g_j = α_r + β_L*(L̄_j − L_ref) + β_xᵀ (x̄_j − x_ref) + ε_j
```

where j indexes nonoverlapping or explicitly correlated windows, g_j local mass slope (kg/day), x includes completed activity (running distance/time, lifting duration/sets as separate features, other sport, optional steps) not a single arbitrary workload unit; β coefficients estimated only with sufficient independent variation. α_r includes all unmeasured influences and logging regime. Invert predicted g to reported target only if β_L is sufficiently identifiable and stable and action-relevant covariates represented; observational associations are not causal response to target changes. Fit regularized regression, use errors-in-variables sensitivity if error information exists, compare without activity covariates. Center predictors and assess rank/collinearity; training volume, device active kcal and steps can overlap. Use model to predict held-out g with prediction intervals rather than to claim estimated physiological calories. Include time trend or regime-specific intercept only with evidence; do not let flexibility absorb arbitrary bias and call it adaptation. Target adherence and realized intake are separate; forecast based on scenarios for realized behavior, not known future logs.

**C2 state-space statistical assumptions:**

```
E_t = μ_t + βᵀ (x_t − x_ref) + e_t
μ_(t+1) = μ_t + ω_t
I_t = L_t + b_r + ν_t           [only where L observed and eligible; missing L marginalized]
U_(t+1) = U_t + (I_t − E_t) Δt  [physical identity]
W_t = W_ref + (U_t−U_ref)/ρ + q_t + ε_t   [local approximation, not tissue physiology]
q_(t+1) = φ q_t + δᵀ z_t + ζ_t  [transient mass model; z = known shift context]
V_t = E_t + c_r + η_t          [only with verified total semantics]
```

μ is slowly varying conditional expenditure baseline, β activity association, q transient mass, b reporting offset, c device offset. ρ is a locally assumed energy-density mapping; do not simultaneously model independent fat/lean trajectories without additional identification. Disturbances can be correlated, heavy-tailed or change regime; simple Gaussian Kalman model only when linear-Gaussian assumptions reasonably approximate data and anchors specified. Priors for bias and coefficients must be justified by independent calibration or explicitly labeled sensitivity assumptions; weak priors along invariant direction yield diffuse or prior-dependent absolute estimates. Even fixing φ and ρ does not resolve b/c offset. If ΔU approximation fails under recomposition, model misspecified. Missing intake is latent with uncertain distribution, not zero; missing-not-at-random may require selection model or sensitivity analysis, not identifiable from observed data alone. Use filtering as-of decision time; smoothing for retrospective analysis is not deployable past prediction. Optional repeated DLW observation `D_j = mean_{t∈H_j} E_t + ε^D_j` (**established reference concept; statistical observation equation with error**) anchors mean E not daily partition. Independently measured RMR constrains one component only under compatible assumptions. Controlled intake plus storage reference may anchor b over window. Repeated device comparisons needed for c changes. 

**C2 estimand:** posterior or feasible set of average E conditional on anchors and model assumptions, or conditional changes; daily E predictions are model-based latent estimates not direct observations. Do not publish absolute estimates from ordinary unanchored fitting; reparameterize to `μ−b` and `b+c` combinations if meaningful and report their limitations. If independent anchor absent, choose C1 or B instead. If anchor and device vary, repeat calibration. Hierarchical pooling across athletes can regularize β/variance, but population priors do not identify personal bias; privacy, transfer and held-out-athlete validation required. No fixed physiological coefficients introduced here.

Pseudocode-level C evaluation:

```
Specify estimand (observed trajectory vs anchored mean EE), assumptions and eligible data.
Check invariance/rank, logging/device regime and feature availability as of prediction.
Fit simpler C1, compare with B and A using forward-held-out windows.
Only if independent anchors justify C2: specify state/noise priors and propagate uncertainty.
Assess posterior/prior sensitivity, prediction calibration and structural equivalence.
Test discontinuities, outliers, missing logs and changing activity modalities.
If out-of-sample and decision value not improved, retain simpler model.
If improved, seek independent review and prospective policy evaluation before adoption.
```

Complexity moderate to high; extra parameters may create overfitting and unstable latent states. Validate innovation autocorrelation, predictive intervals, performance across phases, sensitivity to priors and missingness, and external reference error with paired independent windows. Do not compare fitted smoothed weight to its own inputs as evidence of physiological validity. Higher-resolution telemetry may improve covariates but does not solve bias symmetry. Daily specificity not necessarily useful if decisions concern weekly average fueling and stable targets. Favor separately reviewed session nutrition guidance rather than optimizing every daily expenditure estimate.

### 4.4 Integrated feedback workflow (proposal, not implementation)

Evidence = E IDs or earlier packet claims; consensus = Packet 004 sports-nutrition/IOC guidance (pending appraisal); judgment includes modeling, coaching and engineering. Optional inputs should be sought only if likely to affect action.

| Step | Action and inherited constraint | Required observations | Optional / evidence and unresolved choice |
|---|---|---|---|
| 1 | Establish explicit mass objective (including no weight objective), block priorities and acceptable tradeoff; never impose weight goal. | athlete goals, approved block | event dates, preference; HP-P01/NU-P06; joint efficacy unknown |
| 2 | Check symptoms, restrictions, concern about disordered eating, unintentional change and fueling feasibility; clinical referral supersedes optimization. | relevant feedback when available, known restrictions | professional guidance; Packet 004 consensus; no diagnostic cutoff |
| 3 | Establish reference type and current target in force; choose A branch. | target history or demographics/activity appropriate to equation | RMR/DLW/wearable; E05–09; exact prior selection judgment |
| 4 | Characterize intake completeness and provenance by day type. | reported kcal records if used, date/units/coverage | targeted completeness feedback, meal provenance; E10; unknown bias |
| 5 | Characterize comparable weight coverage, scale/timing and changes. | timestamps, kg, protocol or uncertainty | scale replacement, hydration context; E11–12 |
| 6 | Review actual vs prescribed lifting/running/other sports and ordinary activity shifts. | completed exposure/known deviations | steps, intensity, work/travel; E15–19, CT/EN policies; unknown compensation |
| 7 | Fit descriptive robust trend with window and uncertainty. | eligible spaced mass values | replicate error, alternative smoothers; E11/E17; statistical choice |
| 8 | Identify possible transient changes and competing causes; do not presume fluid. | observed pattern/context | carb/sodium/creatine, illness, cycle, travel; E12/E13; ambiguity |
| 9 | Assess identification; declare estimand and assumptions, avoid unanchored true TEE. | data quality and model assumptions | independent reference; §4.2 proof |
| 10 | Compare A/B estimates and C only in research if justified. | same as-of context | prospective calibration; E03/E14, complexity not guaranteed |
| 11 | Review target adherence, trajectory and both performance commitments. | approved target, applicable actual/feedback, goal | comparable outcomes, burden; Packet 004/006/008; separate unknowns |
| 12 | Compare hold, increase, decrease, redistribute, clarify, defer; protect if concern. | sufficient action-specific evidence | reviewed contextual parameter; E20–23; no universal step |
| 13 | Coordinate with key sessions, recovery, food preferences, phase and feasibility; don't pay exact wearable kcal. | planned session purpose/demand | meal timing/macros if available; NU-P02/03/05 |
| 14 | Record estimate type, window, observed denominator, exclusions, assumptions, alternatives, confidence, proposal, version and approval. | frozen inputs, owner context | independent reviewer; engineering safeguard |
| 15 | Evaluate later response using prospective comparable observations, not causal attribution; keep, revise or expire reference. | actual target/adherence, trend and performance as available | richer observations; Packet 009; no guarantee of benefit |

### 4.5 Quantitative parameter appraisal

Numbers below are source-specific, not operational thresholds. Class codes: T = tested protocol, E = empirical estimate/association, M = measurement agreement/error, C = consensus, S = statistical assumption, P = common convention, V = contextual candidate requiring validation. None is authorized by this packet.

| Parameter / value | Class, source, conditions and limitations | Reviewer decision |
|---|---|---|
| RMR Ten-Haaf 80.2% within ±10%; other equations 40.7–63.7% | M, E05 precision subset, not individual error bound or TEE | choose appropriate equation; validate external population and PAL separately |
| Controlled maintenance 10 days, ±1 kg; ratio range .87–1.27 | T/M, E03 inpatient six adults | not logging-day minimum or equivalence margin |
| Wearable laboratory median EE errors ≥20% across seven devices | M, E07 specific tasks/models | no universal correction factor |
| Elite female runners accelerometer TEE +416 ±242 kcal/day | M, E08 particular method vs DLW | 7-day DLW; reported LoA −59 to +891 kcal/day; verify repeatability; no transfer as correction |
| Athlete reporting vs DLW mean −19% | M, E10 mixed athlete studies, not direct intake-error-only | no automatic multiplier; assess actual energy imbalance and individual context |
| Morning mass variation 0.51 ±0.20 kg / CV .66 ±.24% | M, E11 active men in heat with fluid guidance | not universal minimum detectable change; estimate local noise from comparable measurements |
| Carb sequence +2.4 kg, water +2.2 L | E/T, E12 historical controlled sequence | demonstrates possible magnitude, not conversion for every glycogen change |
| 3,500 kcal/lb ≈7,716 kcal/kg | P, E13 static convention (conversion), ignores dynamic expenditure/composition | use only labeled sensitivity illustration if defensible; no universal ρ |
| Modeled >28 daily weights for CI <300 kcal/day | S/E, E17 virtual subjects, ΔEI estimate | do not make 28 days required or sufficient for coaching; choose horizon by uncertainty and regime stability |
| CALERIE individual RMS deviation 215 kcal/day for ΔEI | M, E14 2-year model vs intake-balance | not daily TEE error or calibrated predictive interval in hybrid athletes |
| Loss targets .7 vs 1.4%/week, realized ~.7 vs 1.0%; intake reductions 19 vs 30% | T/E, E20 elite mixed sports; unequal intervention duration | evidence for tradeoffs, not universally safe rate or precise deficit |
| Surplus/restriction and protein/CHO guidance | E/C, prior Packet 004 conditions and pending claims | retain reviewed context; no new rate of gain, deficit or macro percentage invented |
| Trend window, coverage, practical stability band, smoothing λ, target step, gain K, adjustment frequency, max rate of change | S/V, candidate choices only | choose based on local repeatability/coverage, acceptable target trajectory, action sensitivity and qualified nutrition review; prospectively calibrate against no-change and simpler baselines |

**Parameter selection procedure:** state decision (e.g. whether a change is worthwhile rather than precise tissue rate), define athlete-agreed practical acceptable outcomes and assessment horizon, estimate observation variability with comparable data, evaluate whether candidate actions differ under plausible biases/missingness and windows, choose lowest-complexity defensible parameter with reviewer rationale and safety bounds, predefine reevaluation plan and abort criteria, freeze version; test against synthetic missingness, prospective forecast and actual joint outcomes. No universal rate of gain or loss, calorie increment, minimum log days or time window emerges from the retrieved studies. Published ranges may inform reviewed contextual targets but are not defaults. If current mass goal is inappropriate or uncertain, do not solve via calorie restriction.

### 4.6 Nutritional periodization (extends 004 and 006)

| Block or context | Recommended candidate priorities | Estimation implication |
|---|---|---|
| Strength emphasis | adequate energy and protein, protect lifting and secondary running, CHO available for demanding sessions | stable habitual target may suffice; no automatic surplus solely for strength; monitor both objectives |
| Hypertrophy emphasis | adequate energy/protein, discuss body-composition tradeoffs, retain running fuel | surplus may increase fat as well as lean mass; mass trend not composition; avoid universal gain rate |
| Endurance emphasis | prioritize feeding opportunities for long/quality sessions and doubles; maintain strength stimulus and protein | larger workload may justify fueling before trend identifies change; do not equate estimated exercise kcal with needed increase |
| Balanced | coordinate daily distribution and weekly adequacy, no unnecessary tracking | hold productive target despite noisy device or mass changes; review actual joint burden |
| Higher-volume phases | food access, appetite, between-session recovery, avoid inadvertent deficit | reassess activity regime and representativeness; new estimate not instantly available |
| Intensification | protect key session quality, not fixed calorie reduction with volume | volume decrease not proof lower requirement; retain fueling as needed |
| Deload/transition | preserve recovery and protein, adjust according to context | no automatic calorie decrease; transient mass and activity changes confound |
| Taper/event | preserve priority performance, appropriate event fueling | glycogen/water-associated mass increase may be desired; do not restrict to correct short-term scale shift |
| Intentional fat loss | shared decision, gradual contextual goal, protect performance, no aggressive restriction amid concerning burden | estimate logged target not physiological deficit; if recovery worsens, pause/review rather than intensify cut |
| Intentional gain | monitor acceptable mass trajectory and both disciplines; discuss composition uncertainty | lean gain not identified from scale; avoid escalating surplus merely because mass temporarily stable |
| Interruption/travel/illness | feasible meals, safety and return-to-training; defer restrictive optimization | mark regime, retain old reference as historical; recalibrate once representative |

General guidance (meal composition, protein and carbohydrate recommendations from reviewed sources, fueling opportunities) need not require macros/meal logs. For adherence, actual intake and timing are different observations. For effectiveness, comparable performance and tolerance plus trajectory matter; neither a successful weight trend nor target compliance establishes physiological adequacy.

### 4.7 Worked longitudinal examples (all synthetic)

These are invented fixtures, not personal records, empirical estimator accuracies, validated thresholds or prescriptions. Numbers illustrate behavior and arithmetic; windows are not mandatory minima. Assume consenting adults, no contraindications unless stated, and qualified review before any target change. Weight values are illustrative weekly summaries of comparable daily readings where specified. A/B/C estimates are not necessarily estimates of the same quantity.

#### A — Consistent logging and stable weight

- Approved balanced block, 3 lifts and 3 runs totaling roughly 150 running minutes/week, weight maintenance and strength/run progress. Four successive seven-day mean reported intakes: 2,580, 2,620, 2,590, 2,610 kcal/day; morning mean masses: 79.9, 80.1, 80.0, 80.0 kg. All days reported complete in this fixture, scale/protocol unchanged; comparable lifting and running progressing. Mean wearable total 2,850 kcal/day; illustrative population prior 2,750 kcal/day. True intake and tissue-energy change not independently measured. Synthetic ground truth for test only: true I and E both 2,800 kcal/day, roughly stable stored energy; reporting offset 200, device offset 50 kcal/day. Coach never sees ground truth.
- A1/A2 are conditional 2,750/2,850 references; A3/B logged mean = (2580+2620+2590+2610)/4 = 2,600 kcal/day. Stable observed mass is consistent with practical maintenance; uncertainty about tiny trend and composition persists. Report M_L≈2,600 conditional on this regime, not true TDEE=2,600. C with unanchored biases cannot identify 2,800; adding device data does not resolve it.
- Alternatives: hold current approved target 2,600, investigate if independent physiological estimate necessary, adjust timing around key sessions without changing mean. Prefer hold because goals/response acceptable; no unnecessary target change. Later evaluate representative logs, comparable weights, session quality and both objectives. If logging changes, expire reference. Actual data do not establish energy availability even with stable mass.

#### B — Observationally equivalent systematic underreporting

Same 28-day observed history for two synthetic worlds: complete-intent logged mean 2,600, wearable mean 2,800, stable comparable weights around 80 kg, same activity records; no measured composition or DLW. Assume negligible random noise for the counterexample and stable stored energy.

| Quantity (kcal/day) | World B1 | World B2 |
|---|---:|---:|
| True intake | 2,600 | 3,000 |
| True expenditure | 2,600 | 3,000 |
| Reporting offset b | 0 | 400 |
| Device offset c | +200 | −200 |
| Reported intake L | 2,600 | 2,600 |
| Wearable V | 2,800 | 2,800 |
| Storage change/day | 0 | 0 |

Both imply b+c=200 and identical observations. B estimates same operational reference 2,600, conditional on reporting regime, while the physiological values differ 400. Model A wearable estimate 2,800 is neither world's true TEE. C cannot choose B1 or B2 absent calibration; equally tight noise distributions do not help. If independently measured DLW average 3,000 with known reference uncertainty and storage stable, B2-like physiological estimate becomes better anchored; b≈400 only under storage assumption, not inferred from log discrepancy alone. If both wearable and log were 2,600, same invariance would still allow both worlds with adjusted c. Hold current effective target if appropriate; no recommendation to “correct” logging by 400. Evaluate whether continued logged target actually retains desired trajectory; true physiology only via reference substudy. No need for invasive measurement if decision unchanged.

#### C — Running exposure increases before weight trend resolves

- Endurance-emphasis block; 3 strength sessions, running increases from 150 to 210 minutes/week. Previously stable at logged 2,700 and mass 75.0 kg; wearable 2,850. First two weeks at new exposure: logged 2,700 and 2,690, wearable totals 3,120 and 3,090; mean masses 74.8 and 75.2. One warm run, changed fueling opportunities, unknown full composition; assumed synthetic possible truth is incremental expenditure +150 kcal/day with water variability, but coach cannot see this. Another plausible world has less change in expenditure and incomplete reporting.
- A2 would show +255 kcal/day difference in average device total; exact compensation would change 2,700 to 2,955, unjustified. B old maintenance 2,700 is stale/conditional; new two-week mass pattern uncertain and not enough evidence of stable new regime in this fixture, not a universal duration rule. C1 can flag activity regime and forecast uncertain response if calibrated; untrained β must not be invented; C2 no absolute inference.
- Candidate action: protect long-run/quality-session feeding and assess hunger, actual intake, performance and fatigue; offer practical extra food or CHO timing as appropriate without presenting a measured deficit. Discuss whether average target should rise if repeated credible loss or fueling difficulty; do not wait for mass loss when safety concerns exist. Compare holding with approved fueling redistribution or contextual increase. In this fixture no symptoms and good training: keep mean target temporarily with explicit review and optional targeted fueling feedback. If later representative mean weights 74.5, 74.2, 73.9 at similar intake and unintentional loss, review upward target and/or burden; no exact compensation calculation. Independent paired reference intervals needed to validate activity coefficients. No automatic reduction to previous running dose.

#### D — Abrupt mass increase following carbohydrate loading or creatine

- Synthetic endurance taper, approved weight maintenance and priority 10 km. Logged intake around 2,800; pre-shift mean 70.0 kg, then daily comparable masses 70.9, 71.2, 71.1 after increased carbohydrate; alternatively newly started creatine. Wearable total 2,800; no measured composition or water. For illustrative ground truth, assume mass increase is predominantly transient water/substrate mass; exact components unknown to coach. Athlete reports normal fueling and improved session quality.
- Naive static calculation using 1.1 kg/3 days × 7,716 kcal/kg would imply ~2,829 kcal/day apparent surplus, larger than most plausible change in logged intake; it wrongly assigns all mass to tissue and ignores timing. Model A4 holds; B flags discontinuity and suspends slope-based correction; C q-state may describe shift but cannot prove water or infer amount without external reference. It may also be a genuine combined mass change. No calorie restriction to undo taper-related mass increase. Continue agreed fueling/priority assessment; compare post-event standardized weights and context before revisiting target. No mandatory water correction or fixed “washout” days; later sustained trajectory may justify review.

#### E — Missing weekends and changed logging regime

- Previous representative week logged 2,500/day, stable 82 kg. New travel week observed weekdays: 2,400, 2,500, 2,300, 2,600, 2,400 (mean 2,440); Saturday absent, Sunday partial 900. Weights measured only Monday 82.0 and Friday 82.6 at different times; more restaurant meals, scale change. No independent TEE. One synthetic possible true complete weekend intake 3,400 and 3,200; under assumption weekdays accurate, full-week mean = (12,200+6,600)/7 ≈2,686. Another possible weekend 2,400/day gives ≈2,429. Neither known. Wearable daily estimate 2,700 with altered nonwear.
- Missing-as-zero calculation with partial Sunday would yield (12,200+900)/7≈1,871, false; averaging five eligible days gives 2,440 **only for observed weekdays**, not representative maintenance. Model A4 carries safe prior target 2,500, stale under travel; B defers new maintenance and trend, C missingness model cannot identify unobserved weekends from data alone. Do not impute based on desire to meet target. Ask if logs represent complete days and whether travel/activity differed; no insistence on reconstructing every meal. Resume comparable weighing if desired, review after representative coverage; qualitative fueling regardless. No target adjustment merely from noisy weight increase. If reporting practice permanently changes, create new regime; prior reference not necessarily transportable. Safety concerns independent of log coverage.

#### F — Body-composition goal conflicts with performance

- Synthetic athlete wants gradual loss while maintaining squat and half-marathon preparation. Approved reported target 2,500; four weekly means logged 2,490, 2,470, unknown due missing days, 2,450 (completeness uncertain). Mean comparable weights 86.0, 85.6, 85.2, 84.8 kg. Running duration increases 180→240 min/week, comparable threshold pace at similar effort deteriorates; squat 150 kg ×5 at RPE8 becomes 150 ×4 at RPE9, rising general fatigue and poor sleep. Wearable average 3,200; no macros, medical assessment, measured FFM or independent EE. Synthetic possible causes include restriction, increased burden and disrupted sleep; true b and E unknown.
- Naive estimate from first-to-last mass change −1.2 kg /21 days ×7,716 ≈ −441 kcal/day storage proxy; adding 441 to ~2,470 would suggest ~2,911 TDEE under unverified assumptions, not identified. Do not use this to intensify deficit, set clinical EA or declare device wrong. A/B can record conditional reference or suspend maintenance recalibration; C cannot diagnose cause. Existing target may not be appropriate despite apparent goal progress; prioritize health and both performance commitments, clarify fueling, illness, sleep, adherence and schedule. Discuss pausing weight-loss objective and restoring practical fueling, propose hold progression or reduce selected burden where warranted, refer to sports dietitian/clinician for persistent multi-domain decline or concerning symptoms. If urgent symptoms, urgent care as appropriate. No automated diagnosis of REDs. Athlete approval required for target/workload change; restrictions respected regardless. Track subsequent performance, symptoms, tolerability and representative mass/intake if athlete chooses, without attributing improvement to a single change. No further restriction until reviewed.

### 4.8 Prospective estimation and decision evaluation (dependency for Packet 009)

Separate four study endpoints: (1) absolute/mean EE agreement with independent reference; (2) prediction of observable mass/trajectory conditional on information available at decision; (3) quality and stability of recommendations; (4) actual joint health/performance/nutrition outcomes. A method can excel at one without another. Use a reference substudy if absolute accuracy matters; DLW averaged over matching windows, measured RMR only for rest, controlled intake/DXA balance for separate estimands. Reference has error; report it, do not call it exact daily truth. No direct comparative trial of proposed models in target population identified.

| Comparator | Inputs and estimand | Evaluation question |
|---|---|---|
| A1 population | appropriate RMR equation + contextual PAL | absolute averaged estimate vs reference; predictive baseline |
| A2 wearable | eligible total EE | does device average agree with reference, and do changes track reference changes? |
| A3/A4 historical/carry | representative logged mean/current target | does a simple stable target already achieve acceptable response? |
| B | logged intake and robust mass trajectory | incremental forecasting or action utility vs carry and simple trend |
| C1 | B plus activity covariates | prospective incremental prediction of trajectory and practical decisions |
| C2 | C1 plus independent measurement-error/latent anchors | conditional TEE calibration, prospective prediction, uncertainty and decision utility |

**Stage 1 — synthetic and historical conformance.** Freeze inputs/as-of dates and known approval history; simulate observationally equivalent worlds, known biases, correlated errors, irregular records, drift, abrupt fluids and nonrandom missingness. Test invariance and refusal to overidentify, data eligibility, semantics and exact replay. Historical rolling-origin backtest with blocked holdouts and athlete-level external holdout where possible; tune hyperparameters only within training folds; never use future observations, retrospective smoothing or post-decision realized intake as if known prospectively. Define horizon and whether predicting target adherence vs actual future logs vs mass conditional on specified intake; use scenarios if future behavior uncertain. Evaluate against persistence, simple rolling mean and B. Avoid overlap leakage from rolling windows. Quantify MAE/RMSE, signed bias, calibration/coverage of prediction intervals, conditional error by phase/coverage, abstention rate and performance conditional on eligibility; include all denominators. Compare intervals using calibration and sharpness/proper score, not narrowness alone. Report sensitivity to logging-offset priors and missingness; evaluate reference agreement (paired differences, LoA with assumptions, not correlation alone). Do not assess TEE accuracy from weight prediction alone.

**Stage 2 — prospective shadow mode.** Register estimands, horizon, baseline and practical outcome criteria before observation; compute A/B/C concurrently but no treatment assigned from unreviewed output. Evaluate stability of suggested targets, action discordance and its resolution with athlete feedback or independent review; identify false alarms, delays, unnecessary tracking, coverage and cost. Obtain consent for optional reference substudy and use repeated matched windows to test calibration and response to workload change. Don't infer that more tracking improves decisions just because some prediction errors shrink.

**Stage 3 — reviewed policy comparison.** After scientific/method/safety approval, compare simple reviewed target policy vs reviewed B, then activity-conditioned or richer variant only if incremental value plausible. Prospective randomized or pragmatic parallel design where appropriate; within-athlete crossover requires attention to carryover, training phase and changing adaptation. Specify target and acceptable performance tradeoffs before randomization; keep nutrition safety and fueling baseline common, record actual vs intended exposure/adherence, differences in logging behavior, attrition and cointerventions. Predefine primary outcome (e.g., time within agreed trajectory with protected performance or a transparent multi-outcome assessment), secondary outcomes (strength/run outcomes, fatigue/tolerance, adherence, number/magnitude of target changes, unnecessary changes, logging burden and adverse concerns). Avoid arbitrary composite score; report objective-specific tradeoffs and uncertainty. Blinded outcome assessment where feasible. Analyze intention-to-treat and adherence/coverage descriptively, with careful causal interpretation; don't condition primary treatment effect on post-randomization success. Compare incremental observation sets and model complexity separately to isolate decision value. Qualified oversight and referral, pause/revise if harm concerns. Packet 009 will formalize evaluation design, sample size and decision criteria; none claimed here.

## 5. Draft J1 evidence catalog additions

This is an additive **fragment**, not a registered CorpusRelease. All sources, claims and methods pending; approvals null, transfers empty. Reuse existing Packet 004 sources and claims by exact key. Empirical validation records use specific measurement comparators and outcomes rather than intervention-effect language. J1 currently expresses these as scoped claims but lacks dedicated estimand/measurement error/model-assumption/identifiability types; preserve mathematical proof, consensus guidance, and parameters in narrative rather than encode as intervention effects. Date precision for Cheuvront and Garthe is bibliographic issue convention; reviewer must verify. The fragment is intentionally narrower than the evidence table. Cross-question methods cite prior claims; no new qualification or supersession edges needed.

```json
{
  "questions": [
    {
      "id": "energy-rmr-equation-agreement",
      "description": "How do population equations agree with resting calorimetry in athletes?",
      "gap": "Individual external prediction, PAL and joint-athlete validation unresolved."
    },
    {
      "id": "energy-controlled-maintenance-agreement",
      "description": "How does controlled weight-maintenance intake compare with DLW expenditure?",
      "gap": "Free-living app intake and individual equivalence not established."
    },
    {
      "id": "energy-device-criterion-agreement",
      "description": "How do activity or total expenditure estimates agree with reference measurements?",
      "gap": "Specific device, construct, time window, repeated-change reliability and calibration required."
    },
    {
      "id": "energy-mass-observation-variability",
      "description": "How variable are comparable body-mass observations under defined conditions?",
      "gap": "No universal tissue-change detection threshold or sampling window."
    },
    {
      "id": "energy-longitudinal-intake-model-validation",
      "description": "How do weight-based models estimate changes in intake against reference intake-balance methods?",
      "gap": "Absolute TEE, athlete transfer and decision benefit not established."
    },
    {
      "id": "energy-athlete-weight-loss-rate",
      "description": "How do different planned loss rates affect athlete body composition?",
      "gap": "Different duration and realized exposure; no universal safe loss rate or hybrid policy."
    },
    {
      "id": "energy-operational-maintenance-methodology",
      "description": "How should eligible reported intake and weight response inform nutrition review?",
      "gap": "Structural ambiguity, reporting stability and prospective decision value require review."
    }
  ],
  "sources": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "heymsfield-controlled-maintenance@1",
      "citation": "Heymsfield SB, Peterson CM, Thomas DM, et al. Establishing energy requirements for body weight maintenance: validation of an intake-balance method. BMC Res Notes. 2017;10:220.",
      "doi": "10.1186/s13104-017-2546-4",
      "record_url": "https://doi.org/10.1186/s13104-017-2546-4",
      "published_on": "2017-06-26",
      "design": "Controlled inpatient intake-balance criterion comparison",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "CC BY 4.0 reported by publisher; independent rights review outstanding.",
      "appraisal": "E03: six non-obese adults, 10-day balance protocol, group similarity not individual equivalence. Verify exact paired data and DLW timing.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "oneill-athlete-rmr@1",
      "citation": "O’Neill JER, Corish CA, Horner K. Accuracy of resting metabolic rate prediction equations in athletes: a systematic review with meta-analysis. Sports Med. 2023;53:2373–2398.",
      "doi": "10.1007/s40279-023-01896-z",
      "record_url": "https://doi.org/10.1007/s40279-023-01896-z",
      "published_on": "2023-08-26",
      "design": "Systematic review and meta-analysis of prediction agreement",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "CC BY 4.0 reported by publisher; independent rights review outstanding.",
      "appraisal": "E05: study subsets differ by equation and metric, derivation overlap, calorimetry preparation heterogeneous. Verify Table 3 denominators and subgroup scope.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "shcherbina-device-energy@1",
      "citation": "Shcherbina A, Mattsson CM, Waggott D, et al. Accuracy in wrist-worn, sensor-based measurements of heart rate and energy expenditure in a diverse cohort. J Pers Med. 2017;7:3.",
      "doi": "10.3390/jpm7020003",
      "record_url": "https://doi.org/10.3390/jpm7020003",
      "published_on": "2017-05-24",
      "design": "Laboratory device criterion comparison",
      "access": "abstract",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "Reuse rights not independently verified; metadata, links and original factual summaries only.",
      "appraisal": "E07: abstract result for seven older devices and specific tasks. Verify error definition, device and activity strata in full text.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "ma-runner-dlw@1",
      "citation": "Ma D, Hashii-Arishima Y, Yokoyama K, et al. Validity of triaxial accelerometer for estimating total energy expenditure in elite female university athletes: a doubly labeled water study. Eur J Appl Physiol. 2026;126:5841–5850.",
      "doi": "10.1007/s00421-026-06458-5",
      "record_url": "https://doi.org/10.1007/s00421-026-06458-5",
      "published_on": "2026-10-24",
      "design": "Seven-day accelerometer versus DLW criterion comparison",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "Reuse rights not independently verified; metadata, links and original factual summaries only.",
      "appraisal": "E08: 16 elite female university runners; waist Actimarker, PAL/BMR method; verify BMR and DIT definition and repeated-measure limits.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "murakami-paee-agreement@1",
      "citation": "Murakami H, Kawakami R, Nakae S, et al. Accuracy of 12 wearable devices for estimating physical activity energy expenditure using a metabolic chamber and the doubly labeled water method: validation study. JMIR Mhealth Uhealth. 2019;7:e13938.",
      "doi": "10.2196/13938",
      "record_url": "https://doi.org/10.2196/13938",
      "published_on": "2019-08-02",
      "design": "Chamber and free-living wearable criterion comparison",
      "access": "abstract",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "Reuse rights not independently verified; metadata, links and original factual summaries only.",
      "appraisal": "E09: abstract and indexed original passages; residual PAEE not directly measured. Verify device-specific distributions and multiple comparisons.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "cheuvront-morning-mass@1",
      "citation": "Cheuvront SN, Carter R III, Montain SJ, Sawka MN. Daily body mass variability and stability in active men undergoing exercise-heat stress. Int J Sport Nutr Exerc Metab. 2004;14:532–540.",
      "doi": "10.1123/ijsnem.14.5.532",
      "record_url": "https://doi.org/10.1123/ijsnem.14.5.532",
      "published_on": "2004-10-01",
      "design": "Retrospective repeated morning mass observation",
      "access": "abstract",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "Reuse rights not independently verified; metadata, links and original factual summaries only.",
      "appraisal": "E11: issue month October 2004, OpenAlex bibliographic date 2004-10-01 (day may be issue convention; verify). Heat and fluid protocol specific.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "sanghvi-intake-change-validation@1",
      "citation": "Sanghvi A, Redman LM, Martin CK, Ravussin E, Hall KD. Validation of an inexpensive and accurate mathematical method to measure long-term changes in free-living energy intake. Am J Clin Nutr. 2015;102:353–358.",
      "doi": "10.3945/ajcn.115.111070",
      "record_url": "https://doi.org/10.3945/ajcn.115.111070",
      "published_on": "2015-06-03",
      "design": "Secondary model validation using CALERIE restriction-arm data",
      "access": "abstract",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "Reuse rights not independently verified; metadata, links and original factual summaries only.",
      "appraisal": "E14: abstract and indexed Methods, Results and Discussion passages; direct PMC open blocked. Change in EI from baseline, not absolute TEE; obtain full Table 1 and supplement before approval.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "garthe-athlete-loss-rate@1",
      "citation": "Garthe I, Raastad T, Refsnes PE, Koivisto A, Sundgot-Borgen J. Effect of two different weight-loss rates on body composition and strength and power-related performance in elite athletes. Int J Sport Nutr Exerc Metab. 2011;21:97–104.",
      "doi": "10.1123/ijsnem.21.2.97",
      "record_url": "https://doi.org/10.1123/ijsnem.21.2.97",
      "published_on": "2011-04-01",
      "design": "Randomized comparison of planned weight-loss rates",
      "access": "abstract",
      "checked_on": "2026-11-25",
      "publication_check": "Publication record and specified result located; comprehensive correction, version, retraction and independent review outstanding.",
      "rights": "Reuse rights not independently verified; metadata, links and original factual summaries only.",
      "appraisal": "E20: issue month April 2011, bibliographic issue date 2011-04-01; verify day. Different achieved rates and durations, DXA hydration, training exposure; verify dispersion and follow-up overlap.",
      "next_review": "2027-02-25"
    }
  ],
  "claims": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "controlled-maintenance-intake-dlw-ratio@1",
      "scope": {
        "question": "energy-controlled-maintenance-agreement",
        "objective": "assess-measurement-quality",
        "population": "non-obese-adults",
        "experience": "unknown",
        "intervention": "controlled-constant-metabolizable-intake",
        "comparator": "doubly-labeled-water-tee",
        "outcome": "intake-to-expenditure-ratio",
        "horizon": "ten-days",
        "block_context": "controlled-maintenance"
      },
      "assertion": "In the small controlled maintenance sample, group mean intake was close to DLW expenditure but individual ratios differed.",
      "limitations": "Six adults, inpatient control and weight bound; no equivalence test or free-living log validation.",
      "quality": "moderate",
      "assessment": "Study-specific descriptive agreement, not a general error distribution.",
      "transfers": [],
      "support": [
        {
          "source": "heymsfield-controlled-maintenance@1",
          "locator": "Results and Fig. 3",
          "result": "Intake 2390 ±543 vs DLW 2373 ±713 kcal/day; mean ratio 1.03 ±0.15, range 0.87–1.27.",
          "restriction": "Constant controlled food intake during ten-day balance period."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "ten-haaf-athlete-rmr-group-agreement@1",
      "scope": {
        "question": "energy-rmr-equation-agreement",
        "objective": "assess-measurement-quality",
        "population": "adult-athletes",
        "experience": "mixed",
        "intervention": "ten-haaf-age-height-weight-equation",
        "comparator": "indirect-calorimetry-rmr",
        "outcome": "standardized-rmr-difference",
        "horizon": "single-assessment",
        "block_context": "resting-energy-assessment"
      },
      "assertion": "The pooled standardized difference between Ten-Haaf predicted and measured RMR was near zero in the assessed athlete comparisons.",
      "limitations": "Four studies, seven comparisons, 204 participants; possible local derivation bias and heterogeneous methods; not equivalence.",
      "quality": "moderate",
      "assessment": "Accuracy of group estimate is not individual precision or TEE validity.",
      "transfers": [],
      "support": [
        {
          "source": "oneill-athlete-rmr@1",
          "locator": "Results §3.4.3 Fig. 2",
          "result": "ES 0.04 (95% CI −0.16 to 0.23); I²=0%.",
          "restriction": "Resting energy expenditure only; no PAL or exercise estimate."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "ten-haaf-athlete-rmr-within-bound@1",
      "scope": {
        "question": "energy-rmr-equation-agreement",
        "objective": "assess-measurement-quality",
        "population": "adult-athletes",
        "experience": "mixed",
        "intervention": "ten-haaf-age-height-weight-equation",
        "comparator": "indirect-calorimetry-rmr",
        "outcome": "fraction-within-ten-percent",
        "horizon": "single-assessment",
        "block_context": "resting-energy-assessment"
      },
      "assertion": "The review reported that 80.2% of participants in its Ten-Haaf precision synthesis had predictions within 10% of measured RMR.",
      "limitations": "Precision subset differs from accuracy subset; verify exact denominator and overlap; 10% is study criterion not personal uncertainty.",
      "quality": "moderate",
      "assessment": "Prediction agreement criterion, not reliability or confidence interval.",
      "transfers": [],
      "support": [
        {
          "source": "oneill-athlete-rmr@1",
          "locator": "Results §3.4.6 Table 3",
          "result": "80.2% within ±10%; other reviewed equation estimates 40.7–63.7%.",
          "restriction": "Not a claim of TEE accuracy; verify individual denominator before approval."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "laboratory-wrist-energy-error@1",
      "scope": {
        "question": "energy-device-criterion-agreement",
        "objective": "assess-measurement-quality",
        "population": "diverse-adult-volunteers",
        "experience": "mixed",
        "intervention": "seven-wrist-worn-device-estimates",
        "comparator": "indirect-calorimetry",
        "outcome": "median-energy-expenditure-error",
        "horizon": "laboratory-session",
        "block_context": "activity-energy-assessment"
      },
      "assertion": "None of seven studied wrist devices achieved median energy expenditure error below 20% in the reported laboratory comparison.",
      "limitations": "Older specific devices, seated/walk/run/cycle tasks; no daily TEE or strength-specific validation.",
      "quality": "moderate",
      "assessment": "Check exact error definition and strata; not signed correction.",
      "transfers": [],
      "support": [
        {
          "source": "shcherbina-device-energy@1",
          "locator": "Abstract Results",
          "result": "No device median EE error below 20%.",
          "restriction": "Laboratory tasks; does not quantify current devices or longitudinal change."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "runner-accelerometer-dlw-tee-agreement@1",
      "scope": {
        "question": "energy-device-criterion-agreement",
        "objective": "assess-measurement-quality",
        "population": "elite-female-university-runners",
        "experience": "endurance-trained",
        "intervention": "waist-triaxial-accelerometer-tee",
        "comparator": "doubly-labeled-water-tee",
        "outcome": "mean-tee-method-difference",
        "horizon": "seven-days",
        "block_context": "free-living-energy-assessment"
      },
      "assertion": "The tested accelerometer-based TEE method overestimated mean DLW expenditure in this runner sample.",
      "limitations": "16 young women, single method and seven-day period; no repeated change validation or hybrid population.",
      "quality": "moderate",
      "assessment": "Criterion agreement, not causal effect; no universal correction.",
      "transfers": [],
      "support": [
        {
          "source": "ma-runner-dlw@1",
          "locator": "Results Fig. 2B-2; Methods DLW and triaxial accelerometer",
          "result": "Bias +416 ±242 kcal/day (~12.5%); LoA −59 to +891 kcal/day; r=.828.",
          "restriction": "Waist Actimarker EW4800 PAL/BMR method; not other devices."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "free-living-wearable-paee-underestimation@1",
      "scope": {
        "question": "energy-device-criterion-agreement",
        "objective": "assess-measurement-quality",
        "population": "healthy-adults",
        "experience": "mixed",
        "intervention": "twelve-wearable-paee-estimates",
        "comparator": "dlw-derived-residual-paee",
        "outcome": "device-level-underestimation",
        "horizon": "fifteen-days",
        "block_context": "free-living-energy-assessment"
      },
      "assertion": "Ten of twelve tested wearable PAEE estimates were significantly below the DLW-derived PAEE comparator.",
      "limitations": "19 adults; comparator subtracts BMR and assumed TEF; devices outdated; no equivalence from nonsignificance.",
      "quality": "moderate",
      "assessment": "Device-count finding not person-level error or total expenditure.",
      "transfers": [],
      "support": [
        {
          "source": "murakami-paee-agreement@1",
          "locator": "Abstract Results, 15-day free-living comparison",
          "result": "Reference PAEE 728.0 ±162.7 kcal/day; 10/12 devices significantly underestimated.",
          "restriction": "Residual PAEE, not TEE; verify multiplicity and device-level results."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "morning-mass-variability-active-men@1",
      "scope": {
        "question": "energy-mass-observation-variability",
        "objective": "assess-measurement-quality",
        "population": "active-men",
        "experience": "active",
        "intervention": "repeated-first-morning-weighing",
        "comparator": "within-person-repeated-measurements",
        "outcome": "day-to-day-body-mass-variability",
        "horizon": "four-to-fifteen-days",
        "block_context": "exercise-heat-fluid-monitoring"
      },
      "assertion": "First-morning body mass varied across days in active men exercising in heat under fluid replacement guidance.",
      "limitations": "Retrospective; specific environment, sex and hydration protocol; no tissue inference.",
      "quality": "moderate",
      "assessment": "Descriptive variability not universal minimum detectable change.",
      "transfers": [],
      "support": [
        {
          "source": "cheuvront-morning-mass@1",
          "locator": "Abstract Results",
          "result": "Daily variability 0.51 ±0.20 kg; CV 0.66 ±0.24%.",
          "restriction": "65 men; 4–15 consecutive days."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "calerie-weight-model-intake-change-agreement@1",
      "scope": {
        "question": "energy-longitudinal-intake-model-validation",
        "objective": "assess-measurement-quality",
        "population": "calerie-calorie-restriction-adults",
        "experience": "unknown",
        "intervention": "demographic-and-weight-dynamic-model",
        "comparator": "dlw-dxa-intake-balance",
        "outcome": "energy-intake-change-agreement",
        "horizon": "two-years-four-intervals",
        "block_context": "calorie-restriction"
      },
      "assertion": "The model-estimated changes in intake were close to intake-balance estimates at group level but showed substantial individual disagreement.",
      "limitations": "140 CALERIE restriction participants; reference estimated, not independent absolute intake; body-weight model assumptions and selected completers; not daily EE.",
      "quality": "moderate",
      "assessment": "Change from baseline only; agreement not prospective hybrid intervention efficacy.",
      "transfers": [],
      "support": [
        {
          "source": "sanghvi-intake-change-validation@1",
          "locator": "Abstract Results; Results Table 1 and Fig. 3; Discussion agreement paragraph",
          "result": "Mean ΔEI within 40 kcal/day; overall individual RMS deviation 215 kcal/day; Discussion reports total LoA span ~800–1000 kcal/day.",
          "restriction": "Four intervals in two-year calorie restriction; verify complete Table 1 and supplement."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "athlete-slower-loss-lean-mass@1",
      "scope": {
        "question": "energy-athlete-weight-loss-rate",
        "objective": "body-composition-during-training",
        "population": "elite-athletes",
        "experience": "trained",
        "intervention": "slower-planned-weight-loss",
        "comparator": "faster-planned-weight-loss",
        "outcome": "dxa-lean-body-mass-change",
        "horizon": "intervention-endpoint",
        "block_context": "energy-restriction-with-resistance-training"
      },
      "assertion": "The slower-loss group had a greater lean-body-mass change than the faster-loss group in the studied intervention.",
      "limitations": "Small groups, different durations, realized rates and accumulated resistance exposure; DXA hydration; no direct hybrid running outcome.",
      "quality": "moderate",
      "assessment": "Target rates 0.7 and 1.4% per week, actual rates differ; no universal target.",
      "transfers": [],
      "support": [
        {
          "source": "garthe-athlete-loss-rate@1",
          "locator": "Abstract Results",
          "result": "Lean mass +2.1 ±0.4% vs −0.2 ±0.7%; between-group p<.01.",
          "restriction": "24 randomized athletes; verify dispersion, attrition and duration."
        }
      ]
    }
  ],
  "relations": [],
  "methods": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "energy-regime-eligible-observation-review@1",
      "question": "energy-operational-maintenance-methodology",
      "description": "Review intake completeness, weight comparability and activity regime before quantitative recalibration.",
      "provenance": "Original Fitness Intelligence candidate programming methodology, Packet 007 §§3–4; independent review required.",
      "tradeoffs": "May defer useful changes when data sparse; never infer missing as zero or demand unnecessary tracking.",
      "claims": [
        "athlete-logged-intake-dlw-disagreement@1",
        "morning-mass-variability-active-men@1",
        "wearable-energy-expenditure-validity@1"
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "energy-logging-adjusted-maintenance-review@1",
      "question": "energy-operational-maintenance-methodology",
      "description": "Use representative logged mean and observed mass trend as conditional operational reference, with explicit estimand and uncertainty.",
      "provenance": "Original Fitness Intelligence candidate programming methodology, Packet 007 §§3–4; independent review required.",
      "tradeoffs": "Does not identify physiological TEE or adequacy; relies on stable logging and representative context.",
      "claims": [
        "controlled-maintenance-intake-dlw-ratio@1",
        "calerie-weight-model-intake-change-agreement@1",
        "athlete-logged-intake-dlw-disagreement@1"
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "energy-activity-aware-target-review@1",
      "question": "energy-operational-maintenance-methodology",
      "description": "Review changed training demand, fueling opportunities and acceptable mass trajectory; compare hold, adjustment, redistribution and deferral.",
      "provenance": "Original Fitness Intelligence candidate programming methodology, Packet 007 §§3–4; independent review required.",
      "tradeoffs": "No exact wearable eat-back or validated numerical change; safety and performance goals prevail.",
      "claims": [
        "runner-accelerometer-dlw-tee-agreement@1",
        "energy-deficit-rt-lean-mass@1",
        "lea-combined-myofibrillar-synthesis@1",
        "athlete-slower-loss-lean-mass@1"
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 007)",
      "status": "pending",
      "approval": null,
      "key": "energy-identifiability-first-model-comparison@1",
      "question": "energy-operational-maintenance-methodology",
      "description": "Compare simple baselines with longitudinal and anchored richer models using explicit identification and prospective validation.",
      "provenance": "Original Fitness Intelligence candidate programming methodology, Packet 007 §§3–4; independent review required.",
      "tradeoffs": "Additional complexity may not improve decision outcomes; unanchored physiological claims deferred.",
      "claims": [
        "calerie-weight-model-intake-change-agreement@1",
        "ten-haaf-athlete-rmr-group-agreement@1",
        "runner-accelerometer-dlw-tee-agreement@1"
      ]
    }
  ],
  "withdrawals": []
}
```

## 6. Synthetic evaluation cases

These are invented conformance fixtures, not validated clinical or physiological thresholds. Each row specifies eligible inputs/coverage, acceptable interpretation/action, prohibited inference, uncertainty disclosure, relevant policy, and recalibration/target status. Unless otherwise indicated, observation review is read-only; a proposed nutrition-target or training change requires explicit athlete approval through the existing review boundary, preserves original prescription and rationale, and is revalidated against new restrictions. A qualitative suggestion may be communicated without automatically changing a plan. Referral boundaries in EE-P09 apply in every case independently of data coverage. In tests use a synthetic catalog and approved fixture parameters only; pending real evidence cannot authorize new operational recommendations.

| ID / fixture and eligible observations | Acceptable interpretation and action | Prohibited inference / required disclosure | Policy; recalibration and adjustment |
|---|---|---|---|
| EE01 Stable comparable weight, representative complete-intent logs, unchanged training | Calculate conditional M_L, hold productive target | No physiological TEE or EA claim; disclose regime and uncertainty | P01/04/07; operational recalibration supported, target hold |
| EE02 Same observations in two offset worlds B1/B2 | Same operational result, distinct unknown physiological values | No choice between worlds without independent anchor | P04/05; conditional M_L only, hold |
| EE03 Sustained rising comparable mass, stable logs, unknown tissue | Review goal and actual adherence; if appropriate propose contextual adjustment or investigate | Cannot label tissue gain as fat or compute exact surplus | P03/07; conditional scenario, approval for adjustment |
| EE04 Unintended loss despite seemingly adequate reported intake | Ask about actual intake, workload and symptoms; protect fueling and refer if concerning | Adequate-looking calories not physiological adequacy; no automatic diagnosis | P07/09; defer absolute estimate; possible supportive proposal |
| EE05 Entire weekend calorie days missing | Report coverage; ask completeness if useful, maintain safe target | Missing not zero; weekday mean not full-week estimate | P01/08; no recalibration, hold or qualitative |
| EE06 Some meals logged, day explicitly partial | Preserve partial observation, no complete-intake denominator | Presence of kcal not evidence of complete log | P01/08; defer recalibration |
| EE07 Explicit zero vs absent day, same other data | Distinguish recorded zero, verify context and safety; absent remains unknown | No zero imputation or assumption explicit zero is accurate/safe | P01/09; exclude ambiguous from calibration; assessment if concern |
| EE08 Intake present, no mass observations | Qualitative fueling or A reference; no response-based maintenance estimate | Intake average not TEE; weight response unknown | P02/04; defer B, no automatic change |
| EE09 Several same-day weights under same standardized protocol | Predeclared aggregate/selection and preserve raw data | No cherry-pick low weight or treat repeats as separate days | P03; conditional recalibration only with other evidence |
| EE10 Morning weights replaced with evening weights | Separate comparison protocol, ask or rebaseline | No tissue trend across time-of-day change | P03/08; suspend slope-based change |
| EE11 New scale gives offset, overlap unavailable | Mark discontinuity; old reference historical; request overlap if useful | No immediate tissue interpretation or offset estimate | P03/08; defer recalibration, hold |
| EE12 Carb loading before race, abrupt mass rise | Retain event fueling, flag possible transient shift | No fat gain or exact glycogen inference; disclose uncertainty | P03/06/07; no automatic reduction |
| EE13 Long race or depletion, abrupt mass decrease | Consider hydration/substrate and recovery; context and follow-up | No measured fat loss or exact deficit | P03/09; defer quantitative trend |
| EE14 New creatine and abrupt mass rise | Record event, compare later standardized measurements | Cannot infer all gain is muscle or water | P03/08; defer adjustment |
| EE15 Travel, different weighing and logging pattern | Preserve historical reference as stale, focus feasible fueling | No transfer of old M_L as exact new maintenance | P08; defer recalibration |
| EE16 Changed sodium/hydration with isolated mass shift | Contextual clarification; hold if safe | No deterministic water correction | P03; no adjustment |
| EE17 Restaurant logging increases and calorie estimates change | New regime or uncertain comparability; audit voluntarily | No inferred change in expenditure from reported shift | P08; suspend numeric recalibration |
| EE18 Running duration increases, device kcal rises, weight noisy | Protect priority-session fueling; compare new regime when observations informative | No exact eat-back or inferred compensation | P06/07; context guidance now; numeric conditional |
| EE19 Strength sets increase, no measured EE | Review burden and food access; use separate covariates if validated | No universal kcal per set/repetition/tonnage | P06; qualitative, no automatic target change |
| EE20 More intermittent sport, comparable HR to run | Record modality and demand separately, review fueling | No identical running stimulus or energy cost | P06; conditional context, not conversion |
| EE21 Device consistently reports higher totals than logged intake | Display both types and their uncertainty; assess trend and logging | Disagreement not proof device or log bias magnitude | P02/05; operational reference possible, absolute deferred |
| EE22 Device/algorithm changed; apparent EE jump | Split measurement regime, verify semantics/overlap | No actual physiological jump or generic correction | P01/08; suspend EE calibration, B may remain useful |
| EE23 Total 2800 includes active 800; recorded exercise 500 overlaps | Use total once if verified; quarantine ambiguous decomposition | No sum 2800+800+500, no double count | P01/06; descriptive total only, no auto eat-back |
| EE24 Stable weight, declining squat/run performance | Investigate load, sleep, fueling, adherence, illness; protect/referral as warranted | Stable mass not adequate EA or successful block | P07/09; no restrictive adjustment, context proposal |
| EE25 Short noisy weight stagnation | Hold, compare practical trend and uncertainty | No mandatory calorie reduction for short plateau | P03/07; defer change |
| EE26 Intentional loss, worsening fatigue/recovery | Discuss pause in deficit/goal revision, improve fueling, workload review; refer if persistent or concerning | No REDs diagnosis or intensifying restriction due to goal | P09; quantitative optimization deferred; approved change only |
| EE27 Desired gain and mass increase, composition unknown | Evaluate acceptable trajectory and performance; consider hold | No assertion of hypertrophy or fixed tissue density | P07; conditional operational recalibration |
| EE28 Stable mass despite possible recomposition | Recognize storage energy may differ; monitor outcomes and context | Stable mass not zero energy balance or absolute TEE | P04/05; M_L only, physiological deferred |
| EE29 No macros, planned long run and lift | Give context-specific qualitative fueling and reviewed reference recommendations if inputs sufficient | No macro adherence/glycogen inference or requirement for meal tracking | P02/06; no calorie recalibration needed |
| EE30 Sparse nonrepresentative logs and mass | A or carry safe target; ask only decision-relevant questions | No precise M_L or full-week mean | P01/04; defer recalibration |
| EE31 L and V agree exactly; both potentially biased | Demonstrate offset symmetry; conditional operational target only | Agreement not truth; independent anchors required | P05; physiological deferred |
| EE32 C model narrow posterior despite unconstrained biases | Flag prior dependence/structural nonidentifiability, report scenarios or abstain | No narrow data-derived CI or accurate TDEE claim | P05/10; fail model eligibility |
| EE33 C retrospective fit excellent, forward forecast worse than B | Retain simpler candidate, disclose leakage/misspecification risks | No promotion from in-sample fit | P10; no new estimator authorization |
| EE34 Same canonical observations from two providers | Identical decision if provenance/quality equivalent | No provider-specific scientific threshold | P01/10; same eligibility/action |
| EE35 Evidence pending or scope mismatch | Explicit gap; only separately reviewed practical guidance if authorized | No empirical entitlement or fake citation | P10; no unreviewed numerical change |
| EE36 Actual intake differs from approved target, mass trend unexpected | Address feasible adherence and completeness before changing target | Cannot infer target failure from unexecuted prescription | P07; conditional, usually hold pending clarification |
| EE37 Concerning symptoms despite no intake or weight history | Pause restrictive optimization, recommend qualified assessment; urgent care if severe | No diagnosis or demand to log first | P09; no recalibration; safety priority |
| EE38 Athlete declines target proposal or new restriction arrives | Preserve old approval/history; revalidate or withdraw stale proposal | No automatic change, no hidden rewrite | P07/09; decline holds prior state with safety conflict visible |
| EE39 Future weight enters retrospective smoother | Past decision replay excludes future observation; research retrospective view labeled | No leakage into prospective validation or retroactive change | P03/10; invalid forecast if leakage |
| EE40 Independent matched DLW window available | Anchor average physiological estimate with reference uncertainty; separate operational target and daily latent quantities | No daily TEE truth or bias stability outside reference window | P05; conditional calibration, no automatic target adjustment |

Conformance checks: deterministic replay of eligible sets, target status and explanation; unit/time alignment; no unapproved writes; explicit gaps; invariant output under unidentifiable offset worlds for operational recommendations; no prohibited medical inference; paired cases with optional inputs removed and equivalent canonical inputs. Validate against predefined acceptable alternatives, not one exact calorie number. Prospective efficacy requires independent outcome evaluation (§4.8), not passing fixtures.

## 7. Research backlog

### 7.1 Reconcile identifiers and unresolved research

Historical identifiers are preserved. Packet 004 NU-04 means dietary fat/macro allocation, NU-05 nutritional periodization, NU-06 nutrition-aware adaptation and observation quality; NU-06a data integrity/provenance and NU-06b policy efficacy remain distinct. NU-07 is the earlier expenditure/estimation dependency; P007/EE-01–13 elaborates it without renumbering. Earlier roadmaps used NU-04/05 in different nutrition sequencing contexts; use packet-qualified references rather than silently replacing their meaning. Packet 006 HP-08 integrates fueling with training feasibility and HP-P09 block review; Packet 008 RE-P10/11 adds conflict and recovery review. None is superseded by the estimator. Original scientific review and policy approval obligations from 001–006/008 remain open.

| Priority / question | Outstanding work | Decision consequence |
|---|---|---|
| P0 EE-05/06, NU-06a | Verify historical calorie/weight completeness, provenance, timestamp alignment, duplicate handling, protocol and missingness. Examine athlete-level coverage and selective omissions. | Without representative observations no B recalibration; qualitative guidance remains possible. |
| P0 EE-08/09 | Review structural proof, operational target definition, assumptions and action-specific uncertainty; distinguish stable mass and stored energy. | Do not mislabel logged maintenance or model output as true TDEE. |
| P0 EE-12 | Review weight-goal feasibility, clinical boundaries and joint performance constraints; approve contextual target-change methodology separately. | Initial coach may provide general fueling without automated energy adjustment. |
| P0 EE-03 | Appraise athlete RMR equations, local/external validation, appropriate covariates and PAL assumptions. | Only conditional initial reference; carry tolerated target if relevant. |
| P1 EE-06 | Investigate within-athlete repeatability, weight measurement protocol, carbohydrate/sodium/creatine, menstrual and travel-associated changes; assess practical sensitivity of alternative robust trends. | Improves eligibility, reduces spurious changes; no universal window. |
| P1 EE-02/04 | Repeated matched DLW/chamber studies and current device algorithms; distinguish change agreement and average accuracy. | Wearable estimates optional; no absolute calibration without reference. |
| P1 EE-07/10 | Extract Hall/Chow original equations and CALERIE Table 1/supplements; compare dynamic approximations and model misspecification for trained athletes. | No physiological daily estimates until anchors and validation. |
| P1 EE-11 | Assess activity covariates, net/gross definitions, spontaneous activity and appetite; test incremental value vs B. | Session fueling can use purpose/duration without kcal conversion. |
| P1 EE-13, NU-06b | Prospective temporal prediction, decision-value and policy comparison (Packet 009). | No claim that estimator improves performance or adherence. |
| P2 EE-01 | Repeated component-level measurements and adaptation under changing hybrid load. | Deferred decomposition; not required for practical coach. |
| P2 NU-04/05 | Complete pending macro adequacy and periodization review from Packet 004; no duplicate literature expansion here. | Preserve existing provisional recommendations and safety constraints. |

### 7.2 J3 curation extension (decision-oriented; additions to Packet 006/008 shortlist)

All candidate methods and empirical records pending. IDs below are exact staged keys where available; reference earlier packets for their full source/claim extraction. “Feasible” means data capability, not scientific approval.

| Priority / actual decision | Evidence identifiers and verification | Transfer, numerical guidance and separate method review | Data feasibility and consequence of deferral |
|---|---|---|---|
| Essential: safety and agreed weight/performance objectives (EE-P09) | Packet 004 `oxfeldt-lea@1` / `lea-combined-myofibrillar-synthesis@1`; `caldwell-lea@1` / `lea-endurance-time-trial-power@1`; IOC consensus and clinical referral checklist; Packet 008 RE-P10/11 | verify versions/correction, endpoint and population transfer; no diagnostic thresholds; approve protect/refer method separately | Feasible qualitative from goals and voluntary feedback. Deferral of safety review blocks restrictive advice, not ordinary safe training guidance. |
| Essential: useful fueling without full tracking (EE-P06, NU-P02/03/04/05) | Packet 004 `king-acute-carbohydrate@1` / `acute-cho-resistance-volume@1`; `craven-glycogen@1` / `cho-short-term-glycogen-resynthesis@1`; `morton-protein@1` / `rt-protein-supplement-ffm@1`; prior consensus | verify exact ranges, session/population transfer and clinical exclusions; separate consensus numerical guidance from empirical claims; review meal/day method | Feasible contextual guidance from planned workload, goal, preferences; quantitative conditional. Macros not prerequisite to recommend; absent logs limit verification. |
| Essential: interpret nutrition observations correctly (EE-P01/08) | `capling-diet-validity@1` / `athlete-logged-intake-dlw-disagreement@1`; `fuller-wearable-validity@1` / `wearable-energy-expenditure-validity@1`; new `morning-mass-variability-active-men@1`; `energy-regime-eligible-observation-review@1` | verify actual energy balance and study-specific error; no universal correction or minimum count; review coverage/provenance method | Conditional on verified histories; defer numerical calibration if incomplete. Missing intake never zero; no broad tracking dependency. |
| Early extension: initial conditional reference (EE-P02) | `oneill-athlete-rmr@1` / `ten-haaf-athlete-rmr-group-agreement@1`, `ten-haaf-athlete-rmr-within-bound@1`; E06 | review formula versions, age/sex/FFM, calibration and PAL; contextual parameters separate | Conditional on suitable inputs; carry existing tolerated target or qualitative if deferred. |
| Early extension: operational maintenance and conservative adjustment (EE-P03/04/07) | `heymsfield-controlled-maintenance@1` / `controlled-maintenance-intake-dlw-ratio@1`; `sanghvi-intake-change-validation@1` / `calerie-weight-model-intake-change-agreement@1`; `energy-logging-adjusted-maintenance-review@1` | verify Table 1, individual agreement, study transfer, offset assumptions; approve trend/coverage criteria and target bounds separately | Conditional on representative logs and comparable weights. Deferral retains safe target and general fueling; no actual TDEE inference. |
| Early extension: body composition tradeoffs (EE-P07/09) | `garthe-athlete-loss-rate@1` / `athlete-slower-loss-lean-mass@1`; `murphy-koehler-energy@1` / `energy-deficit-rt-lean-mass@1` and `energy-deficit-rt-strength@1`; `helms-energy-surplus@1` / `surplus-body-mass-skinfold@1` | verify actual rates, intervention duration, DXA and training exposure; no universal rate; separate nutrition method review | Conditional; qualitative protection feasible without logs. Deferral means no automated weight-target changes. |
| Early extension: workload-aware target/fueling changes (EE-P06) | `ma-runner-dlw@1` / `runner-accelerometer-dlw-tee-agreement@1`; E15–19; `energy-activity-aware-target-review@1`; Packet 003/005/006 | verify DLW window/device algorithm, compensation design and modality transfer; no universal kcal coefficient or eat-back | Feasible qualitative, conditional numerical. No need for per-second telemetry to protect demanding sessions. |
| Deferred: absolute and daily TDEE, component/latent estimation (EE-P05/10) | `calerie-weight-model-intake-change-agreement@1`, `runner-accelerometer-dlw-tee-agreement@1`; `energy-identifiability-first-model-comparison@1`; §4.2 mathematical proof (not empirical) | verify independent reference and prior dependence; no fixed tissue coefficient, validate C against A/B before any adoption | Deferred absolute without anchor; conditional C1 research. No loss of essential coaching functionality by deferring. |
| Deferred: causal incremental coaching value (EE-P10 / Packet 009) | Packet 007 §4.8; prior P006/008 evaluation shortlist | prospective comparative design and explicit endpoints; no claim of benefit from software conformance | Conditional research after approval; do not block initial reviewed practical methodology on all open questions. |

### 7.3 Engineering implications (mutable snapshot, not scientific claim definitions)

Garmin-first nutrition is the current project direction supplied for this packet. Sampled daily intake and timestamped weight exist, historical continuity and original source attribution remain unverified. Strength history and recorded activity may support workload context. Current capabilities are not inferred from brand marketing or a single sample; source verification needed in engineering. No assumption of macros, meals, measured RMR, FFM, DLW, high-resolution HR or independent expenditure. No API field name belongs in an empirical scope. Future Health Connect or other integrations are optional, not requirements for basic recommendations.

Prioritize read-only historical coverage and semantic verification before fitting any model: day boundary/time zone, final vs partial daily total, record provenance/duplicates, scale timestamps/units, exact active/basal/total/exercise overlap and estimate method, nonwear, corrections/deletions, actual activity and approved target history. A canonical observation should distinguish reported, complete-intent, partial, explicit zero, unknown, missing and estimated, with version, source and quality. Voluntary targeted completeness/protocol feedback is more useful than requiring comprehensive questionnaires. Preserve original provider records and owner-scoped privacy; avoid over-collection. Estimate records (future design, not schema change here) should include estimand, units, window and as-of instant, input eligibility/coverage, assumptions, model and parameter version, uncertainty type, known regime and stale reason, alternative estimates, decision and approval provenance. Do not store personal observations in shared evidence corpus.

Recommended engineering order, subject to separate authorization: (1) verified canonical calorie/weight/expenditure semantics and coverage; (2) contextual A/carry reference and read-only comparable weight/intake report; (3) reviewed B in shadow mode with missingness and regime tests; (4) bounded proposed target review after policy approval and prospective evaluation; (5) activity covariates only if demonstrable incremental value; (6) anchored C2 only for an explicit physiological estimand and reference substudy. Do not implement TDEE estimator or modify planner here. No daily caloric tracking, macro ingestion, meal-level integration or health connector prerequisite for ordinary nutrition advice.

### 7.4 Roadmap

| Packet | Status / scope |
|---|---|
| 001–006 | Preserved; all independent review requirements remain |
| 008 | Completed intentionally before 007; integrated recovery and autoregulation preserved |
| 007 | Draft complete for staging and independent review; estimator designs research-only |
| 009 | Next — Individual adaptation and prospective evaluation; formal model and policy comparisons, causal limits, baseline and calibration |
| 010 | Later — Longer-term planning, interruptions and adherence; include nutrition regime changes and tracking burden |
| J3 | Focused cross-packet scientific curation may proceed independently, with explicit approval and release process |

## 8. Human review checklist

### Scientific appraisal

- [ ] Confirm E01 isotope review study counts and TEE range are descriptive, not population requirements; verify reference-method uncertainty and exercise-specific limitations (E02–04).
- [ ] Verify Heymsfield controlled protocol, paired data, ratio and Fig. 3; do not interpret p=.96 as equivalence or transfer to consumer logs.
- [ ] Verify O'Neill equation-specific direction, subsets, Table 3 precision denominators, derivation overlap, heterogeneity and calorimetry methods; review original equation versions and coefficient units before operational use. Independent external validation and PAL uncertainty remain open.
- [ ] Verify Shcherbina error definition and activity/device strata, Murakami residual PAEE reference and multiple comparisons, and Ma 2026 seven-day period, waist device, BMR/DIT assumptions and reported LoA. Do not convert individual disagreement or group bias to a universal correction factor. Confirm independent longitudinal responsiveness before use for changes.
- [ ] Recheck Packet 004 Capling/Fuller claims and denominators, distinction between intake vs expenditure discrepancy and true reporting error, missingness and device-version transfer.
- [ ] Obtain full Cheuvront and Olsson/Saltin reports; verify dispersion and protocol; investigate further body-weight variability (sex/cycle, creatine, sodium, travel, inflammation) without universal water corrections or threshold. Assess measurement reliability separately from tissue validity.
- [ ] Obtain complete Hall/Chow and Sanghvi model equations, Table 1 and supplements; verify group vs individual LoA, interval definitions, baseline reference, selected sample and external validity; do not infer absolute intake or TDEE from ΔEI alone.
- [ ] Review dynamic model tissue partition and transfer to recomposition, effects of changing activity/intake; confirm no exact static kcal/kg rule. Verify E15 Careau cross-sectional decomposition/coupling and E16 trial outcomes; distinguish appetite from expenditure compensation.
- [ ] Check Minetti gross/net definitions, slopes and units; Mitchell anaerobic contribution and method limitations; no per-set or universal run kcal coefficient.
- [ ] Obtain full Garthe RCT and follow-up, verify allocation, attrition, achieved rates, actual training, duration and DXA hydration, dispersion; check overlap and independent applicability. Reappraise prior surplus/deficit/LEA records and IOC correction/clinical boundaries; no universal weight-loss/gain rates or diagnostic cutoffs.
- [ ] Check publication versions, DOI, dates, corrections/retractions, rights and exact locators for each new source/claim. Source access fields conservatively marked abstract where only indexed passages inspected; do not upgrade without complete verification. Review issue-date conventions and proposed next-review dates.

### Statistical and coaching-method review

- [ ] Independently verify offset invariance and tissue ambiguity, sign conventions, units, conditional identified set, additive vs multiplicative reporting assumptions and limits of prior-based inference. Distinguish likelihood identification from prior regularization; decide which estimands are operationally useful.
- [ ] Review Model A baseline choice, Model B eligibility and trajectory uncertainty, conditional M_L definition and expiration, proposed scenario arithmetic and hold/adjust alternatives. Model B recommended for research, not implementation authorization.
- [ ] Review Model C state definitions, covariate rank, bias drift, missingness model, anchors, error correlation, tissue approximation and prospective calibration. Reject unanchored absolute physiological estimates and false precision.
- [ ] Set contextual reviewed parameter values only when justified: practical goal trajectory and stability, weigh-in protocol, sufficient coverage, review horizon, target adjustment bounds and safeguards. Document source/assumption, athlete agreement and uncertainty. No automatic 3,500 kcal/lb conversion, compensation multiplier, wearable correction, fixed adjustment increment or mandatory minimum log count.
- [ ] Review EE-P01–10 independently of supporting empirical claims; ensure distinct prescription/adherence/effectiveness/calibration requirements, scientific and data readiness, fallback/referral and approval boundaries. Preserve NU/HP/RE dependencies. No unnecessary tracking requirement.
- [ ] Check the six synthetic examples' arithmetic and distinct ground truth vs observable values; fixtures are not training or diet prescriptions. Test all 40 cases with acceptable alternatives and prohibited inferences.
- [ ] Pre-register temporal prediction estimands, baselines, reference comparison, calibration/abstention, missingness sensitivity, independent holdouts, uncertainty and policy efficacy outcomes. No future-data leakage or efficacy claim from synthetic tests. Advance prospective design in Packet 009.

### Integration and operational boundaries

- [ ] Verify current provider semantics and historical coverage in mutable engineering inventory; do not assume API field equivalence or calorie completeness. Keep provider-independent evidence and policy definitions.
- [ ] Validate J1 fragment against current registered manifest plus all archived drafts using actual strict loader/graph validation, exact revisions, pending status and query gaps; verify source reuse and no identifier collisions. The author checked local JSON and references, not a repository runtime release. New representation needs (measurement agreement, model-validation estimands, consensus numerical guidance, assumptions and identifiability) remain future design discussion.
- [ ] Preserve prior packets and drafts unchanged; carry forward all independent review obligations. No application, planner, repository, registered release or approval changes. No calorie target or estimator deployment until separately reviewed and authorized. Stage this as research input only.
