from django.urls import path, include
from rest_framework_nested import routers
from .views import (SeleccionViewSet, BinsPepaCalibradaViewSet, 
                    TarjaSeleccionadaViewSet, SubProductoOperarioViewSet, 
                    BinSubProductoSeleccionViewSet)

app_name = "seleccion"

router = routers.SimpleRouter()
router.register(r'seleccion', SeleccionViewSet)
router.register(r'binsubproductoseleccion',BinSubProductoSeleccionViewSet)


bins_router = routers.NestedSimpleRouter(router, r'seleccion', lookup='seleccion')
bins_router.register(r'binspepacalibrada', BinsPepaCalibradaViewSet, basename='seleccion-binspepacalibrada')
tarja_router = routers.NestedSimpleRouter(router, r'seleccion', lookup='seleccion')
tarja_router.register(r'tarjaseleccionada', TarjaSeleccionadaViewSet, basename='seleccion-tarjaseleccionada')
subproducto_router = routers.NestedSimpleRouter(router, r'seleccion', lookup='seleccion')
subproducto_router.register(r'subproductooperario', SubProductoOperarioViewSet, basename='seleccion-subproductooperario')
# bin_subproducto_router = routers.NestedSimpleRouter(router, r'seleccion', lookup='seleccion')
# bin_subproducto_router.register(r'binsubproductoseleccion', BinSubProductoSeleccionViewSet, basename='seleccion-binsubproductoseleccion')



#operarios_router = routers.NestedSimpleRouter(router, r'seleccion', lookup='seleccion')
#operarios_router.register(r'operarios', OperarioEnSeleccionViewSet, basename='seleccion-operarios')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(bins_router.urls)),
    path('', include(tarja_router.urls)),
    path('', include(subproducto_router.urls)),
    # path('', include(bin_subproducto_router.urls)),
    #path('', include(operarios_router.urls))
]
