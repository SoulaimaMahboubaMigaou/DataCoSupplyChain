"""Prediction endpoint and schema tests."""


def test_health_reports_the_loaded_model(client):
    body = client.get("/health").json()

    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_model_info_matches_the_request_schema(client, features):
    """The pipeline must expect exactly the features the API accepts."""
    body = client.get("/model-info").json()

    assert body["has_predict_proba"] is True

    if body["features"]:
        assert sorted(body["features"]) == sorted(features)


def test_predict_returns_a_risk_and_a_probability(client, auth, features):
    response = client.post("/predict", json=features, headers=auth)

    assert response.status_code == 200
    body = response.json()

    assert body["late_delivery_risk"] in (0, 1)
    assert body["risk_label"]
    assert body["prediction_id"]
    assert body["created_at"]
    assert 0.0 <= body["risk_probability"] <= 1.0


def test_predict_rejects_a_missing_feature(client, auth, features):
    features.pop("shipping_mode")

    assert client.post(
        "/predict", json=features, headers=auth
    ).status_code == 422


def test_predict_rejects_out_of_range_values(client, auth, features):
    for field, value in [
        ("order_month", 13),
        ("order_day_of_week", 7),
        ("order_quarter", 0),
        ("order_item_quantity", 0),
        ("sales", -1),
    ]:
        payload = dict(features, **{field: value})
        assert client.post(
            "/predict", json=payload, headers=auth
        ).status_code == 422, field


def test_predict_is_recorded_in_the_history(client, auth, features):
    before = client.get("/predictions", headers=auth).json()["count"]

    created = client.post("/predict", json=features, headers=auth).json()
    after = client.get("/predictions", headers=auth).json()

    assert after["count"] == before + 1
    assert after["items"][0]["prediction_id"] == created["prediction_id"]
    assert after["items"][0]["features"] == features


def test_history_can_be_cleared(client, auth, features):
    client.post("/predict", json=features, headers=auth)
    client.delete("/predictions", headers=auth)

    assert client.get("/predictions", headers=auth).json()["count"] == 0


def test_prediction_endpoints_require_authentication(client, features):
    assert client.post("/predict", json=features).status_code == 401
    assert client.get("/predictions").status_code == 401
    assert client.delete("/predictions").status_code == 401


def test_tracking_prediction_requires_a_known_order(client, auth):
    assert client.post(
        "/predictions/not-an-order", headers=auth
    ).status_code == 404
