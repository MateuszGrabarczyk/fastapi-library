#!/usr/bin/env bash
set -e

echo "Waiting for Postgres at db:5432..."
until nc -z db 5432; do
  sleep 1
done
echo "Postgres is up."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn app.main:app \
  --host "${UVICORN_HOST:-0.0.0.0}" \
  --port "${UVICORN_PORT:-8000}" \
  --reload \
  --reload-dir /app/app \
  --reload-dir /app/tests
