# DoMD Project Makefile
# Development, build, and Docker automation

.PHONY: help install dev-install test lint format clean build publish docs serve-docs \
	docker-build docker-run docker-shell docker-test docker-push docker-clean \
	docker-compose-up docker-compose-down docker-logs docker-restart

# Docker image name and tag
IMAGE_NAME ?= domd
IMAGE_TAG ?= latest
DOCKER_COMPOSE_FILE ?= docker-compose.yml

# Docker runtime flags (can be overridden)
DOCKER_RUN_FLAGS ?= --rm -it
DOCKER_RUN_CMD ?= bash

# Docker Compose project name
COMPOSE_PROJECT_NAME ?= domd

# Docker network (for container communication)
DOCKER_NETWORK ?= domd-network

# Default target
help: ## Show this help message
	@echo "DoMD - Project Command Detector"
	@echo "================================="
	@echo "Available commands:"
	@echo "\nInstallation:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /install/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nDevelopment:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /(test|lint|format|mypy|run)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nDocker:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /docker/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nDocumentation:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /(docs|serve)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nBuild & Publish:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*$$/ && ($$0 ~ /(build|publish|clean)/) && !($$0 ~ /docker/) {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install the package
	poetry install

dev-install: ## Install with development dependencies
	poetry install --with dev,docs,testing,lint
	poetry run pre-commit install

install-all: ## Install with all optional dependencies
	poetry install --with dev,docs,testing,lint --extras "all"

install-api: ## Install with REST API dependencies
	poetry install --extras "api"

# Testing targets
test: ## Run all tests
	@echo "Running all tests..."
	poetry run pytest

# Unit and integration tests
test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	poetry run pytest -m "unit"

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	poetry run pytest -m "integration"

test-api: ## Run API tests only
	@echo "Running API tests..."
	poetry run pytest tests/test_api_*.py -v

# Ansible test targets
test-ansible: ## Run all Ansible-related tests
	@echo "Running all Ansible tests..."
	poetry run pytest tests/test_ansible_*.py -v

ansible-lint: ## Run ansible-lint on playbooks and roles
	@echo "Running ansible-lint..."
	if ! command -v ansible-lint >/dev/null; then \
		echo "Installing ansible-lint..."; \
		pip install --user ansible-lint; \
	fi
	ansible-lint -x role-name ansible/

ansible-check: ## Check Ansible playbook syntax
	@echo "Checking Ansible playbook syntax..."
	ansible-playbook ansible/site.yml --syntax-check -i ansible/inventory/production

ansible-dry-run: ## Run Ansible playbook in check mode (dry run)
	@echo "Running Ansible in check mode..."
	ansible-playbook ansible/site.yml --check --diff -i ansible/inventory/production

ansible-install: ## Install Ansible Galaxy requirements
	@echo "Installing Ansible Galaxy requirements..."
	ansible-galaxy install -r ansible/requirements.yml

test-ansible-unit: ## Run Ansible unit tests only
	@echo "Running Ansible unit tests..."
	poetry run pytest tests/test_ansible_*.py -m "unit" -v

test-ansible-integration: ## Run Ansible integration tests
	@echo "Running Ansible integration tests..."
	ANSIBLE_CONFIG=ansible/ansible.cfg poetry run pytest tests/test_ansible_*.py -m "integration" -v

# Specific Ansible component tests
test-playbooks: ## Test Ansible playbook functionality
	@echo "Testing Ansible playbooks..."
	ANSIBLE_CONFIG=ansible/ansible.cfg poetry run pytest tests/test_ansible_playbook.py -v

test-roles: ## Test Ansible role functionality
	@echo "Testing Ansible roles..."
	ANSIBLE_CONFIG=ansible/ansible.cfg poetry run pytest tests/test_ansible_roles.py -v

test-galaxy: ## Test Ansible Galaxy integration
	@echo "Testing Ansible Galaxy..."
	ANSIBLE_CONFIG=ansible/ansible.cfg poetry run pytest tests/test_ansible_galaxy.py -v

test-vault: ## Test Ansible Vault operations
	@echo "Testing Ansible Vault..."
	ANSIBLE_CONFIG=ansible/ansible.cfg poetry run pytest tests/test_ansible_vault.py -v

test-inventory: ## Test Ansible inventory handling
	@echo "Testing Ansible inventory..."
	ANSIBLE_CONFIG=ansible/ansible.cfg poetry run pytest tests/test_ansible_inventory.py -v

