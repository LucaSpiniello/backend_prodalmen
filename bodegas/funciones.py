from bodegas.models import BinBodega
from controlcalidad.models import CCTarjaResultante, CCTarjaResultanteReproceso, CCTarjaSeleccionada
from recepcionmp.models import *
from django.db.models import Count, Sum, Avg, FloatField, F
from django.contrib.contenttypes.models import *


def calcula_peso_envases(pklote):
    peso = EnvasesGuiaRecepcionMp.objects.filter(recepcionmp = pklote).aggregate(peso_envases=Sum(F('envase__peso')*F('cantidad_envases'), output_field=FloatField()))['peso_envases']    
    return peso


def total_envases_lote(pklote):
    lote = RecepcionMp.objects.get(pk=pklote)
    envases = lote.envasesguiarecepcionmp_set.filter(recepcionmp=pklote).aggregate(total_envases=Sum('cantidad_envases'))['total_envases']
    return envases

def get_tipo_binbodega(bin):
    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4', 'bodegag5', 'bodegag6', 'bodegag7', 'agrupaciondebinsbodegas', 'binsubproductoseleccion']:
        return bin.tipo_binbodega.model
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4', 'bodegag5', 'bodegag6', 'bodegag7','agrupaciondebinsbodegas', 'binsubproductoseleccion']:
            return bin.tipo_binbodega.model
        elif bin.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
            if bin.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4', 'bodegag5', 'bodegag6', 'bodegag7', 'agrupaciondebinsbodegas', 'binsubproductoseleccion']:
                return bin.binbodega.tarja.tipo_tarja.model

def get_cc_tarja(bin):
    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
        cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.binbodega.produccion).first()
        return f'{cc_tarja.get_variedad_display()} - {cc_tarja.get_calibre_display()}'
    elif bin.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        cc_tarja_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja = bin.binbodega.reproceso).first()
        return f'{cc_tarja_reproceso.get_variedad_display()} - {cc_tarja_reproceso.get_calibre_display()}'
    elif bin.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja_seleccion = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.binbodega.seleccion).first()
        return f'{cc_tarja_seleccion.get_variedad_display()} - {cc_tarja_seleccion.get_calidad_fruta_display()}'  
    elif bin.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
        return f'Sin variedad / Sin calidad'
    elif bin.tipo_binbodega.model == 'binsubproductoseleccion':
        return f'{bin.bin_bodega.binbodega.get_variedad_display()} - {bin.bin_bodega.binbodega.get_calidad_display()}'
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
        mayor_valor = 0
        bin_con_mas_kilos = None
        for x in bin.binbodega.binsparaagrupacion_set.all():
            if x.tarja.kilos_fruta > mayor_valor:
                mayor_valor = x.tarja.kilos_fruta
                if mayor_valor == x.tarja.kilos_fruta:
                    bin_con_mas_kilos = x.tarja
        ct = ContentType.objects.get_for_model(bin_con_mas_kilos)
        if ct.model in ['bodegag1', 'bodegag2']:
            cc_tarja = CCTarjaResultante.objects.filter(tarja = bin_con_mas_kilos.produccion).first()
            return f'{cc_tarja.get_variedad_display()} - {cc_tarja.get_calibre_display()}'
        elif ct.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            cc_tarja_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja = bin_con_mas_kilos.reproceso).first()
            return f'{cc_tarja_reproceso.get_variedad_display()} - {cc_tarja_reproceso.get_calibre_display()}'
        elif ct.model in ['bodegag3', 'bodegag4', 'bodegag5']:
            cc_tarja_seleccion = CCTarjaResultanteReproceso.objects.filter(tarja_seleccionada = bin_con_mas_kilos.seleccion).first()
            return f'{cc_tarja_seleccion.get_variedad_display()} - {cc_tarja_seleccion.get_calidad_fruta_display()}'
        elif ct.model == ['bodegag6', 'bodegag7']:
            return f'Sin variedad / Sin calidad'
        elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
            if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.binbodega.tarja.produccion).first()
                return f'{cc_tarja.get_variedad_display()} - {cc_tarja.get_calibre_display()}'
            elif bin.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                cc_tarja_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja = bin.binbodega.tarja.reproceso).first()
                return f'{cc_tarja_reproceso.get_variedad_display()} - {cc_tarja_reproceso.get_calibre_display()}'
            elif bin.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
                cc_tarja_seleccionada = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.binbodega.tarja.seleccion).first()
                return f'{cc_tarja_seleccionada.get_variedad_display()} - {cc_tarja_seleccionada.get_calidad_fruta_display()}'
            elif ct.model in ['bodegag6', 'bodegag7']:
                return f'Sin variedad / Sin calidad'
               
            elif bin.binbodega.tipo_tarja.model in ['agrupaciondebinsbodegas', 'binsubproductoseleccion']:
                mayor_valor = 0
                bin_con_mas_kilos = None
                for x in bin.binbodega.binsparaagrupacion_set.all():
                    if x.tarja.kilos_fruta > mayor_valor:
                        mayor_valor = x.tarja.kilos_fruta
                        if mayor_valor == x.tarja.kilos_fruta:
                            bin_con_mas_kilos = x.tarja
                ct = ContentType.objects.get_for_model(bin_con_mas_kilos)
                if ct.model in ['bodegag1', 'bodegag2']:
                    cc_tarja = CCTarjaResultante.objects.filter(tarja = bin_con_mas_kilos.produccion).first()
                    return f'{cc_tarja.get_calibre_display()}'
                elif ct.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                    cc_tarja_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja = bin_con_mas_kilos.reproceso).first()
                    return f'{cc_tarja_reproceso.get_calibre_display()}'
                elif ct.model in ['bodegag3', 'bodegag4', 'bodegag5']:
                    cc_tarja_seleccion = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin_con_mas_kilos.seleccion).first()
                    return f'{cc_tarja_seleccion.get_calidad_fruta_display()}' 

