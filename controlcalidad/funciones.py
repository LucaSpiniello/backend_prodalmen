from django import template
from .models import *
from recepcionmp.models import RecepcionMp, EnvasesGuiaRecepcionMp
from produccion.models import *
from controlcalidad.models import CCRecepcionMateriaPrima, CCRendimiento, CCPepa
from django.db.models import Sum, Avg, F, ExpressionWrapper, FloatField, Value

def busca_dic(id, list_dic):
    diccionario = None
    for x in list_dic:
        if x['cc_lote'] == id:
            diccionario = x
    
    return diccionario

def calcula_netos_lote(pklote):
    lote = RecepcionMp.objects.get(pk=pklote)
    k_camion = lote.kilos_brutos_1 + lote.kilos_brutos_2 - lote.kilos_tara_1 - lote.kilos_tara_2
    k_envases = EnvasesGuiaRecepcionMp.objects.filter(recepcionmp=lote.pk).aggregate(total=Sum(F('cantidad_envases')*F('envase__peso')))['total']
    return k_camion - k_envases


def cc_muestras_lotes(lista_lotes):
    lista_cc_lotes = []
    
    cc_lotes = CCRecepcionMateriaPrima.objects.filter(recepcionmp__in=lista_lotes)
    
    for x in cc_lotes:
        cc_rendimiento =CCRendimiento.objects.filter(cc_recepcionmp=x.pk)
        
        prom_basura = cc_rendimiento.aggregate(total=Avg('basura'))['total']
        prom_pelon = cc_rendimiento.aggregate(total=Avg('pelon'))['total']
        prom_ciega = cc_rendimiento.aggregate(total=Avg('ciega'))['total']
        prom_cascara = cc_rendimiento.aggregate(total=Avg('cascara'))['total']
        prom_pepahuerto = cc_rendimiento.aggregate(total=Avg('pepa_huerto'))['total']
        prom_pepabruta = cc_rendimiento.aggregate(total=Avg('pepa'))['total']
        
        if prom_basura != None and prom_pelon != None and prom_ciega != None and prom_cascara != None and prom_pepahuerto != None and prom_pepabruta != None:
            universo = prom_basura + prom_pelon + prom_ciega + prom_cascara + prom_pepahuerto + prom_pepabruta  
            
            basura = prom_basura / universo * 100
            pelon = prom_pelon / universo * 100
            ciega = prom_ciega / universo * 100
            cascara = prom_cascara / universo * 100
            pepahuerto = prom_pepahuerto / universo * 100
            pepabruta = prom_pepabruta / universo * 100
            
            dic = {'cc_lote':x.pk, 'basura':round(basura, 2), 'pelon':round(pelon, 2), 'ciega':round(ciega, 2), 'cascara':round(cascara, 2), 'pepa_huerto':round(pepahuerto, 2), 'pepa_bruta':round(pepabruta, 2)}
        else:
            dic = {'cc_lote':x.pk, 'basura':0, 'pelon':0, 'ciega':0, 'cascara':0, 'pepa_huerto':0, 'pepa_bruta':0}
        lista_cc_lotes.append(dic)
    
    return lista_cc_lotes


