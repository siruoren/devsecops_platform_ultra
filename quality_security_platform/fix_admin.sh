#!/bin/bash
docker exec -it qsp_web python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_superuser': True,
        'is_staff': True
    }
)
user.set_password('admin123')
user.is_superuser = True
user.is_staff = True
user.save()
print('✅ admin 用户已修复，密码: admin123')
EOF