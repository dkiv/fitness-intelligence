# Observation-aware research methodology

**Scope.** This standing research convention applies from Packet 005 onward. It
extends the [research library](README.md), [coaching science requirements](../coaching-science.md)
and [scientific knowledge design](../scientific-knowledge-design.md). Packets 001–004
remain historical research inputs; do not rewrite them solely because an integration
or this documentation convention changes. This document neither approves scientific
claims or coaching methods nor changes J1, application code or planner rules.

## Three independent layers

| Layer | Responsibility | Boundary |
| --- | --- | --- |
| Scientific knowledge | Physiological constructs, intervention effects, measurement methods, uncertainty, source provenance and applicability to the studied population. | Provider-independent. Current API coverage must not constrain literature selection or become part of an empirical claim's definition. |
| Coaching methodology | Candidate decisions, canonical observation requirements, comparison conditions, applicability, missing-data behavior and evaluation. | Provider-independent and observation-aware. Specify what must be known, with what quality, rather than which app supplies it. |
| Integration capabilities | Mapping provider records and athlete feedback to canonical observations, permissions, provenance, coverage, resolution and known errors. | Mutable engineering inventory. A new or changed integration can alter feasibility without altering scientific findings. |

Investigate the physiological question first, then assess which field observations
could support a specific coaching decision. Do not omit relevant laboratory or
intervention studies because their measurements are unavailable to the MVP. Conversely,
access to a provider metric does not establish that the metric is valid for a decision.
Retain the existing standards for literature search, exact source and result locators,
publication and rights checks, independent review, transfer arguments, conflicting
findings and uncertainty. Distinguish direct concurrent-athlete evidence, indirect
single-discipline evidence, consensus, mechanisms, practical methodology, athlete
observations and engineering or safety safeguards. An intervention effect is not
validation of an adaptive decision algorithm.

## Measurement and proxy appraisal

For each major construct or outcome, describe the literature's measurement protocol,
what it measures directly or estimates, and relevant alternatives in the field. Assess
whether each alternative is defensible for the proposed decision, not merely correlated
with the construct. A proxy may be useful for one decision and inadequate for another.
A directly measured outcome under a study protocol does not necessarily identify the
underlying physiological mechanism.

Document the following for each important observation or proxy:

| Dimension | Questions for appraisal |
| --- | --- |
| Construct and reference | What is the target physiological construct or outcome? What reference measurement, protocol, unit and time horizon does the literature use? Is that reference itself a proxy? |
| Field alternative | What canonical observation could be collected outside the laboratory? Is it measured, athlete-reported, inferred or estimated? |
| Validity | Does it measure the intended construct or predict a relevant decision outcome? What evidence and population support that interpretation? Distinguish cross-sectional association from within-athlete validity. |
| Reliability | How repeatable is it under comparable conditions? Consider device, protocol, assessor, day-to-day variation and estimation error. |
| Sensitivity to change | Can the method distinguish a meaningful change from typical variation or measurement error over the relevant time horizon? Record uncertainty and gaps rather than inventing a cutoff. |
| Confounding and comparability | What changes in conditions, effort, equipment, behavior, environment, training phase or measurement method could explain a difference? When are comparisons informative, and when should they be excluded or qualified? |
| Applicability and limitations | What can and cannot be inferred for experienced hybrid athletes? What observations are insufficient? Could targeted feedback or another measurement resolve important ambiguity? |

Illustrative distinctions (methodological examples, not newly reviewed empirical claims):

| Construct or outcome | Reference or study measure | Possible field observation | Interpretation boundary |
| --- | --- | --- | --- |
| Maximal strength | Standardized measured 1RM | Estimated 1RM or comparable load-repetition-effort performance | An estimate is not a measured maximal lift; exercise, effort and fatigue affect comparisons. |
| Running economy | Oxygen or energy cost at controlled submaximal speed | Pace at comparable heart rate and perceived effort | Not a laboratory economy measure; terrain, weather, fatigue and cardiovascular response can confound it. |
| Aerobic capacity | Laboratory maximal oxygen uptake test | Wearable VO2max estimate or standardized field performance | Neither directly measures maximal oxygen uptake in the laboratory. |
| Recovery capacity | No single comprehensive reference measure | Performance trends, HRV, sleep and subjective feedback | No single observation establishes recovery capacity or the optimal training adjustment. |
| Energy intake and availability | Controlled intake; exercise expenditure and fat-free mass for estimated availability | Logged intake, weight trends and exercise observations | Logged intake is not true intake; weight stability does not by itself establish adequate energy availability. |
| Muscle glycogen | Biopsy or validated spectroscopy | Recent exercise exposure and reported carbohydrate intake | Context for fueling decisions, not a glycogen measurement. |

