from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'recepcionmp'

router = routers.SimpleRouter()
router.register(r'recepcionmp', GuiaRecepcionMPViewSet)
router.register(r'envasesmp', EnvasesMpViewSet)
router.register(r'envaseguiamp', EnvasesGuiaMPViewSet)
# router.register(r'lotes_rechazados', LoteRechazadoViewset, basename='todos_los_lotes_rechazados')

lotes_guia = routers.NestedSimpleRouter(router, r'recepcionmp', lookup='recepcionmp')
lotes_guia.register(r'lotes', RecepcionMpViewSet)

lotes_router = routers.NestedSimpleRouter(router, r'recepcionmp', lookup='recepcionmp')
lotes_router.register(r'lotes', RecepcionMpViewSet, basename='recepcionmp-lotes')

# Anidar 'envases' dentro de 'lotes'
envases_router = routers.NestedSimpleRouter(lotes_router, r'lotes', lookup='lote')
envases_router.register(r'envases', EnvasesGuiaMPViewSet, basename='lotes-envases')

lotes_guia_rechazados = routers.NestedSimpleRouter(router, r'recepcionmp', lookup='recepcionmp')
# lotes_guia_rechazados.register(r'lotes_rechazados', LoteRechazadoViewset )

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(lotes_guia.urls)),
    path('', include(envases_router.urls)),
    path(r'', include(lotes_guia_rechazados.urls))
]