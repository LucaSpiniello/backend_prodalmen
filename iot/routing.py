from django.urls import re_path, path
from .consumers import *
from inventario.consumers import UpdateBinEnInventarioConsumer
from core.consumers import NotificacionesConsumer

websocket_urlpatterns = [
    re_path(r'ws/iot/(?P<room_name>\w+)/$', IoTConsumer.as_asgi()),
    #path('ws/notifications/', NotificationConsumer.as_asgi()),
    re_path(r'ws/notificaciones/$', NotificacionesConsumer.as_asgi()),
    re_path(r'ws/update_bin_en_inventario/$', UpdateBinEnInventarioConsumer.as_asgi()),
]