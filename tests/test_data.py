"""Unit tests for the Wine data pipeline module."""

import numpy as np
import pandas as pd
import pytest
from src.data import (
    load_raw_data,
    load_and_split_data,
    validate_data,
    EXPECTED_FEATURE_COUNT,
    EXPECTED_CLASS_COUNT,
)


def test_load_raw_data_shape_and_types():
    """Verify raw dataset loading returns expected shape and non-empty structures."""
    features, targets = load_raw_data()
    assert isinstance(features, pd.DataFrame)
    assert isinstance(targets, pd.Series)
    assert features.shape == (178, EXPECTED_FEATURE_COUNT)
    assert len(targets) == 178
    assert set(targets.unique()) == set(range(EXPECTED_CLASS_COUNT))


def test_data_validation_success():
    """Verify validation passes cleanly for correct data."""
    features, targets = load_raw_data()
    assert validate_data(features, targets) is True


def test_data_validation_missing_values_error():
    """Verify validation raises ValueError when null values are injected."""
    features, targets = load_raw_data()
    corrupted_features = features.copy()
    corrupted_features.iloc[0, 0] = np.nan
    with pytest.raises(ValueError, match="Null values detected in features"):
        validate_data(corrupted_features, targets)

    corrupted_targets = targets.copy()
    corrupted_targets.iloc[0] = np.nan
    with pytest.raises(ValueError, match="Null values detected in targets"):
        validate_data(features, corrupted_targets)


def test_data_validation_feature_count_error():
    """Verify validation raises ValueError when feature count is not 13."""
    features, targets = load_raw_data()
    corrupted_features = features.iloc[:, :10]  # only 10 features
    with pytest.raises(ValueError, match="Feature count mismatch"):
        validate_data(corrupted_features, targets)


def test_data_validation_invalid_classes_error():
    """Verify validation raises ValueError when unexpected class labels are present."""
    features, targets = load_raw_data()
    corrupted_targets = targets.copy()
    corrupted_targets.iloc[0] = 99
    with pytest.raises(ValueError, match="Invalid target classes found"):
        validate_data(features, corrupted_targets)


def test_load_and_split_data_shapes_and_stratification():
    """Verify stratified split produces expected 80/20 train/test proportions."""
    x_train, x_test, y_train, y_test = load_and_split_data(test_size=0.2, random_state=42)

    total_samples = 178
    expected_test_count = int(np.round(total_samples * 0.2))  # 36
    expected_train_count = total_samples - expected_test_count  # 142

    assert len(x_train) == expected_train_count
    assert len(x_test) == expected_test_count
    assert x_train.shape[1] == EXPECTED_FEATURE_COUNT
    assert x_test.shape[1] == EXPECTED_FEATURE_COUNT

    # Validate stratification ratios are preserved across train and test
    train_dist = y_train.value_counts(normalize=True).sort_index()
    test_dist = y_test.value_counts(normalize=True).sort_index()

    for cls in range(EXPECTED_CLASS_COUNT):
        diff = abs(train_dist[cls] - test_dist[cls])
        assert diff < 0.05, f"Stratification deviation too high for class {cls}: {diff:.4f}"
