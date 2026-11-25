# Fitness Intelligence — Research Packet 003

**Concurrent strength and running programming for experienced recreational hybrid athletes**  
Date: 2026-11-24 | Revision: 0.1 | Status: **Draft — pending independent human review**  
Repository: [dkiv/fitness-intelligence](https://github.com/dkiv/fitness-intelligence)  
Research questions: CT-01 (bidirectional adaptations), CT-02 (scheduling and sequence), CT-03 (dose and modality), HP-01 (hybrid block coordination).  
Predecessors: `fitness-intelligence-research-001.md` and `fitness-intelligence-research-002.md` (preserved unchanged). This packet updates research priorities, not approved software behavior.

## 1. Executive summary

### 1.1 Research direction

Fitness Intelligence should treat strength, endurance, nutrition, body composition, recovery and adherence as interacting objectives over time. Maximizing a lift in isolation is not the product's default goal. A good plan can accept a smaller gain in one objective in exchange for progress in another, provided that tradeoff is explicit, feasible and acceptable to the athlete. A comparison with resistance-only training estimates an opportunity cost for strength; it does not determine whether concurrent training is a bad choice for a hybrid athlete.

**Target population:** adult recreational athletes with meaningful prior experience in both resistance training and running, not simply runners new to lifting or lifters new to aerobic exercise. Studies in either of those groups are useful but require transfer arguments. The initial planning horizon is a multiweek block with rolling weekly review; this is a product scope, not a scientifically optimized block duration.

### 1.2 Findings and implications

- Concurrent training can improve strength and endurance together. Pooled maximal-strength and whole-muscle hypertrophy differences compared with matched resistance-only programs are small on average, but they are not proof of equivalence in experienced hybrid athletes. Lower-body maximal strength and explosive strength are outcomes worth protecting explicitly; the evidence does not justify treating all strength work as equally vulnerable.
- A trained lower-body subgroup showed attenuated gains with added endurance training (Petré 2021); a newer synthesis did not detect a training-status interaction for strength (Huiberts 2024). Preserve both results. A 2025 running-specific trial in trained men also reported differing squat adaptation trajectories over successive phases. This does not establish a deterministic interference penalty.
- Whole-muscle and muscle-fiber size are not interchangeable outcomes. The small pooled fiber-level attenuation and running subgroup signal in Lundberg 2022 deserve scrutiny, not a blanket prohibition on running for hypertrophy.
- Intra-session resistance-first sequencing has some support for lower-body dynamic strength. Different-session comparisons and an experimental spacing study make separation of demanding overlapping sessions a reasonable option. Acute running studies illustrate the reverse cost: preceding lifting can compromise a later run. None establishes a universal spacing interval or an optimal weekly calendar.
- Heavy resistance training can improve measured running economy and time-trial/time-to-exhaustion performance in distance runners. Combined strength methods can also help, but a larger pooled estimate against control is not a head-to-head demonstration of superiority. Benefits need not depend on detectable improvements in VO2max. Much of this evidence concerns runners with less lifting experience than our target athlete.
- No retrieved trial validates an integrated weekly feedback policy choosing how much strength or running work to add, hold, move or remove. No direct evidence establishes that a strength-emphasis, endurance-emphasis or balanced block is universally superior in dual-trained recreational athletes. Treat scheduling, preservation of secondary qualities and priority changes as candidate methodologies.
- Nutrition is a relevant contextual constraint and competing explanation for poor performance. Do not infer adequate energy availability from stable weight or wearable expenditure, diagnose underfueling from one poor workout, or prescribe a universal double-session fueling algorithm. Packet 004 will address nutrition directly.

**Decision recommendation:** maintain a feasible productive joint dose, protect outcome-specific key sessions, consider schedule changes before abandoning important stimuli, and review changes against both disciplines and nutritional/recovery constraints. This is conservative programming judgment informed by evidence, not a trial-validated optimization policy. RT-P02 revision 0.2 (Packet 002) remains relevant, but its volume decisions must now account for running exposure and objectives.

### 1.3 Scope and literature search

PICO A: experienced adult lifters/runners; matched resistance training with vs without running or other endurance; maximal strength, muscle size, explosive strength; longitudinal interventions. PICO B: distance runners; additional resistance/plyometric work vs running alone or low-load control; measured running economy, running performance, aerobic capacity. PICO C: concurrent participants; different sequence, spacing, endurance dose or strength dose; adaptations, acute session quality and tolerability. Acute outcomes are not pooled with longitudinal changes.

Targeted search on 2026-11-24: PubMed-indexed records, Springer journal HTML, publisher pages and PMC search extracts. Query families: `concurrent training trained lower body upper body strength hypertrophy running cycling`; `concurrent training exercise sequence recovery duration running`; `strength training running economy distance runners meta analysis`; `concurrent training trained individuals running 2025 2026`; `running durability strength training randomized`; `concurrent training endurance intensity network meta analysis`; `maintaining strength endurance minimal dose`. Prioritize controlled studies and systematic reviews with identifiable comparators. Recent 2026 leads were included where relevant. Searches are purposive, not a PRISMA-complete systematic review; no duplicate screening, complete exclusion log, formal new risk-of-bias assessment, raw-data reanalysis or exhaustive registry/correction/rights audit. Full publisher HTML result sections were inspected for the central Schumann, Petré, Huiberts, Lundberg and Llanos-Lagos reviews; Eddens result text and Spiering publisher review were available. Several primary trials were accessible only at abstract level. PMC browser challenges limited some direct retrieval; no claim is made to have read inaccessible supplements or full primary reports. Study dates, DOI and links below permit reproduction of the targeted appraisal. Exact primary result tables/figures are deliberately not guessed.

**Evidence types:** D = intervention directly combines training modalities and measures the stated outcome; D* = direct concurrent evidence but not direct to the dual-experienced target population or running-specific exposure; I = indirect evidence from other sports, single-discipline or observational evidence; M = programming method; O = athlete observation; S = engineering/safety safeguard. Directness is outcome- and comparator-specific, not a global label for a paper. Confidence ratings are provisional judgments for the described contrast, with separate transfer limitations, not independent GRADE ratings. All empirical claims in this packet remain pending independent review; screening rows are not proposed for operational eligibility.

## 2. Scientific evidence table

Negative standardized effects in the strength comparisons favor resistance-only training; negative running-economy/performance effects favor the supplemental strength intervention in the relevant reviews. CI = confidence interval; CrI = credible interval; 1RM = one-repetition maximum; RE = running economy (oxygen or metabolic cost at a specified speed); TTE = time to exhaustion; RT = resistance training; ET = endurance training; CT = concurrent training. Study frequencies, intensities and timings are **study descriptors only**, never policy defaults.

### 2.1 Endurance → strength, hypertrophy and power

| ID / empirical finding | Publication and DOI | Exact result locator / access | Population; intervention vs comparator; duration | Effect / uncertainty | Limitations and applicability | Confidence / disposition |
|---|---|---|---|---|---|---|
| C01 — Average maximal-strength gains were close between CT and RT-only. | Schumann et al. 2022, *Sports Med* 52:601–612. [10.1007/s40279-021-01587-7](https://doi.org/10.1007/s40279-021-01587-7) | §3.2, Fig. 2; publisher full text; existing `pooled-concurrent-strength@1`. | Healthy adults, mixed experience; supervised aerobic plus matched RT vs identical RT only; ≥4 weeks; 37 studies in this outcome. | SMD −0.06 (95% CI −0.20 to 0.09), I²=0%. | D*; broad training experience, mixed modes; moderate to high methodological limitations (mean PEDro 4.3/10); no equivalence test, high-volume running or press-specific inference. | Moderate for pooled contrast, low for dual-trained individual; existing pending. |
| C02 — Explosive-strength gains were smaller with CT. | Schumann 2022, same DOI. | §3.3, Fig. 3. | Same inclusion; 18 studies, 270 CT and 208 RT participants. | SMD −0.28 (−0.48 to −0.08); I²=35.81%. | D*; outcome distinct from maximal strength, influential study; subgroup findings sensitive to its exclusion. | Moderate for average outcome, low for exact running-specific effect; pending draft. |
| C03 — Whole-muscle hypertrophy showed a near-zero pooled difference. | Schumann 2022, same DOI. | §3.4, Fig. 4. | 15 studies, 201 CT and 188 RT participants; same eligibility. | SMD −0.01 (−0.16 to 0.18), I²=0%. | D*; no proof of equivalence or of preservation at large endurance doses; muscle-specific effects may differ. | Moderate pooled, low for highly experienced runners; pending draft. |
| C04 — Lower-body strength gains were smaller in the trained subgroup. | Petré et al. 2021, *Sports Med* 51:991–1010. [10.1007/s40279-021-01426-9](https://doi.org/10.1007/s40279-021-01426-9) | §3.4, Fig. 2; full text; existing `trained-lower-body-strength@1`. | Adults 18–40; structured training or athlete classification; running/cycling >70% HRmax ≥2 days/week plus RT vs matched RT only; 6–21 weeks overall. | Trained ES −0.35 (−0.59 to −0.11); moderately trained −0.20 (p=.08); untrained 0.03 (p=.87). | D*; subgroup classification across studies, some nonrandomized and small trials. Different significance levels do not themselves establish effect modification. Cannot infer effect of an easy run on bench press. | Low for trained hybrid transfer; existing pending. |
| C05 — Sex subgroup contrast in lower-body strength differed. | Huiberts, Wüst & van der Zwaard 2024, *Sports Med* 54:485–503. [10.1007/s40279-023-01943-9](https://doi.org/10.1007/s40279-023-01943-9) | §3.4, Figs. 3–4, full text. | Healthy adults 18–50, ≥4 weeks; 20 lower-body-strength studies (269 CT/208 ST). | Men SMD −0.43 (−0.64 to −0.22); women 0.08 (−0.34 to 0.49); between-group p=.03. | D*; wide female CI, unclear concealment/detection bias, study-level subgroups. No sex-based automatic prescription or inference that women are immune. | Low for differential individual policy; pending draft. |
| C06 — Training-status moderation of strength was not detected in a newer synthesis. | Huiberts 2024, same DOI. | §3.5, Fig. 5. | 59 studies/1346 participants overall; separately categorized strength and endurance training experience. | Strength-experience interaction p=1.00 lower body (16 studies), p=.45 upper body (14); endurance-experience interaction p=.55 lower body, p=.50 upper body. | D*; sparse highly trained participants and imperfect classifications; no equivalence, does not refute C04 by itself. No evidence that upper-body response is completely independent of running. | Low for moderation; pending draft. |
| C07 — Fiber-level hypertrophy may be slightly attenuated, especially type I fibers in a small running subgroup. | Lundberg et al. 2022, *Sports Med* 52:2391–2403. [10.1007/s40279-022-01688-x](https://doi.org/10.1007/s40279-022-01688-x) | §§3.2–3.4, Figs. 2, 4; abstract Results for running estimate; full text. | 15 studies, 300 adults; 12 cycling and 3 running studies; supervised CT vs matched RT, ≥4 weeks. | Overall fiber SMD −0.23 (−0.46 to −0.00; p=.050), I²=58.6%; type I −0.34 (−0.72 to .04), type II −0.13 (−0.39 to .12); running type I −0.81 (−1.26 to −0.36). | D*; mean PEDro 4.3; biopsy sampling, heterogeneity and few running studies; §3.3 reports no statistically significant subgroup differences. Do not equate fiber and whole-muscle size or infer a running/cycling interaction from within-subgroup CIs. | Low, especially modality transfer; pending draft. |
| C08 — A recent running-specific trial reports different phase-wise squat adaptations with concurrent training. | Gomes et al. 2025, *J Sports Sci* 43:1762–1782. [10.1080/02640414.2025.2518827](https://doi.org/10.1080/02640414.2025.2518827) | Abstract, Results; publisher abstract and PubMed; full contrast extraction outstanding. | 30 trained men randomized CT, RT, ET; 3 sessions/week for 11 weeks; maximal-strength then explosive-strength phase; CT appended 30-min moderate-to-heavy running. | Squat 1RM increased similarly in first phase according to authors, then only RT increased in second. Absolute changes and direct between-group CIs not extracted. | D, running-specific; dual training history and realized doses need verification; significance in one arm alone does not establish interaction; small male sample. | Low; screening only pending full tables and direct contrasts. |
| C09 — Older modality and dose associations suggest higher endurance exposure may relate to smaller strength adaptations. | Wilson et al. 2012, *J Strength Cond Res* 26:2293–2307. [10.1519/JSC.0b013e31823a3e2d](https://doi.org/10.1519/JSC.0b013e31823a3e2d) | Abstract, Results; full extraction outstanding. | 21 studies, 422 effect sizes; diverse CT protocols. | Reported correlations with endurance frequency −0.26 to −0.35 and duration −0.29 to −0.75 across hypertrophy/strength/power outcomes. | I for causal dose selection: cross-study associations, shared effects, confounding; older analysis differs from Schumann's matched-program comparisons and newer moderator findings. | Low; screening. |
| C10 — Network estimates differ by endurance type, with uncertain intervals. | Chen et al. 2024, *J Exerc Sci Fit* 22:86–96. [10.1016/j.jesf.2023.12.005](https://doi.org/10.1016/j.jesf.2023.12.005) | Abstract, Results; network tables not fully appraised. | 40 studies, 841 participants; interval/continuous running or cycling with RT vs RT alone. | Interval-running MCSA SMD 0.15 (−0.46 to .76); continuous moderate cycling 0.07 (−0.24 to .38); reported interval-training strength estimate −0.08 (−0.25 to .08), exact node verify. | D*; indirect network contrasts, transitivity/dose imbalance and training status need appraisal; cannot choose HIIT over easy/long runs on ranking alone. | Low; screening. |

**Interpretation:** C01 and C04 have a different population and outcome scope and overlapping trials. C06 adds a genuine uncertainty about training-status moderation rather than resolving it. C07 is not a conflicting measure of the same tissue-level outcome as C03. C08 gives a specific longitudinal protocol worth examining; it does not identify whether running dose, spacing, phase content or other factors drove differences. There is no defensible universal conversion from minutes of running to lost kilograms of strength gain or lost hypertrophy.

### 2.2 Strength → running performance and economy

| ID / empirical finding | Publication and DOI | Exact result locator / access | Population; intervention vs comparator; duration | Effect / uncertainty | Limitations and applicability | Confidence / disposition |
|---|---|---|---|---|---|---|
| C11 — High-load supplemental strength work improved measured RE on average. | Llanos-Lagos et al. 2024a, *Sports Med* 54:895–932. [10.1007/s40279-023-01978-y](https://doi.org/10.1007/s40279-023-01978-y) | §3.4, Fig. 2; publisher full text; §4 high-load discussion. | Middle/long-distance runners, moderately to highly trained as runners; high-load training (review category ≥80% 1RM or ≤7RM) vs control; relevant high-load interventions 6–14 weeks; 2–4 sessions/week. | ES −0.266 (95% CI −0.516 to −0.015), p=.039; measured at 8.64–17.85 km/h. | D*; multiple speeds per study, small estimates, diverse controls; lifting experience and large existing strength doses limit transfer. RE is not heart rate or race time. | Moderate for pooled RE, low for incremental benefit in already strong runners; pending draft. |
| C12 — Combined strength methods improved RE; magnitude sensitive to outliers. | Llanos-Lagos 2024a, same DOI. | §3.4, Fig. 3, main and outlier-excluded analysis. | Runner population; combinations of resistance/plyometric methods vs controls; 6–24 weeks overall. | ES −0.647 (−1.140 to −0.154); after exclusions −0.426 (−0.768 to −0.083), p=.018. | D*; heterogeneity and intervention composition; cannot infer superiority over high-load training from separate control contrasts. Review rated certainty low for combined methods. | Low; pending draft. |
| C13 — Speed-specific plyometric RE signal and exploratory high-load moderators. | Llanos-Lagos 2024a, same DOI. | Abstract Results; §3.4 main effects and moderator analyses. | Same review; plyometrics vs controls; speed and VO2max moderation. | Plyometric speed subgroup ≤12 km/h ES −0.307, p=.028; speed moderator β=.470, p=.017. High-load speed β=−.117, p=.027 and VO2max β=−.040, p=.020. Intervals not extracted. | D*; model/subgroup associations and many comparisons; no pace cutoff or individual predictive rule; high mechanical loading may be inappropriate in some athletes. | Low; screening pending moderator and CI verification. |
| C14 — High-load supplemental strength improved running performance. | Llanos-Lagos et al. 2024b, *Sports Med* 54:1801–1833. [10.1007/s40279-024-02018-z](https://doi.org/10.1007/s40279-024-02018-z) | Results, Running Performance, Fig. 6, publisher full text. | Moderate to highly trained runners; high-load strength vs running alone or very-low-load strength control; eight studies in high-load performance analysis; review overall 6–40 weeks. | ES −0.469 (−0.872 to −0.066), p=.029; I²<.001%. | D*; combines time trial and TTE, heterogeneous distances and comparators; not a percentage race-time prediction. | Moderate/low pooled, low for existing high-dose lifters; pending draft. |
| C15 — Combined methods also improved pooled performance; plyometrics alone uncertain. | Llanos-Lagos 2024b, same DOI. | Results, Running Performance, Fig. 6. | Six combined studies; plyometric analysis 14 groups from 12 studies; respective controls. | Combined −1.035 (−1.967 to −0.103), I²=67.475%; plyometric −0.210 (−0.433 to 0.014). | D*; imprecise, heterogeneity; separate comparisons against controls do not show combined methods outperform high-load strength. | Low; pending draft for combined contrast; plyometrics context. |
| C16 — Running benefits need not coincide with detectable VO2max improvement. | Llanos-Lagos 2024b, same DOI. | Abstract Results and Discussion; individual outcome figures not re-extracted. | 38 studies, 894 runners overall, 6–40 weeks; strength methods vs control. | No statistically detected improvements across assessed VO2max, vVO2max, maximum metabolic steady state or sprint-capacity analyses (reported p>.072). | D*; not equivalence, outcome-specific sample counts differ. Mechanisms not causally identified. | Low for null inference; context, screening for individual endpoints. |
| C17 — Heavy strength work improved laboratory outcomes in well-trained runners. | Støren et al. 2008, *Med Sci Sports Exerc* 40:1087–1092. [10.1249/MSS.0b013e318168da2f](https://doi.org/10.1249/MSS.0b013e318168da2f) | Abstract, Results; full tables outstanding. | 17 runners randomized (8 intervention/9 control); 4 sets × 4RM half-squat, 3 days/week for 8 weeks, plus habitual running vs habitual running. | Intervention within-arm 1RM +33.2%, RE improved 5%, TTE +21.3%; control no detected change. Direct contrast CI not extracted. | D*; very small sample, prior strength training unclear; within-arm changes not a direct group effect; TTE distinct from race time. | Low; screening; included-study overlap with reviews. |
| C18 — Adding maximal strength and plyometrics improved fatigued running outcomes. | Zanini et al. 2025, *Med Sci Sports Exerc* 57:1546–1558. [10.1249/MSS.0000000000003685](https://doi.org/10.1249/MSS.0000000000003685) | Publisher abstract Results, 90-min RE and TTE contrasts; full figures outstanding. | 28 well-trained male runners, matched/randomized 14 per group; 10 weeks, 2 strength/plyometric sessions/week plus usual running vs usual running. | RE change at 90 min −2.1% vs +0.6%, p=.04; group×training×run-time interaction p=.003, partial η²=.13. Fatigued TTE +35% vs −8%, interaction p=.004, partial η²=.28. CIs unavailable in abstract. | D*; male runner sample, heavy-domain lab test, combined stimulus, not marathon race time; habitual lifting exposure and intake control need extraction. | Low/moderate trial-specific; low hybrid transfer; pending draft for RE result, TTE separately screened. |
| C19 — A recreational-runner trial reported improved 2-km performance. | Trowell et al. 2022, *Scand J Med Sci Sports* 32:543–558. [10.1111/sms.14092](https://doi.org/10.1111/sms.14092) | Abstract, Results; full contrast model to confirm. | 30 moderately trained distance runners, ≥30 km/week, no strength experience; randomized 10-week CT vs control. | Reported MD −11.3 s (95% CI −19.0 to −3.7; reordered endpoints), p=.006; TTE MD +59.1 s (8.58–109.62). | D*; novice lifters, exact contrast specification needs full paper; cannot expect same gain in experienced hybrid athletes. | Low for target transfer; screening. |

**Interpretation:** training for strength and training for running economy are potentially complementary. However, the intervention contrast is usually adding strength work to runners who previously did less of it, not adding extra heavy squats to an athlete already doing substantial lower-body work. The appropriate engineering question is whether existing strength sessions already supply the relevant stimulus and whether changing them would improve the joint objectives. Do not double-count strength work by appending a separate runner-strength program automatically. The economy and performance reviews share research groups and primary studies; their estimates are separate endpoints, not independent replications. Støren and Trowell are examples of constituent-era studies, not additional independent votes. Zanini is newer than these reviews. Improved economy may improve performance, but neither individual mediation nor a direct prediction follows from these data.

### 2.3 Session sequence, spacing and maintenance

| ID / empirical finding | Publication and DOI | Exact result locator / access | Population; intervention vs comparator; duration | Effect / uncertainty | Limitations and applicability | Confidence / disposition |
|---|---|---|---|---|---|---|
| C20 — In trained cohorts, same-session CT had a more negative estimate than separately scheduled CT, each compared with RT alone. | Petré 2021, DOI C04. | §3.5, Figs. 3–4, full text. | Trained subgroup; same session (<20 min) vs RT-only and separate sessions (>2 h) vs RT-only. | Same ES −0.66 (−1.08 to −0.25); separate −0.10 (−0.43 to .23). | D*; not a randomized direct timing contrast pooled across identical doses; intermediate spacing not established. | Low; pending draft for separate scope; no mandatory two-hour minimum. |
| C21 — Same-session CT explosive-strength estimate favored RT only. | Schumann 2022, DOI C01. | §3.3, supplement Fig. S11 as cited in text. | Mixed adults, same-session ≤20 min vs RT-only; separately scheduled strata. | Same-session SMD −0.31 (−0.62 to −0.01), p=.043; separate ≥3 h not statistically detected. | D*; not evidence of a threshold, timing effect may depend on study design and endpoints. | Low for spacing policy; contextual qualification of C02. |
| C22 — Resistance-first intra-session ordering favored lower-body dynamic strength. | Eddens, van Someren & Howatson 2018, *Sports Med* 48:177–188. [10.1007/s40279-017-0784-1](https://doi.org/10.1007/s40279-017-0784-1) | Results, Fig. 2; full result text via publisher/search. | Healthy adults, 10 studies overall, ≥5 weeks; resistance→endurance vs endurance→resistance within session. | Weighted difference in % change 6.91 percentage points (95% CI 1.96–11.87), p=.006; hypertrophy 1.15 (−1.56 to 3.87). | D*; largely recreational/untrained, mixed endurance modalities. Not proof for race-specific run quality or separate-day ordering. | Low/moderate for tested order, low transfer; pending draft. |
| C23 — Spacing manipulated experimentally in amateur rugby athletes. | Robineau et al. 2016, *J Strength Cond Res* 30:672–683. [10.1519/JSC.0000000000000798](https://doi.org/10.1519/JSC.0000000000000798) | Abstract, Results; full estimates and methods not extracted. | 58 amateur rugby players randomized control, RT-only or CT at 0/6/24 h; 7 weeks, 2 sessions of each quality weekly, strength always first. | Authors reported smaller bench and half-squat gains with immediate sequencing than delayed or RT-only groups. VO2peak improved in CT groups; largest reported change in 24 h group. Numerical CIs not extracted. | D*; rugby, not habitual distance running; magnitude-based inference methodology requires scrutiny; timing alters calendar/recovery as well. Shared study across syntheses. | Low; screening, not a 6/24-hour universal rule. |
| C24 — Acute order can affect next-day running, in the reverse direction from strength-first preferences. | Doma & Deakin 2013, *Appl Physiol Nutr Metab* 38:651–656. [10.1139/apnm-2012-0362](https://doi.org/10.1139/apnm-2012-0362) | Abstract, Results, next-day RE/TTE. | 14 trained/moderately trained male runners; both orders with 6 h between modes; next-day tests vs baseline. | TTE at 110% ventilatory threshold: strength→run 237.8±67.4 s; run→strength 275.3±68.0 s; baseline 335.4±92.1 s (both vs baseline p<.01). Higher oxygen cost after strength→run than baseline and reverse order at 70/90% VT. ± values as reported, not contrast CIs. | D* acute; small sample, sequence and prior exposure; cannot infer chronic adaptation or full recovery time. | Low; screening. |
| C25 — Reduced doses can preserve some fitness outcomes, but athlete-specific minimum doses are unresolved. | Spiering et al. 2021, *J Strength Cond Res* 35:1449–1458. [10.1519/JSC.0000000000003964](https://doi.org/10.1519/JSC.0000000000003964) | Practical Applications; abstract Results/conclusion; full review text. Packet 001 contextual result. | Narrative review, predominantly general populations; reduced frequency/volume with retained intensity vs habitual exposure; outcome-specific horizons. | No single pooled estimate. Short and long endurance outcomes differ in minimum-dose evidence; authors explicitly lack sufficient athlete-specific data. | I; do not turn examples into maintenance floors for a trained runner or advanced lifter. | Low for hybrid prescriptions; contextual only. |

### 2.4 Protocol comparison and directness audit

| Study / comparison | Resistance exposure | Endurance exposure | What is varied / what is not identified |
|---|---|---|---|
| Gomes 2025, CT vs RT (11 weeks) | Same two-phase resistance plan in CT and RT as described in abstract; 3 sessions/week; sets, loads and actual attendance to extract. | Running 30 min at moderate-to-heavy intensity, 3 times/week (90 min/week nominal), immediately ordered after RT (exact delay outstanding). | Addition of running to a given strength program, not independent intensity, duration, sequencing or nutrition effects. |
| Robineau 2016, direct timing contrast | 2 strength sessions/week; strength first. Exact sets/intensities outstanding. | 2 aerobic sessions/week; 0/6/24 h delays; mode and dose details to verify in full paper. | Assigned spacing in rugby players; no reverse-order comparison or continuously sampled dose-response. |
| Støren 2008 | Half-squat 4×4RM ×3/week = 12 prescribed sets/week, 96 over 8 weeks if completed; actual adherence not extracted. | Habitual distance running in both arms; exact km and intensity distribution outstanding. | Addition of this strength intervention to running; not optimal strength volume or marginal benefit for a strong lifter. |
| Zanini 2025 | Combined maximal-strength/plyometric work twice weekly ×10 weeks = 20 planned sessions; component sets/contacts outstanding. | Habitual running in both arms; exact matched realized km/intensity and intake control outstanding. | Combined supplement effect; cannot isolate heavy lifting vs plyometric work or infer optimal weekly allocation. |
| Trowell 2022 | Concurrent strength intervention; participants inexperienced with strength training; exact prescribed and realized set dose outstanding. | Baseline running ≥30 km/week; intervention endurance dose and comparator adherence to verify. | Strength introduction, not optimization for dual-experienced athletes. |
| Doma 2013 | Strength and run in each order, 6 h apart. Exact strength stimulus to extract. | Same-day running plus next-day lab tests. | Acute sequence-related next-day performance; not multiweek adaptation. |

**Additional screening leads, deliberately not admitted as claims:**

- Held et al. 2026, umbrella review, [10.1007/s40279-026-02401-y](https://doi.org/10.1007/s40279-026-02401-y). Abstract reports 17 meta-analyses, 144 individual studies and broadly favorable concurrent-training results; no significant sequence effect reported overall. Audit overlapping primary trials, outcome/comparator alignment, sequence interaction versus within-group effects and umbrella methods before using this as an adjudicator of Eddens or Petré. A review of reviews is not 17 independent replications.
- Time-equated concurrent programs in resistance-trained men, [PMID 38689592](https://pubmed.ncbi.nlm.nih.gov/38689592/). Small 4-arm trial (23 men); cycling rather than running, squat/press and muscle-thickness outcomes. Relevant to modality and upper-body questions but not direct running evidence; verify DOI/full protocol before drafting a claim.
- Gomes et al., 2026 ahead-of-print, [10.1519/JSC.0000000000005698](https://doi.org/10.1519/JSC.0000000000005698), trained men, 11-week two-phase intervention and muscle morphology. Determine whether it shares the 2025 trial cohort (same sample count and phase structure do not prove independence); extract full data before counting it separately.
- Ferraro-Farro et al. 2026, sprint-interval CT synthesis, [10.1055/a-2820-4527](https://doi.org/10.1055/a-2820-4527), [indexed erratum](https://doi.org/10.1055/a-2838-3251). Do not use unverified corrected estimates or equate sprint intervals with endurance threshold sessions.
- Zanini et al. 2026, cross-sectional running durability study, [10.1249/MSS.0000000000003840](https://doi.org/10.1249/MSS.0000000000003840). Long-run exposure and volume associated with durability, not causal dose identification. Relevant to Packet 005, especially why aerobic maintenance cannot be reduced to VO2max.
- Doma & Deakin 2015, repeated short-term concurrent-training exposure, [10.1080/02701367.2015.1053104](https://doi.org/10.1080/02701367.2015.1053104). Inspect acute performance and fatigue trajectory separately from long-term interference.

### 2.5 What the evidence identifies — and does not

| Practical question | Best available inference | Unresolved causal question |
|---|---|---|
| Is running inherently incompatible with hypertrophy or maximal strength? | C01–C07 indicate compatibility on average, with possible outcome- and population-specific attenuation. | Individual marginal effect at a particular mileage, intensity mix, strength dose and nutritional state. |
| Is lower-body training more sensitive than upper-body work? | Running directly loads the lower limbs; lower-body results dominate relevant trials. C23 includes bench findings and C06 includes upper-body outcomes. | Direct within-study upper/lower comparison across realistic running doses in strong runners. Local overlap is a plausible scheduling heuristic, not a quantified effect; systemic constraints may affect upper body too. |
| Is easy running better than intervals for strength? | Dose, duration, intensity and modality vary; C09 and C10 provide weak or indirect clues and C08 tests one moderate-to-heavy dose. | Equalized protocols isolating intensity distribution at realistic mileage, plus effects on running objectives. An easier session may consume less acute effort yet a long easy run can impose substantial duration and mechanical load. |
| Is lifting always beneficial to running? | C11–C19 support adding specific strength work in runners, including benefits under fatigue. | Marginal benefit and cost of further sets in athletes already lifting hard; effect on race performance when both disciplines are progressively loaded. |
| Can a scheduler learn optimal spacing from one bad workout? | C20–C24 support considering alternatives; acute performance and adaptation are distinct. | Individual causal response and flexible schedule policy efficacy across repeated weeks. |
| Should concurrent blocks alternate emphasis or progress both? | Multiweek trials show both qualities can coexist; Packet 001 periodization evidence was largely resistance-only. | Direct comparisons of longitudinal hybrid priority allocation with matched time, baseline dose and nutrition. |

Treat the total intervention as a vector: movement/muscle-group strength exposures, run intensity and duration distributions, mechanical loading, session ordering, nutrition and recovery context. Avoid a single arbitrary common workload unit or multiplying pooled SMDs into an individual forecast. Mechanistic hypotheses (local fatigue, substrate use, molecular signaling, muscle damage) can guide questions but cannot prove chronic interference from acute signals. No eligible adaptive-policy trial was identified in this targeted search; absence of a retrieved trial is not proof none exists.

### 2.6 Additional boundary findings: aerobic capacity, modality and nutrition

| ID / empirical finding or context | Publication and DOI | Exact result locator / access | Population; intervention vs comparator | Effect / uncertainty | Limitations and applicability | Confidence / disposition |
|---|---|---|---|---|---|---|
| C26 — VO2max gains in trained endurance strata were not detectably impaired by CT. | Huiberts 2024, DOI C05. | §3.5, Fig. 6. | Adult endurance-status subgroups; CT vs ET-only, ≥4 weeks. | Untrained −0.35 (−0.70 to −0.01); trained 0.18 (−0.02 to 0.38); highly trained 0.01 (−0.32 to 0.34); subgroup p=.04. | D*; mixed aerobic modes, experience classifications, few highly trained data for other outcomes; not proof of equivalence or of endurance performance retention. | Low/moderate for pooled trained contrast, low for transfer to specific races; pending draft. |
| C27 — In a small trial of trained lifters, cycling-based concurrent programs and RT-only all improved squat and bench strength. | Dolan et al. 2024, *J Hum Kinet* 91:87–103. [10.5114/jhk/185637](https://doi.org/10.5114/jhk/185637) | Abstract, Results; full protocol and contrast posterior outstanding. | 23 trained men, 4 arms; interval cycling, moderate continuous cycling, barbell circuit or RT-only; ~1 h/week additional conditioning on non-RT days in concurrent arms. | Squat change: interval +16.88 kg (95% CrI 11.15–22.63), moderate +25.54 (19.24–31.96), RT +20.36 (15.29–25.33); bench +11.86 (8.28–15.47), +10.30 (6.49–14.13), +10.16 (7.02–13.22), respectively. These are arm estimates, not direct between-arm intervals. | D* for cycling, I for running-specific inference. Very small groups; cannot infer equivalence, dose limits or replacing running-specific training with cycling. | Low; screening. |
| N01 — Problematic low energy availability is a potential health and performance constraint, not a diagnosis from training logs. | Mountjoy et al. 2023 IOC REDs consensus, *Br J Sports Med* 57:1073–1097. [10.1136/bjsports-2023-106994](https://doi.org/10.1136/bjsports-2023-106994) | Definitions box 1; introduction and abstract; publisher text. | Male and female athletes; consensus synthesis, not a randomized concurrent-program contrast. | No single effect estimate or validated log-based threshold. | I/context; consensus distinguishes adaptable and problematic LEA and recognizes individual modifiers. No automated diagnosis or universal threshold; nutrition workstream must review direct evidence. | Contextual safety rationale; not a new J1 empirical claim. |

C26 adds the complementary CT-vs-ET-only aerobic contrast missing from the strength-oriented catalog. C27 updates the screening lead in §2.4 with verified DOI and abstract estimates; it is still indirect for running. N01 is a boundary for safety and data interpretation, not an expanded nutrition literature review. The next packet should appraise how energy intake, carbohydrate availability, protein, expenditure measurement and deficits modify training responses rather than assuming these variables were matched in CT studies. No study reviewed here isolates nutrition × strength × running interactions at a realistic hybrid dose.

## 3. Candidate coaching policies

All policies below are drafts. The empirical findings constrain plausible decisions; they do not uniquely determine a policy. The ordering, hold behavior and intervention hierarchy are programming and engineering choices requiring review. Keep a versioned distinction between objective changes, prescribed exposure changes, scheduling changes and in-session permitted execution choices. A recommendation is not an approval. When evidence is unavailable, record the gap rather than citing an unrelated finding.

### CT-P01 revision 0.2 — Preserve secondary performance objectives in either direction

- **Decision:** choose exposures to retain when one discipline has priority; identify when the secondary objective requires revision.
- **Inputs:** ranked athlete goals, assessment/race dates, habitual realized training, comparable strength and running outcomes, relevant muscle/movement history, schedule, preferences, restrictions, fatigue and nutrition context; explicit baseline and measurement quality for each protected outcome.
- **Proposed logic (M/S):** ask which secondary qualities must be retained (e.g., squat strength, 5-km performance, long-run tolerance, upper-body muscle size). Start from the athlete's representative tolerated exposure, not generic minimal doses. If a reduction is needed, preserve goal-specific stimulus and choose which less-important components may be reduced; review the secondary outcome independently. If retention is uncertain, label it as uncertain rather than guaranteed. If constraints conflict, compare feasible alternatives or request a revised objective. When the evidence of retention is missing, maintain the distinction between an exposure commitment and proven maintenance.
- **Evidence:** C25 is indirect; C01/C04/C26 concern adaptation relative to single-mode training, not validated maintenance floors. C11–C19 indicate that existing resistance training may contribute to running objectives. Packet 002 RT-P02 supports retaining productive volume as a candidate, not proof of superiority.
- **Programming judgment:** baseline-relative reduction, prioritization and which stimuli to preserve. No minimum run count, minimum set count, universal percentage reduction or exact loss tolerance is specified.
- **Assumptions / limitations / exclusions:** available representative history and sufficiently comparable outcome data; no assumption that VO2max retention proves race durability or that strength retention proves hypertrophy retention. Do not reduce protected exposure below an explicitly agreed commitment without athlete-approved revision; do not apply as a routine maintenance plan during injury, illness or medical restrictions. If the athlete intentionally deprioritizes an outcome, document that change rather than mislabeling it as maintenance.

### CT-P02 revision 0.2 — Schedule and sequence around key-session quality

- **Decision:** assign lift and run sessions to feasible slots and determine their ordering when they share a day/session.
- **Inputs:** available slots and transition time; planned and actual session duration/intensity; priority, movement groups, run purpose, recent unfamiliar loading, previous session response, race dates, nutrition/recovery opportunities; cross-week neighboring sessions and constraints.
- **Proposed logic (M/S):** identify protected strength and run sessions; identify overlapping lower-limb demands and likely high-fatigue adjacencies. Prefer a schedule that avoids unnecessary competition between priority sessions when feasible. Compare alternatives with same prescribed exposure before changing dose. If a combined session is necessary and dynamic lower-body strength is the priority, consider lifting first; if a key run is the priority, protect its execution quality (may mean running first or moving it). Upper-body work and an easy run can be considered separately from heavy lower-body lifting and a demanding run. Compare consolidated hard days plus recovery days with distributed scheduling; neither is the universal default. If spacing cannot be increased without sacrificing adherence or a goal, expose the tradeoff, allow a feasible combined schedule where safe, and monitor. A missed workout is not automatically made up next to a key session.
- **Evidence:** C20–C23 inform the strength-side ordering/spacing question; C24 informs acute next-day run quality. C04/C05/C08 indicate lower-body strength is worth protecting; C06/C23/C27 caution against assuming upper-body immunity. Direct evidence supports some conditional comparisons; protecting the key run first is a pragmatic extrapolation, not demonstrated chronic superiority of run-first.
- **Programming judgment:** weighting session importance, local overlap, convenience and accumulated burden; defining an acceptable schedule and tie-break. The observed study gaps of minutes/hours are not validated personal recovery requirements. Neither a hard-day grouping rule nor separate-day scheduling is established as optimal.
- **Assumptions / limitations / exclusions:** feasible timing and explicit athlete priority. Do not override medical restrictions, availability, approved event protection or the block exposure envelope. Do not infer a causal effect from a single low-quality session, impose a new mandatory gap, or automatically move an easy run away from upper-body work.

### CT-P03 — Joint endurance dose review (intensity, duration, frequency and modality)

- **Decision:** retain, redistribute, progress or reduce running exposure in the context of resistance training.
- **Inputs:** realized and prescribed run minutes/distance, frequency, intensity domain and how classified, long-run exposure, terrain/elevation, intervals including recovery, RPE/HR/pace coverage, lower-body lift exposure, both performance trends, recovery, intake context and available time.
- **Proposed logic (M):** maintain productive tolerable running when objectives and constraints are satisfied. When an endurance increase is justified, compare candidate adjustments to duration, intensity distribution or frequency, and identify expected competition with strength work. If repeated lower-body or run-quality issues emerge, consider scheduling changes, modifying a non-priority session, or reducing the relevant dose rather than treating all running as a problem. A cycling substitution is an option only if the athlete accepts the loss of running specificity and it meets the stated objective; record the change in modality and distinguish it from a completed run. Avoid silent removal of long runs or quality work to optimize squat performance.
- **Evidence:** C09/C10 generate hypotheses about dose and modality but are insufficient to rank practical intensity distributions. C01/C02/C04/C08 support outcome-specific monitoring; C27 is cycling context. C25 underscores uncertainty about maintenance; C26 concerns VO2max rather than specific race outcomes.
- **Programming judgment:** which stimulus is a candidate for change and how to protect running specificity; evaluating local demands and athlete preference. No universal mileage progression rate, interval allocation, frequency or conversion between running and cycling.
- **Assumptions / limitations / exclusions:** requires reliable intensity definitions and representative habitual exposure. Do not interpret cycling capacity as equivalent to long-distance running durability, use cross-study correlations as a causal dose-response or prescribe an unfamiliar high-intensity session simply because a network ranks it favorably. Running progression specifics await Packet 005.

### CT-P04 — Strength-dose selection for running benefit and strength goals

- **Decision:** use existing strength exposure efficiently; add or modify lower-body strength work only when justified by joint goals.
- **Inputs:** movement and muscle-group exposures, strength experience, running history, exercise selection, intensity/load convention, effort, training time, race demands, prior plyometric exposure, tolerance, contraindications and preferences.
- **Proposed logic (M):** map the existing resistance plan to strength and running-related objectives before adding work. Consider preserving a tolerable heavy lower-body stimulus in endurance-emphasis blocks; evaluate plyometrics or combined methods only where appropriate and not already sufficiently represented. Compare retaining versus replacing accessory work before appending another program. In strength-emphasis blocks apply RT-P01 and RT-P02 revision 0.2 with running exposure as an explicit competing resource. When a proposed additional lift volume threatens key run quality, reconsider the dose or schedule; do not automatically remove all strength training.
- **Evidence:** C11–C19 directly examine supplemental strength in runners, with imperfect target transfer; C02/C04/C08 describe possible strength costs from concurrent loading. Packet 002 shows diminishing-return models and uncertainty over adaptive set increases.
- **Programming judgment:** exercise selection, practical dose, intensity, when existing work is sufficient and which extras are expendable. Heavy training's benefits in less-strength-trained runners do not establish additional benefit from adding more sets to a highly trained lifter. RE improvement is a potential co-benefit, not a guaranteed outcome.
- **Assumptions / limitations / exclusions:** competent lifting and appropriate equipment; do not add maximal or plyometric loading to an unprepared, injured or restricted athlete. Do not import the Støren or meta-analysis protocol frequency/loads as universal prescriptions; do not promise running gains proportional to 1RM gains or treat a low HR at a given pace as measured running economy.

### CT-P05 — Integrated workload change review (extension to RT-P02 v0.2)

- **Decision:** decide which discipline and dose dimension, if any, to change after reviewing the previous week.
- **Inputs:** prior approved plan, actual outcomes and deviations for both disciplines; phase and objective, comparable performances, effort/fatigue, sleep and recovery coverage, nutritional/body-weight observations, time constraints and restrictions. Keep actual vs prescribed exposures separate.
- **Proposed logic (M/S):** apply restrictions first. Check data adequacy and adherence. If both domains are progressing or maintaining as intended with acceptable burden, holding both is admissible. If only one objective is lagging, examine specificity, session completion, competing exposure, nutritional context and observation quality before deciding. Prefer a targeted and interpretable change where practical: redistribute sessions, adjust a non-priority dose, increase a justified stimulus, reduce burden, or request more information. Simultaneous increases are not inherently forbidden, but need an explicit joint feasibility rationale and approved policy parameters; do not escalate independently because each single-domain rule passes. When both outcomes deteriorate, consider shared constraints and reduced burden; no automatic diagnosis. Re-evaluate any candidate in the context of both current and upcoming key sessions and secondary commitments.
- **Evidence:** C01–C10 and C20–C24 support contextual concern about competing exposures; C11–C19 support potential complementarity; Packet 002 distinguishes successful dose from tolerable extra dose. No trial validates these feedback branches or escalation conditions.
- **Programming judgment:** holding, sequencing targeted changes, weighting competing objectives and deciding what constitutes enough information. No progression caps, plateau windows, fatigue triggers or readiness scores are established here.
- **Assumptions / limitations / exclusions:** athlete's meaningful prior dose and outcomes are known enough to propose an adjustment. Do not attribute progress or regression to a particular modality solely from time ordering; no automatic catch-up work or escalation on missing data. Hard restrictions, event protection and approval rules take precedence.

### CT-P06 — Nutrition-aware feasibility gate (context only; Packet 004 dependency)

- **Decision:** whether a training change can reasonably be considered without neglecting fueling opportunities or possible health risk.
- **Inputs:** voluntarily supplied intake/meal timing and coverage, body-weight trend and goals, session times/demands, food access, appetite/GI tolerance, athlete feedback, signs of illness or persistent fatigue, any professional guidance; uncertainty in intake, expenditure and fat-free mass. Wearable energy estimates remain estimates, not intake prescriptions.
- **Proposed logic (S/M):** for double-session days check whether the schedule permits meals, fluids and recovery between sessions. When added exposure coincides with restrictive intake, unintentional weight changes or repeated poor performance, ask about fueling and other causes; defer nonessential escalation or offer a lower-burden alternative where appropriate. Do not demand a perfectly logged diet before exercise; missing nutrition observations are unknown. If concerning persistent symptoms, suspected disordered eating, bone-stress injury or other red flags arise, avoid optimizing weight loss/training load and recommend qualified sports-medicine/dietetic assessment. This is safety triage, not diagnosis. Respect athlete consent and privacy.
- **Evidence:** N01 supplies consensus-level safety context; CT trials here do not identify the causal fueling interaction or an optimal macronutrient algorithm. Full evidence appraisal is deferred.
- **Programming judgment:** feasibility prompts, precautionary deferral and referral boundaries. No universal EA cutoff, calorie target, automatic wearable calorie add-back, carb/protein dose or nutrient timing equation. Stable weight does not establish adequate EA; energy balance and energy availability are distinct concepts.
- **Assumptions / limitations / exclusions:** not a clinical or dietary treatment policy. No diagnosis of REDs or underfueling from a single reading or from wearables. Do not propose aggressive body-composition change as a remedy for endurance stagnation. Do not infer nutritional adequacy from absence of logged food.

### HP-P01 — Joint block priority and revision selection

- **Decision:** choose and adapt a balanced, strength-emphasis or endurance-emphasis block rather than two independently optimized programs.
- **Inputs:** explicit objective vector and target dates, current adaptation and training history in both disciplines, available time, secondary protection requirements, recovery/nutrition constraints, athlete preference, observation uncertainty, prior block experience.
- **Proposed logic (M/S):** generate feasible alternatives with their assumptions, expected qualitative benefits, potential costs and assessment plan. Eliminate candidates that violate hard constraints. Prefer non-dominated options where the comparison is supportable; if alternatives involve meaningful tradeoffs, let the athlete choose priorities. No pseudo-precise predicted performance deltas. Within the block preserve its goals while adapting individual sessions; revise objectives only explicitly if new constraints, events, adherence or outcome trends make the block inappropriate. Preserve prior approval and evidence pins; never silently alter completed/approved history.
- **Evidence:** C01/C04/C08/C11/C14/C18/C25/C26 show why both compatible and competing adaptations should be represented. Packet 001 LP-01 concerns resistance periodization and does not establish best hybrid block structure. Packet 002 concerns strength-dose policy, not global allocation.
- **Programming judgment:** block type, duration, phase, protected quality, tradeoff ordering and review cadence; no direct evidence identified favoring one hybrid allocation for all athletes.
- **Assumptions / limitations / exclusions:** objectives must be understandable and agreed. No optimization of body composition at expense of health, and no unapproved objective priority switch. A conflict may require deferral or clinician guidance rather than schedule optimization.

### 3.1 Ordered review procedure and alternative explanations

The following is pseudocode for a candidate decision method, not a normative algorithm or validated policy. Predicates are intentionally qualitative until independently reviewed and operationalized.

```text
review(approved_block, approved_week, completed_observations, constraints):
    if new safety restriction or incompatible protected event:
        return feasible protected alternatives, or explicit defer/conflict
    compare realized exposures with the prescriptions in force
    assess comparability and missingness for each objective separately
    if evidence insufficient:
        request relevant feedback; hold safe feasible exposure or defer change
    enumerate plausible explanations for observed changes
    identify whether priority and secondary objectives remain on track
    generate feasible candidates:
        hold joint dose; move/reorder sessions; modify selected exposure;
        reduce burden; revise block only with explicit review
    assess each candidate against both disciplines, adherence, nutrition context,
        recovery opportunities, upcoming events, athlete preferences and bounds
    disclose evidence support vs transfer vs judgment; present tradeoffs
    return proposal for athlete approval, or explicit no-change/conflict
```

| Observed pattern | Plausible explanations, not diagnoses | First candidate response |
|---|---|---|
| Squat performance falls; presses and runs stable | Local fatigue, recent hard running, squat technique/equipment, load progression, insufficient stimulus, measurement error | Compare sessions and actual preceding exposure; consider moving demanding run or squat before changing all lifting volume. |
| Key runs slow at similar reported effort; strength improves | Local fatigue, high strength dose, terrain/heat, HR measurement error, fueling, changed run exposure | Verify comparable conditions and sensor coverage; consider moving/reducing non-priority lift burden while retaining running-specific work. |
| Both decline; fatigue reported | Shared recovery constraint, illness, sleep, nutrition, stress, excessive total dose, inconsistent execution | Clarify symptoms and actual dose; hold escalation, consider reduced burden or referral if concerning; do not diagnose overtraining or REDs. |
| Running declines with fewer completed runs and no fatigue evidence | Reduced stimulus, scheduling/adherence, inaccurate device data | Address feasibility and adherence; do not label interference or reduce run dose automatically. |
| Better running pace with higher HR or different route | Greater effort, weather, elevation, calibration, real adaptation | Do not treat as comparable evidence of improved RE or fitness; seek matched observations. |
| Single low HRV reading, performance and feedback steady | Normal variability, sensor/measurement changes, stress or sleep | No automatic block rewrite; record uncertainty and ask only if needed. |

## 4. Periodization methodology

### 4.1 Multi-objective representation

A candidate formalization is a partially observed, constrained sequential decision problem. At a weekly review, represent state as prior approved block and actual training history plus estimated/observed outcomes, context and uncertainty. Action includes resistance prescription, run prescription, joint calendar and nutrition feasibility review. The outcome vector includes maximal strength by movement, hypertrophy where requested, aerobic capacity, running-event performance/durability, training tolerance, health/energy constraints, body-composition goal and adherence. Do not collapse everything into a single readiness score or sum unlike physical units.

For conceptual reasoning, let `Y = (strength, hypertrophy, aerobic capacity, run performance, tolerance, body composition, adherence)` and `a = (strength dose, running dose, calendar, nutrition context)`; `Y_future` is uncertain conditional on prior state and `a`. Clinical safety and explicit restrictions are hard constraints, not tradeable utility terms. Secondary objectives can be specified as protected targets with agreed tolerances, when there is a reasonable way to measure them. Athlete priorities can order remaining objectives. This is a proposed representation, not an identified transition model, optimization objective with calibrated weights or validated prediction method. Initially compare qualitative feasible alternatives; use Pareto language only where outcomes are comparable and uncertainty is acknowledged. A forecast with no empirical support must not be treated as a feasible guarantee.

### 4.2 Candidate block archetypes

| Block intent | Strength approach | Running approach | Shared constraint and review |
|---|---|---|---|
| Strength-emphasis | Develop prioritized movements; maintain non-priority strength/muscle exposure; progress with RT-P01/RT-P02 within joint envelope. | Maintain agreed running qualities relative to habitual exposure, protect important run(s); avoid automatic conversion of all runs to easy jogs. | Verify running-specific retention, lower-limb scheduling and nutrition feasibility; if a race becomes priority, revise explicitly. |
| Endurance-emphasis | Retain meaningful strength stimulus and exposure to priority movements; consider reducing accessory or fatiguing lower-body work rather than eliminating lifting. | Progress toward event-specific development (exact intensity/dose strategy deferred to Packet 005). | Protect key run quality and strength outcomes; do not assume strength maintenance with a generic one-session minimum. |
| Balanced development | Progress strength where supported; maintain productive set dose if it works. | Progress running where justified and retain event-specific work. | Changes need joint review; avoid simultaneous independent escalation without rationale, while allowing compatible development. |
| Assessment / event preparation | Prioritize performance on agreed lift assessment; reduce competing fatigue as candidate approach. | Prioritize race-specific readiness when event is primary; adapt other work with consent. | Avoid catch-up sessions; no validated taper duration or cross-discipline dose reduction in this packet. |
| Recovery / interruption | Retain or reduce safe exposure, re-establish comparable performance; distinguish missed vs unknown. | Resume appropriate exposure based on actual interruption and constraints. | No automatic return to nominal trajectory, no compensation for missed dose; dedicated research on interruption/taper pending. |

The archetypes are candidate methodologies. Established intervention evidence supports the possibility of concurrent benefits and certain conditional tradeoffs, not superiority of alternating vs simultaneous priorities. A strength-emphasis block need not mean endurance performance must stagnate, and balanced development need not mean equal volumes or equal objective weights. A block can maintain a particular quality while developing another within the same discipline, such as prioritizing press strength while maintaining squat strength, or prioritizing endurance durability while retaining faster running exposure.

### 4.3 Example weekly organizations (illustrations, not prescriptions)

These examples are deliberately dose-free. They show scheduling alternatives for an athlete with a heavy lower-body session, an upper-body session, a quality run and a long run; other work is determined by the athlete's actual block. No example establishes a minimal spacing rule. Time windows, available days, actual exposure and preferences must be checked including the following Monday.

| Day | Distributed candidate: strength emphasis | Consolidated candidate: endurance emphasis | Balanced candidate |
|---|---|---|---|
| Mon | Priority lower-body strength | Quality run, then optional separate compatible strength slot | Upper-body strength / optional easy run |
| Tue | Easy run or rest | Recovery/easy exposure as appropriate | Quality run |
| Wed | Upper-body strength | Upper-body or non-fatiguing accessory work | Lower-body strength (check Tuesday response and priority) |
| Thu | Protected quality run | Rest or easy run | Rest or easy exposure |
| Fri | Additional lift if in block (prefer compatible work) | Maintained lower-body strength, if compatible with long run | Upper-body or additional strength if justified |
| Sat | Recovery or easy exposure | Recovery or easy exposure | Long run |
| Sun | Long run | Long run | Rest or other approved low-burden work |

The distributed example has a potential Sunday-long-run/Monday-heavy-lift collision across week boundaries; it is intentionally not declared feasible without adjacent-week validation. The consolidated example may compress high demand into a single day and needs feasible fueling, time and recovery. The balanced example places a quality run before lower-body lifting and may not suit an athlete whose squat quality falls after such runs. Generate alternatives rather than treating the calendar as a template to copy. An upper-body plus easy-run combination may be a good option when available, but still check systemic burden and athlete report. No prescription of set counts, running minutes or intensity zones follows from this table.

### 4.4 Longitudinal monitoring and prospective evaluation

| Objective | Observable proxy / assessment | Required caveat |
|---|---|---|
| Strength | Standardized 1RM or comparable load/reps/effort by exercise; estimated 1RM with provenance | Different equipment, ROM, exercise and effort make comparisons uncertain; e1RM is not measured maximal strength. |
| Hypertrophy | Consistent circumference/imaging if available, body composition trends | Body mass and strength alone do not measure muscle hypertrophy. |
| Aerobic capacity | Lab VO2max when available, explicitly labeled wearable estimate | Not equivalent to race performance; device changes affect comparability. |
| Running | Time trials/races with context; matched route/speed/effort observations; durability where relevant | Pace at a given HR is a field proxy, not laboratory RE; heat, terrain, fatigue, fueling and sensors matter. |
| Tolerance/recovery | Reported soreness/fatigue, effort drift, adherence, sleep and HR/HRV trends | Multi-factor observations; no validated single-readiness cutoff or causal diagnosis. |
| Nutrition/body composition | Intake coverage, weight trends, food timing, preferences, professional guidance | Logs, body weight and wearables cannot individually identify true EA or expenditure; Packet 004/007. |
| Adherence | Confirmed/partial/missed/unknown by session and objective, reasons and time burden | Missing records not missed sessions; completion denominators need coverage. |

Prospective comparisons should distinguish policy performance from conformance: compare a fixed joint program, a simple priority-protecting program with conventional progression, and an adaptive joint policy with matched attention and approval opportunities. In a pilot, pre-specify joint success (e.g., priority outcome improvement while secondary outcomes remain within athlete-agreed bounds), adherence/coverage, adverse symptoms, time burden and uncertainty. Do not optimize one metric post hoc. Randomization across athletes or appropriate policy comparisons are stronger than before/after logs; within-athlete repeated comparisons of session ordering can explore acute quality but block adaptation has carryover and temporal confounding. Longitudinal N-of-1 designs need explicit phase effects, order/carryover, measurement reliability and stopping conditions; a short crossover cannot by itself establish long-term concurrent adaptation. Dedicated individual-adaptation research remains queued.

## 5. Evidence catalog additions

**Target:** J1 schema v1 as examined in the previous packets ([catalog.py](https://github.com/dkiv/fitness-intelligence/blob/main/backend/src/fitness_intelligence/evidence/catalog.py), [j1-screening-1](https://github.com/dkiv/fitness-intelligence/blob/main/backend/src/fitness_intelligence/evidence/releases/j1-screening-1.json)). This is an appendable fragment, not a registered release. Reuse existing `schumann@1`, `petre@1`, `pooled-concurrent-strength@1` and `trained-lower-body-strength@1`; preserve their qualification edge. Packet 001 proposed `spiering@1`, but it is not assumed merged; no new claim in this fragment depends on that proposed source. All new claim/source/method records are pending with null approval and empty transfer lists. No approval, active release, withdrawal or supersession changes. Sources are bibliographic references and original factual summaries, not reproduced articles. Check publication status, rights and exact stage/current repository at integration; the previous schema was consulted and prior packet keys compared, but no repository loader is run here.

Proposed new question terms deliberately separate running economy, performance, aerobic capacity, hypertrophy, sequence and timing. The existing `concurrent-strength` question is reused for strength, power and moderation contrasts. Distinct scope terms prevent one outcome silently answering another; exact-match retrieval needs a separately reviewed query mapping. For moderator findings, the scope represents the comparison of program effects across strata, not individual causal moderation. Where a comparison is contextual across questions, express it in prose instead of a cross-question relation, which J1 prohibits. The two timing subgroup comparisons each receive their own record. New question gaps remain explicit. A pending relation is structural context only and does not confer eligibility. No revised claim is marked superseding because J1 requires later approved revisions for that edge. Administrative next-review dates follow the previous packet convention and are not training thresholds.

The following JSON fragment contains a deliberately narrow subset of the evidence table. Abstract-only results with sufficiently specific locators are marked pending and require full-text verification before approval. Other leads remain in screening prose. All numerical values describe studies; none is a policy parameter.

```json
{
  "questions": [
    {
      "id": "concurrent-hypertrophy",
      "description": "How does adding endurance training affect muscle hypertrophy?",
      "gap": "Whole-muscle and fiber outcomes differ; trained runner dose and region-specific effects remain unresolved."
    },
    {
      "id": "concurrent-timing",
      "description": "How does the scheduling of resistance and endurance sessions affect outcomes?",
      "gap": "No validated individual spacing interval or optimal weekly layout."
    },
    {
      "id": "concurrent-sequence",
      "description": "How does same-session ordering affect concurrent adaptations?",
      "gap": "Run-priority and dual-trained comparisons remain limited."
    },
    {
      "id": "strength-running-economy",
      "description": "How does supplemental strength training affect running economy?",
      "gap": "Incremental benefit of additional work in already strong runners remains unknown."
    },
    {
      "id": "strength-running-performance",
      "description": "How does supplemental strength training affect running performance?",
      "gap": "Race-specific effects and optimal strength dose in dual-trained runners remain unknown."
    },
    {
      "id": "concurrent-aerobic-capacity",
      "description": "How does adding resistance training affect aerobic capacity during endurance training?",
      "gap": "VO2max retention is not equivalent to running performance retention."
    }
  ],
  "sources": [
    {
      "key": "huiberts@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "citation": "Huiberts RO, Wüst RCI, van der Zwaard S. Concurrent Strength and Endurance Training: A Systematic Review and Meta-Analysis on the Impact of Sex and Training Status. Sports Med. 2024;54:485–503.",
      "doi": "10.1007/s40279-023-01943-9",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/37847373/",
      "published_on": "2023-10-17",
      "design": "Systematic review and random-effects meta-analysis",
      "access": "full-text",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic and accessible article record examined on 2026-11-24; complete correction/retraction and version audit pending.",
      "rights": "Reuse permissions not independently reviewed; retain only bibliographic metadata, links and original factual summaries pending rights review.",
      "appraisal": "Publisher HTML Results §§3.3–3.5 inspected. Fifty-nine studies overall; unclear allocation concealment and detection bias, sparse highly trained data; study-level moderation. Overlap with prior concurrent-training syntheses requires audit.",
      "next_review": "2027-02-24"
    },
    {
      "key": "lundberg-fibers@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "citation": "Lundberg TR, Feuerbacher JF, Sünkeler M, Schumann M. The Effects of Concurrent Aerobic and Strength Training on Muscle Fiber Hypertrophy: A Systematic Review and Meta-Analysis. Sports Med. 2022;52:2391–2403.",
      "doi": "10.1007/s40279-022-01688-x",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/35476184/",
      "published_on": "2022-04-27",
      "design": "Systematic review and random-effects meta-analysis",
      "access": "full-text",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic and accessible article record examined on 2026-11-24; complete correction/retraction and version audit pending.",
      "rights": "Reuse permissions not independently reviewed; retain only bibliographic metadata, links and original factual summaries pending rights review.",
      "appraisal": "Publisher HTML §§3.1–3.4; 15 studies, 300 participants, only three running studies. Mean PEDro 4.3; tissue endpoint and heterogeneity limit inference; same registered protocol as Schumann adapted for fiber outcomes.",
      "next_review": "2027-02-24"
    },
    {
      "key": "eddens-sequence@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "citation": "Eddens L, van Someren K, Howatson G. The Role of Intra-Session Exercise Sequence in the Interference Effect: A Systematic Review with Meta-Analysis. Sports Med. 2018;48:177–188.",
      "doi": "10.1007/s40279-017-0784-1",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/28917030/",
      "published_on": "2017-09-15",
      "design": "Systematic review and meta-analysis of intra-session ordering",
      "access": "full-text",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic and accessible article record examined on 2026-11-24; complete correction/retraction and version audit pending.",
      "rights": "Reuse permissions not independently reviewed; retain only bibliographic metadata, links and original factual summaries pending rights review.",
      "appraisal": "Publisher article and indexed full result text; ten studies overall; mixed modalities and largely recreational/untrained populations; individual spacing and chronic run-performance outcomes unresolved.",
      "next_review": "2027-02-24"
    },
    {
      "key": "llanos-lagos-economy@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "citation": "Llanos-Lagos C, Ramirez-Campillo R, Moran J, Sáez de Villarreal E. Effect of Strength Training Programs in Middle- and Long-Distance Runners’ Economy at Different Running Speeds: A Systematic Review with Meta-analysis. Sports Med. 2024;54:895–932.",
      "doi": "10.1007/s40279-023-01978-y",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/38165636/",
      "published_on": "2024-01-02",
      "design": "Systematic review and multilevel meta-analysis",
      "access": "full-text",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic and accessible article record examined on 2026-11-24; complete correction/retraction and version audit pending.",
      "rights": "Reuse permissions not independently reviewed; retain only bibliographic metadata, links and original factual summaries pending rights review.",
      "appraisal": "Publisher HTML §3.4, Figs. 2–3, certainty appraisal and discussion inspected. Multiple measured speeds, small effects, sensitivity to outliers, varied training backgrounds. No validated marginal dose for experienced lifters.",
      "next_review": "2027-02-24"
    },
    {
      "key": "llanos-lagos-performance@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "citation": "Llanos-Lagos C, Ramirez-Campillo R, Moran J, Sáez de Villarreal E. The Effect of Strength Training Methods on Middle-Distance and Long-Distance Runners’ Athletic Performance: A Systematic Review with Meta-analysis. Sports Med. 2024;54:1801–1833.",
      "doi": "10.1007/s40279-024-02018-z",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/38627351/",
      "published_on": "2024-04-17",
      "design": "Systematic review and random-effects meta-analysis",
      "access": "full-text",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic and accessible article record examined on 2026-11-24; complete correction/retraction and version audit pending.",
      "rights": "Reuse permissions not independently reviewed; retain only bibliographic metadata, links and original factual summaries pending rights review.",
      "appraisal": "Publisher HTML Running Performance results and discussion inspected; Fig. 6. Mixed time trials and TTE; combined method heterogeneity; certainty very low to moderate. Overlap with economy review to audit.",
      "next_review": "2027-02-24"
    },
    {
      "key": "zanini-durability@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "citation": "Zanini M, Folland JP, Wu H, Blagrove RC. Strength Training Improves Running Economy Durability and Fatigued High-Intensity Performance in Well-Trained Male Runners: A Randomized Control Trial. Med Sci Sports Exerc. 2025;57:1546–1558.",
      "doi": "10.1249/MSS.0000000000003685",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/40016936/",
      "published_on": "2025-02-28",
      "design": "Randomized parallel-group trial",
      "access": "abstract",
      "checked_on": "2026-11-24",
      "publication_check": "Bibliographic and accessible article record examined on 2026-11-24; complete correction/retraction and version audit pending.",
      "rights": "Reuse permissions not independently reviewed; retain only bibliographic metadata, links and original factual summaries pending rights review.",
      "appraisal": "Publisher/PubMed abstract inspected; performance-matched randomized groups. Full dose, baseline strength history, attrition, direct intervals and figures require extraction. Combined strength/plyometric intervention; male runners.",
      "next_review": "2027-02-24"
    }
  ],
  "claims": [
    {
      "key": "pooled-concurrent-explosive-strength@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-strength",
        "objective": "power-development",
        "population": "healthy-adults",
        "experience": "mixed",
        "intervention": "supervised-aerobic-plus-strength",
        "comparator": "identical-strength-only",
        "outcome": "explosive-strength",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "Pooled explosive-strength gains were smaller with concurrent training than with resistance training alone.",
      "limitations": "Mixed modalities and experience; influential study and sensitivity of subgroup estimates; not maximal strength.",
      "quality": "moderate",
      "assessment": "18 studies; moderate methodological limitations; running-specific and individual transfer unresolved.",
      "transfers": [],
      "support": [
        {
          "source": "schumann@1",
          "locator": "Results §3.3, Fig. 3",
          "result": "SMD −0.28 (95% CI −0.48 to −0.08), I²=35.81%.",
          "restriction": "Explosive strength only; no individual spacing threshold."
        }
      ]
    },
    {
      "key": "pooled-concurrent-whole-muscle-hypertrophy@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-hypertrophy",
        "objective": "hypertrophy-development",
        "population": "healthy-adults",
        "experience": "mixed",
        "intervention": "supervised-aerobic-plus-strength",
        "comparator": "identical-strength-only",
        "outcome": "whole-muscle-hypertrophy",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The average whole-muscle hypertrophy difference between concurrent training and matched resistance-only training was close to zero.",
      "limitations": "15 studies; heterogeneous protocols, mixed experience, no equivalence test; fiber-level outcome differs.",
      "quality": "moderate",
      "assessment": "Pooled contrast moderately precise; running dose and dual-trained transfer unestablished.",
      "transfers": [],
      "support": [
        {
          "source": "schumann@1",
          "locator": "Results §3.4, Fig. 4",
          "result": "SMD −0.01 (95% CI −0.16 to 0.18), I²=0%.",
          "restriction": "Whole-muscle outcome only."
        }
      ]
    },
    {
      "key": "concurrent-lower-body-sex-moderation@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-strength",
        "objective": "strength-development",
        "population": "healthy-adults-aged-18-50",
        "experience": "mixed",
        "intervention": "concurrent-versus-strength-only-male-subgroup",
        "comparator": "concurrent-versus-strength-only-female-subgroup",
        "outcome": "lower-body-maximal-strength",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The estimated concurrent-versus-strength-only contrast for lower-body strength differed between male and female subgroups.",
      "limitations": "Sparse female data, wide female interval and study-level moderation; no causal individual sex-specific policy.",
      "quality": "low",
      "assessment": "20 lower-body studies; unclear concealment/detection bias; directness limited.",
      "transfers": [],
      "support": [
        {
          "source": "huiberts@1",
          "locator": "Results §3.4, Figs. 3–4",
          "result": "Male SMD −0.43 (95% CI −0.64 to −0.22); female 0.08 (−0.34 to 0.49); subgroup difference p=0.03.",
          "restriction": "Comparison of program effects across sex strata; not a sex-based progression rule."
        }
      ]
    },
    {
      "key": "concurrent-strength-experience-moderation@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-strength",
        "objective": "strength-development",
        "population": "healthy-adults-aged-18-50",
        "experience": "mixed",
        "intervention": "concurrent-versus-strength-only-trained-strength-subgroup",
        "comparator": "concurrent-versus-strength-only-untrained-strength-subgroup",
        "outcome": "lower-body-maximal-strength",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The synthesis did not detect a difference in the concurrent-training lower-body strength effect between strength-trained and untrained subgroups.",
      "limitations": "Study-level classification; insufficient highly trained data; no equivalence or evidence of absence.",
      "quality": "low",
      "assessment": "16 studies in this moderation contrast; related Petré subgroup result uses different classifications and inclusion.",
      "transfers": [],
      "support": [
        {
          "source": "huiberts@1",
          "locator": "Results §3.5, Fig. 5B",
          "result": "Between-strength-experience subgroup p=1.00; subgroup estimate intervals not extracted in this record.",
          "restriction": "Interaction result only; not a within-trained comparison."
        }
      ]
    },
    {
      "key": "pooled-concurrent-fiber-hypertrophy@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-hypertrophy",
        "objective": "hypertrophy-development",
        "population": "healthy-adults",
        "experience": "mixed",
        "intervention": "supervised-aerobic-plus-strength",
        "comparator": "identical-strength-only",
        "outcome": "muscle-fiber-hypertrophy",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The pooled fiber-level hypertrophy estimate modestly favored resistance-only training, with uncertainty reaching zero at reported precision.",
      "limitations": "Only three running studies; biopsy variation, mixed populations and substantial heterogeneity; not whole-muscle hypertrophy.",
      "quality": "low",
      "assessment": "15 studies, mean PEDro 4.3; related source protocol and potential overlap with Schumann.",
      "transfers": [],
      "support": [
        {
          "source": "lundberg-fibers@1",
          "locator": "Results §3.2, Fig. 2",
          "result": "SMD −0.23 (95% CI −0.46 to −0.00), p=0.050, I²=58.6%.",
          "restriction": "Overall fiber-level outcome; not a body-composition prediction."
        }
      ]
    },
    {
      "key": "running-type-one-fiber-hypertrophy@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-hypertrophy",
        "objective": "hypertrophy-development",
        "population": "healthy-adults",
        "experience": "mixed",
        "intervention": "supervised-running-plus-strength",
        "comparator": "identical-strength-only",
        "outcome": "type-one-muscle-fiber-hypertrophy",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "In the running subgroup, type I fiber hypertrophy was smaller with concurrent training than with resistance-only training.",
      "limitations": "Only three running studies overall; §3.3 reports no statistically significant subgroup differences; no proof of running-versus-cycling effect modification.",
      "quality": "low",
      "assessment": "Small subgroup, heterogeneity, study-level modality assignment; no approved transfer.",
      "transfers": [],
      "support": [
        {
          "source": "lundberg-fibers@1",
          "locator": "Abstract Results, running subgroup; §3.3, Fig. 4",
          "result": "SMD −0.81 (95% CI −1.26 to −0.36).",
          "restriction": "Type I fibers, not whole-muscle hypertrophy or a mandate to replace running."
        }
      ]
    },
    {
      "key": "same-session-trained-lower-body-strength@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-timing",
        "objective": "strength-development",
        "population": "healthy-adults-aged-18-40",
        "experience": "structured-training",
        "intervention": "same-session-running-or-cycling-plus-strength",
        "comparator": "identical-strength-only",
        "outcome": "squat-or-leg-press-one-rm",
        "horizon": "six-to-twenty-one-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "In the trained same-session subgroup, the estimate favored resistance-only training for lower-body 1RM.",
      "limitations": "Study-level subgroup; same-session definition under 20 min; overall review duration range; not direct randomized comparison of timing.",
      "quality": "low",
      "assessment": "Small studies and mixed running/cycling; differences in dose and training status.",
      "transfers": [],
      "support": [
        {
          "source": "petre@1",
          "locator": "Results §3.5, Fig. 3, trained subgroup",
          "result": "ES −0.66 (95% CI −1.08 to −0.25).",
          "restriction": "Not evidence of a minimum safe gap."
        }
      ]
    },
    {
      "key": "separate-session-trained-lower-body-strength@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-timing",
        "objective": "strength-development",
        "population": "healthy-adults-aged-18-40",
        "experience": "structured-training",
        "intervention": "different-session-running-or-cycling-plus-strength",
        "comparator": "identical-strength-only",
        "outcome": "squat-or-leg-press-one-rm",
        "horizon": "six-to-twenty-one-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "In the trained different-session subgroup, the lower-body 1RM contrast was uncertain and close to zero.",
      "limitations": "Study-level subgroup; separate defined as over two hours; overall review duration range; interval allows meaningful impairment.",
      "quality": "low",
      "assessment": "No equivalence test or direct timing contrast.",
      "transfers": [],
      "support": [
        {
          "source": "petre@1",
          "locator": "Results §3.5, Fig. 4, trained subgroup",
          "result": "ES −0.10 (95% CI −0.43 to 0.23), p=0.55.",
          "restriction": "No inference about intermediate spacing or individual recovery time."
        }
      ]
    },
    {
      "key": "resistance-first-dynamic-strength@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-sequence",
        "objective": "strength-development",
        "population": "healthy-adults",
        "experience": "mixed",
        "intervention": "same-session-strength-then-endurance",
        "comparator": "same-session-endurance-then-strength",
        "outcome": "lower-body-dynamic-strength",
        "horizon": "at-least-five-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "Resistance-first ordering yielded greater lower-body dynamic strength improvement in the pooled same-session comparisons.",
      "limitations": "Mostly recreational/untrained samples, varied modalities; not a race-specific performance or separate-day ordering result.",
      "quality": "low",
      "assessment": "Direct sequence contrast but limited dual-trained running applicability.",
      "transfers": [],
      "support": [
        {
          "source": "eddens-sequence@1",
          "locator": "Results, Fig. 2, lower-body dynamic strength",
          "result": "Weighted mean difference in percent change 6.91 percentage points (95% CI 1.96 to 11.87).",
          "restriction": "Only this outcome; no universal order."
        }
      ]
    },
    {
      "key": "high-load-running-economy@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "strength-running-economy",
        "objective": "running-economy-development",
        "population": "middle-and-long-distance-runners",
        "experience": "moderate-to-high-endurance-experience",
        "intervention": "high-load-strength-plus-running",
        "comparator": "running-with-no-or-low-dose-strength-control",
        "outcome": "measured-running-economy",
        "horizon": "six-to-twenty-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The pooled running-economy contrast favored the studied supplemental strength method over control.",
      "limitations": "Varied control conditions and lifting experience; speed-dependent tests; no individual conversion to race time.",
      "quality": "moderate",
      "assessment": "Publisher results and review certainty assessment; dual-trained marginal effect unknown. Horizon is review overall.",
      "transfers": [],
      "support": [
        {
          "source": "llanos-lagos-economy@1",
          "locator": "Results §3.4, Fig. 2",
          "result": "ES −0.266 (95% CI −0.516 to −0.015), p=0.039.",
          "restriction": "Negative effect favors lower measured running cost. Study prescriptions are not defaults."
        }
      ]
    },
    {
      "key": "combined-strength-running-economy@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "strength-running-economy",
        "objective": "running-economy-development",
        "population": "middle-and-long-distance-runners",
        "experience": "moderate-to-high-endurance-experience",
        "intervention": "combined-strength-methods-plus-running",
        "comparator": "running-with-no-or-low-dose-strength-control",
        "outcome": "measured-running-economy",
        "horizon": "six-to-twenty-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The pooled running-economy contrast favored the studied supplemental strength method over control.",
      "limitations": "Heterogeneity and outlier sensitivity, distinct method combinations; no head-to-head superiority.",
      "quality": "low",
      "assessment": "Publisher results and review certainty assessment; dual-trained marginal effect unknown. Horizon is review overall.",
      "transfers": [],
      "support": [
        {
          "source": "llanos-lagos-economy@1",
          "locator": "Results §3.4, Fig. 3",
          "result": "ES −0.647 (95% CI −1.140 to −0.154); outlier-excluded ES −0.426 (−0.768 to −0.083).",
          "restriction": "Negative effect favors lower measured running cost. Study prescriptions are not defaults."
        }
      ]
    },
    {
      "key": "high-load-running-performance@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "strength-running-performance",
        "objective": "running-performance-development",
        "population": "middle-and-long-distance-runners",
        "experience": "moderate-to-high-endurance-experience",
        "intervention": "high-load-strength-plus-running",
        "comparator": "running-with-no-or-low-dose-strength-control",
        "outcome": "time-trial-or-time-to-exhaustion",
        "horizon": "six-to-forty-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The pooled running-performance contrast favored the studied supplemental strength method over control.",
      "limitations": "Combines time trials and TTE; no individual race-time percentage or optimal additional strength dose.",
      "quality": "moderate",
      "assessment": "Mixed laboratory/field outcomes and overlapping primary studies; hybrid transfer not approved. Horizon is review overall.",
      "transfers": [],
      "support": [
        {
          "source": "llanos-lagos-performance@1",
          "locator": "Results, Running Performance, Fig. 6",
          "result": "ES −0.469 (95% CI −0.872 to −0.066), p=0.029.",
          "restriction": "Negative effects favor supplemental strength; no predicted individual race-time change."
        }
      ]
    },
    {
      "key": "combined-strength-running-performance@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "strength-running-performance",
        "objective": "running-performance-development",
        "population": "middle-and-long-distance-runners",
        "experience": "moderate-to-high-endurance-experience",
        "intervention": "combined-strength-methods-plus-running",
        "comparator": "running-with-no-or-low-dose-strength-control",
        "outcome": "time-trial-or-time-to-exhaustion",
        "horizon": "six-to-forty-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The pooled running-performance contrast favored the studied supplemental strength method over control.",
      "limitations": "Heterogeneous combined methods; no direct proof of superiority to high-load-only training.",
      "quality": "low",
      "assessment": "Mixed laboratory/field outcomes and overlapping primary studies; hybrid transfer not approved. Horizon is review overall.",
      "transfers": [],
      "support": [
        {
          "source": "llanos-lagos-performance@1",
          "locator": "Results, Running Performance, Fig. 6",
          "result": "ES −1.035 (95% CI −1.967 to −0.103), I²=67.475%.",
          "restriction": "Negative effects favor supplemental strength; no predicted individual race-time change."
        }
      ]
    },
    {
      "key": "strength-running-economy-durability@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "strength-running-economy",
        "objective": "running-economy-development",
        "population": "well-trained-male-runners",
        "experience": "trained-endurance",
        "intervention": "maximal-strength-and-plyometrics-plus-habitual-running",
        "comparator": "habitual-running-only",
        "outcome": "running-economy-at-ninety-minutes",
        "horizon": "ten-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "In the trial, the supplemented group improved oxygen cost at the end of the prolonged run relative to running-only control.",
      "limitations": "Male runners, 14 per group; abstract-level extraction; combined stimulus; baseline strength training and CIs require full-text confirmation.",
      "quality": "low",
      "assessment": "Randomized comparison and explicit time-specific outcome; no independent full-text or rights review.",
      "transfers": [],
      "support": [
        {
          "source": "zanini-durability@1",
          "locator": "Abstract Results, 90-min running-economy comparison",
          "result": "Change −2.1% vs +0.6%, p=0.04; group×training×run-time p=0.003, partial eta-squared 0.13.",
          "restriction": "Measured laboratory oxygen cost at 90 minutes; not race performance or a universal training dose."
        }
      ]
    },
    {
      "key": "concurrent-trained-endurance-vo2max@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "scope": {
        "question": "concurrent-aerobic-capacity",
        "objective": "aerobic-capacity-development",
        "population": "healthy-adults-aged-18-50",
        "experience": "trained-endurance",
        "intervention": "concurrent-strength-and-endurance",
        "comparator": "endurance-only",
        "outcome": "vo2max",
        "horizon": "at-least-four-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The trained endurance subgroup did not show detectably smaller VO2max gains with concurrent versus endurance-only training.",
      "limitations": "Mixed aerobic modes and sparse high-level evidence; no equivalence test; not running economy, race time or retention.",
      "quality": "low",
      "assessment": "Outcome-specific comparison with moderate imprecision; study-level training-status classification.",
      "transfers": [],
      "support": [
        {
          "source": "huiberts@1",
          "locator": "Results §3.5, Fig. 6, trained endurance subgroup",
          "result": "SMD 0.18 (95% CI −0.02 to 0.38); p=0.08.",
          "restriction": "Trained endurance subgroup only; no inference about all performance qualities."
        }
      ]
    }
  ],
  "relations": [
    {
      "key": "timing-trained-separate-context@1",
      "kind": "qualifies",
      "subject": "separate-session-trained-lower-body-strength@1",
      "object": "same-session-trained-lower-body-strength@1",
      "reason": "Same review, distinct timing strata and common comparator type. Separate-session estimate is uncertain; this does not estimate a randomized direct timing contrast or establish a minimum gap."
    },
    {
      "key": "training-status-moderation-context@1",
      "kind": "qualifies",
      "subject": "concurrent-strength-experience-moderation@1",
      "object": "trained-lower-body-strength@1",
      "reason": "Huiberts did not detect a strength-status interaction; Petré reports a within-trained program comparison. Different estimands and classification, overlapping literature; neither logically refutes the other."
    },
    {
      "key": "fiber-vs-whole-muscle-context@1",
      "kind": "qualifies",
      "subject": "pooled-concurrent-fiber-hypertrophy@1",
      "object": "pooled-concurrent-whole-muscle-hypertrophy@1",
      "reason": "Different tissue measurement levels and partially overlapping research; do not transfer whole-muscle estimate to fibers or vice versa."
    }
  ],
  "methods": [
    {
      "key": "priority-aware-concurrent-calendar@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "question": "concurrent-timing",
      "description": "Compare feasible weekly schedules with explicit key-session priorities and actual athlete responses; consider separation or ordering changes before altering protected dose.",
      "provenance": "Research Packet 003 CT-P02 v0.2; original candidate programming method, not empirical finding.",
      "tradeoffs": "Spacing, adherence and other priorities can conflict; no universal interval; direct timing evidence limited.",
      "claims": [
        "same-session-trained-lower-body-strength@1",
        "separate-session-trained-lower-body-strength@1",
        "resistance-first-dynamic-strength@1"
      ]
    },
    {
      "key": "existing-strength-stimulus-for-running@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "question": "strength-running-economy",
      "description": "Map existing resistance training to running and strength objectives before adding supplemental work; consider retaining suitable strength exposure or replacing less important work.",
      "provenance": "Research Packet 003 CT-P04; original candidate programming method, not empirical finding.",
      "tradeoffs": "Additional work may not improve running in already strong athletes and may compromise session quality; exact doses unvalidated.",
      "claims": [
        "high-load-running-economy@1",
        "high-load-running-performance@1",
        "combined-strength-running-performance@1"
      ]
    },
    {
      "key": "joint-priority-block-review@1",
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted extraction, Research Packet 003)",
      "status": "pending",
      "approval": null,
      "question": "concurrent-strength",
      "description": "Review both disciplines and secondary commitments within a shared block; compare feasible alternatives, disclose uncertainty and require athlete approval for objective changes.",
      "provenance": "Research Packet 003 HP-P01 and CT-P05; original candidate programming method, not empirical finding.",
      "tradeoffs": "No demonstrated optimal priority trajectory or adaptation algorithm; needs athlete preferences, nutrition context and explicit secondary protection.",
      "claims": [
        "pooled-concurrent-strength@1",
        "trained-lower-body-strength@1",
        "concurrent-trained-endurance-vo2max@1",
        "high-load-running-performance@1"
      ]
    }
  ]
}
```

**Integration note:** exact `Scope` terms are draft vocabulary; for example, `moderate-to-high-endurance-experience` does not imply resistance training status. `concurrent-versus-strength-only-trained-strength-subgroup` represents a moderator comparison, not a workout prescription. Cross-question links in a method's claims are permitted by the previously inspected J1 model; relations must remain within a question. Verify this against current repository code before integration. This fragment contains 6 source records, 15 claim records, 6 question records, 3 qualification edges and 3 method records; none eligible. JSON parsing, key patterns, old-key collision checks, known-reference checks and relation question consistency were performed against the known manifest keys and both local predecessors. Actual loader, registry digest, current repository staging state and formal retrieval tests remain outstanding. Do not register or merge as part of this research task.

## 6. Evaluation cases

Synthetic cases test policy semantics, scope boundaries, tradeoff handling, feasibility and authority; they are not a substitute for training outcome trials. Qualitative conditions such as repeated comparable poor sessions are fixture inputs, not production thresholds. Record each fixture's as-of date, approved block, context, actual exposure and missingness, goals, constraints, evidence status and versions, acceptable alternatives, forbidden decisions and rationale requirements. All fixture evidence must remain in the synthetic namespace.

| ID | Synthetic observations / perturbation | Acceptable behavior | Forbidden behavior / required rationale |
|---|---|---|---|
| HY-A01 | Strength and running both improving at stable achieved dose; feedback favorable. | Hold both or justify a phase-specific bounded change. | Mandatory increases in either modality; claim additional work is required. CT-P05 / RT-P02. |
| HY-A02 | Squat quality repeatedly poor after interval running; comparable presses stable; schedule alternatives available. | Move one key session while preserving exposure; review subsequent outcomes; consider other causes. | Diagnose interference from temporal correlation; reduce all lifting or all running. CT-P02. |
| HY-A03 | Same A02 history, but one poor squat only and unclear device data. | Hold, seek feedback or compare history. | Apply a deterministic fatigue threshold or change block based solely on the isolated observation. |
| HY-A04 | Only one shared slot for strength and running; squat development ranked first. | Propose lifting first or alternative feasible arrangement; disclose potential tradeoff. | Declare combined training invalid because it violates an invented spacing interval. C22 scope restricted. |
| HY-A05 | Identical slots to A04, but upcoming race and quality run now first priority. | Protect run quality, consider run-first or schedule revision. | Copy strength-first rule without regard to goal; claim chronic run-first superiority. |
| HY-A06 | Upper-body press plus easy run feasible; athlete has tolerated combination. | Allow combination when constraints pass; monitor. | Apply same prohibition as heavy squats and demanding intervals; claim upper body immune. |
| HY-A07 | Athlete already performs substantial lower-body heavy training; asks to add a runner-strength template. | Map existing work; retain or substitute if justified, rather than blindly append. | Assume supplemental-strength trials establish marginal benefit in already strong athlete. CT-P04. |
| HY-A08 | Strength-emphasis block with two easy runs, but athlete's protected target is half-marathon performance and habitual long runs/threshold work omitted. | Flag maintenance uncertainty; review goal-specific exposure and feasible alternatives. | Equate number of runs or VO2max estimate with endurance maintenance. CT-P01. |
| HY-A09 | Endurance-emphasis block with stable race metrics but loss of standardized squat strength. | Flag secondary outcome conflict; review retained dose and key run burden; propose approved revision if necessary. | Remove all lifting or silently accept strength loss despite protected objective. |
| HY-A10 | Athlete has improving endurance and asks to replace all runs with cycling solely to maximize strength. | Discuss running specificity, tradeoffs and goal change; allow appropriate cross-training only with consent. | Treat cycling VO2peak or duration as equivalent race preparation. CT-P03. |
| HY-A11 | Both domain progression rules propose increases in same week; recovery/time constraints binding. | Evaluate joint feasibility; hold one, redistribute, or compare alternatives. | Independently concatenate two plans or assume separate pass implies joint pass. |
| HY-A12 | Both domains progressing; athlete has ample time, tolerable exposure, no conflicting restrictions, and both increases are justified. | Consider joint increase only under reviewed constraints; holding also permissible. | Invent a universal prohibition on any simultaneous progression or numerical increment. |
| HY-A13 | Pace slower on hotter/hillier route, HR unreliable; strength steady. | Mark comparison as uncertain; ask about context; retain safe plan. | Diagnose aerobic regression or treat pace/HR as direct RE. |
| HY-A14 | Fatigue and poorer runs/strength coincide with newly restrictive intake and added double sessions. | Ask about intake coverage, schedule and symptoms; defer unnecessary escalation; consider referral if concerning. | Diagnose REDs, prescribe a calorie deficit or universal calorie compensation from wearable burn. CT-P06. |
| HY-A15 | Identical A14 training history but nutrition missing, no red flags, usual performance stable. | Keep nutrition unknown; feasible training may continue with optional prompts. | Treat unlogged meals as zero intake or require comprehensive food logging for every workout. |
| HY-A16 | Long run moved to Sunday; Monday protected heavy lower-body session already approved. | Check adjacent-week schedule and time availability; review potential conflict. | Validate only within the seven-day window or silently shift approved Monday session. |
| HY-A17 | Athlete misses a threshold run just before race taper; strength work still scheduled. | Preserve event protections, record missed work, consider only feasible reviewed alternative. | Automatic catch-up interval session or unrestricted increase in lifting volume. |
| HY-A18 | Athlete chooses simultaneous max-strength and race peaks but available slots cannot satisfy agreed protected sessions. | Present named infeasibility and priority alternatives; require explicit objective decision. | Fabricate a jointly optimal plan or silently delete secondary sessions. HP-P01. |
| HY-A19 | Retrieval yields pooled maximal-strength claim and a trained lower-body qualification; requested explanation concerns running effects on press. | Surface scope gap and indirect applicability; use only labeled scheduling judgment. | Cite lower-body effect as direct evidence for press or ignore relevant qualification. |
| HY-A20 | Strength-running-economy result retrieved; user asks for expected 10-km improvement. | Distinguish RE and running performance; no individual conversion or guaranteed benefit. | Convert SMD to seconds or promise a fixed percentage race improvement. |
| HY-A21 | Female athlete and male athlete have identical training observations and priorities. | Same feasible decisions unless relevant individual context justifies change; communicate subgroup uncertainty if asked. | Sex-only automatic escalation, immunity assumption, or sex-specific numerical constraint. |
| HY-A22 | Athlete's new pain restriction conflicts with a pending heavy lower-body session and quality run. | Reject stale/infeasible candidate, request qualified evaluation if appropriate, offer safe alternatives subject to approval. | Override restriction or authorize a new plan without review. |
| HY-A23 | All relevant records in J1 are pending; proposed move is based on athlete-reported poor quality and availability. | A rules/method-only proposal may state judgment and evidence gap if permissible. | Render pending claims as approved empirical rationale or fake human approval. |
| HY-A24 | A claim supporting a pending proposal is later withdrawn. | Keep historical pin, flag/review dependent proposal, block new approval relying on withdrawn evidence. | Rewrite historical rationale or continue silently with invalid claim. |

**Evaluation separation:** run these cases against planner, persistence and explanation independently. Pre-register expected admissible alternatives and disallowed changes. Use paired perturbations (priority, completeness, modality, nutrition, phase and constraints) to test whether a decision changes only for relevant reasons. Measure evidence entailment separately from feasibility. Longitudinal pilot comparisons evaluate actual joint outcomes, not only code conformance. No new quantitative acceptance threshold or production rule parameter is specified here.

## 7. Research backlog

### 7.1 Revised integrated research sequence

Packet 001 and 002 retain their contents and scientific-review blockers. Their resistance-specific P0 priorities are recontextualized rather than deleted. Priority now denotes importance to credible integrated hybrid coaching, not academic importance or clinical severity. P0 is central to early joint planning, P1 extends adaptation and validation, P2 is later sophistication. All future packets retain the same eight-section structure: focused appraisal, empirical claims with exact locators, candidate policies, longitudinal implications, pending J1 records, synthetic cases, backlog and review checklist. Complete review and record gaps before promoting claims; do not require every scientific gap to be solved before investigating the next dependency.

| Packet / priority | Focused research questions | Main deliverables and dependencies | Status |
|---|---|---|---|
| 001 — retained | RT-01, LP-01: load/repetition progression, strength periodization, context for maintenance. | Review existing extractions and retain strength-method boundaries. | Staged/reviewed for architectural relevance per user; independent scientific approval not established. |
| 002 — retained | RT-02: habitual volume, fixed escalation, cumulative dose, feedback-adjustment gap. | RT-P02 v0.2; integrate with joint volume review in Packet 003. | Staged/reviewed for architectural relevance per user; scientific verification outstanding. |
| 003 — P0 | CT-01/02/03: bidirectional adaptations, scheduling, dose/modality, secondary outcomes. | Candidate CT-P01–06 and HP-P01; empirical boundary and screening queue. | This packet, pending. |
| 004 — P0 | NU-01/02/03: energy availability/balance and safe body-composition goals; carbohydrate availability/fueling across session types and double sessions; protein for concurrent athletes. | Direct concurrent/nutrition trials vs single-sport transfers; feasibility and escalation guard, dietary strategy alternatives, uncertainty and referral. Scope each subquestion separately within packet; no wearable-based calorie algorithm. | Next recommended. |
| 005 — P0 | EN-01/02: running development for experienced recreational athletes; intensity distribution, threshold/interval/long-run stimulus, baseline-relative volume change and adherence. | Running progression policies with lifting interaction, race-specific measures and modality specificity; distinguish elite/endurance-only transfer. | Queued. |
| 006 — P0 | HP-01/02/03: joint multiweek priorities, maintenance in both directions, coordinated deload/taper and assessment planning. | Balanced vs emphasis alternatives; longitudinal constraints, event conflict, phase-aware progression; appraise direct periodization and taper trials. Uses Packets 001–005. | Queued. |
| 007 — P1 | NU-04/05: individual energy expenditure from intake/weight observations, wearable validity, nutrition adaptation with changing training. | Identifiability, observation noise and missingness; calibrated prediction and uncertainty; separate estimation from dietary recommendation; evaluate against simple baselines. | Queued; safety context from 004 remains P0. |
| 008 — P1 | RE-01/02 and EV-01: integrated recovery interpretation and autoregulation; effort, sleep, HRV, HR, training/food/weight evidence, alternative explanations. | Review policy interventions vs association, measurement comparability, decision uncertainty, no single readiness score. Use existing RT-P02 evidence and Packet 004–007. | Queued. |
| 009 — P1 | EV-02/03: individualized adaptation and prospective multi-objective evaluation. | Within-athlete designs, noise/carryover, policy comparisons, causal limitations, held-out cases, calibration and adherence; evaluate improvement beyond fixed-program and simple progression baselines. | Queued. |
| 010 — P2 | HP/EV extensions: interruptions, complex event conflicts, longer-term adherence and preference evolution, only if evidence/observational coverage warrants. | Refine constraints and model complexity based on measured failure, not novelty. | Queued. |

Packet 004 should not be an attempt to solve all sports nutrition or infer a personalized caloric prescription at once. Start with the safety/energy availability question and session fueling as the main immediate joint-planning dependencies; separate protein and body-composition comparisons within the review. Packet 007 is the individual estimation workstream, not a reason to defer safe fueling context in 004. This sequencing is a research recommendation and can be revised with the user.

### 7.2 Packet 003 outstanding questions and appraisal queue

| ID | Priority | Unresolved question / concrete next action |
|---|---|---|
| CT-01a | P0 | Verify Schumann/Petré/Huiberts inclusion, overlapping studies and classification definitions; extract actual trained and upper-body estimates with intervals, subgroup interaction tests and dose coverage. Do not sum review effects. |
| CT-01b | P0 | Verify Gomes 2025 full protocol, actual running volume/intensity and RT dose, participant baseline experience in both disciplines, group-by-time contrasts and confidence intervals; cross-check Gomes 2026 cohort and publication version. |
| CT-01c | P1 | Audit Lundberg biopsy sampling, type I running subgroup and modality interaction; distinguish whole-muscle and fiber outcomes and overlapping protocols. |
| CT-02a | P0 | Full appraisal of Robineau timing trial, including statistical method and direct comparisons; inspect Eddens study composition, newer sequence evidence and acute Doma studies. Seek direct running-specific order/spacing comparisons with priority session quality. |
| CT-03a | P0 | Seek running-dose trials in trained lifters with matched RT and realistic easy/long/quality intensity distributions. Audit Wilson correlations, Chen network transitivity and Dolan cycling protocol. No universal dose or intensity ranking now. |
| CT-04a | P0 | Verify Llanos-Lagos high-load and combined meta-analysis extraction, risk of bias, comparators, outcome dependence and overlapping trials; separate RE, TTE and actual race/time-trial outcomes. |
| CT-04b | P0 | Extract Støren, Trowell, Zanini primary intervention dose, baseline strength status, realized running exposure, adherence, effect intervals and intake control; seek trials in already strength-trained runners to identify marginal benefit. |
| CT-04c | P1 | Investigate durability and event-specific outcomes; avoid equating steady-state oxygen cost, VO2max and race performance. Zanini 2026 association is a lead, not dose evidence. |
| HP-01a | P0 | Seek controlled balanced-vs-emphasis block comparisons and outcome-specific maintenance in dual-trained athletes; distinguish prior exposure, trial horizon, event timing and actual adaptation. |
| NU-01 | P0 | Appraise relevant nutrition interventions and health constraints; determine which moderators were actually measured in CT trials; no causal nutrition interaction assumed. |
| EV-02a | P1 | Find studies testing feedback-based concurrent scheduling/dose decisions; if absent, compare candidate policies prospectively with matched attention and explicit joint outcomes. |
| REVIEW-03 | P0 | Validate draft source metadata, exact scopes, access, publication/rights status and relation meaning; review actual repository staging state and loader. |

## 8. Human review checklist

### Scientific extraction and interpretation

- [ ] Check exact bibliographic records, publication versions, corrections/retractions, rights and permitted use for every admitted source. Confirm author/title/date metadata and accessible article edition; no rights or approval inferred from open access.
- [ ] Re-extract Schumann §3.2–3.4 and supplements, including hypertrophy CI and influential-study sensitivity; ensure maximal-strength, power and hypertrophy claims stay separate. Confirm no null-result equivalence claim.
- [ ] Verify Petré Fig. 2–4 subgroup intervals and training classification, prescribed running/cycling inclusion criteria, trial duration and timing bins; verify no direct timing or training-status interaction is inferred merely from separate significance results.
- [ ] Review Huiberts §§3.4–3.5 and supplementary upper-body estimates, subgroup tests, sex sample composition, risk-of-bias and moderation definitions. Check overlap with Schumann and Petré; avoid sex-only rule and false contradiction. Verify trained VO2max comparison is against ET-only.
- [ ] Check Lundberg fiber-level model, rounded upper CI, number of running studies, biopsy method, moderator tests and shared protocol with Schumann. Confirm no direct whole-muscle or cycling superiority conclusion.
- [ ] Verify Eddens lower-body dynamic strength outcome and units, sample experience, modality and comparator; compare newer umbrella review and other sequence syntheses only after study overlap and methods review.
- [ ] Obtain full primary Gomes, Robineau, Doma, Dolan, Støren, Trowell and Zanini reports as appropriate. Extract direct contrasts and intervals, starting/realized doses, training experience in both domains, adherence and nutrition controls. Screen 2026 Gomes cohort overlap and Ferraro-Farro erratum before adding claims. Do not treat abstract-only arm changes as between-group effects.
- [ ] Check Llanos-Lagos 2024a §3.4, Fig. 2/3 and 2024b Fig. 6: sign, CI, comparator, measurement speed and durations, certainty and outlier sensitivity, combined-vs-single interpretation. Audit overlap across reviews and outcome dependence; extract strength experience and running dose. Do not convert effects to race-time predictions.
- [ ] Verify Zanini 90-min RE interaction and contrasts, TTE contrast, sample flow and version of record; extract uncertainty intervals. Distinguish late-exercise oxygen cost from real race performance and avoid count of thesis as replication.
- [ ] Review Spiering general-population maintenance limitations and athlete transfer; no exact session minimum. Confirm that nutrition context N01 is consensus-based and not a direct intervention claim; reserve full appraisal for Packet 004.
- [ ] Document each study's PICO, bias, precision, directness, study overlap and any unresolved source locator; agree provisional confidence ratings and do not approve by default.

### Programming and scientific evaluation

- [ ] Agree on the product's multi-objective outcome representation, secondary protection semantics, priorities and how to display uncertainty rather than a single readiness or weighted score. Define what is feasible, not an arbitrary scalar utility.
- [ ] Review CT-P01 through CT-P06 and HP-P01; identify each empirical premise versus method, athlete observation, preference and safeguard. No numerical spacing, progression, dose, recovery or nutrition threshold added by this packet.
- [ ] Decide whether to retain priority-first sequencing and hold-productive-dose as candidate defaults; allow exceptions and distinguish from proven chronic optimality. Review interaction with RT-P01, RT-P02 v0.2, event protection and actual vs prescribed exposure.
- [ ] Specify qualitative definitions and later validation plan for priority session, overlapping demand, representative exposure, meaningful change, observation coverage, tolerance, schedule feasibility and secondary goal conflict. Do not silently reuse synthetic fixture bounds as operational values.
- [ ] Review clinical/nutrition safeguard wording with qualified professionals, including referral and sensitive-data boundaries. Do not diagnose from logs, recommend unsafe weight loss or treat wearable estimates as reliable expenditure.
- [ ] Review paired cases, allowed alternatives and prohibited rationales; add held-out cases for missing run data, competing goals, changing priorities, cross-week timing, withdrawal, nutrition uncertainty and scope transfer. Enforce approval and historical lineage.
- [ ] Design prospective policy evaluation with fixed and simple joint-program comparators, predeclared joint outcomes, adherence, adverse symptoms, time cost and uncertainty; address carryover/confounding. Golden-case success does not establish coaching efficacy.
- [ ] Confirm revised roadmap and order of Packet 004 onward; preserve Packets 001/002 and their unresolved review tasks.

### Repository and J1 integration (future authorized work only)

- [ ] Verify current J1 schema and exact source/claim keys against the actual staging branch and releases; resolve any collisions without overwriting immutable history. Proposed new vocabulary is not an approved transfer mapping. Check moderator and duration scopes against the code's exact-match retrieval semantics.
- [ ] Merge candidate fragment only in a draft review context; run actual strict loader, graph validation, release registry/digest and eligibility/retrieval checks. No pending record can become an operational empirical assertion; no implicit approvals or pending supersession edges.
- [ ] Ensure citations use exact result locators and preserve material qualification/conflict context, including scope mismatches. Review author/edition, correction and rights records and approval attestations before any release.
- [ ] Verify explicit athlete approval, no unapproved prescription change or provider write, and preservation of historical rationale under future corrections/withdrawals. No repository files are to be modified by this packet.

**Handoff disposition:** Packet 003 is a research-library deliverable, not an implementation specification or operational evidence release. The proposed shift toward integrated optimization, conditional scheduling, qualitative dose review and revised sequence is deliberate programming/product judgment. Limitations include incomplete primary full texts and direct contrasts, limited dual-experienced populations, no systematic search or independent extraction, no definitive nutrition modifier appraisal, and no repository-loader execution. All new claims and methods remain pending independent human review. No prior packet or software repository was modified. The next technical session should treat every numerical study descriptor as evidence context only, never a prescription parameter.
