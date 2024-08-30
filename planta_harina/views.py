from rest_framework import viewsets
from .models import ProgramaPH, BinParaPrograma, BinResultantePrograma, OperariosEnProgramaPH, RechazoPrograma, VariablesProgramaPH
from .serializers import *
from rest_framework.decorators import action
from bodegas.models import *
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404
from .funciones import *
from django.db.models import DateField, Sum, Count, Q, Sum, Count, Subquery, Max,  F
from django.db.models.functions import Cast, TruncDate
from django.utils.timezone import make_aware, is_naive
from datetime import datetime, timedelta




class ProgramaPHViewSet(viewsets.ModelViewSet):
    queryset = ProgramaPH.objects.all()
    serializer_class = ProgramaPHSerializer
    
    @action(detail=False, methods=['GET'], url_path = 'pdf-programas')
    def pdf_programas(self, request):
        desde_str = request.query_params.get('desde').replace('Z', '')
        hasta_str = request.query_params.get('hasta').replace('Z', '')
        desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
        
        programas = ProgramaPH.objects.filter(Q(fecha_creacion__gte=desde) & Q(fecha_creacion__lte=hasta))
        bins_resultantes = BinResultantePrograma.objects.filter(programa__in = programas)
        kilos_totales_procesados = bins_resultantes.filter(esta_eliminado=False).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )
        print(kilos_totales_procesados)
        
        resultado = []
        
        for bin in bins_resultantes:
            programa = f'{bin.programa.get_tipo_programa_display().capitalize()} N° {bin.programa.pk}'
            dic = {
                "bin": bin.codigo_tarja,
                "programa": programa,
                "kilos": round(bin.peso - bin.tipo_patineta, 2),
                "fecha_creacion": bin.fecha_creacion
            }
            resultado.append(dic)
            
        serializer = PDFProgramasPHSerializer(data = resultado, many = True)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            "kilos_totales": kilos_totales_procesados['total_kilos'],
            "resultado": serializer.data
        })
    
    @action(detail=True, methods=['GET'], url_path = 'pdf-documento-entrada')
    def pdf_entrada(self, request, pk):

        programa =  ProgramaPH.objects.filter(pk = pk).first()
        bin_ingresados = BinParaPrograma.objects.filter(programa = programa)
    
        resultado = []
        
        kilos_totales = 0

        for bin in bin_ingresados:
            kilos_totales += bin.bin_bodega.binbodega.kilos_fruta
            cc_tarja = CCTarjaSeleccionada.objects.get(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion)
            programa = f'Selección N° {bin.programa.pk}'
            dic = {
                "bin": bin.bin_bodega.binbodega.seleccion.codigo_tarja,
                "programa": programa,
                "cc_tarja":f'{cc_tarja.get_variedad_display()} / {cc_tarja.get_calibre_display()} / {cc_tarja.get_calidad_fruta_display()}',
                "kilos": round(bin.bin_bodega.binbodega.kilos_fruta),
                "procesado": bin.procesado
            }
            resultado.append(dic)
        print(kilos_totales)
        
        serializer = PDFDocumentoEntradaProgramaPHSerializer(data = resultado, many = True)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'kilos_totales': kilos_totales,
            'bins_resultantes': serializer.data
        })
    
    @action(detail=True, methods=['GET'], url_path = 'pdf-documento-salida')
    def pdf_salida(self, request, pk):

        programa =  ProgramaPH.objects.filter(pk = pk).first()
        bins_resultantes = BinResultantePrograma.objects.filter(programa = programa)
        
        kilos_totales_procesados = bins_resultantes.filter(esta_eliminado=False).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )
        
        resultado = []


        for bin in bins_resultantes:
            cc_tarja = CCBinResultanteProgramaPH.objects.get(bin_resultante = bin)
            dic = {
                "bin": bin.codigo_tarja,
                "estado": bin.get_estado_bin_display(),
                "humedad": f'{cc_tarja.humedad} %',
                "piel_aderida": f'{cc_tarja.piel_aderida} %',
                "calidad": 'Sin Calidad',
                "kilos": round(bin.peso - bin.tipo_patineta, 2),
            }
            resultado.append(dic)
        
        serializer = PDFDocumentoSalidaProgramaPHSerializer(data = resultado, many = True)
        serializer.is_valid(raise_exception=True)
        
        
        return Response({
            'programa': self.get_serializer(programa).data,
            "kilos_totales": kilos_totales_procesados['total_kilos'],
            'bins_resultantes': serializer.data
        })

    def get_laborable_dates(self, start_date, end_date):
        date_list = []
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
        OperariosEnProgramaPH.objects.create(
            programa=programa,
            operario=operario,
            skill_operario=skill_operario
        )
        return Response({'status': 'Operario registrado en el programa'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def asignar_dias_kilos(self, request, pk=None):
        programa = self.get_object()
        
        # Validar fechas de inicio y término del proceso
        if programa.fecha_inicio_programa and programa.fecha_termino_programa:
            start_date = programa.fecha_inicio_programa
            end_date = programa.fecha_termino_programa

            # Obtener las fechas laborables
            laborable_dates = self.get_laborable_dates(start_date, end_date)
            num_laborable_days = len(laborable_dates)

            # Obtener operarios por skill
            operarios_programaph1 = OperariosEnProgramaPH.objects.filter(programa=programa, skill_operario='p_harina')
            
            num_operarios_programaph1 = operarios_programaph1.count()

            # Calcular kilos totales de inputs
            total_kilos_input = sum(bin.bin_bodega.kilos_bin for bin in BinParaPrograma.objects.filter(programa=programa))


            kilos_por_dia_programaph1  = total_kilos_input / (num_laborable_days * num_operarios_programaph1) if num_operarios_programaph1 > 0 else 0
            for operario in operarios_programaph1:
                for laborable_date in laborable_dates:
                    DiaDeOperarioProgramaPH.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        kilos_dia=kilos_por_dia_programaph1
                    )


            return Response({'status': 'Días y kilos asignados a operarios'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Fechas de inicio o término no definidas'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def lista_operarios_dias(self, request, pk=None):
        programa = self.get_object()
        operarios_en_produccion = OperariosEnProgramaPH.objects.filter(programa=programa)
        serializer = OperariosEnProgramaPHSerializer(operarios_en_produccion, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def metricas_en_tiempo_real(self, request, pk=None):
        programa = self.get_object()
        now = datetime.now()

        # Asegurarse de que both now y fecha_inicio tengan zona horaria o ninguna de las dos
        if is_naive(now):
            now = make_aware(now)
        
        if programa.fecha_inicio_programa:
            if isinstance(programa.fecha_inicio_programa, datetime):
                fecha_inicio = programa.fecha_inicio_programa
            else:
                fecha_inicio = datetime.combine(programa.fecha_inicio_programa, datetime.min.time())

            if is_naive(fecha_inicio):
                fecha_inicio = make_aware(fecha_inicio)
        else:
            return Response({'detail': 'La producción no ha comenzado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Total de kilos de fruta en LotesPrograma
        total_kilos_fruta = BinParaPrograma.objects.filter(
            programa=programa,
            #esta_eliminado=False
        ).aggregate(total_kilos=Sum('bin_bodega__kilos_bin'))['total_kilos'] or 0

        # Total de kilos de fruta procesada (pre_limpia)
        kilos_procesados_programaph = sum(bin.bin_bodega.kilos_bin for bin in BinParaPrograma.objects.filter(programa=programa))

        # Kilos de fruta resultante (despelo)
        kilos_resultantes_programaph = BinResultantePrograma.objects.filter(
            programa=programa,
            # esta_eliminado=False
        ).aggregate(total_kilos=Sum(F('peso') - F('tipo_patineta')))['total_kilos'] or 0

        # Rendimiento de producción
        rendimiento_produccion = (kilos_resultantes_programaph / kilos_procesados_programaph) * 100 if kilos_procesados_programaph else 0

        # Kilos procesados por operario por día
        operarios_produccion = OperariosEnProgramaPH.objects.filter(programa=programa)
        kilos_por_operario = []
        for operario in operarios_produccion:
            kilos_dia = DiaDeOperarioProgramaPH.objects.filter(
                operario=operario,
                dia=now.date()
            ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
            kilos_por_operario.append({
                'operario': operario.operario.nombre,
                'kilos_dia': kilos_dia
            })

        # Tasa de producción por hora
        horas_trabajadas = (now - fecha_inicio).total_seconds() / 3600
        tasa_produccion_hora = kilos_procesados_programaph / horas_trabajadas if horas_trabajadas > 0 else 0

        # Eficiencia del operario
        eficiencia_operarios = []
        for operario in operarios_produccion:
            eficiencia = DiaDeOperarioProgramaPH.objects.filter(
                operario=operario
            ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
            eficiencia_operarios.append({
                'operario': operario.operario.nombre,
                'eficiencia': eficiencia
            })

        metricas = {
            'total_kilos_fruta': total_kilos_fruta,
            'kilos_procesados_programaph': kilos_procesados_programaph,
            'kilos_resultantes_programaph': kilos_resultantes_programaph,
            'rendimiento_produccion': rendimiento_produccion,
            'kilos_por_operario': kilos_por_operario,
            'tasa_produccion_hora': tasa_produccion_hora,
            'eficiencia_operarios': eficiencia_operarios
        }

        return Response(metricas, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['GET'])
    def dias_trabajados_operario(self, request, pk=None):
        programa = self.get_object()
        operario_id = request.query_params.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        operario = get_object_or_404(Operario, pk=operario_id)
        operarios_en_produccion = OperariosEnProgramaPH.objects.filter(programa=programa, operario=operario).first()
        
        if not operarios_en_produccion:
            return Response({'error': 'No se encontraron registros de trabajo para este operario en la producción especificada'}, status=status.HTTP_404_NOT_FOUND)

        dias_trabajados = DiaDeOperarioProgramaPH.objects.filter(operario=operarios_en_produccion)
        serializer = DiaDeOperarioProgramaPHSerializer(dias_trabajados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'])
    def actualizar_ausente(self, request, pk=None):
        dia_id = request.data.get('dia_id')
        if not dia_id:
            return Response({'error': 'dia_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        dia = get_object_or_404(DiaDeOperarioProgramaPH, pk=dia_id)
        
        serializer = DiaDeOperarioProgramaPHSerializer(dia, data=request.data, partial=True)
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
            operario = get_object_or_404(OperariosEnProgramaPH, programa=programa, pk=operario_id)
            if operario:
                operario.delete()
                return Response({'status': 'Operario eliminado de la producción'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'No se encontro el operario en la producción'}, status=status.HTTP_400_BAD_REQUEST)
          
    @action(detail=True, methods=['GET'])
    def estado_termino_programa(self, request, pk=None):
        programa = self.get_object()
        tarjas = programa.binresultanteprograma_set.all()
        cc_tarja_resultante = CCBinResultanteProgramaPH.objects.filter(bin_resultante__in=tarjas)
        
        # Verificar control de calidad de las tarjas
        tarjas_sin_cc = [cc for cc in cc_tarja_resultante if cc.estado_cc != '0']
        if len(tarjas_sin_cc) == 0:
            cc_estado_text = "Todas las tarjas tienen su control de calidad."
        else:
            cc_estado_text = f"{len(tarjas_sin_cc)} tarjas sin control de calidad."
        
        # Verificar operarios en producción
        operarios_produccion = OperariosEnProgramaPH.objects.filter(programa=programa)
        if operarios_produccion.exists():
            operarios_estado_text = f"Se han agregado {operarios_produccion.count()} operarios a esta producción."
        else:
            operarios_estado_text = "No hay operarios registrados."

        # Verificar estado de los lotes programa
        lotes_programa = BinParaPrograma.objects.filter(programa=programa)
        lotes_pendientes = lotes_programa.filter(procesado=False).count()
        if lotes_pendientes == 0:
            lotes_estado_text = "Todos los lotes programa han sido procesados."
        else:
            lotes_estado_text = f"{lotes_pendientes} lotes pendientes de procesamiento."

        # Construir la respuesta
        response_data = {
            "estado_control_calidad": cc_estado_text,
            "estado_operarios": operarios_estado_text,
            "estado_lotes": lotes_estado_text
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def estado_cierre_programa(self, request, pk=None):
        programa = self.get_object()
        operarios_produccion = OperariosEnProgramaPH.objects.filter(programa=programa)

        estado_dias = []
        for operario in operarios_produccion:
            dias_trabajados = DiaDeOperarioProgramaPH.objects.filter(operario=operario)
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


class BinParaProgramaViewSet(viewsets.ModelViewSet):
    queryset = BinParaPrograma.objects.all()
    serializer_class = BinParaProgramaSerializer

    
    @action(detail = False, methods=['POST'])
    def registrar_bins(self, request, pks_bins = None, programa_pk = None):
        bins = request.data.get('bins', [])
        programa_ph = ProgramaPH.objects.filter(pk = programa_pk).first()
        for bin in bins:
            id_bin = bin.get('id')
            bins = BinBodega.objects.filter(pk = id_bin).first()
            BinParaPrograma.objects.update_or_create(programa = programa_ph, bin_bodega = bins)
        return Response({ "message": 'Creados Exitosamente' }, status=status.HTTP_201_CREATED)
    
    @action(detail = False, methods = ['POST'])
    def procesado_masivo(self, request, programa_pk = None):
        bins = request.data.get('bins', [])
        programa = ProgramaPH.objects.filter(pk = programa_pk).first()
        BinParaPrograma.objects.filter(programa = programa, pk__in = [bin.get('id') for bin in bins]).update(procesado = True)
        return Response({ "message": 'Procesados Exitosamente' }, status=status.HTTP_200_OK)
        
    def list(self, request, programa_pk=None):
        queryset = self.queryset.filter(programa = programa_pk) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
class BinResultanteProgramaViewSet(viewsets.ModelViewSet):
    queryset = BinResultantePrograma.objects.all()
    serializer_class = BinResultanteProgramaSerializer
    
    def list(self, request, programa_pk=None):
        queryset = self.queryset.filter(programa = programa_pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RechazoProgramaViewSet(viewsets.ModelViewSet):
    queryset = RechazoPrograma.objects.all()
    serializer_class = RechazoProgramaSerializer
    
    @action(detail=False, methods=['get'])
    def metricas(self, request, programa_pk=None):
        programa = RechazoPrograma.objects.filter(programa=programa_pk).first()
        if programa is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        rechazos = get_rechazos_agrupados(programa.id)
        return Response(rechazos, status=status.HTTP_200_OK)
    
    def list(self, request, programa_pk=None):
        queryset = self.queryset.filter(programa = programa_pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class VariablesProgramaPHViewSet(viewsets.ModelViewSet):
    lookup_field = 'programa__pk'
    queryset = VariablesProgramaPH.objects.all()
    serializer_class = VariablesProgramaPHSerializer
    
    def list(self, request, programa_pk=None):
        queryset = self.queryset.filter(programa = programa_pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


### Proceso PH ###

class ProcesoPHViewSet(viewsets.ModelViewSet):
    queryset = ProcesoPH.objects.all()
    serializer_class = ProcesoPHSerializer
    
    # @action(detail=False, methods=['GET'], url_path = 'pdf-procesos')
    # def pdf_proceso(self, request):
    #     desde_str = request.query_params.get('desde').replace('Z', '')
    #     hasta_str = request.query_params.get('hasta').replace('Z', '')
    #     desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
    #     hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
        
    #     proceso = ProcesoPH.objects.filter(Q(fecha_creacion__gte=desde) & Q(fecha_creacion__lte=hasta))
    #     bins_resultantes = BinResultanteProceso.objects.filter(proceso__in = proceso)
    #     kilos_totales_procesados = bins_resultantes.filter(esta_eliminado=False).aggregate(
    #         total_kilos=Sum(F('peso') - F('tipo_patineta'))
    #     )
    #     print(kilos_totales_procesados)
        
    #     resultado = []
        
    #     for bin in bins_resultantes:
    #         proceso = f'{bin.proceso.get_tipo_proceso_display().capitalize()} N° {bin.proceso.pk}'
    #         dic = {
    #             "bin": bin.codigo_tarja,
    #             "programa": proceso,
    #             "kilos": round(bin.peso - bin.tipo_patineta, 2),
    #             "fecha_creacion": bin.fecha_creacion
    #         }
    #         resultado.append(dic)
            
    #     serializer = PDFProgramasPHSerializer(data = resultado, many = True)
    #     serializer.is_valid(raise_exception=True)
        
    #     return Response({
    #         "kilos_totales": kilos_totales_procesados['total_kilos'],
    #         "resultado": serializer.data
    #     })
    
    @action(detail=False, methods=['GET'], url_path='pdf-procesos')
    def pdf_proceso(self, request):
        desde_str = request.query_params.get('desde').replace('Z', '')
        hasta_str = request.query_params.get('hasta').replace('Z', '')
        
        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%d')
        except ValueError:
            desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S')
            
        try:
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d')
        except ValueError:
            hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S')
        
        proceso = ProcesoPH.objects.filter(Q(fecha_creacion__gte=desde) & Q(fecha_creacion__lte=hasta))
        bins_resultantes = BinResultanteProceso.objects.filter(proceso__in=proceso)
        kilos_totales_procesados = bins_resultantes.filter(esta_eliminado=False).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )
        print(kilos_totales_procesados)
        
        resultado = []
        
        for bin in bins_resultantes:
            proceso = f'{bin.proceso.get_tipo_proceso_display().capitalize()} N° {bin.proceso.pk}'
            dic = {
                "bin": bin.codigo_tarja,
                "programa": proceso,
                "kilos": round(bin.peso - bin.tipo_patineta, 2),
                "fecha_creacion": bin.fecha_creacion
            }
            resultado.append(dic)
            
        serializer = PDFProgramasPHSerializer(data=resultado, many=True)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            "kilos_totales": kilos_totales_procesados['total_kilos'],
            "resultado": serializer.data
        })
        
    @action(detail=True, methods=['GET'], url_path = 'pdf-documento-entrada')
    def pdf_entrada(self, request, pk):
        
        proceso =  ProcesoPH.objects.filter(pk = pk).first()
        bin_ingresados = BinsParaProceso.objects.filter(proceso = proceso)
    
        resultado = []
        
        kilos_totales = 0

        for bin in bin_ingresados:
            kilos_totales += bin.bin_bodega.binbodega.kilos_fruta
            cc_tarja = None
            cc_tarja_bin = None
            if bin.bin_bodega.tipo_binbodega.model in ['bodegag4','bodegag5']:
                cc_tarja = CCTarjaSeleccionada.objects.get(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion)
            elif bin.bin_bodega.tipo_binbodega.model == 'bodegag6':
                cc_tarja_bin = CCBinResultanteProgramaPH.objects.get(bin_resultante = bin.bin_bodega.binbodega.programa)
            programa = f'Selección N° {bin.proceso.pk}' if bin.bin_bodega.tipo_binbodega.model == 'bodegag5' else f'Planta Harina N° {bin.proceso.pk}'
            dic = {
                "bin": bin.bin_bodega.binbodega.seleccion.codigo_tarja if bin.bin_bodega.tipo_binbodega.model in ['bodegag4','bodegag5'] else bin.bin_bodega.binbodega.programa.codigo_tarja,
                "programa": programa,
                "cc_tarja":f'{cc_tarja.get_variedad_display()} / {cc_tarja.get_calibre_display()} / {cc_tarja.get_calidad_fruta_display()}' if bin.bin_bodega.tipo_binbodega.model in ['bodegag4','bodegag5'] else f'{cc_tarja_bin.humedad} %/ {cc_tarja_bin.piel_aderida} % / Sin Calidad',
                "kilos": round(bin.bin_bodega.binbodega.kilos_fruta),
                "procesado": bin.procesado
            }
            resultado.append(dic)
        print(kilos_totales)
        
        serializer = PDFDocumentoEntradaProgramaPHSerializer(data = resultado, many = True)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'kilos_totales  ': kilos_totales,
            'bins_resultantes': serializer.data
        })
    
    @action(detail=True, methods=['GET'], url_path = 'pdf-documento-salida')
    def pdf_salida(self, request, pk):

        proceso =  ProcesoPH.objects.filter(pk = pk).first()
        bins_resultantes = BinResultanteProceso.objects.filter(proceso = proceso)
        
        kilos_totales_procesados = bins_resultantes.filter(esta_eliminado=False).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )
        
        resultado = []


        for bin in bins_resultantes:
            cc_tarja = CCBinResultanteProcesoPH.objects.get(bin_resultante = bin)
            dic = {
                "bin": bin.codigo_tarja,
                "estado": bin.get_estado_bin_display(),
                "humedad": f'{cc_tarja.humedad} %',
                "piel_aderida": f'{cc_tarja.piel_aderida} %',
                "granulometria": f'{cc_tarja.granulometria}',
                "parametro": f'{cc_tarja.get_parametro_display()}',
                "calidad": 'Sin Calidad',
                "kilos": round(bin.peso - bin.tipo_patineta, 2),
            }
            resultado.append(dic)
        
        serializer = PDFDocumentoSalidaProgramaPHSerializer(data = resultado, many = True)
        serializer.is_valid(raise_exception=True)
        
        
        return Response({
            'programa': self.get_serializer(proceso).data,
            "kilos_totales": kilos_totales_procesados['total_kilos'],
            'bins_resultantes': serializer.data
        })
        
    def get_laborable_dates(self, start_date, end_date):
        date_list = []
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
        OperariosEnProcesoPH.objects.create(
            programa=programa,
            operario=operario,
            skill_operario=skill_operario
        )
        return Response({'status': 'Operario registrado en el programa'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def asignar_dias_kilos(self, request, pk=None):
        programa = self.get_object()
        
        # Validar fechas de inicio y término del proceso
        if programa.fecha_inicio_proceso and programa.fecha_termino_proceso:
            start_date = programa.fecha_inicio_proceso
            end_date = programa.fecha_termino_proceso

            # Obtener las fechas laborables
            laborable_dates = self.get_laborable_dates(start_date, end_date)
            num_laborable_days = len(laborable_dates)

            # Obtener operarios por skill
            operarios_programaph1 = OperariosEnProcesoPH.objects.filter(programa=programa, skill_operario='p_harina')
            #operarios_programaph2 = OperariosEnProcesoPH.objects.filter(programa=programa, skill_operario='p_harina')
            
            num_operarios_programaph1 = operarios_programaph1.count()
            #num_operarios_programaph2 = operarios_programaph2.count()

            # Calcular kilos totales de inputs
            total_kilos_input = sum(bin.bin_bodega.kilos_bin for bin in BinsParaProceso.objects.filter(proceso=programa))

            # Calcular kilos totales de outputs
            # total_kilos_output = BinResultanteProceso.objects.filter(proceso=programa).aggregate(
            #     total_kilos=models.Sum(models.F('peso') - models.F('tipo_patineta'))
            # )['total_kilos'] or 0

            kilos_por_dia_programaph1  = total_kilos_input / (num_laborable_days * num_operarios_programaph1) if num_operarios_programaph1 > 0 else 0
            for operario in operarios_programaph1:
                for laborable_date in laborable_dates:
                    DiaDeOperarioProcesoPH.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        kilos_dia=kilos_por_dia_programaph1
                    )

            # kilos_por_dia_programaph2 = total_kilos_output / (num_laborable_days * num_operarios_programaph2) if num_operarios_programaph2 > 0 else 0
            # for operario in operarios_programaph2:
            #     for laborable_date in laborable_dates:
            #         DiaDeOperarioProcesoPH.objects.update_or_create(
            #             operario=operario,
            #             dia=laborable_date,
            #             kilos_dia=kilos_por_dia_programaph2
            #         )

            return Response({'status': 'Días y kilos asignados a operarios'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Fechas de inicio o término no definidas'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def lista_operarios_dias(self, request, pk=None):
        programa = self.get_object()
        operarios_en_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)
        serializer = OperariosEnProcesoPHSerializer(operarios_en_produccion, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def metricas_en_tiempo_real(self, request, pk=None):
        programa = self.get_object()
        now = datetime.now()

        # Asegurarse de que both now y fecha_inicio tengan zona horaria o ninguna de las dos
        if is_naive(now):
            now = make_aware(now)
        
        if programa.fecha_inicio_proceso:
            if isinstance(programa.fecha_inicio_proceso, datetime):
                fecha_inicio = programa.fecha_inicio_proceso
            else:
                fecha_inicio = datetime.combine(programa.fecha_inicio_proceso, datetime.min.time())

            if is_naive(fecha_inicio):
                fecha_inicio = make_aware(fecha_inicio)
        else:
            return Response({'detail': 'La producción no ha comenzado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Total de kilos de fruta en LotesPrograma
        total_kilos_fruta = sum(bin.bin_bodega.kilos_bin for bin in BinsParaProceso.objects.filter(proceso=programa))

        # Total de kilos de fruta procesada (pre_limpia)
        kilos_procesados_programaph = sum(bin.bin_bodega.kilos_bin for bin in BinsParaProceso.objects.filter(proceso=programa, procesado=True))

        # Kilos de fruta resultante (despelo)
        kilos_resultantes_programaph = BinResultanteProceso.objects.filter(
            proceso=programa,
            # esta_eliminado=False
        ).aggregate(total_kilos=Sum(F('peso') - F('tipo_patineta')))['total_kilos'] or 0

        # Rendimiento de producción
        rendimiento_produccion = (kilos_resultantes_programaph / kilos_procesados_programaph) * 100 if kilos_procesados_programaph else 0

        # Kilos procesados por operario por día
        operarios_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)
        kilos_por_operario = []
        for operario in operarios_produccion:
            kilos_dia = DiaDeOperarioProcesoPH.objects.filter(
                operario=operario,
                dia=now.date()
            ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
            kilos_por_operario.append({
                'operario': operario.operario.nombre,
                'kilos_dia': kilos_dia
            })

        # Tasa de producción por hora
        horas_trabajadas = (now - fecha_inicio).total_seconds() / 3600
        tasa_produccion_hora = kilos_procesados_programaph / horas_trabajadas if horas_trabajadas > 0 else 0

        # Eficiencia del operario
        eficiencia_operarios = []
        for operario in operarios_produccion:
            eficiencia = DiaDeOperarioProcesoPH.objects.filter(
                operario=operario
            ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
            eficiencia_operarios.append({
                'operario': operario.operario.nombre,
                'eficiencia': eficiencia
            })

        metricas = {
            'total_kilos_fruta': total_kilos_fruta,
            'kilos_procesados_programaph': kilos_procesados_programaph,
            'kilos_resultantes_programaph': kilos_resultantes_programaph,
            'rendimiento_produccion': rendimiento_produccion,
            'kilos_por_operario': kilos_por_operario,
            'tasa_produccion_hora': tasa_produccion_hora,
            'eficiencia_operarios': eficiencia_operarios
        }

        return Response(metricas, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['GET'])
    def dias_trabajados_operario(self, request, pk=None):
        programa = self.get_object()
        operario_id = request.query_params.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        operario = get_object_or_404(Operario, pk=operario_id)
        operarios_en_produccion = OperariosEnProcesoPH.objects.filter(programa=programa, operario=operario).first()
        
        if not operarios_en_produccion:
            return Response({'error': 'No se encontraron registros de trabajo para este operario en la producción especificada'}, status=status.HTTP_404_NOT_FOUND)

        dias_trabajados = DiaDeOperarioProcesoPH.objects.filter(operario=operarios_en_produccion)
        serializer = DiaDeOperarioProcesoPHSerializer(dias_trabajados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'])
    def actualizar_ausente(self, request, pk=None):
        dia_id = request.data.get('dia_id')
        if not dia_id:
            return Response({'error': 'dia_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        dia = get_object_or_404(DiaDeOperarioProcesoPH, pk=dia_id)
        
        serializer = DiaDeOperarioProcesoPHSerializer(dia, data=request.data, partial=True)
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
            operario = get_object_or_404(OperariosEnProcesoPH, programa=programa, pk=operario_id)
            if operario:
                operario.delete()
                return Response({'status': 'Operario eliminado de la producción'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'No se encontro el operario en la producción'}, status=status.HTTP_400_BAD_REQUEST)
          
    @action(detail=True, methods=['GET'])
    def estado_termino_programa(self, request, pk=None):
        programa = self.get_object()
        tarjas = programa.binresultanteproceso_set.all()
        cc_tarja_resultante = CCBinResultanteProcesoPH.objects.filter(bin_resultante__in=tarjas)
        
        # Verificar control de calidad de las tarjas
        tarjas_sin_cc = [cc for cc in cc_tarja_resultante if cc.estado_control != '0']
        if len(tarjas_sin_cc) == 0:
            cc_estado_text = "Todas las tarjas tienen su control de calidad."
        else:
            cc_estado_text = f"{len(tarjas_sin_cc)} tarjas sin control de calidad."
        
        # Verificar operarios en producción
        operarios_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)
        if operarios_produccion.exists():
            operarios_estado_text = f"Se han agregado {operarios_produccion.count()} operarios a esta producción."
        else:
            operarios_estado_text = "No hay operarios registrados."

        # Verificar estado de los lotes programa
        lotes_programa = BinsParaProceso.objects.filter(proceso=programa)
        lotes_pendientes = lotes_programa.filter(procesado=False).count()
        if lotes_pendientes == 0:
            lotes_estado_text = "Todos los lotes programa han sido procesados."
        else:
            lotes_estado_text = f"{lotes_pendientes} lotes pendientes de procesamiento."

        # Construir la respuesta
        response_data = {
            "estado_control_calidad": cc_estado_text,
            "estado_operarios": operarios_estado_text,
            "estado_lotes": lotes_estado_text
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def estado_cierre_programa(self, request, pk=None):
        programa = self.get_object()
        operarios_produccion = OperariosEnProcesoPH.objects.filter(programa=programa)

        estado_dias = []
        for operario in operarios_produccion:
            operario_p = operarios_produccion.get(pk=operario.pk)
            dias_trabajados = DiaDeOperarioProcesoPH.objects.filter(operario=operario_p)
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



class BinsParaProcesoViewSet(viewsets.ModelViewSet):
    queryset = BinsParaProceso.objects.all()
    serializer_class = BinsParaProcesoSerializer
    
    @action(detail = False, methods=['POST'])
    def registrar_bins(self, request, pks_bins = None, proceso_pk = None):
        bins = request.data.get('bins', [])
        proceso_ph = ProcesoPH.objects.filter(pk = proceso_pk).first()
        for bin in bins:
            id_bin = bin.get('id')
            bins = BinBodega.objects.filter(pk = id_bin).first()
            BinsParaProceso.objects.update_or_create(proceso = proceso_ph, bin_bodega = bins)
        return Response({ "message": 'Creados Exitosamente' }, status=status.HTTP_201_CREATED)
    
    @action(detail = False, methods = ['POST'])
    def procesado_masivo(self, request, proceso_pk = None):
        bins = request.data.get('bins', [])
        proceso = ProcesoPH.objects.filter(pk = proceso_pk).first()
        BinsParaProceso.objects.filter(proceso = proceso, pk__in = [bin.get('id') for bin in bins]).update(procesado = True)
        return Response({ "message": 'Procesados Exitosamente' }, status=status.HTTP_200_OK)
        
    def list(self, request, proceso_pk=None):
        queryset = self.queryset.filter(proceso = proceso_pk) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,proceso_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), proceso=proceso_pk, pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)
    
class BinResultanteProcesoViewSet(viewsets.ModelViewSet):
    queryset = BinResultanteProceso.objects.all()
    serializer_class = BinResultanteProcesoSerializer
    
    def list(self, request, proceso_pk=None):
        queryset = self.queryset.filter(proceso = proceso_pk) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,proceso_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), proceso=proceso_pk, pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)

class OperariosEnProcesoPHViewSet(viewsets.ModelViewSet):
    queryset = OperariosEnProcesoPH.objects.all()
    serializer_class = OperariosEnProcesoPHSerializer
    
    @action(detail=False, methods=['GET'])
    def lista_filtrada_por_operario(self, request, proceso_pk=None):
        proceso = get_object_or_404(ProcesoPH, pk=proceso_pk)
        operarios_agregados = OperariosEnProcesoPH.objects.filter(proceso=proceso).annotate(
            dia_truncado=TruncDate('dia')  # Truncar la hora y conservar solo la fecha
        ).values(
            'operario__rut',
            'operario__nombre', 
            'operario__apellido',
            'skill_operario',
            'dia_truncado'  # Usar el día truncado para agrupación
        ).annotate(
            total_kilos_producidos=Sum('kilos'),
            dias_trabajados=Count('dia_truncado', distinct=True)
        ).distinct().order_by('dia_truncado', 'operario__rut')  # Ordenar por día truncado y rut del operario

        serializer = OperariosAgregadosSerializer(data=list(operarios_agregados), many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
      
    @action(detail=False, methods=['POST'])
    def lista_detalle_dias_operario(self, request, proceso_pk=None):
        proceso = get_object_or_404(ProcesoPH, pk = proceso_pk)
        lista_operario = OperariosEnProcesoPH.objects.filter(programa = proceso, operario__rut = request.data.get('rut'))
        serializer = OperariosEnProcesoPHSerializer(lista_operario, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['DELETE'])
    def eliminar_registro_dia_por_rut_y_id(self, request, proceso_pk=None):
        proceso = get_object_or_404(ProcesoPH, pk = proceso_pk)
        OperariosEnProcesoPH.objects.filter(programa = proceso, operario__rut = request.data.get('rut')).delete()
        return Response({ "message": 'Eliminado exitosamente' }, status = status.HTTP_204_NO_CONTENT)
           
    def list(self, request, proceso_pk=None):
        queryset = self.queryset.filter(proceso = proceso_pk) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,proceso_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), proceso=proceso_pk, pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)

class RechazoProcesoPHViewSet(viewsets.ModelViewSet):
    queryset = RechazoProcesoPH.objects.all()
    serializer_class = RechazoProcesoPHSerializer
    
    @action(detail=False, methods=['get'])
    def metricas(self, request, proceso_pk=None):
        proceso = ProcesoPH.objects.filter(pk=proceso_pk).first()
        if proceso is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        rechazos = get_rechazos_agrupados_proceso(proceso.id)
        return Response(rechazos, status=status.HTTP_200_OK)
         
    def list(self, request, proceso_pk=None):
        queryset = self.queryset.filter(proceso = proceso_pk) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,proceso_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), proceso=proceso_pk, pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)

class VariablesProcesoPHViewSet(viewsets.ModelViewSet):
    #lookup_field = 'proceso__pk'
    queryset = VariablesProcesoPH.objects.all()
    serializer_class = VariablesProcesoPHSerializer
    

    def list(self, request, proceso_pk=None):
        queryset = self.queryset.filter(proceso = proceso_pk) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request,proceso_pk=None, pk=None):
        queryset=get_object_or_404(self.get_queryset(), proceso=proceso_pk, pk=pk)
        serializer=self.get_serializer_class()(queryset)
        return  Response(serializer.data)

