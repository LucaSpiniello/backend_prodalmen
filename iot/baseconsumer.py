# base_consumer.py
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class BaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Verificar si el usuario está autenticado antes de aceptar la conexión
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            self.room_group_name = f'iot_{self.scope["url_route"]["kwargs"]["room_name"]}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Desconectar el grupo si la conexión fue previamente aceptada
        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )