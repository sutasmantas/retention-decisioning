# SignalRoom GitHub implementation audit

Date: 2026-08-05

## Audit boundary

Repository components were checked before admitting any substantial custom
logic. The audit compares implemented estimators, metrics, policy/evaluation
seams, maintenance, runtime compatibility, downloads, and integration cost.
No repository was cloned into
SignalRoom, no data/model was downloaded, and no dependency or application
code changed during this dossier.

The current project originated from GitHub and its real-data slice already
refit bounded patterns from public repositories. This audit is stricter: a
future experiment must adopt a maintained estimator/evaluator where one exists
instead of rebuilding it inside SignalRoom.

Repository heads were resolved with `git ls-remote` and release/activity fields
were read from GitHub on 2026-08-05.

## Component comparison

| Repository and pin | Reusable component | Runnable/maintenance evidence | Integration cost and hazard | Decision |
| --- | --- | --- | --- | --- |
| `binshuangli/uplift-bench` `604cf7caee4f2f1322e0eac81968161741c7a99f` | 12 estimators, 25 instances/7 dataset families, six objectives, outer-test-isolated repeated CV, adapters, manifests and committed results | pushed 2026-08-02; one commit; no release; repository accompanies arXiv `2608.00915`; Python >=3.11,<3.13; core/full reproduction documented | new and under review; about 2 GB excluding Criteo and reported 20/26 core-hours; current SignalRoom development badge is Python 3.13, so it requires a separate 3.12 environment | **Adopt first as an isolated benchmark surface; treat numerical findings as provisional** |
| `py-why/EconML` release `v0.17.0`, commit `f0fc2e7d39d20e1a9d9201233fb7945e88cab0cc` | S/X learners, NonParamDML/R-style orthogonal estimation, DRLearner, CausalForestDML, RScorer, inference, DR policy trees/forests and cost interpretation | release published 2026-08-04; release notes cover sklearn 1.7/1.8/1.9 and DRLearner sample trimming; unified sklearn-style Python API | substantial optional numerical stack; candidate APIs and inference assumptions differ; must pin extras and prohibit implicit model/data retrieval | **Primary future Python estimator surface** |
| `uber/causalml` release `v0.17.0`, commit `77ee0a793b18818f18d49b42bc8b7a988e68432c` | S/T/X/R/DR-style meta-learners, uplift tree/forest criteria, uplift metrics and synthetic data | release published 2026-07-04; repository pushed 2026-08-04; documented campaign-targeting use; some APIs explicitly experimental | overlaps EconML for meta-learners and brings another large runtime; metric/tie conventions need fixture parity | **Isolated direct-uplift challenger and metric oracle; do not add both full runtimes to the product** |
| `grf-labs/grf` `5bee99b51471f76cb2d63acbc8a9b0ffec408ba0` | honest causal forest, overlap diagnostics, calibration/BLP, AIPW scores, RATE/TOC, policy-value examples | official R/C++ paper implementation; pushed 2026-04-30; extensive diagnostic and guide material | second language/runtime and different defaults; not a thin product dependency | **Reference/reproduction oracle for forest, calibration, overlap and RATE** |
| `grf-labs/policytree` `b543f0fa35dcb4cbe97e28d102b20523e2fcedaf` | shallow policy trees over doubly robust scores | official package pushed 2026-08-04; documented policy learning/evaluation seam | R environment; policy overfitting if evaluation is not outer-held-out | **Policy-learning oracle after simple rules pass; no current runtime integration** |
| `grf-labs/maq` `3d00392181de57f1ebe337dc523023b3c25db26c` | multi-action allocation under variable costs and budgets | official peer-reviewed implementation; pushed 2026-08-04 | multi-treatment R contract exceeds SignalRoom's current binary action | **Adopt cost/budget protocol ideas; integrate only if action contract expands** |
| `DoubleML/doubleml-for-py` release `0.11.3`, commit `caac090f6a16ba50263d659544c5cef4da182924` | DML estimators, repeated cross-fitting, policy trees and sensitivity bounds | release published 2026-05-22; pushed 2026-07-20; official sensitivity guide and Python API | overlaps EconML for orthogonal estimation; separate result objects and dependency surface | **Sensitivity/orthogonal-inference oracle; add only for a named gap** |
| `py-why/dowhy` release `v0.14`, commit `1d1efe77b092661252038baad72dc5d53e35ebfa` | causal graphs, identification, refuters and multiple sensitivity analyses | release published 2025-11-08; repository pushed 2026-08-05; official refuter documentation | graph/observational workflow is unnecessary for randomized Hillstrom; can encourage ritual refuters without a defensible graph | **Conditional observational-assumption adapter only** |
| `Larsvanderlaan/causalCalibration` `fdaad7b823ce0acb8040d11f1c342510e2e4b627` | reference R implementation of cross-fitted causal isotonic calibration | official paper repository; pushed 2026-04-15; no release and no open issues at audit | R-only research surface; requires strict fold isolation and metric parity | **Calibration reproduction oracle; port only through verified fixtures or call in an isolated benchmark** |
| `AliciaCurth/CATENets` `f8c961c307766609aec62cf95ca6e8b2363dfca7` | JAX implementations of SNet/FlexTENet/OffsetNet, TARNet/CFRNet/DragonNet-family estimators and published benchmark configs | official paper repository; pushed 2024-06-22; no release; two open issues at audit | JAX and neural training stack, extra tuning/compute, overlapping estimands | **Neural research reserve; do not integrate before a documented classical/forest failure** |
| `Valentyn1997/OAR` `e8c669dbd1c64d51e3d1a4332155f7877b2250d8` | official overlap-adaptive regularization experiments and estimator code | ICLR 2026 paper repository; pushed 2026-06-01; no release | recent experimental implementation and another model stack; relevant only under weak overlap | **Provisional overlap-stress challenger, not a default estimator** |
| `maks-sh/scikit-uplift` release `v0.5.1`, commit `0038e659428f6e7a49b935b850651cd9a9db3f54` | Qini/uplift metrics, basic meta-models and datasets | last release 2022-08-11; last push 2023-10-21; current SignalRoom used it only for an independent metric cross-check | stale as a production dependency and redundant with newer surfaces | **Retain cross-check evidence only; do not add to runtime** |