def get_programa(bin):
    if bin.tipo_binbodega.model in ['bodegag1','bodegag2']:
        if bin.binbodega.produccion:
            return f'Producción N° {bin.binbodega.produccion.produccion.pk}'
    elif bin.tipo_binbodega.model in ['bodegag1reproceso','bodegag2reproceso']:
        if bin.binbodega.reproceso:
            return f'Reproceso N° {bin.binbodega.reproceso.reproceso.pk}'
    elif bin.tipo_binbodega.model in ['bodegag3','bodegag4', 'bodegag5']:
        if bin.binbodega.seleccion:
            return f'Selección N° {bin.binbodega.seleccion.seleccion.pk}'
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
        return f'Agrupacion N° {bin.binbodega.pk}'
    elif bin.tipo_binbodega.model == 'bodegag6':
        return f'Programa Planta Harina N° {bin.binbodega.programa.programa.pk}'
    elif bin.tipo_binbodega.model == 'bodegag7':
        return f'Proceso Planta Harina N° {bin.binbodega.proceso.proceso.pk}'
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
            return f'Produccion N° {bin.binbodega.tarja.produccion.produccion.pk}'
        elif bin.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            return f'Reproceso N° {bin.binbodega.tarja.reproceso.reproceso.pk}'
        elif bin.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
            return f'Selección N° {bin.binbodega.tarja.seleccion.seleccion.pk}'
        elif bin.binbodega.tipo_tarja.model == 'agrupaciondebinsbodega':
            return f'Agrupación N° {bin.binbodega.tarja.pk}'
        elif bin.binbodega.tipo_tarja.model == 'bodegag6':
            return f'Programa Planta Harina N° {bin.binbodega.tarja.programa.programa.pk}'
        elif bin.binbodega.tipo_tarja.model == 'bodegag7':
            return f'Proceso Planta Harina N° {bin.binbodega.tarja.proceso.proceso.pk}'
        elif bin.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
            if bin.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                return f'Producción N° {bin.binbodega.tarja.tarja.produccion.produccion.pk}'
            elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                return f'Reproceso N° {bin.binbodega.tarja.tarja.reproceso.reproceso.pk}'
            elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
                return f'Selección N° {bin.binbodega.tarja.tarja.seleccion.seleccion.pk}'
            elif bin.binbodega.tarja.tipo_tarja.model == 'agrupaciondebinsbodega':
                return f'Agrupación N° {bin.binbodega.tarja.tarja.pk}'
            elif bin.binbodega.tarja.tipo_tarja.model == 'bodegag6':
                return f'Programa Planta Harina N° {bin.binbodega.tarja.tarja.programa.programa.pk}'
            elif bin.binbodega.tarja.tipo_tarja.model == 'bodegag7':
                return f'Proceso Planta Harina N° {bin.binbodega.tarja.tarja.proceso.proceso.pk}'         
            
