from django.contrib import admin
from .models import ReleaseVersion, VersionRegistration

@admin.register(ReleaseVersion)
class ReleaseVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'status', 'created_by', 'created_at', 'released_at')
    search_fields = ('version', 'status')
    list_filter = ('status', 'created_by')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(VersionRegistration)
class VersionRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'release_version', 'project', 'app_version', 'created_by', 'created_at', 'updated_at')
    search_fields = ('release_version__version', 'project__name', 'app_version')
    list_filter = ('release_version', 'project', 'created_by')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
