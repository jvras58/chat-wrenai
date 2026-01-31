.PHONY: install run workers

# Instalar dependências usando uv
install:
	uv sync

# Modo pacote
package:
	uv pip install -e .

# Executar a Api
run:
	set PYTHONPATH=. && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8081

# Executar scripts
dbsample:
	set PYTHONPATH=. && uv run python scripts/dbsample.py

# Testes
test:
	set PYTHONPATH=. && Invoke-WebRequest -Uri "http://localhost:8000/chat" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body ([System.Text.Encoding]::UTF8.GetBytes((ConvertTo-Json @{message = "Qual região vendeu mais em 2025? Top 3 produtos?"}))) | Select-Object -ExpandProperty Content