def get_calibre_display(bin):
    if bin.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
        return 'Sin Calibre'
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return 'Sin Calibre'
        elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return 'Sin Calibre'
    return bin.binbodega.get_calibre_display()       
            
def get_calibre(bin):
    if bin.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
        return '0'
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return '0'
        elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return '0'
    return bin.binbodega.get_calibre_display()       

def get_variedad_display(bin):
    if bin.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
        return 'Sin Especificar'
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return 'Sin Especificar'
        elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return 'Sin Especificar'
    return bin.binbodega.get_variedad_display()

def get_variedad(bin):
    if bin.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
        return 'RV'
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return 'RV'
        elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
            return 'RV'
    return bin.binbodega.variedad

def get_calidad(bin):
    if bin.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5', 'agrupaciondebinsbodegas']:
        return bin.binbodega.calidad
    return 'SN'
    
def get_calidad_display(bin):
    if bin.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5', 'agrupaciondebinsbodegas']:
        return bin.binbodega.calidad
    return 'Sin Calidad'
    
def get_kilos_bin(bin):
    if bin.tipo_binbodega.model in ['bodegag1','bodegag2']:
        if bin.binbodega.produccion:
            return round(bin.binbodega.produccion.peso - bin.binbodega.produccion.tipo_patineta, 2)
    elif bin.tipo_binbodega.model in ['bodegag1reproceso','bodegag2reproceso']:
        if bin.binbodega.reproceso:
            return round(bin.binbodega.reproceso.peso - bin.binbodega.reproceso.tipo_patineta, 2)
    elif bin.tipo_binbodega.model in ['bodegag3','bodegag4', 'bodegag5']:
        if bin.binbodega.seleccion:
            return round(bin.binbodega.seleccion.peso - bin.binbodega.seleccion.tipo_patineta, 2)
        else: 
          return 0
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
      return round(bin.binbodega.kilos_fruta, 2)
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      return round(bin.binbodega.kilos_fruta, 2)
    return 0

def get_codigo_tarja(bin):
    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
        return bin.binbodega.produccion.codigo_tarja
    elif bin.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        return bin.binbodega.reproceso.codigo_tarja
    elif bin.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
        return bin.binbodega.seleccion.codigo_tarja
    elif bin.tipo_binbodega.model == 'bodegag6':
        return bin.binbodega.programa.codigo_tarja
    elif bin.tipo_binbodega.model == 'bodegag6':
        return bin.binbodega.proceso.codigo_tarja
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
            return bin.binbodega.tarja.produccion.codigo_tarja
        elif bin.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            return bin.binbodega.tarja.reproceso.codigo_tarja
        elif bin.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
            return bin.binbodega.tarja.seleccion.codigo_tarja
        elif bin.binbodega.tipo_tarja.model == 'bodegag6':
            return bin.binbodega.tarja.programa.codigo_tarja
        elif bin.binbodega.tipo_tarja.model == 'bodega7':
            return bin.binbodega.tarja.proceso.codigo_tarja
        elif bin.binbodea.tipo_tarja.model == 'frutasobrantedeagrupacion':
            if bin.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                return bin.binbodega.tarja.tarja.produccion.codigo_tarja
            elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                return bin.binbodega.tarja.tarja.reproceso.codigo_tarja
            elif bin.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
                return bin.binbodega.tarja.tarja.seleccion.codigo_tarja
            elif bin.binbodega.tarja.tipo_tarja.model == 'bodegag6':
                return bin.binbodega.tarja.tarja.programa.codigo_tarja
            elif bin.binbodega.tarja.tipo_tarja.model == 'bodegag7':
                return bin.binbodega.tarja.tarja.proceso.codigo_tarja            

