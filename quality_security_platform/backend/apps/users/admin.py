from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'department', 'position', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'department', 'position')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'department')
    ordering = ('-created_at',)
