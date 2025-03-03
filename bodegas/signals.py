from django.db.models.signals import post_save
from .models import *
from django.dispatch import receiver
from recepcionmp.models import RecepcionMp, EnvasesGuiaRecepcionMp
from django.db.models import Count, Sum, Avg, FloatField, F
from django.contrib.contenttypes.models import ContentType
from recepcionmp.models import GuiaRecepcionMP
import math, random, string


@receiver(post_save, sender=GuiaRecepcionMP)
def vincular_envases_a_guiapatio_despues_de_cerrar_guia_recepcion(sender, instance, created, **kwargs):
    if instance.estado_recepcion == '4' and not hasattr(instance, '_signal_executed'):
        instance._signal_executed = True
        instance.save()
        ct = ContentType.objects.get_for_model(RecepcionMp)
        pks_lotes = instance.recepcionmp_set.all().values_list('pk', flat=True)
        guiaspatioext = PatioTechadoExterior.objects.filter(tipo_recepcion=ct, id_recepcion__in=pks_lotes)
        
        for guiapatio in guiaspatioext:
            if guiapatio.ubicacion == '0':
                print("La ubicación es '0', saliendo del signal.")
                continue

            recepcion = guiapatio.lote_recepcionado
            if recepcion.guiarecepcion.estado_recepcion != '4':
                print("La recepción no está en estado '4', saliendo del signal.")
                continue

            # Calcular el peso total de la recepción y el peso de los envases
            peso_envases = EnvasesGuiaRecepcionMp.objects.filter(recepcionmp=recepcion).aggregate(
                peso_envases=Sum(F('envase__peso') * F('cantidad_envases'))
            )['peso_envases'] or 0
            peso_total_recepcion = (
                (recepcion.kilos_brutos_1 + recepcion.kilos_brutos_2) -
                (recepcion.kilos_tara_1 + recepcion.kilos_tara_2) - 
                peso_envases
            )

            es_granel = recepcion.envasesguiarecepcionmp_set.filter(envase__nombre='Granel').exists()
            if es_granel:
                pala_retro = 950
                cantidad_envases_granel = math.ceil(peso_total_recepcion / pala_retro)
                peso_por_envase_granel = peso_total_recepcion / cantidad_envases_granel

                for numero_bin in range(1, cantidad_envases_granel + 1):
                    EnvasesPatioTechadoExt.objects.create(
                        guia_patio=guiapatio,
                        numero_bin=numero_bin,
                        kilos_fruta=peso_por_envase_granel,
                        variedad=guiapatio.lote_recepcionado.envasesguiarecepcionmp_set.first().variedad,
                    )
            else:
                # Procedimiento para otros tipos de envase no 'Granel'
                total_envases = sum(envase.cantidad_envases for envase in recepcion.envasesguiarecepcionmp_set.all())
                peso_fruta_por_envase = peso_total_recepcion / total_envases if total_envases > 0 else 0
                for numero_bin in range(1, total_envases + 1):
                    EnvasesPatioTechadoExt.objects.create(
                        guia_patio=guiapatio,
                        numero_bin=numero_bin,
                        kilos_fruta=peso_fruta_por_envase,
                        variedad=guiapatio.lote_recepcionado.envasesguiarecepcionmp_set.first().variedad,
                    )
                    print(f"Creado EnvasesPatioTechadoExt con numero_bin: {numero_bin} y kilos_fruta: {peso_fruta_por_envase}")

            # Actualizar el estado de la recepción a un nuevo estado, si es necesario
            estado_nuevo = '6'
            RecepcionMp.objects.filter(pk=recepcion.pk).update(estado_recepcion=estado_nuevo)
            print(f"Estado de la recepción actualizado a: {estado_nuevo}")


# @receiver(post_save, sender=BodegaG1)
# def vincular_bin_g1_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(BodegaG1)
#         BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk)
                    
# @receiver(post_save, sender=BodegaG1Reproceso)
# def vincular_bin_g1_reproceso_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(BodegaG1Reproceso)
#         BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk)                  

# @receiver(post_save, sender=BodegaG2)
# def vincular_bin_g2_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(BodegaG2)
#         BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk)
                    
# @receiver(post_save, sender=BodegaG2Reproceso)
# def vincular_bin_g2_reproceso_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(BodegaG2Reproceso)
#         BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk) 
        

# @receiver(post_save, sender=BodegaG3)
# def vincular_bin_g3_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(BodegaG3)
#         BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk)

# @receiver(post_save, sender=BodegaG4)
# def vincular_bin_g4_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(BodegaG4)
#         BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk)
        

# def random_codigo_tarja(lenght=6):
#     return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))

# @receiver(post_save, sender = BodegaG5)
# def vincular_bin_g5_a_binbodega(sender, instance, created, **kwargs):
#     if created and instance:
#         ct = ContentType.objects.get_for_model(instance)
#         BinBodega.objects.update_or_create(tipo_binbodega = ct, id_binbodega = instance.pk)
        
           
# @receiver(post_save, sender=TarjaTransferidaG5)
# def vincular_bin_transferidog5_a_g5_y_binbodega(sender, instance, **kwargs):
#     if instance.registro_transferencia.estado_transferencia == '1':
#         codigo = str('G5-')+random_codigo_tarja()
#         bintransg5 = BodegaG5.objects.get_or_create(tarja_g5=instance, codigo_tarja=codigo, kilos_fruta=instance.bin_bodega.binbodega.kilos_fruta)
#         ct = ContentType.objects.get_for_model(BodegaG5)
#         BinBodega.objects.get_or_create(tipo_binbodega=ct, id_binbodega=bintransg5.pk, )