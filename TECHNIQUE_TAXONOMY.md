# SignalRoom technique taxonomy

Date: 2026-08-05

## Decision boundary

SignalRoom has two different estimands and one downstream action problem:

1. ordinary churn risk predicts who may leave;
2. conditional treatment effect estimates whose outcome may change because of
   an intervention; and
3. a policy chooses actions under capacity, value, cost, uncertainty, and harm
   constraints.

The dossier asks which evidence and component families are needed to make the
second and third claims defensible. It does not authorize a new model run,
dataset download, dependency, product route, or UI change. The current real
benchmark remains the frozen Hillstrom Mens-email-versus-control T-learner run.

## Problem decomposition

| Decision | Why it is independent | Required evidence |
| --- | --- | --- |
| Estimand | response prediction, ATE, CATE ranking, and policy value answer different questions | explicit treatment, control, outcome horizon, unit, and target population |
| Identification | randomized assignment closes measured confounding but not interference, attrition, non-compliance, or transport | assignment audit, leakage checks, overlap and outcome availability |
| Estimator family | S/T/X/R/DR learners, direct uplift, forests, Bayesian and representation learners make different bias/variance assumptions | identical split, base learners, tuning budget, and repeated seeds |
| Nuisance estimation | outcome and propensity errors can dominate orthogonal/DR estimators | cross-fitting, calibration, clipping/trimming, overlap diagnostics |
| Ranking evaluation | Qini/AUUC/RATE and related metrics assess prioritization, not calibrated effect levels | held-out randomized data, uncertainty, tie conventions, multiple metrics |
| Effect calibration | a good order can still put the zero-benefit threshold in the wrong place | out-of-fold calibration and calibration plots/tests |
| Policy evaluation | ranking quality does not establish the value of the deployed threshold or budget | IPW/SNIPS/DR value, equal-capacity baselines, regret and confidence intervals |
| Economic action | benefit depends on customer value, action cost, capacity and possibly uncertain cost | frozen utility contract and sensitivity grid |
| Safety/no-harm | average utility can hide adverse individual or group outcomes | separately measured harm outcome and conservative constraint |
| Robustness | weak overlap, imbalance, sparse outcomes and seed choice can reverse rankings | synthetic/semi-synthetic stressors and repeated outer splits |
| Transport | internal validity on one campaign does not establish another population or horizon | target-population validation and cross-campaign stability |

## Search protocol

- Search date: 2026-08-05.
- Time window: foundational work plus current sources through the search date;
  recent 2026 preprints are retained only as provisional evidence.
- Sources: peer-reviewed papers, official paper pages, official documentation,
  dataset-owner pages, and official GitHub repositories. Secondary material was
  used only to locate a primary source.
- Starting anchors: the 2017 uplift review, the 2022 systematic benchmark, the
  2026 practical HTE guide, current metric/policy literature, and maintained
  EconML, CausalML, GRF, DoubleML, DoWhy, and UpliftBench implementations.
- Query groups: uplift/HTE surveys; S/T/X/R/DR and direct learners; causal and
  uplift forests; calibration; Qini/AUUC/RATE/pROCini; high-variance RCT
  metrics; policy value/regret; cost/capacity; overlap/sensitivity;
  transportability; safe/no-harm policy; datasets and benchmark leakage; and
  GitHub implementation/reproduction code.
- Admission rule: a family enters the immediate queue only if it changes a
  decision under SignalRoom's one-shot, binary-treatment, pre-treatment-feature
  contract and can be compared without changing the estimand.
- Saturation rule: stop only after two consecutive breadth expansions add no
  decision-relevant technique family. Variants, different estimands, and
  unsupported data contracts are recorded rather than counted as new immediate
  candidates.
- Exclusion rule: repository popularity is weak maintenance evidence only.
  License was not researched or used as a filter.

## Survey and benchmark anchors

