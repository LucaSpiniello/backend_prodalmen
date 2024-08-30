from rest_framework_nested import routers
from django.urls import path, include
from .views import InventarioBodegaViewSet, BinEnInventarioViewSet
app_name = 'inventario'
router = routers.DefaultRouter()
router.register(r'inventarios', InventarioBodegaViewSet)
router.register(r'bin-en-inventarios', BinEnInventarioViewSet)

inventario_router = routers.NestedSimpleRouter(router, r'inventarios', lookup='inventario')
inventario_router.register(r'bins', BinEnInventarioViewSet, basename='inventario-bins')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(inventario_router.urls)),
]