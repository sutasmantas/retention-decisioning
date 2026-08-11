# SignalRoom research decision

Date: 2026-08-05

## Decision

SignalRoom should remain a value-aware intervention decision system, with a
later routed estimator/evaluation benchmark rather than a homemade “advanced
uplift” rewrite:

1. retain risk prediction only as a forecasting and risk-only policy control;
2. retain difference in means and the current T-learner as frozen intervention
   and software controls;
3. admit matched S/T/X, R/DR, one causal forest and one direct uplift forest to
   a later isolated multi-estimator comparison;
4. require cross-fitting, overlap diagnostics, calibration and repeated outer
   evaluation rather than treating the estimator class as the technique;
5. evaluate ranking with a panel and uncertainty, then evaluate the exact
   deployed rule with IPW/SNIPS/DR policy value, regret and equal-capacity
   baselines;
6. route by non-dominated operating region across data regime, objective,
   capacity, cost and resources; do not crown a universal winner;
7. treat no-harm, fairness, observational sensitivity, transport, multi-arm and
   dynamic decisions as conditional profiles with explicit entry data;
8. preserve the existing result/action contract and restrict custom work to
   adapters, provenance, client utility and routing.

No experiment, data/model download, implementation, dependency, UI change,
merge, push, polish, or production claim is authorized by this decision.

## Consequential external answers

| Question | External answer | Confidence and consequence |
| --- | --- | --- |
| Is churn risk a valid intervention score? | no; outcome risk and treatment response are different estimands | **Established:** keep risk only as a baseline |
| Does a positive ATE support personalized targeting? | no; current Hillstrom targeting intervals and the broader literature separate broad effect from heterogeneity/policy value | **Established:** preserve `PROMOTE_AVERAGE_EFFECT_ONLY` |
| Is one meta-learner enough? | surveys and cross-stream benchmarks identify meta, direct uplift, forest and orthogonal families with regime-dependent behavior | **Established:** compare a bounded cross-family set |
| Is R/DR or causal forest automatically superior? | theory supplies robustness/inference under assumptions; systematic benchmarks show volatility and no universal ordering | **Established family, unknown local order:** require controlled comparison |
| Is Qini a deployment gate? | it is useful prioritization evidence but can be high-variance, convention-sensitive and misaligned with calibrated threshold/policy objectives | **Contested sufficiency:** use a metric panel and exact policy value |
| Can outcome adjustment solve metric problems? | it can reduce variance on RCT evaluation | **Established but bounded:** compare it; it does not repair objective mismatch |
| Should CATE scores be calibrated? | calibration work shows ranking and effect level are different and supports cross-fitted calibration | **Established:** measure calibration before sign/value thresholding |
| Is current IPW value enough? | IPW is transparent but high-variance; SNIPS and DR provide distinct checks under assumptions | **Established:** evaluate the frozen policy with all three |
| Does Hillstrom validate no harm? | no; it lacks unsubscribe, complaint and long-run adverse outcomes | **Established data boundary:** mark no-harm unavailable |
| Can Hillstrom results transfer to Criteo or clients? | internal validity does not establish target-population validity | **Established:** compare conclusion stability only; no fitted-model/claim transfer |
| Should multi-arm, dynamic, survival or interference methods enter now? | those are genuine techniques for different treatment/timing/outcome/identification contracts | **Established but out of scope:** reserve until the product question changes |

## Candidate and duplicate disposition

