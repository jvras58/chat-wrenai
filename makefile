.PHONY: install run workers

# Instalar dependências usando uv
install:
	uv sync

# Modo pacote
package:
	uv pip install -e .

# Executar a Api
run:
	set PYTHONPATH=. && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Executar scripts
dbsample:
	set PYTHONPATH=. && uv run python scripts/dbsample.py
