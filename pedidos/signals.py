from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from despacho.models import Despacho, DespachoProducto
from pedidos.models import Pedido, FrutaEnPedido
from mercadointerno.models import PedidoMercadoInterno
from exportacion.models import PedidoExportacion
from guiassalida.models import GuiaSalidaFruta
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from bodegas.models import *
from embalaje.models import *


@receiver(post_save, sender=PedidoMercadoInterno)
def vincula_pedido_mercadointerno_a_pedidos_sys(sender, instance, created, **kwargs):
    if created:
        ct = ContentType.objects.get_for_model(instance)
        Pedido.objects.get_or_create(tipo_pedido=ct, id_pedido=instance.pk)

        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     'notificaciones',
        #     {
        #         'type': 'pedido.notificacion',
        #         'message': f'Pedido N° {instance.pk} creado'
        #     }
        # )
        
        
        
        
@receiver(post_save, sender = FrutaEnPedido)
def creacion_en_despacho(sender, created, instance, **kwargs):
    if created and not instance.pedido.pedido_real.retira_cliente:
        despacho = Despacho.objects.get(pedido = instance.pedido)
        DespachoProducto.objects.update_or_create(
            despacho = despacho,
            fruta_en_pedido = instance,
            cantidad = instance.cantidad
        )
        
        
@receiver(pre_delete, sender = FrutaEnPedido)
def eliminacion_en_despacho(sender, instance, **kwargs):
    try:     
        despacho = Despacho.objects.get(pedido = instance.pedido)
        DespachoProducto.objects.filter(despacho = despacho).delete()
    except:
        pass
        
@receiver(pre_save, sender = FrutaEnPedido)
def cambiar_estado_de_pallet_o_bodega_relacionada(sender, instance, **kwargs):
    if instance.tipo_fruta.model == 'binbodega':
        BinBodega.objects.filter(pk = instance.id_fruta).update(estado_binbodega = '13', ingresado=True)
    elif instance.tipo_fruta.model == 'palletproductoterminado':
        PalletProductoTerminado.objects.filter(pk = instance.id_fruta).update(estado_pallet = '2')

@receiver(pre_delete, sender=FrutaEnPedido)
def cambiar_estado_de_pallet_o_bodega_relacionada_tras_eliminar(sender, instance, **kwargs):
    if instance.tipo_fruta.model == 'binbodega':
        BinBodega.objects.filter(pk = instance.id_fruta).update(estado_binbodega = '16', ingresado=False)
    elif instance.tipo_fruta.model == 'palletproductoterminado':
        PalletProductoTerminado.objects.filter(pk = instance.id_fruta).update(estado_pallet = '1')

@receiver(post_save, sender=GuiaSalidaFruta)
def vincula_pedido_guiasalidafruta_a_pedidos_sys(sender, instance, created, **kwargs):
    if created:
        ct = ContentType.objects.get_for_model(instance)
        Pedido.objects.get_or_create(tipo_pedido=ct, id_pedido=instance.pk)

       
@receiver(post_save, sender=PedidoExportacion)
def vincula_pedido_exportacion_a_pedidos_sys(sender, instance, created, **kwargs):
    if created:
        ct = ContentType.objects.get_for_model(instance)
        Pedido.objects.get_or_create(tipo_pedido=ct, id_pedido=instance.pk)

@receiver(post_save, sender=Pedido)
def crear_despacho_automaticamente(sender, instance, created, **kwargs):
    if created and not instance.pedido_real.retira_cliente:
        if instance.tipo_pedido.model == 'pedidomercadointerno':
            usuario_creador = instance.pedido_real.solicitado_por
        elif instance.tipo_pedido.model == 'pedidoexportacion':
            usuario_creador = instance.pedido_real.creado_por
        elif instance.tipo_pedido.model == 'guiasalidafruta':
                usuario_creador = instance.pedido_real.solicitado_por

        if usuario_creador:
            # Crear el despacho con los datos adecuados
            Despacho.objects.create(
                pedido=instance,
                creado_por=usuario_creador,
                empresa_transporte = 'Sin registro',
                camion = 'Sin registro',
                nombre_chofer = 'Sin registro',
                rut_chofer = 'Sin registro',
                observaciones = 'Sin observaciones',
                estado_despacho='0'
            )
   
        


# @receiver(pre_save, sender=Pedido)
# def verificar_retiro_cliente(sender, instance, **kwargs):
#     if instance.pedido_real.retira_cliente:
#         print('me ejecuto en v')
#         # Decidir el usuario creado basado en el tipo de pedido
#         usuario_creador = None
#         if instance.tipo_pedido.model == 'pedidomercadointerno':
#             usuario_creador = instance.pedido_real.solicitado_por
#         elif instance.tipo_pedido.model == 'pedidoexportacion':
#             usuario_creador = instance.pedido_real.creado_por
#         elif instance.tipo_pedido.model == 'guiasalidafruta':
#             usuario_creador = instance.pedido_real.solicitado_por
        
#         if usuario_creador:
#             # Crear el despacho con los datos adecuados
#             despacho = Despacho.objects.create(
#                 pedido=instance,
#                 creado_por=usuario_creador,
#                 estado_despacho='0'
#             )
        
        
#         for fruta in instance.frutas_en_pedido.filter(despachado=False):
#             DespachoProducto.objects.create(
#                 despacho=despacho,
#                 fruta_en_pedido=fruta,
#                 cantidad=fruta.cantidad
#             )
#     else:
#         # Eliminar despacho si el pedido se actualiza de no retiro por el cliente a retiro por el cliente
#         Despacho.objects.filter(pedido=instance).delete()

# @receiver(post_save, sender=Despacho)
# def crear_despacho_producto(sender, instance, created, **kwargs):
#     if created and instance.despacho_parcial:
#         for fruta in instance.pedido.frutas_en_pedido.filter(despachado=False):
#             DespachoProducto.objects.create(
#                 despacho=instance,
#                 fruta_en_pedido=fruta,
#                 cantidad=fruta.cantidad
#             )

@receiver(post_save, sender=Despacho)
def crear_despacho_producto(sender, instance, created, **kwargs):
    if created:
        frutas_en_pedido = instance.pedido.frutas_en_pedido.all()
        
        # Verificar si todos los elementos están despachado=True
        all_despachado = all(fruta.despachado for fruta in frutas_en_pedido)

        if all_despachado:
            # Si todos están despachado=True, crear DespachoProducto para todos
            for fruta in frutas_en_pedido:
                DespachoProducto.objects.create(
                    despacho=instance,
                    fruta_en_pedido=fruta,
                    cantidad=fruta.cantidad
                )
            instance.despacho_parcial = False  # Todos están despachados, no es parcial
        else:
            # Crear DespachoProducto solo para los que están despachado=True
            for fruta in frutas_en_pedido.filter(despachado=True):
                DespachoProducto.objects.create(
                    despacho=instance,
                    fruta_en_pedido=fruta,
                    cantidad=fruta.cantidad
                )
            instance.despacho_parcial = True  # No todos están despachados, es parcial
        
        # Guardar el estado actualizado de despacho_parcial
        instance.save()
        

@receiver(pre_delete, sender=Pedido)
def eliminar_pedido_asociado(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    Pedido.objects.filter(tipo_pedido=ct, id_pedido=instance.pk).delete()