| Family/candidate | Disposition | Why |
| --- | --- | --- |
| Difference in means / ATE | retain core control | most defensible randomized broad-intervention answer |
| Current logistic T-learner | retain software/technique control | transparent and already frozen; failed stronger targeting promotion rather than being post-hoc tuned |
| S-learner | admit matched meta candidate | lower-complexity shared model tests treatment-interaction regularization |
| X-learner | admit matched meta candidate | distinct treatment-imbalance behavior relevant to Criteo |
| R-learner | admit orthogonal candidate | tests residualized loss and nuisance separation |
| DR-learner | admit orthogonal/DR candidate | supports DR effect/policy seam with cross-fitting and trimming sensitivity |
| EconML CausalForestDML | first Python forest candidate | distinct flexible honest/orthogonal profile on maintained Python surface |
| GRF causal forest | oracle, not product runtime | strongest diagnostic/RATE reference but adds an R environment |
| CausalML uplift forest | first direct-uplift candidate | covers treatment-aware splitting missing from HTE-only comparison |
| Bayesian causal forest | research reserve | genuine different prior structure, but another runtime before a documented gap |
| CATENets/neural HTE | research reserve | distinct high-dimensional family; public tabular marketing case does not justify first integration cost |
| OAR | conditional overlap reserve | recent/no-release code; only useful after a controlled weak-overlap failure |
| TMLE | subgroup/targeted-parameter reserve | valuable but duplicates immediate DR question unless subgroup inference is the deliverable |
| pROCini and balanced ranking | conditional metric challengers | credible work conflicts; require maintained code and parity fixtures before use |
| Policy tree | conditional after simple policy | learned allocation must beat a calibrated threshold/equal-capacity rule on outer holdout |
| MAQ | design oracle | multi-action uncertain-cost optimizer exceeds current binary action contract |
| No-harm/safe policy | conditional profile | requires an adverse outcome and conservative acceptance rule absent from Hillstrom |
| DoWhy/DoubleML sensitivity | conditional observational tools | do not add confounding machinery to a randomized benchmark without an observational question |
| Multi-arm/dynamic/survival/interference/non-compliance | scope reserve | changes the estimand or data contract; not a missing binary-uplift technique |

Higher complexity did not itself reject a candidate. Immediate candidates were
limited when maintained implementations answer the same question with a
smaller shared surface. Reserves remain explicit so a later observed failure
can reopen them without another unbounded search.

## GitHub reuse decision

The first future benchmark seam is
`binshuangli/uplift-bench@604cf7caee4f2f1322e0eac81968161741c7a99f`
in an isolated Python 3.12 environment. Its adapter, outer-test-isolated
orchestration, dataset/objective matrix, failure capture and provenance solve
the larger integration problem better than custom SignalRoom benchmark code.
Because it was submitted on 2026-08-02 and is under review, its empirical
conclusions remain provisional.

The primary maintained Python estimator surface is EconML `v0.17.0` at
`f0fc2e7d39d20e1a9d9201233fb7945e88cab0cc`. CausalML `v0.17.0` at
`77ee0a793b18818f18d49b42bc8b7a988e68432c` supplies the direct uplift-tree/
forest challenger. GRF, policytree, MAQ, DoubleML, DoWhy,
causalCalibration, CATENets and OAR remain pinned reproduction or conditional
oracles. Scikit-uplift remains historical cross-check evidence only.

Custom work is restricted to a thin SignalRoom frame/result adapter,
manifest/provenance, client value/harm/capacity composition and routing. The
project must not implement estimator, forest, calibration, metric, off-policy,
sensitivity, dataset-loader or benchmark-orchestration logic from scratch.
License was not researched or used as a decision signal.

## External answer versus experiment queue

| Item | Reuse level | Local work required? |
| --- | --- | --- |
| Estimand and technique taxonomy | adopt/triangulate surveys and guides | no |
| No universal estimator | triangulate systematic and current benchmarks | no |
| Metric/objective mismatch | triangulate metric and policy literature | fixture parity later; no broad rediscovery run |
| SignalRoom estimator routing | applicable external results conflict by regime | yes, S2 after S0/S1 authorization |
| Overlap/nuisance behavior | external theory closes the risk; local regime matters | yes, controlled S3 |
| Policy value under costs/capacity | utility is deployment-specific | yes, controlled S5 |
| Hillstrom-to-client transport | external evidence closes that it is unsupported | target validation later, not model transfer |
| No-harm policy | external evidence closes the data requirement | no run until a harm outcome exists |
| Multi-arm/dynamic/interference | external evidence closes that the contract differs | no current experiment |

## Exact first controlled experiment

