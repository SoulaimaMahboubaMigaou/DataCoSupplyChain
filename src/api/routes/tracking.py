import os
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.geo import geocode
from src.api.security import get_current_admin

router = APIRouter(
    prefix="/tracking",
    tags=["Shipment Tracking"],
    dependencies=[Depends(get_current_admin)],
)

ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = Path(
    os.getenv(
        "DATASET_PATH",
        str(ROOT / "data" / "processed" / "DataCo_featured.csv"),
    )
)

# Maximum number of rows resolved through the geocoder in one list request.
GEOCODE_LIVE_LIMIT = 10

COLUMN_ALIASES = {
    "order_id": ["Order Id", "order_id", "Order ID"],
    "status": ["Delivery Status", "delivery_status", "Order Status", "order_status"],
    "late_risk": ["Late_delivery_risk", "late_delivery_risk"],
    "shipping_mode": ["Shipping Mode", "shipping_mode"],
    "order_date": [
        "order date (DateOrders)", "order_date", "order_date_dateorders",
    ],
    "shipping_date": [
        "shipping date (DateOrders)", "shipping_date", "shipping_date_dateorders",
    ],
    "customer_city": ["Customer City", "customer_city"],
    "customer_country": ["Customer Country", "customer_country"],
    "customer_state": ["Customer State", "customer_state"],
    "order_city": ["Order City", "order_city"],
    "order_country": ["Order Country", "order_country"],
    "order_state": ["Order State", "order_state"],
    "customer_lat": [
        "Latitude", "Customer Latitude", "customer_latitude", "latitude",
    ],
    "customer_lon": [
        "Longitude", "Customer Longitude", "customer_longitude", "longitude",
    ],
    "order_lat": ["Order Latitude", "order_latitude"],
    "order_lon": ["Order Longitude", "order_longitude"],
    "customer_first": ["Customer Fname", "customer_fname", "customer_first_name"],
    "customer_last": ["Customer Lname", "customer_lname", "customer_last_name"],
    "scheduled_days": ["Days for shipment (scheduled)", "days_for_shipment_scheduled"],
    "real_days": ["Days for shipping (real)", "days_for_shipping_real"],
}


def load_orders() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Dataset introuvable : {DATASET_PATH}",
        )

    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = [str(column).strip() for column in df.columns]
    return df


def find_column(df: pd.DataFrame, logical_name: str):
    for candidate in COLUMN_ALIASES.get(logical_name, []):
        if candidate in df.columns:
            return candidate
    return None


def value(row, column):
    if not column:
        return None
    item = row.get(column)
    if pd.isna(item):
        return None
    if hasattr(item, "item"):
        item = item.item()
    return item


def safe_float(item):
    try:
        number = float(item)
        if pd.notna(number) and -180 <= number <= 180:
            return number
    except (TypeError, ValueError):
        pass
    return None


