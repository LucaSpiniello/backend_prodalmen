from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import *

app_name='despacho'
router = DefaultRouter()
router.register(r'despachos', DespachoViewSet)

despachos_router = routers.NestedSimpleRouter(router, r'despachos', lookup='despacho')
despachos_router.register(r'fruta', FrutaEnDespacho)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(despachos_router.urls)),
]
