from django.db.models.signals import post_save, pre_delete, pre_save
from .models import *
from django.dispatch import receiver
from recepcionmp.models import RecepcionMp, EnvasesGuiaRecepcionMp
from django.db.models import Count, Sum, Avg, FloatField, F
from django.contrib.contenttypes.models import ContentType
from recepcionmp.models import GuiaRecepcionMP
import math
from bodegas.models import BinBodega


@receiver(post_save, sender=AgrupacionDeBinsBodegas)
def vincular_bin_agrupado_a_binbodega(sender, instance, created, **kwargs):
    if not created and instance.agrupamiento_ok:
        ct = ContentType.objects.get_for_model(AgrupacionDeBinsBodegas)
        BinBodega.objects.get_or_create(tipo_binbodega=ct, id_binbodega=instance.pk, estado_binbodega='11')

        variedades = []
        for bin_ingresado in instance.binsparaagrupacion_set.all():
            modelo_bin = bin_ingresado.tipo_tarja.model

            if modelo_bin not in ['bodegag6', 'bodegag7']:
                # Si tiene el atributo 'variedad' y es no nulo, agregarlo a la lista
                if hasattr(bin_ingresado.tarja, 'variedad') and bin_ingresado.tarja.variedad:
                    variedades.append(bin_ingresado.tarja.variedad)
                else:
                    # Añadir un valor predeterminado si no hay variedad o si no está definida
                    variedades.append('RV')
            else:
                # Manejar explícitamente bins de los tipos g6 o g7
                variedades.append('RV')

        # Determinar la variedad para la agrupación
        variedades_unicas = set(variedades)
        variedad = 'RV' if len(variedades_unicas) > 1 else variedades_unicas.pop() if variedades_unicas else 'Indefinido'
        
        if instance.variedad != variedad:
            instance.variedad = variedad
            instance.save(update_fields=['variedad'])

        
            
        
        


# @receiver(post_save, sender=BinsParaAgrupacion)
# def cambiar_estado_en_bin_bodega_introducida_en_agrupacion(sender, instance, created, **kwargs):
#     BinBodega.objects.filter(id_binbodega = instance.id_tarja, tipo_binbodega = instance.tipo_tarja).update(estado_binbodega = '10')
    
    
 
    # @receiver(pre_delete, sender=AgrupacionDeBinsBodegas)
    # def modificar_booleano_de_bin_bodega_introducida_en_agrupacion(sender, instance, **kwargs):
    #     menor_valor = float('inf')
    #     bin_menor_valor = None
    #     for bin in instance.binsparaagrupacion_set.all():
    #         if bin.tarja.kilos_fruta < menor_valor:
    #             menor_valor = bin.tarja.kilos_fruta
    #             bin_menor_valor = bin.tarja       
    #     ct = ContentType.objects.get_for_model(bin_menor_valor)
    #     binbodega = BinBodega.objects.filter(id_binbodega = bin_menor_valor.pk, tipo_binbodega = ct)
    #     fruta_sobrante = FrutaSobranteDeAgrupacion.objects.filter(id_tarja = bin_menor_valor.pk, tipo_tarja = ct)
    #     if binbodega.exists() and fruta_sobrante.exists():
    #         binbodega.update(estado_binbodega = '10')
    #     else:
    #         BinBodega.objects.filter(id_binbodega = bin.id_tarja, tipo_binbodega = bin.tipo_tarja).update(estado_binbodega = '16')
            
        
@receiver(post_save, sender=FrutaSobranteDeAgrupacion)
def creacion_de_bin_bodega_de_fruta_resultante(sender, instance, created, **kwargs):
    if created and instance:
        ct = ContentType.objects.get_for_model(FrutaSobranteDeAgrupacion)
        BinBodega.objects.get_or_create(tipo_binbodega=ct, id_binbodega = instance.pk, estado_binbodega = '16')
        
        
