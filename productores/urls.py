from django.urls import path, include
from rest_framework_nested import routers
from .views import *

app_name = 'productores'

router = routers.SimpleRouter()
router.register(r'productores', ProductorViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    # path(r'', include(domains_router.urls)),
]