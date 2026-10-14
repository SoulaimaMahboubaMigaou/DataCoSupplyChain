
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

# --------------------------------------------------
# 1. Chemins du projet
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "DataCo_featured.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "best_delivery_risk_model.pkl"

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset introuvable : {DATA_PATH}")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Modèle introuvable : {MODEL_PATH}. "
        "Exécute d'abord la cellule de sauvegarde du notebook."
    )

# --------------------------------------------------
# 2. Charger les données et le modèle entraîné
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

features = [
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

X = df[features]
y = df["late_delivery_risk"]

# Même séparation que dans le notebook
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# Pipeline complet : prétraitement + Random Forest
model = joblib.load(MODEL_PATH)

# --------------------------------------------------
# 3. Prédictions et métriques
# --------------------------------------------------

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

metrics = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(
        y_test, y_pred, zero_division=0
    ),
    "recall": recall_score(
        y_test, y_pred, zero_division=0
    ),
    "f1_score": f1_score(
        y_test, y_pred, zero_division=0
    ),
    "roc_auc": roc_auc_score(y_test, y_proba),
}

# --------------------------------------------------
# 4. Configuration MLflow
# --------------------------------------------------

MLFLOW_DB = PROJECT_ROOT / "mlflow.db"

mlflow.set_tracking_uri(
    f"sqlite:///{MLFLOW_DB.as_posix()}"
)

mlflow.set_experiment("DataCo-Delivery-Risk")

# --------------------------------------------------
# 5. Enregistrer le run
# --------------------------------------------------

with mlflow.start_run(run_name="RandomForest-Delivery-Risk"):

    # Paramètres principaux du Random Forest
    rf = model.named_steps["model"]

    mlflow.log_params({
        "model_type": "RandomForestClassifier",
        "n_estimators": rf.n_estimators,
        "max_depth": (
            rf.max_depth
            if rf.max_depth is not None
            else "None"
        ),
        "random_state": rf.random_state,
        "test_size": 0.2,
        "split_random_state": 42,
        "number_of_features": len(features),
        "training_rows": len(X_train),
        "test_rows": len(X_test),
    })

    # Métriques calculées sur le jeu de test
    mlflow.log_metrics(metrics)

    # Enregistrer le pipeline complet comme artefact MLflow
    mlflow.sklearn.log_model(
    sk_model=model,
    name="random_forest_delivery_risk",
    serialization_format="cloudpickle",
    input_example=X_train.head(3),
)
    print("Run MLflow enregistré avec succès !")
    print("\nMétriques :")

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")

    print("\nRun ID :", mlflow.active_run().info.run_id)

print("\nTerminé. Lance l'interface MLflow pour consulter le run.")