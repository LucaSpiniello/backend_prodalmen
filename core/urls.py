from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'core'

router = routers.SimpleRouter()
router.register(r'colosos', ColosoViewSet)
router.register(r'operarios', OperarioViewSet)
router.register(r'tractores', TractorViewSet)
router.register(r'etiquetas-zpl', EtiquetasZplViewSet)
router.register(r'choferes', ChoferViewSet)
router.register(r'camiones', CamionViewSet)


tractor_coloso = routers.NestedSimpleRouter(router, r'tractores', lookup='tractores')
tractor_coloso.register(r'coloso-tractor', TractorColosoViewSet)

urlpatterns = [
    path(r'registros/', include(router.urls)),
    path(r'registros/', include(tractor_coloso.urls)),
    path('contenttypes/', ContentTypeListView.as_view(), name='contenttype-list'),
]