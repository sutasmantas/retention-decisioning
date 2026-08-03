from __future__ import annotations

import argparse
import json
import platform
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from scipy.stats import chisquare
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from signalroom.real_data import (
    CATEGORICAL_FEATURES,
    CONTROL_ARM,
    FEATURES,
    HILLSTROM_COMMIT,
    HILLSTROM_SHA256,
    HILLSTROM_URL,
    NUMERIC_FEATURES,
    OUTCOME,
    TREATMENT_ARM,
    download_hillstrom,
    joint_stratified_split,
    load_hillstrom,
    prepare_binary_contrast,
)
from signalroom.real_metrics import (
    average_treatment_effect,
    capacity_assignments,
    percentile_bootstrap,
    policy_value,
    qini_coefficient,
    targeting_decision,
    targeting_gain,
    uplift_at_k,
)

DEFAULT_DATA_PATH = Path("data/runtime/real_data/hillstrom.csv")
DEFAULT_OUTPUT_DIR = Path("artifacts/real_data")
DEFAULT_SEED = 42
DEFAULT_CAPACITY = 0.2


def _make_outcome_pipeline() -> Pipeline:
    preprocessing = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    return Pipeline(
        [
            ("features", preprocessing),
            (
                "classifier",
                LogisticRegression(max_iter=1000, C=0.8, random_state=DEFAULT_SEED),
            ),
        ]
    )


def _fit_t_learner(train: pd.DataFrame) -> tuple[Pipeline, Pipeline]:
    control = train[train["treatment"] == 0]
    treated = train[train["treatment"] == 1]
    control_model = _make_outcome_pipeline().fit(control[FEATURES], control["outcome"])
    treated_model = _make_outcome_pipeline().fit(treated[FEATURES], treated["outcome"])
    return control_model, treated_model


def _predict_uplift(models: tuple[Pipeline, Pipeline], frame: pd.DataFrame) -> np.ndarray:
    control_model, treated_model = models
    control_probability = control_model.predict_proba(frame[FEATURES])[:, 1]
    treated_probability = treated_model.predict_proba(frame[FEATURES])[:, 1]
    return treated_probability - control_probability


def _balance_table(frame: pd.DataFrame) -> list[dict[str, Any]]:
    categorical = [column for column in FEATURES if frame[column].dtype == "object"]
    numeric = [column for column in FEATURES if column not in categorical]
    design_parts: list[pd.DataFrame] = []
    if numeric:
        design_parts.append(frame[numeric].apply(pd.to_numeric, errors="raise"))
    if categorical:
        design_parts.append(
            pd.get_dummies(frame[categorical], prefix=categorical, prefix_sep=":", dtype=float)
        )
    design = pd.concat(design_parts, axis=1)
    treated = frame["treatment"] == 1

    rows: list[dict[str, Any]] = []
    for column in design:
        treated_values = design.loc[treated, column]
        control_values = design.loc[~treated, column]
        pooled_sd = np.sqrt((treated_values.var(ddof=1) + control_values.var(ddof=1)) / 2)
        smd = 0.0 if pooled_sd == 0 else (treated_values.mean() - control_values.mean()) / pooled_sd
        rows.append(
            {
                "feature": column,
                "smd": round(float(smd), 6),
                "abs_smd": round(abs(float(smd)), 6),
                "pass": bool(abs(smd) <= 0.1),
            }
        )
    return sorted(rows, key=lambda row: row["abs_smd"], reverse=True)


def _model_diagnostics(
    models: tuple[Pipeline, Pipeline], holdout: pd.DataFrame
) -> dict[str, dict[str, float | int]]:
    control_model, treated_model = models
    diagnostics: dict[str, dict[str, float | int]] = {}
    for name, arm, model in [
        ("control", 0, control_model),
        ("mens_email", 1, treated_model),
    ]:
        rows = holdout[holdout["treatment"] == arm]
        probabilities = model.predict_proba(rows[FEATURES])[:, 1]
        diagnostics[name] = {
            "rows": len(rows),
            "outcome_rate": round(float(rows["outcome"].mean()), 6),
            "roc_auc": round(float(roc_auc_score(rows["outcome"], probabilities)), 6),
            "brier_score": round(float(brier_score_loss(rows["outcome"], probabilities)), 6),
        }
    return diagnostics


def evaluate_real_experiment(
    raw: pd.DataFrame,
    *,
    seed: int = DEFAULT_SEED,
    capacity: float = DEFAULT_CAPACITY,
    n_boot: int = 500,
) -> dict[str, Any]:
    contrast = prepare_binary_contrast(raw)
    train, holdout = joint_stratified_split(contrast, train_fraction=0.8, seed=seed)
    models = _fit_t_learner(train)
    score = _predict_uplift(models, holdout)
    treatment = holdout["treatment"].to_numpy()
    outcome = holdout["outcome"].to_numpy()

    top_metric = lambda s, t, y: uplift_at_k(s, t, y, k=capacity)  # noqa: E731
    gain_metric = lambda s, t, y: targeting_gain(s, t, y, capacity=capacity)  # noqa: E731
    ate = percentile_bootstrap(
        average_treatment_effect, score, treatment, outcome, n_boot=n_boot, seed=seed
    )
    qini = percentile_bootstrap(
        qini_coefficient, score, treatment, outcome, n_boot=n_boot, seed=seed + 1
    )
    top_uplift = percentile_bootstrap(
        top_metric, score, treatment, outcome, n_boot=n_boot, seed=seed + 2
    )
    policy_gain = percentile_bootstrap(
        gain_metric, score, treatment, outcome, n_boot=n_boot, seed=seed + 3
    )

    assignments = capacity_assignments(score, capacity=capacity)
    realized_capacity = float(assignments.mean())
    learned_value = policy_value(assignments, treatment, outcome)
    treated = treatment.astype(bool)
    random_capacity_value = (
        realized_capacity * float(outcome[treated].mean())
        + (1 - realized_capacity) * float(outcome[~treated].mean())
    )

    counts = contrast["treatment"].value_counts().sort_index()
    chi_square, srm_p_value = chisquare(counts.to_numpy(), np.full(2, len(contrast) / 2))
    balance = _balance_table(contrast)
    promotion = targeting_decision(ate, qini, top_uplift, policy_gain)

    return {
        "dataset": {
            "source_url": HILLSTROM_URL,
            "source_commit": HILLSTROM_COMMIT,
            "sha256": HILLSTROM_SHA256,
            "raw_rows": len(raw),
            "contrast_rows": len(contrast),
            "train_rows": len(train),
            "holdout_rows": len(holdout),
            "treatment_arm": TREATMENT_ARM,
            "control_arm": CONTROL_ARM,
            "outcome": OUTCOME,
        },
        "contract": {
            "features": FEATURES,
            "excluded_post_treatment_columns": ["segment", "visit", "conversion", "spend"],
            "split": "joint treatment/outcome 80/20 holdout",
            "seed": seed,
            "maximum_capacity": capacity,
            "realized_capacity": round(realized_capacity, 6),
        },
        "experiment_health": {
            "arm_counts": {"control": int(counts.loc[0]), "mens_email": int(counts.loc[1])},
            "srm_chi_square": round(float(chi_square), 6),
            "srm_p_value": round(float(srm_p_value), 6),
            "srm_pass": bool(srm_p_value >= 0.001),
            "maximum_abs_smd": balance[0]["abs_smd"],
            "covariate_balance_pass": all(row["pass"] for row in balance),
            "largest_balance_differences": balance[:5],
        },
        "model": {
            "type": "logistic-regression T-learner",
            "diagnostics": _model_diagnostics(models, holdout),
            "uplift_distribution": {
                "minimum": round(float(score.min()), 6),
                "median": round(float(np.median(score)), 6),
                "maximum": round(float(score.max()), 6),
                "positive_share": round(float((score > 0).mean()), 6),
            },
        },
        "heldout_metrics": {
            "average_treatment_effect": ate.as_dict(),
            "qini_coefficient": qini.as_dict(),
            "top_capacity_uplift": top_uplift.as_dict(),
            "policy_gain_vs_random_capacity": policy_gain.as_dict(),
            "learned_policy_value": round(float(learned_value), 6),
            "random_capacity_policy_value": round(float(random_capacity_value), 6),
        },
        "promotion": promotion,
        "runtime": {
            "run_date": date.today().isoformat(),
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
        },
    }


def _format_interval(interval: dict[str, Any]) -> str:
    return f"{interval['point']:.4f} [{interval['lower']:.4f}, {interval['upper']:.4f}]"


