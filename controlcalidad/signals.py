from django.db.models.signals import post_save, pre_save
from .models import *
from django.dispatch import receiver
from recepcionmp.models import RecepcionMp, GuiaRecepcionMP, LoteRecepcionMpRechazadoPorCC
from bodegas.models import *
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from planta_harina.models import BinResultantePrograma, BinResultanteProceso
from django.contrib.auth.models import Group
from core.funciones_redis import *
from core.etiquetas import etiqueta_produccion, etiqueta_seleccion
from django.utils import timezone
from produccion.models import TarjaResultante, TarjaResultanteReproceso
from seleccion.estados_modelo import TIPO_RESULTANTE_SELECCION

#### INICIO SIGNALS DE CONTROL DE APROBACION LOTES EN RECEPCION ###

@receiver(post_save, sender=CCRecepcionMateriaPrima)
def comprueba_si_aprueba_cc_por_humedad_recepcionmp(sender, instance, created, **kwargs):
    recepcionmp = RecepcionMp.objects.get(pk=instance.recepcionmp.pk)
    
    if instance and created:
        pass
    else:
        if instance.humedad <= 6 and instance.estado_aprobacion_cc == '0':
            CCRecepcionMateriaPrima.objects.filter(pk=instance.pk).update(estado_cc='1')
            ctccrecepcionmp = ContentType.objects.get_for_model(CCRecepcionMateriaPrima)
            ctrecepcionmp = ContentType.objects.get_for_model(RecepcionMp)
            guiaccpatio = CCGuiaInterna.objects.update_or_create(tipo_cc_guia=ctccrecepcionmp, id_guia=instance.pk)
            guiacdcpation  = CCGuiaInterna.objects.get(pk=guiaccpatio[0].pk)
            RecepcionMp.objects.filter(pk=recepcionmp.pk).update(estado_recepcion='3') 
            guiapatioexterior = PatioTechadoExterior.objects.update_or_create(cc_guia=guiacdcpation, tipo_recepcion=ctrecepcionmp, id_recepcion=recepcionmp.pk, )
            print(f'Guia de Ingreso a Patio Techado Registrada con el N° {guiapatioexterior[0].pk}')
            if not recepcionmp.guiarecepcion.mezcla_variedades:
                GuiaRecepcionMP.objects.filter(pk=instance.recepcionmp.guiarecepcion.pk).update(estado_recepcion='3')
            else:
                GuiaRecepcionMP.objects.filter(pk=instance.recepcionmp.guiarecepcion.pk).update(estado_recepcion='2')   
        elif instance.humedad <= 6 and instance.estado_aprobacion_cc == '1':
            RecepcionMp.objects.filter(pk=recepcionmp.pk).update(estado_recepcion='7') 
        else:
            ultimo_numero_rechazo = LoteRecepcionMpRechazadoPorCC.objects.order_by('-numero_lote_rechazado').first()
            if ultimo_numero_rechazo:
                nuevo_numero_rechazo = ultimo_numero_rechazo.numero_lote_rechazado + 1
            else:
                nuevo_numero_rechazo = 1000
            CCRecepcionMateriaPrima.objects.filter(pk=instance.pk).update(estado_cc='0', estado_aprobacion_cc='2')
            RecepcionMp.objects.filter(pk=instance.recepcionmp.pk).update(estado_recepcion='4',numero_lote=0) 
            LoteRecepcionMpRechazadoPorCC.objects.create(
                recepcionmp=instance.recepcionmp, 
                rechazado_por=instance.cc_registrado_por,
                numero_lote_rechazado=nuevo_numero_rechazo
                )
            if not recepcionmp.guiarecepcion.mezcla_variedades:
                GuiaRecepcionMP.objects.filter(pk=instance.recepcionmp.guiarecepcion.pk).update(estado_recepcion='4')
            else:
                GuiaRecepcionMP.objects.filter(pk=instance.recepcionmp.guiarecepcion.pk).update(estado_recepcion='2')

#### FIN SIGNALS DE CONTROL DE APROBACION LOTES EN RECEPCION ###

