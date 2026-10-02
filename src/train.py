"""Model training, 5-fold cross-validation, and MLflow model registry module."""

import os
import time
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import StratifiedKFold

os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
import mlflow  # noqa: E402
from mlflow.models import infer_signature  # noqa: E402
from mlflow.tracking import MlflowClient  # noqa: E402

from src.data import load_and_split_data  # noqa: E402

EXPERIMENT_NAME = "Wine-Cultivar-Classification-Production-Main"
REGISTERED_MODEL_NAME = "WineClassifier"
CHAMPION_ALIAS = "champion"
DEFAULT_DB_FILE = "mlflow.db"


def get_tracking_uri(db_path: str = DEFAULT_DB_FILE) -> str:
    """Return SQLite tracking URI for MLflow.

    Args:
        db_path: Relative or absolute path to SQLite file.

    Returns:
        str: Formatted tracking URI.
    """
    abs_path = os.path.abspath(db_path)
    return f"sqlite:///{abs_path}"


def get_search_grids() -> Dict[str, List[Dict[str, Any]]]:
    """Define search grids for RandomForest and GradientBoosting classifiers.

    Returns:
        Dict mapping model family name to list of candidate configurations.
    """
    return {
        "RandomForestClassifier": [
            {
                "n_estimators": 50,
                "max_depth": 3,
                "min_samples_split": 2,
                "random_state": 42,
            },
            {
                "n_estimators": 100,
                "max_depth": 5,
                "min_samples_split": 2,
                "random_state": 42,
            },
            {
                "n_estimators": 150,
                "max_depth": 7,
                "min_samples_split": 4,
                "random_state": 42,
            },
        ],
        "GradientBoostingClassifier": [
            {
                "n_estimators": 50,
                "learning_rate": 0.05,
                "max_depth": 3,
                "random_state": 42,
            },
            {
                "n_estimators": 100,
                "learning_rate": 0.10,
                "max_depth": 3,
                "random_state": 42,
            },
            {
                "n_estimators": 150,
                "learning_rate": 0.10,
                "max_depth": 5,
                "random_state": 42,
            },
        ],
    }


def instantiate_model(family: str, params: Dict[str, Any]):
    """Instantiate a classifier instance based on family name and parameters.

    Args:
        family: 'RandomForestClassifier' or 'GradientBoostingClassifier'.
        params: Hyperparameter dictionary.

    Returns:
        BaseEstimator: Instantiated classifier.
    """
    if family == "RandomForestClassifier":
        return RandomForestClassifier(**params)
    elif family == "GradientBoostingClassifier":
        return GradientBoostingClassifier(**params)
    raise ValueError(f"Unsupported model family: {family}")