def cc_pepa_lote(lista_lotes):
    lista_cc_pepa = []
    
    cc_lotes = CCRecepcionMateriaPrima.objects.filter(recepcionmp__in=lista_lotes)
    
    for x in cc_lotes:
        cc_rendimiento = CCRendimiento.objects.filter(cc_recepcionmp=x.pk)
        cc_pepa = CCPepa.objects.filter(cc_rendimiento__in=cc_rendimiento)

        
        prom_pepabruta = cc_rendimiento.aggregate(total=Avg('pepa'))['total']
        prom_muestra_variedad = cc_pepa.aggregate(total=Avg('muestra_variedad'))['total']
        prom_daño_insecto = cc_pepa.aggregate(total=Avg('daño_insecto'))['total']
        prom_hongo = cc_pepa.aggregate(total=Avg('hongo'))['total']
        prom_dobles = cc_pepa.aggregate(total=Avg('doble'))['total']
        prom_color = cc_pepa.aggregate(total=Avg('fuera_color'))['total']
        prom_vana = cc_pepa.aggregate(total=Avg('vana_deshidratada'))['total']
        prom_pgoma = cc_pepa.aggregate(total=Avg('punto_goma'))['total']
        prom_goma = cc_pepa.aggregate(total=Avg('goma'))['total']
        
        if prom_pepabruta is not None and prom_muestra_variedad is not None and prom_daño_insecto is not None and prom_hongo is not None and prom_dobles is not None and prom_color is not None and prom_vana is not None and prom_pgoma is not None and prom_goma is not None:
            universo = prom_muestra_variedad + prom_daño_insecto + prom_hongo + prom_dobles + prom_color + prom_vana + prom_pgoma + prom_goma
            pepa_exp = prom_pepabruta - universo
            total_universo = universo + pepa_exp
            
            mezcla = prom_muestra_variedad / total_universo * 100
            insecto = prom_daño_insecto / total_universo * 100
            hongo = prom_hongo / total_universo * 100
            dobles = prom_dobles / total_universo * 100
            color = prom_color / total_universo * 100
            vana = prom_vana / total_universo * 100
            pgoma = prom_pgoma / total_universo * 100
            goma = prom_goma / total_universo * 100
            
            dic = {'cc_lote': x.pk, 'mezcla': round(mezcla, 2), 'insecto': round(insecto, 2), 'hongo': round(hongo, 2), 'dobles': round(dobles, 2), 'color': round(color, 2), 'vana': round(vana, 2), 'pgoma': round(pgoma, 2), 'goma': round(goma, 2)}
        else:
            dic = {'cc_lote': x.pk, 'mezcla': 0, 'insecto': 0, 'hongo': 0, 'dobles': 0, 'color': 0, 'vana': 0, 'pgoma': 0, 'goma': 0}
            
        lista_cc_pepa.append(dic)
        
    return lista_cc_pepa



