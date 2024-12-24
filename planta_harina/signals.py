from django.db.models.signals import post_save, pre_save, pre_delete
from .models import *
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
import math, random, string
from bodegas.models import *
from django.db.models import *
from datetime import timedelta
from controlcalidad.models import CCBinResultanteProgramaPH, CCBinResultanteProcesoPH
from datetime import date

        
@receiver(post_save, sender=BinResultantePrograma)
def vincula_resultante_programaph_bodega_g6(sender, created, instance, **kwargs):
    def random_codigo_tarja(length=6):
        """Genera un código alfanumérico aleatorio para usar como código de tarja."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if created:
        # Calcular los kilos de fruta restando el peso de la patineta
        kilos_fruta = instance.peso - instance.tipo_patineta
        
        # Crear o actualizar el registro en BodegaG6
        bodega_g6, _ = BodegaG6.objects.get_or_create(programa=instance, defaults={'kilos_fruta': kilos_fruta}, calle_bodega = instance.calle_bodega)
        
        # Generar un nuevo código de tarja solo si es necesario
        tipo_programa = instance.programa.tipo_programa
        if tipo_programa == 'repelado':
            instance.tipo_resultante = 'A'
        else:
            instance.tipo_resultante = 'B'
        if not instance.codigo_tarja:
            codigo = 'G6-' + random_codigo_tarja()
            
            instance.codigo_tarja = codigo
            instance.save()
        
        # Crear o verificar la existencia de un registro en CCBinResultanteProgramaPH
        CCBinResultanteProgramaPH.objects.get_or_create(bin_resultante=instance)
        
        
@receiver(post_save, sender=BinResultantePrograma)
def vincular_bin_agrupado_a_bodega_g6(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        binsparaprograma = BinParaPrograma.objects.filter(programa = instance.programa)
        calidades = [bin.bin_bodega.binbodega.calidad for bin in binsparaprograma]
        calidades_unicas = set(calidades)
        calidad = '3' if len(calidades_unicas) > 1 else calidades_unicas.pop() if calidades_unicas else None
        BodegaG6.objects.filter(programa = instance).update(calidad = calidad)
        

@receiver(pre_save, sender=ProgramaPH)
def set_fecha_inicio_programa_ph(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = ProgramaPH.objects.get(pk=instance.pk)
            if previous.estado_programa == '1' and instance.estado_programa != '1':
                instance.fecha_inicio_programa = date.today()
        except ProgramaPH.DoesNotExist:
            pass

@receiver(pre_save, sender=ProcesoPH)
def set_fecha_inicio_proceso_ph(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = ProcesoPH.objects.get(pk=instance.pk)
            if previous.estado_proceso == '1' and instance.estado_proceso != '1':
                instance.fecha_inicio_proceso = date.today()
        except ProcesoPH.DoesNotExist:
            pass
              
   
@receiver(post_save, sender=ProgramaPH)
def vincula_variables_al_programaph(sender, created, instance, **kwargs):
    if created and instance:
        VariablesProgramaPH.objects.get_or_create(programa=instance)
        
@receiver(post_save, sender=ProcesoPH)
def vincula_variables_al_procesoph(sender, created, instance, **kwargs):
    if created and instance:
        VariablesProcesoPH.objects.get_or_create(proceso=instance)
        
        
@receiver(post_save, sender=BinResultanteProceso)
def vincula_resultante_procesoph_bodega_g7(sender, created, instance, **kwargs):
    def random_codigo_tarja(length=6):
        """Genera un código alfanumérico aleatorio para usar como código de tarja."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    if created:
        # Calcular los kilos de fruta restando el peso de la patineta
        kilos_fruta = instance.peso - instance.tipo_patineta
        
        # Crear o actualizar el registro en BodegaG6
        bodega_g7, _ = BodegaG7.objects.get_or_create(proceso=instance, defaults={'kilos_fruta': kilos_fruta}, calle_bodega = instance.calle_bodega)
        
        tipo_proceso = instance.proceso.tipo_proceso
        if not instance.codigo_tarja and not instance.tipo_resultante:
            codigo = 'G7-' + random_codigo_tarja()
            instance.codigo_tarja = codigo
            instance.tipo_resultante = tipo_proceso
            instance.save()
        
        # Crear o verificar la existencia de un registro en CCBinResultanteProgramaPH
        CCBinResultanteProcesoPH.objects.get_or_create(bin_resultante=instance)
        
        
@receiver(post_save, sender = BinParaPrograma)
def cambiar_estado_binbodega(sender, instance, created, **kwargs):
    if created:
        BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '17', ingresado = True)
    elif instance.procesado:
        BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '18', procesado = True)
        
@receiver(pre_delete, sender = BinParaPrograma)
def cambiar_estado_binbodega_cuando_se_elimina(sender, instance, **kwargs):
    BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '16', ingresado = False)
    
    
@receiver(post_save, sender = BinsParaProceso)
def cambiar_estado_binbodega(sender, instance, created, **kwargs):
    if created:
        BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '19', ingresado = True)
    elif instance.procesado:
        BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '20', procesado = True)
        
@receiver(pre_delete, sender = BinsParaProceso)
def cambiar_estado_binbodega_cuando_se_elimina(sender, instance, **kwargs):
    BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '16', ingresado = False)
    
    
    
    

    