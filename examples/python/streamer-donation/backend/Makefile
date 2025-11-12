.PHONY: help install dev-install test test-cov lint format typecheck pre-commit clean run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	uv sync

dev-install: ## Install development dependencies
	uv sync --extra dev
	pre-commit install

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

lint: ## Run ruff linter
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .
	uv run ruff check --fix .

typecheck: ## Run type checking with basedpyright
	uv run basedpyright app tests

pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run: ## Run development server
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-clean: ## Remove database (will be recreated with mock data)
	rm -rf ./data/donations.db

check: format lint typecheck test ## Run all quality checks

ci: lint typecheck test-cov ## Run CI checks
