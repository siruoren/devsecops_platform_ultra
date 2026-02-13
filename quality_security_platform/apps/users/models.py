from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    username = models.CharField('用户名', max_length=150, unique=True)
    email = models.EmailField('邮箱', unique=True)
    password = models.CharField('密码', max_length=128)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    department = models.CharField('部门', max_length=100, blank=True)
    position = models.CharField('职位', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    def __str__(self):
        return self.username
