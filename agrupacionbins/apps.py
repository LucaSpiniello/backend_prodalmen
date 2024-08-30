from django.apps import AppConfig


class AgrupacionbinsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agrupacionbins'
    def ready(self):
        import agrupacionbins.signals
