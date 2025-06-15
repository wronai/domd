# DoMD Project Makefile
# Development, build, and Docker automation

.PHONY: help install dev-install test lint format clean build publish docs serve-docs \
	docker-build docker-run docker-shell docker-test docker-push docker-clean \
	docker-compose-up docker-compose-down docker-logs docker-restart \
	docker-setup docker-prune docker-ls docker-cp

# Docker image name and tag
IMAGE_NAME ?= domd
IMAGE_TAG ?= latest
DOCKER_COMPOSE_FILE ?= docker-compose.yml
DOCKER_RUN_OPTS ?= --rm -it
DOCKER_WORKDIR ?= /app
DOCKER_USER ?= $(shell id -u):$(shell id -g)

# Docker Compose project name
COMPOSE_PROJECT_NAME ?= domd

# Docker network (for container communication)
DOCKER_NETWORK ?= domd-network

# Frontend settings
FRONTEND_DIR = frontend
NODE_ENV ?= development
NPM = npm --prefix $(FRONTEND_DIR)
NPM_RUN = $(NPM) run
NPM_CI = $(NPM) ci
NPM_INSTALL = $(NPM) install
NPM_BUILD = $(NPM_RUN) build
NPM_START = $(NPM_RUN) start
NPM_TEST = $(NPM_RUN) test
NPM_LINT = $(NPM_RUN) lint
NPM_FORMAT = $(NPM_RUN) format
NPM_ANALYZE = $(NPM_RUN) analyze
NPM_AUDIT = $(NPM) audit
NPM_OUTDATED = $(NPM) outdated
NPM_UPDATE = $(NPM) update
NPM_DEDUPE = $(NPM) dedupe

# Backend settings
PYTHON = python
PIP = pip
POETRY = poetry
PYTEST = $(POETRY) run pytest
UVICORN = $(POETRY) run uvicorn
PORT ?= 8000

# Default target
help: ## Show this help message
	@echo "DoMD - Project Command Detector"
	@echo "================================="
	@echo "Available commands:"
	@echo "\nInstallation:"
	@awk 'BEGIN {FS = \":.*?## \"} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /install/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nDevelopment:"
	@awk 'BEGIN {FS = \":.*?## \"} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /(test|lint|format|mypy|run)/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nFrontend:"
	@awk 'BEGIN {FS = \":.*?## \"} /^frontend-[-a-z]+:.*?## .*$$/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nDocker:"
	@awk 'BEGIN {FS = \":.*?## \"} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /docker/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nDocumentation:"
	@awk 'BEGIN {FS = \":.*?## \"} /^[a-zA-Z_-]+:.*?## .*$$/ && $$0 ~ /(docs|serve)/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nBuild & Publish:"
	@awk 'BEGIN {FS = \":.*?## \"} /^[a-zA-Z_-]+:.*?## .*$$/ && ($$0 ~ /(build|publish|clean)/) && !($$0 ~ /(docker|frontend)/) {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
# Development Commands
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python dependencies
	@echo "Installing Python dependencies..."
	$(POETRY) install

install-frontend: ## Install Node.js dependencies
	@echo "Installing frontend dependencies..."
	$(NPM_CI)


update-deps: update-backend-deps update-frontend-deps ## Update all dependencies

update-backend-deps: ## Update Python dependencies
	@echo "Updating Python dependencies..."
	$(POETRY) update

update-frontend-deps: ## Update frontend dependencies
	@echo "Updating frontend dependencies..."
	$(NPM_UPDATE)
	$(NPM_DEDUPE)

# Backend targets
run-backend: ## Start the backend development server
	@echo "Starting backend development server..."
	$(UVICORN) domd.main:app --reload --port $(PORT)

run-backend-prod: ## Start the backend production server
	@echo "Starting backend production server..."
	$(UVICORN) domd.main:app --host 0.0.0.0 --port $(PORT)

run-backend-worker: ## Start the background worker
	@echo "Starting background worker..."
	$(POETRY) run python -m domd.worker

test-backend: ## Run backend tests
	@echo "Running backend tests..."
	$(PYTEST)

lint-backend: ## Lint backend code
	@echo "Linting backend code..."
	$(POETRY) run black --check .
	$(POETRY) run isort --check-only .
	$(POETRY) run flake8 .

format-backend: ## Format backend code
	@echo "Formatting backend code..."
	$(POETRY) run black .
	$(POETRY) run isort .


