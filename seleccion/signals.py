from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from .models import *
from controlcalidad.models  import *
from django.dispatch import receiver
from datetime import datetime
from bodegas.models import *
import random, string
from bodegas.models import BodegaG3, BodegaG4
from django.contrib.contenttypes.models import ContentType
from simple_history.utils import update_change_reason
from datetime import timedelta
from django.db.models import Sum, F
from recepcionmp.signals import sugerir_numero_faltante
from datetime import date

def random_codigo_tarja(lenght=6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))


@receiver(pre_save, sender=Seleccion)
def set_fecha_inicio_seleccion(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Seleccion.objects.get(pk=instance.pk)
            if previous.estado_programa == '1' and instance.estado_programa != '1':
                instance.fecha_inicio_proceso = date.today()
        except Seleccion.DoesNotExist:
            pass

@receiver(post_save, sender = Seleccion)
def generar_numero_programa_correlativo(sender, instance, created, **kwargs):
    if created and instance:
        # Obtener todos los números de lote existentes
        numeros_programa_existentes = Seleccion.objects.exclude(numero_programa__isnull=True).values_list('numero_programa', flat=True)
        instance.numero_programa = sugerir_numero_faltante(numeros_programa_existentes)
        # Guarda el objeto con el nuevo número de lote
        instance.save()

@receiver(post_save, sender=BinsPepaCalibrada)
def cambia_estado_bin_bodega_cuando_ingresa_fruta_a_seleccion(sender, instance, created, **kwargs):
    ## ('6', 'Ingresado En Selección'), ##
    instance.binbodega.estado_binbodega = '6'
    instance.binbodega.ingresado = True
    instance.binbodega.save()

@receiver(post_delete, sender=BinsPepaCalibrada)
def retorna_estado_bin_bodega_cuando_se_saca_de_la_fruta_programa(sender, instance, **kwargs):
    if not instance.bin_procesado:
        ## ('16', 'Calibrado x CDC'), ##
        instance.binbodega.estado_binbodega = '16'
        instance.binbodega.save()
    
@receiver(post_save, sender=BinsPepaCalibrada)
def cambia_estado_bin_bodega_cuando_se_procesa_fruta_a_seleccion(sender, instance, created, **kwargs):
    if instance.bin_procesado:
        ## ('7', 'Procesado En Selección'), ##
        instance.binbodega.estado_binbodega = '7'
        instance.binbodega.procesado = True
        instance.binbodega.save()

@receiver(post_save, sender=TarjaSeleccionada)
def vincula_seleccionada_a_bodega_g3_g4(sender, created, instance, **kwargs): # type: ignore
    def random_codigo_tarja(lenght=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))
    kilos_fruta = instance.peso - instance.tipo_patineta
    if created and instance:
        if instance.tipo_resultante == '2':
            BodegaG4.objects.update_or_create(seleccion=instance, kilos_fruta=kilos_fruta)
            codigo = str('G4-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        elif instance.tipo_resultante == '1':
            BodegaG3.objects.update_or_create(seleccion=instance, kilos_fruta=kilos_fruta)
            codigo = str('G3-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        elif instance.tipo_resultante == '3':
            BodegaG5.objects.update_or_create(seleccion=instance, kilos_fruta=kilos_fruta)
            codigo = str('G5-')+random_codigo_tarja()
            instance.codigo_tarja = codigo
        instance.save()
        
@receiver(post_save, sender=TarjaSeleccionada)
def crear_cc_tarja_seleccionada_y_vincular_a_tarja(sender, instance, created, **kwargs):   
    if instance.tipo_resultante in ['1', '2', '3'] and created:
        variedades = []
        bins_en_seleccion = BinsPepaCalibrada.objects.filter(seleccion= instance.seleccion)
        for bin in bins_en_seleccion:
            variedades.append(bin.binbodega.variedad_clave)
        variedades_unicas = set(variedades)
        variedad = 'RV' if len(variedades_unicas) > 1 else variedades_unicas.pop() if variedades_unicas else None
        CCTarjaSeleccionada.objects.get_or_create(tarja_seleccionada = instance, variedad = variedad)
      
@receiver(post_save, sender=BinSubProductoSeleccion)
def vincula_seleccionada_a_bodega_g3_g4(sender, instance, created, **kwargs):
    if created and instance:
        ct = ContentType.objects.get_for_model(instance)
        BinBodega.objects.update_or_create(tipo_binbodega=ct, id_binbodega=instance.pk)
        codigo = 'G4-' + random_codigo_tarja()
        instance.codigo_tarja = codigo
        instance.save()
        change_reason = f'Se ha creado el bin {codigo}'
        update_change_reason(instance, change_reason)
        
@receiver(post_save, sender=SubproductosEnBin)
def update_change_reason_on_add(sender, instance, **kwargs):
    try:
        bin  = BinSubProductoSeleccion.objects.get(pk = instance.bin_subproducto.pk)
        change_reason = f"Se ha agregado un subproducto: Operario: {instance.subproducto_operario.operario.nombre} {instance.subproducto_operario.operario.apellido}, Kilos: {instance.subproducto_operario.peso}, Programa: {instance.subproducto_operario.seleccion}"
        update_change_reason(bin, change_reason)
    except:
        print("ERROR NO PASO")
        
@receiver(pre_save, sender=BinSubProductoSeleccion)
def capture_old_values(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = BinSubProductoSeleccion.objects.get(pk=instance.pk)
        instance._old_instance = old_instance
    except BinSubProductoSeleccion.DoesNotExist:
        instance._old_instance = None
            
@receiver(post_save, sender=BinSubProductoSeleccion)
def set_change_reason(sender, instance, **kwargs):
    if not hasattr(instance, '_old_instance') or not instance._old_instance:
        return

    old_instance = instance._old_instance
    changes = []
    fields_to_check = [
        'tipo_patineta', 'cc_subproducto', 'fecha_cc_subproducto', 'variedad', 
        'calibre', 'calidad', 'fumigado', 'codigo_tarja', 'ubicacion', 
        'calle_bodega', 'tipo_subproducto', 'estado_bin', 'agrupado'
    ]
    
    for field in fields_to_check:
        old_value = getattr(old_instance, field)
        new_value = getattr(instance, field)

        # Obtener los labels de los choices
        if field in ['tipo_patineta', 'variedad', 'calibre', 
                     'calidad', 'ubicacion', 'calle_bodega', 'tipo_subproducto', 'estado_bin']:
            field_choices = dict(instance._meta.get_field(field).choices)
            old_value_label = field_choices.get(old_value, old_value)
            new_value_label = field_choices.get(new_value, new_value)
        else:
            old_value_label = old_value
            new_value_label = new_value
        
        
        if old_value != new_value:
            changes.append(f'{field} cambió de {old_value_label} a {new_value_label}')
                
    if changes:
        change_reason = '; '.join(changes)
        update_change_reason(instance, change_reason)  # Asegúrate de pasar 'instance' y no 'bin'
    else:
        print("No changes detected")  # Para depuración

