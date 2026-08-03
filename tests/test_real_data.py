from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from signalroom.real_data import (
    FEATURES,
    POST_TREATMENT_COLUMNS,
    joint_stratified_split,
    load_hillstrom,
    prepare_binary_contrast,
    sha256_file,
    validate_hillstrom,
)


def make_hillstrom_like(rows: int = 800, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    treatment = np.arange(rows) % 2
    history = rng.gamma(2.0, 120.0, rows)
    recency = rng.integers(1, 13, rows)
    response_probability = 1 / (1 + np.exp(-(-2.0 + history / 500 - recency / 15)))
    heterogeneous_lift = treatment * (0.05 + 0.14 * (history > 250))
    visit = rng.binomial(1, np.clip(response_probability + heterogeneous_lift, 0.01, 0.9))
    conversion = rng.binomial(1, np.clip((response_probability + heterogeneous_lift) / 12, 0, 1))
    return pd.DataFrame(
        {
            "recency": recency,
            "history_segment": np.where(history > 250, "4) $350 - $500", "2) $100 - $200"),
            "history": history,
            "mens": (np.arange(rows) % 3 == 0).astype(int),
            "womens": (np.arange(rows) % 4 == 0).astype(int),
            "zip_code": np.where(np.arange(rows) % 2, "Urban", "Rural"),
            "newbie": (recency < 5).astype(int),
            "channel": np.where(np.arange(rows) % 3, "Web", "Phone"),
            "segment": np.where(treatment == 1, "Mens E-Mail", "No E-Mail"),
            "visit": visit,
            "conversion": conversion,
            "spend": conversion * rng.uniform(20, 250, rows),
        }
    )


def test_prepare_contrast_has_explicit_leakage_boundary() -> None:
    prepared = prepare_binary_contrast(make_hillstrom_like(120))
    assert len(prepared) == 120
    assert set(prepared["treatment"]) == {0, 1}
    assert set(prepared["outcome"]) <= {0, 1}
    assert not set(FEATURES) & set(POST_TREATMENT_COLUMNS)
    assert prepared["customer_id"].is_unique


def test_joint_split_is_reproducible_and_preserves_all_strata() -> None:
    prepared = prepare_binary_contrast(make_hillstrom_like(400))
    train_a, test_a = joint_stratified_split(prepared, seed=42)
    train_b, test_b = joint_stratified_split(prepared, seed=42)
    assert train_a["customer_id"].tolist() == train_b["customer_id"].tolist()
    assert test_a["customer_id"].tolist() == test_b["customer_id"].tolist()
    assert set(train_a["customer_id"]).isdisjoint(test_a["customer_id"])
    assert len(train_a) + len(test_a) == len(prepared)
    assert train_a.groupby(["treatment", "outcome"]).size().ge(1).all()
    assert test_a.groupby(["treatment", "outcome"]).size().ge(1).all()


def test_validation_rejects_missing_columns_and_bad_checksum(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_hillstrom(pd.DataFrame({"visit": [1]}))

    fake = tmp_path / "hillstrom.csv"
    fake.write_text("not,the,pinned,file\n", encoding="utf-8")
    assert len(sha256_file(fake)) == 64
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_hillstrom(fake)

