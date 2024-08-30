import os
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
# from clientemqtt.consumers import BalanzaMQTT
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prodalwebV3.settings')
django_asgi_app = get_asgi_application()
import iot.routing
from iot.mildware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            iot.routing.websocket_urlpatterns
        )
    ),
})