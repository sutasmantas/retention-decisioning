from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    mean_squared_error,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from signalroom.data import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES


@dataclass
class ModelBundle:
    churn: Pipeline
    treated: Pipeline
    control: Pipeline


def make_pipeline() -> Pipeline:
    transformer = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("segment", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("features", transformer),
            ("classifier", LogisticRegression(max_iter=1000, C=0.8)),
        ]
    )


def fit_models(train: pd.DataFrame) -> ModelBundle:
    churn = make_pipeline().fit(train[FEATURES], train["churned"])
    treated_rows = train[train["treatment"] == 1]
    control_rows = train[train["treatment"] == 0]
    treated = make_pipeline().fit(treated_rows[FEATURES], treated_rows["retained"])
    control = make_pipeline().fit(control_rows[FEATURES], control_rows["retained"])
    return ModelBundle(churn=churn, treated=treated, control=control)


def score_frame(bundle: ModelBundle, frame: pd.DataFrame) -> pd.DataFrame:
    scored = frame.copy()
    scored["risk"] = bundle.churn.predict_proba(frame[FEATURES])[:, 1]
    treated_probability = bundle.treated.predict_proba(frame[FEATURES])[:, 1]
    control_probability = bundle.control.predict_proba(frame[FEATURES])[:, 1]
    scored["uplift"] = np.clip(treated_probability - control_probability, -0.2, 0.4)
    scored["expected_mrr_protected"] = np.maximum(scored["uplift"], 0) * scored["mrr"]
    scored["action"] = scored.apply(recommend_action, axis=1)
    scored["action_cost"] = scored["segment"].map(
        {"Enterprise": 950.0, "Business": 420.0, "Growth": 180.0}
    )
    scored["expected_net_value"] = scored["expected_mrr_protected"] - scored["action_cost"]
    return scored


def recommend_action(row: pd.Series) -> str:
    if row["priority_tickets"] >= 3 or row["resolution_hours"] >= 36:
        return "Executive service recovery"
    if row["feature_adoption"] < 0.42 or row["weekly_active_ratio"] < 0.45:
        return "Adoption enablement plan"
    if row["seat_change_pct"] <= -18:
        return "Customer-success recovery plan"
    if row["days_to_renewal"] <= 30:
        return "Renewal alignment call"
    return "Targeted success review"


def reason_codes(row: pd.Series) -> list[dict[str, Any]]:
    candidates = [
        (
            "Weekly active usage",
            max(0.0, (0.65 - float(row["weekly_active_ratio"])) * 45),
            f"{float(row['weekly_active_ratio']) * 100:.0f}% active-seat ratio",
        ),
        (
            "Feature adoption",
            max(0.0, (0.60 - float(row["feature_adoption"])) * 42),
            f"{float(row['feature_adoption']) * 100:.0f}% adoption index",
        ),
        (
            "Seat contraction",
            max(0.0, -float(row["seat_change_pct"]) * 0.7),
            f"{float(row['seat_change_pct']):.0f}% seat change",
        ),
        (
            "Priority support load",
            float(row["priority_tickets"]) * 4.5,
            f"{int(row['priority_tickets'])} priority tickets",
        ),
        (
            "Renewal proximity",
            max(0.0, (45 - float(row["days_to_renewal"])) * 0.35),
            f"{int(row['days_to_renewal'])} days to renewal",
        ),
    ]
    ranked = sorted(candidates, key=lambda item: item[1], reverse=True)[:3]
    return [
        {"label": label, "impact_points": round(impact, 1), "evidence": evidence}
        for label, impact, evidence in ranked
    ]


def calibration_rows(actual: pd.Series, predicted: np.ndarray) -> list[dict[str, Any]]:
    bins = np.linspace(0, 1, 6)
    indexes = np.digitize(predicted, bins[1:-1])
    rows = []
    for index in range(5):
        mask = indexes == index
        rows.append(
            {
                "band": f"{index * 20}–{(index + 1) * 20}%",
                "predicted": round(float(predicted[mask].mean()) if mask.any() else 0, 3),
                "observed": round(float(actual.to_numpy()[mask].mean()) if mask.any() else 0, 3),
                "count": int(mask.sum()),
            }
        )
    return rows


def _population_stability(train: pd.Series, test: pd.Series) -> float:
    quantiles = np.unique(np.quantile(train, np.linspace(0, 1, 11)))
    if len(quantiles) < 3:
        return 0.0
    quantiles[0], quantiles[-1] = -np.inf, np.inf
    train_share = pd.cut(train, quantiles).value_counts(normalize=True, sort=False)
    test_share = pd.cut(test, quantiles).value_counts(normalize=True, sort=False)
    train_share = np.maximum(train_share.to_numpy(), 0.0001)
    test_share = np.maximum(test_share.to_numpy(), 0.0001)
    return float(np.sum((test_share - train_share) * np.log(test_share / train_share)))


def evaluate(bundle: ModelBundle, train: pd.DataFrame, test: pd.DataFrame) -> dict[str, Any]:
    predictions = bundle.churn.predict_proba(test[FEATURES])[:, 1]
    treated_probability = bundle.treated.predict_proba(test[FEATURES])[:, 1]
    control_probability = bundle.control.predict_proba(test[FEATURES])[:, 1]
    predicted_uplift = treated_probability - control_probability
    metrics: dict[str, Any] = {
        "holdout_accounts": len(test),
        "prevalence": round(float(test["churned"].mean()), 4),
        "roc_auc": round(float(roc_auc_score(test["churned"], predictions)), 4),
        "pr_auc": round(float(average_precision_score(test["churned"], predictions)), 4),
        "brier_score": round(float(brier_score_loss(test["churned"], predictions)), 4),
        "uplift_rmse": round(
            float(mean_squared_error(test["true_uplift"], predicted_uplift) ** 0.5), 4
        ),
        "calibration": calibration_rows(test["churned"], predictions),
        "segments": [],
        "feature_stability": [],
    }
    for segment, rows in test.groupby("segment"):
        segment_predictions = predictions[rows.index.to_numpy()]
        metrics["segments"].append(
            {
                "segment": segment,
                "accounts": len(rows),
                "pr_auc": round(
                    float(average_precision_score(rows["churned"], segment_predictions)), 3
                ),
                "brier_score": round(
                    float(brier_score_loss(rows["churned"], segment_predictions)), 3
                ),
            }
        )
    for feature in [
        "weekly_active_ratio",
        "feature_adoption",
        "priority_tickets",
        "days_to_renewal",
    ]:
        metrics["feature_stability"].append(
            {
                "feature": feature,
                "psi": round(_population_stability(train[feature], test[feature]), 4),
            }
        )
    return metrics
