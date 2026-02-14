#!/bin/bash
set -e

echo "🚀 启动质量安全平台后端服务..."

# ========== 开发环境专用：自动重置数据库 ==========
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.development" ]; then
    echo "⚠️ 开发环境：自动重置 SQLite 数据库（所有数据将丢失）"
    rm -f /app/db.sqlite3
    find /app/apps -path "*/migrations/*.py" -not -name "__init__.py" -delete
    echo "✅ 数据库重置完成"
fi

# ========== 重新生成迁移文件 ==========
echo "📦 生成数据库迁移文件..."
python manage.py makemigrations users --noinput
python manage.py makemigrations rbac --noinput
python manage.py makemigrations projects --noinput
python manage.py makemigrations versions --noinput
python manage.py makemigrations vulnerabilities --noinput
python manage.py makemigrations ci_cd --noinput
python manage.py makemigrations risk --noinput
python manage.py makemigrations system --noinput
python manage.py makemigrations auth_unified --noinput
echo "✅ 迁移文件生成完成"

# ========== 执行迁移 ==========
echo "🔄 执行数据库迁移..."
python manage.py migrate --noinput
echo "✅ 数据库迁移完成"

# ========== 初始化超级用户 ==========
echo "👤 初始化超级用户..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户 admin 创建成功')
else:
    print('ℹ️ 超级用户 admin 已存在')
EOF

# ========== 收集静态文件 ==========
echo "📁 收集静态文件..."
mkdir -p /app/static
python manage.py collectstatic --noinput
echo "✅ 静态文件收集完成"

echo "✅ 质量安全平台后端服务启动完成！"
exec "$@"