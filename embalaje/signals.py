from django.db.models.signals import post_save, pre_delete, pre_save, post_delete
from django.dispatch import receiver
from .models import *
from simple_history.utils import update_change_reason
from django.db import transaction
from django.db.models import Sum, F
from datetime import timedelta
from .funciones import *




@receiver(post_save, sender = FrutaBodega)
def cambiar_estado_a_binbodega(sender, created, instance, **kwargs):
  ## esto se debera cambiar en algun minuto por los estados, por ahora lo haremos con ingresado
  if created:
    BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '8')
  elif instance.procesado != False:
    BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '9', procesado = True)
    
@receiver(pre_delete, sender = FrutaBodega)
def cambiar_estado_a_bin_bodega_posterior_a_eliminacion(sender, instance, **kwargs):
  BinBodega.objects.filter(pk = instance.bin_bodega.pk).update(estado_binbodega = '16')
  
  
@receiver(pre_delete, sender = Embalaje)
def cambiar_estado_a_bin_bodega_posterior_a_eliminacion(sender, instance, **kwargs):
  for fruta in instance.frutabodega_set.all():
    BinBodega.objects.filter(pk = fruta.pk).update(estado_binbodega = '16')
    
    
@receiver(post_save, sender = PalletProductoTerminado)
def cambiar_razon_para_el_historico(sender, created, instance, **kwargs):
  if created and instance:
        change_reason = f'Se ha creado el pallet {instance.codigo_pallet}'
        update_change_reason(instance, change_reason)
        
        