def cc_pepa_calibres_lote(lista_lotes):
    lista_cc_calibres = []
    
    cc_lotes = CCRecepcionMateriaPrima.objects.filter(recepcionmp__in=lista_lotes)
    
    for x in cc_lotes:
        prom_pepabruta = CCRendimiento.objects.filter(cc_recepcionmp=x.pk).aggregate(total=Avg('pepa'))['total']
        cc_rendimiento = CCRendimiento.objects.filter(cc_recepcionmp=x.pk)
        desechos = CCPepa.objects.filter(cc_rendimiento__in=cc_rendimiento).aggregate(total=Avg(F('muestra_variedad')+F('daño_insecto')+F('hongo')+F('doble')+F('fuera_color')+F('vana_deshidratada')+F('punto_goma')+F('goma')))['total']
        lista_calibres = []
        
        if prom_pepabruta is not None and desechos is not None:
            # cc_rendimiento = cc_rendimiento.order_by('-pk').order_by('-id').first()
            cc_rendimiento = cc_rendimiento.values_list('id', flat=True)

            cc_pepa = CCPepa.objects.filter(cc_rendimiento__in=cc_rendimiento, cc_calibrespepaok=True)
            if cc_pepa.exists():  # Verifica si hay resultados
                cc_pepa = cc_pepa[0]  # Obtén el primer objeto
                lista_calibres.append(cc_pepa.pre_calibre if cc_pepa.pre_calibre is not None else 0)
                lista_calibres.append(cc_pepa.calibre_18_20 if cc_pepa.calibre_18_20 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_20_22 if cc_pepa.calibre_20_22 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_23_25 if cc_pepa.calibre_23_25 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_25_27 if cc_pepa.calibre_25_27 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_27_30 if cc_pepa.calibre_27_30 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_30_32 if cc_pepa.calibre_30_32 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_32_34 if cc_pepa.calibre_32_34 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_34_36 if cc_pepa.calibre_34_36 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_36_40 if cc_pepa.calibre_36_40 is not None else 0)
                lista_calibres.append(cc_pepa.calibre_40_mas if cc_pepa.calibre_40_mas is not None else 0)
            else:
                # Si no hay resultados, agrega ceros a la lista de calibres
                lista_calibres.extend([0] * 11)  # 11 ceros para cada calibre
            
            # Calcula pepa_exp
            pepa_exp = sum(lista_calibres)
            
            if pepa_exp != 0:
                # Calcula los porcentajes de calibre
                precalibre = lista_calibres[0] * 100 / pepa_exp
                calibre_18_20 = lista_calibres[1] * 100 / pepa_exp
                calibre_20_22 = lista_calibres[2] * 100 / pepa_exp
                calibre_23_25 = lista_calibres[3] * 100 / pepa_exp
                calibre_25_27 = lista_calibres[4] * 100 / pepa_exp
                calibre_27_30 = lista_calibres[5] * 100 / pepa_exp
                calibre_30_32 = lista_calibres[6] * 100 / pepa_exp
                calibre_32_34 = lista_calibres[7] * 100 / pepa_exp
                calibre_34_36 = lista_calibres[8] * 100 / pepa_exp
                calibre_36_40 = lista_calibres[9] * 100 / pepa_exp
                calibre_40_mas = lista_calibres[10] * 100 / pepa_exp
            else:
                # Si pepa_exp es cero, asigna cero a todos los porcentajes de calibre
                precalibre = calibre_18_20 = calibre_20_22 = calibre_23_25 = calibre_25_27 = calibre_27_30 = calibre_30_32 = calibre_32_34 = calibre_34_36 = calibre_36_40 = calibre_40_mas = 0
            
            dic = {
                'cc_lote': x.pk,
                'precalibre': round(precalibre, 3),
                'calibre_18_20': round(calibre_18_20, 3),
                'calibre_20_22': round(calibre_20_22, 3),
                'calibre_23_25': round(calibre_23_25, 3),
                'calibre_25_27': round(calibre_25_27, 3),
                'calibre_27_30': round(calibre_27_30, 3),
                'calibre_30_32': round(calibre_30_32, 3),
                'calibre_32_34': round(calibre_32_34, 3),
                'calibre_34_36': round(calibre_34_36, 3),
                'calibre_36_40': round(calibre_36_40, 3),
                'calibre_40_mas': round(calibre_40_mas, 3)
            }
        else:
            dic = {
            'cc_lote': x.pk,
            'precalibre': 0,
            'calibre_18_20': 0,
            'calibre_20_22': 0,
            'calibre_23_25': 0,
            'calibre_25_27': 0,
            'calibre_27_30': 0,
            'calibre_30_32': 0,
            'calibre_32_34': 0, 
            'calibre_34_36': 0,
            'calibre_36_40': 0,
            'calibre_40_mas': 0
        }
        
        lista_cc_calibres.append(dic)
            
    return lista_cc_calibres


###### CALCULO DESCUENTO ######


