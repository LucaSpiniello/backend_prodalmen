from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'clientes'

# Crear el router principal
router = routers.DefaultRouter()

router.register(r'clientes', ClientesViewSet, basename = 'clientes_unificados')
router.register(r'countries', CountryViewSet)
router.register(r'clientes_mercado_interno', ClienteMercadoInternoViewSet)
router.register(r'ctas_corrientes', Cta_CorrienteViewSet)
router.register(r'sucursales_mercado_interno', SucursalClienteMercadoViewSet)
router.register(r'representantes_legales', RRLLViewSet)
router.register(r'clientes_exportacion', ClienteExportacionViewSet)
router.register(r'sucursales_exportacion', SucursalClienteExportacionViewSet)

# Crear los routers anidados
clientes_mercado_router = routers.NestedSimpleRouter(router, r'clientes_mercado_interno', lookup='cliente_mercado_interno')
clientes_mercado_router.register(r'sucursales', SucursalClienteMercadoViewSet, basename='cliente-mercado-sucursales')
clientes_mercado_router.register(r'representantes', RRLLViewSet, basename='cliente-mercado-representantes')
clientes_mercado_router.register(r'cuentas_corrientes', Cta_CorrienteViewSet, basename='cliente-mercado-cuentas')

clientes_exportacion_router = routers.NestedSimpleRouter(router, r'clientes_exportacion', lookup='cliente_exportacion')
clientes_exportacion_router.register(r'sucursales', SucursalClienteExportacionViewSet, basename='cliente-exportacion-sucursales')

countries_router = routers.NestedSimpleRouter(router, r'countries', lookup='country')
countries_router.register(r'cities', CityViewSet, basename='country-cities')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(clientes_mercado_router.urls)),
    path('', include(clientes_exportacion_router.urls)),
    path('', include(countries_router.urls)),
]
