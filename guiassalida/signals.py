from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from despacho.models import Despacho
from pedidos.models import *
from guiassalida.models import GuiaSalidaFruta
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(pre_save, sender=GuiaSalidaFruta)
def capturar_estado_original_guia_salida(sender, instance, **kwargs):
    if instance.pk:
        original = sender.objects.get(pk=instance.pk)
        instance._original_retira_cliente = original.retira_cliente
    else:
        instance._original_retira_cliente = False
        
@receiver(pre_delete, sender = GuiaSalidaFruta)
def eliminacion_de_pedido_padre(sender, instance, **kwargs):
  ct = ContentType.objects.get_for_model(instance)
  Pedido.objects.filter(tipo_pedido = ct, id_pedido = instance.pk).delete()

@receiver(post_save, sender=GuiaSalidaFruta)
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
