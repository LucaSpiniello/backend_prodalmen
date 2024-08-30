from django.apps import AppConfig


class PlantaHarinaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planta_harina'

    def ready(self):
        import planta_harina.signals