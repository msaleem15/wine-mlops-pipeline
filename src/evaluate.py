"""Inference verification module for loading champion model and evaluating on test split."""

import os
import time
from typing import Any, Dict
from sklearn.metrics import accuracy_score, f1_score, log_loss

os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
import mlflow  # noqa: E402

from src.data import load_and_split_data  # noqa: E402
from src.train import (  # noqa: E402
    CHAMPION_ALIAS,
    DEFAULT_DB_FILE,
    REGISTERED_MODEL_NAME,
    get_tracking_uri,
    run_experiments,
)


def load_champion_model(db_path: str = DEFAULT_DB_FILE) -> Any:
    """Load the champion model version from MLflow Model Registry.

    If no model has been registered yet, triggers training to establish champion.

    Args:
        db_path: Path to SQLite MLflow database.

    Returns:
        Loaded scikit-learn model estimator.
    """
    tracking_uri = get_tracking_uri(db_path)
    mlflow.set_tracking_uri(tracking_uri)

    champion_model_uri = f"models:/{REGISTERED_MODEL_NAME}@{CHAMPION_ALIAS}"

    try:
        model = mlflow.sklearn.load_model(model_uri=champion_model_uri)
        return model
    except Exception as exc:
        print(f"Registered champion model not found ({exc}). Running training pipeline...")
        run_experiments(db_path=db_path)
        return mlflow.sklearn.load_model(model_uri=champion_model_uri)


def evaluate_test_set(
    model: Any = None,
    db_path: str = DEFAULT_DB_FILE,
) -> Dict[str, float]:
    """Perform inference on the holdout test set and calculate evaluation metrics.

    Args:
        model: Optional pre-loaded model. If None, loads registered champion.
        db_path: Path to MLflow database.

    Returns:
        Dict[str, float]: Evaluation metrics (test_macro_f1, test_accuracy,
                          test_log_loss, batch_latency_ms).
    """
    if model is None:
        model = load_champion_model(db_path=db_path)

    _, x_test, _, y_test = load_and_split_data(test_size=0.2, random_state=42)

    # Measure batch inference latency
    start_time = time.perf_counter()
    y_pred = model.predict(x_test)
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000.0

    y_prob = model.predict_proba(x_test)

    test_macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
    test_accuracy = float(accuracy_score(y_test, y_pred))
    test_loss = float(log_loss(y_test, y_prob, labels=[0, 1, 2]))

    results = {
        "test_macro_f1": test_macro_f1,
        "test_accuracy": test_accuracy,
        "test_log_loss": test_loss,
        "batch_latency_ms": latency_ms,
        "test_samples": float(len(x_test)),
    }

    print("\n=======================================================")
    print("INFERENCE VERIFICATION ON HOLDOUT TEST SPLIT")
    print(f"Test Samples:      {len(x_test)}")
    print(f"Test Macro F1:     {test_macro_f1:.4f}")
    print(f"Test Accuracy:     {test_accuracy:.4f}")
    print(f"Test Log Loss:     {test_loss:.4f}")
    print(f"Batch Latency:     {latency_ms:.2f} ms")
    print("=======================================================\n")

    return results


if __name__ == "__main__":
    evaluate_test_set()
