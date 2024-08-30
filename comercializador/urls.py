from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = 'comercializador'

router = routers.SimpleRouter()
router.register(r'comercializador', ComercializadorViewSet)

urlpatterns = [
  path(r'', include(router.urls))
]

