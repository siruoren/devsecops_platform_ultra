from django.apps import AppConfig

class CiCdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ci_cd'
    verbose_name = 'CI/CD管理'
    
    def ready(self):
        # 导入信号处理器，确保信号被注册
        import apps.ci_cd.signals