def descuentos_cat2_desechos(list_dic, lista_muestras):
    lista_descuentos = []
    """
        CAT 2
        Mezcla => 5%
        Color => 5%
        Dobles => 10%
        
        DESECHOS 
        Insecto => 1.5%
        Hongo => 1.5%
        Vana => 1%
        Punto Goma => 0.5%
        Goma => 0.5%    
    """
    for x in list_dic:
        lote = CCRecepcionMateriaPrima.objects.get(pk=x['cc_lote'])
        kilos_netos = calcula_netos_lote(lote.recepcionmp.pk)
        muestra = busca_dic(x['cc_lote'], lista_muestras)
        por_pepabruta = muestra['pepa_bruta']
        kilos_pepa_bruta = por_pepabruta * kilos_netos/ 100 
        
        
        if x['mezcla'] > 5:
            porcentaje = x['mezcla'] - 5
            mezcla = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            mezcla = 0
        
        if x['color'] > 5:
            porcentaje = x['color'] - 5
            color = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            color = 0
        if x['dobles'] > 10:
            porcentaje = x['dobles'] - 10
            dobles = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            dobles = 0
        
        if x['insecto'] > 1.5:
            porcentaje = x['insecto'] - 1.5
            insecto = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            insecto = 0
        
        if x['hongo'] > 1.5:
            porcentaje = x['hongo'] - 1.5
            hongo = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            hongo = 0
        
        if x['vana'] > 1:
            porcentaje = x['vana'] - 1
            vana = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            vana = 0
        
        if x['pgoma'] > 0.5:
            porcentaje = x['pgoma'] - 0.5
            punto_goma = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            punto_goma = 0
        
        if x['goma'] > 0.5:
            porcentaje = x['goma'] - 0.5
            goma = round((porcentaje*kilos_pepa_bruta)/100, 3)
        else:
            goma = 0
        
        
        cat2 = mezcla + color + dobles
        desechos = insecto + hongo + vana + punto_goma + goma
        pepa_exp = kilos_pepa_bruta - cat2 - desechos
        
        dic = {'cc_lote':x['cc_lote'], 'pepa_exp':pepa_exp, 'cat2':cat2, 'desechos':desechos, 'mezcla':mezcla, 'color':color, 'dobles':dobles, 'insecto':insecto, 'hongo':hongo, 'vana':vana, 'pgoma':punto_goma, 'goma':goma}
        
        lista_descuentos.append(dic)
    return lista_descuentos


def aporte_pex(lista_desc, lista_muestras):
    lista_aporte = []
    for x in lista_desc:
        lote = CCRecepcionMateriaPrima.objects.get(pk=x['cc_lote'])
        kilos_netos = calcula_netos_lote(lote.recepcionmp.pk)
        muestra = busca_dic(x['cc_lote'], lista_muestras)
        por_pepabruta = muestra['pepa_bruta']
        kilos_pepa_bruta = por_pepabruta*kilos_netos/100
        
        if kilos_pepa_bruta > 0:
            exp = x['pepa_exp'] / kilos_pepa_bruta * 100
            cat2 = x['cat2'] / kilos_pepa_bruta * 100
            des = x['desechos'] / kilos_pepa_bruta * 100
            
            dic = {'cc_lote':x['cc_lote'], 'exportable':exp, 'cat2':cat2, 'des':des}
        else:
            dic = {'cc_lote':x['cc_lote'], 'exportable':0, 'cat2':0, 'des':0}
        lista_aporte.append(dic)
    return lista_aporte

def porcentaje_a_liquidar(list_pex):
    lista = []
    
    for x in list_pex:
        if x['exportable'] > 0:
            
            cat2 = x['cat2'] 
            
            desechos = x['des']
            
            exportable = x['exportable']
            
            dic = {'cc_lote':x['cc_lote'], 'exportable':exportable, 'cat2':cat2, 'des':desechos}
        else:
            dic = {'cc_lote':x['cc_lote'], 'exportable':0, 'cat2':0, 'des':0}
        lista.append(dic)
    return lista

def kilos_descontados_merma(lista_menos_3, lista_muestra):
    lista = []
    
    for x in lista_menos_3:
        if x['exportable'] > 0:
            lote = CCRecepcionMateriaPrima.objects.get(pk=x['cc_lote'])
            kilos_netos = calcula_netos_lote(lote.recepcionmp.pk)
            muestra = busca_dic(x['cc_lote'], lista_muestra)
            por_pepabruta = muestra['pepa_bruta']
            kilos_pepa_bruta = por_pepabruta*kilos_netos/100
            
            exportable = kilos_pepa_bruta * x['exportable'] / 100
            cat2 = kilos_pepa_bruta * x['cat2'] / 100
            des = kilos_pepa_bruta * x['des'] / 100
            
            dic = {'cc_lote':x['cc_lote'], 'exportable':exportable, 'cat2':cat2, 'des':des}
        else:
            dic = {'cc_lote':x['cc_lote'], 'exportable':0, 'cat2':0, 'des':0}
        lista.append(dic)
    
    return lista


