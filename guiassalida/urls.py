# urls.py
from rest_framework_nested import routers
from django.urls import path, include
from .views import GuiaSalidaFrutaViewSet

app_name="guiassalida"

router = routers.SimpleRouter()
router.register(r'guias-salida', GuiaSalidaFrutaViewSet, basename='guia-salida')

fruta_router = routers.NestedSimpleRouter(router, r'guias-salida', lookup='guiasalida')
# fruta_router.register(r'frutas', FrutaEnGuiaSalidaViewSet, basename='guia-salida-fruta')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(fruta_router.urls)),
]
