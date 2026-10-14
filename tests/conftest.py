"""Test fixtures for the DataCo API.

Every writable path is redirected to a temporary directory and the geocoder is
kept offline, so running the suite never touches the real administrator
account, the saved prediction history, or the network.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

_TMP = Path(tempfile.mkdtemp(prefix="dataco-tests-"))

SEED_EMAIL = "test-admin@dataco.local"
SEED_PASSWORD = "TestPassw0rd!"

# Set before any src.api import: these are read at module import time.
os.environ["ADMIN_ACCOUNT_FILE"] = str(_TMP / "admin_account.json")
os.environ["PREDICTION_HISTORY_FILE"] = str(_TMP / "predictions.json")
os.environ["ADMIN_EMAIL"] = SEED_EMAIL
os.environ["ADMIN_PASSWORD"] = SEED_PASSWORD
os.environ["GEOCODING_ENABLED"] = "0"
os.environ.setdefault("JWT_SECRET", "x" * 48)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from src.api.main import app

    return TestClient(app)


@pytest.fixture(autouse=True)
def fresh_account():
    """Reset the stored administrator before each test."""
    from src.api import accounts

    if accounts.ACCOUNT_FILE.exists():
        accounts.ACCOUNT_FILE.unlink()

    os.environ["ADMIN_EMAIL"] = SEED_EMAIL
    os.environ["ADMIN_PASSWORD"] = SEED_PASSWORD
    accounts.get_email()  # re-seeds the file

    yield


@pytest.fixture
def token(client):
    response = client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": SEED_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def features():
    """A payload matching DeliveryFeatures / the trained pipeline."""
    return {
        "days_for_shipment_scheduled": 2,
        "shipping_mode": "Standard Class",
        "customer_segment": "Consumer",
        "market": "Europe",
        "order_region": "Western Europe",
        "order_country": "France",
        "category_name": "Cleats",
        "department_name": "Footwear",
        "order_item_quantity": 1,
        "sales": 100.0,
        "order_item_discount": 0.0,
        "order_item_profit_ratio": 0.1,
        "product_price": 100.0,
        "order_month": 10,
        "order_day_of_week": 1,
        "order_quarter": 4,
    }
