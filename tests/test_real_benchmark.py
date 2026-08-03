from __future__ import annotations

import json
from pathlib import Path

from test_real_data import make_hillstrom_like

from signalroom.real_benchmark import evaluate_real_experiment, render_markdown, write_report


def test_real_benchmark_runs_end_to_end_without_touching_product_runtime(tmp_path: Path) -> None:
    report = evaluate_real_experiment(make_hillstrom_like(), n_boot=50)
    assert report["dataset"]["contrast_rows"] == 800
    assert report["contract"]["excluded_post_treatment_columns"] == [
        "segment",
        "visit",
        "conversion",
        "spend",
    ]
    assert report["experiment_health"]["srm_pass"] is True
    assert report["promotion"]["decision"] in {
        "PROMOTE_CAPACITY_TARGETING",
        "PROMOTE_AVERAGE_EFFECT_ONLY",
        "DO_NOT_PROMOTE_INTERVENTION",
    }
    assert "real randomized" in render_markdown(report)

    json_path, markdown_path = write_report(report, tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["dataset"]["raw_rows"] == 800
    assert "Pre-registered gate" in markdown_path.read_text(encoding="utf-8")
