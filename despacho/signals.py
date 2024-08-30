from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from despacho.models import *
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from mercadointerno.models import *
from exportacion.models import *
from embalaje.models import *



@receiver(post_save, sender=Despacho)
def creacion_fruta_pedido_segun_despacho_parcial(sender, instance, created, **kwargs):
    with transaction.atomic():
        if created:
            # # Manejo de creación de nuevos despachos
            # if instance.pedido.frutas.all().count() > 0:
            #     for fruta in instance.pedido.frutas.all():
            #         DespachoProducto.objects.create(
            #             despacho=instance,
            #             fruta_en_pedido=fruta,
            #             cantidad=fruta.cantidad
            #         )
            # return
            pass

        # Cargar la instancia anterior del despacho para comparar cambios
        old_instance = Despacho.objects.get(pk=instance.pk)

        if old_instance.despacho_parcial and not instance.despacho_parcial:
            # Convertir de despacho parcial a no parcial
            DespachoProducto.objects.filter(despacho=instance).delete()
            for fruta in instance.pedido.frutas.all():
                DespachoProducto.objects.create(
                    despacho=instance,
                    fruta_en_pedido=fruta,
                    cantidad=fruta.cantidad
                )

        elif instance.despacho_parcial:
            # Manejar cambios en despacho parcial
            if instance.estado_despacho not in ['1', '2', '3']:
                DespachoProducto.objects.filter(despacho=instance).delete()
    

@receiver(post_save, sender = Despacho)
def descuento_de_fruta_de_bodega_o_pallet_seleccionado(sender, instance, **kwargs):

    if instance.estado_despacho == '2':
        pedido = Pedido.objects.filter(pk = instance.pedido.pk).update(estado_pedido = 'E')
        productos_despacho = DespachoProducto.objects.filter(despacho = instance)
        for producto in productos_despacho:
            ct = ContentType.objects.get_for_model(producto.fruta_en_pedido.fruta)
            if ct.model == 'palletproductoterminado':
                cajas = CajasEnPalletProductoTerminado.objects.filter(pallet = producto.fruta_en_pedido.fruta).first()
                cajas.cantidad_cajas -= producto.cantidad
                cajas.save()
                PalletProductoTerminado.objects.filter(pk = producto.fruta_en_pedido.fruta.pk).update(estado_pallet = '2')
            elif ct.model == 'binbodega':
                BinBodega.objects.filter(pk = producto.fruta_en_pedido.fruta.pk).update(estado_binbodega = '14')
                