The exact next experiment is **S0 baseline, environment and artifact
reconciliation** from `BENCHMARK_DESIGN.md`. Freeze the SignalRoom source,
constraints, current synthetic and Hillstrom artifacts, split lineage, feature
allowlist, metrics, 15 tests and service configuration at commit `ecbf009`.
Record the pandas 3.0.5 uncontrolled compatibility failure and the pinned
pandas 2.2.3 pass. S0 uses no data/model download and makes no estimator or UI
change. Only a later checkpoint may authorize S1.

## Expertise disposition

`docs/EXPERTISE_NOTES.md` preserves the existing real-RCT note and records five
additional consequential decisions:

1. match uplift evaluation to the deployed decision rule;
2. inspect overlap and nuisance support before personalizing;
3. calibrate treatment-effect scores before sign/value thresholding;
4. treat harm as a separate constrained outcome;
5. validate targeting conclusions under campaign/population shift.

The old note maps to the existing central card about beating an equal-capacity
baseline. Four new buyer-retrieval cards are proposed for decision-rule
alignment, overlap, harm and campaign shift. Calibration is deliberately
unindexed because it is a technical control inside the broader decision-rule
card, not a distinct buyer trigger.

## Known limitations and claim boundary

- No S/X/R/DR learner, causal/uplift forest, calibration method, RATE, new
  metric, policy tree, sensitivity tool or no-harm model was run.
- No Criteo, IHDP, ACIC, Jobs, synthetic stress, data or model was downloaded.
- Published results differ in data, DGP, outcome, assignment, base learner,
  tuning, metric, capacity, seed and compute; their numbers are not placed on a
  fake common leaderboard with SignalRoom.
- UpliftBench is extremely recent and under review; its design is reusable but
  its numerical conclusions are provisional.
- Qini/pROCini/balanced-ranking sufficiency remains contested.
- Real randomized trials do not reveal both potential outcomes per unit; PEHE
  is reserved for known-effect simulations/semi-synthetic data.
- Current Hillstrom evidence supports only a two-week average visit effect for
  Mens email versus control. It does not support individualized targeting,
  churn reduction, revenue, long-term retention, no-harm, transport or
  production deployment.
- The global pandas 3.0.5 compatibility failure remains a bounded technical
  limitation even though the repository's frozen pandas 2.2.3 stack passes.
- A dossier `PASS` approves only a future controlled queue. It is not evidence
  that a new technique works.

## Systematic gate result

| Gate | Evidence | Status |
| --- | --- | --- |
| Problem decomposition | eleven independent estimand/estimator/evaluation/policy decisions in `TECHNIQUE_TAXONOMY.md` | PASS |
| Search protocol | dated sources, rules, query families, review labels and exclusion criteria recorded | PASS |
| Survey coverage | uplift review, systematic benchmark, meta/orthogonal/forest work and 2026 practical guide followed | PASS |
| Benchmark coverage | Hillstrom, corrected Criteo, IHDP, ACIC, Jobs, controlled DGPs, leak/DGP criticism and objective-aware benchmark recorded | PASS |
| Existing-answer search | every consequential question has an external-answer/local-experiment disposition | PASS |
| Technique-family saturation | two consecutive breadth expansions added variants/different contracts but no immediate family | PASS |
| Candidate comparison | estimand, assumptions, data regime, objective, resources, integration and failure routes compared | PASS |
| Contrary evidence | no-universal-winner, Qini variance/objective mismatch, ranking-metric dispute, DGP bias, Criteo leak, weak overlap and transport limits included | PASS |
| Implementation evidence | twelve repositories pinned; adoption, duplication, environment, download, maintenance and custom-logic boundaries recorded | PASS |
| Portfolio fit | SignalRoom's distinct risk-versus-effect/value/capacity evidence and proposal-safe boundaries recorded | PASS |
| Review status | conclusions labelled established, provisional, contested or unknown; queue and claim boundary explicit | PASS |

**Dossier result:** `PASS`. SignalRoom is ready only for the later S0
reconciliation specified above. This dossier does not authorize it.