Do not silently equate distinct outcomes, such as running economy and race performance,
or replace an unobserved construct with a conveniently available estimate. Record the
comparison protocol, uncertainty, and plausible alternative explanations. Do not invent
universal minimum detectable changes or observation windows where the evidence is absent.

## Candidate policy documentation

Retain the eight-section research packet structure. Include the measurement appraisal in
the scientific evidence section where relevant, and the following consistent assessment
for each candidate policy in the candidate coaching policies section. These are research
documentation conventions, not new J1 fields or application interfaces.

| Field | Required content |
| --- | --- |
| Policy ID and revision | Stable identifier, decision scope and relationship to earlier policies. |
| Decision and alternatives | The decision being made; relevant block objectives and feasible alternatives, including maintaining a productive prescription. |
| Constructs and outcomes | Underlying scientific variables and intended outcomes in each affected discipline. |
| Evidence and judgment | Direct and indirect supporting claims, transfer limits, unresolved questions, and which choices are methodology, preference or safeguards rather than empirical results. |
| Ideal observations | Reference-quality observations that would best inform the decision, even if unavailable today. |
| Minimum sufficient observations | Canonical inputs and quality or comparability conditions sufficient for the stated recommendation; do not require unrelated tracking. |
| Optional observations | Additional inputs, their incremental decision value, and when obtaining them is worth the burden. |
| Prescription requirements | Observations needed to generate a defensible recommendation at the proposed specificity. |
| Adherence requirements | Observations needed to establish actual exposure relative to the prescription; distinguish confirmed, partial, missed and unknown. |
| Effectiveness requirements | Comparable outcome observations, baseline, follow-up and relevant confounders needed to evaluate the subsequent response. |
| Scientific readiness | Evidence strength, directness, measurement validity, unresolved efficacy and independent review status. |
| Data readiness and applicability | Availability, continuity, quality, provenance and comparability of required canonical observations; classify prescription, adherence and effectiveness separately where they differ. |
| Missing-data implications | Which conclusions weaken or become unavailable when required or optional observations are missing, noisy or contradictory. |
| Candidate decision logic | Bounded proposed choices, assumptions, contra-indications, safety and referral boundaries, and authority to change the plan. |
| Fallback behavior | Qualitative guidance, hold, ask targeted feedback, propose a feasible conservative alternative, or defer as appropriate. |
| Prohibited inferences | Conclusions the available observations or scientific evidence cannot justify. |
| Richer-data extensions | How new observations could improve the decision, and what validation would still be needed. |
| Review status | Pending independent human review until explicitly reviewed; distinguish method review from evidence approval and operational adoption. |

### Prescription, adherence and effectiveness are distinct

A recommendation may be useful before its adherence or effectiveness is observable.
Do not make comprehensive tracking a prerequisite merely because it could help evaluate
an intervention later. The minimum data requirement depends on the decision and its
specificity. Illustrative examples:

| Decision | Generate a recommendation | Assess adherence | Evaluate effectiveness |
| --- | --- | --- | --- |
| Contextual protein guidance | Relevant body mass (for a mass-based target), goals, training and dietary constraints | Reported protein intake or relevant athlete feedback | Longitudinal outcomes and relevant confounders; intake alone does not establish benefit |
| Long-run fueling suggestion | Planned duration, intensity, tolerance and constraints | Reported fueling and session completion | Comparable session quality, tolerance and performance |
| Progress a lift | Comparable prior exposure, goal and sufficient effort/performance context | Actual sets, reps, load and relevant deviations | Subsequent comparable performance and fatigue context |

