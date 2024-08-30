from rest_framework_nested import routers
from .views import *

app_name = 'planta_harina'


router = routers.SimpleRouter()
router.register(r'programas', ProgramaPHViewSet)
router.register(r'bines-para-programa', BinParaProgramaViewSet)
router.register(r'bines-resultantes-programa', BinResultanteProgramaViewSet)
#router.register(r'operarios-programa', OperariosEnProgramaPHViewSet)
router.register(r'rechazos-programa', RechazoProgramaViewSet)
router.register(r'variables-programa', VariablesProgramaPHViewSet)

router.register(r'procesos', ProcesoPHViewSet)
bins_router = routers.NestedSimpleRouter(router, r'procesos', lookup='proceso')
bins_router.register(r'bines-para-proceso', BinsParaProcesoViewSet, basename='proceso-bins')
bins_router.register(r'bines-resultantes-proceso', BinResultanteProcesoViewSet, basename='proceso-binresultantes')
bins_router.register(r'operarios-proceso', OperariosEnProcesoPHViewSet, basename='proceso-operarios')
bins_router.register(r'rechazos-proceso', RechazoProcesoPHViewSet, basename='proceso-rechazos')
bins_router.register(r'variables-proceso', VariablesProcesoPHViewSet, basename='proceso-variables')

# Nested routers
programas_router = routers.NestedSimpleRouter(router, r'programas', lookup='programa')
programas_router.register(r'bines-para-programa', BinParaProgramaViewSet, basename='programa-binparaprograma')
programas_router.register(r'bines-resultantes-programa', BinResultanteProgramaViewSet, basename='programa-binresultanteprograma')
#programas_router.register(r'operarios-programa', OperariosEnProgramaPHViewSet, basename='programa-operarios')
programas_router.register(r'rechazos-programa', RechazoProgramaViewSet, basename='programa-rechazos')
programas_router.register(r'variables-programa', VariablesProgramaPHViewSet, basename='programa-variables')

urlpatterns = router.urls + programas_router.urls + bins_router.urls
