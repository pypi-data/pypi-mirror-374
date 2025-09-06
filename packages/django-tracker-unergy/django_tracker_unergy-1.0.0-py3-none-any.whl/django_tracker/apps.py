from django.apps import AppConfig


class LoggerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_tracker"
    verbose_name = "Django Tracker"

    def ready(self):
        """Configuración cuando la app está lista"""
        import logging

        logger = logging.getLogger("auditlog")
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