These examples are not approved prescriptions or exhaustive requirements. For instance,
observed protein intake is not inherently required to suggest a contextually appropriate
protein target; it is required to quantify adherence to that target. Missing intake
must never be read as zero intake. No recorded activity is not necessarily a missed
session. Missing feedback is not evidence of successful recovery.

### Applicability and readiness

Assess **scientific readiness** independently of **data readiness**. Scientific readiness
asks whether the relevant result is sufficiently appraised, applicable and independently
reviewed, whether the proposed inference is valid, and whether the decision methodology
has been reviewed or evaluated. Data readiness asks whether observations necessary for
a particular action are actually available with sufficient coverage and quality. Record
both with reasons. Neither implies the other, and neither alone establishes operational
approval. A strong scientific finding may be unusable with current observations; a fully
observed candidate policy may still lack evidence of benefit.

Use these data-applicability classifications for the stated decision and specificity:

| Classification | Meaning |
| --- | --- |
| Feasible | The minimum canonical observations are obtainable in the current context, subject to verified coverage and quality. |
| Conditionally feasible | Requires particular coverage, comparison conditions or targeted voluntary athlete feedback that is not assured. |
| Qualitative only | Contextual guidance is supportable, but quantitative individual prescription or adaptation is not adequately supported by the observations. |
| Deferred | Required observations are unavailable or unusable for the intended decision; also defer any action whose scientific, safety or approval prerequisites are unmet, recording that separate reason. |

Classifications are contextual and can differ across prescription, adherence assessment
and effectiveness evaluation. They are not evidence grades or permission to automate a
change. Record how missing optional inputs change confidence and specificity. If an input
is essential and absent, do not impute it as observed; ask for useful clarification, use
a separately defensible fallback, or defer. A restriction or safety concern may require
professional review rather than holding or progressing a plan. Preserve athlete approval
and existing hard constraints for any proposed change. Distinguish uncertainty from evidence
of no effect and avoid causal diagnoses from sparse or confounded histories.

## Provider capability inventory

Keep provider coverage in a mutable engineering inventory or dated contextual appendix,
separate from empirical claims and canonical policy definitions. It may describe Hevy,
Garmin, voluntary feedback and future providers such as Android Health Connect, but
provider field names, identifiers and API behavior do not belong in empirical claims.
For each canonical observation, distinguish advertised or anticipated capabilities from
verified samples, actual longitudinal coverage and decision-grade quality. Record the
verification date, source/provenance, units and resolution, transformation/estimate
method, permissions, gaps, comparability limits and known confounding or error. Sampled
availability is not proof of continuous history or reliable attribution.

The current working context includes strength exposure, running activities and summaries,
selected recovery observations, and voluntary athlete feedback. Calorie intake and weight
coverage are under investigation; macros, meal timing and richer health observations are
optional capabilities. This is a contextual snapshot, not a permanent list of allowable
scientific variables or a verified integration contract. Do not require a specific provider
if a defensible equivalent canonical observation can be obtained another way.

When richer observations become available, revisit the data-readiness assessment, proxy
appraisal and policy specificity. Reassess provenance, reliability and incremental decision
value rather than automatically making the new metric mandatory. Revise policies with a
versioned rationale when needed; an API change alone does not justify changing an empirical
claim, rewriting an archived packet or approving a policy.

## Evaluation and review

Extend each packet's synthetic evaluation cases to include paired histories with adequate,
missing, noisy, contradictory or non-comparable observations, and equivalent canonical
observations from different sources. State admissible recommendations, required uncertainty
disclosures, forbidden inferences, fallback actions, and whether adherence and effectiveness
can be assessed separately. Test that missing optional tracking does not unnecessarily block
an otherwise defensible recommendation and that missing essential evidence does not enable
unsupported quantitative adaptation.

Keep software conformance separate from physiological or coaching efficacy. Prospective
assessment should use comparable outcomes, coverage, adherence, uncertainty and alternative
explanations, with appropriate baseline policies and review. Do not claim that a proxy or
adaptive policy improves outcomes merely because deterministic tests pass. Include these
checks in the packet's human review checklist. All new claims and programming methods
remain pending independent review under the existing research and J1 release procedures.
