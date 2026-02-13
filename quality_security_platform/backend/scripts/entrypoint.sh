#!/bin/bash
set -e
if [ ! -f /app/db.sqlite3 ]; then touch /app/db.sqlite3; fi
chmod 666 /app/db.sqlite3
python manage.py migrate --noinput
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    exec(open('scripts/init_db.py').read())
    print('✅ 初始数据已导入')
fi
python manage.py collectstatic --noinput
exec "$@"
