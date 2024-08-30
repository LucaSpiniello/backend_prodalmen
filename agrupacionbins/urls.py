from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgrupacionDeBinsBodegasViewSet

app_name="agrupacionbins"


router = DefaultRouter()
router.register(r'agrupacion', AgrupacionDeBinsBodegasViewSet)

urlpatterns = [
    path('', include(router.urls)),
]