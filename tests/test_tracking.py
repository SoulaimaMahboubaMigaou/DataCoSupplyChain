"""Shipment tracking tests (historical dataset, no live GPS)."""

KNOWN_ORDER = "75939"


def test_summary_exposes_dataset_counters(client, auth):
    body = client.get("/tracking/summary", headers=auth).json()

    assert body["total_orders"] > 0
    assert body["data_mode"] == "historical_dataset"
    assert isinstance(body["statuses"], dict)


def test_search_returns_the_matching_order_with_coordinates(client, auth):
    body = client.get(
        f"/tracking/shipments?search={KNOWN_ORDER}&limit=5", headers=auth
    ).json()

    assert body["total"] >= 1

    order = next(
        item for item in body["items"] if item["tracking_id"] == KNOWN_ORDER
    )

    # The customer coordinates come straight from the dataset.
    assert order["origin"] is not None
    assert -90 <= order["origin"]["lat"] <= 90
    assert -180 <= order["origin"]["lon"] <= 180
    assert order["destination_city"]
    assert order["destination_country"]


def test_detail_reports_historical_fields(client, auth):
    body = client.get(f"/tracking/shipments/{KNOWN_ORDER}", headers=auth).json()

    assert body["tracking_id"] == KNOWN_ORDER
    assert body["status"]
    assert body["order_date"]
    assert body["shipping_date"]
    assert body["position_type"] == "historical_data"
    # Either from the dataset or geocoded, never invented silently.
    assert body["destination_source"] in (None, "dataset", "geocoded")


def test_unknown_order_returns_404(client, auth):
    assert client.get(
        "/tracking/shipments/does-not-exist", headers=auth
    ).status_code == 404
