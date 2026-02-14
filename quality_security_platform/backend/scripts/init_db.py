#!/usr/bin/env python3
"""初始化数据库脚本"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置 Django 配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.rbac.models import Permission, Role, UserRole

User = get_user_model()

def init_superuser():
    """初始化超级用户"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ 超级用户 admin 创建成功')
    else:
        print('ℹ️ 超级用户 admin 已存在')

def init_rbac():
    """初始化 RBAC 权限系统"""
    # 创建默认角色
    admin_role, created = Role.objects.get_or_create(name='超级管理员', code='admin')
    if created:
        print('✅ 角色 超级管理员 创建成功')
    else:
        print('ℹ️ 角色 超级管理员 已存在')
    
    # 为超级用户分配角色
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        user_role, created = UserRole.objects.get_or_create(user=admin_user, role=admin_role)
        if created:
            print('✅ 超级用户权限分配成功')
        else:
            print('ℹ️ 超级用户权限已分配')

if __name__ == '__main__':
    print('🚀 初始化数据库...')
    init_superuser()
    init_rbac()
    print('✅ 数据库初始化完成！')