def merma_porcentual(lista_pex):
    lista = []
    
    for x in lista_pex:
        
        exportable = x['exportable'] 
        cat2 = x['cat2'] 
        des = x['des'] 
        
        dic = {'cc_lote':x['cc_lote'], 'exportable':exportable, 'cat2':cat2, 'des':des}
        
        lista.append(dic)
        
    return lista


def calculo_final(lista_muestras, lista_merma, lista_descontados, lista_kilos):
    kilos_netos = 0
    kilos_brutos = 0
    por_brutos = 0
    merma_exp = 0
    final_exp = 0
    merma_cat2 = 0
    final_cat2 = 0
    merma_des = 0
    final_des = 0
    
    
    for x in lista_muestras:
        lote = CCRecepcionMateriaPrima.objects.get(pk=x['cc_lote'])
        merma = busca_dic(x['cc_lote'], lista_merma)
        descontado = busca_dic(x['cc_lote'], lista_descontados)
        kilos_desc = busca_dic(x['cc_lote'], lista_kilos)
        
        # print("merma", merma, '\n')
        # print("descontado", descontado, '\n')
        # print("kilos_desc", kilos_desc, '\n')

        netos = calcula_netos_lote(lote.recepcionmp.pk)
        brutos = x['pepa_bruta'] * netos / 100
        
        kilos_netos += round(netos, 1)
        kilos_brutos += round(brutos, 1)

        m_exp = round((merma['exportable'] * brutos) / 100, 2)
        merma_exp += m_exp
        final_exp += kilos_desc['exportable']

        m_cat2 = (merma['cat2'] * brutos)
        merma_cat2 += m_cat2
        final_cat2 += descontado['cat2']
        
        m_des = (merma['des'] * brutos) / 100
        merma_des += round(m_des, 1)
        final_des += round(kilos_desc['des'], 1)
        
    if kilos_netos == 0:
        kilos_netos = 1
        
    por_brutos = kilos_brutos / kilos_netos * 100
        
    if len(lista_muestras) >= 1:
        dic = {'kilos_netos':round(kilos_netos, 1), 'kilos_brutos':round(kilos_brutos, 1), 'por_brutos':round(por_brutos , 1), 'merma_exp':round(merma_exp, 1), 'final_exp':round(final_exp, 1), 'merma_cat2':round(merma_cat2, 1), 'final_cat2':round(final_cat2, 1), 'merma_des':round(merma_des, 1), 'final_des':round(final_des, 1)}
    else:
        dic = {'kilos_netos': 0, 'kilos_brutos': 0, 'por_brutos': 0, 'merma_exp': 0, 'final_exp': 0, 'merma_cat2': 0, 'final_cat2': 0, 'merma_des': 0 , 'final_des': 0}
    return dic



