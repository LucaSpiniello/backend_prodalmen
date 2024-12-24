from rest_framework import viewsets
from .models import *
from .serializers import *
from bodegas.models import *
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef, Q, Sum, Count, Subquery, Max,  F
from .funciones import *
from bodegas.funciones import *
from django.utils.timezone import make_aware, is_naive, now
from datetime import datetime, timedelta
# impoer CALIDAD_FRUTA from estados_modelos
CALIDAD_FRUTA = (
    ('0', 'Extra N°1'),
    ('1', 'Supreme'),
    ('2', 'Whole & Broken'),
    ('3', 'Sin Calidad'),
    ('4', 'Whole para Harina'),
)

class TipoEmbalajeViewSet(viewsets.ModelViewSet):
    queryset = TipoEmbalaje.objects.all()
    serializer_class = TipoEmbalajeSerializer
    


class EtiquetaEmbalajeViewSet(viewsets.ModelViewSet):
    queryset = EtiquetaEmbalaje.objects.all()
    serializer_class = EtiquetaEmbalajeSerializer

class EmbalajeViewSet(viewsets.ModelViewSet):
    queryset = Embalaje.objects.all()
    serializer_class = EmbalajeSerializer


    def retrieve(self, request,seleccion_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)
    
    @action(detail=True, methods=['GET'], url_path='pdf-entrada-embalaje')
    def pdf_entrada_embalaje(self, request, pk=None):
        embalaje = Embalaje.objects.filter(pk = pk).first()
        bins_en_embalaje = FrutaBodega.objects.filter(embalaje = embalaje)
        
        if not bins_en_embalaje:
            return Response({ "message": "No hay bins cargados aún"}, status=status.HTTP_400_BAD_REQUEST)
        
        resultados = []
        
        for bins in bins_en_embalaje:
            codigo_tarja = obtener_codigo_tarja_embalaje(bins)
            programa = obtener_programa_embalaje(bins)
            variedad = obtener_variedad_embalaje(bins)
            calibre = obtener_calibre_embalaje(bins)
            calidad = obtener_calidad_embalaje(bins)
            
            dic = {
                "codigo_tarja": codigo_tarja,
                "programa": programa,
                "variedad": variedad,
                "calibre": calibre,
                "calidad": calidad,
                "kilos_fruta": bins.bin_bodega.binbodega.kilos_fruta,
                "calle_bodega": bins.bin_bodega.binbodega.get_calle_bodega_display()
            }
            
            resultados.append(dic)
    
        serializer = EmbalajeSerializer(embalaje)
        
        return Response({
            "programa": serializer.data,
            "bines": resultados
        })
        
    @action(detail=True, methods=['GET'], url_path='pdf-salida-embalaje')
    def pdf_salida_embalaje(self, request, pk=None):
        embalaje = Embalaje.objects.filter(pk = pk).first()
        pallets = PalletProductoTerminado.objects.filter(embalaje = embalaje)
        bins_en_embalaje = FrutaBodega.objects.filter(embalaje = embalaje)
        variedades_unicas = set([obtener_variedad_embalaje(bin) for bin in bins_en_embalaje])
        variedad = 'Revueltas' if len(variedades_unicas) > 1 else variedades_unicas.pop()
        calibres_unicos = set([obtener_calibre_embalaje(bin) for bin in bins_en_embalaje])
        calibre = 'Indefinido' if len(calibres_unicos) > 1 else calibres_unicos.pop()
        calidad = embalaje.get_calidad_display()
        resultados = []
        
        if not pallets:
            return Response({ "message": "No hay bins cargados aún"}, status=status.HTTP_400_BAD_REQUEST)
        
        for pallet in pallets:
            dic = {
                "id": pallet.id,
                "codigo_pallet": pallet.codigo_pallet,
                "variedad": variedad,
                "calibre": calibre,
                "calidad": calidad,
                "kilos_fruta": obtener_kilos_fruta_pallet_embalaje(pallet),
                "fecha_creacion": pallet.fecha_creacion
            }
            
            resultados.append(dic)
            
        serializer = EmbalajeSerializer(embalaje)  
        return Response({
            "programa": serializer.data,
            "pallets": resultados
        })
            
    
    @action(detail=True, methods=['PATCH'])
    def bins_en_embalaje(self, request, pk=None):
        bins = request.data.get('bins', [])
        fruta_procesada_ids = []

        for bin in bins:
            bin_id = bin.get('id')
            if bin_id is not None:
                FrutaBodega.objects.filter(pk=bin_id).update(procesado=True)
                fruta_procesada_ids.append(bin_id)

        # Obtener los objetos actualizados
        fruta_procesada = FrutaBodega.objects.filter(pk__in=fruta_procesada_ids)

        # Serializar los objetos actualizados
        serializer = FrutaBodegaSerializer(fruta_procesada, many=True)

        # Devolver la respuesta con los datos serializados
        return Response(serializer.data)

    @action(detail = False, methods = ['GET'])
    def pallets_producto_terminados(self, request):
        embalaje = self.get_queryset().values_list('id', flat = True)
        
        cajas_subquery = CajasEnPalletProductoTerminado.objects.filter(pallet=OuterRef('pk'))
        pallets = PalletProductoTerminado.objects.annotate(
            has_cajas=Exists(cajas_subquery)
        ).filter(has_cajas=True, embalaje__in=embalaje)
        
        resultados = []
        
        for pallet in pallets:
            total_peso = 0
            cantidad_cajas = 0
            if pallet.cajasenpalletproductoterminado_set.exists():  # Verificar si hay cajas en el pallet
                print(f" cajas {pallet.cajasenpalletproductoterminado_set.all()}")
                for caja in pallet.cajasenpalletproductoterminado_set.all():
                    total_peso += caja.peso_x_caja * caja.cantidad_cajas
                    cantidad_cajas += caja.cantidad_cajas    
                    
            if total_peso == 0:
                continue
                  
            dic = {
                "id": pallet.id,
                "codigo_pallet": pallet.codigo_pallet,
                "calidad": pallet.embalaje.get_calidad_display(),
                "variedad": pallet.embalaje.get_variedad_display(),
                "calibre": pallet.embalaje.get_calibre_display(),
                "cantidad_cajas": cantidad_cajas,
                "peso_pallet": round(total_peso, 2)
            }
            
            resultados.append(dic)
        serializer = PalletProductoTerminadoBodegaSerializer(data = resultados, many = True)
        serializer.is_valid(raise_exception = True)
        return Response(serializer.data)
            
    
    @action(detail = False, methods = ['GET'])
    def historico_pallet(self, request):
        pallet_id = request.query_params.get('id')
        embalaje_ids = self.get_queryset().values_list('id', flat=True)
        pallet = PalletProductoTerminado.objects.filter(embalaje__in=embalaje_ids, pk=pallet_id).first()
        print(pallet)
        if not pallet:
            return Response({'error': 'PalletProductoTerminado no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PalletProductoTerminadoSerializer(pallet)

        # Preparar el historial para el pallet
        historico = pallet.historia.all()
        historico_data = []
        for record in historico:
            historico_data.append({
                'codigo_pallet': pallet.codigo_pallet,
                'fecha': record.history_date,
                'cambio': record.history_change_reason or 'No especificado',
                'tipo_cambio': record.history_type,
                'registrado_por': f'{record.history_user.first_name} {record.history_user.last_name}' if record.history_user else 'No disponible',
            })

        # Devolver tanto los detalles del pallet como su historial
        return Response(historico_data, status=status.HTTP_200_OK)
        
    def get_laborable_dates(self, start_date, end_date):
        date_list = []
        # Verificar si las fechas son el mismo día y es laborable
        if start_date == end_date and start_date.weekday() < 5:
            return [start_date]
        
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday are 0-4
                date_list.append(current_date)
            current_date += timedelta(days=1)  # Usa timedelta desde datetime
        return date_list

    @action(detail=True, methods=['POST'])
    def registrar_operario(self, request, pk=None):
        programa = self.get_object()
        operario_id = request.data.get('operario_id')
        skill_operario = request.data.get('skill_operario')

        operario = Operario.objects.get(pk=operario_id)
        OperariosEnEmbalaje.objects.create(
            programa=programa,
            operario=operario,
            skill_operario=skill_operario
        )
        return Response({'status': 'Operario registrado en el programa'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def asignar_dias_kilos(self, request, pk=None):
        embalaje = self.get_object()
        # Validar fechas de inicio y término del proceso
        if embalaje.fecha_inicio_embalaje:
            # Obtener operarios por skill
            operarios_programaph1 = OperariosEnEmbalaje.objects.filter(programa=embalaje, skill_operario='embalaje')
            # Calcular kilos totales de inputs
            start_date = embalaje.fecha_inicio_embalaje
            if not embalaje.fecha_termino_embalaje:
                end_date = datetime.now().date()
            else:
                end_date = embalaje.fecha_termino_embalaje

            laborable_dates = self.get_laborable_dates(start_date, end_date)
            # total_kilos_input = sum(bin.bin_bodega.kilos_bin for bin in FrutaBodega.objects.filter(embalaje=embalaje))

            for operario in operarios_programaph1:
                for laborable_date in laborable_dates:
                    pallets = PalletProductoTerminado.objects.filter(
                        embalaje=embalaje,
                        fecha_creacion__date=laborable_date
                    )

                    # Sumar manualmente los valores de peso_total_pallet para cada PalletProductoTerminado
                    total_kilos_dia_operario = sum(pallet.peso_total_pallet for pallet in pallets) or 0
                    DiaDeOperarioEmbalaje.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        kilos_dia=total_kilos_dia_operario
                    )

            return Response({'status': 'Días y kilos asignados a operarios'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Fechas de inicio o término no definidas'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'])
    def pdf_informe_embalaje(self, request):
        desde = request.data.get('desde').replace('Z', '')
        hasta = request.data.get('hasta').replace('Z', '')
        desde = datetime.strptime(desde, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta, '%Y-%m-%dT%H:%M:%S.%f')
        hoy = now().date()
        if desde.date() > hoy:
            programas_embalaje = Embalaje.objects.none()  
        else:
            programas_embalaje = Embalaje.objects.filter(
                Q(fecha_inicio_embalaje__gte=desde, fecha_termino_embalaje__lte=hasta) |  
                Q(fecha_termino_embalaje__isnull=True, fecha_inicio_embalaje__lte=hasta)
            )
            
        informe_programa = []
        for programa in programas_embalaje:
            bins_en_embalaje = FrutaBodega.objects.filter(embalaje = programa)
            pallets = PalletProductoTerminado.objects.filter(embalaje = programa, fecha_creacion__range=(desde, hasta))
            print(f"pallets {pallets}")
            variedades_unicas = set([obtener_variedad_embalaje(bin) for bin in bins_en_embalaje])
            variedad = 'Revueltas' if len(variedades_unicas) > 1 else variedades_unicas.pop()
            calibres_unicos = set([obtener_calibre_embalaje(bin) for bin in bins_en_embalaje])
            calibre = 'Indefinido' if len(calibres_unicos) > 1 else calibres_unicos.pop()
            calidades_unicas = set([obtener_calidad_embalaje(bin) for bin in bins_en_embalaje])
            calidad = 'MultiCalidades' if len(calidades_unicas) > 1 else calidades_unicas.pop()
            
            if calidad != 'MultiCalidades':
                calidad = dict(CALIDAD_FRUTA).get(calidad)
            
            if not pallets:
                return Response([])
            
            for pallet in pallets:
                dic = {
                    "codigo_pallet": pallet.codigo_pallet,
                    "variedad": variedad,
                    "calibre": calibre,
                    "kilos_fruta": obtener_kilos_fruta_pallet_embalaje(pallet),
                    "fecha_creacion": pallet.fecha_creacion,
                    "programa": programa.pk,
                    "producto": programa.get_tipo_producto_display(),
                    "calidad": calidad
                }
                
                informe_programa.append(dic)
        return Response(informe_programa)

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
            programas_embalaje = Embalaje.objects.none()
        else:
            programas_embalaje = Embalaje.objects.filter(
                Q(fecha_inicio_embalaje__gte=desde, fecha_termino_embalaje__lte=hasta) |  
                Q(fecha_termino_embalaje__isnull=True, fecha_inicio_embalaje__lte=hasta),
                operarios__in = [operario]
            )
        operario = Operario.objects.get(pk=operario)
        for programa in programas_embalaje:
            pallets = PalletProductoTerminado.objects.filter(embalaje = programa, fecha_creacion__range=(desde, hasta))
            if not pallets:
                continue
            
            kilos_fruta = sum(pallet.peso_total_pallet for pallet in pallets)
            pago_embalaje_x_kilo = SkillOperario.objects.get(operario = operario, tipo_operario = 'embalaje').pago_x_kilo
            neto = kilos_fruta * pago_embalaje_x_kilo
            dic = {
                "programa": f'Embalaje N° {programa.pk}',
                "kilos": kilos_fruta,
                "neto": round(kilos_fruta * pago_embalaje_x_kilo),
                "type": "embalaje"
            }
            resultados_informe.append(dic)
        return Response(resultados_informe)

    @action(detail=False, methods=['POST'])
    def pdf_informe_operario_resumido(self, request):
        desde = request.data.get('desde').replace('Z', '')
        hasta = request.data.get('hasta').replace('Z', '')
        
        desde = datetime.strptime(desde, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta, '%Y-%m-%dT%H:%M:%S.%f')

        resultados_informe = []
        hoy = now().date()
        if desde.date() > hoy:
            programas_embalaje = Embalaje.objects.none()
        else:
            programas_embalaje = Embalaje.objects.filter(
                Q(fecha_inicio_embalaje__gte=desde, fecha_termino_embalaje__lte=hasta) |  
                Q(fecha_termino_embalaje__isnull=True, fecha_inicio_embalaje__lte=hasta)
            )
        
        for programa in programas_embalaje:
            operarios_en_embalaje = OperariosEnEmbalaje.objects.filter(programa=programa, skill_operario='embalaje')
            for operario in operarios_en_embalaje:
                kilos_in_prod = DiaDeOperarioEmbalaje.objects.filter(operario=operario, dia__gte=desde, dia__lte=hasta).aggregate(Sum('kilos_dia'))['kilos_dia__sum'] or 0
                pago_por_kilo_operario = SkillOperario.objects.get(operario=operario.operario, tipo_operario='embalaje').pago_x_kilo
                if kilos_in_prod > 0:
                    dic = {
                        "operario": f'{operario.operario.nombre} {operario.operario.apellido}',
                        "kilos": kilos_in_prod,
                        "neto": kilos_in_prod * pago_por_kilo_operario
                    }
                    resultados_informe.append(dic)
        resultados_agrupados = {}
        for resultado in resultados_informe:
            operario = resultado['operario']
            if operario in resultados_agrupados:
                resultados_agrupados[operario]['kilos'] += resultado['kilos']
                resultados_agrupados[operario]['neto'] += resultado['neto']
            else:
                resultados_agrupados[operario] = resultado

        # Convertir el diccionario agrupado de vuelta a una lista
        resultados_informe = list(resultados_agrupados.values())
        return Response(resultados_informe)
                        
            
        

    @action(detail=True, methods=['GET'])
    def lista_operarios_dias(self, request, pk=None):
        programa = self.get_object()
        operarios_en_produccion = OperariosEnEmbalaje.objects.filter(programa=programa)
        serializer = OperariosEnEmbalajeSerializer(operarios_en_produccion, many=True)
        return Response(serializer.data)
    
    # @action(detail=True, methods=['GET'])
    # def metricas_en_tiempo_real(self, request, pk=None):
    #     programa = self.get_object()
    #     now = datetime.now()

    #     # Asegurarse de que both now y fecha_inicio tengan zona horaria o ninguna de las dos
    #     if is_naive(now):
    #         now = make_aware(now)
        
    #     if programa.fecha_inicio_proceso:
    #         if isinstance(programa.fecha_inicio_proceso, datetime):
    #             fecha_inicio = programa.fecha_inicio_proceso
    #         else:
    #             fecha_inicio = datetime.combine(programa.fecha_inicio_proceso, datetime.min.time())

    #         if is_naive(fecha_inicio):
    #             fecha_inicio = make_aware(fecha_inicio)
    #     else:
    #         return Response({'detail': 'La producción no ha comenzado.'}, status=status.HTTP_400_BAD_REQUEST)

    #     # Total de kilos de fruta en LotesPrograma
    #     total_kilos_fruta = sum(bin.bin_bodega.kilos_bin for bin in BinsParaProceso.objects.filter(proceso=programa))

    #     # Total de kilos de fruta procesada (pre_limpia)
    #     kilos_procesados_programaph = sum(bin.bin_bodega.kilos_bin for bin in BinsParaProceso.objects.filter(proceso=programa, procesado=True))

    #     # Kilos de fruta resultante (despelo)
    #     kilos_resultantes_programaph = BinResultanteProceso.objects.filter(
    #         proceso=programa,
    #         # esta_eliminado=False
    #     ).aggregate(total_kilos=Sum(F('peso') - F('tipo_patineta')))['total_kilos'] or 0

    #     # Rendimiento de producción
    #     rendimiento_produccion = (kilos_resultantes_programaph / kilos_procesados_programaph) * 100 if kilos_procesados_programaph else 0

    #     # Kilos procesados por operario por día
    #     operarios_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)
    #     kilos_por_operario = []
    #     for operario in operarios_produccion:
    #         kilos_dia = DiaDeOperarioProcesoPH.objects.filter(
    #             operario=operario,
    #             dia=now.date()
    #         ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
    #         kilos_por_operario.append({
    #             'operario': operario.operario.nombre,
    #             'kilos_dia': kilos_dia
    #         })

    #     # Tasa de producción por hora
    #     horas_trabajadas = (now - fecha_inicio).total_seconds() / 3600
    #     tasa_produccion_hora = kilos_procesados_programaph / horas_trabajadas if horas_trabajadas > 0 else 0

    #     # Eficiencia del operario
    #     eficiencia_operarios = []
    #     for operario in operarios_produccion:
    #         eficiencia = DiaDeOperarioProcesoPH.objects.filter(
    #             operario=operario
    #         ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
    #         eficiencia_operarios.append({
    #             'operario': operario.operario.nombre,
    #             'eficiencia': eficiencia
    #         })

    #     metricas = {
    #         'total_kilos_fruta': total_kilos_fruta,
    #         'kilos_procesados_programaph': kilos_procesados_programaph,
    #         'kilos_resultantes_programaph': kilos_resultantes_programaph,
    #         'rendimiento_produccion': rendimiento_produccion,
    #         'kilos_por_operario': kilos_por_operario,
    #         'tasa_produccion_hora': tasa_produccion_hora,
    #         'eficiencia_operarios': eficiencia_operarios
    #     }

    #     return Response(metricas, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['GET'])
    def dias_trabajados_operario(self, request, pk=None):
        programa = self.get_object()
        operario_id = request.query_params.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        operario = get_object_or_404(Operario, pk=operario_id)
        operarios_en_produccion = OperariosEnEmbalaje.objects.filter(programa=programa, operario=operario).first()
        
        if not operarios_en_produccion:
            return Response({'error': 'No se encontraron registros de trabajo para este operario en la producción especificada'}, status=status.HTTP_404_NOT_FOUND)

        dias_trabajados = DiaDeOperarioEmbalaje.objects.filter(operario=operarios_en_produccion)
        serializer = DiaDeOperarioEmbalajeSerializer(dias_trabajados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'])
    def actualizar_ausente(self, request, pk=None):
        dia_id = request.data.get('dia_id')
        if not dia_id:
            return Response({'error': 'dia_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        dia = get_object_or_404(DiaDeOperarioEmbalaje, pk=dia_id)
        
        serializer = DiaDeOperarioEmbalajeSerializer(dia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['DELETE'])
    def eliminar_operario(self, request, pk=None):
        programa = self.get_object()
        operario_id = request.data.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            operario = get_object_or_404(OperariosEnEmbalaje, programa=programa, pk=operario_id)
            if operario:
                operario.delete()
                return Response({'status': 'Operario eliminado de la producción'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'No se encontro el operario en la producción'}, status=status.HTTP_400_BAD_REQUEST)
          
    # @action(detail=True, methods=['GET'])
    # def estado_termino_programa(self, request, pk=None):
    #     programa = self.get_object()
    #     tarjas = programa.binparaproceso_set.all()
    #     cc_tarja_resultante = CCBinResultanteProcesoPH.objects.filter(bin_resultante__in=tarjas)
        
    #     # Verificar control de calidad de las tarjas
    #     tarjas_sin_cc = [cc for cc in cc_tarja_resultante if cc.estado_cc != '0']
    #     if len(tarjas_sin_cc) == 0:
    #         cc_estado_text = "Todas las tarjas tienen su control de calidad."
    #     else:
    #         cc_estado_text = f"{len(tarjas_sin_cc)} tarjas sin control de calidad."
        
    #     # Verificar operarios en producción
    #     operarios_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)
    #     if operarios_produccion.exists():
    #         operarios_estado_text = f"Se han agregado {operarios_produccion.count()} operarios a esta producción."
    #     else:
    #         operarios_estado_text = "No hay operarios registrados."

    #     # Verificar estado de los lotes programa
    #     lotes_programa = BinsParaProceso.objects.filter(proceso=programa)
    #     lotes_pendientes = lotes_programa.filter(procesado=False).count()
    #     if lotes_pendientes == 0:
    #         lotes_estado_text = "Todos los lotes programa han sido procesados."
    #     else:
    #         lotes_estado_text = f"{lotes_pendientes} lotes pendientes de procesamiento."

    #     # Construir la respuesta
    #     response_data = {
    #         "estado_control_calidad": cc_estado_text,
    #         "estado_operarios": operarios_estado_text,
    #         "estado_lotes": lotes_estado_text
    #     }
        
    #     return Response(response_data, status=status.HTTP_200_OK)
    
    # @action(detail=True, methods=['GET'])
    # def estado_cierre_programa(self, request, pk=None):
    #     programa = self.get_object()
    #     operarios_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)

    #     estado_dias = []
    #     for operario in operarios_produccion:
    #         dias_trabajados = DiaDeOperarioProgramaPH.objects.filter(operario=operario)
    #         if dias_trabajados.exists():
    #             total_dias = dias_trabajados.count()
    #             total_kilos = dias_trabajados.aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
    #             estado_dias.append({
    #                 'nombre_operario': f'{operario.operario.nombre} {operario.operario.apellido}',
    #                 'dias_trabajados': total_dias,
    #                 'total_kilos': total_kilos,
    #                 #'mensaje': f'El operario {operario.operario.nombre} {operario.operario.apellido} tiene en esta producción {total_dias} días creados con un total de {total_kilos} kilos.'
    #             })
    #         else:
    #             estado_dias.append({
    #                 'nombre_operario': f'{operario.operario.nombre} {operario.operario.apellido}',
    #                 'dias_trabajados': 0,
    #                 'total_kilos': 0,
    #                 #'mensaje': f'El operario {operario.operario.nombre} {operario.operario.apellido} no tiene días asignados en este programa de producción.'
    #             })

    #     return Response({'estado_dias': estado_dias}, status=status.HTTP_200_OK)    


class FrutaBodegaViewSet(viewsets.ModelViewSet):
    queryset = FrutaBodega.objects.all()
    serializer_class = FrutaBodegaSerializer
    
    def list(self,request, embalaje_pk=None):
        queryset= self.get_queryset().filter(embalaje=embalaje_pk)
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
        
        
    @action(detail = False, methods = ['POST'])
    def agregar_fruta_bodega(self, request, embalaje_pk=None):
        bins = request.data.get('bins', [])
        embalaje = Embalaje.objects.filter(pk = embalaje_pk)
        binbodega = BinBodega.objects.filter(pk__in = [bin.get('id') for bin in bins])
        variedades_unicas = set([get_variedad(bin) for bin in binbodega])
        variedad = 'RV' if len(variedades_unicas) > 1 else variedades_unicas.pop()
        calibre_unicas = set([get_calibre(bin) for bin in binbodega])
        calibre = '0' if len(calibre_unicas) > 1 else calibre_unicas.pop()
        calidades_unicas = set()
        for bin in bins:
            calidades_unicas.add(bin["calidad"])
        calidad = 'MultiCalidades' if len(calidades_unicas) > 1 else calidades_unicas.pop()
        tipo_producto_unico = set([(bin) for bin in binbodega])
        tipo_producto = clasificar_bines_por_tipo(tipo_producto_unico)
        embalaje.update(variedad = variedad, calibre = calibre, calidad = calidad, tipo_producto = tipo_producto)    
    
        for bin_data in bins:
            binbodega = BinBodega.objects.filter(pk = bin_data.get('id')).first()
            bin_obj = FrutaBodega.objects.create(
                embalaje_id = embalaje_pk,
                bin_bodega = binbodega
            )
            bin_obj.save()

        return Response({"mensaje": "Bins registrados exitosamente"}, status=status.HTTP_201_CREATED)
        
    
    
    

# class OperariosEnEmbalajeViewSet(viewsets.ModelViewSet):
#     queryset = OperariosEnEmbalaje.objects.all()
#     serializer_class = OperariosEnEmbalajeSerializer
        
#     def list(self,request, embalaje_pk=None):
#         queryset= self.get_queryset().filter(embalaje=embalaje_pk)
#         serializer= self.get_serializer_class()(queryset, many=True)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['GET'])
#     def lista_filtrada_por_operario_embalaje(self, request, embalaje_pk=None):
#         embalaje = get_object_or_404(Embalaje, pk = embalaje_pk)
#         operarios_agregados = OperariosEnEmbalaje.objects.filter(embalaje=embalaje).values(
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
        
#         serializer = OperariosAgregadosEmbalajeSerializer(data = list(operarios_agregados), many = True)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data)
    
    
#     @action(detail=False, methods=['GET'], url_path='lista_diaria_operario')
#     def lista_detalle_dias_operario_embalaje(self, request, embalaje_pk=None):
#         embalaje = get_object_or_404(Embalaje, pk = embalaje_pk)

#         lista_operario = OperariosEnEmbalaje.objects.filter(embalaje = embalaje, operario__rut = request.query_params.get('rut'))
#         serializer = OperariosEnEmbalajeSerializer(lista_operario, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


#     @action(detail=False, methods=['DELETE'])
#     def eliminar_registro_dia_por_rut(self, request, embalaje_pk=None):
#         embalaje = get_object_or_404(Embalaje, pk = embalaje_pk)
#         OperariosEnEmbalaje.objects.filter(embalaje = embalaje, operario__rut = request.data.get('rut')).delete()
#         return Response(status = status.HTTP_204_NO_CONTENT )
    
    
#     @action(detail=False, methods=['DELETE'])
#     def eliminar_registro_dia_por_rut_y_id(self, request, embalaje_pk=None):
#         embalaje = get_object_or_404(Embalaje, pk = embalaje_pk)
#         OperariosEnEmbalaje.objects.filter(embalaje = embalaje, operario__rut = request.data.get('rut'), id = request.data.get('id')).delete()
#         return Response(status = status.HTTP_204_NO_CONTENT )

class PalletProductoTerminadoViewSet(viewsets.ModelViewSet):
    queryset = PalletProductoTerminado.objects.all()
    serializer_class = PalletProductoTerminadoSerializer
    
    def list(self,request, embalaje_pk=None):
        queryset= self.get_queryset().filter(embalaje=embalaje_pk)
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'], url_path='get_all_pallets')
    def get_all_pallets(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class CajasEnPalletProductoTerminadoViewSet(viewsets.ModelViewSet):
    queryset = CajasEnPalletProductoTerminado.objects.all()
    serializer_class = CajasEnPalletProductoTerminadoSerializer
    
    def list(self,request, pallet_pk=None):
        queryset= self.get_queryset().filter(pallet=pallet_pk)
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class PalletProductoTerminadoParaPedidoViewSet(viewsets.ModelViewSet):
    queryset = PalletProductoTerminado.objects.all()
    serializer_class = PalletProductoTerminadoParaPedidoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # Obtener el queryset inicial
        
        # Filtrar los objetos cuya peso_total_pallet (peso_total_ptt) sea mayor que 0
        filtered_queryset = [obj for obj in queryset if obj.peso_total_pallet > 0]

        # Serializar los datos filtrados
        serializer = self.get_serializer(filtered_queryset, many=True)
        
        # Retornar la respuesta serializada
        return Response(serializer.data)