from __future__ import annotations

import numpy as np
import pytest

from signalroom.real_metrics import (
    MetricInterval,
    average_treatment_effect,
    capacity_assignments,
    percentile_bootstrap,
    policy_value,
    qini_coefficient,
    targeting_decision,
    targeting_gain,
    uplift_at_k,
)


def deterministic_uplift_fixture(rows: int = 4000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(3)
    score = rng.uniform(-0.05, 0.25, rows)
    treatment = rng.binomial(1, 0.5, rows)
    baseline = np.full(rows, 0.12)
    outcome = rng.binomial(1, np.clip(baseline + treatment * np.maximum(score, 0), 0, 0.95))
    return score, treatment, outcome


def test_metrics_reward_informative_uplift_ranking() -> None:
    score, treatment, outcome = deterministic_uplift_fixture()
    ate = average_treatment_effect(score, treatment, outcome)
    assert ate > 0
    assert qini_coefficient(score, treatment, outcome) > 0
    assert uplift_at_k(score, treatment, outcome, k=0.2) > ate
    assert targeting_gain(score, treatment, outcome, capacity=0.2) > 0


def test_policy_value_and_capacity_boundaries() -> None:
    score, treatment, outcome = deterministic_uplift_fixture(1000)
    assignments = capacity_assignments(score, capacity=0.2)
    assert 0 < assignments.mean() <= 0.2
    assert np.isfinite(policy_value(assignments, treatment, outcome))
    with pytest.raises(ValueError, match="capacity"):
        capacity_assignments(score, capacity=0)
    with pytest.raises(ValueError, match="both treatment arms"):
        average_treatment_effect(score, np.zeros(len(score)), outcome)


def test_percentile_bootstrap_is_seeded_and_validates_count() -> None:
    score, treatment, outcome = deterministic_uplift_fixture(800)
    first = percentile_bootstrap(
        qini_coefficient, score, treatment, outcome, n_boot=50, seed=12
    )
    second = percentile_bootstrap(
        qini_coefficient, score, treatment, outcome, n_boot=50, seed=12
    )
    assert first == second
    assert first.lower <= first.upper
    with pytest.raises(ValueError, match="at least 50"):
        percentile_bootstrap(qini_coefficient, score, treatment, outcome, n_boot=49)


def test_promotion_requires_average_effect_and_all_targeting_gates() -> None:
    positive = MetricInterval(point=0.08, lower=0.03, upper=0.12, n_boot=100)
    top = MetricInterval(point=0.13, lower=0.04, upper=0.2, n_boot=100)
    gain = MetricInterval(point=0.02, lower=0.001, upper=0.05, n_boot=100)
    promoted = targeting_decision(positive, positive, top, gain)
    assert promoted["decision"] == "PROMOTE_CAPACITY_TARGETING"

    weak_gain = MetricInterval(point=0.01, lower=-0.01, upper=0.03, n_boot=100)
    average_only = targeting_decision(positive, positive, top, weak_gain)
    assert average_only["decision"] == "PROMOTE_AVERAGE_EFFECT_ONLY"
    assert average_only["targeting_supported"] is False

