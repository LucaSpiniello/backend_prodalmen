from django.contrib import admin
from django.apps import apps

# Reemplaza 'nombre_de_tu_app' por el nombre real de tu aplicación
app = apps.get_app_config('exportacion')

for model_name, model in app.models.items():
    admin.site.register(model)
