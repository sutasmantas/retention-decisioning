# SignalRoom real-data admission and reuse decision

Date: 2026-08-03

Status: **ADMITTED for a bounded, non-UI experiment**.

This document freezes the inputs and decision rule before the first model run.
The existing synthetic SaaS application remains intact. The real-data slice is
a separate reproducible command and report; it must not silently replace the
application's domain, model artifacts, API, or interface.

## Claim boundary

The admitted dataset supports one question:

> For prior retail customers in the Hillstrom randomized email experiment,
> can a model rank the incremental two-week website-visit effect of sending
> the Mens merchandise email, when only 20% of customers can be contacted?

It does **not** validate SaaS churn prediction, retention revenue, long-term
customer retention, production drift, or individualized causal effects. The
buyer-readable term is `capacity-constrained re-engagement decisioning`.

## Pinned dataset

- GitHub repository: `TerraBaseAI/campaign-decisioning-engine`
- Commit: `c44ae9aea5923533ffdaf34522e4937afd813c9e`
- File: `data/hillstrom.csv`
- Git blob: `083522a43100d6c8a15ae960877a5520a1860bd7`
- SHA-256: `0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece`
- Observed shape: 64,000 rows x 12 columns
- Arms: 21,306 No E-Mail; 21,307 Mens E-Mail; 21,387 Womens E-Mail
- Missing values: none in the pinned file
- Source description: Kevin Hillstrom's 2008 MineThatData email analytics
  challenge, described by the publisher and downstream research as a
  randomized customer email test.

The repository mirror is selected because it is small, checksum-pinned, and
reproducible from GitHub. Criteo was rejected because its approximately
14-million-row anonymous benchmark creates unnecessary download and CI cost.
UCI Online Retail was rejected for this slice because it has transactions but
no randomized intervention. RetailHero was rejected because its raw purchase
history is much larger and adds feature-pipeline work without improving this
minimum causal evidence gate.

No license filtering, ranking, or research was performed. License suitability
is deliberately outside this private portfolio workflow.

## Frozen target, split, leakage, and action contract

- Population: only `Mens E-Mail` and `No E-Mail` rows (42,613 customers).
- Treatment: `1` for `Mens E-Mail`, `0` for `No E-Mail`.
- Outcome: `visit`, a binary indicator measured during the two weeks after
  assignment. Conversion is too sparse for this minimum slice; spend is
  heavy-tailed and requires a separate value/robustness experiment.
- Features: `recency`, `history`, `history_segment`, `mens`, `womens`,
  `zip_code`, `newbie`, and `channel` only.
- Leakage exclusion: `segment`, `visit`, `conversion`, and `spend` are never
  model inputs. A stable row-derived customer ID is metadata only.
- Split: deterministic 80/20 holdout, stratified jointly on treatment and
  outcome with seed 42. The public dataset has no event timestamp, so temporal
  generalization is explicitly untested.
- Estimator: campaign-specific logistic-regression T-learner with independent
  treated and control outcome pipelines. Uplift is `P(visit|email,X) -
  P(visit|no email,X)`.
- Action: email the top 20% by estimated positive uplift; suppress the rest.
- Evaluation: held-out randomized outcomes only.

Because this is a public, repeatedly analyzed benchmark, the holdout is a
reproducibility check rather than a claim of untouched scientific discovery.

## Pre-run promotion rule

The report must always publish the experiment-level average treatment effect,
its percentile-bootstrap 95% interval, treatment balance, and leakage audit.

Individualized targeting is promoted only if all of these held-out gates pass:

1. normalized Qini coefficient bootstrap lower bound is greater than zero;
2. realized uplift in the top 20% exceeds the held-out overall ATE;
3. the 20%-capacity IPW policy-value gain over a random 20% policy has a
   bootstrap lower bound greater than zero.

If the email has a positive average effect but any targeting gate fails, the
valid result is: `the experiment supports broad treatment, but the available
features do not support learned targeting`. That negative result is retained;
model or threshold shopping after the run is prohibited.

