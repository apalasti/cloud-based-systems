#!/bin/sh
set -e

# Create DB directory and upload dir from env
DB_PATH="${DATABASE_URL#sqlite:///}"
mkdir -p "$(dirname "$DB_PATH")" "$UPLOAD_DIR"

uv run alembic upgrade head
exec "$@"
