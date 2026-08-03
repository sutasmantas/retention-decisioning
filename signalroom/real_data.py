from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HILLSTROM_COMMIT = "c44ae9aea5923533ffdaf34522e4937afd813c9e"
HILLSTROM_URL = (
    "https://raw.githubusercontent.com/TerraBaseAI/campaign-decisioning-engine/"
    f"{HILLSTROM_COMMIT}/data/hillstrom.csv"
)
HILLSTROM_SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"
HILLSTROM_ROWS = 64_000

CONTROL_ARM = "No E-Mail"
TREATMENT_ARM = "Mens E-Mail"
OUTCOME = "visit"

NUMERIC_FEATURES = ["recency", "history", "mens", "womens", "newbie"]
CATEGORICAL_FEATURES = ["history_segment", "zip_code", "channel"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
POST_TREATMENT_COLUMNS = ["segment", "visit", "conversion", "spend"]
REQUIRED_COLUMNS = FEATURES + POST_TREATMENT_COLUMNS


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_hillstrom(destination: Path, *, timeout: int = 60) -> Path:
    """Download the commit-pinned GitHub file and enforce its published hash."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and sha256_file(destination) == HILLSTROM_SHA256:
        return destination

    temporary = destination.with_suffix(f"{destination.suffix}.part")
    request = urllib.request.Request(HILLSTROM_URL, headers={"User-Agent": "SignalRoom/2"})
    with urllib.request.urlopen(request, timeout=timeout) as response, temporary.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)

    observed_hash = sha256_file(temporary)
    if observed_hash != HILLSTROM_SHA256:
        temporary.unlink(missing_ok=True)
        raise ValueError(
            f"Hillstrom checksum mismatch: expected {HILLSTROM_SHA256}, got {observed_hash}"
        )
    temporary.replace(destination)
    return destination


def load_hillstrom(path: Path, *, verify_pinned_file: bool = True) -> pd.DataFrame:
    if verify_pinned_file:
        observed_hash = sha256_file(path)
        if observed_hash != HILLSTROM_SHA256:
            raise ValueError(
                f"Hillstrom checksum mismatch: expected {HILLSTROM_SHA256}, got {observed_hash}"
            )

    frame = pd.read_csv(path)
    validate_hillstrom(frame, require_full_file=verify_pinned_file)
    return frame


def validate_hillstrom(frame: pd.DataFrame, *, require_full_file: bool = False) -> None:
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Hillstrom data is missing required columns: {missing}")
    if require_full_file and len(frame) != HILLSTROM_ROWS:
        raise ValueError(f"Hillstrom row count must be {HILLSTROM_ROWS}, got {len(frame)}")

    required = frame[REQUIRED_COLUMNS]
    null_counts = required.isna().sum()
    null_counts = null_counts[null_counts > 0]
    if not null_counts.empty:
        raise ValueError(f"Hillstrom data has nulls: {null_counts.to_dict()}")

    expected_arms = {CONTROL_ARM, TREATMENT_ARM, "Womens E-Mail"}
    unexpected_arms = set(frame["segment"].unique()) - expected_arms
    if unexpected_arms:
        raise ValueError(f"Hillstrom data has unexpected treatment arms: {sorted(unexpected_arms)}")
    for column in ["mens", "womens", "newbie", "visit", "conversion"]:
        values = set(frame[column].unique())
        if not values <= {0, 1}:
            raise ValueError(f"{column} must be binary, got {sorted(values)}")


def prepare_binary_contrast(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the frozen Mens-email versus control table with a leakage-safe schema."""
    validate_hillstrom(frame)
    contrast = frame[frame["segment"].isin([CONTROL_ARM, TREATMENT_ARM])].copy()
    contrast.insert(0, "customer_id", [f"hillstrom-{index:05d}" for index in contrast.index])
    contrast["treatment"] = (contrast["segment"] == TREATMENT_ARM).astype("int8")
    contrast["outcome"] = contrast[OUTCOME].astype("int8")
    return contrast.reset_index(drop=True)


def joint_stratified_split(
    frame: pd.DataFrame, *, train_fraction: float = 0.8, seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deterministically split each treatment/outcome stratum into train and holdout."""
    if not 0 < train_fraction < 1:
        raise ValueError(f"train_fraction must be in (0, 1), got {train_fraction}")
    if not {"treatment", "outcome"} <= set(frame.columns):
        raise ValueError("split requires treatment and outcome columns")

    rng = np.random.default_rng(seed)
    strata = frame["treatment"].astype(str) + "_" + frame["outcome"].astype(str)
    train_parts: list[np.ndarray] = []
    test_parts: list[np.ndarray] = []
    for _, indexes in strata.groupby(strata, sort=True).groups.items():
        shuffled = np.asarray(indexes, dtype=np.int64).copy()
        rng.shuffle(shuffled)
        split_at = round(len(shuffled) * train_fraction)
        train_parts.append(shuffled[:split_at])
        test_parts.append(shuffled[split_at:])

    train_indexes = np.sort(np.concatenate(train_parts))
    test_indexes = np.sort(np.concatenate(test_parts))
    train = frame.iloc[train_indexes].reset_index(drop=True)
    test = frame.iloc[test_indexes].reset_index(drop=True)
    return train, test