## Repository-level GitHub comparison

| Repository | Useful evidence | Decision |
| --- | --- | --- |
| `TerraBaseAI/campaign-decisioning-engine@c44ae9a` | Pinned Hillstrom file, schema, leakage warning, causal decision framing | Adopt the file and checksum only. Its training/evaluation/policy files are intentionally stubs, so they do not supply implementation logic. |
| `yablochnikovds/uplift-bench@a20ea60` | Modular Hillstrom loader, joint treatment/outcome split, Qini, uplift-at-k, bootstrap, and IPW policy value with tests | Primary component source. Refit only the bounded loader/split/metric patterns; importing its seven-model benchmark, Hydra-style config, MLflow, CatBoost, and EconML surface would be integration-heavy. |
| `maks-sh/scikit-uplift@0038e65` (`v0.5.1`) | Established `TwoModels`, Qini, and uplift-at-k APIs | Cross-check definitions, but do not add the 2022 package to the runtime merely for three small metrics already covered by the selected source and local tests. |
| `aokassamali/Hillstrom-emails-experiment@b239f70` | SRM/covariate checks, honest policy-value baseline, and an explicit negative targeting result | Reuse the strong-baseline decision rule and health-check expectations, not its full analysis suite. |
| `rahuldas98rd-png/uplift-promotions@24384a9` | Qini plus SNIPS policy evaluation across five estimators | Useful policy-evaluation comparison; rejected as a foundation because the notebook/model breadth exceeds this minimum slice. |
| `tkarim45/uplift-targeting-engine@534ce7f` | Hillstrom/Criteo adapters and a FastAPI targeting service | Reject: SignalRoom already has a tested API and distinct interface; adopting it would duplicate product surface and cause rework. |

## Component/source audit

| Component | Reuse decision | Reason |
| --- | --- | --- |
| Download and integrity | Adapt the pinned-URL and checksum boundary from the selected GitHub dataset/loader patterns | Prevents mutable or silently corrupt input. |
| Schema and leakage validation | Refit the narrow boundary validation in `uplift-bench/data/validation.py` | The required invariants are small; adding a new dataframe-validation framework is not justified. |
| Joint stratified holdout | Refit `uplift-bench/data/splits.py` to a two-fold 80/20 contract | Preserves treatment/outcome representation without importing benchmark abstractions. |
| T-learner | Retain SignalRoom's existing two-pipeline pattern after comparing `scikit-uplift.models.TwoModels` and `uplift-bench/models/t_learner.py` | The local implementation is the same bounded formula and already integrates with sklearn preprocessing. A new meta-learner dependency adds no behavior. |
| Qini and uplift-at-k | Refit the vectorized, stable-ranking implementations and their edge-case tests from `uplift-bench/metrics` | Avoids inventing causal ranking metrics and avoids a stale runtime dependency. |
| Capacity policy value | Refit the randomized-trial IPW formulation from `uplift-bench/metrics/policy_value.py` and compare against the random-capacity baseline used by the experiment-analysis repositories | This is the consequential decision metric, so repository logic is reused and locally verified. |
| Bootstrap | Use a small percentile bootstrap adapted from the selected benchmark; exclude BCa | BCa's jackknife cost is unnecessary on the 8,523-row holdout. |
| UI/API | No change | Visual polish and domain replacement are outside the authorized slice. |

## Planned artifacts and stop boundary

- `python -m signalroom.real_benchmark` downloads/verifies the file, trains
  from the frozen split, and writes a machine-readable JSON plus Markdown
  decision report.
- `requirements-benchmark.txt` freezes the four numerical packages required
  for exact artifact reproduction without narrowing the product's normal
  dependency ranges.
- Unit tests cover checksum/schema/leakage, split reproducibility, metric edge
  cases, and the promotion rule.
- A clean-checkout reproduction command must pass.
- Stop after the functional report, expertise note, checkpoint, and commits.
  Do not begin UI polish, API integration, additional models, or a new project.