def render_markdown(report: dict[str, Any]) -> str:
    data = report["dataset"]
    health = report["experiment_health"]
    metrics = report["heldout_metrics"]
    promotion = report["promotion"]
    gates = promotion["targeting_gates"]
    diagnostics = report["model"]["diagnostics"]
    rows_summary = (
        f"{data['contrast_rows']:,} total; {data['train_rows']:,} train; "
        f"{data['holdout_rows']:,} holdout"
    )
    policy_gain_text = _format_interval(metrics["policy_gain_vs_random_capacity"])
    control = diagnostics["control"]
    mens_email = diagnostics["mens_email"]
    control_row = (
        f"| Control | {control['roc_auc']:.4f} | {control['brier_score']:.4f} | "
        f"{control['outcome_rate']:.4f} |"
    )
    mens_email_row = (
        f"| Mens email | {mens_email['roc_auc']:.4f} | {mens_email['brier_score']:.4f} | "
        f"{mens_email['outcome_rate']:.4f} |"
    )
    return f"""# SignalRoom real-data feasibility result

Decision: **{promotion['decision']}**

This is a capacity-constrained re-engagement benchmark on a real randomized
retail email experiment. It is not evidence of SaaS churn reduction or client
revenue.

## Frozen contract

- Data: Hillstrom GitHub mirror at `{data['source_commit']}` (`{data['sha256']}`)
- Contrast: {data['treatment_arm']} versus {data['control_arm']}
- Outcome: two-week `{data['outcome']}`
- Rows: {rows_summary}
- Policy: positive predicted uplift, up to {report['contract']['maximum_capacity']:.0%} capacity
- Split: {report['contract']['split']}, seed {report['contract']['seed']}

## Experiment health

- Arm counts: {health['arm_counts']}
- Sample-ratio check: p={health['srm_p_value']:.4f} ({'PASS' if health['srm_pass'] else 'FAIL'})
- Maximum absolute covariate SMD: {health['maximum_abs_smd']:.4f}
  ({'PASS' if health['covariate_balance_pass'] else 'FAIL'} at 0.10)

## Held-out result

All brackets are percentile-bootstrap 95% intervals.

| Metric | Result |
| --- | ---: |
| Average treatment effect | {_format_interval(metrics['average_treatment_effect'])} |
| Normalized Qini | {_format_interval(metrics['qini_coefficient'])} |
| Top-capacity realized uplift | {_format_interval(metrics['top_capacity_uplift'])} |
| IPW policy gain vs random at equal capacity | {policy_gain_text} |
| Learned policy value | {metrics['learned_policy_value']:.4f} |
| Random capacity policy value | {metrics['random_capacity_policy_value']:.4f} |

Underlying outcome-model diagnostics:

| Arm | ROC AUC | Brier score | Outcome rate |
| --- | ---: | ---: | ---: |
{control_row}
{mens_email_row}

## Pre-registered gate

- Qini lower bound > 0: **{gates['qini_lower_above_zero']}**
- Top-capacity uplift > overall ATE: **{gates['top_capacity_uplift_above_ate']}**
- Policy-gain lower bound > 0: **{gates['policy_gain_lower_above_zero']}**

Targeting supported: **{promotion['targeting_supported']}**. Average effect
supported: **{promotion['average_effect_supported']}**.

If targeting is rejected, the correct operational result is to retain the
experiment-level effect and not claim that the available features improve who
should receive the intervention.

## Limitations

- Public historical benchmark; the holdout is a reproducibility check, not an
  untouched scientific discovery.
- No timestamps, so temporal generalization and drift are untested.
- Visit is a short-horizon re-engagement outcome, not retention or revenue.
- Unsubscribe, complaint, long-term churn, and other harm outcomes are absent.
- The benchmark uses one email creative and a fixed 20% maximum capacity.

Reproduce with:

```bash
pip install -c requirements-benchmark.txt -e ".[dev]"
python -m signalroom.real_benchmark --bootstrap {metrics['qini_coefficient']['n_boot']}
```
"""


def write_report(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "benchmark.json"
    markdown_path = output_dir / "benchmark.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run SignalRoom's pinned Hillstrom real-data feasibility benchmark."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bootstrap", type=int, default=500)
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    if not args.data.exists():
        if args.no_download:
            parser.error(f"pinned dataset not found at {args.data}")
        download_hillstrom(args.data)
    raw = load_hillstrom(args.data)
    report = evaluate_real_experiment(raw, n_boot=args.bootstrap)
    json_path, markdown_path = write_report(report, args.output)
    print(f"Decision: {report['promotion']['decision']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {markdown_path}")


if __name__ == "__main__":
    main()
