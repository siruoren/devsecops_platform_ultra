#!/bin/bash
set -e

# ========== 开发环境专用：自动重置数据库 ==========
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.development" ]; then
    echo "⚠️ 开发环境：自动重置 SQLite 数据库（所有数据将丢失）"
    rm -f /app/db.sqlite3
    find /app/apps -path "*/migrations/*.py" -not -name "__init__.py" -delete
fi


# ========== 重新生成迁移文件 ==========
python manage.py makemigrations users  --noinput
python manage.py makemigrations rbac --noinput
python manage.py makemigrations projects --noinput
python manage.py makemigrations versions --noinput
python manage.py makemigrations vulnerabilities --noinput
python manage.py makemigrations ci_cd --noinput
python manage.py makemigrations risk --noinput
python manage.py makemigrations system --noinput
python manage.py makemigrations auth_unified   --noinput


# ========== 执行迁移 ==========
python manage.py migrate --noinput

# ========== 初始化超级用户 ==========
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户 admin 创建成功')
EOF

# ========== 收集静态文件 ==========
    # 确保静态文件目录存在
mkdir -p /app/static
python manage.py collectstatic --noinput

exec "$@"