def serialize_order(row, mapping, allow_geocoding: bool = False):
    result = {
        "tracking_id": str(value(row, mapping["order_id"]) or ""),
        "status": str(value(row, mapping["status"]) or "Unknown"),
        "shipping_mode": value(row, mapping["shipping_mode"]),
        "order_date": value(row, mapping["order_date"]),
        "shipping_date": value(row, mapping["shipping_date"]),
        "customer_city": value(row, mapping["customer_city"]),
        "customer_country": value(row, mapping["customer_country"]),
        "customer_state": value(row, mapping["customer_state"]),
        "destination_city": value(row, mapping["order_city"]),
        "destination_country": value(row, mapping["order_country"]),
        "destination_state": value(row, mapping["order_state"]),
        "customer_name": " ".join(
            str(part) for part in [
                value(row, mapping["customer_first"]),
                value(row, mapping["customer_last"]),
            ] if part
        ) or None,
        "late_delivery_risk": value(row, mapping["late_risk"]),
        "scheduled_days": value(row, mapping["scheduled_days"]),
        "real_days": value(row, mapping["real_days"]),
        "origin": None,
        "destination": None,
        "destination_source": None,
        "position_type": "historical_data",
    }

    lat = safe_float(value(row, mapping["customer_lat"]))
    lon = safe_float(value(row, mapping["customer_lon"]))
    if lat is not None and lon is not None and -90 <= lat <= 90:
        result["origin"] = {"lat": lat, "lon": lon}

    lat = safe_float(value(row, mapping["order_lat"]))
    lon = safe_float(value(row, mapping["order_lon"]))
    if lat is not None and lon is not None and -90 <= lat <= 90:
        result["destination"] = {"lat": lat, "lon": lon}
        result["destination_source"] = "dataset"

    # DataCo ships without destination coordinates, so the order city is
    # geocoded (cached on disk) to place the delivery point on the map.
    if result["destination"] is None:
        point = geocode(
            city=result["destination_city"],
            state=result["destination_state"],
            country=result["destination_country"],
            allow_network=allow_geocoding,
        )
        if point:
            result["destination"] = point
            result["destination_source"] = "geocoded"

    for key in ("order_date", "shipping_date"):
        if result[key] is not None:
            result[key] = str(result[key])

    return result


def prepare_data():
    df = load_orders()
    mapping = {
        key: find_column(df, key)
        for key in COLUMN_ALIASES
    }

    if not mapping["order_id"]:
        raise HTTPException(
            status_code=500,
            detail=(
                "Colonne d'identifiant introuvable. "
                f"Colonnes disponibles : {df.columns.tolist()}"
            ),
        )

    df = df.where(pd.notna(df), None)
    return df, mapping


@router.get("/columns")
def available_columns():
    df = load_orders()
    return {"columns": df.columns.tolist()}


@router.get("/summary")
def tracking_summary():
    df, mapping = prepare_data()
    status_col = mapping["status"]
    risk_col = mapping["late_risk"]

    statuses = {}
    if status_col:
        statuses = (
            df[status_col].fillna("Unknown").astype(str)
            .value_counts().to_dict()
        )

    # Le CSV traité ne contient que "Late" / "On Time" ; le dataset brut utilise
    # "Shipping on time" / "Advance shipping". On couvre les deux vocabulaires.
    on_time = sum(
        count for name, count in statuses.items()
        if "on time" in name.lower() or "advance" in name.lower()
    )
    late = sum(
        count for name, count in statuses.items()
        if "late" in name.lower()
    )

    return {
        "total_orders": int(len(df)),
        "statuses": statuses,
        "on_time_count": int(on_time),
        "late_count": int(late),
        "late_risk_count": (
            int(pd.to_numeric(df[risk_col], errors="coerce").eq(1).sum())
            if risk_col else None
        ),
        "data_mode": "historical_dataset",
    }


@router.get("/shipments")
def list_shipments(
    search: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    df, mapping = prepare_data()
    id_col = mapping["order_id"]
    status_col = mapping["status"]

    if search:
        df = df[df[id_col].astype(str).str.contains(
            search, case=False, na=False, regex=False
        )]

    if status and status_col:
        df = df[df[status_col].astype(str).str.lower() == status.lower()]

    page = df.iloc[offset:offset + limit]
    total = len(df)

    # Geocoding is network-bound, so only a short result set (typically a
    # tracking-id search) is resolved live. Longer lists still use whatever
    # the cache already holds.
    allow_geocoding = len(page) <= GEOCODE_LIVE_LIMIT

    records = [
        serialize_order(row, mapping, allow_geocoding=allow_geocoding)
        for _, row in page.iterrows()
    ]

    return {
        "items": records,
        "total": int(total),
        "limit": limit,
        "offset": offset,
        "data_mode": "historical_dataset",
    }


@router.get("/shipments/{tracking_id}")
def shipment_detail(tracking_id: str):
    df, mapping = prepare_data()
    id_col = mapping["order_id"]

    match = df[df[id_col].astype(str) == tracking_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    return serialize_order(match.iloc[0], mapping, allow_geocoding=True)