| Source | External answer | Review status | SignalRoom consequence |
| --- | --- | --- | --- |
| Gutierrez & Gérardy, *Causal Inference and Uplift Modelling* (PMLR 2017) | separates two-model, class-transformation, and direct uplift approaches | established survey | do not compare only meta-learners |
| Rößler & Schoder, *Bridging the Gap* (2022) | 15 methods across 27 synthetic and six real datasets; no universal winner and material method volatility | established systematic benchmark with binary/Qini boundary | compare uplift and HTE streams under more than one objective |
| Künzel et al., meta-learners (PNAS) | S/T/X are reductions whose relative behavior depends on treatment imbalance and response surfaces | established | use matched base learners and report regime dependence |
| Nie & Wager, R-learner; Kennedy, DR-learner | orthogonal/pseudo-outcome learners reduce sensitivity to nuisance error under their assumptions | established | require cross-fitting and nuisance diagnostics, not acronym-only adoption |
| Wager & Athey / GRF | honest forests support flexible HTE estimation and inference; GRF adds calibration, overlap and RATE diagnostics | established | causal forest is a distinct nonparametric profile |
| Practical HTE guide (2026) | estimand, honesty, cross-fitting, calibration and transport must precede personalized claims | recent peer-reviewed practical synthesis | treat workflow controls as part of the technique, not post-hoc documentation |
| UpliftBench preprint/repository (submitted 2026-08-02) | broad objective-aware benchmark; reports severe Qini/effect-accuracy mismatch in some regimes and no universal estimator | provisional: very recent, single-author, under review | reuse its isolated harness first, but do not promote its numerical conclusions as settled |
| Curth et al., *Really Doing Great...* | common IHDP/ACIC designs can favor methods through their data-generating process | established contrary benchmark evidence | no single semi-synthetic leaderboard selects SignalRoom's model |

## Technique families

### 1. Risk and average-effect controls

- **Risk model:** useful for forecasting, but it cannot identify intervention
  response. Retain only as a product baseline.
- **Difference in means / ATE:** primary randomized-experiment sanity check and
  a valid broad-treatment answer. It cannot establish profitable targeting.
- **Treat-none, treat-all, random and equal-capacity policies:** mandatory
  decision baselines. A personalized policy must beat the feasible alternative,
  not merely produce a positive model score.

Status: established controls; retained.

### 2. Outcome-model meta-learners

- **S-learner:** one outcome model with treatment as a feature. Low integration
  cost but can regularize treatment interactions away.
- **T-learner:** separate treated/control outcome models. Transparent and
  current SignalRoom baseline; variance can grow when an arm is small.
- **X-learner:** imputes effects and combines arm-specific estimates; especially
  plausible under treatment imbalance.

Status: established family. S/T/X enter the matched meta-learner profile; the
T-learner remains a software control rather than the presumed winner.

### 3. Orthogonal and doubly robust learners

- **R-learner / residual-on-residual loss:** targets CATE after removing outcome
  and treatment nuisance components.
- **DR-learner / AIPW pseudo-outcome:** combines outcome and propensity models;
  it can be consistent when one nuisance side is correctly specified, subject
  to regularity and overlap.
- **TMLE/targeted learning:** valuable for targeted parameters and subgroup
  inference; it is a reserve rather than a separate first estimator because the
  immediate policy evaluation already needs DR scores and cross-fitting.

Status: established, but not uniformly superior. Enter R and DR with explicit
cross-fitting, propensity diagnostics, clipping/trimming sensitivity, and
matched nuisance budgets.

### 4. Direct uplift and transformed-outcome methods

- class transformation, transformed outcomes, uplift trees and uplift random
  forests optimize a transformed or split criterion closer to targeting;
- U-KL, U-ED and U-CHI represent distinct uplift-tree criteria in prior
  benchmarks;
- their score scale and metric conventions may not be calibrated CATE.

Status: established and decision-relevant. At least one maintained uplift-tree
or forest implementation must challenge the HTE learners. Do not hand-code its
split criteria or metric stack.

### 5. Causal forests

- honest causal forests estimate flexible heterogeneity with sample splitting
  and inferential machinery;
- EconML's `CausalForestDML` supplies a Python route; GRF is the reference
  implementation for calibration, overlap-aware analysis, AIPW scores and RATE;
- forest uncertainty is not an individual counterfactual guarantee.

Status: established distinct profile. Enter one Python causal-forest candidate
and use GRF as a reproduction/diagnostic oracle rather than adding an R runtime
to the product.

### 6. Bayesian and neural representation learners

- Bayesian causal forests explicitly separate prognostic and treatment-effect
  structure and can be strong in some benchmark regimes;
- TARNet/CFRNet/DragonNet and CATENets-style architectures learn shared and
  treatment-specific representations;
- recent structural-bias work reports neural robustness in selected settings,
  but public real marketing data, compute and calibration do not justify making
  this the first SignalRoom comparison.

Status: real family, research reserve. Reopen only after the lower-cost
meta/forest/DR profiles leave a specific failure unanswered.

### 7. Effect calibration and uncertainty

- causal isotonic calibration uses cross-fitted nuisance predictions to align
  estimated and observed treatment-effect structure;
