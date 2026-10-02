# Wine Cultivar Classification: MLOps Pipeline with CI/CD & MLflow

![CI/CD MLOps Quality Gate](https://github.com/USER/wine-mlops-pipeline/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.14-blue)
![MLflow Tracking](https://img.shields.io/badge/MLflow-v3.16-brightgreen)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-v1.9-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

An end-to-end, reproducible Machine Learning Operations (MLOps) continuous integration pipeline for multi-class chemical cultivar classification using `sklearn.datasets.load_wine` (178 samples, 13 chemical features, 3 cultivar target classes).

---

## Repository Architecture

```
wine-mlops-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated CI pipeline with Quality Gates
├── data/
│   └── .gitkeep                 # Data directory anchor
├── src/
│   ├── __init__.py              # Package initialization
│   ├── data.py                  # Modular data ingestion, validation, and stratified splitting
│   ├── train.py                 # 5-fold CV hyperparameter search, MLflow tracking, champion registry
│   └── evaluate.py              # Inference verification and test set metric evaluation
├── tests/
│   ├── __init__.py              # Test suite initialization
│   ├── test_data.py             # Ingestion schema and data validation tests
│   └── test_model_gate.py       # Automated MLOps Quality Gate (F1, latency, output schema)
├── .gitignore                   # Excludes transient artifacts, bytecode, and MLflow cache
├── Makefile                     # Standard GNU automation targets
├── requirements.txt             # Pinned reproducible dependencies
└── README.md                    # System architecture and operational manual
```

---

## MLOps Pipeline Workflow

```
+--------------------------+
|  sklearn load_wine (178) |
+--------------------------+
             |
             v
+--------------------------+
| Data Validation & Split  | ---> Stratified 80/20 (Seed 42)
+--------------------------+      (142 train / 36 test)
             |
             v
+-----------------------------------------------------------+
| 5-Fold Stratified Cross-Validation on Dual Tree Families  |
| - RandomForestClassifier (3 distinct hyperparameter grids)|
| - GradientBoostingClassifier (3 hyperparameter grids)    |
+-----------------------------------------------------------+
             |
             v
+-----------------------------------------------------------+
| MLflow Experiment Tracking (Wine-Cultivar-Classification) |
| - Parameters, Metrics (F1, Accuracy, Log Loss), Signatures|
+-----------------------------------------------------------+
             |
             v
+-----------------------------------------------------------+
| Champion Model Selection & Model Registry Promotion       |
| - Winning Model: RandomForestClassifier (Config 2)        |
| - Registered as 'WineClassifier' with alias 'champion'    |
+-----------------------------------------------------------+
             |
             v
+-----------------------------------------------------------+
| Automated MLOps Quality Gate (GitHub Actions CI)          |
| 1. Metric Gate: Holdout Macro F1 >= 0.88 (Measured: 1.00) |
| 2. Latency Gate: Batch Inference <= 30ms (Measured: ~4ms) |
| 3. Schema Gate: Discrete class output in {0, 1, 2}        |
+-----------------------------------------------------------+
```

---

## Experimental Results: Hyperparameter Tuning

| Model Family | Config ID | Hyperparameters | Train Acc | Val Acc | Train F1 | Val Macro F1 | Val LogLoss | Status |
|---|---|---|---|---|---|---|---|---|
| **RandomForest** | `config_1` | `n_est=50, depth=3, split=2` | 0.9982 | 0.9653 | 0.9982 | 0.9665 | 0.2055 | Candidate |
| **RandomForest** | `config_2` | `n_est=100, depth=5, split=2` | 1.0000 | **0.9791** | 1.0000 | **0.9789** | **0.1630** | **CHAMPION** |
| **RandomForest** | `config_3` | `n_est=150, depth=7, split=4` | 1.0000 | 0.9791 | 1.0000 | 0.9789 | 0.1688 | Candidate |
| **GradientBoost**| `config_1` | `n_est=50, lr=0.05, depth=3` | 1.0000 | 0.9022 | 1.0000 | 0.9053 | 0.2298 | Candidate |
| **GradientBoost**| `config_2` | `n_est=100, lr=0.10, depth=3` | 1.0000 | 0.9236 | 1.0000 | 0.9259 | 0.4281 | Candidate |
| **GradientBoost**| `config_3` | `n_est=150, lr=0.10, depth=5` | 1.0000 | 0.9020 | 1.0000 | 0.9069 | 0.5759 | Candidate |

### Holdout Test Split Metrics (Champion Model):
- **Test Samples**: 36
- **Test Accuracy**: 100.0% (1.0000)
- **Test Macro F1**: 1.0000
- **Test Log Loss**: 0.1059
- **Batch Inference Latency**: ~3.85 ms

---

## GNU Makefile Commands

| Target | Description |
|---|---|
| `make install` | Upgrades `pip` and installs pinned dependencies from `requirements.txt` |
| `make lint` | Runs `flake8` over `src/` and `tests/` with maximum line length 100 |
| `make test` | Executes the complete test suite including data validation and quality gates |
| `make train` | Runs the 5-fold CV hyperparameter search, MLflow tracking, and model registration |
| `make clean` | Cleans up bytecode (`*.pyc`), `__pycache__`, test caches, and temporary tracking runs |
| `make all` | Executes `install`, `lint`, `test`, and `train` in sequence |

---

## Automated MLOps Quality Gate

The pipeline implements an automated operational quality gate executed via `pytest -v tests/`:

1. **Metric Threshold Gate**: Asserts that validation/holdout Macro F1-score is $\ge 0.88$.
2. **Inference Latency Gate**: Asserts that median batch inference latency on the test set is $\le 30.0\text{ ms}$.
3. **Output Schema Integrity Gate**: Asserts discrete class predictions $\in \{0, 1, 2\}$, output probability row-sum equals $1.0$, and prediction dimensions strictly match the input length.

---

## CI/CD Pipeline (GitHub Actions)

The workflow (`.github/workflows/ci.yml`) triggers on every `push` and `pull_request` targeting `main`:
1. Checks out repository source code via `actions/checkout@v4`.
2. Sets up Python 3.10 with dependency pip caching.
3. Executes `make install`.
4. Executes `make lint` (`flake8`).
5. Executes `make test` (`pytest` verifying unit data integrity and the MLOps quality gates).

---

## Local Development & Execution

```bash
# 1. Clone repository
git clone https://github.com/<USERNAME>/wine-mlops-pipeline.git
cd wine-mlops-pipeline

# 2. Install dependencies
make install

# 3. Code formatting & lint verification
make lint

# 4. Train models & track in MLflow
make train

# 5. Run automated Quality Gate tests
make test
```
