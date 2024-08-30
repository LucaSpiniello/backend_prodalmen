from django.db.models.signals import post_save, post_delete, pre_save
from recepcionmp.signals import sugerir_numero_faltante
from .models import *
from django.dispatch import receiver
from recepcionmp.models import RecepcionMp, EnvasesGuiaRecepcionMp
from django.db.models import Count, Sum, Avg, FloatField, F
from django.contrib.contenttypes.models import ContentType
from bodegas.models import *
import random, string
from controlcalidad.models import *
from django.utils import timezone
from datetime import timedelta
from recepcionmp.signals import sugerir_numero_faltante
from datetime import date


### INICIO SIGNALS DE GESTION DE PROGRAMA ###
@receiver(post_save, sender = Produccion)
def generar_numero_programa_correlativo(sender, instance, created, **kwargs):
    if created and instance:
        # Obtener todos los números de lote existentes
        numeros_programa_existentes = Produccion.objects.exclude(numero_programa=0).values_list('numero_programa', flat=True)
        instance.numero_programa = sugerir_numero_faltante(numeros_programa_existentes)
        # Guarda el objeto con el nuevo número de lote
        instance.save()

@receiver(pre_save, sender=Produccion)
def set_fecha_inicio_proceso(sender, instance, **kwargs):
    if instance.pk:  # Verificar si la instancia ya existe en la base de datos
        try:
            previous = Produccion.objects.get(pk=instance.pk)
            if previous.estado == '1' and instance.estado != '1':
                instance.fecha_inicio_proceso = date.today()
        except Produccion.DoesNotExist:
            # Esto manejará el caso en el que el objeto no exista, aunque esto no debería suceder
            pass

