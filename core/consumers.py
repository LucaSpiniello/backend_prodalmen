from core.base_consumer import JWTConsumerBase
import json
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from bodegas.models import BinBodega
from asgiref.sync import sync_to_async
from .redis_client import redis_client

class NotificacionesConsumer(JWTConsumerBase):
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("accion")
            if action == "get_notificaciones":
                await self.get_notifications()
            else:
                await self.send(text_data=json.dumps({"type": "error", "message": "Acción inválida"}, ensure_ascii=False))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "JSON inválido recibido"}, ensure_ascii=False))

    async def get_notifications(self):
        notifications = await self.get_notifications_from_redis()
        await self.send(text_data=json.dumps({
            "type": "notificaciones",
            "data": notifications
        }, ensure_ascii=False))


    @sync_to_async
    def get_notifications_from_redis(self):
        notifications = redis_client.lrange(f'notificaciones:{self.user.id}', 0, -1)
        return [json.loads(notification) for notification in notifications]
        
        
