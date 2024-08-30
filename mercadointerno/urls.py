from django.urls import path, include
from rest_framework_nested import routers
from .views import PedidoMercadoInternoViewSet

app_name = 'mercadointerno'

# Crear el router principal
router = routers.DefaultRouter()
router.register(r'pedidos_mercado_interno', PedidoMercadoInternoViewSet)

# Crear los routers anidados
pedidos_router = routers.NestedSimpleRouter(router, r'pedidos_mercado_interno', lookup='pedido_mercado_interno')
# pedidos_router.register(r'frutas', FrutaPedidoViewSet, basename='pedido-mercado-interno-frutas')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(pedidos_router.urls)),
]
