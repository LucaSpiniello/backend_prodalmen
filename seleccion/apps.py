from django.apps import AppConfig


class SeleccionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seleccion'
    def ready(self):
        import seleccion.signals