## Component-level reuse plan

| Needed capability | Adopt/refit/custom decision | Reason |
| --- | --- | --- |
| Multi-estimator benchmark orchestration | **Adopt/refit** UpliftBench's outer-test-isolated runner and `from_frame`-style adapter in Python 3.12 | avoids writing a bespoke leaderboard and already records folds, objectives, failures and provenance |
| S/X/R/DR and causal forest | **Adopt** pinned EconML estimators | maintained common Python surface compatible with sklearn 1.8 |
| Direct uplift tree/forest | **Adopt** pinned CausalML in an isolated optional adapter | fills a genuine technique-family gap not supplied by the current T-learner |
| Forest diagnostics and RATE | **Adopt/triangulate** GRF outputs and fixtures | mature implementation; avoids a custom inference/RATE port without parity |
| Effect calibration | **Adopt/triangulate** `causalCalibration`; expose fold/result contract through the harness | avoids inventing treatment-effect calibration |
| Policy value | **Adopt** DR/AIPW score implementations from EconML/GRF; retain current IPW only as a transparent control | current custom IPW is not sufficient evidence for the broader panel |
| Cost and budget allocation | **Refit** MAQ/policytree protocol; retain custom binary value/cost/capacity composition | SignalRoom-specific utility is valid glue; optimizer internals are not |
| Sensitivity | **Adopt** DoubleML or DoWhy only under an observational profile | randomized Hillstrom does not need a confounding theatre layer |
| Dataset loaders/splits | **Adopt** UpliftBench or owner adapters and pin content hashes | prevents repeated leak/split mistakes, especially for corrected Criteo |
| Result/provenance schema | **Custom thin seam only** | SignalRoom must connect estimator outputs to its value/action contract without copying algorithms |
| Harm and fairness rules | **Custom policy composition over adopted estimates only** | acceptance criteria are client-specific, but estimators/bounds must come from maintained research code |

## Rejected custom logic

The dossier rejects writing the following inside SignalRoom:

- S/X/R/DR learners, causal/uplift forests, neural representation learners, or
  propensity/outcome cross-fitting engines;
- causal-forest inference, overlap tests, RATE/TOC, pROCini, balanced ranking,
  causal isotonic calibration, TMLE, or conformal ITE machinery;
- generic IPW/SNIPS/DR off-policy estimators or policy-tree optimizers;
- Criteo/IHDP/ACIC/Jobs loaders, published benchmark simulations, or repeated
  nested-CV orchestration when the selected harness supplies them;
- an unbounded plugin architecture that imports every research framework into
  the application runtime.

Small custom code remains justified for the SignalRoom data-to-harness adapter,
content/provenance manifest, normalized candidate-result schema, client utility
and capacity composition, action routing, and explicit unavailable/failure
states.

## Required later integration checks

Research admission is not implementation approval. Each admitted component
must later pass:

1. a pinned isolated install and dependency lock with no surprise data/model
   download on import or service startup;
2. one success fixture, one malformed-input failure, one unsupported-estimand
   failure, and one candidate-runtime failure;
3. explicit treatment/outcome/feature/propensity shapes and no post-treatment
   feature access;
4. split/fold lineage proving that nuisance, calibration, policy selection and
   final test are isolated;
5. one published or owner fixture reproducing estimator/metric conventions;
6. identical base learners and tuning budget wherever the family comparison
   permits it;
7. result fields for seed, folds, package/commit, environment, data hash,
   metric version, ties, propensity handling, runtime and failures;
8. disable/fallback behavior that leaves the current SignalRoom product and
   frozen Hillstrom evidence usable.

## Maintenance boundary

Repository activity does not establish statistical validity, and a paper does
not establish maintainable software. Both were required for an adoption
decision. UpliftBench's code is the best first benchmark seam but its findings
remain provisional because of its age and review status. EconML is the primary
Python implementation surface; CausalML, GRF, policytree, MAQ, DoubleML,
DoWhy, causalCalibration, CATENets and OAR remain bounded challengers or
oracles. Their logic must not be copied into a second homemade framework.
