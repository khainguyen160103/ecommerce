#!/bin/sh
set -e

# Giá trị mặc định, bạn có thể override bằng env trong docker-compose
: "${DB_HOST:=mysql}"
: "${DB_PORT:=3306}"

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
# Chờ MySQL sẵn sàng
while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
  sleep 1
done
echo "MySQL is up."

# Chạy migrate
alembic upgrade head

# Seed admin (dùng -m cho chắc chắn import được package app)
python -m app.core.seed_admin

# Chạy server
uvicorn main:app --host 0.0.0.0 --port 8000