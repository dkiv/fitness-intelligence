# Fitness Intelligence — J3A.2
## Multiweek block construction and protected secondary outcomes

**Revision:** 0.1 · **Date:** 2026-11-25 · **Status:** AI-assisted scientific appraisal and candidate programming methodology. All evidence, transfers, parameters and methods remain pending independent human review. No operational authorization.

**Predecessors:** J3A.1 and J3B.1 (J3-M01a–c). **Proposed method family:** J3-M02, a review identifier, not a registered J1 key. J3-M02 constructs the block that J3-M01 consumes. Running-specific progression methodology is a separate subsequent capability.

## 1. Executive summary

Construct a hybrid block around a ranked set of measurable outcomes, the athlete's relevant actual training history, and a feasible calendar. Do not start from a universal weekly template, a fixed fraction of maximal volume, or an inferred recovery score. A strength-emphasis block can retain running work; a running-emphasis block can retain meaningful lifting; a balanced block can develop both without requiring equal time, sets or physiological adaptation. An emphasis is an allocation decision, not a biological phase.

Six existing publications were selected: Moesgaard (resistance periodization), Micke (concentrated versus distributed conditioning), Rønnestad/Nymark/Raastad (in-season strength maintenance), Bickel (reduced-dose muscle retention), Hickson/Kanakis et al. (reduced endurance duration), and Huiberts (concurrent development). J3A.1's Petré appraisal is reused, not counted as an additional new appraisal. No new literature was added. Four selected publications were inspected beyond abstracts (publisher HTML for Micke/Huiberts, journal-text copy for Bickel, early journal-layout text copy for Rønnestad). Moesgaard and Hickson remain abstract-level checks; the Rønnestad copy requires final-version confirmation. The access distinctions matter for approval.

Main findings:

- Planned variation in resistance training is defensible for strength development; the existing Moesgaard estimates are supported at abstract level. Neither the trained-subgroup estimate nor the review as a whole establishes the best phase sequence or duration. The publisher's Crossmark record notes a table-format update; use the updated text for final review.
- Micke studied temporal organization of **conditioning**, not a controlled comparison of strength-emphasis and running-emphasis blocks. The reported deadlift model coefficient favors concentrated conditioning, but external lifting was not monitored, carryover is plausible and absence of detected conditioning differences is not equivalence or retention proof.
- Rønnestad's soccer study offers a relevant assigned-dose comparison. Weekly half-squat training was associated with a favorable descriptive retention pattern compared with alternate-week training. The latter group's reported half-squat decline is 10 ± 4% (mean ± SE). Frequency and total dose differed, and a clear direct strength-change contrast interval remains missing.
- Bickel's full text is available as a third-party journal-layout copy. Recently trained young adults receiving reduced doses retained elevated mean myofiber area relative to pretraining baseline, with age-dependent results. This cannot be converted into a one-ninth maintenance rule for experienced athletes, or into proof of exact retention of all acquired hypertrophy. Repeated strength assessments are additional exposure even in the detraining arm.
- Hickson shows why outcome specificity is essential: two reduced-duration groups reportedly retained VO2max, but the shorter-duration arm lost long-duration endurance. The abstract gives 139 to 123 minutes (authors describe ~10% decline); exact test conditions and uncertainty remain unverified.
- Huiberts reports heterogeneous concurrent development contrasts by outcome and training-status strata. Those contrasts are not maintenance trials or individual interference penalties. Avoid double counting shared trials with Petré/Schumann.

Recommendation: adopt a reviewable candidate block workflow with an initial six-week horizon (four to eight weeks reasonable for the first configuration), weekly intent and end-of-block comparable assessment, and an athlete-approved outcome protection contract. Select starting exposure from representative actual history; a productive familiar dose is a reasonable default. Numerical suggestions below are contextual programming choices, not scientific optima. A coach can choose them without accepting unresolved quantitative retention claims.

## 2. Selected coaching capability and scope

### 2.1 Repository and predecessor verification

