import json
from .redis_client import redis_client
from django.utils import timezone


def guardar_notificacion_usuario(user_id, tipo, mensaje):

    notification = {
            "type": tipo,
            "message": mensaje,
            "timestamp": timezone.now().isoformat()
        }
    
    notification_data = json.dumps(notification)
    redis_client.rpush(f'notificaciones:{user_id}', notification_data)
    redis_client.expire(f'notificaciones:{user_id}', 30 * 24 * 60 * 60)  # Expira en 1 mes 30 * 24 * 60 * 60
