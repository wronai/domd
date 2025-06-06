# DoMD Project Makefile
# Development and build automation

.PHONY: help install dev-install test lint format clean build publish docs serve-docs

# Default target
help: ## Show this help message
	@echo "DoMD - Project Command Detector"
	@echo "================================="
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install the package
	poetry install

dev-install: ## Install with development dependencies
	poetry install --with dev,docs,testing,lint
	poetry run pre-commit install

install-all: ## Install with all optional dependencies
	poetry install --with dev,docs,testing,lint --extras "all"

# Testing targets
test: ## Run all tests
	poetry run pytest

test-unit: ## Run unit tests only
	poetry run pytest -m "unit"

test-integration: ## Run integration tests only
	poetry run pytest -m "integration"

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=domd --cov-report=html --cov-report=term

test-verbose: ## Run tests with verbose output
	poetry run pytest -v

# Code quality targets
lint: ## Run all linting tools
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/
	poetry run flake8 src/ tests/
	poetry run mypy src/

format: ## Format code with black and isort
	poetry run black src/ tests/
	poetry run isort src/ tests/

format-check: ## Check if code is properly formatted
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

mypy: ## Run type checking
	poetry run mypy src/

flake8: ## Run flake8 linter
	poetry run flake8 src/ tests/

pylint: ## Run pylint
	poetry run pylint src/domd/

# Documentation targets
docs: ## Build documentation
	poetry run mkdocs build

serve-docs: ## Serve documentation locally
	poetry run mkdocs serve

docs-clean: ## Clean documentation build
	rm -rf site/

# Build and publish targets
clean: ## Clean build artifacts
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean ## Build the package
	poetry build

publish-test: build ## Publish to test PyPI
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

publish: build ## Publish to PyPI
	poetry publish

# Development targets
run: ## Run domd on current directory
	poetry run domd

run-dry: ## Run domd in dry-run mode
	poetry run domd --dry-run --verbose

run-example: ## Run domd on example project
	poetry run domd --path examples/ --verbose

# Quality assurance targets
qa: lint test ## Run quality assurance (lint + test)

ci: ## Run CI pipeline locally
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test-cov
	$(MAKE) build

pre-commit: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

# Utility targets
version: ## Show current version
	@poetry version

bump-patch: ## Bump patch version
	poetry version patch

bump-minor: ## Bump minor version
	poetry version minor

bump-major: ## Bump major version
	poetry version major

security: ## Run security checks
	poetry run bandit -r src/
	poetry run safety check

deps-update: ## Update dependencies
	poetry update

deps-show: ## Show dependency tree
	poetry show --tree

# Environment targets
env-info: ## Show environment information
	@echo "Python version:"
	@python --version
	@echo "Poetry version:"
	@poetry --version
	@echo "Project info:"
	@poetry show --no-dev

# Health check (dogfooding)
health-check: ## Run domd on itself
	poetry run domd --path . --verbose

health-check-dry: ## Preview domd run on itself
	poetry run domd --path . --dry-run --verbose

# Example and demo targets
create-examples: ## Create example projects for testing
	mkdir -p examples/javascript examples/python examples/docker
	echo '{"name": "test", "scripts": {"test": "echo test", "build": "echo build"}}' > examples/javascript/package.json
	echo 'test:\n\techo "Testing"' > examples/Makefile
	echo 'FROM python:3.9\nRUN echo "Docker test"' > examples/docker/Dockerfile

demo: create-examples ## Run demo on example projects
	@echo "Running DoMD demo..."
	poetry run domd --path examples/ --verbose

# Cleanup targets
clean-all: clean docs-clean ## Clean everything
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf examples/

# Git targets
git-clean: ## Clean git repository
	git clean -fdx

tag: ## Create git tag with current version
	git tag v$(shell poetry version -s)
	git push origin v$(shell poetry version -s)

# Database/cache cleanup
clean-cache: ## Clean Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Development workflow shortcuts
dev: dev-install format lint test ## Full development setup and check

quick-test: ## Quick test run (unit tests only)
	poetry run pytest tests/ -x -v --tb=short

watch-test: ## Watch files and run tests on changes
	poetry run pytest-watch

# Release workflow
release-check: ## Check if ready for release
	@echo "Checking release readiness..."
	$(MAKE) clean
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build
	@echo "✅ Ready for release!"

release-patch: ## Release patch version
	$(MAKE) release-check
	$(MAKE) bump-patch
	$(MAKE) tag
	$(MAKE) publish

release-minor: ## Release minor version
	$(MAKE) release-check
	$(MAKE) bump-minor
	$(MAKE) tag
	$(MAKE) publish

release-major: ## Release major version
	$(MAKE) release-check
	$(MAKE) bump-major
	$(MAKE) tag
	$(MAKE) publish
