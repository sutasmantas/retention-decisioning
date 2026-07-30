import pandas as pd

from signalroom.data import generate_accounts
from signalroom.policy import apply_policy, apply_risk_only_policy, policy_curve


def test_synthetic_generation_is_reproducible_and_treatment_is_randomized():
    first = generate_accounts(250, seed=9)
    second = generate_accounts(250, seed=9)

    pd.testing.assert_frame_equal(first, second)
    assert 0.35 < first["treatment"].mean() < 0.65
    assert first["true_uplift"].between(0.02, 0.27).all()
    assert first["churned"].nunique() == 2


def test_policy_respects_capacity_and_uses_positive_net_value():
    accounts = pd.DataFrame(
        {
            "risk": [0.90, 0.82, 0.77, 0.51],
            "uplift": [0.12, 0.08, 0.01, 0.20],
            "expected_net_value": [800, 500, -20, 1000],
            "expected_mrr_protected": [1000, 700, 50, 1400],
            "mrr": [8000, 7000, 5000, 9000],
            "churned": [1, 1, 0, 0],
        }
    )

    selected, outcome = apply_policy(accounts, threshold=0.60, capacity=1)

    assert len(selected) == 1
    assert selected.iloc[0]["expected_net_value"] == 800
    assert outcome["queued_accounts"] == 1
    assert outcome["capacity_used"] == 1
    assert len(policy_curve(accounts, capacity=2)) == 36


def test_value_aware_policy_outperforms_risk_only_when_high_risk_action_has_no_value():
    accounts = pd.DataFrame(
        {
            "risk": [0.95, 0.88, 0.81],
            "uplift": [-0.02, 0.08, 0.12],
            "expected_net_value": [-200, 500, 900],
            "expected_mrr_protected": [0, 700, 1200],
            "mrr": [12000, 9000, 10000],
            "churned": [1, 1, 0],
        }
    )

    selected, value_aware = apply_policy(accounts, threshold=0.80, capacity=2)
    baseline_selected, risk_only = apply_risk_only_policy(
        accounts,
        threshold=0.80,
        capacity=2,
    )

    assert selected["expected_net_value"].tolist() == [900, 500]
    assert baseline_selected["expected_net_value"].tolist() == [-200, 500]
    assert value_aware["expected_net_value"] > risk_only["expected_net_value"]
    assert risk_only["negative_uplift_accounts"] == 1
