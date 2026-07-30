import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from signalroom.config import Settings
from signalroom.data import FEATURES
from signalroom.modeling import reason_codes, score_frame
from signalroom.policy import apply_policy, policy_curve
from signalroom.schemas import PolicyRequest, ScoreRequest
from signalroom.training import train_and_persist


class RetentionService:
    def __init__(self, settings: Settings):
        self.settings = settings
        train_and_persist(settings)
        self.bundle = joblib.load(settings.model_path)
        self.metrics = json.loads(settings.metrics_path.read_text(encoding="utf-8"))
        self.accounts = pd.read_csv(settings.accounts_path)

    def _policy(self) -> dict[str, Any]:
        return json.loads(self.settings.policy_path.read_text(encoding="utf-8"))

    @staticmethod
    def _risk_tier(risk: float) -> str:
        if risk >= 0.85:
            return "Critical"
        if risk >= 0.75:
            return "High"
        if risk >= 0.55:
            return "Elevated"
        return "Monitor"

    @staticmethod
    def _action_description(action: str) -> str:
        descriptions = {
            "Executive service recovery": (
                "Resolve the open service issues, align an executive owner "
                "and agree a recovery date."
            ),
            "Adoption enablement plan": (
                "Run a targeted workflow session and set a 30-day adoption checkpoint."
            ),
            "Customer-success recovery plan": (
                "Review seat contraction with the account owner and agree "
                "measurable recovery actions."
            ),
            "Renewal alignment call": (
                "Confirm renewal criteria, decision owners and remaining "
                "blockers before the deadline."
            ),
            "Targeted success review": (
                "Review current value realization and address the strongest risk signal."
            ),
        }
        return descriptions[action]

    def _account_payload(self, row: pd.Series, detail: bool = False) -> dict[str, Any]:
        risk = float(row["risk"])
        payload: dict[str, Any] = {
            "account_id": row["account_id"],
            "account_name": row["account_name"],
            "segment": row["segment"],
            "mrr": round(float(row["mrr"]), 0),
            "risk": round(risk, 4),
            "risk_tier": self._risk_tier(risk),
            "uplift": round(float(row["uplift"]), 4),
            "expected_mrr_protected": round(float(row["expected_mrr_protected"]), 0),
            "expected_net_value": round(float(row["expected_net_value"]), 0),
            "days_to_renewal": int(row["days_to_renewal"]),
            "action": row["action"],
            "top_signal": json.loads(row["drivers"])[0]["label"],
        }
        if detail:
            payload.update(
                {
                    "drivers": json.loads(row["drivers"]),
                    "action_description": self._action_description(row["action"]),
                    "features": {
                        feature: (
                            row[feature].item() if hasattr(row[feature], "item") else row[feature]
                        )
                        for feature in FEATURES
                    },
                    "model_version": "churn-logit-1.0",
                }
            )
        return payload

    def summary(self) -> dict[str, Any]:
        policy = self._policy()
        selected, outcome = apply_policy(self.accounts, policy["threshold"], policy["capacity"])
        return {
            "policy": policy,
            "outcome": outcome,
            "model": {
                "status": self.health_status(),
                "version": "churn-logit-1.0",
                "holdout_accounts": self.metrics["holdout_accounts"],
                "roc_auc": self.metrics["roc_auc"],
                "brier_score": self.metrics["brier_score"],
            },
            "total_accounts": len(self.accounts),
            "priority_accounts": [
                self._account_payload(row) for _, row in selected.head(5).iterrows()
            ],
        }

    def list_accounts(self, limit: int = 100) -> list[dict[str, Any]]:
        return [
            self._account_payload(row)
            for _, row in self.accounts.sort_values(["risk", "expected_net_value"], ascending=False)
            .head(limit)
            .iterrows()
        ]

    def get_account(self, account_id: str) -> dict[str, Any] | None:
        rows = self.accounts[self.accounts["account_id"] == account_id]
        if rows.empty:
            return None
        return self._account_payload(rows.iloc[0], detail=True)

    def score(self, request: ScoreRequest) -> dict[str, Any]:
        values = request.model_dump()
        name = values.pop("account_name")
        frame = pd.DataFrame([values], columns=FEATURES)
        row = score_frame(self.bundle, frame).iloc[0]
        risk = float(row["risk"])
        return {
            "account_name": name,
            "risk": round(risk, 4),
            "risk_tier": self._risk_tier(risk),
            "uplift": round(float(row["uplift"]), 4),
            "expected_mrr_protected": round(float(row["expected_mrr_protected"]), 0),
            "action": row["action"],
            "action_description": self._action_description(row["action"]),
            "drivers": reason_codes(row),
            "model_version": "churn-logit-1.0",
        }

    def save_policy(self, request: PolicyRequest) -> dict[str, Any]:
        policy = {"threshold": round(request.threshold, 2), "capacity": request.capacity}
        self.settings.policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")
        _, outcome = apply_policy(self.accounts, policy["threshold"], policy["capacity"])
        return {"policy": policy, "outcome": outcome}

    def curve(self, capacity: int) -> list[dict[str, Any]]:
        return policy_curve(self.accounts, capacity)

    def monitoring(self) -> dict[str, Any]:
        return {
            **self.metrics,
            "status": self.health_status(),
            "model_version": "churn-logit-1.0",
            "data_note": "Metrics use a deterministic synthetic holdout set.",
        }

    def health_status(self) -> str:
        max_psi = max(item["psi"] for item in self.metrics["feature_stability"])
        healthy = (
            self.metrics["roc_auc"] >= 0.75
            and self.metrics["brier_score"] <= 0.20
            and max_psi < 0.20
        )
        return "Healthy" if healthy else "Review"


def runtime_files(settings: Settings) -> list[Path]:
    return [
        settings.model_path,
        settings.metrics_path,
        settings.accounts_path,
        settings.policy_path,
    ]
