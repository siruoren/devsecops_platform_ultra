from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
class Permission(models.Model):
    code = models.CharField('权限代码', max_length=100, unique=True)
    name = models.CharField('权限名称', max_length=100)
    module = models.CharField('所属模块', max_length=50)
    is_menu = models.BooleanField('是否为菜单', default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: db_table = 'rbac_permissions'
class Role(models.Model):
    name = models.CharField('角色名称', max_length=100, unique=True)
    code = models.CharField('角色标识', max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    description = models.TextField('描述', blank=True)
    class Meta: db_table = 'rbac_roles'
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'rbac_user_roles'