def promedio_porcentaje_muestras(lista_muestras):
    netos_totales = 0
    if len(lista_muestras) > 0:
        basura = []
        pelon = []
        ciega = []
        cascara = []
        pepa_huerto = []
        pepa_bruta = 0
        for x in lista_muestras:
            lote = CCRecepcionMateriaPrima.objects.get(pk=x['cc_lote'])
            basura.append(x['basura'])
            pelon.append(x['pelon'])
            ciega.append(x['ciega'])
            cascara.append(x['cascara'])
            pepa_huerto.append(x['pepa_huerto'])
            netos_totales += calcula_netos_lote(lote.recepcionmp.pk)
            netos = calcula_netos_lote(lote.recepcionmp.pk)
            brutos = x['pepa_bruta'] * netos / 100
            pepa_bruta += round(brutos, 1)

        
        prom_basura = sum(basura)/len(basura)
        prom_pelon = sum(pelon)/len(pelon)
        prom_ciega = sum(ciega)/len(ciega)
        prom_cascara = sum(cascara)/len(cascara)
        prom_pepa_huerto = sum(pepa_huerto)/len(pepa_huerto)
        prom_pepa_bruta = (pepa_bruta / netos_totales) * 100
        
        
        return {'basura':round(prom_basura, 2), 'pelon':round(prom_pelon, 2), 'ciega':round(prom_ciega, 2), 'cascara':round(prom_cascara, 2), 'pepa_huerto':round(prom_pepa_huerto, 2), 'pepa_bruta':round(prom_pepa_bruta, 3)}
    else:
        return {'basura':0, 'pelon':0, 'ciega':0, 'cascara':0, 'pepa_huerto':0, 'pepa_bruta':0}

def promedio_porcentaje_cc_pepa(lista_cc_pepa):

    if len(lista_cc_pepa) > 0:
        mezcla = []
        insecto = []
        hongo = []
        dobles = []
        color = []
        vana = []
        pgoma = []
        goma = []
        
        for x in lista_cc_pepa:
            mezcla.append(x['mezcla'])
            insecto.append(x['insecto'])
            hongo.append(x['hongo'])
            dobles.append(x['dobles'])
            color.append(x['color'])
            vana.append(x['vana'])
            pgoma.append(x['pgoma'])
            goma.append(x['goma'])
        
        prom_mezcla = sum(mezcla)/len(mezcla)
        prom_insecto = sum(insecto)/len(insecto)
        prom_hongo = sum(hongo)/len(hongo)
        prom_dobles = sum(dobles)/len(dobles)
        prom_color = sum(color)/len(color)
        prom_vana = sum(vana)/len(vana)
        prom_pgoma = sum(pgoma)/len(pgoma)
        prom_goma = sum(goma)/len(goma)
        
        return {'mezcla': round(prom_mezcla, 2), 'insecto': round(prom_insecto, 2), 'hongo': round(prom_hongo, 2), 'dobles': round(prom_dobles, 2), 'color': round(prom_color, 2), 'vana': round(prom_vana, 2), 'pgoma': round(prom_pgoma, 2), 'goma': round(prom_goma, 2)}
    else:
        return {'mezcla': 0, 'insecto': 0, 'hongo': 0, 'dobles': 0, 'color': 0, 'vana': 0, 'pgoma': 0, 'goma': 0}
    
    
    
def promedio_porcentaje_calibres(lista_calibres):
    if len(lista_calibres) > 0:
        precalibre = []
        calibre_18_20 = []
        calibre_20_22 = []
        calibre_23_25 = []
        calibre_25_27 = []
        calibre_27_30 = []
        calibre_30_32 = []
        calibre_32_34 = []
        calibre_34_36 = []
        calibre_36_40 = []
        calibre_40_mas = []
        
        for x in lista_calibres:
            precalibre.append(x['precalibre'])
            calibre_18_20.append(x['calibre_18_20'])
            calibre_20_22.append(x['calibre_20_22'])
            calibre_23_25.append(x['calibre_23_25'])
            calibre_25_27.append(x['calibre_25_27'])
            calibre_27_30.append(x['calibre_27_30'])
            calibre_30_32.append(x['calibre_30_32'])
            calibre_32_34.append(x['calibre_32_34'])
            calibre_34_36.append(x['calibre_34_36'])
            calibre_36_40.append(x['calibre_36_40'])
            calibre_40_mas.append(x['calibre_40_mas'])
            
        prom_precalibre = sum(precalibre)/len(precalibre)
        prom_calibre_18_20 = sum(calibre_18_20)/len(calibre_18_20)
        prom_calibre_20_22 = sum(calibre_20_22)/len(calibre_20_22)
        prom_calibre_23_25 = sum(calibre_23_25)/len(calibre_23_25)
        prom_calibre_25_27 = sum(calibre_25_27)/len(calibre_25_27)
        prom_calibre_27_30 = sum(calibre_27_30)/len(calibre_27_30)
        prom_calibre_30_32 = sum(calibre_30_32)/len(calibre_30_32)
        prom_calibre_32_34 = sum(calibre_32_34)/len(calibre_32_34)
        prom_calibre_34_36 = sum(calibre_34_36)/len(calibre_34_36)
        prom_calibre_36_40 = sum(calibre_36_40)/len(calibre_36_40)
        prom_calibre_40_mas =sum(calibre_40_mas)/len(calibre_40_mas)
        
        return {
                'precalibre': round(prom_precalibre, 2),
                'calibre_18_20': round(prom_calibre_18_20, 2),
                'calibre_20_22': round(prom_calibre_20_22, 2),
                'calibre_23_25': round(prom_calibre_23_25, 2),
                'calibre_25_27': round(prom_calibre_25_27, 2),
                'calibre_27_30': round(prom_calibre_27_30, 2),
                'calibre_30_32': round(prom_calibre_30_32, 2),
                'calibre_32_34': round(prom_calibre_32_34, 2),
                'calibre_34_36': round(prom_calibre_34_36, 2),
                'calibre_36_40': round(prom_calibre_36_40, 2),
                'calibre_40_mas': round(prom_calibre_40_mas, 2)
                }
    else:
        return  {
            'precalibre': 0,
            'calibre_18_20': 0,
            'calibre_20_22': 0,
            'calibre_23_25': 0,
            'calibre_25_27': 0,
            'calibre_27_30': 0,
            'calibre_30_32': 0,
            'calibre_32_34': 0, 
            'calibre_34_36': 0,
            'calibre_36_40': 0,
            'calibre_40_mas': 0
        }
        
        
        
def consulta_kilos_tarjas_res(pkproduccion):
    # Filtrar por tipo_resultante igual a 2 y calcular la suma de peso menos tipo_patineta
    tarjasres = TarjaResultante.objects.filter(produccion=pkproduccion).aggregate(kilos=Sum(F('peso') - F('tipo_patineta')))['kilos'] or 0
    tarja_res_residuo = TarjaResultante.objects.filter(produccion=pkproduccion, tipo_resultante = '2').aggregate(kilos=Sum(F('peso') - F('tipo_patineta')))['kilos'] or 0
    return tarjasres - tarja_res_residuo

