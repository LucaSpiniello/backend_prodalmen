from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'controlcalidad'

router = routers.SimpleRouter()
router.register(r'control-calidad/recepcionmp', CCRecepcionMateriaPrimaViewSet)
router.register(r'control-calidad/recepcionmp-vb', CCRecepcionMateriaPrimaVBViewSet, basename='cdcaprobado')
#router.register(r'envasesmp', EnvasesMpViewSet)
router.register(r'fotos-cc', FotosCCRecepcionMateriaPrimaViewSet)

muestras = routers.NestedSimpleRouter(router, r'control-calidad/recepcionmp', lookup='cc_recepcionmp')
muestras.register(r'muestras', CCRendimientoViewSet)
cdcpepa_muestra = routers.NestedSimpleRouter(muestras, r'muestras', lookup='cc_rendimiento')
cdcpepa_muestra.register(r'cdcpepa', CCPepaViewSet)

router.register(r'produccion/cdc-tarjaresultante', CCTarjaResultanteViewSet)
router.register(r'reproceso/cdc-tarjaresultante', CCTarjaResultanteReprocesoViewSet)
router.register(r'seleccion/cdc-tarjaseleccionada', CCTarjaSeleccionadaViewSet)
router.register(r'planta-harina/cdc-bin-resultante', CCBinResultanteViewSet)
router.register(r'proceso-planta-harina/cdc-bin-resultante', CCBinResultanteProcesoViewSet)





urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(muestras.urls)),
    path(r'', include(cdcpepa_muestra.urls)),
]