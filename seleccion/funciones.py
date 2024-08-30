from calendar import c
from django.db.models import Sum, Avg, Count, F
from .models import *
from controlcalidad.models import *
from produccion.models import *
from recepcionmp.models import *
from bodegas.models import *
from django.contrib.contenttypes.models import ContentType
import random, string

# def random_codigo_tarja(lenght=6):
#     return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))

  
def calcula_calibres_fruta_calibrada(pkseleccion):
    tarjas = BinsPepaCalibrada.objects.filter(seleccion=pkseleccion)
    
    sincalibre = 0
    precalibre = 0
    calibre_18_20 = 0
    calibre_20_22 = 0
    calibre_23_25 = 0
    calibre_25_27 = 0
    calibre_27_30 = 0
    calibre_30_32 = 0
    calibre_32_34 = 0
    calibre_34_36 = 0
    calibre_36_40 = 0
    calibre_40_mas = 0
    
    cc_encontrados = []
    dic = {}
    
    for x in tarjas:
        cc_tarja = x.binbodega.cdc_tarja
        cc_encontrados.append(cc_tarja)
        if x.binbodega.kilos_bin is not str():
            if cc_tarja.calibre == '0':
                sincalibre += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '1':
                precalibre += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '2':
                calibre_18_20 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '3':
                calibre_20_22 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '4':
                calibre_23_25 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '5':
                calibre_25_27 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '6':
                calibre_27_30 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '7':
                calibre_30_32 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '8':
                calibre_32_34 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '9':
                calibre_34_36 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '10':
                calibre_36_40 += x.binbodega.kilos_bin
            elif cc_tarja.calibre == '11':
                calibre_40_mas += x.binbodega.kilos_bin
            

                
                

    total = sincalibre + precalibre + calibre_18_20 + calibre_20_22 + calibre_23_25 + calibre_25_27 + calibre_27_30 + calibre_32_34 + calibre_34_36 + calibre_36_40 + calibre_40_mas
    sincalibre = sincalibre * 100 / total
    precalibre = precalibre * 100 / total
    calibre_18_20 = calibre_18_20 * 100 / total
    calibre_20_22 = calibre_20_22 * 100 / total
    calibre_23_25 = calibre_23_25 * 100 / total
    calibre_25_27 = calibre_25_27 * 100 / total
    calibre_27_30 = calibre_27_30 * 100 / total
    calibre_30_32 = calibre_30_32 * 100 / total
    calibre_32_34 = calibre_32_34 * 100 / total
    calibre_34_36 = calibre_34_36 * 100 / total
    calibre_36_40 = calibre_36_40 * 100 / total
    calibre_40_mas = calibre_40_mas * 100 / total
    
    dic = {
            'sincalibre': round(sincalibre, 2),
            'precalibre': round(precalibre, 2),
            'calibre_18_20': round(calibre_18_20, 2),
            'calibre_20_22': round(calibre_20_22, 2),
            'calibre_23_25': round(calibre_23_25, 2),
            'calibre_25_27': round(calibre_25_27, 2),
            'calibre_27_30': round(calibre_27_30, 2),
            'calibre_30_32': round(calibre_30_32, 2),
            'calibre_32_34': round(calibre_32_34, 2),
            'calibre_34_36': round(calibre_34_36, 2),
            'calibre_36_40': round(calibre_36_40, 2),
            'calibre_40_mas': round(calibre_40_mas, 2)
        }
    
    return dic
  
  
