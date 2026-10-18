from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from cloudcost_ai.config import PROJECT_ROOT
from cloudcost_ai.utils.logger import get_logger
from cloudcost_ai.utils.exception import CustomException

logger = get_logger(__name__)

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "anomaly_detector.joblib"

NUMERIC_FEATURES = [
    "usage_quantity",
    "unit_price",
    "cost",
    "cpu_utilization_pct",
    "memory_utilization_pct",
    "storage_utilization_pct",
    "request_count",
    "data_transfer_gb",
    "resource_age_days",
    "monthly_budget",
    "utilization_efficiency_pct",
    "previous_period_cost",
    "cost_growth_pct",
    "budget_utilization_pct",
]

CATEGORICAL_FEATURES = [
    "cloud_provider",
    "department",
    "environment",
    "region",
    "service",
    "resource_type",
    "resource_status",
    "billing_category",
    "billing_currency",
]

TARGET = "is_anomaly"


def build_pipeline():
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_anomaly_detector(
    billing_path=None,
    ground_truth_path=None,
    model_path=None,
):
    try:
        billing_path = billing_path or (
            PROJECT_ROOT / "data" / "raw" / "cloudcost_billing_50000.csv"
        )
        ground_truth_path = ground_truth_path or (
            PROJECT_ROOT / "data" / "raw" / "cloudcost_anomaly_ground_truth.csv"
        )
        model_path = Path(model_path or MODEL_PATH)

        billing = pd.read_csv(billing_path)
        truth = pd.read_csv(ground_truth_path)

        required_truth_columns = {"usage_id", "anomaly_type", "episode_id"}
        if not required_truth_columns.issubset(truth.columns):
            raise ValueError(
                f"Ground truth must contain {sorted(required_truth_columns)}"
            )

        if billing["usage_id"].duplicated().any():
            raise ValueError("Billing data contains duplicate usage_id values")

        if truth["usage_id"].duplicated().any():
            raise ValueError("Ground truth contains duplicate usage_id values")

        missing_features = [
            col
            for col in NUMERIC_FEATURES + CATEGORICAL_FEATURES
            if col not in billing.columns
        ]

        if missing_features:
            raise ValueError(f"Missing model features: {missing_features}")

        unknown_ids = set(truth["usage_id"]) - set(billing["usage_id"])
        if unknown_ids:
            raise ValueError(
                f"{len(unknown_ids)} ground-truth IDs do not exist in billing data"
            )

        billing[TARGET] = billing["usage_id"].isin(truth["usage_id"]).astype(int)

        X = billing[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
        y = billing[TARGET]

        if y.nunique() != 2:
            raise ValueError(
                "Training requires both normal and anomaly examples"
            )

        x_train, x_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            stratify=y,
            random_state=42,
        )

        pipeline = build_pipeline()
        pipeline.fit(x_train, y_train)

        predictions = pipeline.predict(x_test)
        probabilities = pipeline.predict_proba(x_test)[:, 1]

        metrics = {
            "precision": precision_score(
                y_test, predictions, zero_division=0
            ),
            "recall": recall_score(
                y_test, predictions, zero_division=0
            ),
            "f1_score": f1_score(
                y_test, predictions, zero_division=0
            ),
            "average_precision": average_precision_score(
                y_test, probabilities
            ),
        }

        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, model_path)

        print("\nANOMALY DETECTOR - TEST RESULTS")
        print(f"Training records: {len(x_train)}")
        print(f"Test records: {len(x_test)}")
        print(f"Known anomaly rate: {y.mean():.2%}")
        print(f"Model saved to: {model_path}")

        print("\nMETRICS:")
        for name, value in metrics.items():
            print(f"{name}: {value:.4f}")

        print("\nConfusion matrix [[TN, FP], [FN, TP]]:")
        print(confusion_matrix(y_test, predictions))

        print("\nClassification report:")
        print(
            classification_report(
                y_test,
                predictions,
                target_names=["normal", "anomaly"],
                zero_division=0,
            )
        )

        logger.info(
            "Anomaly model trained. Records=%s, anomalies=%s, metrics=%s",
            len(billing),
            int(y.sum()),
            metrics,
        )

        return pipeline, metrics

    except Exception as error:
        logger.exception("Anomaly detector training failed")
        raise CustomException(error) from error


if __name__ == "__main__":
    train_anomaly_detector()