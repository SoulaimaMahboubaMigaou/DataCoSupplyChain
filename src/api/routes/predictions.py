
import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from src.api.security import get_current_admin

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
    dependencies=[Depends(get_current_admin)],
)

ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = Path(
    os.getenv(
        "DATASET_PATH",
        str(ROOT / "data" / "processed" / "DataCo_featured.csv"),
    )
)
MODEL_PATH = ROOT / "models" / "best_delivery_risk_model.pkl"

FEATURES = [
    "days_for_shipment_scheduled",
    "shipping_mode",
    "customer_segment",
    "market",
    "order_region",
    "order_country",
    "category_name",
    "department_name",
    "order_item_quantity",
    "sales",
    "order_item_discount",
    "order_item_profit_ratio",
    "product_price",
    "order_month",
    "order_day_of_week",
    "order_quarter",
]


@router.post("/{tracking_id}")
def predict_delivery_risk(
    tracking_id: str,
):
    if not DATASET_PATH.exists():
        raise HTTPException(503, "Dataset introuvable")

    if not MODEL_PATH.exists():
        raise HTTPException(503, "Modèle ML introuvable")

    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    id_candidates = ["Order Id", "order_id", "Order ID"]
    id_column = next(
        (c for c in id_candidates if c in df.columns), None
    )

    if id_column is None:
        raise HTTPException(
            500,
            "Colonne ID de commande introuvable. Vérifie /tracking/columns.",
        )

    matches = df[df[id_column].astype(str) == tracking_id]

    if matches.empty:
        raise HTTPException(404, "Commande introuvable")

    missing = [feature for feature in FEATURES if feature not in df.columns]
    if missing:
        raise HTTPException(
            500,
            detail={
                "message": "Des variables du modèle sont absentes du CSV.",
                "missing_features": missing,
            },
        )

    model = joblib.load(MODEL_PATH)
    X = matches[FEATURES].head(1)

    try:
        prediction = int(model.predict(X)[0])
        probability = None

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X)[0]
            classes = list(model.classes_)
            if 1 in classes:
                probability = float(probabilities[classes.index(1)])

    except Exception as exc:
        raise HTTPException(
            500,
            detail=f"Erreur lors de la prédiction : {exc}",
        ) from exc

    return {
        "tracking_id": tracking_id,
        "predicted_late_delivery_risk": prediction,
        "risk_label": "High risk" if prediction == 1 else "Low risk",
        "risk_probability": probability,
        "model": "Random Forest",
        "data_mode": "prediction_from_historical_order_features",
    }
