from core.base_consumer import JWTConsumerBase
import json
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import BinEnInventario, InventarioBodega
from bodegas.models import BinBodega
from asgiref.sync import sync_to_async

# class UpdateBinEnInventarioConsumer(JWTConsumerBase):
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         bin_id = data.get('bin_id')
#         inventario_id = data.get('inventario_id')
#         validado = data.get('validado')

#         if bin_id is not None and inventario_id is not None and validado is not None:
#             update_result = await self.update_bin_en_inventario(bin_id, inventario_id, validado)
#             if update_result:
#                 await self.send(text_data=json.dumps({
#                     'status': 'success',
#                     'message': f'Bin {bin_id} actualizado correctamente.'
#                 }))
#             else:
#                 await self.send(text_data=json.dumps({
#                     'status': 'error',
#                     'message': 'Error actualizando el Bin.'
#                 }))
#         else:
#             await self.send(text_data=json.dumps({
#                 'status': 'error',
#                 'message': 'Datos inválidos.'
#             }))

#     @database_sync_to_async
#     def update_bin_en_inventario(self, bin_id, inventario_id, validado):
#         try:
#             # binbodega = BinBodega.objects.get(pk=bin_id)
#             inventario = InventarioBodega.objects.get(pk=inventario_id)
#             bin_en_inventario = BinEnInventario.objects.get(pk=bin_id, inventario=inventario)
#             bin_en_inventario.validado = validado
#             bin_en_inventario.validado_por = self.user
#             bin_en_inventario.save()
#             return True
#         except (BinEnInventario.DoesNotExist, BinBodega.DoesNotExist, InventarioBodega.DoesNotExist) as e:
#             return False


class UpdateBinEnInventarioConsumer(JWTConsumerBase):
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        bin_id = data.get('bin_id')
        inventario_id = data.get('inventario_id')

        if action == 'check_and_update_bin_status':
            await self.handle_check_and_update_bin_status(bin_id, inventario_id)
        else:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Acción no válida.'
            }))

    async def handle_check_and_update_bin_status(self, bin_id, inventario_id):
        if bin_id is not None and inventario_id is not None:
            bin_status = await self.check_and_update_bin_status(bin_id, inventario_id)
            if bin_status['status'] == 'success':
                await self.send(text_data=json.dumps(bin_status))
            else:
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': bin_status['message']
                }))
        else:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Datos inválidos.'
            }))

    @database_sync_to_async
    def check_and_update_bin_status(self, bin_id, inventario_id):
        try:
            inventario = InventarioBodega.objects.get(pk=inventario_id)
            bin_en_inventario = BinEnInventario.objects.get(pk=bin_id, inventario=inventario)

            if bin_en_inventario.validado:
                return {
                    'status': 'info',
                    'message': f'Bin {bin_id} ya habia sido validado anteriormente.',
                    'bin_id': bin_id,
                    'inventario_id': inventario_id,
                    'validado': bin_en_inventario.validado,
                    'validado_por': bin_en_inventario.validado_por.email if bin_en_inventario.validado_por else None,
                    'fecha_modificacion': bin_en_inventario.fecha_modificacion.isoformat() if bin_en_inventario.fecha_modificacion else None
                }
            else:
                bin_en_inventario.validado = True
                bin_en_inventario.validado_por = self.user
                bin_en_inventario.save()
                return {
                    'status': 'success',
                    'message': f'Bin {bin_id} validado correctamente.',
                    'bin_id': bin_id,
                    'inventario_id': inventario_id,
                    'validado': bin_en_inventario.validado,
                    'validado_por': bin_en_inventario.validado_por.email if bin_en_inventario.validado_por else None,
                    'fecha_modificacion': bin_en_inventario.fecha_modificacion.isoformat() if bin_en_inventario.fecha_modificacion else None
                }
        except (BinEnInventario.DoesNotExist, InventarioBodega.DoesNotExist) as e:
            return {
                'status': 'error',
                'message': 'Error obteniendo o actualizando el estado del Bin.'
            }
