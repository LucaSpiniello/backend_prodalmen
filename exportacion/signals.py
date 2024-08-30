from django.db.models.signals import post_save, pre_delete, pre_save
from .models import *
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from pedidos.models import *
from despacho.models import *

@receiver(pre_save, sender=PedidoExportacion)
def capturar_estado_original(sender, instance, **kwargs):
    # Si la instancia ya está en la base de datos, capturamos el estado original
    if instance.pk:
        original = sender.objects.get(pk=instance.pk)
        instance._original_retira_cliente = original.retira_cliente
        instance._original_estado_pedido = original.estado_pedido
    else:
        # Si es una nueva instancia, asumimos que no es retira_cliente por defecto
        instance._original_retira_cliente = False

@receiver(post_save, sender=PedidoExportacion)
def creacion_de_despacho_en_caso_de_retira_cliente(sender, instance, created, **kwargs):
    # Solo actuar si no es una creación y si hay un cambio relevante en 'retira_cliente'
    if not created and hasattr(instance, '_original_retira_cliente'):
        if instance.retira_cliente != instance._original_retira_cliente:
            ct = ContentType.objects.get_for_model(instance)
            pedido = Pedido.objects.filter(tipo_pedido=ct, id_pedido=instance.pk).first()

            if not instance.retira_cliente:
                # Si 'retira_cliente' cambia a False, crear un despacho
                if instance.creado_por:
                    Despacho.objects.create(
                        pedido=pedido,
                        creado_por=instance.creado_por,
                        empresa_transporte='Sin registro',
                        camion='Sin registro',
                        nombre_chofer='Sin registro',
                        rut_chofer='Sin registro',
                        observaciones='Sin observaciones',
                        estado_despacho='0'
                    )
            else:
                # Si 'retira_cliente' cambia a True, eliminar despachos existentes
                Despacho.objects.filter(pedido=pedido).delete()
                

# @receiver(post_save, sender = FrutaPedido)
# def cambiar_estado_del_pedido_mercado_interno(sender, created, instance, **kwargs):
#   if created:
#     PedidoExportacion.objects.filter(pk = instance.exportacion.pk).update(estado_pedido = '2')
    
@receiver(pre_delete, sender = PedidoExportacion)
def eliminacion_de_pedido_padre(sender, instance, **kwargs):
  ct = ContentType.objects.get_for_model(instance)
  Pedido.objects.filter(tipo_pedido = ct, id_pedido = instance.pk).delete()
  
@receiver(pre_save, sender = PedidoExportacion)
def descuento_de_bodega_o_pallet_producto_terminado(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = instance.pk).first()

    if instance.estado_pedido == '3':
      Despacho.objects.filter(pedido = pedido).update(estado_despacho = '2')
    elif instance.estado_pedido == '4':
      Despacho.objects.filter(pedido = pedido).update(estado_despacho = '3')