#### INICIO SIGNALS DE CDC EN PLANTA DE HARINA ####
@receiver(post_save, sender=CCBinResultanteProgramaPH)
def tarjasresultantesprogramas_aprobadas_se_crean_en_binbodega(sender, instance, created, **kwargs):
    if created:
        return  # No action on creation

    if hasattr(instance, '_signal_handled'):
        return  # Exit if the signal has already been handled for this instance
    
    if instance.humedad <= 6.0 and instance.estado_cc != '1':
        instance.estado_cc = '1'
        # Mark the instance as handled before saving
        instance._signal_handled = True
        instance.save()

        # Aprobado
        bin_en_su_bodega = BodegaG6.objects.get(programa=instance.bin_resultante)
        bin_en_su_bodega.estado_bin = '1'
        bin_en_su_bodega.save(update_fields=['estado_bin'])
        BinResultantePrograma.objects.filter(programa=instance.bin_resultante.programa).update(estado_bin='2')
        ct = ContentType.objects.get_for_model(BodegaG6)
        BinBodega.objects.get_or_create(tipo_binbodega=ct, id_binbodega=bin_en_su_bodega.pk, estado_binbodega='16')

    else:
        instance.estado_cc = '2'
        # Mark the instance as handled before saving
        instance._signal_handled = True
        instance.save()

        # Rechazado
        bin_en_su_bodega = BodegaG6.objects.get(programa=instance.bin_resultante)
        bin_en_su_bodega.estado_bin = '5'
        bin_en_su_bodega.save(update_fields=['estado_bin'])
        BinResultantePrograma.objects.filter(programa=instance.bin_resultante.programa).update(estado_bin='3')


    # Solo actualiza si realmente hay campos para actualizar
    # if update_fields:
    #     CCBinResultanteProgramaPH.objects.filter(pk=instance.pk).update(**update_fields)

@receiver(post_save, sender=CCBinResultanteProcesoPH)
def tarjasresultantesproceso_aprobadas_se_crean_en_binbodega(sender, instance, created, **kwargs):
    # if created:
    #     return  # No action on creation

    # # update_fields = {}
    # if instance.humedad <= 6.0 and instance.estado_control != '1':
    #     # Aprobado
    #     #update_fields['estado_control'] = '1'
    #     bin_en_su_bodega = BodegaG7.objects.get(proceso=instance.bin_resultante)
    #     bin_en_su_bodega.estado_bin = '2'
    #     bin_en_su_bodega.save(update_fields=['estado_bin'])
    #     BinResultanteProceso.objects.filter(proceso=instance.bin_resultante.pk).update(estado_bin='2')
    #     ct = ContentType.objects.get_for_model(BodegaG7)
    #     BinBodega.objects.get_or_create(tipo_binbodega=ct, id_binbodega=bin_en_su_bodega.pk, estado_binbodega='16')

    # else:
    #     # Rechazado
    #     #update_fields['estado_control'] = '2'
    #     bin_en_su_bodega = BodegaG7.objects.get(proceso=instance.bin_resultante)
    #     bin_en_su_bodega.estado_bin = '5'
    #     bin_en_su_bodega.save(update_fields=['estado_bin'])
    #     BinResultanteProceso.objects.filter(proceso=instance.bin_resultante.proceso).update(estado_bin='3')
    
    if created:
        return  # No action on creation

    if hasattr(instance, '_signal_handled'):
        return  # Exit if the signal has already been handled for this instance
    
    if instance.humedad <= 6.0 and instance.estado_control != '1':
        instance.estado_control = '1'
        # Mark the instance as handled before saving
        instance._signal_handled = True
        instance.save()

        # Aprobado
        bin_en_su_bodega = BodegaG7.objects.get(proceso=instance.bin_resultante)
        bin_en_su_bodega.estado_bin = '1'
        bin_en_su_bodega.save(update_fields=['estado_bin'])
        BinResultanteProceso.objects.filter(proceso=instance.bin_resultante.proceso).update(estado_bin='2')
        ct = ContentType.objects.get_for_model(BodegaG7)
        BinBodega.objects.get_or_create(tipo_binbodega=ct, id_binbodega=bin_en_su_bodega.pk, estado_binbodega='16')

    else:
        instance.estado_control = '2'
        # Mark the instance as handled before saving
        instance._signal_handled = True
        instance.save()

        # Rechazado
        bin_en_su_bodega = BodegaG7.objects.get(proceso=instance.bin_resultante)
        bin_en_su_bodega.estado_bin = '5'
        bin_en_su_bodega.save(update_fields=['estado_bin'])
        BinResultanteProceso.objects.filter(proceso=instance.bin_resultante.proceso).update(estado_bin='3')

    # Solo actualiza si realmente hay campos para actualizar y evitar llamadas innecesarias a save()
    # if update_fields:
    #     CCBinResultanteProcesoPH.objects.filter(pk=instance.pk).update(**update_fields)
     
