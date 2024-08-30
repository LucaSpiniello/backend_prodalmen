from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'produccion'

router = routers.SimpleRouter()
router.register(r'produccion', ProduccionViewSet)
router.register(r'reproceso', ReprocesoViewSet)
# router.register(r'home', DashboardProgramasViewSet, basename='dashboard')

datos_produccion = routers.NestedSimpleRouter(router, r'produccion', lookup='produccion')
datos_produccion.register(r'lotes_en_programa', LotesProgramaViewSet)
datos_produccion.register(r'tarjas_resultantes', TarjaResultanteViewSet)
#datos_produccion.register(r'operarios', OperariosEnProduccionViewSet)

datos_reproceso = routers.NestedSimpleRouter(router, r'reproceso', lookup='reproceso')
datos_reproceso.register(r'bins_en_reproceso', BinsEnReprocesoViewSet)
datos_reproceso.register(r'tarjas_resultantes', TarjaResultanteReprocesoViewSet)
#datos_reproceso.register(r'operarios', OperariosEnReprocesoViewSet)



urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(datos_produccion.urls)),
    path(r'', include(datos_reproceso.urls)),
]