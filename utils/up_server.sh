#!/bin/bash

cleanup() {
    echo "Stopping Docker Compose services..."
    docker-compose down
    exit 0
}

trap cleanup SIGINT

if [ "$1" = "build" ]; then
    # Rebuild Docker images
    docker-compose build
fi

# Start the database service
docker-compose up -d db

# Wait for the database to be ready before starting the app
until docker-compose exec db pg_isready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

# Run database migrations using Alembic
docker-compose run --rm app sh -c "alembic upgrade head"

# Start the application service
docker-compose up -d app
docker-compose logs -f
