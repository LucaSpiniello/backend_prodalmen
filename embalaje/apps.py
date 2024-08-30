from django.apps import AppConfig


class EmbalajeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'embalaje'
    
    def ready(self):
        import  embalaje.signals