- two-stage HTE calibration is useful when thresholds, budgets, multiple
  outcomes, or treatment choices depend on score level;
- conformal counterfactual/ITE intervals address a different uncertainty
  question and require assumptions that must be stated; no observed unit
  reveals both potential outcomes.

Status: calibration is an immediate evaluation layer; conformal individualized
intervals are a provisional reserve. A ranking model may not drive a sign
threshold until calibration is measured.

### 8. Ranking metrics

- **Qini/AUUC/uplift-at-k:** intuitive randomized-data targeting curves, but
  noisy and convention-sensitive; ranking can ignore score level.
- **RATE/TOC:** prioritization metrics with inferential support; implemented by
  GRF.
- **pROCini:** proposes stronger theoretical grounding using negative outcomes
  and an optimal-deployment gain construction.
- **balanced causal ranking:** recent contrary work argues conventional Qini and
  related metrics can remain biased on RCTs and challenges alternatives.
- **outcome adjustment:** published evidence shows covariate adjustment can
  reduce high variance in randomized uplift evaluation.

Status: metric choice is contested. Use a panel, predeclare definitions and
ties, and report disagreement. Do not write a bespoke pROCini or balanced
metric until maintained reproduction code and fixture parity exist.

### 9. Policy evaluation and learning

- **IPW/SNIPS:** transparent randomized-policy estimators; IPW may have high
  variance and SNIPS changes finite-sample behavior.
- **DR/AIPW policy value:** combines reward/outcome and assignment models to
  improve the bias/variance tradeoff under stated assumptions.
- **policytree / EconML DR policy trees:** learn interpretable policies from DR
  scores under honest evaluation.
- **MAQ:** solves multi-action allocation with variable costs and budgets; for
  the current binary action it is a cost-aware reference, not an immediate
  multi-treatment runtime.

Status: DR held-out value and regret are immediate; learned policy trees are
conditional on a stable benefit over simpler thresholded/equal-capacity rules.

### 10. Cost, capacity, harm and fairness

- utility must combine incremental outcome, customer value, action cost and
  capacity; capacity sweeps can reverse candidate rankings;
- uncertain/variable costs require sensitivity or robust allocation rather
  than a single assumed price;
- harm is not the negation of average benefit. Safe/no-harm policies require a
  separate adverse outcome or a defensible partial-identification bound;
- fairness-constrained policy learning is a genuine family, but SignalRoom's
  current public benchmark has no approved protected-attribute policy contract.

Status: value/cost/capacity is immediate. No-harm and fairness are conditional
profiles. Hillstrom cannot validate them because unsubscribe, complaints,
long-run harm, and a protected-group policy objective are absent.

### 11. Overlap, sensitivity and transport

- Hillstrom's randomized assignment gives strong marginal overlap; future
  observational data still require propensity distributions, effective sample
  size, trimming and subgroup support;
- OAR is a new overlap-adaptive CATE proposal with public code, but remains a
  provisional stress candidate rather than a default;
- DoWhy and DoubleML supply sensitivity analyses for unobserved confounding;
  they do not manufacture identification from unsupported data;
- internal validity on Hillstrom does not establish another campaign,
  population, outcome or horizon. Cross-dataset work can compare conclusion
  stability, not transfer the fitted Hillstrom model to Criteo.

Status: overlap diagnostics and controlled stress are immediate. Observational
sensitivity and transport are conditional on the deployment data contract.

## Workload taxonomy

| Workload | What it can answer | What it cannot answer | Disposition |
| --- | --- | --- | --- |
| Current synthetic SaaS data | product/API regression and known generated policy behavior | real intervention efficacy or transport | retain as software control only |
| Hillstrom Mens email vs control | randomized average effect, held-out prioritization and binary policy evaluation | churn, long-term retention, harm, temporal shift or ITE truth | retain as first real RCT workload |
| Corrected Criteo uplift data | large, imbalanced randomized advertising ranking and scale behavior | named features, general customer retention or full-scale result from a sample | later scale/imbalance workload; pin corrected version and digest |
| IHDP and ACIC | semi-synthetic known-effect error under published simulations | universal real-world ranking | oracle workload with DGP criticism reported |
| Jobs / policy-risk cases | policy regret and objective-selection behavior | marketing transport | policy-selection oracle |
| Controlled synthetic DGPs | known PEHE/regret, overlap, imbalance, sparsity, heterogeneity and misspecification | real-world usefulness | required diagnostic workload |
| Multiple campaigns/time windows | conclusion and policy stability under shift | automatic target-population validity | conditional transport workload |

