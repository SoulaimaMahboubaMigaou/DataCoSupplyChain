
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

from src.api.routes import predictions
import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, tracking

from src.api.history import add_prediction, clear_history, read_history
from src.api.schemas import DeliveryFeatures
from src.api.security import get_current_admin


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "best_delivery_risk_model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

app = FastAPI(
    title="DataCo Supply Chain API",
    description="Delivery delay risk prediction service",
    version="1.0.0",
)


# FRONTEND_ORIGIN accepts a comma-separated list; the Vite dev server runs on
# both localhost and 127.0.0.1 depending on how it is opened.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(tracking.router)
app.include_router(predictions.router)

@app.get("/")
def home():
    return {
        "application": "DataCo Supply Chain Intelligence",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
    }


@app.get("/model-info")
def model_info():
    return {
        "model_type": type(model).__name__,
        "model_path": str(MODEL_PATH.name),
        "features": list(
            getattr(model, "feature_names_in_", [])
        ),
        "feature_count": len(
            getattr(model, "feature_names_in_", [])
        ),
        "has_predict_proba": hasattr(model, "predict_proba"),
    }


@app.post("/predict")
def predict(
    features: DeliveryFeatures,
    admin: dict = Depends(get_current_admin),
):
    try:
        payload = features.model_dump()
        input_data = pd.DataFrame([payload])

        # If the saved pipeline declares feature names,
        # enforce the exact expected names and order.
        expected = getattr(model, "feature_names_in_", None)
        if expected is not None:
            missing = set(expected) - set(input_data.columns)
            extra = set(input_data.columns) - set(expected)

            if missing or extra:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "message": "Input features do not match model schema",
                        "missing": sorted(missing),
                        "extra": sorted(extra),
                    },
                )

            input_data = input_data[list(expected)]

        prediction = model.predict(input_data)[0]

        # Support binary classifiers with classes such as 0 and 1.
        classes = list(getattr(model, "classes_", []))
        if not classes and hasattr(model, "named_steps"):
            final_estimator = list(model.named_steps.values())[-1]
            classes = list(getattr(final_estimator, "classes_", []))

        risk_probability = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_data)[0]
            if 1 in classes:
                risk_probability = float(probabilities[classes.index(1)])

        # This assumes target class 1 means late delivery risk.
        risk = int(prediction) == 1

        result = {
            "prediction_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "late_delivery_risk": int(prediction),
            "risk_label": (
                "High risk of late delivery"
                if risk
                else "Low risk of late delivery"
            ),
            "risk_probability": risk_probability,
        }

        add_prediction({
            **result,
            "features": payload,
        })

        return result

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc


@app.get("/predictions")
def list_predictions(admin: dict = Depends(get_current_admin)):
    return {
        "count": len(read_history()),
        "items": read_history(),
    }


@app.delete("/predictions")
def delete_predictions(admin: dict = Depends(get_current_admin)):
    clear_history()
    return {"message": "Prediction history cleared"}
