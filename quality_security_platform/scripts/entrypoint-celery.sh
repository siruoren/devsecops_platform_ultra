#!/bin/bash
set -e

# 等待redis启动
until nc -z redis 6379; do
  echo "Waiting for Redis..."
  sleep 1
done

exec "$@"
