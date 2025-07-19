from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    
    path('token_estaticos/', include('rest_authtoken.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/', include('recepcionmp.urls', namespace='recepcionmp')),
    path('api/', include('productores.urls', namespace='productores')),
    path('api/', include('core.urls', namespace='core')),
    path('api/', include('comunas.urls')),
    path('api/', include('comercializador.urls', namespace='comercializador')),
    path('api/', include('controlcalidad.urls', namespace='controlcalidad')),
    path('api/', include('bodegas.urls', namespace='bodegas')),
    path('api/', include('produccion.urls', namespace='produccion')),
    path('api/', include('seleccion.urls', namespace='seleccion')),
    path('api/', include('cuentas.urls', namespace='cuentas')),
    path('api/', include('agrupacionbins.urls', namespace='agrupacionbins')),
    path('api/', include('despacho.urls', namespace='despacho')),
    path('api/', include('clientes.urls', namespace='clientes')),
    path('api/', include('mercadointerno.urls', namespace='mercadointerno')),
    path('api/', include('embalaje.urls', namespace='embalaje')),
    path('api/', include('exportacion.urls', namespace='exportacion')),
    path('api/', include('pedidos.urls', namespace='pedidos')),
    path('api/', include('guiassalida.urls', namespace='guiassalida')),
    path('api/', include('inventario.urls', namespace='inventario')),
    path('api/', include('planta_harina.urls', namespace='planta_harina')),
    #path('api/', include('agrupaciondebins.urls', namespace='agrupaciondebins')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)