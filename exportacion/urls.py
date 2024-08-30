from django.urls import path, include
from rest_framework_nested import routers
from .views import PedidoExportacionViewSet

app_name = 'exportacion'

# Crear el router principal
router = routers.DefaultRouter()
router.register(r'pedidos_exportacion', PedidoExportacionViewSet)

# Crear los routers anidados
pedidos_router = routers.NestedSimpleRouter(router, r'pedidos_exportacion', lookup='pedido_exportacion')
# pedidos_router.register(r'frutas', FrutaPedidoViewSet, basename='pedido-exportacion-frutas')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(pedidos_router.urls)),
]