@receiver(pre_save, sender=Reproceso)
def set_fecha_inicio_reproceso(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Reproceso.objects.get(pk=instance.pk)
            if previous.estado == '0' and instance.estado != '0':
                instance.fecha_inicio_proceso = date.today()
        except Reproceso.DoesNotExist:
            # Esto manejará el caso en el que el objeto no exista, aunque esto no debería suceder
            pass

@receiver(post_save, sender = Reproceso)
def generar_numero_programa_correlativo_reproceso(sender, instance, created, **kwargs):
    if created and instance:
        # Obtener todos los números de lote existentes
        numeros_programa_existentes = Reproceso.objects.exclude(numero_programa=0).values_list('numero_programa', flat=True)
        instance.numero_programa = sugerir_numero_faltante(numeros_programa_existentes)
        # Guarda el objeto con el nuevo número de lote
        instance.save()

### FIN SIGNALS DE GESTION DE PROGRAMA ###  

### INICIO SIGNALS DE GESTION DE LOTES EN PROGRAMA ###

@receiver(post_save, sender=LotesPrograma)
def cambio_estado_lote_programa(sender, created, instance, **kwargs):
    if created and instance:
        EnvasesPatioTechadoExt.objects.filter(pk = instance.bodega_techado_ext.pk).update(estado_envase = '2')
        instance.bin_ingresado = True
        instance.save()

@receiver(post_delete, sender=LotesPrograma)
def retorno_a_bodega_tras_eliminarse_lote_programa_en_produccion(sender, instance, **kwargs):
    if instance:
        EnvasesPatioTechadoExt.objects.filter(pk = instance.bodega_techado_ext.id).update(estado_envase = '1')
        
@receiver(post_save, sender=LotesPrograma)
def actualizar_estado_envasepatiotechadoext_al_procesar_en_produccion(sender, instance, **kwargs):
    if instance.bin_procesado:
        post_save.disconnect(actualizar_estado_envasepatiotechadoext_al_procesar_en_produccion, sender=LotesPrograma)

        EnvasesPatioTechadoExt.objects.filter(pk = instance.bodega_techado_ext.pk).update(estado_envase = '3')
        instance.fecha_procesado = timezone.now()
        instance.save()
        post_save.connect(actualizar_estado_envasepatiotechadoext_al_procesar_en_produccion, sender=LotesPrograma)

            
@receiver(post_save, sender=BinsEnReproceso)
def cambio_estado_bin_bodega_al_crear_en_reproceso(sender, instance, **kwargs):
    if instance.bin_procesado:
        ## ('5', 'Procesado En Reproceso'), ##
        BinBodega.objects.filter(pk = instance.binbodega.pk).update(estado_binbodega = '5', procesado=True)
    else:
        ##     ('4', 'Ingresado En Reproceso'), ##
        BinBodega.objects.filter(pk = instance.binbodega.pk).update(estado_binbodega = '4')
   
@receiver(post_delete, sender=BinsEnReproceso)
def cambio_estado_bin_al_eliminar(sender, instance, **kwargs):
    ## ('0', 'Disponible en Bodega'), ##
    BinBodega.objects.filter(pk = instance.binbodega.pk).update(estado_binbodega = '0')

### FIN SIGNALS DE GESTION DE LOTES EN PROGRAMA ###
      
                            
### INICIO SIGNALS DE GESTION DE RESULTANTES EN PRODUCCION ###

@receiver(post_save, sender=TarjaResultante)
def vincula_resultante_bodega_g1_g2(sender, created, instance, **kwargs):
    def random_codigo_tarja(lenght=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))
    
    kilos_fruta = instance.peso - instance.tipo_patineta
    print(instance.tipo_resultante)
    if created and instance:
        if instance.tipo_resultante == '3':
            BodegaG2.objects.get_or_create(produccion=instance, kilos_fruta=kilos_fruta, calle_bodega = instance.calle_bodega)
            codigo = str('G2-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        elif instance.tipo_resultante in ['1','2','4']:
            BodegaG1.objects.get_or_create(produccion=instance, kilos_fruta=kilos_fruta, calle_bodega = instance.calle_bodega)
            codigo = str('G1-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        instance.save()
        
@receiver(post_save, sender=TarjaResultanteReproceso)
def vincula_resultante_reproceso_bodega_g1_g2(sender, created, instance, **kwargs):
    def random_codigo_tarja(lenght=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))
    
    kilos_fruta = instance.peso - instance.tipo_patineta
    if created and instance:
        if instance.tipo_resultante == '3':
            BodegaG2Reproceso.objects.update_or_create(reproceso=instance, kilos_fruta=kilos_fruta, calle_bodega = instance.calle_bodega)
            codigo = str('G2-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        elif instance.tipo_resultante in ['1','2','4']:
            BodegaG1Reproceso.objects.update_or_create(reproceso=instance, kilos_fruta=kilos_fruta, calle_bodega = instance.calle_bodega)
            codigo = str('G1-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        instance.save()

@receiver(post_save, sender=TarjaResultante)
def crear_cc_tarja_resultante_y_vincular_a_tarja(sender, instance, created, **kwargs):
    if created:
        lotes = LotesPrograma.objects.filter(produccion=instance.produccion)
        variedades_unicas = set(lotes.values_list('bodega_techado_ext__variedad', flat=True))
        variedad = 'RV' if len(variedades_unicas) > 1 else variedades_unicas.pop() if variedades_unicas else None
        CCTarjaResultante.objects.update_or_create(
            tarja=instance,
            defaults={'variedad': variedad}
        )
        if instance.tipo_resultante == '3':
            BodegaG2.objects.filter(produccion = instance).update(variedad = variedad)
        elif instance.tipo_resultante == ['1', '2', '3']:
            BodegaG1.objects.filter(produccion = instance).update(variedad = variedad)
            
@receiver(post_save, sender=TarjaResultanteReproceso)
def crear_cc_tarja_resultante_reproceso_y_vincular_a_cc(sender, instance, created, **kwargs):
    if created and instance:
        bins = BinsEnReproceso.objects.filter(reproceso=instance.reproceso)
        verdades_unicas = []
        for bin in bins:
            if bin.binbodega.tipo_binbodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso','bodegag3', 'bodegag4', 'agrupaciondebinsbodegas', 'frutasobrantedeagrupacion']:
                verdades_unicas.append(bin.binbodega.variedad_clave)
            
        variedades_unicas = set(verdades_unicas)
        variedad = 'RV' if len(variedades_unicas) > 1 else variedades_unicas.pop() if variedades_unicas else None
        CCTarjaResultanteReproceso.objects.update_or_create(
            tarja=instance,
            variedad = variedad
            ) 

### FIN SIGNALS DE GESTION DE RESULTANTES EN PRODUCCION ###