"""Automated MLOps Quality Gate tests for Wine cultivar classification."""

import time
import numpy as np
import pytest
from sklearn.metrics import f1_score
from src.data import EXPECTED_CLASS_COUNT, load_and_split_data
from src.evaluate import load_champion_model


@pytest.fixture(scope="module")
def model_and_data():
    """Fixture providing champion model and test split."""
    model = load_champion_model()
    _, x_test, _, y_test = load_and_split_data(test_size=0.2, random_state=42)
    return model, x_test, y_test


def test_metric_threshold_gate(model_and_data):
    """Quality Gate 1: Assert Macro F1-score is at or above the 0.88 threshold."""
    model, x_test, y_test = model_and_data
    y_pred = model.predict(x_test)
    macro_f1 = float(f1_score(y_test, y_pred, average="macro"))

    print(f"\n[Quality Gate] Measured Holdout Macro F1: {macro_f1:.4f} (Required >= 0.88)")
    assert macro_f1 >= 0.88, (
        f"Model failed Metric Threshold Gate: Macro F1 {macro_f1:.4f} is below 0.88 minimum."
    )


def test_inference_latency_gate(model_and_data):
    """Quality Gate 2: Assert batch inference time is within 30 ms budget."""
    model, x_test, _ = model_and_data

    # Warm-up run
    _ = model.predict(x_test)

    # Measured latency across multiple batch iterations
    latencies = []
    for _ in range(10):
        t_start = time.perf_counter()
        _ = model.predict(x_test)
        t_end = time.perf_counter()
        latencies.append((t_end - t_start) * 1000.0)

    median_latency_ms = float(np.median(latencies))
    print(
        f"\n[Quality Gate] Measured Median Batch Latency: "
        f"{median_latency_ms:.2f} ms (Budget <= 30.0 ms)"
    )

    assert median_latency_ms <= 30.0, (
        f"Model failed Latency Gate: Median batch latency {median_latency_ms:.2f} ms > 30.0 ms."
    )


def test_output_schema_integrity(model_and_data):
    """Quality Gate 3: Assert predictions adhere strictly to class schema (0, 1, or 2)."""
    model, x_test, _ = model_and_data
    y_pred = model.predict(x_test)

    # 1. Output length matches input sample count
    assert len(y_pred) == len(x_test), "Output sample length does not match input sample length."

    # 2. Output values belong strictly to allowed class index set {0, 1, 2}
    allowed_classes = set(range(EXPECTED_CLASS_COUNT))
    observed_classes = set(np.unique(y_pred))
    assert observed_classes.issubset(allowed_classes), (
        f"Model output schema violation: observed classes {observed_classes} "
        f"outside allowed set {allowed_classes}."
    )

    # 3. Output probability distribution integrity
    y_prob = model.predict_proba(x_test)
    assert y_prob.shape == (len(x_test), EXPECTED_CLASS_COUNT)
    assert np.all(y_prob >= 0.0) and np.all(y_prob <= 1.0), (
        "Probability outputs out of valid [0, 1] range."
    )
    row_sums = np.sum(y_prob, axis=1)
    np.testing.assert_allclose(
        row_sums,
        np.ones(len(x_test)),
        rtol=1e-5,
        err_msg="Predicted class probabilities must sum to 1.0."
    )
