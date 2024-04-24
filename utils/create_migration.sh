if [ -z "$1" ]; then
    echo "Usage: $0 <migration_name>"
    exit 1
fi

docker-compose run migration alembic revision --autogenerate -m "$1"