def obtener_bins_calibrados(bin):
    bins_calibrados = []
    
    print(bins_calibrados)

    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
        if bin.binbodega.produccion:
            cc_resultante = CCTarjaResultante.objects.filter(tarja=bin.binbodega.produccion).first()
            if cc_resultante:
                bins_calibrados.append(bin.binbodega)
    elif bin.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        if bin.binbodega.reproceso:
            cc_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja=bin.binbodega.reproceso).first()
            if cc_reproceso:
                bins_calibrados.append(bin.binbodega)
    elif bin.tipo_binbodega.model in ['bodegag3', 'bodegag4']:
        if bin.binbodega.seleccion:
            cc_seleccion = CCTarjaSeleccionada.objects.filter(tarja_seleccionada=bin.binbodega.seleccion).first()
            if cc_seleccion:
                bins_calibrados.append(bin.binbodega)
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
        mayor_valor = 0
        bin_con_mas_kilos = None
        for x in bin.binbodega.tarja.binsparaagrupacion_set.all():
            if x.tarja.kilos_fruta > mayor_valor:
                mayor_valor = x.tarja.kilos_fruta
                bin_con_mas_kilos = x.tarja

        ct = ContentType.objects.get_for_model(bin_con_mas_kilos)

        if ct.model in ['bodegag1', 'bodegag2']:
            cc_resultante = CCTarjaResultante.objects.filter(tarja=bin_con_mas_kilos.produccion).first()
            if cc_resultante:
                bins_calibrados.append(bin.binbodega.tarja)
        elif ct.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            cc_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja=bin_con_mas_kilos.reproceso).first()
            if cc_reproceso:
                bins_calibrados.append(bin.binbodega.tarja)
        elif ct.model in ['bodegag3', 'bodegag4']:
            cc_seleccion = CCTarjaSeleccionada.objects.filter(tarja_seleccionada=bin_con_mas_kilos.seleccion).first()
            if cc_seleccion:
                bins_calibrados.append(bin.binbodega.tarja)
                
        elif ct.model == 'frutasobrantedeagrupacion':
            if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                cc_resultante = CCTarjaResultante.objects.filter(tarja=bin.binbodega.tarja.produccion).first()
                if cc_resultante:
                    bins_calibrados.append(bin.binbodega.tarja)
            elif bin.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                cc_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja=bin.binbodega.tarja.reproceso).first()
                if cc_reproceso:
                    bins_calibrados.append(bin.binbodega.tarja)
            elif bin.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4']:
                cc_seleccionada = CCTarjaSeleccionada.objects.filter(tarja=bin.binbodega.tarja.seleccion).first()
                if cc_seleccionada:
                    bins_calibrados.append(bin.binbodega.tarja)

            
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
            cc_resultante = CCTarjaResultante.objects.filter(tarja=bin.binbodega.tarja.produccion).first()
            if cc_resultante:
                bins_calibrados.append(bin.binbodega.tarja)
        elif bin.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            cc_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja=bin.binbodega.tarja.reproceso).first()
            if cc_reproceso:
                bins_calibrados.append(bin.binbodega.tarja)
        elif bin.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4']:
            cc_seleccionada = CCTarjaSeleccionada.objects.filter(tarja=bin.binbodega.tarja.seleccion).first()
            if cc_seleccionada:
                bins_calibrados.append(bin.binbodega.tarja)

    return bins_calibrados
        
        
        
        
        
        
        
        
    #   return bin.binbodega.codigo_tarja
    # elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
    #   if bin.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
    #     return bin.binbodega.tarja.produccion.codigo_tarja
    #   elif bin.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
    #     return bin.binbodega.tarja.reproceso.codigo_tarja
    #   elif bin.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4']:
    #     return bin.binbodega.tarja.seleccion.codigo_tarja
    #   elif bin.binbodega.tipo_tarja.model == 'agrupaciondebinsbodega':
    #     return bin.binbodega.codigo_tarja
    # return 0