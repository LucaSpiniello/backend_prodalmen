from django.db.models.signals import post_save, pre_delete, pre_save
from .models import *
from django.dispatch import receiver
from pedidos.models import *
from django.contrib.contenttypes.models import ContentType
from despacho.models import *

@receiver(pre_save, sender=PedidoMercadoInterno)
def capturar_estado_original_mercado_interno(sender, instance, **kwargs):
    if instance.pk:
        original = sender.objects.get(pk=instance.pk)
        instance._original_retira_cliente = original.retira_cliente
    else:
        instance._original_retira_cliente = False


@receiver(post_save, sender=PedidoMercadoInterno)
def creacion_de_despacho_en_caso_de_retira_cliente(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_original_retira_cliente'):
        if instance.retira_cliente != instance._original_retira_cliente:
            ct = ContentType.objects.get_for_model(instance)
            pedido = Pedido.objects.filter(tipo_pedido=ct, id_pedido=instance.pk).first()

            if not instance.retira_cliente:
                # Crear despacho si 'retira_cliente' cambia a False
                if instance.solicitado_por:
                    Despacho.objects.create(
                        pedido=pedido,
                        creado_por=instance.solicitado_por,
                        empresa_transporte='Sin registro',
                        camion='Sin registro',
                        nombre_chofer='Sin registro',
                        rut_chofer='Sin registro',
                        observaciones='Sin observaciones',
                        estado_despacho='0'
                    )
            else:
                # Eliminar despachos existentes si 'retira_cliente' cambia a True
                Despacho.objects.filter(pedido=pedido).delete()

# @receiver(post_save, sender = FrutaPedido)
# def cambiar_estado_del_pedido_mercado_interno(sender, created, instance, **kwargs):
#   if created:
#     PedidoMercadoInterno.objects.filter(pk = instance.pedido.pk).update(estado_pedido = '2')
    
    
@receiver(pre_delete, sender = PedidoMercadoInterno)
def eliminacion_de_pedido_padre(sender, instance, **kwargs):
  ct = ContentType.objects.get_for_model(instance)
  Pedido.objects.filter(tipo_pedido = ct, id_pedido = instance.pk).delete()
  

@receiver(pre_save, sender=PedidoMercadoInterno)
def descuento_de_bodega_o_pallet_producto_terminado(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    
    try:
        pedido = Pedido.objects.get(tipo_pedido=ct, id_pedido=instance.pk)
        print(pedido)
    except Pedido.DoesNotExist:
        pedido = None

    if pedido:
        if instance.estado_pedido == '3':
            Despacho.objects.filter(pedido=pedido).update(estado_despacho='2')
        elif instance.estado_pedido == '4':
            Despacho.objects.filter(pedido=pedido).update(estado_despacho='3')
    
    