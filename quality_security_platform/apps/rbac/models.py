from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Permission(models.Model):
    """功能权限 - 对应菜单/按钮"""
    code = models.CharField('权限代码', max_length=100, unique=True)
    name = models.CharField('权限名称', max_length=100)
    module = models.CharField('所属模块', max_length=50)
    is_menu = models.BooleanField('是否为菜单', default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父权限')
    class Meta:
        db_table = 'rbac_permissions'
        verbose_name = '权限'
    def __str__(self):
        return f"{self.module}-{self.name}"
    @classmethod
    def init_defaults(cls):
        default_perms = [
            ('user_view', '查看用户', 'user', False),
            ('user_add', '新建用户', 'user', False),
            ('user_edit', '编辑用户', 'user', False),
            ('user_delete', '删除用户', 'user', False),
            ('user_menu', '用户管理', 'user', True),
            ('project_view', '查看项目', 'project', False),
            ('project_add', '新建项目', 'project', False),
            ('project_edit', '编辑项目', 'project', False),
            ('project_delete', '删除项目', 'project', False),
            ('project_menu', '项目管理', 'project', True),
            ('version_view', '查看版本', 'version', False),
            ('version_edit', '编辑版本', 'version', False),
            ('version_menu', '版本管理', 'version', True),
            ('vuln_view', '查看漏洞', 'vuln', False),
            ('vuln_import', '导入漏洞', 'vuln', False),
            ('vuln_menu', '安全漏洞', 'vuln', True),
            ('system_config', '系统配置', 'system', True),
            ('cicd_view', '查看流水线', 'cicd', False),
            ('cicd_trigger', '触发构建', 'cicd', False),
            ('cicd_menu', 'CI/CD', 'cicd', True),
            ('risk_view', '风险看板', 'risk', True),
        ]
        for code, name, module, is_menu in default_perms:
            cls.objects.get_or_create(code=code, defaults={'name': name, 'module': module, 'is_menu': is_menu})

class Role(models.Model):
    """角色"""
    name = models.CharField('角色名称', max_length=100, unique=True)
    code = models.CharField('角色标识', max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='权限')
    description = models.TextField('描述', blank=True)
    class Meta:
        db_table = 'rbac_roles'
        verbose_name = '角色'
    def __str__(self):
        return self.name
    @classmethod
    def init_defaults(cls):
        admin_role, _ = cls.objects.get_or_create(code='admin', defaults={'name': '系统管理员'})
        admin_role.permissions.set(Permission.objects.all())
        dev_role, _ = cls.objects.get_or_create(code='developer', defaults={'name': '开发人员'})
        dev_role.permissions.set(Permission.objects.filter(code__in=[
            'project_view', 'version_view', 'vuln_view', 'cicd_view', 'risk_view'
        ]))
        qa_role, _ = cls.objects.get_or_create(code='qa', defaults={'name': '测试人员'})
        qa_role.permissions.set(Permission.objects.filter(code__in=[
            'project_view', 'version_view', 'vuln_view', 'vuln_import', 'risk_view'
        ]))

class UserRole(models.Model):
    """用户角色分配"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'rbac_user_roles'
        unique_together = ('user', 'role')
