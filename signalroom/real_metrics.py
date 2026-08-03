from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

Array = np.ndarray[Any, np.dtype[Any]]
Metric = Callable[[Array, Array, Array], float]


@dataclass(frozen=True, slots=True)
class MetricInterval:
    point: float
    lower: float
    upper: float
    n_boot: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "point": self.point,
            "lower": self.lower,
            "upper": self.upper,
            "n_boot": self.n_boot,
        }


def _aligned(*values: Array | list[Any]) -> tuple[Array, ...]:
    arrays = tuple(np.asarray(value).ravel() for value in values)
    if not arrays:
        raise ValueError("at least one array is required")
    expected = len(arrays[0])
    if expected == 0:
        raise ValueError("metric requires at least one observation")
    if any(len(array) != expected for array in arrays[1:]):
        raise ValueError("metric arrays must have the same length")
    return arrays


def _stable_descending(score: Array) -> Array:
    return np.argsort(-score, kind="stable")


def average_treatment_effect(score: Array, treatment: Array, outcome: Array) -> float:
    del score
    treatment, outcome = _aligned(treatment, outcome)
    treated = treatment.astype(bool)
    if not treated.any() or not (~treated).any():
        raise ValueError("average treatment effect requires both treatment arms")
    return float(outcome[treated].mean() - outcome[~treated].mean())


def uplift_at_k(score: Array, treatment: Array, outcome: Array, *, k: float = 0.2) -> float:
    if not 0 < k <= 1:
        raise ValueError(f"k must be in (0, 1], got {k}")
    score, treatment, outcome = _aligned(score, treatment, outcome)
    top = _stable_descending(score)[: max(1, round(len(score) * k))]
    treated = treatment[top].astype(bool)
    if not treated.any() or not (~treated).any():
        return float("nan")
    return float(outcome[top][treated].mean() - outcome[top][~treated].mean())


def _cumulative_uplift(score: Array, treatment: Array, outcome: Array) -> tuple[Array, Array]:
    order = _stable_descending(score)
    treatment = treatment[order].astype(float)
    outcome = outcome[order].astype(float)
    cumulative_treatment = np.cumsum(treatment)
    cumulative_control = np.cumsum(1 - treatment)
    treated_outcomes = np.cumsum(treatment * outcome)
    control_outcomes = np.cumsum((1 - treatment) * outcome)
    safe_control = np.where(cumulative_control > 0, cumulative_control, 1)
    incremental = treated_outcomes - control_outcomes * cumulative_treatment / safe_control
    incremental = np.where(cumulative_control > 0, incremental, treated_outcomes)
    share = np.concatenate(([0.0], np.arange(1, len(score) + 1) / len(score)))
    uplift = np.concatenate(([0.0], incremental / len(score)))
    return share, uplift


def qini_coefficient(score: Array, treatment: Array, outcome: Array) -> float:
    """Normalized Qini using the stable-ranking convention from uplift-bench/sklift."""
    score, treatment, outcome = _aligned(score, treatment, outcome)
    share, uplift = _cumulative_uplift(score, treatment, outcome)
    sample_ate = float(uplift[-1])
    random_area = 0.5 * sample_ate
    raw_area = float(np.trapezoid(uplift, share)) - random_area

    perfect_score = outcome * (2 * treatment - 1)
    _, perfect_uplift = _cumulative_uplift(perfect_score, treatment, outcome)
    perfect_area = float(np.trapezoid(perfect_uplift, share)) - random_area
    return raw_area / perfect_area if perfect_area > 0 else raw_area


def capacity_assignments(score: Array, *, capacity: float = 0.2) -> Array:
    if not 0 < capacity <= 1:
        raise ValueError(f"capacity must be in (0, 1], got {capacity}")
    score = np.asarray(score).ravel()
    assignments = np.zeros(len(score), dtype=bool)
    positive = _stable_descending(score)
    positive = positive[score[positive] > 0]
    assignments[positive[: round(len(score) * capacity)]] = True
    return assignments


def policy_value(assignments: Array, treatment: Array, outcome: Array) -> float:
    assignments, treatment, outcome = _aligned(assignments, treatment, outcome)
    assignments = assignments.astype(bool)
    treatment = treatment.astype(bool)
    propensity = float(treatment.mean())
    if not 0 < propensity < 1:
        raise ValueError("policy value requires both treatment arms")
    matches_treated = assignments & treatment
    matches_control = (~assignments) & (~treatment)
    weighted = outcome[matches_treated].sum() / propensity
    weighted += outcome[matches_control].sum() / (1 - propensity)
    return float(weighted / len(outcome))


def targeting_gain(
    score: Array, treatment: Array, outcome: Array, *, capacity: float = 0.2
) -> float:
    score, treatment, outcome = _aligned(score, treatment, outcome)
    assignments = capacity_assignments(score, capacity=capacity)
    treated_rate = float(assignments.mean())
    learned_value = policy_value(assignments, treatment, outcome)
    treated = treatment.astype(bool)
    random_value = (
        treated_rate * float(outcome[treated].mean())
        + (1 - treated_rate) * float(outcome[~treated].mean())
    )
    return learned_value - random_value


def percentile_bootstrap(
    metric: Metric,
    score: Array,
    treatment: Array,
    outcome: Array,
    *,
    n_boot: int = 500,
    seed: int = 42,
) -> MetricInterval:
    if n_boot < 50:
        raise ValueError("n_boot must be at least 50")
    score, treatment, outcome = _aligned(score, treatment, outcome)
    point = float(metric(score, treatment, outcome))
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    attempts = 0
    while len(estimates) < n_boot and attempts < n_boot * 2:
        indexes = rng.integers(0, len(score), size=len(score))
        attempts += 1
        try:
            estimate = float(metric(score[indexes], treatment[indexes], outcome[indexes]))
        except ValueError:
            continue
        if np.isfinite(estimate):
            estimates.append(estimate)
    if len(estimates) < n_boot:
        raise ValueError("bootstrap could not produce enough finite two-arm samples")
    lower, upper = np.quantile(np.asarray(estimates), [0.025, 0.975])
    return MetricInterval(point=point, lower=float(lower), upper=float(upper), n_boot=n_boot)


def targeting_decision(
    ate: MetricInterval,
    qini: MetricInterval,
    top_capacity_uplift: MetricInterval,
    policy_gain: MetricInterval,
) -> dict[str, Any]:
    average_effect_supported = ate.lower > 0
    gates = {
        "qini_lower_above_zero": qini.lower > 0,
        "top_capacity_uplift_above_ate": top_capacity_uplift.point > ate.point,
        "policy_gain_lower_above_zero": policy_gain.lower > 0,
    }
    targeting_supported = average_effect_supported and all(gates.values())
    if targeting_supported:
        decision = "PROMOTE_CAPACITY_TARGETING"
    elif average_effect_supported:
        decision = "PROMOTE_AVERAGE_EFFECT_ONLY"
    else:
        decision = "DO_NOT_PROMOTE_INTERVENTION"
    return {
        "decision": decision,
        "average_effect_supported": average_effect_supported,
        "targeting_supported": targeting_supported,
        "targeting_gates": gates,
    }
