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
        cc_tarja = CCTarjaSeleccionada.objects.get(tarja_seleccionada=tarja.pk)

        calibre = cc_tarja.get_calibre_display()
        print(f"calibre: {calibre}, peso: {tarja.peso}, tipo_patineta: {tarja.tipo_patineta}")
        if calibre in kilos_por_calibre:
            kilos_por_calibre[calibre] += round(tarja.peso - tarja.tipo_patineta, 2)
            
        dic = {
          'sin_calibre':  kilos_por_calibre['Sin Calibre'],
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
          'calibre_40_mas':  kilos_por_calibre['40/mas']
          }
    
        return dic

def calcular_kilos_por_calibre_tarjas_seleccionadas(pk_selection):
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
    
    tarjas = CCTarjaSeleccionada.objects.filter(tarja_seleccionada__seleccion=pk_selection)
    
    for tarja in tarjas:
        calibre = tarja.get_calibre_display()
        kilos = tarja.tarja_seleccionada.peso - tarja.tarja_seleccionada.tipo_patineta
        if calibre in kilos_por_calibre:
            kilos_por_calibre[calibre] += kilos
    return kilos_por_calibre

def calcular_control_sub_productos_tarjas_seleccionadas(pk_selection):
    bins_en_seleccion = TarjaSeleccionada.objects.filter(seleccion=pk_selection)
    subProductos = SubProductoOperario.objects.filter(seleccion=pk_selection)
    
    resultados_informe = []
    resultados_subproductos = [] 

    # Inicializamos un diccionario para acumular los kilos de cada pérdida
    acumulador_controles = {
        "trozo": 0,
        "picada": 0,
        "hongo": 0,
        "insecto": 0,
        "dobles": 0,
        "p_goma": 0,
        "basura": 0,
        "mezcla": 0,
        "color": 0,
        "goma": 0,
        "pepa": 0,  # Este lo excluiremos en el cálculo de pérdidas
        "kilos_total_perdidas": 0,  # Suma total de las pérdidas (sin pepa)
        "kilos_total": 0,  # Suma total de todos los kilos
    }

    # Recorremos los subproductos
    for producto in subProductos:
        dic = {
            "operario": f'{producto.operario.nombre} {producto.operario.apellido}',
            "tipo_producto": f'{producto.get_tipo_subproducto_display()}',
            "peso": producto.peso
        }
        resultados_subproductos.append(dic)
    
    # Recorremos los bins seleccionados y acumulamos los valores en el diccionario
    for bins in bins_en_seleccion:
        cc_bin = CCTarjaSeleccionada.objects.filter(pk=bins.pk).first()
        if not cc_bin:
            continue

        # Kilos netos de los bins
        kilosnetos = (bins.peso - bins.tipo_patineta)
        acumulador_controles["kilos_total"] += kilosnetos

        # Acumular las pérdidas en kilos (sin contar la pepa)
        acumulador_controles["trozo"] += cc_bin.trozo
        acumulador_controles["picada"] += cc_bin.picada
        acumulador_controles["hongo"] += cc_bin.hongo
        acumulador_controles["insecto"] += cc_bin.daño_insecto
        acumulador_controles["dobles"] += cc_bin.dobles
        acumulador_controles["p_goma"] += cc_bin.punto_goma
        acumulador_controles["basura"] += cc_bin.basura
        acumulador_controles["mezcla"] += cc_bin.mezcla_variedad
        acumulador_controles["color"] += cc_bin.fuera_color
        acumulador_controles["goma"] += cc_bin.goma

        # Acumular las pérdidas (sin pepa) en un total
        acumulador_controles["kilos_total_perdidas"] += (
            cc_bin.trozo + cc_bin.picada + cc_bin.hongo + cc_bin.daño_insecto +
            cc_bin.dobles + cc_bin.punto_goma + cc_bin.basura + cc_bin.mezcla_variedad +
            cc_bin.fuera_color + cc_bin.goma
        )

        # Acumular también los kilos de pepa
        acumulador_controles["pepa"] += cc_bin.pepa_sana
    
    resultados_informe = {
        "trozo_kilos": acumulador_controles["trozo"],
        "trozo_pct": round((acumulador_controles["trozo"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "picada_kilos": acumulador_controles["picada"],
        "picada_pct": round((acumulador_controles["picada"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "hongo_kilos": acumulador_controles["hongo"],
        "hongo_pct": round((acumulador_controles["hongo"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "insecto_kilos": acumulador_controles["insecto"],
        "insecto_pct": round((acumulador_controles["insecto"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "dobles_kilos": acumulador_controles["dobles"],
        "dobles_pct": round((acumulador_controles["dobles"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "p_goma_kilos": acumulador_controles["p_goma"],
        "p_goma_pct": round((acumulador_controles["p_goma"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "basura_kilos": acumulador_controles["basura"],
        "basura_pct": round((acumulador_controles["basura"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "mezcla_kilos": acumulador_controles["mezcla"],
        "mezcla_pct": round((acumulador_controles["mezcla"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "color_kilos": acumulador_controles["color"],
        "color_pct": round((acumulador_controles["color"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "goma_kilos": acumulador_controles["goma"],
        "goma_pct": round((acumulador_controles["goma"] / acumulador_controles["kilos_total_perdidas"]) * 100, 1) if acumulador_controles["kilos_total_perdidas"] > 0 else 0,

        "pepa_kilos": acumulador_controles["pepa"],  # La pepa no se incluye en las pérdidas
        "kilos_total": acumulador_controles["kilos_total"],
        "kilos_total_perdidas": acumulador_controles["kilos_total_perdidas"],
    }

    return resultados_informe, resultados_subproductos
    
    
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