# Frontend targets
frontend-install: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	$(NPM_CI)

frontend-update: ## Update frontend dependencies
	@echo "Updating frontend dependencies..."
	$(NPM_UPDATE)
	$(NPM_DEDUPE)

frontend-start: ## Start frontend development server
	@echo "Starting frontend development server..."
	NODE_ENV=$(NODE_ENV) $(NPM_START)

frontend-build: ## Build frontend for production
	@echo "Building frontend for production..."
	NODE_ENV=production $(NPM_BUILD)

frontend-test: ## Run frontend tests
	@echo "Running frontend tests..."
	$(NPM_TEST)

frontend-lint: ## Lint frontend code
	@echo "Linting frontend code..."
	$(NPM_LINT)

frontend-format: ## Format frontend code
	@echo "Formatting frontend code..."
	$(NPM_FORMAT)

frontend-audit: ## Check for vulnerable frontend dependencies
	@echo "Auditing frontend dependencies..."
	$(NPM_AUDIT)

frontend-outdated: ## Check for outdated frontend dependencies
	@echo "Checking for outdated frontend dependencies..."
	$(NPM_OUTDATED)

frontend-clean: ## Clean frontend build artifacts
	@echo "Cleaning frontend build artifacts..."
	rm -rf $(FRONTEND_DIR)/build

# Combined development commands
dev: ## Start both frontend and backend in development mode
	@echo "Starting development environment..."
	@echo "Backend: http://localhost:$(PORT)"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop all processes"
	@echo ""
	@echo "Starting backend and frontend..."
	@$(MAKE) -j 2 run-backend frontend-start

# Database commands
db-shell: ## Open a database shell
	@echo "Opening database shell..."
	$(POETRY) run python -m domd.db shell

db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	$(POETRY) run alembic upgrade head

db-reset: ## Reset the database (WARNING: This will delete all data!)
	@echo "Resetting database..."
	@read -p "Are you sure you want to reset the database? This will delete all data! [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Dropping and recreating database..."; \
		$(POETRY) run python -m domd.db reset; \
		echo "Running migrations..."; \
		$(MAKE) db-migrate; \
		echo "Database reset complete."; \
	else \
		echo "Database reset cancelled."; \
	fi
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -f $(FRONTEND_DIR)/package-lock.json

# Installation targets
install: frontend-install ## Install the package and frontend dependencies
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
docker-build: ## Build Docker image with current user permissions
	@echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker build \
		--build-arg USER_ID=$(shell id -u) \
		--build-arg GROUP_ID=$(shell id -g) \
		-t ${IMAGE_NAME}:${IMAGE_TAG} .

docker-run: ## Run Docker container with current directory mounted
	@echo "Running Docker container from ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker run ${DOCKER_RUN_OPTS} \
		-v $(CURDIR):${DOCKER_WORKDIR} \
		-w ${DOCKER_WORKDIR} \
		${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_RUN_CMD}

docker-shell: ## Start an interactive shell in the container
	@echo "Starting shell in ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker run ${DOCKER_RUN_OPTS} \
		-v $(CURDIR):${DOCKER_WORKDIR} \
		-w ${DOCKER_WORKDIR} \
		--entrypoint /bin/bash \
		${IMAGE_NAME}:${IMAGE_TAG}

docker-setup: ## Set up development environment in container
	@echo "Setting up development environment in ${IMAGE_NAME}:${IMAGE_TAG}..."
	docker run ${DOCKER_RUN_OPTS} \
		-v $(CURDIR):${DOCKER_WORKDIR} \
		-w ${DOCKER_WORKDIR} \
		${IMAGE_NAME}:${IMAGE_TAG} \
		poetry install --with dev,test,lint,docs

docker-prune: ## Clean up unused Docker resources
	@echo "Pruning Docker resources..."
	docker system prune -f

docker-ls: ## List all containers and images
	@echo "=== Running Containers ==="
	docker ps -a
	@echo "\n=== Available Images ==="
	docker images

docker-cp: ## Copy files between host and container
	@echo "Usage: make DOCKER_CONTAINER=container_id SRC=/path/to/src DEST=/path/to/dest docker-cp"

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
clean: frontend-clean ## Remove build artifacts and temporary files
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	find . -path './.venv' -prune -o -type f -name '*.py[co]' -delete 2>/dev/null || true
	find . -path './.venv' -prune -o -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."

frontend-clean: ## Clean frontend build artifacts
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/

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
