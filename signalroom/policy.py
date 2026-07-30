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


def policy_curve(accounts: pd.DataFrame, capacity: int) -> list[dict[str, Any]]:
    return [apply_policy(accounts, threshold / 100, capacity)[1] for threshold in range(45, 81)]
