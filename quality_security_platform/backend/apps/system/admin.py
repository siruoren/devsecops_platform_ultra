from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'title', 'is_read', 'created_at', 'read_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'content', 'recipient__username', 'sender__username')
    readonly_fields = ('created_at', 'read_at')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.sender:
            obj.sender = request.user
        super().save_model(request, obj, form, change)
