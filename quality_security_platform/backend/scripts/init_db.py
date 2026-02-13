import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()
from django.contrib.auth import get_user_model
from apps.rbac.models import Permission, Role, UserRole
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户 admin 创建成功')
# 初始化权限、角色等（完整代码略）