Read-only `main` snapshot verified by comparing main against itself: [`1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c`](https://github.com/dkiv/fitness-intelligence/commit/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c), 2026-11-25. The [research index](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/README.md) includes Packet 009 and reports 58 questions, 81 source revisions, 106 claim revisions, four relations, 32 candidate methods, zero withdrawals, and 78 distinct DOIs. These counts are reported by the repository, not independently validated here. Packet 010 is described as next; it is not a prerequisite. No claim is made about separate staging branches or PRs beyond main's content.

Inspected exact [006 draft](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/drafts/006-evidence-additions.json), [003 draft](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/drafts/003-evidence-additions.json), [009 draft](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/drafts/009-evidence-additions.json), relevant sections of [006 archive](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/006-integrated-hybrid-periodization.md), [009 archive](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/009-individual-training-history.md) and [backlog](https://github.com/dkiv/fitness-intelligence/blob/1c5205dc8c5096e4612ef152f51b7bdabf1d4d9c/docs/research/research-backlog.md). Read the local predecessor Markdown deliverables. Planning architecture is reused from J3B.1's inspection of `training-plan-design.md`, `strength-analytics.md`, `endurance-recovery.md`, `adaptive-coaching-cycle.md` and `coaching-evaluation-design.md` at its prior pinned snapshot. Their implementation and changes since that snapshot have not been independently audited in this tranche. The exact registered `moesgaard@1` source object was not fetched; its key and claim links are established in J3A.1/Packet 001.

### 2.2 Capability contract

Given confirmed goals, priority order, time horizon, equipment and availability, restrictions, representative actual lifting/running history, and optional athlete feedback: propose a block archetype, starting exposures, named secondary outcome targets, weekly intent, boundaries, assessment opportunities and alternative feasible calendars. Show what is preserved, what is reduced, why, what remains uncertain, and when review is required. No autonomous plan change or clinical advice. No assumption that a documented session is performed.

This tranche consolidates backlog A1, A7, parts of A4/A15/A16 and A20/A21/A22. A5/A6 (running development/intensity), A8 (nutrition), A9/A13 (measurement and adherence), A10 (recovery), and taper/return-to-training remain partial dependencies or separate tranches. It extends HP-P01–05/09, CT-P01/02/05, IA-P01–06. Do not mark these entire priorities resolved. All exact method/claim links remain pending.

### 2.3 Selection rationale

| Publication | Decision served | Why selected / limitation |
|---|---|---|
| Moesgaard | Whether planned variation is defensible | Direct to resistance periodization, indirect to hybrid blocks; abstract-level access |
| Micke | Can concentration/distribution matter in trained mixed-modal athletes? | Direct mixed-modal comparison, but not controlled lifting or race outcome |
| Rønnestad soccer | Retain meaningful lower-body strength during a competing sport | Actual reduced frequency and cumulative dose contrast; small professional male sample |
| Bickel | Distinguish hypertrophy from strength retention | Reduced-dose randomized maintenance with tissue measurement; recently trained adults |
| Hickson duration | Protect endurance quality rather than just aerobic capacity | Direct duration manipulation; small induced-training sample, no race endpoint |
| Huiberts | Coordinate competing development outcomes | Separates strength/endurance training status and outcomes; study-level synthesis |

Defer hockey (sport-specific, abstract access), cycling strength retention (related but redundant with soccer for initial decision), flexible DUP (not essential for initial structure), Mølmen (endurance block optimization beyond this tranche), Hickson frequency/intensity (useful when selecting actual endurance progression), taper, detraining, and running-economy supplements. No universal maintenance fractions are needed to start. Packet 009 measurement claims are reused as pending methodological context; no new source appraisal is claimed for them.

## 3. Original-source verification and scientific appraisal

### 3.0 Access, provenance and review standards

Sources below are the original published reports or copies of those reports, not summaries of summaries. Verification was targeted to the listed sections and contrasts; full-text access does not mean exhaustive reanalysis or complete supplement verification. No participant-level reanalysis, original forest plot reconstruction, systematic review overlap matrix or independent human attestation was performed. Publication identities and DOI records were checked on 2026-11-25. Except for the Moesgaard Crossmark check, authoritative correction/retraction checks remain incomplete; do not interpret a lack of visible notice as a negative audit. Third-party copies are for factual verification only; do not reproduce figures, tables or program text. Verify licensing and the exact final version before human approval. Numerical values below are factual summaries, not prescriptions.

### 3.1 Moesgaard et al. — planned variation of resistance-training volume and intensity

**Source:** `moesgaard@1` (registered screening source, exact metadata not independently fetched). Moesgaard L, Beck MM, Christiansen L, Aagaard P, Lundbye-Jensen J. *Sports Med.* 2022;52:1647–1666. DOI [10.1007/s40279-021-01636-1](https://doi.org/10.1007/s40279-021-01636-1). Original [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/35044672/) and [university bibliographic record](https://researchprofiles.ku.dk/en/publications/effects-of-periodization-on-strength-and-muscle-hypertrophy-in-vo/) inspected. Online 19 January 2022; July issue. Publisher full article could not be fetched. [Crossmark](https://crossmark.crossref.org/dialog/?doi=10.1007%2Fs40279-021-01636-1) reported current document and a 4 February 2022 update for table formatting. Not a verified substantive correction. Rights: publisher exclusive license reported by university; factual summaries only.

**Design and comparator:** 35 eligible studies across the review, not 35 independent studies per contrast. Random-effects inverse-variance pooling comparing volume-equated periodized versus nonperiodized training, and linear versus undulating programs. Subgroup by training experience. The equality condition is study-defined pre/post volume matching, not proven equality of realized effort, specific heavy work, completed repetitions or mechanical exposure. Full participant counts per contrast, allocation, duration, adherence, coding of volume and overlap are not accessible from the abstract. Need Methods, study characteristics, primary forest plots, moderator interaction and sensitivity results from updated paper.

**Claims and results:**

| Existing claim | Original extraction | Verified abstract result | Disposition |
|---|---|---|---|
| `periodized-vs-constant-strength@1` | Strength estimate favors periodized, ES 0.31 (95% CI 0.04–0.57) | Same; p=0.02 | Retain numerical extraction as pending; full-text/source review required |
| `undulating-trained-strength@1` | Trained subgroup ES 0.61 (95% CI 0.00–1.22) | Same; p=0.05; untrained ES 0.06 (−0.20–0.31); overall LP/UP ES 0.31 (0.02–0.61) | Restrict to subgroup estimate; no established trained-specific superiority absent interaction verification |

Hypertrophy contrasts periodized/nonperiodized ES 0.13 (−0.10–0.36), undulating/linear ES 0.05 (−0.20–0.29). These are not equivalence tests. No new J1 hypertrophy claim proposed; enough for a scope warning. Do not infer a mechanism or a phase sequence from these aggregate estimates. Specificity to 1RM testing could partly explain results; cannot distinguish from other explanations without primary studies. No exact block duration or hybrid-transfer claim supported.

**Coaching consequence:** use planned variation in workload and task specificity when it advances an explicit goal, but a stable familiar pattern is reasonable during maintenance. A six-week plan with weekly intents is a product/programming choice independent of accepting the magnitude of the periodization estimate. Full-source verification and actual dose/interaction check required before scientific approval; no need to defer ordinary structured planning while these are unresolved.

### 3.2 Micke et al. — timing of mixed-modal conditioning

**Source:** `micke-hift-block@1`. Micke F, Huelle J, D’Hulst G, Isenmann E, Geisler S, Held S. *Front Physiol.* 2026;17:1810477. DOI [10.3389/fphys.2026.1810477](https://doi.org/10.3389/fphys.2026.1810477). [Publisher article](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2026.1810477/full), [PubMed](https://pubmed.ncbi.nlm.nih.gov/42245829/), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13229720/). Publisher and PubMed publication date 20 May 2026 (DOI resolver header has displayed a conflicting 19 May; use article's explicit publication date pending metadata audit). Publisher CC BY; confirm rights and notice status. Inspect Methods 2.1–2.3, 2.6, Results 3.1/Table 1, Fig. 1 and discussion. Supplement and exact participant-level realized strength exposure remain unchecked.

**Population and design:** 20 experienced HIFT athletes completed randomized two-period crossover; mean age 34.5 ± 9.8 y, experience 5.8 ± 3.2 y (SD). Eligibility included at least one year of training/competition and at least five weekly sessions over the prior three months. Sequence allocation, sex-specific counts and exclusions should be confirmed in full participant flow. Each intervention lasted six weeks, separated by four days of deload, midtesting and three days recovery. Such a washout may dissipate some fatigue but cannot erase chronic adaptation. Tests at similar times/conditions, requested 72 hours without intense training.

**Exposure:** 5 assigned conditioning sessions/week (3 MetCon and 2 runs) in both conditions. Distributed: 3 high-intensity and 2 low-intensity sessions each week. Concentrated: two three-week cycles of 5 high-intensity in first week, then 2 high/3 low in each subsequent week. Both schedules assign 18 high and 12 low sessions across six weeks. Intensity categories used session RPE criteria (high ≥8, low <5; low running RPE 2–4); these are protocol parameters, not general training zones. An identical separate lifting plan was supplied but adherence to actual lifting was not monitored. Assigned conditioning sessions and realized total training demand cannot be equated. Minimum 80% assigned-session adherence required for analysis; achieved dose and compliance distribution not extracted here. No claim of complete realized dose matching.

**Claim `hift-conditioning-block-deadlift@1`:** original assertion that deadlift 1RM change favored concentration, d=0.85, p=0.018. Verified Results §3.1/Table 1: adjusted intervention coefficient +5.53 kg, SE 2.11 kg, p=0.018, d=0.85. A simple normal approximation would be +1.39 to +9.67 kg, but this is **not** the study's exact interval (degrees of freedom/model covariance not extracted); do not insert it into J1. Preserve beta, SE and reported p. Other outcomes include IMTP +176.08 N (SE 80.87, p=0.038) and combined strength total +8.64 kg (SE 3.71, p=0.027); conditioning outcomes not significantly different, not a noninferiority result. Step-test WOD had a sequence effect. Outcome multiplicity, small sample, carryover, possible baseline and external training differences limit confidence. The authors' acute CMJ change does not prove a necessary functional-overreaching mechanism.

**Disposition:** revise before review to record the model estimate and clarify the intervention. Keep low confidence; not a direct test of strength-versus-running emphasis. No justification to copy five demanding sessions in one week, schedule functional overreaching, or promise preserved running performance. It makes variable conditioning organization a feasible option, not a preferred default. A balanced weekly pattern is equally available as a programming judgment.

### 3.3 Rønnestad, Nymark & Raastad — professional soccer strength maintenance

**Source:** `ronnestad-soccer-maintenance@1`. *J Strength Cond Res.* 2011;25:2653–2660. DOI [10.1519/JSC.0b013e31822dcd96](https://doi.org/10.1519/JSC.0b013e31822dcd96). [PubMed](https://pubmed.ncbi.nlm.nih.gov/21873897/) confirms October 2011 issue. [Original article text copy](https://www.researchgate.net/publication/51601921_Effects_of_In-Season_Strength_Maintenance_Training_Frequency_in_Professional_Soccer_Players) inspected: Subjects, Experimental Approach, Table 1, Statistical Analyses, Results (In-season Adaptations), Fig. 1/2 captions. Copy shows early pagination (25(X)); final typeset publisher comparison and exact day of publication are outstanding. Do not present 1 October as verified day. Publisher reuse rights unverified.

**Population/flow:** 19 Norwegian male professional soccer players volunteered; prior 5–7 sessions/week for three years. Transfer, injury and illness affected participation; 12 contribute preparatory change, 14 contribute in-season data (7/group, including two newcomers randomly allocated). Groups mean age 22 ± 2 and 26 ± 2 y (SE as article states). This is a trained sport population, not experienced barbell specialists. Randomization reported; allocation concealment not verified. The replacement participants mean the preparatory pooled estimate does not describe exactly the same cohort as the in-season comparison.

**Exposure:** 10-week twice-weekly preparatory half-squat program; subsequent 12 weeks assigned once weekly versus once every two weeks, each 3 × 4RM. Thus planned 36 versus 18 in-season sets (not verified actual completed counts), versus 60 preparatory sets across ten weeks if both weekly sessions completed. Both continued extensive soccer (typically 6–8 ~90-min sessions weekly, reported matches 1.8 ± 0.2/week). Actual lifting adherence, realized loads/reps and match exposure by arm need verification; frequency and cumulative set dose are inseparable in this comparison. Testing standardized half-squat to 90° knee angle, 3–5 days after final lifting session; measured 1RM, sprint, jump. This recovery timing is a test protocol, not a prescription.

**Claim `soccer-weekly-strength-retention@1`:** original descriptive retention assertion accurate but incomplete. Results report weekly group no detected decrease, alternate-week half-squat 1RM decrease 10 ± 4% (SE), p<0.05; 40-m sprint performance deteriorated 1.1 ± 0.3% (SE) in alternate-week group, with no detected change in weekly group. No detected jump change in either. Statistics specify paired t-tests and between-arm unpaired tests of relative change; extracted result paragraph does not clearly report a direct strength-change estimate/CI. Do not infer significance of the between-arm strength contrast from the pattern of within-arm p-values. Small sample, attrition, one movement, sport-specific context, possible activity differences, measurement variation and no equivalence margin.

**Disposition:** source access upgrade only after final version confirmation; pending full-text-copy appraisal and revised claim result. Restrict outcome to measured half-squat 1RM; propose a narrower outcome scope term and verify catalog compatibility. Do not assume exact retention in weekly arm or a universal one-session/three-set floor. Use regular meaningful specific strength exposure as a conservative starting convention when preserving a familiar lift during a running emphasis. For an experienced lifter already training 2–3 times/week, retention at their existing schedule or modestly reducing it is reasonable. No reason to jump to the studied reduced dose.

### 3.4 Bickel, Cross & Bamman — outcome-specific reduced-dose resistance training

**Source:** `bickel-retention@1`. *Med Sci Sports Exerc.* 2011;43:1177–1187. DOI [10.1249/MSS.0b013e318207c15d](https://doi.org/10.1249/MSS.0b013e318207c15d). [PubMed](https://pubmed.ncbi.nlm.nih.gov/21131862/) and [journal-layout copy](https://paulogentil.com/pdf/Exercise%20Dosing%20to%20Retain%20Resistance%20Training%20Adaptations%20in%20Young%20and%20Older%20Adults.pdf) inspected; pp.1178–1179 (Methods/Fig.1), p.1182 (Fig.2/results), discussion pp.1184–1185. Figures 1/2 visually checked. July issue; exact day of publication unresolved, do not certify placeholder 2011-07-01. Third-party copy not checked against publisher-hosted bytes. Copyright statement on copy; metadata and original factual summaries only.

**Population and protocol:** 70 adults (39 young 20–35 y, 31 older 60–75 y) undertook 16 weeks of initial resistance training three times/week. These are recently trained participants, not a trial of established strength athletes. Phase 2 randomized to detraining or reduced dose for 32 weeks. 57 completed phase 2, one excluded for detraining noncompliance, analysis n=56 (biopsy n=55); detraining n=16 (7 young/9 older), one-third n=19 (10/9), one-ninth n=21 (11/10). Assigned three exercises (squat, leg press, knee extension) × 3 sets × 3 days initially = 27 exercise sets/week; then 9 or 3 exercise sets/week at 8–12RM with same exercises, once weekly. These totals are assignment arithmetic, not unique quadriceps stimulus or actual attendance. Verify achieved loads and completed exposure. Detraining arm still underwent periodic strength testing (every 4–8 weeks), not zero resistance effort. Biopsy mean fiber area (MFA) and type-specific CSA, DXA, and voluntary strength are distinct endpoints. Analysis included mean substitution for some missing samples; small age-by-dose cells and attrition constrain uncertainty.

**Claim `young-reduced-dose-hypertrophy-retention@1`:** original assertion that young participants retained acquired hypertrophy at both reduced doses needs scope tightening. Results p.1182/Fig.2 report a time × age × group interaction for MFA (p<0.05); both young maintenance arms remained above pretraining baseline during phase 2, and the one-third dose increased MFA further during the first 16 phase-2 weeks (p<0.05). The older arms were no longer detectably above baseline at phase-2 sampling. The graph displays individual age-group means/error bars; no precise matched phase-1-end-to-phase-2-end contrast estimate or CI extracted, and no equivalence margin. Remaining above pretraining baseline does not establish exact retention of the entire training gain. Strength can persist despite tissue loss; do not infer retained hypertrophy from strength or DXA from biopsy.

**Disposition:** revise source access and claim assertion/result/limitations; retain the existing question but propose narrower outcome and comparator scope terms for catalog review. A separate age interaction claim is not necessary for first useful coach. Low transfer confidence. The protocol suggests that maintenance needs can differ by outcome and developmental history. It does not justify reducing an experienced lifter's volume to one-ninth or setting an individual minimum. Preserve a meaningful amount of target-muscle work if hypertrophy matters; use direct measurement or explicitly label the outcome unverified.

### 3.5 Hickson et al. — aerobic power versus long-duration endurance

**Source:** `hickson-duration-retention@1`. Hickson RC, Kanakis C Jr, Davis JR, Moore AM, Rich S. *J Appl Physiol.* 1982;53:225–229. DOI [10.1152/jappl.1982.53.1.225](https://doi.org/10.1152/jappl.1982.53.1.225). [Publisher abstract](https://journals.physiology.org/doi/abs/10.1152/jappl.1982.53.1.225) and [PubMed](https://pubmed.ncbi.nlm.nih.gov/6214534/). Publisher subscriber-only article; full text not verified. Publisher record gives 1 July 1982 publication date. No full correction/retraction/rights audit. Inspect original abstract Methods/Results only.

**Design:** 13 subjects acquired training over ten weeks of bicycling/running, 40 min/day, six days/week, then trained for fifteen more weeks at either 26 or 13 min/day. Frequency and intensity were intended to match last three weeks of development. Assigned durations 240, 156 or 78 min/week (65% or 32.5% of initial duration). The abstract does not verify random assignment, group sizes, demographic details, actual achieved exposure, adherence, initial training experience beyond study induction, or exact endurance test mode/protocol. Do not call these well-trained distance runners or assume every minute was running.

**Claim `reduced-endurance-duration-long-endurance@1`:** existing extraction reports ~10% long-endurance decline despite VO2max retention. Abstract describes long-duration endurance falling from 139 to 123 minutes in the 13-minute group (authors describe 10%; arithmetic from rounded endpoints is approximately 11.5%, not a substitute for participant-level percentage change); 26-minute group reportedly maintained long-duration endurance. Both reportedly retained VO2max and short-duration endurance (~5 min). No exact direct contrast, uncertainty, p-value or matched-person changes available. Keep authors' wording and endpoints separate; do not claim equivalence or that 26 minutes is sufficient for everyone. Need original tables and measures before approval.

**Disposition:** retain only pending abstract extraction, additional verification required. No new claim necessary. Practical implication: protect long-duration running with relevant exposure and an assessment, rather than maintaining minutes or VO2max alone. Even if the numerical estimate is not accepted, distinguish endpoints on conceptual grounds. No prescription of six high-intensity days/week or a two-thirds reduction.

### 3.6 Huiberts, Wüst & van der Zwaard — concurrent development and outcome specificity

**Source:** `huiberts@1`. *Sports Med.* 2024;54:485–503. DOI [10.1007/s40279-023-01943-9](https://doi.org/10.1007/s40279-023-01943-9). [Publisher article](https://link.springer.com/article/10.1007/s40279-023-01943-9), [PubMed](https://pubmed.ncbi.nlm.nih.gov/37847373/), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10933151/). Published online 17 October 2023, February 2024 issue. Open-access publisher article; final licensing and notice checks outstanding. Methods §§2.3–2.4, analysis/sensitivity description, Results §§3.4–3.5 (Figs.3–6) and discussion inspected. No individual trial re-extraction or forest plot reanalysis performed.

**Population/design:** 59 studies overall (1,346 participants), healthy adults, study-level training-status categorization separately for strength and endurance using reported performance and experience. Mixed strength/endurance modalities and heterogeneous durations, doses, and exercise interventions; not a trial of two hybrid block archetypes. Only ~60% of studies supplied sufficient information to classify both strength and endurance status. The review compares concurrent with corresponding single-mode development, not continuation of a previous maintenance dose. Assigned intervention details are extracted; realized dose/adherence and subgroup trial-level membership not independently reconstructed. Unclear allocation/detection bias, ecological moderator confounding, sparse highly trained and female data, and overlap with other syntheses limit transfer. Review's standardized effect scale is not kg or minutes.

| Existing claim | Verified result and interpretation | Disposition |
|---|---|---|
| `concurrent-lower-body-sex-moderation@1` | Publisher Results §3.4 confirms male SMD −0.43 (95% CI −0.64 to −0.22), female 0.08 (−0.34–0.49), subgroup p=0.03; 20 studies, 269 concurrent and 208 strength-only participants. | Retain pending, no sex-specific rule; not essential for this capability |
| `concurrent-strength-experience-moderation@1` | Lower-body strength subgroup difference p=1.00, 16 studies; individual stratum intervals not extracted | Retain pending; failure to detect moderation is not equivalence |
| `concurrent-trained-endurance-vo2max@1` | Trained endurance SMD +0.18 (95% CI −0.02–0.38), p=0.08; untrained −0.35 (−0.70 to −0.01), highly trained +0.01 (−0.32–0.34); overall training-status moderation p=0.04, 42 studies for VO2max | Retain pending; estimate applies to concurrent vs endurance-only development, not retention, race time or economy |

**Coaching consequence:** simultaneous development is a legitimate candidate, but monitor specific outcomes and priorities. The mean differences do not tell a coach the best starting exposure or whether this athlete's next run harms lifting. No categorical sex-based or training-status-based penalty. Reuse J3A.1 `same-session-trained-lower-body-strength@1` and `separate-session-trained-lower-body-strength@1` as pending context from Petré (same-session SMD −0.66 [−1.08, −0.25], separate-session −0.10 [−0.43, 0.23]). That appraisal specifically rejects a universal recovery interval or inference of acute causal interference; subgroup designs differ and study overlap is not audited. Do not count multiple syntheses as independent replication. Scheduling to protect priority-session quality is a practical choice even without accepting those estimates.

## 4. Existing evidence-record corrections and proposed revisions

Maintain exact prior revisions. The following are proposed forward revisions for curation, not approved changes. The draft JSON in Appendix A uses the existing record shape and preserved scope vocabularies where scientifically appropriate. No automatic supersession edges, method replacements, registry changes, withdrawal, or source release are proposed now. A final human reviewer must reconcile exact scope terms, verify versions, dates and rights, and apply the release procedure. Source access means access for appraisal, not permission to redistribute.

| Existing revision(s) | Change | Proposed next revision / disposition |
|---|---|---|
| `moesgaard@1`; `periodized-vs-constant-strength@1`; `undulating-trained-strength@1` | Abstract agrees with magnitude/interval; Crossmark table update; subgroup interaction not verified | Retain staged claims pending full text; source screening status remains. No JSON revision now. |
| `micke-hift-block@1`; `hift-conditioning-block-deadlift@1` | Add adjusted coefficient and SE, clarify assigned conditioning and unmeasured lifting; note sequence and version limits | `micke-hift-block@2`; `hift-conditioning-block-deadlift@2` pending |
| `ronnestad-soccer-maintenance@1`; `soccer-weekly-strength-retention@1` | Original-text copy, actual test half squat, within-arm −10 ± 4% SE, group/flow and cumulative dose details | `ronnestad-soccer-maintenance@2`; `soccer-weekly-strength-retention@2` pending final-version/date/contrast review |
| `bickel-retention@1`; `young-reduced-dose-hypertrophy-retention@1` | Full-text copy, biopsy endpoint versus pretraining baseline; no proof of exact maintenance; attrition and imputation | `bickel-retention@2`; `young-reduced-dose-hypertrophy-retention@2` pending final-version/date review |
| `hickson-duration-retention@1`; `reduced-endurance-duration-long-endurance@1` | Abstract supports existing qualitative assertion; endpoint values 139→123 min; uncertainty and test details unavailable | Retain pending; annotate review notes, require full article if quantitative use becomes essential |
| `huiberts@1`; three selected claims in §3.6 | Results support moderation caution and trained VO2max contrast; no individualized transfer | Retain pending; complete subgroup and overlap audit |

### Method-link follow-through

- `hierarchical-hybrid-block-construction@1` uses hockey, HIFT, periodization and adaptive-running claims. If adopted later, review the replacement HIFT revision and avoid implying every linked claim is necessary for the practical planning choice. Hockey and adaptive running are not re-appraised here.
- `outcome-specific-strength-maintenance@1` uses soccer, cyclist and young-adult hypertrophy claims. The proposed new revisions are narrower; cyclist remains unreviewed in this tranche. The reviewed method must not encode the studied one-ninth or weekly frequency as default floor.
- `outcome-specific-running-maintenance@1` links endurance frequency, endurance duration and wearable VO2 agreement. Separate physiological capacity, retention intervention and field proxy. Frequency and wearable evidence not independently appraised here.
- `phase-aware-undulating-specialization@1`, `joint-priority-block-review@1`, `priority-aware-concurrent-calendar@1`, `bounded-hybrid-review-transition@1`, `context-eligible-individual-history-review@1`, and `contextual-decision-response-history@1` remain pending. M02 consolidates the decision process, not their full empirical scope. M01 continues to handle local resistance prescriptions and scheduling within the approved boundary.

The draft is additive. Before acceptance, resolve all new source/claim edges and separately review the affected methods and exact transfer records; ensure both old and new revisions remain replayable. Do not use a pending revision as eligible J1 evidence or represent the candidate method as an approved programming option. An independently justified practical choice may be proposed without citing a specific unverified empirical effect as established.

## 5. Applicability and transfer assessment

### 5.1 Directness by coaching decision

| Decision | Best relevant evidence | What is supportable | What remains unknown |
|---|---|---|---|
| Organize multiple weeks with variable strength work | Moesgaard; J3A.1 Plotkin/Helms | Planned variation and local load/rep progression are plausible tools | Best hybrid phase order, duration, individual response |
| Select emphasis versus balanced | Micke, Huiberts, reused Petré | Different temporal distributions and concurrent modalities can yield different task outcomes | Whether any archetype is superior for this athlete; effects of strength/running allocation with matched realized work |
| Preserve maximal strength during running focus | Soccer; Bickel context | Meaningful specific loading is a reasonable candidate; retention cannot be assumed after reduction | Minimum dose in trained lifters; movement-specific dose and response |
| Preserve hypertrophy | Bickel | Tissue outcomes can differ from strength | Experienced lifter maintenance dose, measurement quality, whole-muscle transfer |
| Preserve aerobic capacity | Hickson; Huiberts | Capacity need not track endurance outcomes; concurrent training can be considered | Individual retention floor and direct running-only effect |
| Preserve running-specific speed/endurance | Hickson indirectly; Packet 005 measurement context | Keep relevant exposure and measure the actual protected task | Race-specific retention dose and durability under lifting |
| Choose starting dose | J3A.1 Barsuhn with limitations; IA-P03/05 | Use current actual history as practical reference | Causal dose response, optimal/maximum tolerable volume |
| Coordinate schedule | Reused Petré, M01c | Prioritize session quality and feasible separation if helpful | Universal timing interval or acute interference diagnosis |

No selected trial directly compares strength-emphasis, running-emphasis and balanced blocks in experienced recreational barbell lifters who run while also playing other sports. The method is an explicit transfer of general programming principles and a practical allocation decision, not a claim of demonstrated comparative efficacy. Do not conflate clinical older-adult or initially trained studies with an experienced recreational hybrid athlete. Athlete experience must be assessed separately in each discipline. Nor should lower-body findings transfer automatically to upper-body strength.

### 5.2 Outcomes and observation contract

| Protected outcome | Preferred assessment | Practical proxy / minimum observation | Important non-equivalence |
|---|---|---|---|
| Maximal strength | Same movement/equipment standardized 1RM | Comparable external load/reps/effort with same technique and set purpose; no 1RM test required | Estimated 1RM and old PR are not measured current maximum |
| Hypertrophy | Standardized muscle-specific imaging | Consistent circumference/appearance/body-mass context if athlete elects, explicitly low specificity; muscle work exposure | Strength or stable mass does not establish tissue retention |
| Aerobic capacity | Comparable laboratory VO2max | Standardized submaximal pace/HR/effort trend for functional context | Device VO2 estimate is not laboratory capacity; pace/HR not a direct VO2max test |
| Running-specific performance | Comparable timed run, race, or fixed-distance controlled test | Recent comparable task completion/time/effort; note terrain, weather, course and fatigue | A faster easy run or stable VO2max does not establish 10-km performance |
| Long-duration endurance | Comparable prolonged task with defined success criterion | Completion of familiar long run, duration/distance, reported effort and late-session tolerance | Long run completion is a functional observation, not proof of unchanged maximal endurance or economy |

For each target, distinguish measurement validity, test-retest reliability and sensitivity to change. Packet 009's `trained-measured-one-rm-repeatability@1` and `trained-bench-relative-load-repetition-repeatability@1` remain pending; their group summaries are not individual detection thresholds. No claim of longitudinal change can be made merely because two device values differ. For running, use Packet 005's eligible field observations and known conditions, not aggregate split rows as reconstructed intervals. If an outcome is unobservable, retain its exposure commitment but label effectiveness unknown and arrange a proportionate assessment opportunity. Optional recovery/nutrition context may guide a question or caution, but is not a mandatory daily questionnaire or a measurement of latent recovery.

## 6. Candidate practical coaching methodology

### 6.1 J3-M02 review bundles and relationship to J3-M01

| Bundle | Responsibility | Outputs to existing planner |
|---|---|---|
| M02a — goals, archetype, reference | Resolve ranked objectives, current capacity, exposure and context | Objective specification, reference provenance, block rationale and alternatives |
| M02b — weekly structure and protected outcomes | Select starting commitments, duration, phase intents, outcome criteria, progression envelopes and calendar feasibility | BlockVersion candidate, week intents, protected slots/exposures and contextual bounds |
| M02c — review and transition | Interpret actual exposure and comparable outcomes; route local adaptation or block revision | Frozen review facts, candidate continued week, change request, conflict or new block proposal |

These are review bundles, not separate engines, schemas or registered J1 method IDs. Use existing plan generation, validation, submission, preview, approval and outcome-attribution architecture. M01a/b/c receive the approved block's priority rankings, task purpose, movement-specific baselines, weekly floors/ceilings, allowed changes, phase, timing and protected commitments. They cannot silently expand them. A proposed run adjustment is allowed only under a separately reviewed running rule and the same block authority; M01 does not become an endurance prescription engine by virtue of reading run history.

### 6.2 Step 1 — establish objectives and ranked priorities

For each outcome record: discipline, exact task or measure, desired direction (develop, retain, restore, assess, defer), horizon/event, current reference and date, athlete-defined material deterioration or assessment trigger if available, measurement protocol and alternatives. Clarify the cost of preservation in time and burden. Separate:

- Hard constraints: current restrictions, time/equipment, fixed dates, accepted exposure bounds/protected slots, safety. These are planning constraints, not guaranteed physiological outputs.
- Outcome priorities: primary development and explicitly protected secondary outcomes, plus unprotected preferences. A secondary outcome can have a hard exposure floor by agreement, but cannot be guaranteed by a rule.
- Soft preferences: days, favored exercises, session length, convenience. Rank them only if the athlete agrees or clearly permits a default. If two development priorities are tied, preserve both and ask which should win an unavoidable conflict; don't infer it from sport labels.

Example: primary incline press strength, secondary retain familiar squat strength and ability to finish a comfortable 75-min run; no race time target. This differs from preserving a sub-45-minute 10-km race. Do not replace the latter with a count of easy runs. A lifetime PR can be an aspirational goal, not a baseline target unless relevant today.

### 6.3 Step 2 — choose an archetype, not an automatic periodization model

| Archetype | Selection condition | Strength exposure | Running exposure | Common alternative |
|---|---|---|---|---|
| Strength emphasis | Clear priority lift/strength objective, available time and relevant baseline | Specific priority work; stable or modestly increased demand within approved M01 bounds; retain secondary movements | Keep agreed run purposes and exposure; avoid unnecessary new hard running load | Balanced if both outcomes are progressing and no conflict |
| Running emphasis | Clear race, distance or performance priority with relevant recent runs | Familiar specific loading for protected lifts; if burden demands, trim nonessential accessories/sets before removing all specific work | Allocate time to relevant easy, quality or longer runs based on existing tolerance and objective; no independent run progression rule yet | Retain full habitual lifting if feasible |
| Balanced | Both disciplines valued without a clear tradeoff, feasible productive schedule | Maintain or selectively progress meaningful movement work | Maintain or selectively progress relevant running work | Emphasis if deadlines, stagnation or time conflict justify it |
| Transition/maintenance | Interruption, changed constraints or no feasible development plan | Conservative familiar re-entry or retention | Conservative current-tolerance work | Explicit new goals or return-to-training review |

Default: keep an existing productive balanced schedule rather than inventing specialization. An emphasis does not require reducing secondary work if there is capacity. A balanced block need not alternate hard days perfectly, allocate equal hours or produce equal percentage changes. Formal block periodization with concentrated training loads is only one option; a product block is simply a coherent planning horizon with objectives and boundaries. Do not import the Micke concentrated protocol as a default.

### 6.4 Steps 3–4 — determine recent capacity and habitual actual exposure; initialize

Follow IA-P01–05 in Packet 009. Freeze as-of instant, time zone, coverage, explicit identity and conditions before looking at outcomes. Partition observations into eligible comparable, contextual-only, uncertain and excluded. Select same movement/load convention/ROM/set role and relevant effort context; same run task/time/distance convention, terrain/weather and intensity purpose. Prefer recent representative examples; keep dates, range, median where meaningful, deviations and counterexamples. A prior block with similar context can inform the schedule even if its loads cannot be transferred. After equipment change, illness, travel or interruption, invalidate stale load/pace assumptions; ask for familiar recent exposure or a conservative assessment.

Summarize actual training by movement-specific working sets, frequency, load/reps/effort and set role; by running frequency, weekly duration/distance, purposes, longest representative exposure and available effort; and by other sports/time demand. Do not sum unlike stimulus metrics into a single workload score. Avoid duplicate workouts, open/empty records, missing coverage, and assumed completion. Hevy inferred positive reps in ended workouts are descriptive, not automatically confirmed; seek targeted confirmation before treating history as a strong capacity anchor or using M01 progression. Use representative completed weeks, not assigned planned volume or best-ever volume. Mark unusually hard race weeks, deloads, holidays and interruptions; don't silently delete them, but distinguish context. If only sparse observations, ask a small number of consequential questions; avoid numerical progression or drastic reductions until a defensible reference exists.

Initialization rule: begin from a familiar productive and tolerable dose near current actual exposure, not historical maximum, not a universal optimal stimulus. If evidence of tolerance is uncertain, choose a conservative starting dose, obtain athlete agreement and review earliest comparable execution. If no relevant history, establish a safe task-specific familiarization/assessment rather than pretending to know capacity. Keep running commitments that match the athlete's actual background, avoiding novel long or hard sessions merely because an archetype suggests them. If both disciplines have a productive history, holding one while progressing the other is a reasonable first allocation. If the current dose is impractical, offer a reduction with named tradeoffs rather than claiming maintenance will be preserved.

### 6.5 Step 5 — outcome-specific secondary protection contract

Each protected outcome needs five elements:

1. Target and reference: e.g., preserve squat performance on familiar 150 kg working sets, or comfortable 75-min continuous running at familiar effort.
2. Agreed training proxy commitments: named weekly exposures, relevant movement/intensity/purpose, duration or set floor, and ceilings if needed. State why they are selected from actual history. A commitment can be enforced as schedule/prescription, not physiology.
3. Assessment opportunity: baseline and review method, comparability criteria, dates or conditional windows, no mandatory maximal test. An assessment can substitute for a familiar session if within bounds and reviewed; no extra maximal effort by default.
4. Outcome status: supported stable within available resolution, favorable observed direction, possible deterioration, mixed, or insufficient comparable evidence. Separate status from exposure compliance. Use an athlete-approved review tolerance when useful; never present that tolerance as smallest detectable physiological change.
5. Response policy: when a protected session is repeatedly missed or outcome may deteriorate, check quality/context and feasibility, preserve or redistribute exposure, request feedback, or explicitly reconsider priority/floor/assessment with athlete approval. If no option satisfies hard constraints, return a named conflict.

Illustration: maintain squat 2 × 5 at familiar load/effort weekly and 75-min long run as goals. If the athlete completes the squat dose but actual comparable strength deteriorates, adherence may be high while outcome evidence is adverse. If long run is shortened and wearable VO2max unchanged, do not mark endurance preserved. If no comparison is possible because of weather or equipment, leave outcome unknown even when dose completed. No outcome target can override new pain, medical restrictions or feasibility.

### 6.6 Steps 6–7 — duration, weekly intent, assessment and progression envelope

Choose block length around the athlete's horizon, time needed for useful repeated exposures, known interruptions and assessment. Candidate six weeks with a start review, development opportunities and final review; 4–8 is a practical range, not a physiological optimization. An event or interruption may require shorter or longer; the calendar can carry multiple blocks with stable objective lineage.

Illustrative six-week intent (not a universal sequence):

| Weeks | Intent | Permitted behavior |
|---|---|---|
| 1 | Establish representative baseline and feasible schedule | Familiar actual dose; conservative if current capacity uncertain; no compulsory ramp |
| 2–3 | Development or retention per ranked outcomes | M01 review within approved bounds; hold productive doses; protect key run purpose |
| 4–5 | Continue or refine specificity; reassess conflicts | Same priority/floors; reversible adaptation when observations warrant; reduce or redistribute local demand if needed |
| 6 | Comparable assessment and transition review | Maintain familiar work or adjust locally to permit assessment; no mandated taper, deload or maximal test |

If a block has a clear assessment event, define protected dates and feasible neighboring work in advance. Changes to assessment purpose/date that violate agreed protection need explicit review. A planned lower-burden week may be sensible based on availability and objectives; no physiological cycle is assumed. Do not preordain that each week escalates. Plan future weekly intents and bounds; detailed future session prescriptions may be generated and approved one week at a time. Use daily time budgets, equipment, rest allowance and worst permitted endpoints to validate each candidate calendar.

For each week/purpose pin nominal target, allowed execution interval, working-set or duration/distance floor/ceiling, progression constraints relative to predecessor and starting baseline, permitted change dimensions, forbidden simultaneous increases, protected key sessions/events, assessment exceptions and neighbor constraints. Preserve explicit distinction between plan target versus execution interval. A load increase with rep reset is a single progression decision; increasing sets and per-set demand together is not default M01 behavior. An approved absolute ceiling is a cumulative block limit as well as per-step caps; prevent repeated small increases from bypassing the intended envelope. Running time and distance are not two independent dose totals to add; choose a metric and retain the other descriptively. Do not set pace/HR targets absent eligible anchors. Other recreational sport participates in time/context feasibility but isn't automatically counted as equivalent strength/running training.

### 6.7 Steps 8–9 — feasibility and review routing

First evaluate current restrictions, exact calendar availability, event windows, equipment, approved objectives, time including transitions/rest, and adjacent session/block bounds. Protect highest priority quality and agreed secondary floors, then athlete preferences. Separate demanding local work where feasible and useful; no universal mandatory recovery interval is introduced. Consider retaining schedule, moving an unprotected slot, trimming nonessential lower-body work, adjusting local load/sets, or simplifying work. Do not automatically move a protected run or reduce its dose; treat only explicitly allowed date flexibility as an execution/planning alternative, and submit a changed future schedule for approval. If a new restriction invalidates an approved prescription, flag conflict and protect the athlete; never insist on executing it to satisfy a floor.

| Situation | Review routing |
|---|---|
| Productive priority and supported secondary outcomes | Continue or bounded M01 change; no block revision required merely to progress |
| One unusually difficult comparable lift near demanding run | M01c local clarification, hold, reduction or redistribution; no causal diagnosis |
| Poor adherence with viable alternate dates | Propose feasible schedule change within same block; obtain athlete approval |
| Repeated inability to satisfy protected exposure despite feasible attempts | Explicit block review, offer changed time, objective, floor, dates or transition |
| Possible secondary deterioration despite exposure | Check measurement and context; offer reversible adjustment within bounds, then escalate if needed |
| New goal/event, lasting restriction or context change invalidates reference | New context and explicit block revision; validate future affected weeks |
| No feasible schedule with all hard constraints | Return infeasibility and conflicting constraints; no hidden relaxation or automatic priority change |

A safe stop or refusal to train is always permitted. The coach cannot guarantee that an exposure floor preserves an outcome. Athlete approval is required for changed future nominal prescription, allowed range, calendar or block; no approval required to choose an already permitted execution option or to observe data. Frozen prior approvals, completed slots, evidence and historical rationale remain immutable. Recheck current context, observations/support, head and evidence eligibility at decision time. Decline leaves prior head intact; a stale proposal needs fresh preview. Use the existing architecture rather than a second optimization engine.

### 6.8 Step 10 — observed block review and continuation

At weekly reviews show actual versus prescribed exposure by discipline and purpose, known/partial/missed/unknown denominators, adherence and deviations, relevant feedback, eligible comparable outcomes, change context and alternative explanations. Use the current approved revision at time of performance. A missing provider import is unknown, not a missed run. A successful session does not itself establish capacity for more training or causal benefit of prior decisions.

At midpoint or block close, compare each outcome with its agreed baseline and assessment opportunity; include all comparable observations (not only best results), identify missing/confounded observations, note changed effort and conditions, and distinguish observed difference from sustained trend and physiological adaptation. Outcome status can remain unknown. Summarize whether exposure was feasible, burden acceptable, objective progress observed and whether athlete wants same priority. Propose continue same block intent/new block, refine exposure, change archetype, reschedule assessment, or transition. Preserve outcome and decision lineage and retain useful contextual patterns with counterexamples (IA-P04/06). Example: Tuesday squat repeatedly difficult after Monday hard runs may justify trying another slot; it does not prove causal interference or a permanent recovery rule. A later context change invalidates or weakens the pattern. No formal experiment or latent model is necessary for useful review, and historical improvement cannot establish causal coaching superiority.

### 6.9 Observation readiness and minimum input contract

| Decision | Prescription minimum | Adherence / effectiveness requirements | Fallback |
|---|---|---|---|
| Select archetype | Confirmed ranked goals, horizon, restrictions, availability and rough actual history | Actual block exposures and comparable outcomes for evaluation | Qualitative archetype alternatives; ask about priority or recent workload |
| Set numeric initial exposure | Eligible representative movement/run history or athlete-confirmed actual workload | Attributable performed work and coverage | Conservative familiar exposure or assessment; no invented baseline |
| Set protected outcomes | Athlete's specific outcome and feasible assessment/commitment | Exposure linkage and outcome-specific follow-up | Explicit unverified outcome; protect planned exposure without claiming retention |
| Change local work | M01 inputs, current block envelope, actual execution and optional feedback | Subsequent comparable performance | Hold, clarify, reduce safely, or conflict |
| Revise block | Current context, material mismatch, alternatives and authority | Approved new version, later observations | Preserve approved plan subject to current safety; no silent change |

Scientific readiness is pending for all methods/claims; data readiness is conditional per task. Historical strength analytics can support descriptive summaries with explicit exercise mapping and inferred/confirmed coverage; canonical endurance summaries support dated time/distance/frequency with verified history. Optional Garmin HRV/sleep and high-resolution telemetry are not necessary. Aggregate splits and step instructions cannot establish interval adherence. Need engineering for generalized movement/slot linkage, confirmed actual set coverage, context-eligible historical selection and run comparison where not already supported. J3B.1 documented E1/E3's strict synthetic progression predicate; do not change it or infer live provider coverage. No source code or tests run here.

## 7. Proposed contextual numerical parameters and unresolved programming choices

These are initial review defaults for J3B.2, not evidence-based cutoffs. Each parameter is a programming judgment (P), practical convention (C) or engineering safeguard (E); no number here is an empirically established individual dose. Existing approved block constraints and current restrictions take precedence. A reviewer may select tighter bounds or an alternative with explicit rationale. Do not transfer experimental frequency or dose ratios into operational defaults.

| Parameter | Candidate starting configuration and type | Conditions, overrides and fallback |
|---|---|---|
| Horizon | 6 weeks, ordinarily 4–8 (P) | Match goal/event, availability, interruptions and review opportunities. Short horizon/transition possible; no mandate to finish an infeasible block. |
| Exposure lookback | 3–4 representative completed weeks, preferably recent stable regime (P/C, aligned M01) | Identify actual counts/durations and coverage; extend if same context and scarce; after interruption avoid stale dose. Missing data: athlete-confirm or qualitative/conservative initialization. |
| Strength reference | 2–3 comparable exposures, normally within 28 days (P/C, M01) | Same task, role, equipment and actual work; current most representative anchor. Old PR contextual only. If one eligible exposure, conservative prescription/confirm; no unplanned RPE-free increase until M01 criteria. |
| Running reference | 2–3 comparable recent task exposures if available; last 3–4 completed weeks for habitual duration/frequency (P/C) | Weather, terrain, distance/time and purpose; no fixed pace/HR inference. If only one comparable long run, treat it as tentative, not a trend. |
| Starting exposure | Nominal 100% of representative familiar exposure if productive, feasible and tolerated (P) | This is a starting choice, not an optimal volume. Reduce if capacity or calendar changed. No automatic increase just because primary. Confirm inferred history. |
| Secondary dose option | First retain 100%; if necessary, propose modest local reduction e.g. 1–2 nonessential working sets/week or 10–20% weekly duration from familiar baseline, without violating protected task/floor (P) | Not a minimum maintenance fraction. If small baseline, percentage may be infeasible; preserve key specificity and use exact counts; if floor conflict return explicit block review. Avoid simultaneous reduction of every intensity/frequency dimension. |
| Secondary specificity | Preserve at least one meaningful familiar exposure opportunity per agreed task each review week where that was habitual and feasible (P) | Not an empirical minimum; retain more if outcome requires or athlete wants it. A previously less frequent task may retain its actual cadence; a longer run cannot be replaced by arbitrary short run. |
| Initial strength envelope | Per eligible movement follow M01 +1 total rep or smallest load step, caps 2.5% upper / 5% lower; +1 weekly set within 25% and approved ceiling (P) | Reference approved predecessor plus separate block ceiling; no automatic increases. Equipment rounding down to feasible increment, hold/rep alternative if above cap. Tighten for secondary work or context. |
| Initial block ceilings | Example review configuration: primary movement set target up to baseline +2 sets over six weeks, only if each step satisfies M01; secondary target unchanged unless reviewed, floors negotiated (P/E) | Not a universal volume limit. Set counts integers, both step and cumulative bounds. A baseline 3-set movement cannot automatically add a set under 25% cap. Allow reviewed alternative block; no cap bypass via new week. |
| Running envelope | For this tranche, default hold nominal weekly duration/long-run purpose until reviewed running progression method; optional planning headroom e.g. 0–10 min/week only if athlete has approved a specific bounded option (P) | Headroom is not a recommendation or permission to autonomously progress. No universal 10% rule, no unreviewed speed/interval prescription. If running is primary, reserve feasible time and define future intent; prescribe familiar task pending running method. |
| Simultaneous demand | Default one materially increased demand dimension across the competing lower-body priority work at a review; avoid simultaneous increases in sets and per-set demand (P) | Athlete/coach may review a specific planned combination; upper-body changes need not be held solely due to running if independent and feasible. No physiological score. |
| Review cadence | Weekly (C/E); midpoint around week 3 and close at week 6 (P) | Earlier review for pain, new restriction, conflict, or material unexpected performance; no requirement for daily questionnaire. |
| Outcome trigger | Prefer explicit athlete-defined functional threshold and comparable reassessment; otherwise two comparable adverse observations prompt review, one material adverse event prompts earlier clarification (P) | Not a significance test or universal detection threshold. Never ignore safety or clear missed commitment. If uncertain comparison, classify mixed/unknown, repeat or ask. |
| Assessment | Baseline in week 1 or existing eligible observation; end-of-block comparable opportunity, optional midpoint; no required 1RM or maximal run (P) | Select task and conditions; if not comparable, defer rather than fabricate retention. Avoid adding an exhausting test solely for data. |
| Calendar feasibility | Exact available minutes, rest/transitions, approved neighbor spacing and event windows (E) | No additional scientific spacing constant. Prefer separate priority sessions if feasible. If no schedule satisfies hard constraints, return conflict rather than relax. |

J3B.2 must turn these into a coherent initial configuration, not treat every table row as a separate approval decision. Review whether an explicit cumulative cap is appropriate for different movements, how to choose conservative exposure reductions, and how to express exact weekly run intent before running-specific policy is reviewed. A 25% M01 set cap applied to 3 sets disallows +1 unless specifically reviewed; the example +2 cumulative ceiling is not an override. Running duration headroom and secondary reductions require relevant history and explicit approved bounds; no numerical run escalation is authorized by J3A.2.

## 8. Synthetic evaluation cases

All values are invented and illustrate recommendation quality/authority, not expected physiological effects. Acceptable alternatives are intentionally non-unique. Each changed future prescription/plan needs athlete approval; unchanged advice, stopping unsafe work, and choices within already approved execution intervals do not. All proposals require feasibility/authority validation. No case establishes physiological efficacy.

| Case | Observations and constraints | Acceptable action and required explanation | Prohibited inference / action |
|---|---|---|---|
| B02-01 strength emphasis, running protected | Actual 4-week pattern: incline 8 sets/week, squat 5 sets, 3 runs totaling 120 min including 60-min comfortable long run. Athlete prioritizes incline; long-run ability protected, time budget unchanged. | Propose six-week block starting at actual dose; choose specific incline progression envelope under M01 and retain long-run purpose, assess comparable press and long-run effort. Alternative: balanced continuation if both productive. Explain no need to cut running solely for emphasis. | Universal interference penalty, guaranteed 10-km retention, mandatory escalating volume. |
| B02-02 running emphasis, strength retention | Familiar 3 lifting days, squat 6 working sets, incline 8 sets, 3 runs totaling 135 min; upcoming 10-km event; available time allows either extra running opportunity or full accessory work, not both. | Retain specific squat and press tasks; propose removing 1–2 lower-priority accessories within agreed bounds and reserve running time. Define strength assessment, running objective and future run-rule review. | Prescribe one-ninth lifting dose from Bickel; infer race performance from VO2max; introduce unreviewed interval plan. |
| B02-03 balanced productive | Comparable lifts improving; familiar runs show stable or improving task performance and acceptable burden, no imminent event. | Continue balanced familiar schedule; set weekly review and optional bounded M01 progression. State productive current exposure is not evidence of need for more. | Forced specialization, equal time or set/minute weighting. |
| B02-04 exposure preserved but outcome deteriorates | 3/3 scheduled runs completed weekly; long run shortened from 80 to 45 min within a previously agreed temporary exception; Garmin VO2 estimate stable; comparable prolonged effort now difficult twice. | Flag possible long-duration deterioration, not established cause; review task comparability, restore familiar relevant exposure if feasible and approved or revise the secondary objective explicitly. | Mark endurance maintained because run count/VO2 stable; infer glycogen or fatigue mechanism. |
| B02-05 old PR and sparse history | 180 kg squat PR a year ago, recent confirmed 135 × 5; 3 weeks interrupted travel, imported Hevy sets mostly inferred. | Use current confirmed work conservatively, clarify recent actual exposure; short transition/assessment or defer numeric progression; PR is aspiration only. | Anchor to 180 kg; treat inferred sets as current confirmed progression evidence. |
| B02-06 local conflict | Athlete prioritizes running, Tuesday hard run precedes Wednesday squat; two difficult lower-body sessions, upper-body unaffected; Thursday lifting window available, within approved weekly exposure and spacing. | M01c propose moving squat to Thursday or local reduction, retain upper work and protected run, review next comparable response. Explicitly state temporal association is not causal. | Automatically cut running, introduce 48-h physiological rule or reduce all work. |
| B02-07 infeasible block | Two protected running dates and 3 lifting slots required; new work obligation removes both possible times for one protected run; no permissible alternative. | Return named conflicting constraint and alternatives: change availability, explicit protection/date revision or transition. Preserve approval history; do not activate infeasible candidate. | Quietly remove protected run, move observed session, infer changed priorities. |
| B02-08 hypertrophy unobserved | Running emphasis, squat loads/reps stable, no direct muscle-size measure; lower-body accessory exposure reduced. | Report observed strength proxy stable, hypertrophy effectiveness unknown; retain/review agreed relevant muscle exposure and offer optional appropriate assessment. | Claim no muscle loss from unchanged squat or mass; require invasive testing as MVP. |
| B02-09 conflicting measurements | Baseline 10-km assessment on cool flat route, follow-up slower in heat/hills; weekly training and effort plausible. | Label comparison contextual or uncertain; arrange comparable assessment, maintain or adjust exposure based on other eligible facts. | Diagnose fitness decline or reset goal solely from time. |
| B02-10 stale proposal | New block proposed using two confirmed exposures; a late correction removes support for one, and athlete reports new movement restriction before approval. | Reject stale candidate; freeze correction/context, re-evaluate feasible proposal, protect athlete; replay earlier rationale unchanged. | Auto-rebase/approve, ignore restriction, migrate old outcome to new head. |

Conformance should exercise semantic determinism with stable candidate order, explicit bounds and conflicts, exact revision pins and immutable outcome attribution. Check both coverage and adherence denominators. Include counterfactual pairs (same exposures but changed goal; same goal but unknown outcome; same calendar but protected commitment) to ensure decisions respond only to eligible facts. Evaluate rationale for uncertainty, tradeoffs, alternatives and no fabricated evidence. A prospective personal review can evaluate usefulness and burden, not causally establish optimum training.

## 9. Human review decisions required

Review bundles separately while preserving exact revision-level traceability. AI-assisted appraisal is not independent human review. Technical project owner can verify arithmetic, source locator, schema and implementation invariants; a qualified strength/endurance coach or sports-science reviewer should assess population transfer, exercise/run specificity, progression and retention choices. Athlete chooses goals, preferences, tradeoffs, acceptable commitment and assessment. Clinical/dietetic issues require appropriate professionals; no diagnostic/rehabilitation/nutrition prescription authorized here.

| Bundle | Empirical premises for review | Practical decisions for review | Permitted only after appropriate method/rule authorization and athlete approval | Deferred / prohibited |
|---|---|---|---|---|
| M02a | `periodized-vs-constant-strength@1`, `undulating-trained-strength@1`, `hift-conditioning-block-deadlift@2` if accepted; Huiberts and Petré context; Packet 009 history measurement review pending | Priority hierarchy, archetype defaults, eligible baseline and conservative fallback, duration | Generate block alternatives and initial reference from approved goals/observations | Claim superior archetype, infer current capacity from PR, invent physiological state |
| M02b | `soccer-weekly-strength-retention@2`, `young-reduced-dose-hypertrophy-retention@2`, `reduced-endurance-duration-long-endurance@1` if accepted; `concurrent-trained-endurance-vo2max@1` not retention | Exposure floors versus outcome targets; assessment and tolerance; weekly intent; cumulative caps; scheduling and other sport constraints | Propose bounded future prescriptions and exact protected commitments; delegate local lift rules to reviewed M01 | Universal maintenance fraction, mandatory intervals, guarantee outcome, unreviewed run progression or taper |
| M02c | J3A.1 measurement/effort constraints, IA-P01–06 and pending Packet 009 measurement records | Weekly and end review, when to clarify/hold/redistribute versus explicit block revision; provenance and stale handling | Propose same-block changes or explicit new block with validated future schedule and review | Diagnose causal interference, silently relax objective, automatically approve or change historical plan |

Consolidated reviewer checklist:

1. **Scientific factual checks:** verify updated Moesgaard full text and moderator interaction; Micke model, allocation, participant flow, achieved conditioning and unmonitored background lifting, sequence/carryover and multiplicity; soccer final version, relative-change test and interval, adherence and exact publication date; Bickel final version, mean fiber area and exact contrast, imputation and attrition, date; Hickson full protocol/endpoint and precision; Huiberts subgroup figures, overlap and notice audit. Assess rights for all. Do not create reviewer attestations here.
2. **Transfer and interpretation:** agree narrow meaning of each claim; no universal floor, optimum or interference coefficient. Determine if a practical programming choice can be accepted independently of unresolved empirical effect. Preserve limitations and no approved transfer until explicitly recorded.
3. **Coaching review:** choose a coherent default duration/phase approach and starting exposure method; accept or revise candidate caps, secondary outcome protection and assessment triggers; assess running specificity and coordination in actual context. Do not require individual approval of every minor display parameter.
4. **Athlete choice:** agree outcome ranking, acceptable secondary tradeoffs, protected slots/exposure, review tolerance and burden, and alternatives if infeasible. Review exact plan changes. Preference is not an empirical claim.
5. **Engineering review:** verify schema compatibility, versioned policy/config, exact support links, existing validator, source identity/completion, coverage, immutable revisions, replay, stale rejection and conformance cases. Separate scientific eligibility from data readiness and authorization. No current E1/E3 behavior changes.

Approval gate: proposed source/claim revisions remain pending with null approval and no transfers. If approved, a separate reviewed release with exact revision pins and digest is required for operational evidence. Method approval and rule adoption require independent evaluation and explicit authorization. Athlete approval applies to exact future plan, not general scientific validity. No live coaching rule, provider write, implementation or release has been made.

## 10. Recommended next curation tranche

Proceed to **J3B.2 — Practical multiweek block construction**, not another broad periodization review. It should refine M02a/b/c into an implementable candidate procedure within the current planner, with exact block and weekly-intent representations, contextual parameter defaults, conflict routing, and three detailed synthetic programs (strength emphasis, running emphasis, balanced). Include at least one interruption/constraint change, an unobservable protected outcome and a secondary deterioration case. Show explicit handoff to M01 and preserve current approval architecture. Treat running-specific new progression prescriptions as dependent on a separate reviewed method; current familiar running exposure can already be represented.

Later targeted appraisal: running prescription/progression and measurement (Packet 005, Nuuttila bundle and field comparisons) followed by practical J3B refinement. Nutrition/recovery, return after interruption and longer-horizon transition should be pulled forward only for concrete requirements. Continue Packet 009's proportionate history-based evaluation. Defer taper optimization, composite readiness, physiological decay modeling, dose-response inference, formal randomized personal trials and optimal maintenance dose estimation. Useful coaching does not require solving every scientific uncertainty, but must not hide the ones material to the proposed action.

---

## Appendix A — Pending J1 draft additions

Proposed additive fragment. Exact earlier source/claim identifiers are shown in §4. The `published_on` day for Bickel and soccer is inherited from the existing placeholder to conform to the date-shaped field; **not verified** and must be resolved before review/release. `full-text` means an inspected article-text copy, not independently authenticated publisher bytes. Existing exact question tags are preserved; propose narrower scope terms for Bickel (pretraining baseline and mean myofiber area) and soccer (half-squat 1RM). Verify scope vocabulary compatibility before release. No relation, method, withdrawal or attestation is added. JSON syntax is checked locally; full `CorpusRelease` validation and collision check against all staged branches are not performed. Do not integrate unreviewed replacements into an operational release.

```json
{
  "questions": [],
  "sources": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.2)",
      "status": "pending",
      "approval": null,
      "key": "micke-hift-block@2",
      "citation": "Micke F, Huelle J, D’Hulst G, Isenmann E, Geisler S, Held S. Block periodization vs. traditional periodization in high-intensity functional training: a randomized crossover study. Front Physiol. 2026;17:1810477.",
      "doi": "10.3389/fphys.2026.1810477",
      "record_url": "https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2026.1810477/full",
      "published_on": "2026-05-20",
      "design": "Randomized crossover conditioning trial",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "Publisher article and PubMed date inspected; DOI resolver header date discrepancy, comprehensive correction/retraction and version checks outstanding.",
      "rights": "CC BY reported by publisher; factual summaries only pending rights review.",
      "appraisal": "Methods 2.1–2.3, Results 3.1 and Table 1 checked; assigned conditioning pool matched, external lifting unmonitored, potential carryover and multiplicity; achieved exposure and supplement checks remain.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.2)",
      "status": "pending",
      "approval": null,
      "key": "ronnestad-soccer-maintenance@2",
      "citation": "Rønnestad BR, Nymark BS, Raastad T. Effects of in-season strength maintenance training frequency in professional soccer players. J Strength Cond Res. 2011;25:2653–2660.",
      "doi": "10.1519/JSC.0b013e31822dcd96",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/21873897/",
      "published_on": "2011-10-01",
      "design": "Randomized comparative in-season strength maintenance trial",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "PubMed issue month and early journal-layout article-text copy checked; inherited first-day placeholder is not verified. Final version, exact publication day and correction/retraction checks outstanding.",
      "rights": "Third-party copy inspected for factual verification; redistribution and reuse rights not verified.",
      "appraisal": "Article text on ResearchGate: Subjects, Table 1, Statistical Analyses, In-season Adaptations. 14 in-season participants; prescribed frequency and cumulative dose differ; direct strength contrast interval and actual dose unverified.",
      "next_review": "2027-02-25"
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.2)",
      "status": "pending",
      "approval": null,
      "key": "bickel-retention@2",
      "citation": "Bickel CS, Cross JM, Bamman MM. Exercise dosing to retain resistance training adaptations in young and older adults. Med Sci Sports Exerc. 2011;43:1177–1187.",
      "doi": "10.1249/MSS.0b013e318207c15d",
      "record_url": "https://pubmed.ncbi.nlm.nih.gov/21131862/",
      "published_on": "2011-07-01",
      "design": "Two-phase randomized reduced-dose trial",
      "access": "full-text",
      "checked_on": "2026-11-25",
      "publication_check": "PubMed and journal-layout copy inspected; inherited first-day issue-month placeholder is not verified. Final publisher version, exact date and correction/retraction checks outstanding.",
      "rights": "Copyright notice on third-party journal copy; no redistribution rights verified; factual summaries only.",
      "appraisal": "Methods pp.1178–1179, Fig. 1, p.1182 Fig. 2 and discussion checked. Phase 2 n=56, biopsy n=55; recently trained, small age-by-dose cells, imputation; repeated strength testing even during detraining.",
      "next_review": "2027-02-25"
    }
  ],
  "claims": [
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.2)",
      "status": "pending",
      "approval": null,
      "key": "hift-conditioning-block-deadlift@2",
      "scope": {
        "question": "hybrid-periodization-comparison",
        "objective": "performance-development",
        "population": "hift-athletes",
        "experience": "experienced",
        "intervention": "concentrated-conditioning-intensity",
        "comparator": "evenly-distributed-conditioning-intensity",
        "outcome": "deadlift-one-rm",
        "horizon": "six-weeks-per-condition",
        "block_context": "concurrent-training"
      },
      "assertion": "The adjusted deadlift 1RM change contrast favored concentrated versus distributed conditioning in the six-week-per-condition crossover.",
      "limitations": "Unmonitored background lifting; carryover, multiple outcomes, achieved dose uncertainty; not a controlled strength-versus-running emphasis comparison.",
      "quality": "low",
      "assessment": "Original model coefficient and SE extracted; exact interval and independent review outstanding.",
      "transfers": [],
      "support": [
        {
          "source": "micke-hift-block@2",
          "locator": "Results 3.1, Table 1 deadlift; Methods 2.2–2.3",
          "result": "Adjusted intervention beta +5.53 kg, SE 2.11 kg, p=0.018, d=0.85; exact model CI not extracted.",
          "restriction": "Study-specific conditioning allocation; no inference of maintenance equivalence, optimal phase order or approved hybrid transfer."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.2)",
      "status": "pending",
      "approval": null,
      "key": "soccer-weekly-strength-retention@2",
      "scope": {
        "question": "strength-maintenance-dose",
        "objective": "performance-retention",
        "population": "professional-soccer-players",
        "experience": "trained",
        "intervention": "weekly-strength-maintenance",
        "comparator": "alternate-week-strength-maintenance",
        "outcome": "half-squat-one-rm",
        "horizon": "twelve-weeks",
        "block_context": "concurrent-training"
      },
      "assertion": "The weekly and alternate-week groups showed different descriptive patterns of measured half-squat 1RM retention after preparatory training.",
      "limitations": "Seven per arm; participant turnover/attrition; cumulative set dose differs; within-group significance pattern does not establish between-group effect or equivalence.",
      "quality": "low",
      "assessment": "Article-text copy checked; final version, adherence, direct contrast and independent review outstanding.",
      "transfers": [],
      "support": [
        {
          "source": "ronnestad-soccer-maintenance@2",
          "locator": "Table 1; Results In-season Adaptations; Fig. 1",
          "result": "Weekly group no detected decline; alternate-week group half-squat 1RM declined 10 ± 4% (mean ± SE), p<0.05. Direct between-group change interval not extracted.",
          "restriction": "Specific half-squat protocol; not a universal weekly maintenance floor; no approved hybrid transfer."
        }
      ]
    },
    {
      "synthetic": false,
      "extracted_by": "ChatGPT (AI-assisted appraisal, J3A.2)",
      "status": "pending",
      "approval": null,
      "key": "young-reduced-dose-hypertrophy-retention@2",
      "scope": {
        "question": "strength-maintenance-dose",
        "objective": "performance-retention",
        "population": "adults-aged-20-to-35",
        "experience": "recently-trained",
        "intervention": "one-third-or-one-ninth-development-dose",
        "comparator": "pretraining-baseline",
        "outcome": "mean-myofiber-area",
        "horizon": "thirty-two-weeks",
        "block_context": "strength-maintenance"
      },
      "assertion": "Mean myofiber area in the young reduced-dose groups remained above pretraining baseline through phase 2; the one-third group showed additional enlargement at the first phase-2 sampling. Exact retention of the entire acquired gain relative to end of development was not established by an equivalence comparison.",
      "limitations": "Recently trained adults; biopsy endpoint; small age-by-dose samples; attrition and mean substitution; age-dependent responses. Verified significance comparison is against pretraining baseline; narrower scope proposed, subject to catalog validation.",
      "quality": "low",
      "assessment": "Article-text copy and figure inspected; matched end-development to final contrast and interval not extracted.",
      "transfers": [],
      "support": [
        {
          "source": "bickel-retention@2",
          "locator": "Results p.1182; Fig. 2, mean myofiber area; Methods Fig. 1",
          "result": "Time × age × group interaction p<0.05; young groups remained above baseline at phase-2 sampling, p<0.05; one-third group additional enlargement in first 16 weeks of phase 2, p<0.05. Exact retention contrast CI unavailable.",
          "restriction": "Myofiber area, not measured whole-muscle retention or a universal one-ninth maintenance rule. No approved transfer."
        }
      ]
    }
  ],
  "relations": [],
  "methods": [],
  "withdrawals": []
}
```
