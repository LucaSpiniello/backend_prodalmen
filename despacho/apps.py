from django.apps import AppConfig


class DespachoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'despacho'
    
    def ready(self):
        import despacho.signals
