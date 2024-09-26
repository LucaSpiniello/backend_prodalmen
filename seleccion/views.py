from django.shortcuts import render
from python_utils import raise_exception
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from yaml import serialize
from .serializers import *
from .models import *
from cuentas.models import *
from django.db.models import Q, Sum, Count, Subquery, Max,  F
from bodegas.models import *
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.contenttypes.models import *
from .funciones import * 
from collections import defaultdict
from datetime import datetime
from rest_framework.exceptions import NotFound
from django.utils.timezone import make_aware, is_naive, now
from datetime import datetime, timedelta, time
# impoer TIPO_RESULTANTE_SELECCION from estados_modelo
from .estados_modelo import TIPO_RESULTANTE_SELECCION


class SeleccionViewSet(viewsets.ModelViewSet):
    queryset = Seleccion.objects.all()
    serializer_class = SeleccionSerializer
    
    @action(detail=True, methods=['GET'])
    def subproducto_metricas(self, request, pk=None):
        obj = self.get_object()
        subproductos = SubProductoOperario.objects.filter(seleccion=obj).first()
        
        if not subproductos:
            return Response({"message": "No hay métricas disponibles para esta selección."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Accede a todos los SubproductosEnBin vinculados a este SubProductoOperario
        kilos_por_operario = subproductos.subproductosenbin_set.values(
            'subproducto_operario__operario__id', 
            'subproducto_operario__operario__nombre',
            'subproducto_operario__id'
        ).annotate(total_kilos=Sum('peso'))
        
        # Preparar una lista para devolver los resultados.
        resultados = []
        for operario in kilos_por_operario: 
            # Buscando el objeto de SubProductoOperario para obtener el display del tipo de subproducto
            operario_obj = SubProductoOperario.objects.get(id=operario['subproducto_operario__id'])
            resultados.append({
                "nombre": operario['subproducto_operario__operario__nombre'],
                "total_kilos": operario['total_kilos'],
                "tipo_subproducto": operario_obj.get_tipo_subproducto_display(),  # Usando get_FOO_display() para obtener el valor legible
                "subproducto_id": operario['subproducto_operario__id']
            })

        return Response(resultados)

        # create a get enp to get all the proccesed bins
    @action(detail=False, methods=['GET'], url_path='get_all_info')
    def get_all_info(self, request, seleccion_pk=None):

        selecciones = Seleccion.objects.filter(estado_programa='4')
    
        resultado_selecciones = []
        for i in selecciones:
            produccion = i.produccion
            bins_procesados = BinsPepaCalibrada.objects.filter(seleccion=i)
            variedad = bins_procesados.first().binbodega.cdc_tarja.get_variedad_display()

            productor = "Sin productor"
            comercializador = "Sin comercializador"
            guias_recepcion = "Sin guia"
            if produccion is not None:
                primer_lote = produccion.lotes.all().first()
                
                if primer_lote and primer_lote.guia_patio and primer_lote.guia_patio.lote_recepcionado:
                    productor = primer_lote.guia_patio.lote_recepcionado.guiarecepcion.productor.nombre
                    comercializador = primer_lote.guia_patio.lote_recepcionado.guiarecepcion.comercializador.nombre
                    
                    # Crear un conjunto para almacenar guías de recepción únicas
                    guias_recepcion_set = {
                        lote.guia_patio.lote_recepcionado.guiarecepcion.pk
                        for lote in produccion.lotes.all()
                        if lote.guia_patio and lote.guia_patio.lote_recepcionado
                    }
                    
                    guias_recepcion = ", ".join(str(guia) for guia in sorted(guias_recepcion_set))

            calibres = calcular_kilos_por_calibre_tarjas_seleccionadas(i.pk)
            fruta_resultante = consulta_bins_seleccionados(i.pk)
            controles = calcular_control_sub_productos_tarjas_seleccionadas(i.pk)
            fruta_resultante = fruta_resultante['fruta_resultante']
            fecha_termino = i.fecha_termino_proceso
            resultado_selecciones.append({
                "seleccion": i.pk,
                "variedad": variedad,
                "productor": productor,
                "comercializador": comercializador,
                "calibres": calibres,
                "fruta_resultante": fruta_resultante,
                "guia_recepcion": guias_recepcion,
                "perdidas": controles[0],
                "fecha_termino": fecha_termino,
            })
        return Response(resultado_selecciones)
    
    @action(detail = False, methods = ['GET'])
    def subproductos_lista(self, request):
        subproducto = SubProductoOperario.objects.all()
        serializer = SubProductoOperarioSerializer(subproducto, many = True)
        return Response(serializer.data)
    
    @action(detail = True, methods = ['GET'])
    def subproductos_en_seleccion(self, request, pk=None):
        seleccion = self.get_object()
        subproducto = SubProductoOperario.objects.filter(seleccion=seleccion)
        serializer = SubProductoOperarioSerializer(subproducto, many = True)
        return Response(serializer.data)
    
    @action(detail = True, methods = ['GET'])
    def subproductos_para_agrupacion(self, request, pk=None):
        seleccion = self.get_object()
        subproducto = SubProductoOperario.objects.filter(en_bin = False, seleccion=seleccion)
        serializer = SubProductoOperarioSerializer(subproducto, many = True)
        return Response(serializer.data)
    
    @action(detail = False, methods = ['GET'])
    def ultimos_programas_seleccion(self, request):
        programas = Seleccion.objects.all()[:2]
        serializer = SeleccionSerializer(programas, many = True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def rendimiento_bin_seleccion(self, request, pk=None):
        
        CCRendimientoSeleccion = calcula_calibres_fruta_calibrada(pk)
        CCTarjaSeleccionadaRendimiento = calcula_calibres_fruta_seleccionada(pk)
        BinFrutaCalibradaRendimiento = consulta_bins_ingresados_a_seleccion(pk)
        BinsFrutaResultanteRendimiento = consulta_bins_seleccionados(pk)
        porcentaje_proyeccion_entrante = porcentaje(BinFrutaCalibradaRendimiento['fruta_resultante'], BinFrutaCalibradaRendimiento['pepa_sana_proyectada'])
        porcentaje_proyeccion_saliente = porcentaje(BinsFrutaResultanteRendimiento['fruta_resultante'], BinsFrutaResultanteRendimiento['pepa_sana_proyectada'])
        porcentaje_diferencia = porcentaje_proyeccion_saliente - porcentaje_proyeccion_entrante
        KilosBinFrutaCalibradaRendimiento = calcular_kilos_por_calibre_recepcionada(pk)
        KilosBinsFrutaResultanteRendimiento = calcular_kilos_por_calibre_saliente(pk)
        
        serializerEntrante = PepaCalibradaRendimientoSerializer(CCRendimientoSeleccion)
        serializerSaliente = TarjaSeleccionadaRendimientoSerializer(CCTarjaSeleccionadaRendimiento)
        serializerBinFrutaCalibrada = BinsFrutaCalibradaRendimientoSerializer(BinFrutaCalibradaRendimiento)
        serializerBinFrutaResultante = BinsFrutaResultanteRendimientoSerializer(BinsFrutaResultanteRendimiento)
        serializerKilosEntrante = PepaCalibradaRendimientoConSinCalibreSerializer(KilosBinFrutaCalibradaRendimiento)
        serializerKilosSaliente = TarjaSeleccionadaRendimientoConSinCalibreSerializer(KilosBinsFrutaResultanteRendimiento)
        
        return Response({
            "cc_rendimiento_entrantes": serializerEntrante.data,
            "cc_rendimiento_salientes": serializerSaliente.data,
            "bin_fruta_calibrada_rendimiento": serializerBinFrutaCalibrada.data,
            "bin_fruta_resultante_rendimiento": serializerBinFrutaResultante.data,
            "porcentaje_proyeccion_entrante": porcentaje_proyeccion_entrante,
            "porcentaje_proyeccion_saliente": porcentaje_proyeccion_saliente,
            "diferencia": porcentaje_diferencia,
            "kilos_entrantes": serializerKilosEntrante.data,
            "kilos_salientes": serializerKilosSaliente.data
            
            }, status = status.HTTP_200_OK)
      
    @action(detail=False, methods=['POST'])
    def pdf_informe_seleccion(self, request):
        desde = request.data.get('desde').replace('Z', '')
        hasta = request.data.get('hasta').replace('Z', '')
        
        if not desde or not hasta:
            return Response({'error': 'Los campos "desde" y "hasta" son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        desde = datetime.strptime(desde, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta, '%Y-%m-%dT%H:%M:%S.%f')
        
        hoy = now().date()
        if desde.date() > hoy:
            programas_seleccion = Seleccion.objects.none()  
        else:
            programas_seleccion = Seleccion.objects.filter(
                Q(fecha_inicio_proceso__gte=desde, fecha_termino_proceso__lte=hasta) |  
                Q(fecha_termino_proceso__isnull=True, fecha_inicio_proceso__lte=hasta)
            )
            
        resultados_informe = []

        for programa in programas_seleccion:
            tarjas_seleccionadas = TarjaSeleccionada.objects.filter(seleccion = programa.pk, fecha_creacion__gte = desde, fecha_creacion__lte = hasta)
            cc_tarja_seleccionada = CCTarjaSeleccionada.objects.filter(tarja_seleccionada__in = tarjas_seleccionadas).first()
            for tarja in tarjas_seleccionadas:
                kilostarja = (tarja.peso - tarja.tipo_patineta)
                producto = "Pepa Seleccionada"
                if tarja.tipo_resultante == "1":
                    producto = "Descarte Sea"
                elif tarja.tipo_resultante == "3":
                    producto = "Whole & Broken para PH"
                dic = {
                    "tarja": tarja.codigo_tarja,
                    "programa": f"Selección N° {programa.pk}",
                    "producto": producto,
                    "variedad": f'{cc_tarja_seleccionada.get_variedad_display()}', # type: ignore
                    "calibre": f'{cc_tarja_seleccionada.get_calibre_display()}', # type: ignore
                    "calidad": f'{cc_tarja_seleccionada.get_calidad_fruta_display()}',
                    "kilos": f'{kilostarja}'   
                }
                resultados_informe.append(dic)
                
        serializer = PDFInformeSeleccionSerializer(data = resultados_informe, many=True)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status = status.HTTP_200_OK)
        
    @action(detail=False, methods=['POST'])
    def pdf_kilos_por_operario(self, request):
        operario = request.data.get('operario')
        desde = request.data.get('desde').replace('Z', '')
        hasta = request.data.get('hasta').replace('Z', '')
        
        desde = datetime.strptime(desde, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta, '%Y-%m-%dT%H:%M:%S.%f')
            
        resultados_informe = []
        hoy = now().date()
        if desde.date() > hoy:
            programas_seleccion = Seleccion.objects.none()  
        else:
            programas_seleccion = Seleccion.objects.filter(
                (Q(fecha_inicio_proceso__gte=desde, fecha_termino_proceso__lte=hasta) |  
                Q(fecha_termino_proceso__isnull=True, fecha_inicio_proceso__lte=hasta)
                ),
                operarios__in = [operario]
            )
        
        operario = Operario.objects.get(pk = operario)     
        for programa in programas_seleccion:
            subproducto = SubProductoOperario.objects.filter(seleccion = programa.pk, operario = operario, fecha_creacion__gte = desde, fecha_creacion__lte = hasta)

            for producto in subproducto:
                pago_x_kilo_operario = SkillOperario.objects.get(operario = operario, tipo_operario = 'sub_prod').pago_x_kilo
                dic = {
                    "tarja": f'Sub Producto N° {producto.pk}',
                    "programa": f'{producto.seleccion}',
                    "tipo_resultante": producto.get_tipo_subproducto_display(),
                    "fecha_registro": producto.fecha_creacion,
                    "kilos": producto.peso,
                    "neto": round(producto.peso * pago_x_kilo_operario),
                    "type": "subproducto"
                }
                
                resultados_informe.append(dic)

            # get total kilos seleccinoados
            operario_select = OperariosEnSeleccion.objects.filter(seleccion = programa.pk, operario = operario).first()
            kilos_in_prod = DiaDeOperarioSeleccion.objects.filter(operario = operario_select, dia__gte = desde, dia__lte = hasta).aggregate(Sum('kilos_dia'))['kilos_dia__sum'] or 0
            fecha_seleccion = DiaDeOperarioSeleccion.objects.filter(operario = operario_select, dia__gte = desde, dia__lte = hasta).aggregate(Max('dia'))['dia__max']

  
            tarja_seleccionada = TarjaSeleccionada.objects.filter(seleccion = programa.pk, tipo_resultante = '3', fecha_creacion__gte = desde, fecha_creacion__lte = hasta)
            existe_whole = True if tarja_seleccionada.first() else False 
            
            tipo_resultante = 'Whole y Pepa Seleccionada' if existe_whole else 'Pepa Seleccionada'

            if kilos_in_prod > 0 and fecha_seleccion:   
                fecha_seleccion = datetime.combine(fecha_seleccion, time(23, 59))
                pago_x_kilo_operario = SkillOperario.objects.get(operario = operario, tipo_operario = 'seleccion').pago_x_kilo
                print(f"Operaio: {operario.nombre} {operario.apellido} Kilos: {kilos_in_prod} Pago: {pago_x_kilo_operario}")
                dic = {
                    "tarja": f'Selección N° {programa.pk}',
                    "programa": f'{programa}',
                    "tipo_resultante": tipo_resultante,
                    "fecha_registro": fecha_seleccion,
                    "kilos": kilos_in_prod,
                    "neto": round(kilos_in_prod * pago_x_kilo_operario),
                    "type": "seleccion"
                }
                resultados_informe.append(dic)
        serializer = PDFInformeKilosXOperarioSerializer(data = resultados_informe, many = True)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            {
                "operario": f'{operario.nombre} {operario.apellido}',
                "pago_x_kilos": serializer.data
            },
            status = status.HTTP_200_OK)
            
    @action(detail=False, methods=['POST'])
    def pdf_informe_operario_resumido(self, request):
        desde = request.data.get('desde').replace('Z', '')
        hasta = request.data.get('hasta').replace('Z', '')
        
        desde = datetime.strptime(desde, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta, '%Y-%m-%dT%H:%M:%S.%f')
        
        resultados_informe = defaultdict(list)
        
        hoy = now().date()
        if desde.date() > hoy:
            programas_seleccion = Seleccion.objects.none()  
        else:
            programas_seleccion = Seleccion.objects.filter(
                Q(fecha_inicio_proceso__gte=desde, fecha_termino_proceso__lte=hasta) |  
                Q(fecha_termino_proceso__isnull=True, fecha_inicio_proceso__lte=hasta)
            )
        
        informe_agrupado = []
        
        for programa in programas_seleccion:

            subproductos = SubProductoOperario.objects.filter(seleccion=programa.pk)
            for subproducto in subproductos:
                resultados_informe[subproducto.operario.id].append(subproducto)

            operarios_seleccion = OperariosEnSeleccion.objects.filter(seleccion = programa.pk, skill_operario = 'seleccion')
            for operario in operarios_seleccion:
                kilos_in_prod = DiaDeOperarioSeleccion.objects.filter(operario = operario, dia__gte = desde, dia__lte = hasta).aggregate(Sum('kilos_dia'))['kilos_dia__sum'] or 0
                pago_por_kilo_operario = SkillOperario.objects.get(operario = operario.operario, tipo_operario = 'seleccion').pago_x_kilo
                if kilos_in_prod > 0 :
                    dic = {
                        "operario": f'{operario.operario.nombre} {operario.operario.apellido}',
                        "kilos": kilos_in_prod,
                        "neto": kilos_in_prod * pago_por_kilo_operario,
                        "detalle": "Selección"
                    }
                    informe_agrupado.append(dic)


        for operario_id, subproductos in resultados_informe.items():

            kilos_totales = sum(
                subproducto.peso 
                for subproducto in subproductos 
                if desde <= subproducto.fecha_creacion <= hasta
            )
            pago_x_kilo_operario = SkillOperario.objects.get(operario=subproductos[0].operario, tipo_operario='sub_prod').pago_x_kilo
            pago_neto = kilos_totales * pago_x_kilo_operario
            
            dic = {
                "operario": f'{subproductos[0].operario.nombre} {subproductos[0].operario.apellido}',
                "kilos": kilos_totales,
                "neto": pago_neto,
                "detalle": "SubProducto"
            }
            informe_agrupado.append(dic)
                
        serializer = PDFInformeOperarioResumidoSerializer(data=informe_agrupado, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def pdf_documento_entrada_en_seleccion(self, request, pk=None):
        resultados_informe = []
        bins_en_seleccion = BinsPepaCalibrada.objects.filter(seleccion=pk)
        seleccion = Seleccion.objects.get(pk=pk)
        programa_produccion = seleccion.produccion.pk
        for bins in bins_en_seleccion:
            cc_bin = bins.binbodega.cdc_tarja
            codigo_tarja = bins.binbodega.codigo_tarja_bin
            
            peso_total_muestra = cc_bin.cantidad_muestra or 1 
            
            # Calcular porcentajes
            trozo_pct = (cc_bin.trozo / peso_total_muestra) * 100
            picada_pct = (cc_bin.picada / peso_total_muestra) * 100
            hongo_pct = (cc_bin.hongo / peso_total_muestra) * 100
            insecto_pct = (cc_bin.daño_insecto / peso_total_muestra) * 100
            dobles_pct = (cc_bin.dobles / peso_total_muestra) * 100
            p_goma_pct = (cc_bin.punto_goma / peso_total_muestra) * 100
            basura_pct = (cc_bin.basura / peso_total_muestra) * 100
            mezcla_pct = (cc_bin.mezcla_variedad / peso_total_muestra) * 100
            color_pct = (cc_bin.fuera_color / peso_total_muestra) * 100
            goma_pct = (cc_bin.goma / peso_total_muestra) * 100
            pepa_pct = (cc_bin.pepa_sana / peso_total_muestra) * 100
            
            dic = {
                "numero_programa": f'Sel N° {pk}',
                "codigo_tarja": f'{codigo_tarja}',
                "variedad": cc_bin.get_variedad_display(),
                "calibre": cc_bin.get_calibre_display(),
                "trozo": round(trozo_pct, 1),
                "picada": round(picada_pct, 1),
                "hongo": round(hongo_pct, 1),
                "insecto": round(insecto_pct, 1),
                "dobles": round(dobles_pct, 1),
                "p_goma": round(p_goma_pct, 1),
                "basura": round(basura_pct, 1),
                "mezcla": round(mezcla_pct, 1),
                "color": round(color_pct, 1),
                "goma": round(goma_pct, 1),
                "pepa": round(pepa_pct, 1),
                "kilos": round(bins.binbodega.kilos_bin, 1),   
                "colectado": f'{True if cc_bin.estado_cc == "3" else False}',
                'programa_produccion': programa_produccion
            }
            
            resultados_informe.append(dic)
        
        serializer = PDFDetalleEntradaSeleccionSerializer(data=resultados_informe, many=True)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def pdf_documento_salida_en_seleccion(self, request, pk = None):
        resultados_informe = []
        resultados_subproductos = []
        bins_en_seleccion = TarjaSeleccionada.objects.filter(seleccion = pk)
        subProductos = SubProductoOperario.objects.filter(seleccion = pk)
        
        for producto in subProductos:
            dic = {
                "operario": f'{producto.operario.nombre} {producto.operario.apellido}',
                "tipo_producto": f'{producto.get_tipo_subproducto_display()}',
                "peso": producto.peso
            }
            
            resultados_subproductos.append(dic)
        
        for bins in bins_en_seleccion:
            cc_bin = None
            cc_bin = CCTarjaSeleccionada.objects.filter(pk = bins.pk).first()
            peso_total_muestra = cc_bin.cantidad_muestra or 1  # Evitar división por cero en caso de datos faltantes

            trozo_pct = (cc_bin.trozo / peso_total_muestra) * 100
            picada_pct = (cc_bin.picada / peso_total_muestra) * 100
            hongo_pct = (cc_bin.hongo / peso_total_muestra) * 100
            insecto_pct = (cc_bin.daño_insecto / peso_total_muestra) * 100
            dobles_pct = (cc_bin.dobles / peso_total_muestra) * 100
            p_goma_pct = (cc_bin.punto_goma / peso_total_muestra) * 100
            basura_pct = (cc_bin.basura / peso_total_muestra) * 100
            mezcla_pct = (cc_bin.mezcla_variedad / peso_total_muestra) * 100
            color_pct = (cc_bin.fuera_color / peso_total_muestra) * 100
            goma_pct = (cc_bin.goma / peso_total_muestra) * 100
            pepa_pct = (cc_bin.pepa_sana / peso_total_muestra) * 100
            calidad = cc_bin.get_calidad_fruta_display()
            tipo_resultante = cc_bin.tarja_seleccionada.tipo_resultante
            # Buscar el nombre asociado al código en la tupla TIPO_RESULTANTE_SELECCION
            tipo = next((nombre for codigo, nombre in TIPO_RESULTANTE_SELECCION if codigo == tipo_resultante), "Tipo desconocido")
            if cc_bin != None:
                kilosnetos = (bins.peso-bins.tipo_patineta)
                dic = {
                "codigo_tarja": f'{bins.codigo_tarja}',
                "variedad": cc_bin.get_variedad_display() if cc_bin != None else 'Sin Variedad',
                "calibre": cc_bin.get_calibre_display() if cc_bin != None else 'Sin Calibre',
                "trozo": round(trozo_pct, 1),
                "picada": round(picada_pct, 1),
                "hongo": round(hongo_pct, 1),
                "insecto": round(insecto_pct, 1),
                "dobles": round(dobles_pct, 1),
                "p_goma": round(p_goma_pct, 1),
                "basura": round(basura_pct, 1),
                "mezcla": round(mezcla_pct, 1),
                "color": round(color_pct, 1),
                "goma": round(goma_pct, 1),
                "pepa": round(pepa_pct, 1),
                "kilos": round(kilosnetos,1),
                "calidad": calidad,
                "tipo": tipo
                }
            else:
                return Response({ "message": "No se ha encontrado control de calidad"}, status = status.HTTP_400_BAD_REQUEST)
            
            resultados_informe.append(dic)
        
        serializer = PDFDetalleSalidaSeleccionSerializer(data = resultados_informe, many = True)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            "bines": serializer.data,
            "subproductos": resultados_subproductos
            }, status = status.HTTP_200_OK)   

    def get_laborable_dates(self, start_date, end_date):
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday are 0-4
                date_list.append(current_date)
            current_date += timedelta(days=1)
        return date_list
    
    @action(detail=True, methods=['POST'])
    def registrar_operario(self, request, pk=None):
        seleccion = self.get_object()
        operario_id = request.data.get('operario_id')
        skill_operario = request.data.get('skill_operario')

        operario = get_object_or_404(Operario, pk=operario_id)
        OperariosEnSeleccion.objects.create(
            seleccion=seleccion,
            operario=operario,
            skill_operario=skill_operario
        )
        return Response({'status': 'Operario registrado en la selección'}, status=status.HTTP_201_CREATED)
   
    @action(detail=True, methods=['POST'])
    def asignar_dias_kilos(self, request, pk=None):
        seleccion = self.get_object()
        if seleccion.fecha_inicio_proceso:
            
            start_date = seleccion.fecha_inicio_proceso
            if not seleccion.fecha_termino_proceso:
                end_date = datetime.now().date()
            else:
                end_date = seleccion.fecha_termino_proceso

            laborable_dates = self.get_laborable_dates(start_date, end_date)

            operarios_seleccion_1 = OperariosEnSeleccion.objects.filter(seleccion=seleccion, skill_operario='seleccion')

            # Calcular total de kilos input manualmente usando la propiedad kilos_bin

            for operario in operarios_seleccion_1:
                for laborable_date in laborable_dates:
                    total_kilos = TarjaSeleccionada.objects.filter(
                        seleccion=seleccion,
                        fecha_creacion__date=laborable_date,
                        tipo_resultante__in=['2', '3'],
                        esta_eliminado=False
                    ).annotate(
                        peso_neto=F('peso') - F('tipo_patineta')  # Restar tipo_patineta del peso
                    ).aggregate(
                        total_kilos=Sum('peso_neto')  # Sumar los pesos netos
                    )['total_kilos'] or 0 
                    DiaDeOperarioSeleccion.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        defaults={'kilos_dia': total_kilos}
                    )
            operarios_seleccion_sub_productos = OperariosEnSeleccion.objects.filter(seleccion=seleccion, skill_operario='sub_prod')
    
            for operario in operarios_seleccion_sub_productos:
                for laborable_date in laborable_dates:
                    total_kilos = SubProductoOperario.objects.filter(
                        seleccion=seleccion,
                        fecha_creacion__date=laborable_date,
                        operario=operario.operario,
                    ).aggregate(
                        total_kilos=Sum('peso')
                    )['total_kilos'] or 0
                    DiaDeOperarioSeleccion.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        defaults={'kilos_dia': total_kilos}
                    )

            return Response({'status': 'Días y kilos asignados a operarios'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Fechas de inicio o término no definidas'}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['GET'])
    def lista_operarios_dias(self, request, pk=None):
        seleccion = self.get_object()
        operarios_en_seleccion = OperariosEnSeleccion.objects.filter(seleccion=seleccion)
        serializer = DetalleOperariosEnSeleccionSerializer(operarios_en_seleccion, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def dias_trabajados_operario(self, request, pk=None):
        seleccion = self.get_object()
        operario_id = request.query_params.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        operario = get_object_or_404(Operario, pk=operario_id)
        operarios_en_seleccion = OperariosEnSeleccion.objects.filter(seleccion=seleccion, operario=operario).first()
        
        if not operarios_en_seleccion:
            return Response({'error': 'No se encontraron registros de trabajo para este operario en el seleccion especificado'}, status=status.HTTP_404_NOT_FOUND)

        dias_trabajados = DiaDeOperarioSeleccion.objects.filter(operario=operarios_en_seleccion)
        serializer = DiaDeOperarioSeleccionSerializer(dias_trabajados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def actualizar_ausente(self, request, pk=None):
        dia_id = request.data.get('dia_id')
        if not dia_id:
            return Response({'error': 'dia_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        dia = get_object_or_404(DiaDeOperarioSeleccion, pk=dia_id)
        
        serializer = DiaDeOperarioSeleccionUpdateSerializer(dia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def eliminar_operario(self, request, pk=None):
        seleccion = self.get_object()
        operario_id = request.data.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            operario = get_object_or_404(OperariosEnSeleccion, seleccion=seleccion, pk=operario_id)
            if operario:
                operario.delete()
                return Response({'status': 'Operario eliminado de la producción'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'No se encontro el operario en la producción'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'])
    def estado_termino_programa(self, request, pk=None):
        seleccion = self.get_object()
        tarjas = seleccion.tarjaseleccionada_set.filter(esta_eliminado=False)
        cc_tarja_resultante = CCTarjaSeleccionada.objects.filter(tarja_seleccionada__in=tarjas)
        
        # Verificar control de calidad de las tarjas
        tarjas_sin_cc = [cc for cc in cc_tarja_resultante if cc.estado_cc != '3']
        if len(tarjas_sin_cc) == 0:
            cc_estado_text = "Todas las tarjas tienen su control de calidad."
        else:
            cc_estado_text = f"{len(tarjas_sin_cc)} tarjas sin control de calidad."
        
        # Verificar operarios en producción
        operarios_seleccion = OperariosEnSeleccion.objects.filter(seleccion=seleccion)
        if operarios_seleccion.exists():
            operarios_estado_text = f"Se han agregado {operarios_seleccion.count()} operarios a este seleccion."
        else:
            operarios_estado_text = "No hay operarios registrados."

        # Verificar estado de los lotes programa
        lotes_programa = BinsPepaCalibrada.objects.filter(seleccion=seleccion)
        lotes_pendientes = lotes_programa.filter(bin_procesado=False).count()
        if lotes_pendientes == 0:
            lotes_estado_text = "Todas las tarjas del programa han sido procesados."
        else:
            lotes_estado_text = f"{lotes_pendientes} Tarjas pendientes de procesamiento."

        # Construir la respuesta
        response_data = {
            "estado_control_calidad": cc_estado_text,
            "estado_operarios": operarios_estado_text,
            "estado_lotes": lotes_estado_text
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def estado_cierre_programa(self, request, pk=None):
        seleccion = self.get_object()
        operarios_seleccion = OperariosEnSeleccion.objects.filter(seleccion=seleccion)

        estado_dias = []
        for operario in operarios_seleccion:
            dias_trabajados = DiaDeOperarioSeleccion.objects.filter(operario=operario)
            if dias_trabajados.exists():
                total_dias = dias_trabajados.count()
                total_kilos = dias_trabajados.aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
                estado_dias.append({
                    'nombre_operario': f'{operario.operario.nombre} {operario.operario.apellido}',
                    'dias_trabajados': total_dias,
                    'total_kilos': total_kilos,
                    #'mensaje': f'El operario {operario.operario.nombre} {operario.operario.apellido} tiene en esta producción {total_dias} días creados con un total de {total_kilos} kilos.'
                })
            else:
                estado_dias.append({
                    'nombre_operario': f'{operario.operario.nombre} {operario.operario.apellido}',
                    'dias_trabajados': 0,
                    'total_kilos': 0,
                    #'mensaje': f'El operario {operario.operario.nombre} {operario.operario.apellido} no tiene días asignados en este programa de producción.'
                })

        return Response({'estado_dias': estado_dias}, status=status.HTTP_200_OK)
                  
    
class BinsPepaCalibradaViewSet(viewsets.ModelViewSet):
    queryset = BinsPepaCalibrada.objects.all()
    serializer_class = BinsPepaCalibradaSerializer
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return BinsPepaCalibradaSerializer
        return DetalleBinsPepaCalibradaSerializer
    
    def list(self,request, seleccion_pk=None):
        queryset= self.get_queryset().filter(seleccion=seleccion_pk)
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,seleccion_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def registrar_bins_seleccion(self, request, seleccion_pk=None):
        bins = request.data.get('bins', [])
        
        for bin_data in bins:
            program_number = bin_data.get('programa').split(' ')[-1]
            pkbinbodega = bin_data.get('id')
            binbodega = get_object_or_404(BinBodega, pk=pkbinbodega)
            bin_obj = BinsPepaCalibrada.objects.create(
                seleccion_id=seleccion_pk,
                binbodega=binbodega
            )
            bin_obj.save()

        return Response({"mensaje": "Bins registrados exitosamente"}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['POST'], url_path='procesado-masivo')
    def procesar_masivamente_bines(self, request, seleccion_pk=None):
        bines = request.data.get('bins', [])
        BinsPepaCalibrada.objects.filter(seleccion = seleccion_pk, pk__in = [bin.get('id') for bin in bines]).update(bin_procesado = True)
        return Response({ "message": 'Procesados Exitosamente' }, status=status.HTTP_200_OK)

    
class TarjaSeleccionadaViewSet(viewsets.ModelViewSet):
    queryset = TarjaSeleccionada.objects.all()
    serializer_class = TarjaSeleccionadaSerializer
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return TarjaSeleccionadaSerializer
        return DetalleTarjaSeleccionadaSerializer
    
    def list(self,request, seleccion_pk=None):
        queryset= self.get_queryset().filter(seleccion=seleccion_pk, esta_eliminado= False)
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,seleccion_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)
    
    @action(detail=False, methods=['PUT', 'PATCH'])
    def eliminar_tarja_seleccion(self, request, seleccion_pk=None,):
        seleccion = get_object_or_404(Seleccion, pk=seleccion_pk)
        queryset = get_object_or_404(self.get_queryset(), seleccion=seleccion, pk = request.data.get('id'))
        if queryset.cc_tarja != True:
            queryset.esta_eliminado = request.data.get('esta_eliminado')
            if (queryset.tipo_resultante == 'descarte'):
                ct = ContentType.objects.get_for_model(BodegaG3)
                bodegag1 = BodegaG3.objects.filter(seleccion = queryset.pk).first()
                BinBodega.objects.filter(id_binbodega = bodegag1.id, tipo_binbodega = ct).update(estado_binbodega = '1') # type: ignore
            elif (queryset.tipo_resultante == 'pepa_seleccion'):
                ct = ContentType.objects.get_for_model(BodegaG4)
                bodegag2 = BodegaG4.objects.filter(seleccion = queryset.pk).first()
                BinBodega.objects.filter(id_binbodega = bodegag2.id, tipo_binbodega = ct).update(estado_binbodega = '1') # type: ignore
            queryset.save()
            serializer = self.get_serializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({ 'message': 'No se puede eliminar la tarja una vez se a calibrado '}, status=status.HTTP_400_BAD_REQUEST)    
    

class SubProductoOperarioViewSet(viewsets.ModelViewSet):
    queryset = SubProductoOperario.objects.all()
    serializer_class = SubProductoOperarioSerializer
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return SubProductoOperarioSerializer
        return DetalleSubProductoOperarioSerializer
    
    def list(self,request, seleccion_pk=None):
        queryset= self.get_queryset().filter(seleccion=seleccion_pk)
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,seleccion_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)

class BinSubProductoSeleccionViewSet(viewsets.ModelViewSet):
    queryset = BinSubProductoSeleccion.objects.annotate(
        total_pesoa=Sum('subproductosenbin__peso')
    ).filter(Q(total_pesoa__gte=0, total_pesoa__lt=500) | Q(total_pesoa__isnull=True))
    serializer_class = BinSubProductoSeleccionSerializer

    @action(detail=True, methods=['POST'])
    def agrupar_subproductos(self, request, pk=None):
        subproductos = request.data.get('subproductos', [])
        max_peso = 500
        
        bin_producto = get_object_or_404(BinSubProductoSeleccion, pk=pk)

        # Calcular el peso total de los subproductos ya en el bin
        peso_total_actual = bin_producto.subproductosenbin_set.aggregate(total_pesoa=Sum('peso'))['total_pesoa'] or 0
        
        subproductos_en_bin_ids = []

        for subproducto_data in subproductos:
            peso = subproducto_data.get('peso', 0)

            if peso_total_actual + peso > max_peso:
                peso_restante = max_peso - peso_total_actual
                return Response({'detail': 'El peso total excede el límite permitido de 500 kg.', 'restante': peso_restante}, status=status.HTTP_400_BAD_REQUEST)
            
            peso_total_actual += peso

            subproducto_operario = get_object_or_404(SubProductoOperario, pk=subproducto_data['id'])
            subproductos_en_bin_ids.append(subproducto_operario.pk)
            
            SubproductosEnBin.objects.get_or_create(
                subproducto_operario_id=subproducto_operario.pk,
                bin_subproducto_id=bin_producto.pk,
                peso=peso
            )

        SubProductoOperario.objects.filter(pk__in=subproductos_en_bin_ids).update(en_bin=True)
        
        variedades = [
            subproducto.subproducto_operario.tipo_subproducto
            for subproducto in bin_producto.subproductosenbin_set.all() 
        ]
        variedades_unicas = set(variedades)
        if len(variedades_unicas) > 1:
            variedad = 'RV'
        elif len(variedades_unicas) == 1:
            variedad = variedades_unicas.pop()
        else:
            variedad = '---'

        bin_producto.variedad = variedad
        bin_producto.save()
        bin_producto_serializer = BinSubProductoSeleccionSerializer(bin_producto)
        
        return Response(bin_producto_serializer.data)
    
    @action(detail=True, methods=['GET'])
    def historico(self, request, pk=None):
        
        CHANGE_TYPE_MAP = {
        '+': 'Creación',
        '~': 'Actualización',
        '-': 'Eliminación'
            }
        try:
            bin_instance = BinSubProductoSeleccion.objects.get(pk=pk)
            historico = bin_instance.historia.all()
            historico_data = []

            for record in historico:
                if record.history_change_reason:
                    historico_data.append({
                        'fecha': record.history_date,
                        'cambio': record.history_change_reason, 
                        'tipo_patineta': record.get_tipo_patineta_display(),
                        'registrado_por': f'{record.registrado_por.first_name} {record.registrado_por.last_name}',
                    })

            return Response(historico_data, status=status.HTTP_200_OK)
        except BinSubProductoSeleccion.DoesNotExist:
            return Response({'error': 'BinSubProductoSeleccion no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        bin_producto = self.get_object()
        
        if bin_producto.subproductosenbin_set.exists():
            return Response({'detail': 'No se puede eliminar el bin porque tiene subproductos registrados.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)
        
    
# class OperarioEnSeleccionViewSet(viewsets.ModelViewSet):
#     queryset = OperariosEnSeleccion.objects.all()
#     serializer_class = OperariosEnSeleccionSerializer
    
#     def get_queryset(self):
#         user = self.request.user
#         try:
#             anio = PersonalizacionPerfil.objects.get(usuario= user).anio
#             if anio == 'Todo':
#                 return self.queryset
#             else:
#                 qs = OperariosEnSeleccion.objects.filter(fecha_creacion__year = anio)
#                 return qs
#         except:
#             return self.queryset
        
#     def get_serializer_class(self):        
#         if self.action in ["create", "update", "partial_update", "destroy"]:
#             return OperariosEnSeleccionSerializer
#         return DetalleOperariosEnSeleccionSerializer
        
#     def retrieve(self, request,seleccion_pk=None, pk=None):
#         seleccion_instance = get_object_or_404(Seleccion, pk=seleccion_pk)
#         seleccion = get_object_or_404(self.get_queryset(),seleccion=seleccion_instance, pk=pk)
#         serializer = self.get_serializer(seleccion)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['GET'])
#     def lista_filtrada_por_operario_seleccion(self, request, seleccion_pk=None):
#         seleccion = get_object_or_404(Seleccion, pk = seleccion_pk)
#         operarios_agregados = OperariosEnSeleccion.objects.filter(seleccion=seleccion).values(
#             'operario',  # Incluir el ID del operario
#             'operario__id',
#             'operario__rut',  # Obtener el RUT del operario
#             'operario__nombre',  # Obtener el nombre del operario
#             'operario__apellido',  # Obtener el apellido del operario
#             'skill_operario'
#         ).annotate(
#             total_kilos_producidos=Sum('kilos'),  # Sumar los kilos producidos por el operario
#             dias_trabajados=Count('dia')
#         )
        
#         serializer = OperariosAgregadosSeleccionSerializer(data = list(operarios_agregados), many = True)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['POST'])
#     def lista_detalle_dias_operario_seleccion(self, request, seleccion_pk=None):
#         seleccion = get_object_or_404(Seleccion, pk = seleccion_pk)

#         lista_operario = OperariosEnSeleccion.objects.filter(seleccion = seleccion, operario__rut = request.data.get('rut'))
#         serializer = DetalleOperariosEnSeleccionSerializer(lista_operario, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     @action(detail=False, methods=['DELETE'])
#     def eliminar_registro_dia_por_rut(self, request, seleccion_pk=None):
#         seleccion = get_object_or_404(Seleccion, pk = seleccion_pk)
#         OperariosEnSeleccion.objects.filter(seleccion = seleccion, operario__rut = request.data.get('rut')).delete()
#         return Response(status = status.HTTP_204_NO_CONTENT )
    
#     @action(detail=False, methods=['DELETE'])
#     def eliminar_registro_dia_por_rut_y_id(self, request, seleccion_pk=None):
#         seleccion = get_object_or_404(Seleccion, pk = seleccion_pk)
#         OperariosEnSeleccion.objects.filter(seleccion = seleccion, operario__rut = request.data.get('rut'), id = request.data.get('id')).delete()
#         return Response(status = status.HTTP_204_NO_CONTENT )