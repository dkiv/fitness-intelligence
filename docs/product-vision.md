# Fitness Intelligence

Fitness Intelligence aims to be an adaptive coaching platform for athletes seriously pursuing
both strength and endurance performance. It will create and continuously improve coordinated
strength, running and nutrition plans using each athlete's training history, recovery signals,
actual performance and feedback. Athletes will keep recording workouts and food in their
existing apps. Food logging, GPS tracking and workout recording are outside the product scope.

## The athlete's week

An athlete sets goals, available days, injury constraints and exercise preferences. The coach
uses these alongside longitudinal history, long-term goals and target events to select a
multiweek training block. Even the first seven-day schedule must advance that block's objective.
The coach can use different periodization approaches as the evidence, athlete's constraints
and individual response warrant. The athlete can see
how lifting and running sessions fit together and, as evidence permits, how to fuel them.
Fitness Intelligence owns the canonical prescription and its revision history. Hevy and Garmin
serve as execution platforms. With athlete approval and authorized write access, the platform
can publish strength routines to Hevy and structured running workouts to Garmin. Athletes can use the
exported plan if they prefer manual entry.

At review time, the coach compares the prescription with completed sessions, tracks progress,
adherence and training exposure, and asks how the week felt. For example, if the athlete says
a hard run left their legs tired for a scheduled squat session, the coach can propose moving
next week's run. It shows the original and proposed schedules, cites the athlete's report and
available performance history, and explains how uncertain the benefit is. The proposed move
must still fit the block's training emphasis and recovery plan. If that intent needs to change,
the athlete reviews a block revision. Every change to a
scheduled workout and every publication requires explicit athlete approval. Recommendations,
decisions, plan versions and subsequent outcomes remain available for review and evaluation.

## Evidence behind the plan

Hevy, Garmin, Android Health Connect and compatible future sources will contribute to a unified
history of lifting, running, sleep, heart-rate variability, resting heart rate, body weight and
calorie intake as permissions and record availability allow. Analytics must be reproducible
independently of the language model. Reports distinguish measured observations from estimates
and describe correlations as hypotheses. Missing recovery data leaves recovery uncertain.

The coach must ground scientific claims in a curated, versioned body of peer-reviewed exercise
science. Athletes should be able to trace a claim to its source, see whom it applies to and
understand where findings disagree. A coaching method offers a way to structure a block.
An athlete's own observations help decide whether to continue it. Neither establishes that
the method caused an outcome. See [coaching science and evaluation](coaching-science.md).

Planning uses explicit constraints and conservative progression and adaptation rules. The
language model supports conversation, captures preferences, orchestrates structured tools and
explains their results. The minimal coach can start with strength history and athlete feedback.
Endurance, recovery and nutrition evidence will improve its prescriptions incrementally.

## Current scope

Development started with a local API and PostgreSQL foundation. Main includes the canonical
strength schema, a private read-only Hevy importer, bounded verification tools and internal
strength analytics. The personal historical import and subsequent integrity checks completed
locally. Public access requires authentication and tenant-isolation testing. Adaptive
plans, fueling recommendations and workout publishing are future capabilities. The
[roadmap](roadmap.md) records implementation status, dependencies and acceptance criteria.
