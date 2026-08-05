#!/bin/sh
set -e

echo ">>> Running Alembic migrations..."
alembic upgrade head

echo ">>> Seeding database..."
psql "$DATABASE_URL" -f "$(dirname "$0")/seed.sql" 2>/dev/null || \
  PGPASSWORD=sasis psql -h db -U sasis -d sasis -f "$(dirname "$0")/seed.sql" 2>/dev/null || \
  echo ">>> Seed skipped or already applied (non-fatal)"

echo ">>> Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
