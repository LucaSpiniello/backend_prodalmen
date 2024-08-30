from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'cuentas'

router = routers.SimpleRouter()
router.register(r'personalizacion-perfil', PersonalizacionPerfilViewSet)
router.register(r'grupos', GroupViewSet)


urlpatterns = [
    path(r'registros/', include(router.urls)),
    path('user_groups/', get_user_groups, name='get_user_groups'),

]