# Variables
PROJECT_DIR := $(shell pwd)
VENV_DIR := $(PROJECT_DIR)
PYTHON := python3
TEST_DIR := tests

# Help target
.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  venv           - Create a virtual environment"
	@echo "  test                 Run unit tests"
	@echo "  install              Install required Python packages using pip3"
	@echo "  lint                 Run code linting with flake8"
	@echo "  format               Run code formatting with Black"
	@echo "  clean                Clean up generated files"

# Create and activate the virtual environment
.PHONY: venv
venv:
	python3 -m venv $(VENV_DIR)

.PHONY: install
install: venv
	@if ! command -v poetry > /dev/null; then \
		echo "Poetry not found. Installing..."; \
		pip3 install poetry; \
	fi
	poetry install

# Run unit tests
.PHONY: test
test: venv
	pytest $(TEST_DIR)

# Run Black code formatting
.PHONY: format
format: venv
	$(PYTHON) -m black expense_tracker tests

# Run flake8 linting
.PHONY: lint
lint: venv
	$(PYTHON) -m flake8 expense_tracker tests

# Clean up
.PHONY: clean
clean:
	find . -type f -name '.*~' -delete
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +