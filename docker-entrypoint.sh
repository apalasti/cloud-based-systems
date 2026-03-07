#!/bin/sh
set -e

# Create upload dir
mkdir -p "$UPLOAD_DIR"

uv run alembic upgrade head
exec "$@"