from datetime import date 
@receiver(pre_save, sender=Embalaje)
def set_fecha_inicio_embalaje(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Embalaje.objects.get(pk=instance.pk)
            if previous.estado_embalaje == '1' and instance.estado_embalaje != '1':
                instance.fecha_inicio_embalaje = date.today()
        except Embalaje.DoesNotExist:
            pass
              

@receiver(pre_save, sender=PalletProductoTerminado)
def capture_old_values(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = PalletProductoTerminado.objects.get(pk=instance.pk)
        instance._old_instance = old_instance
    except PalletProductoTerminado.DoesNotExist:
        instance._old_instance = None

            
@receiver(post_save, sender=PalletProductoTerminado)
def set_change_reason(sender, instance, **kwargs):
    if not hasattr(instance, '_old_instance') or not instance._old_instance:
        return

    old_instance = instance._old_instance
    changes = []
    fields_to_check = [
        'numero_pallet', 'calle_bodega', 'observaciones', 'codigo_pallet'
    ]
    
    for field in fields_to_check:
        old_value = getattr(old_instance, field, None)  
        new_value = getattr(instance, field, None)      

        if field == 'calle_bodega':
            field_choices = dict(instance._meta.get_field(field).choices)
            old_value_label = field_choices.get(old_value, old_value)
            new_value_label = field_choices.get(new_value, new_value)
        else:
            old_value_label = old_value
            new_value_label = new_value
        

        print(f'Checking field {field}: old_value = {old_value_label}, new_value = {new_value_label}')
        
        if old_value != new_value:
            changes.append(f'{field} cambió de {old_value_label} a {new_value_label}')
                
    if changes:
        change_reason = '; '.join(changes)
        update_change_reason(instance, change_reason)  
    else:
        print("No changes detected")  # For debugging


@receiver(post_save, sender=CajasEnPalletProductoTerminado)
def update_change_reason_on_add(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            pallet = instance.pallet
            if not pallet:
                return
            change_reason = f"Se ha agregado una caja: Tipo de caja: {instance.tipo_caja}, " \
                            f"Cantidad de cajas: {instance.cantidad_cajas}, Peso por caja: {instance.peso_x_caja} Kgs"
            update_change_reason(pallet, change_reason)
            pallet.save()  # Guardar para asegurar una nueva entrada de historial

@receiver(pre_delete, sender=CajasEnPalletProductoTerminado)
def update_change_reason_when_was_deleted(sender, instance, **kwargs):
    with transaction.atomic():
        pallet = instance.pallet
        if not pallet:
            return
        change_reason = f"Se ha eliminado una caja: Tipo de caja: {instance.tipo_caja}, " \
                        f"Cantidad de cajas: {instance.cantidad_cajas}, Peso por caja: {instance.peso_x_caja} Kgs"
        update_change_reason(pallet, change_reason)
        pallet.save()  # Guardar para asegurar una nueva entrada de historial
        

@receiver(pre_save, sender=CajasEnPalletProductoTerminado)
def capture_peso_anterior_cajas(sender, instance, **kwargs):
    pallet = instance.pallet
    if not pallet:
        return
    
    # Evitar capturar el peso si ya se ha hecho en este ciclo
    if hasattr(pallet, '_captured_peso'):
        return  # Ya capturamos el peso

    # Capturamos el peso total del pallet antes de modificar las cajas
    pallet._old_peso_total = pallet.peso_total_pallet
    pallet._captured_peso = True  
    print(f"Peso total antes de modificar cajas: {pallet._old_peso_total}")
    
@receiver(post_save, sender=CajasEnPalletProductoTerminado)
def actualizar_peso_inicial_post_cajas(sender, instance, **kwargs):
    pallet = instance.pallet
    if not pallet:
        return

    # Peso total después de modificar las cajas
    peso_actual = pallet.peso_total_pallet
    print(f"Peso total después de modificar cajas: {peso_actual}")
    # Si el peso ha disminuido y el peso inicial aún no está definido o es menor
    print(f"Peso anterior es {pallet._old_peso_total} y peso actual es {peso_actual}")
    if hasattr(pallet, '_old_peso_total'):
        print(f"ENTRA")
        if peso_actual < pallet._old_peso_total:
            print(f"Peso inicial es {pallet.peso_inicial}")
            if pallet.peso_inicial is None:
                print(f"Peso inicial actualizado de {pallet.peso_inicial} a {pallet._old_peso_total}")
                pallet.peso_inicial = pallet._old_peso_total
                pallet.save(update_fields=['peso_inicial'])
    
    # Marcamos que ya actualizamos el peso en este ciclo
    pallet._peso_actualizado = True
                


# @receiver(post_save, sender=Embalaje)
# def asignar_kilos_operarios_embalaje(sender, instance, created, **kwargs):
#     if created:
#         return  # No ejecutar lógica adicional si el objeto acaba de ser creado

#     if instance.estado_embalaje == '5' and instance.fecha_inicio_embalaje and instance.fecha_termino_embalaje:
#         # Calcular los días de producción excluyendo los fines de semana
#         dias_produccion = calcular_dias_habiles(instance.fecha_inicio_embalaje, instance.fecha_termino_embalaje)

#         # Sumar los kilos netos de todos los bins resultantes
#         kilos_bins = 0
#         for fruta in FrutaBodega.objects.filter(embalaje = instance):
#             kilos_bins += fruta.bin_bodega.binbodega.kilos_fruta

#         num_operarios = max(instance.operariosenembalaje_set.count(), 1)
#         kilos_por_dia = round(kilos_bins / dias_produccion, 2) if dias_produccion else 0
#         kilos_por_operario_por_dia = round(kilos_por_dia / num_operarios, 2)

#         # Asignar los kilos a cada operario por día hábil
#         fecha_actual = instance.fecha_inicio_embalaje
#         while fecha_actual <= instance.fecha_termino_embalaje:
#             if fecha_actual.weekday() < 5:  # Días hábiles de lunes a viernes
#                 asignar_operarios_embalaje(instance, fecha_actual, kilos_por_operario_por_dia)
#             fecha_actual += timedelta(days=1)

# def asignar_operarios_embalaje(embalaje, fecha_operario, kilos_por_operario):
#     operarios_asignados = OperariosEnEmbalaje.objects.filter(embalaje=embalaje)
#     for operario_asignado in operarios_asignados:
#         operario_existente = OperariosEnEmbalaje.objects.filter(
#             embalaje=embalaje, operario=operario_asignado.operario, dia=fecha_operario
#         ).first()
#         if operario_existente:
#             operario_existente.kilos = kilos_por_operario
#             operario_existente.save()
#         else:
#             OperariosEnEmbalaje.objects.update_or_create(
#                 embalaje=embalaje,
#                 operario=operario_asignado.operario,
#                 kilos=kilos_por_operario,
#                 dia=fecha_operario
#             )     
        
# def calcular_dias_habiles(fecha_inicio, fecha_fin):
#     dias_habiles = 0
#     fecha_actual = fecha_inicio
#     while fecha_actual <= fecha_fin:
#         if fecha_actual.weekday() < 5:  # De lunes a viernes
#             dias_habiles += 1
#         fecha_actual += timedelta(days=1)
#     return dias_habiles



# @receiver(post_save, sender=FrutaBodega)
# def registrar_tipo_de_variedad_calidad_calibre_de_programa(sender, instance: FrutaBodega, created, **kwargs):
#     if created:
#         variedad = obtener_variedad_id(instance)
#         calidad = obtener_calidad_id(instance)
#         calibre = obtener_calibre_id(instance)
        
#         print(variedad)
#         print(calidad)
#         print(calibre)
#         codigo_tarja = obtener_codigo_tarja(instance)
#         tipo_producto = None
#         if codigo_tarja.startswith('G1'):
#             tipo_producto = '1'
#         elif codigo_tarja.startswith('G2'):
#             tipo_producto = '1'
#         elif codigo_tarja.startswith('G3'):
#             tipo_producto = '1'
#         elif codigo_tarja.startswith('G4'):
#             tipo_producto = '1'
#         elif codigo_tarja.startswith('G5'):
#             tipo_producto = '1'
#         elif codigo_tarja.startswith('G6'):
#             tipo_producto = '2'
#         elif codigo_tarja.startswith('G7'):
#             tipo_producto = '3'
        
#         Embalaje.objects.filter(pk = instance.embalaje.pk).update(variedad = variedad, calibre = calibre, calidad = calidad, tipo_producto = tipo_producto)
        
        
    #     pass
    # elif instance.estado_embalaje == '1':
    #     codigo_tarja = obtener_codigo_tarja(codigo_tarja)
    #     variedades_unicas = set([obtener_variedad(bin) for bin in FrutaBodega.objects.filter(embalaje = instance)])
    #     variedad = 'Revueltas' if len(variedades_unicas) > 1 else variedades_unicas.pop()
    #     calibres_unicos = set([obtener_calibre(bin) for bin in FrutaBodega.objects.filter(embalaje = instance)])
    #     calibre = 'Indefinido' if len(calibres_unicos) > 1 else calibres_unicos.pop()
    #     calidades_unicas = set([obtener_calidad(bin) for bin in FrutaBodega.objects.filter(embalaje = instance)])
    #     calidad = 'Indefinido' if len(calidades_unicas) > 1 else calibres_unicos.pop()
    #     instance.calibre = calidad
    #     instance.variedad = variedad
    #     instance.calibre = calibre
    #     if codigo_tarja.startswith('G1'):
    #         instance.tipo_producto = '1'
    #     elif codigo_tarja.startswith('G2'):
    #         instance.tipo_producto = '1'
    #     elif codigo_tarja.startswith('G3'):
    #         instance.tipo_producto = '1'
    #     elif codigo_tarja.startswith('G4'):
    #         instance.tipo_producto = '1'
    #     elif codigo_tarja.startswith('G5'):
    #         instance.tipo_producto = '1'
    #     elif codigo_tarja.startswith('G6'):
    #         instance.tipo_producto = '2'
    #     elif codigo_tarja.startswith('G7'):
    #         instance.tipo_producto = '3'
        
    #     instance.save()
    
        