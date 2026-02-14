#!/bin/bash
set -e

echo "🚀 启动 Celery 服务..."

echo "⏳ 等待 Redis 服务就绪..."
until nc -z redis 6379; do 
    echo "🔄 等待 Redis..."
    sleep 2
done

echo "✅ Redis 服务已就绪"
echo "✅ Celery 服务启动完成！"

exec "$@"