# Test coverage
coverage: ## Generate test coverage report
	@echo "Generating test coverage report..."
	poetry run pytest --cov=domd --cov-report=term-missing --cov-report=html

# Linting and code quality
lint: ## Run all linting and code quality checks
	@echo "Running linting and code quality checks..."
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/
	poetry run flake8 src/ tests/
	poetry run mypy src/

format: ## Format code with black and isort
	@echo "Formatting code..."
	poetry run black src/ tests/
	poetry run isort src/ tests/

format-check: ## Check if code is properly formatted
	@echo "Checking code formatting..."
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	poetry run pytest --cov=domd --cov-report=html --cov-report=term

test-verbose: ## Run tests with verbose output
	@echo "Running tests with verbose output..."
	poetry run pytest -v

mypy: ## Run type checking
	@echo "Running type checking with mypy..."
	poetry run mypy src/

flake8: ## Run flake8 linter
	@echo "Running flake8 linting..."
	poetry run flake8 src/ tests/
pylint: ## Run pylint
	@echo "Running pylint..."
	poetry run pylint src/domd/

# Documentation targets
docs: ## Build documentation
	poetry run mkdocs build

serve-docs: ## Serve documentation locally
	poetry run mkdocs serve

# API targets
run-api: ## Run the REST API server
	poetry run domd-api

run-api-debug: ## Run the REST API server in debug mode
	poetry run domd-api --debug

run-api-port: ## Run the REST API server on a specific port
	@read -p "Enter port number (default: 5000): " port; \
	poetry run domd-api --port $${port:-5000}

docs-clean: ## Clean documentation build
	rm -rf site/

# Docker targets
docker-build: ## Build Docker image
	@echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

docker-run: ## Run Docker container
	@echo "Running Docker container from ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker run ${DOCKER_RUN_FLAGS} ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_RUN_CMD}

docker-shell: ## Start a shell in the Docker container
	@echo "Starting shell in ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker run ${DOCKER_RUN_FLAGS} --entrypoint /bin/bash ${IMAGE_NAME}:${IMAGE_TAG}

docker-test: ## Run tests inside Docker container
	@echo "Running tests in Docker container..."
	docker run ${DOCKER_RUN_FLAGS} ${IMAGE_NAME}:${IMAGE_TAG} make test

docker-push: ## Push Docker image to registry
	@echo "Pushing ${IMAGE_NAME}:${IMAGE_TAG} to registry..."
	docker push ${IMAGE_NAME}:${IMAGE_TAG}

docker-clean: ## Remove Docker containers and images
	@echo "Removing containers..."
	docker ps -aq --filter "name=domd" | xargs -r docker rm -f 2>/dev/null || true
	@echo "Removing images..."
	docker images -q ${IMAGE_NAME} | xargs -r docker rmi -f 2>/dev/null || true

docker-logs: ## View container logs
	docker-compose -f ${DOCKER_COMPOSE_FILE} logs -f

docker-restart: ## Restart containers
	docker-compose -f ${DOCKER_COMPOSE_FILE} restart

docker-compose-up: ## Start containers using docker-compose
	docker-compose -f ${DOCKER_COMPOSE_FILE} up -d

docker-compose-down: ## Stop and remove containers
	docker-compose -f ${DOCKER_COMPOSE_FILE} down

# Build and publish targets
clean: ## Clean build artifacts and Docker resources
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info/ || true
	@echo "Cleaning Python cache files..."
	find . -path './.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -path './.venv' -prune -o -type f -name '*.py[co]' -delete 2>/dev/null || true
	find . -path './.venv' -prune -o -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."

# Combined targets
dev: dev-install pre-commit ## Set up development environment
	@echo "Development environment ready!"

pre-commit: ## Install pre-commit hooks
	poetry run pre-commit install

# Utility targets
version: ## Show current version
	@poetry version

update: ## Update dependencies
	poetry update

upgrade: update ## Alias for update

# Helper targets
.PHONY: check-docker check-docker-compose

check-docker:
	@command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is required but not installed. Aborting."; exit 1; }

check-docker-compose:
	@command -v docker-compose >/dev/null 2>&1 || { echo >&2 "Docker Compose is required but not installed. Aborting."; exit 1; }

build: clean ## Build the package
	poetry version patch
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
