from django.apps import AppConfig


class MercadointernoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mercadointerno'
    
    def ready(self):
        import  mercadointerno.signals