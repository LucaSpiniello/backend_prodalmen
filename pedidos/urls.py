from django.urls import path, include
from rest_framework_nested import routers
from .views import FrutaFicticaViewSet, PedidoViewSet, FrutaEnPedidoViewSet

app_name = 'pedidos'
# Crear el router principal
router = routers.DefaultRouter()
router.register(r'fruta-ficticia', FrutaFicticaViewSet)
router.register(r'pedidos', PedidoViewSet, basename='pedidos_unidos')


# Crear los routers anidados
pedidos_router = routers.NestedSimpleRouter(router, r'pedidos', lookup='pedido')
pedidos_router.register(r'frutas', FrutaEnPedidoViewSet, basename='pedido-frutas')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(pedidos_router.urls)),
]
