# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    VENV_PATH="/opt/venv"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Create a virtual environment
RUN python -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy only necessary files for installation
COPY pyproject.toml poetry.lock README.md ./
COPY src/domd/ ./src/domd/

# Install the package in development mode with all extras
RUN poetry config virtualenvs.create false \
    && poetry install --with dev,docs,testing,lint,all --no-interaction --no-ansi --no-root \
    && poetry install --no-interaction --no-ansi

# Verify installation
RUN python -c "import domd; print(f'Successfully installed domd version: {domd.__version__}'); print(f'Python path: {domd.__file__}')"

# Run tests
RUN poetry run pytest -v tests/
