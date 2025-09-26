#!/usr/bin/env bash
set -e

IMAGE_NAME="posts_analytics"
CONTAINER_NAME="posts_analytics_etl"

docker build -t ${IMAGE_NAME} .

docker run -d \
  --name ${CONTAINER_NAME} \
  -e POSTGRES_PASSWORD=postgres \
  -e DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres \
  -e API_URL=https://jsonplaceholder.typicode.com/posts \
  -e WEB_PORT=8080 \
  -p 5432:5432 \
  -p 8080:8080 \
  ${IMAGE_NAME}

sleep 2
echo "Проверить логи: docker logs -f ${CONTAINER_NAME}"