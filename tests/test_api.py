def score_payload(**overrides):
    payload = {
        "account_name": "Test Account",
        "segment": "Business",
        "mrr": 24000,
        "seat_change_pct": -30,
        "weekly_active_ratio": 0.30,
        "priority_tickets": 3,
        "days_to_renewal": 20,
        "feature_adoption": 0.25,
        "tenure_months": 18,
        "nps": -15,
        "resolution_hours": 52,
    }
    payload.update(overrides)
    return payload


def test_summary_accounts_and_account_detail(api_client):
    summary = api_client.get("/api/summary")
    accounts = api_client.get("/api/accounts", params={"limit": 8})

    assert summary.status_code == 200
    assert summary.json()["total_accounts"] == 300
    assert len(summary.json()["priority_accounts"]) > 0
    assert len(accounts.json()["accounts"]) == 8

    account_id = accounts.json()["accounts"][0]["account_id"]
    detail = api_client.get(f"/api/accounts/{account_id}")
    assert detail.status_code == 200
    assert len(detail.json()["drivers"]) == 3
    assert detail.json()["model_version"] == "churn-logit-1.0"
    assert api_client.get("/api/accounts/not-real").status_code == 404


def test_live_scoring_changes_with_account_health(api_client):
    high = api_client.post("/api/score", json=score_payload())
    low = api_client.post(
        "/api/score",
        json=score_payload(
            seat_change_pct=18,
            weekly_active_ratio=0.92,
            priority_tickets=0,
            days_to_renewal=150,
            feature_adoption=0.91,
            nps=72,
            resolution_hours=4,
        ),
    )

    assert high.status_code == 200
    assert low.status_code == 200
    assert high.json()["risk"] > low.json()["risk"]
    assert high.json()["drivers"][0]["impact_points"] > 0
    assert api_client.post("/api/score", json=score_payload(mrr=-1)).status_code == 422


def test_policy_is_previewed_and_persisted(api_client):
    curve = api_client.get("/api/policy/curve", params={"capacity": 25})
    saved = api_client.put("/api/policy", json={"threshold": 0.70, "capacity": 25})
    refreshed = api_client.get("/api/summary")

    assert curve.status_code == 200
    assert len(curve.json()["curve"]) == 36
    assert saved.status_code == 200
    assert saved.json()["outcome"]["queued_accounts"] <= 25
    assert refreshed.json()["policy"] == {"threshold": 0.7, "capacity": 25}


def test_monitoring_and_health_are_artifact_backed(api_client):
    health = api_client.get("/api/health")
    monitoring = api_client.get("/api/monitoring")

    assert health.status_code == 200
    assert monitoring.status_code == 200
    assert monitoring.json()["holdout_accounts"] == 300
    assert len(monitoring.json()["calibration"]) == 5
    assert len(monitoring.json()["feature_stability"]) == 4
    assert "synthetic" in monitoring.json()["data_note"].lower()