#### FIN SIGNALS DE CDC EN PLANTA DE HARINA ####

#### CONTROLES DE CALIDAD DE PRODUCCION, REPROCESO ####

@receiver(post_save, sender=CCTarjaResultante)
def actualizar_info_validada_cdc_tarja_resultante_programa_produccion_en_bodega(sender, instance, created, **kwargs):   
    if instance.estado_cc == '3' and not created:
        kilosnetos = instance.tarja.peso - instance.tarja.tipo_patineta
        # etiqueta_produccion(variedad=instance.get_variedad_display(), pkprograma=instance.tarja.produccion.pk, codigo_tarja=instance.tarja.codigo_tarja, kilos_fruta=kilosnetos, calibre=instance.get_calibre_display(), fecha_programa=str(instance.tarja.produccion.fecha_creacion), fecha=str(instance.tarja.fecha_modificacion))
        resultante = instance.tarja.tipo_resultante
        if resultante in ['1', '2', '4']:
            bodega = BodegaG1.objects.filter(produccion=instance.tarja.pk).first()
            BodegaG1.objects.filter(produccion=instance.tarja.pk).update(
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            ct = ContentType.objects.get_for_model(bodega)
            ## ('16', 'Calibrado x CDC'),
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
        elif resultante == '3':
            bodega = BodegaG2.objects.filter(produccion=instance.tarja.pk).first()
            BodegaG2.objects.filter(produccion=instance.tarja.pk).update(
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            ct = ContentType.objects.get_for_model(bodega)
            ## ('16', 'Calibrado x CDC'),
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
        
        tarja = TarjaResultante.objects.filter(pk=instance.tarja.pk)
        tarja.update(fecha_cc_tarja=timezone.now())
        datos_tarja = tarja.first()
        kilosnetos = datos_tarja.peso - datos_tarja.tipo_patineta
        etiqueta_produccion(variedad=instance.get_variedad_display(), codigo_tarja=datos_tarja.codigo_tarja, pkprograma=datos_tarja.produccion.pk, kilos_fruta=kilosnetos, calibre=instance.get_calibre_display(), fecha=str(datos_tarja.fecha_creacion), fecha_programa=str(datos_tarja.produccion.fecha_inicio_proceso))
                   
@receiver(post_save, sender=CCTarjaResultanteReproceso)
def actualizar_info_validada_cdc_tarja_resultante_programa_reproceso_en_bodega(sender, instance, created, **kwargs):   
    if instance.estado_cc == '3' and not created:
        resultante = instance.tarja.tipo_resultante
        if resultante in ['1', '2', '4']:
            bodega = BodegaG1Reproceso.objects.filter(reproceso=instance.tarja.pk).first()
            BodegaG1Reproceso.objects.filter(reproceso=instance.tarja.pk).update(
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            ct = ContentType.objects.get_for_model(bodega)
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
        elif resultante == '3':
            bodega = BodegaG2Reproceso.objects.filter(reproceso=instance.tarja.pk).first()
            BodegaG2Reproceso.objects.filter(reproceso=instance.tarja.pk).update(
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            ct = ContentType.objects.get_for_model(bodega)
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
        tarja = TarjaResultanteReproceso.objects.filter(pk=instance.tarja.pk)
        tarja.update(fecha_cc_tarja=timezone.now())  
        datos_tarja = tarja.first()
        kilosnetos = datos_tarja.peso - datos_tarja.tipo_patineta
        programareproceso = f'{datos_tarja.reproceso.pk} R'
        etiqueta_produccion(variedad=instance.get_variedad_display(), codigo_tarja=datos_tarja.codigo_tarja, pkprograma=programareproceso, kilos_fruta=kilosnetos, calibre=instance.get_calibre_display(), fecha=str(datos_tarja.fecha_creacion), fecha_programa=str(datos_tarja.reproceso.fecha_inicio_proceso))    
            
### CONTROLES DE CALIDAD DE SELECCION ###

@receiver(post_save, sender=CCTarjaSeleccionada)
def actualizar_info_validada_cdc_tarja_seleccionada_en_bodega(sender, instance, created, **kwargs):   
    if instance.estado_cc == '3' and not created:
        
        resultante = instance.tarja_seleccionada.tipo_resultante
        if resultante == '2':
            bodega =  BodegaG4.objects.filter(seleccion=instance.tarja_seleccionada.pk).first()
            tarja = BodegaG4.objects.filter(seleccion=instance.tarja_seleccionada.pk)
            tarja.update(
                calidad=instance.calidad_fruta,
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            ct = ContentType.objects.get_for_model(bodega)
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
            tarja.update(
                calidad=instance.calidad_fruta,
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            datos_tarja = tarja.first()
            kilosnetos = datos_tarja.seleccion.peso - datos_tarja.seleccion.tipo_patineta
            tipo_resultante = TIPO_RESULTANTE_SELECCION[int(resultante)-1][1]
            calidad = instance.get_calidad_fruta_display()
            if instance.picada < 25 and instance.variedad == 'NP':
                calidad = 'Extra N°1'
            elif instance.picada >= 25 and instance.variedad == 'NP':
                calidad = 'Supreme'
                
            print(f"IMPRIMIENDO TARJA {datos_tarja.seleccion.codigo_tarja} calidad es {calidad} estado es {instance.estado_cc}")
            etiqueta_seleccion(variedad=instance.get_variedad_display(), codigo_tarja=datos_tarja.seleccion.codigo_tarja, pk=datos_tarja.seleccion.seleccion.pk, kilos_fruta=kilosnetos, calibre=calidad,calidad=instance.get_calidad_fruta_display(), fecha=str(datos_tarja.fecha_creacion), fecha_programa=str(datos_tarja.seleccion.seleccion.fecha_inicio_proceso), tipo_fruta=tipo_resultante)
        elif resultante == '1':
            bodega =  BodegaG3.objects.filter(seleccion=instance.tarja_seleccionada.pk).first()
            tarja = BodegaG3.objects.filter(seleccion=instance.tarja_seleccionada.pk)
            tarja.update(
                calidad=instance.calidad_fruta,
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            ct = ContentType.objects.get_for_model(bodega)
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
            tarja.update(
                calidad=instance.calidad_fruta,
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            datos_tarja = tarja.first()
            kilosnetos = datos_tarja.seleccion.peso - datos_tarja.seleccion.tipo_patineta
            tipo_resultante = TIPO_RESULTANTE_SELECCION[int(resultante)-1][1]
            etiqueta_seleccion(variedad=instance.get_variedad_display(), codigo_tarja=datos_tarja.seleccion.codigo_tarja, pk=datos_tarja.seleccion.seleccion.pk, kilos_fruta=kilosnetos, calibre=instance.get_calibre_display(),calidad=instance.get_calidad_fruta_display(), fecha=str(datos_tarja.fecha_creacion), fecha_programa=str(datos_tarja.seleccion.seleccion.fecha_inicio_proceso), tipo_fruta=tipo_resultante)
            
        elif resultante == '3':
            bodega =  BodegaG5.objects.filter(seleccion=instance.tarja_seleccionada.pk).first()
            tarja = BodegaG5.objects.filter(seleccion=instance.tarja_seleccionada.pk)
            tarja.update(
                calidad=instance.calidad_fruta,
                variedad=instance.variedad,
                calibre=instance.calibre,
            )
            datos_tarja = tarja.first()
            kilosnetos = datos_tarja.seleccion.peso - datos_tarja.seleccion.tipo_patineta
            tipo_resultante = TIPO_RESULTANTE_SELECCION[int(resultante)-1][1]
            etiqueta_seleccion(variedad=instance.get_variedad_display(), codigo_tarja=datos_tarja.seleccion.codigo_tarja, pk=datos_tarja.seleccion.seleccion.pk, kilos_fruta=kilosnetos, calibre=instance.get_calibre_display(),calidad=instance.get_calidad_fruta_display(), fecha=str(datos_tarja.fecha_creacion), fecha_programa=str(datos_tarja.seleccion.seleccion.fecha_inicio_proceso), tipo_fruta=tipo_resultante)
            ct = ContentType.objects.get_for_model(bodega)
            BinBodega.objects.get_or_create(tipo_binbodega = ct, id_binbodega = bodega.pk, estado_binbodega = '16')
        
