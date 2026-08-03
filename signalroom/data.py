import numpy as np
import pandas as pd

FEATURES = [
    "segment",
    "mrr",
    "seat_change_pct",
    "weekly_active_ratio",
    "priority_tickets",
    "days_to_renewal",
    "feature_adoption",
    "tenure_months",
    "nps",
    "resolution_hours",
]
NUMERIC_FEATURES = FEATURES[1:]
CATEGORICAL_FEATURES = ["segment"]


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def generate_accounts(count: int = 2400, seed: int = 42) -> pd.DataFrame:
    """Create deterministic SaaS account data with randomized treatment assignment."""
    rng = np.random.default_rng(seed)
    segment = rng.choice(["Enterprise", "Business", "Growth"], count, p=[0.18, 0.48, 0.34])
    segment_scale = (
        pd.Series(segment)
        .map({"Enterprise": 42_000, "Business": 14_000, "Growth": 5_000})
        .to_numpy()
    )
    mrr = np.clip(rng.lognormal(np.log(segment_scale), 0.42), 1_000, 150_000)
    seat_change = np.clip(rng.normal(-4, 20, count), -75, 55)
    active_ratio = np.clip(rng.beta(4.2, 2.3, count), 0.04, 0.99)
    tickets = np.clip(rng.poisson(1.2, count), 0, 9)
    renewal = rng.integers(5, 181, count)
    adoption = np.clip(0.55 * active_ratio + 0.45 * rng.beta(3, 2.5, count), 0.03, 0.99)
    tenure = rng.integers(3, 85, count)
    nps = np.clip(rng.normal(28 + 45 * (adoption - 0.5), 27, count), -100, 100)
    resolution = np.clip(rng.lognormal(2.5 + 0.14 * tickets, 0.65, count), 1, 180)

    seat_decline = np.clip(-seat_change / 50, 0, 1.5)
    renewal_pressure = np.clip((60 - renewal) / 60, 0, 1)
    slow_support = np.clip((resolution - 18) / 48, 0, 2)
    logit = (
        -3.65
        + 2.8 * (1 - active_ratio)
        + 2.35 * (1 - adoption)
        + 1.9 * seat_decline
        + 0.31 * tickets
        + 1.45 * renewal_pressure
        + 0.75 * slow_support
        - 0.017 * nps
    )
    churn_probability = np.clip(_sigmoid(logit), 0.02, 0.96)
    churned = rng.binomial(1, churn_probability)

    treatment = rng.binomial(1, 0.5, count)
    true_uplift = np.clip(
        0.025
        + 0.105 * (1 - adoption)
        + 0.055 * renewal_pressure
        + 0.025 * np.minimum(tickets, 4)
        + 0.035 * (segment == "Enterprise"),
        0.02,
        0.27,
    )
    retained_probability = np.clip(1 - churn_probability + treatment * true_uplift, 0.02, 0.98)
    retained = rng.binomial(1, retained_probability)

    return pd.DataFrame(
        {
            "segment": segment,
            "mrr": mrr.round(0),
            "seat_change_pct": seat_change.round(1),
            "weekly_active_ratio": active_ratio.round(3),
            "priority_tickets": tickets,
            "days_to_renewal": renewal,
            "feature_adoption": adoption.round(3),
            "tenure_months": tenure,
            "nps": nps.round(0),
            "resolution_hours": resolution.round(1),
            "churn_probability_true": churn_probability,
            "churned": churned,
            "treatment": treatment,
            "retained": retained,
            "true_uplift": true_uplift,
        }
    )
