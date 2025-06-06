# Inicjalizacja środowiska
poetry install

# Instalacja z dodatkami
poetry install --extras "all"

# Uruchomienie testów
poetry run pytest

# Formatowanie kodu
poetry run black src/ tests/
poetry run isort src/ tests/

# Linting
poetry run flake8 src/ tests/
poetry run mypy src/

# Budowanie dokumentacji
poetry run mkdocs serve

# Budowanie paczki
poetry build

# Publikacja (po skonfigurowaniu PyPI)
poetry publish