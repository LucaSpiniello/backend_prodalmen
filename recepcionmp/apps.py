from django.apps import AppConfig


class RecepcionmpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recepcionmp'
    def ready(self):
        import recepcionmp.signals