def calcula_calibres_fruta_seleccionada(pkseleccion):
    tarjas = TarjaSeleccionada.objects.filter(seleccion=pkseleccion)
    
    sincalibre = 0
    precalibre = 0
    calibre_18_20 = 0
    calibre_20_22 = 0
    calibre_23_25 = 0
    calibre_25_27 = 0
    calibre_27_30 = 0
    calibre_30_32 = 0
    calibre_32_34 = 0
    calibre_34_36 = 0
    calibre_36_40 = 0
    calibre_40_mas = 0
    
    for x in tarjas:
        cc_tarja = CCTarjaSeleccionada.objects.get(tarja_seleccionada=x.pk)
        if cc_tarja.calibre == '0':
            sincalibre += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '1':
            precalibre += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '2':
            calibre_18_20 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '3':
            calibre_20_22 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '4':
            calibre_23_25 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '5':
            calibre_25_27 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '6':
            calibre_27_30 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '7':
            calibre_30_32 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '8':
            calibre_32_34 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '9':
            calibre_34_36 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '10':
            calibre_36_40 += round(x.peso - x.tipo_patineta)
        elif cc_tarja.calibre == '11':
            calibre_40_mas += round(x.peso - x.tipo_patineta)
    
    total = sincalibre + precalibre + calibre_18_20 + calibre_20_22 + calibre_23_25 + calibre_25_27 + calibre_27_30 + calibre_30_32 + calibre_32_34 + calibre_34_36 + calibre_36_40 + calibre_40_mas
    sincalibre = sincalibre * 100 / total if total != 0 else 0
    precalibre = precalibre * 100 / total if total != 0 else 0
    calibre_18_20 = calibre_18_20 * 100 / total if total != 0 else 0
    calibre_20_22 = calibre_20_22 * 100 / total if total != 0 else 0
    calibre_23_25 = calibre_23_25 * 100 / total if total != 0 else 0
    calibre_25_27 = calibre_25_27 * 100 / total if total != 0 else 0
    calibre_27_30 = calibre_27_30 * 100 / total if total != 0 else 0
    calibre_30_32 = calibre_30_32 * 100 / total if total != 0 else 0
    calibre_32_34 = calibre_32_34 * 100 / total if total != 0 else 0
    calibre_34_36 = calibre_34_36 * 100 / total if total != 0 else 0
    calibre_36_40 = calibre_36_40 * 100 / total if total != 0 else 0
    calibre_40_mas = calibre_40_mas * 100 / total if total != 0 else 0
    
    dic = {
          'sincalibre': round(sincalibre, 2),
          'precalibre': round(precalibre, 2),
          'calibre_18_20': round(calibre_18_20, 2),
          'calibre_20_22': round(calibre_20_22, 2),
          'calibre_23_25': round(calibre_23_25, 2),
          'calibre_25_27': round(calibre_25_27, 2),
          'calibre_27_30': round(calibre_27_30, 2),
          'calibre_30_32': round(calibre_30_32, 2),
          'calibre_32_34': round(calibre_32_34, 2),
          'calibre_34_36': round(calibre_34_36, 2),
          'calibre_36_40': round(calibre_36_40, 2),
          'calibre_40_mas': round(calibre_40_mas, 2)
        }
    return dic
            
            
            
def consulta_bins_ingresados_a_seleccion(pkseleccion):
    tarjas = BinsPepaCalibrada.objects.filter(seleccion=pkseleccion)
    kilos_fruta = 0
    kilos_fruta_2 = 0
    
    print(kilos_fruta)
    print(kilos_fruta_2)
    
    for x in tarjas:
        kilos_fruta += x.binbodega.kilos_bin
        kilos_tarja = x.binbodega.kilos_bin
        cc_tarja = x.binbodega.cdc_tarja
        cantidad_muestra = cc_tarja.cantidad_muestra
        por_pepa_sana = cc_tarja.pepa_sana * 100 / cantidad_muestra
        kilos_pepa = por_pepa_sana * kilos_tarja / 100
        kilos_fruta_2 += kilos_pepa
    dic = {
        "fruta_resultante": kilos_fruta,
        "pepa_sana_proyectada": kilos_fruta_2   
        }
    
    return dic
  
def consulta_bins_seleccionados(pkseleccionn):
    tarjas = TarjaSeleccionada.objects.filter(seleccion=pkseleccionn)
    kilos_fruta = tarjas.aggregate(total=Sum(F('peso')-F('tipo_patineta')))['total']
    kilos_fruta = kilos_fruta if kilos_fruta != None else 0
    kilos_proyectados = 0
    
    for x in tarjas:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada=x.pk).first()
        if cc_tarja:
            cantidad_muestra = cc_tarja.cantidad_muestra
            if cantidad_muestra != None and cc_tarja.pepa_sana != None:
                por_pepa_sana = cc_tarja.pepa_sana * 100 / cantidad_muestra 
                kilos_pepa = por_pepa_sana * (x.peso - x.tipo_patineta) / 100
                kilos_proyectados += kilos_pepa
            
    dic = {
        "fruta_resultante": kilos_fruta,
        "pepa_sana_proyectada": kilos_proyectados
    } 
    
    return dic
  
  
