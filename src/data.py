"""Data loading, validation, and splitting module for Wine cultivar classification."""

from typing import Tuple
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split

EXPECTED_FEATURE_COUNT = 13
EXPECTED_CLASS_COUNT = 3


def load_raw_data() -> Tuple[pd.DataFrame, pd.Series]:
    """Load the raw Wine dataset from scikit-learn as a DataFrame and Series.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Features X and cultivar targets y.
    """
    dataset = load_wine(as_frame=True)
    features_df: pd.DataFrame = dataset.data
    targets_series: pd.Series = dataset.target
    return features_df, targets_series


def validate_data(features: pd.DataFrame, targets: pd.Series) -> bool:
    """Validate data integrity for Wine dataset.

    Ensures:
      1. Features and targets are non-empty.
      2. Feature count strictly equals 13.
      3. No null or NaN values exist in features or targets.
      4. Target classes are within expected categories (0, 1, 2).

    Args:
        features: Feature DataFrame to validate.
        targets: Target Series to validate.

    Returns:
        bool: True if validation passes.

    Raises:
        ValueError: If any validation rule is violated.
    """
    if features is None or targets is None:
        raise ValueError("Features and targets must not be None.")

    if len(features) == 0 or len(targets) == 0:
        raise ValueError("Features and targets must be non-empty.")

    if len(features) != len(targets):
        raise ValueError(
            f"Sample count mismatch: features ({len(features)}) vs targets ({len(targets)})."
        )

    if features.shape[1] != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"Feature count mismatch: expected {EXPECTED_FEATURE_COUNT}, got {features.shape[1]}."
        )

    null_feature_count = int(features.isnull().sum().sum())
    if null_feature_count > 0:
        raise ValueError(f"Null values detected in features: {null_feature_count} nulls found.")

    null_target_count = int(targets.isnull().sum())
    if null_target_count > 0:
        raise ValueError(f"Null values detected in targets: {null_target_count} nulls found.")

    unique_classes = set(targets.unique())
    expected_classes = set(range(EXPECTED_CLASS_COUNT))
    if not unique_classes.issubset(expected_classes):
        raise ValueError(
            f"Invalid target classes found: {unique_classes - expected_classes}. "
            f"Expected subset of {expected_classes}."
        )

    return True


def load_and_split_data(
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Load Wine dataset, validate integrity, and perform stratified 80/20 split.

    Args:
        test_size: Proportion of dataset allocated to the holdout test split (default 0.2).
        random_state: Fixed random seed for reproducible stratification (default 42).

    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    """
    features, targets = load_raw_data()
    validate_data(features, targets)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        targets,
        test_size=test_size,
        stratify=targets,
        random_state=random_state
    )

    validate_data(x_train, y_train)
    validate_data(x_test, y_test)

    return x_train, x_test, y_train, y_test


if __name__ == "__main__":
    X_tr, X_te, y_tr, y_te = load_and_split_data()
    print("Data pipeline executed successfully:")
    print(f"  Training samples: {X_tr.shape[0]}, Features: {X_tr.shape[1]}")
    print(f"  Test samples:     {X_te.shape[0]}, Features: {X_te.shape[1]}")
    print(f"  Target distribution (train): {dict(y_tr.value_counts())}")
    print(f"  Target distribution (test):  {dict(y_te.value_counts())}")
