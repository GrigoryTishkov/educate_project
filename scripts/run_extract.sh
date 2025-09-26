#!/usr/bin/env bash
set -e


if [ -f /etc/container_env ]; then
source /etc/container_env
fi


if [ -z "${DATABASE_URL}" ]; then
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
fi


python3 /usr/local/bin/scripts/extract.py