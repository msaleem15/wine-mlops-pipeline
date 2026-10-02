PYTHON ?= python3

.PHONY: help install lint test train clean all

help:
	@echo "Available targets:"
	@echo "  install  : Upgrade pip and install pinned dependencies from requirements.txt"
	@echo "  lint     : Run flake8 across src/ and tests/ with max line length 100"
	@echo "  test     : Run all unit tests via pytest with verbose output"
	@echo "  train    : Execute the MLflow training and hyperparameter search script"
	@echo "  clean    : Remove compiled bytecode (*.pyc), test caches, and temporary files"
	@echo "  all      : Run install, lint, test, and train"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m flake8 src/ tests/ --max-line-length=100

test:
	$(PYTHON) -m pytest -v tests/

train:
	$(PYTHON) -m src.train

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf mlruns mlflow.db mlartifacts

all: install lint test train
