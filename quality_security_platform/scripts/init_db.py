#!/usr/bin/env python
import os
import sys
import django

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 以下代码保持不变...
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()
from django.contrib.auth import get_user_model
from apps.rbac.models import Role, Permission
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户 admin 创建成功')
else:
    print('ℹ️ 超级用户已存在')
# 初始化默认权限
Permission.init_defaults()
# 初始化默认角色
Role.init_defaults()
print('🎉 数据库初始化完成')
