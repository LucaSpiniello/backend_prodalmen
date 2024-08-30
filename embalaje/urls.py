from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'embalaje'

# Crear el router principal
router = routers.DefaultRouter()
router.register(r'tipo_embalaje', TipoEmbalajeViewSet)
router.register(r'etiqueta_embalaje', EtiquetaEmbalajeViewSet)
router.register(r'embalaje', EmbalajeViewSet)   
router.register(r'fruta_bodega', FrutaBodegaViewSet)
router.register(r'pallets_pedido', PalletProductoTerminadoParaPedidoViewSet)
# router.register(r'operarios_en_embalaje', OperariosEnEmbalajeViewSet)
# router.register(r'pallet_producto_terminado', PalletProductoTerminadoViewSet)
# router.register(r'cajas_en_pallet_producto_terminado', CajasEnPalletProductoTerminadoViewSet)

# Crear los routers anidados
embalaje_router = routers.NestedSimpleRouter(router, r'embalaje', lookup='embalaje')
embalaje_router.register(r'fruta_bodega', FrutaBodegaViewSet)
embalaje_router.register(r'pallet_producto_terminado', PalletProductoTerminadoViewSet, basename='embalaje-pallet_producto_terminado')
# embalaje_router.register(r'operarios_en_embalaje', OperariosEnEmbalajeViewSet, basename='embalaje-operarios_en_embalaje')

pallet_router = routers.NestedSimpleRouter(embalaje_router, r'pallet_producto_terminado', lookup='pallet')
pallet_router.register(r'cajas_en_pallet_producto_terminado', CajasEnPalletProductoTerminadoViewSet, basename='pallet-cajas_en_pallet_producto_terminado')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(embalaje_router.urls)),
    path('', include(pallet_router.urls)),
]
