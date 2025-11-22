#!/bin/bash
set -e

echo "🔄 Starting backend service..."

# Wait for database to be ready (additional safety beyond docker healthcheck)
echo "⏳ Waiting for database connection..."
uv run python -c "
import time
from app.core.database import engine
from sqlalchemy import text

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✅ Database connection established')
        break
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            print(f'❌ Failed to connect to database after {max_retries} attempts')
            raise
        print(f'⏳ Waiting for database... ({retry_count}/{max_retries})')
        time.sleep(1)
"

# Run database migrations (create tables)
echo "📊 Creating database tables..."
uv run python -c "
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('✅ Database tables ready')
"

# Seed the database with default templates
echo "🌱 Seeding database with default templates..."
uv run python seed_db.py

# Start the application
echo "🚀 Starting FastAPI server..."
echo "📡 API will be available at http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo ""

exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
