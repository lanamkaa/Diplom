#!/bin/sh

# Wait for PostgreSQL to be ready
until psql $DATABASE_URL -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Run migrations and start the application
python -m bot migrate
python -m bot