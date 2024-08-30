from django.apps import AppConfig


class ControlcalidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controlcalidad'
    
    def ready(self):
        import  controlcalidad.signals
