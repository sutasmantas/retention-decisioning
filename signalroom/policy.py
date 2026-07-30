from typing import Any

import pandas as pd
from sklearn.metrics import precision_score, recall_score


def apply_policy(
    accounts: pd.DataFrame, threshold: float, capacity: int
) -> tuple[pd.DataFrame, dict[str, Any]]:
    eligible = accounts[
        (accounts["risk"] >= threshold)
        & (accounts["uplift"] > 0)
        & (accounts["expected_net_value"] > 0)
    ].sort_values(["expected_net_value", "risk"], ascending=False)
    selected = eligible.head(capacity).copy()
    predictions = accounts["risk"] >= threshold
    actual = accounts["churned"].astype(int)
    metrics = {
        "threshold": round(threshold, 2),
        "capacity": capacity,
        "eligible_accounts": len(eligible),
        "queued_accounts": len(selected),
        "capacity_used": round(len(selected) / capacity, 3),
        "at_risk_mrr": round(float(accounts.loc[predictions, "mrr"].sum()), 0),
        "expected_mrr_protected": round(float(selected["expected_mrr_protected"].sum()), 0),
        "expected_net_value": round(float(selected["expected_net_value"].sum()), 0),
        "precision": round(float(precision_score(actual, predictions, zero_division=0)), 3),
        "recall": round(float(recall_score(actual, predictions, zero_division=0)), 3),
    }
    return selected, metrics


def apply_risk_only_policy(
    accounts: pd.DataFrame, threshold: float, capacity: int
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build the common baseline queue: threshold and rank by churn risk only."""
    eligible = accounts[accounts["risk"] >= threshold].sort_values("risk", ascending=False)
    selected = eligible.head(capacity).copy()
    return selected, {
        "eligible_accounts": len(eligible),
        "queued_accounts": len(selected),
        "expected_mrr_protected": round(float(selected["expected_mrr_protected"].sum()), 0),
        "expected_net_value": round(float(selected["expected_net_value"].sum()), 0),
        "negative_uplift_accounts": int((selected["uplift"] <= 0).sum()),
        "negative_value_accounts": int((selected["expected_net_value"] <= 0).sum()),
    }


def policy_curve(accounts: pd.DataFrame, capacity: int) -> list[dict[str, Any]]:
    rows = []
    for threshold in range(45, 81):
        value_aware = apply_policy(accounts, threshold / 100, capacity)[1]
        _, risk_only = apply_risk_only_policy(accounts, threshold / 100, capacity)
        rows.append(
            {
                **value_aware,
                "risk_only_expected_net_value": risk_only["expected_net_value"],
                "net_value_gain_vs_risk_only": round(
                    value_aware["expected_net_value"] - risk_only["expected_net_value"],
                    0,
                ),
            }
        )
    return rows
