from django.apps import AppConfig


class GuiassalidaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'guiassalida'
    def ready(self):
        import guiassalida.signals
    
