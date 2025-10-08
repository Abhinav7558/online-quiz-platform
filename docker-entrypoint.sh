#!/bin/sh
set -e
echo "Running database migrations (alembic upgrade head)..."
# Run migrations if alembic is available
if command -v alembic >/dev/null 2>&1; then
  alembic upgrade head
else
  echo "alembic not found in PATH, skipping migrations"
fi

echo "Starting process: $@"
exec "$@"