def calcular_kilos_por_calibre_recepcionada(pk_seleccion):
    tarjas = BinsPepaCalibrada.objects.filter(seleccion=pk_seleccion)
    
    kilos_por_calibre = {
        'Sin Calibre': 0,
        'PreCalibre': 0,
        '18/20': 0,
        '20/22': 0,
        '23/25': 0,
        '25/27': 0,
        '27/30': 0,
        '30/32': 0,
        '32/34': 0,
        '34/36': 0,
        '36/40': 0,
        '40/mas': 0
    }

    for tarja in tarjas:
        cc_tarja = tarja.binbodega.cdc_tarja
        calibre = cc_tarja.get_calibre_display()
        

        if calibre in kilos_por_calibre:
            kilos_por_calibre[calibre] += tarja.binbodega.kilos_bin
            
           
        dic = {
        'sincalibre':  kilos_por_calibre["Sin Calibre"],
        'precalibre':  kilos_por_calibre['PreCalibre'],
        'calibre_18_20': kilos_por_calibre['18/20'],
        'calibre_20_22': kilos_por_calibre['20/22'],
        'calibre_23_25': kilos_por_calibre['23/25'],
        'calibre_25_27': kilos_por_calibre['25/27'],
        'calibre_27_30': kilos_por_calibre['27/30'],
        'calibre_30_32': kilos_por_calibre['30/32'],
        'calibre_32_34': kilos_por_calibre['32/34'],
        'calibre_34_36': kilos_por_calibre['34/36'],
        'calibre_36_40': kilos_por_calibre['36/40'],
        'calibre_40_mas': kilos_por_calibre['40/mas']
        }

    return dic
  
  
def calcular_kilos_por_calibre_saliente(pk_seleccion):
    tarjas = TarjaSeleccionada.objects.filter(seleccion=pk_seleccion)
    
    kilos_por_calibre = {
        'Sin Calibre': 0,
        'preCalibre': 0,
        '18/20': 0,
        '20/22': 0,
        '23/25': 0,
        '25/27': 0,
        '27/30': 0,
        '30/32': 0,
        '32/34': 0,
        '34/36': 0,
        '36/40': 0,
        '40/mas': 0
    }

    for tarja in tarjas:
        cc_tarja = CCTarjaSeleccionada.objects.get(tarja_seleccionada=tarja.pk)


        calibre = cc_tarja.get_calibre_display()
        if calibre in kilos_por_calibre:
            kilos_por_calibre[calibre] += round(tarja.peso - tarja.tipo_patineta, 2)
            
        dic = {
          'sin_calibre':  kilos_por_calibre['Sin Calibre'],
          'precalibre':  kilos_por_calibre['preCalibre'],
          'calibre_18_20': kilos_por_calibre['18/20'],
          'calibre_20_22': kilos_por_calibre['20/22'],
          'calibre_23_25': kilos_por_calibre['23/25'],
          'calibre_25_27': kilos_por_calibre['25/27'],
          'calibre_27_30': kilos_por_calibre['27/30'],
          'calibre_30_32': kilos_por_calibre['30/32'],
          'calibre_32_34': kilos_por_calibre['32/34'],
          'calibre_34_36': kilos_por_calibre['34/36'],
          'calibre_36_40': kilos_por_calibre['36/40'],
          'calibre_40_mas':  kilos_por_calibre['40/mas']
          }
    
        return dic

  
def porcentaje(n1, n2):
    if isinstance(n1, str):
        n1 = float(n1.replace('.', '').replace(',', '.'))
    
    if isinstance(n2, str):
        n2 = float(n2.replace('.', '').replace(',', '.'))
        
    try:
        porcentaje = n2 * 100 / n1
    except ZeroDivisionError:
        porcentaje = 0
    
    return round(porcentaje, 2)