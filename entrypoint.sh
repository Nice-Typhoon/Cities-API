#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."

# повторы пока не будет полностью запущен контейнер с postgis
MAX_TRIES=30
TRIES=0
until python - <<'PYEOF'
import asyncio, asyncpg, os, sys

async def check():
    try:
        conn = await asyncpg.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ.get("DB_PORT", 5432)),
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
        await conn.close()
    except Exception as e:
        print(f"DB not ready: {e}", file=sys.stderr)
        sys.exit(1)

asyncio.run(check())
PYEOF
do
  TRIES=$((TRIES + 1))
  if [ "$TRIES" -ge "$MAX_TRIES" ]; then
    echo "Database never became reachable. Aborting."
    exit 1
  fi
  echo "Attempt $TRIES/$MAX_TRIES — retrying in 2s..."
  sleep 2
done

echo "Database is reachable. Running migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