The original Criteo release contained an advertiser leak. Only the dataset
owner's corrected 13,979,592-row version may enter, with exact version and
content hash. A capped or sampled Criteo run must be labelled as such.

## Metric taxonomy

| Layer | Required measures | Interpretation boundary |
| --- | --- | --- |
| Experiment health | sample-ratio mismatch, covariate balance, missingness, arm/outcome counts | validates the experiment mechanics, not targeting |
| Average effect | ATE, standard error/CI, covariate-adjusted ATE | population intervention evidence only |
| Oracle effect accuracy | PEHE, ATE error, subgroup error | only when both potential outcomes or a known DGP exist |
| Ranking | Qini, AUUC, uplift-at-k, RATE/TOC; pROCini/balanced metrics only with parity | prioritization, not calibrated sign or realized value |
| Calibration | calibration curve/error, BLP/calibration test, threshold reliability | whether score level supports an action threshold |
| Policy | IPW, SNIPS and DR value; regret; treat-none/all/random/equal-capacity baselines | value of the exact held-out rule under assumptions |
| Safety | harm rate/value and conservative bound | impossible without a separately measured harm outcome |
| Robustness | per-regime worst case, seed/split intervals, overlap ESS, failure count | avoids hiding unstable or unsupported regions |
| Resources | runtime, peak memory, artifact size, install/start failure | deployment evidence only on named hardware/environment |

## Search expansion and saturation log

| Round | Expansion | New decision-relevant family? | Disposition |
| --- | --- | --- | --- |
| 0 | surveys, uplift/HTE learners, forests, metrics, policy value, cost/capacity | yes | formed the core taxonomy |
| 1 | calibration, high-variance metric correction, no-harm, sensitivity, transport and partial identification | yes | added evaluation/safety/shift layers |
| 2 | multi-treatment/continuous dose, dynamic regimes, survival, interference and non-compliance | no for current contract | genuine methods, but each changes treatment, timing, outcome or identification; reserve until data contract changes |
| 3 | conformal ITE, TMLE subgroups, distributional outcomes, fairness constraints and multi-outcome inference | no for the immediate queue | calibration/DR/safety taxonomy already owns the applicable decision; specialized variants need uncertainty, protected-attribute or multi-outcome acceptance criteria absent here |
| 4 | current marketing-specific 2026 benchmarks, graph/deep uplift, long-term and resource-constrained ranking | no | reinforced structural-bias, objective-alignment and cost families; no new immediate operating profile |

Rounds 3 and 4 were consecutive breadth expansions with no new
decision-relevant family. Technique-family saturation therefore passes for the
bounded SignalRoom contract. Saturation is not a claim that the literature is
complete; a changed treatment/outcome/deployment contract reopens it.

## Preliminary operating profiles

| Profile | Included candidates | Entry gate | Primary failure risk |
| --- | --- | --- | --- |
| `meta-learner` | S/T/X with identical base learners | one-shot binary treatment; transparent control | regularization, arm imbalance, nuisance bias |
| `orthogonal-dr` | R/DR with cross-fitting | adequate overlap and stable nuisance models | extreme pseudo-outcomes and false confidence |
| `causal-forest` | EconML causal forest, GRF oracle | enough rows for honest partitions and heterogeneity | unstable fine-grained effects and resource cost |
| `direct-uplift` | maintained uplift tree/forest | randomized binary outcome and metric parity | uncalibrated scores and criterion-specific ranking |
| `value-aware-policy` | threshold/equal-capacity plus DR policy value; policy tree conditional | frozen utility, capacity and holdout | optimizing the evaluator or assumed costs |
| `no-harm-safe` | benefit plus adverse-outcome constraint | separately observed harm and acceptance bound | pretending missing harm data means no harm |
| `observational-sensitive` | propensity diagnostics plus DoWhy/DoubleML analyses | defensible causal graph and measured confounders | unsupported ignorability/positivity |

## Review labels

- **Established:** supported by peer-reviewed work and/or mature maintained
  implementation, but still conditional on its assumptions.
- **Provisional:** recent, under-review, single-source, unreleased, or not yet
  independently reproduced.
- **Contested:** credible primary sources disagree on definition, ranking, or
  empirical behavior.
- **Unknown:** must be answered on SignalRoom/client data under a frozen local
  experiment.

The estimator families are established. Their SignalRoom ordering is unknown.
Metric sufficiency is contested. UpliftBench and OAR conclusions are
provisional. The current Hillstrom average effect is established for that
experiment; a personalized targeting benefit remains unsupported.
