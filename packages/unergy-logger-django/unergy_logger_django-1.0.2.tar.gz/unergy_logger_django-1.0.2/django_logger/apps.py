from django.apps import AppConfig


class LoggerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_logger"
    verbose_name = "Django Logger"

    def ready(self):
        """Configuración cuando la app está lista"""
        pass
