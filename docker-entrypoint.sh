#!/bin/sh
set -e

# Create upload dir
mkdir -p "$UPLOAD_DIR"

uv run alembic upgrade head

workers="${UVICORN_WORKERS:-4}"
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 5000 --workers "$workers"