def consulta_muestras_tarjasresultantes_cdc_pepabruta(listalotes):
    controlesrendimientos = CCTarjaResultante.objects.filter(tarja__in=listalotes)
    avg_trozo = controlesrendimientos.aggregate(promedio=Avg('trozo'))['promedio']
    avg_picada = controlesrendimientos.aggregate(promedio=Avg('picada'))['promedio']
    avg_hongo      = controlesrendimientos.aggregate(promedio=Avg('hongo'))['promedio']
    avg_danoinsect = controlesrendimientos.aggregate(promedio=Avg('daño_insecto'))['promedio']
    avg_dobles      = controlesrendimientos.aggregate(promedio=Avg('dobles'))['promedio']
    avg_goma      = controlesrendimientos.aggregate(promedio=Avg('goma'))['promedio']
    avg_basura = controlesrendimientos.aggregate(promedio=Avg('basura'))['promedio']
    avg_mezclavari = controlesrendimientos.aggregate(promedio=Avg('mezcla_variedad'))['promedio']
    avg_fueracolor = controlesrendimientos.aggregate(promedio=Avg('fuera_color'))['promedio']
    avg_puntogoma = controlesrendimientos.aggregate(promedio=Avg('punto_goma'))['promedio']
    avg_pepasana = controlesrendimientos.aggregate(promedio=Avg('pepa_sana'))['promedio']
    #avg_calibre_2325 = controlesrendimientos.filter(calibre='4').aggregate(promedio=Avg('pepa_sana'))['promedio']
    
    
    if not avg_trozo or not avg_picada or not avg_hongo or not avg_danoinsect or not avg_dobles or not avg_goma or not avg_basura or not avg_mezclavari or not avg_fueracolor or not avg_puntogoma or not avg_pepasana:
        trozo = 0
        picada = 0
        hongo = 0
        danoinsec = 0
        dobles = 0
        goma = 0
        basura = 0
        mezclavarie = 0
        fueracolor = 0
        puntogoma = 0
        pepasana = 0
    else:
        totalmuestras =  avg_trozo + avg_picada + avg_hongo + avg_danoinsect + avg_dobles + avg_goma + avg_basura + avg_mezclavari + avg_fueracolor + avg_puntogoma + avg_pepasana
        
        trozo = avg_trozo/totalmuestras*100
        picada = avg_picada/totalmuestras*100
        hongo = avg_hongo/totalmuestras*100
        danoinsec = avg_danoinsect/totalmuestras*100
        dobles = avg_dobles/totalmuestras*100
        goma = avg_goma/totalmuestras*100
        basura = avg_basura/totalmuestras*100
        mezclavarie = avg_mezclavari/totalmuestras*100
        fueracolor = avg_fueracolor/totalmuestras*100
        puntogoma = avg_puntogoma/totalmuestras*100
        pepasana = avg_pepasana/totalmuestras*100
        
    return [trozo, picada, hongo, danoinsec, dobles, goma, basura, mezclavarie, fueracolor, puntogoma, pepasana] 
        
        
def consulta_tarjasresultantes_en_produccion(pkproduccion):
    produccion = Produccion.objects.get(pk=pkproduccion)
    pkstarjas = []
    pksunicos = []
    for x in produccion.tarjaresultante_set.all():
        pkstarjas.append(x.pk)
        [pksunicos.append(y) for y in pkstarjas if y not in pksunicos]
    return pksunicos


def consulta_muestras_tarjasresultantes_cdc_calibres(listalotes):
    tarja_res = TarjaResultante.objects.filter(pk__in=listalotes)
    
    kilos_sin_calibre = 0    
    kilos_precalibre = 0
    kilos_18_20 = 0
    kilos_20_22 = 0
    kilos_23_25 = 0
    kilos_25_27 = 0
    kilos_27_30 = 0
    kilos_30_32 = 0
    kilos_32_34 = 0
    kilos_34_36 = 0
    kilos_36_40 = 0
    kilos_40_mas = 0
    
    for x in tarja_res:
        try:
            cc_tarja = CCTarjaResultante.objects.get(tarja=x.pk)
        except:
            cc_tarja = None
        
        if cc_tarja != None:
            if cc_tarja.calibre == '0':
                kilos_sin_calibre += x.peso -x.tipo_patineta
            elif cc_tarja.calibre == '1':
                kilos_precalibre += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '2':
                kilos_18_20 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '3':
                kilos_20_22 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '4':
                kilos_23_25 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '5':
                kilos_25_27 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '6':
                kilos_27_30 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '7':
                kilos_30_32 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '8':
                kilos_32_34 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '9':
                kilos_34_36 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '10':
                kilos_36_40 += x.peso - x.tipo_patineta
            elif cc_tarja.calibre == '11':
                kilos_40_mas += x.peso - x.tipo_patineta
        
    return {
            'sincalibre': kilos_sin_calibre,
            'precalibre': kilos_precalibre,
            'calibre_18_20': kilos_18_20,
            'calibre_20_22': kilos_20_22,
            'calibre_23_25': kilos_23_25,
            'calibre_25_27': kilos_25_27,
            'calibre_27_30': kilos_27_30,
            'calibre_30_32': kilos_30_32,
            'calibre_32_34': kilos_32_34,
            'calibre_34_36': kilos_34_36,
            'calibre_36_40': kilos_36_40,
            'calibre_40_mas': kilos_40_mas
            }

    
