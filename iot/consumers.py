# # iot_consumers.py
# import json
# from channels.db import database_sync_to_async
# from .baseconsumer import BaseConsumer
# from controlcalidad.models import CCRecepcionMateriaPrima
# from recepcionmp.models import GuiaRecepcionMP
# from django.contrib.auth.models import AnonymousUser
# from channels.generic.websocket import AsyncWebsocketConsumer

# class IoTConsumer(BaseConsumer):
#     async def receive(self, text_data):
#         if isinstance(self.scope['user'], AnonymousUser):
#             await self.send(text_data=json.dumps({"error": "Usuario no autenticado"}))
#             return

#         text_data_json = json.loads(text_data)
#         action = text_data_json.get('accion')

#         # Llama a la función correspondiente según la acción
#         if action == 'lotes_aprobados_cdc':
#             await self.process_approved_lots()
#         elif action == 'total_guias_recepcion':
#             await self.process_total_guias_recepcion()
#         else:
#             await self.send(text_data=json.dumps({"error": "Accion no reconocida"}))

#     @database_sync_to_async
#     def get_approved_count(self):
#         return CCRecepcionMateriaPrima.objects.filter(estado_aprobacion_cc='1').count()

#     @database_sync_to_async
#     def count_guias_recepcion(self):
#         return GuiaRecepcionMP.objects.all().count()

#     async def process_approved_lots(self):
#         total_lotes = await self.get_approved_count()
#         await self.send(text_data=json.dumps({
#             'accion': 'lotes_aprobados_cdc',
#             'total': total_lotes
#         }))

#     async def process_total_guias_recepcion(self):
#         total_guias = await self.count_guias_recepcion()
#         await self.send(text_data=json.dumps({
#             'accion': 'total_guias_recepcion',
#             'total': total_guias
#         }))


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.channel_layer.group_add('notificaciones', self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard('notificaciones', self.channel_name)

#     async def user_notification(self, event):
#         message = event['message']
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))

# iot_consumers.py
import json
from channels.db import database_sync_to_async
from .baseconsumer import BaseConsumer
from controlcalidad.models import CCRecepcionMateriaPrima
from recepcionmp.models import GuiaRecepcionMP, RecepcionMp
from django.contrib.auth.models import AnonymousUser
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

class IoTConsumer(BaseConsumer):
    async def receive(self, text_data):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.send(text_data=json.dumps({"error": "Usuario no autenticado"}))
            return

        text_data_json = json.loads(text_data)
        action = text_data_json.get('accion')

        # Llama a la función correspondiente según la acción
        if action == 'lotes_aprobados_cdc':
            await self.process_approved_lots()
        elif action == 'total_guias_recepcion':
            await self.process_total_guias_recepcion()
        elif action == 'recepcionmp_metrica':
            await self.process_recepcionmp_metrica()
        else:
            await self.send(text_data=json.dumps({"error": "Accion no reconocida"}))

    @database_sync_to_async
    def get_approved_count(self):
        return CCRecepcionMateriaPrima.objects.filter(estado_aprobacion_cc='1').count()

    @database_sync_to_async
    def count_guias_recepcion(self):
        return GuiaRecepcionMP.objects.all().count()

    @database_sync_to_async
    def get_recepcionmp_metrics(self):
        current_year = timezone.now().year

        guiasrecepcion_creadas = GuiaRecepcionMP.objects.filter(estado_recepcion='1').count()
        guiasrecepcion_en_curso = GuiaRecepcionMP.objects.filter(estado_recepcion__in=['2', '3']).count()
        guiasrecepcion_completadas = GuiaRecepcionMP.objects.filter(estado_recepcion='4').count()
        
        lotes_aprobados = RecepcionMp.objects.filter(estado_recepcion__in=['3', '5', '6'], fecha_creacion__year=current_year).count()
        lotes_rechazados = RecepcionMp.objects.filter(estado_recepcion='4', fecha_creacion__year=current_year).count()

        return {
            'guiasrecepcion_creadas': guiasrecepcion_creadas,
            'guiasrecepcion_en_curso': guiasrecepcion_en_curso,
            'guiasrecepcion_completadas': guiasrecepcion_completadas,
            'lotes_aprobados': lotes_aprobados,
            'lotes_rechazados': lotes_rechazados,
        }

    async def process_approved_lots(self):
        total_lotes = await self.get_approved_count()
        await self.send(text_data=json.dumps({
            'accion': 'lotes_aprobados_cdc',
            'total': total_lotes
        }))

    async def process_total_guias_recepcion(self):
        total_guias = await self.count_guias_recepcion()
        await self.send(text_data=json.dumps({
            'accion': 'total_guias_recepcion',
            'total': total_guias
        }))

    async def process_recepcionmp_metrica(self):
        metrics = await self.get_recepcionmp_metrics()
        await self.send(text_data=json.dumps({
            'accion': 'recepcionmp_metrica',
            'data': metrics
        }))