def evaluate_cv_5fold(
    family: str,
    params: Dict[str, Any],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    n_splits: int = 5,
    random_state: int = 42,
) -> Tuple[Dict[str, float], Any]:
    """Evaluate configuration via 5-fold stratified cross-validation.

    Computes Macro F1-score, Accuracy, and Log Loss on train and validation folds.

    Args:
        family: Model family name.
        params: Model hyperparameters.
        x_train: Training features DataFrame.
        y_train: Training targets Series.
        n_splits: Number of CV folds (default 5).
        random_state: Stratification random state (default 42).

    Returns:
        Tuple of (metrics_dict, fully_fitted_model).
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    labels = [0, 1, 2]

    train_f1s, val_f1s = [], []
    train_accs, val_accs = [], []
    train_losses, val_losses = [], []

    for fold_train_idx, fold_val_idx in skf.split(x_train, y_train):
        x_tr = x_train.iloc[fold_train_idx]
        y_tr = y_train.iloc[fold_train_idx]
        x_va = x_train.iloc[fold_val_idx]
        y_va = y_train.iloc[fold_val_idx]

        model = instantiate_model(family, params)
        model.fit(x_tr, y_tr)

        # Train predictions
        y_tr_pred = model.predict(x_tr)
        y_tr_prob = model.predict_proba(x_tr)
        train_f1s.append(f1_score(y_tr, y_tr_pred, average="macro"))
        train_accs.append(accuracy_score(y_tr, y_tr_pred))
        train_losses.append(log_loss(y_tr, y_tr_prob, labels=labels))

        # Val predictions
        y_va_pred = model.predict(x_va)
        y_va_prob = model.predict_proba(x_va)
        val_f1s.append(f1_score(y_va, y_va_pred, average="macro"))
        val_accs.append(accuracy_score(y_va, y_va_pred))
        val_losses.append(log_loss(y_va, y_va_prob, labels=labels))

    metrics = {
        "train_macro_f1": float(np.mean(train_f1s)),
        "val_macro_f1": float(np.mean(val_f1s)),
        "train_accuracy": float(np.mean(train_accs)),
        "val_accuracy": float(np.mean(val_accs)),
        "train_log_loss": float(np.mean(train_losses)),
        "val_log_loss": float(np.mean(val_losses)),
    }

    # Fit final model on full training split
    full_model = instantiate_model(family, params)
    full_model.fit(x_train, y_train)

    return metrics, full_model


def run_experiments(
    db_path: str = DEFAULT_DB_FILE
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Execute hyperparameter experimentation, MLflow logging, and champion promotion.

    Args:
        db_path: SQLite database file path for MLflow tracking backend.

    Returns:
        Tuple of (all_run_results, best_run_info).
    """
    tracking_uri = get_tracking_uri(db_path)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    x_train, x_test, y_train, y_test = load_and_split_data(test_size=0.2, random_state=42)

    grids = get_search_grids()
    run_records: List[Dict[str, Any]] = []

    print(f"Starting MLflow experimentation with backend: {tracking_uri}")
    print(f"Experiment: {EXPERIMENT_NAME}\n")

    for family, config_list in grids.items():
        for idx, config in enumerate(config_list, start=1):
            run_name = f"{family}_config_{idx}"
            print(f"--- Running {run_name} ---")
            print(f"Parameters: {config}")

            cv_metrics, fitted_model = evaluate_cv_5fold(family, config, x_train, y_train)

            print(f"CV Val Macro F1: {cv_metrics['val_macro_f1']:.4f} | "
                  f"Val Acc: {cv_metrics['val_accuracy']:.4f} | "
                  f"Val LogLoss: {cv_metrics['val_log_loss']:.4f}")

            with mlflow.start_run(run_name=run_name) as run:
                run_id = run.info.run_id

                # 1. Log tags
                mlflow.set_tag("model_family", family)
                mlflow.set_tag("framework", "scikit-learn")
                mlflow.set_tag("config_index", str(idx))
                mlflow.set_tag("cv_method", "5-fold StratifiedKFold")

                # 2. Log parameters
                mlflow.log_params(config)
                mlflow.log_param("cv_folds", 5)
                mlflow.log_param("random_state", 42)

                # 3. Log metrics
                mlflow.log_metrics(cv_metrics)

                # 4. Signatures and Input Example
                signature = infer_signature(x_train, fitted_model.predict(x_train))
                input_example = x_train.iloc[:5]

                # 5. Log Model Artifact
                mlflow.sklearn.log_model(
                    sk_model=fitted_model,
                    artifact_path="model",
                    signature=signature,
                    input_example=input_example,
                    serialization_format="cloudpickle",
                )

                record = {
                    "run_id": run_id,
                    "run_name": run_name,
                    "family": family,
                    "config": config,
                    "metrics": cv_metrics,
                    "model_uri": f"runs:/{run_id}/model",
                }
                run_records.append(record)

    # Identify champion based on validation macro F1-score
    best_record = max(run_records, key=lambda r: r["metrics"]["val_macro_f1"])

    print("\n=======================================================")
    print("EXPERIMENTATION SUMMARY & CHAMPION PROMOTION")
    print(f"Total runs logged: {len(run_records)}")
    print(f"Champion Run ID:   {best_record['run_id']}")
    print(f"Champion Model:    {best_record['run_name']}")
    print(f"Best Val Macro F1: {best_record['metrics']['val_macro_f1']:.4f}")
    print("=======================================================\n")

    # Register champion model into MLflow Model Registry
    client = MlflowClient()
    model_version = mlflow.register_model(
        model_uri=best_record["model_uri"],
        name=REGISTERED_MODEL_NAME,
    )

    # Assign alias 'champion'
    client.set_registered_model_alias(
        name=REGISTERED_MODEL_NAME,
        alias=CHAMPION_ALIAS,
        version=model_version.version,
    )
    print(
        f"Assigned alias '{CHAMPION_ALIAS}' to {REGISTERED_MODEL_NAME} "
        f"version {model_version.version}"
    )

    return run_records, best_record


if __name__ == "__main__":
    start_time = time.time()
    runs, champion = run_experiments()
    duration = time.time() - start_time
    print(f"Training and MLflow pipeline completed in {duration:.2f} seconds.")
