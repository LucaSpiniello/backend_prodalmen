from .serializers import *
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404 
from rest_framework.decorators import action
from django.contrib.contenttypes.models import *
from cuentas.models import PersonalizacionPerfil
from core.models import Operario
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Q, Sum, Count, Subquery, Max,  F
from core.models import *
from seleccion.models import *
from embalaje.models import *
from .funciones import *
from django.utils.timezone import make_aware, is_naive
from datetime import datetime, timedelta

class ProduccionViewSet(viewsets.ModelViewSet):
    queryset = Produccion.objects.all()
    serializer_class = ProduccionSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = Produccion.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):  
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return ProduccionSerializer
        return DetalleProduccionSerializer
    
    def retrieve(self, request, pk=None, ):
        produccion = get_object_or_404(Produccion, pk=pk)
        serializer = self.get_serializer(produccion)
        return Response(serializer.data)
    
    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def pdf_documento_envases(self, request, pk=None):
        lotes_en_produccion = LotesPrograma.objects.filter(produccion=pk)

        resultados = []
        kilos_fruta = 0
        comercializador = None
        variedad = None
        productores = set()  # Cambiado a conjunto para evitar duplicados

        for lote in lotes_en_produccion:
            envase = EnvasesPatioTechadoExt.objects.get(pk=lote.bodega_techado_ext.pk)
            cantidad_envases = PatioTechadoExterior.objects.get(pk=envase.guia_patio.pk).envasespatiotechadoext_set.all().count()
            ubicacion = PatioTechadoExterior.objects.get(pk=envase.guia_patio.pk).get_ubicacion_display()
            suma_kilos_fruta = lote.bodega_techado_ext.kilos_fruta
            if suma_kilos_fruta is not None:
                kilos_fruta += suma_kilos_fruta

            if envase.guia_patio.tipo_recepcion.model == 'recepcionmp':
                numero_lote = envase.guia_patio.lote_recepcionado.numero_lote
                productor = envase.guia_patio.lote_recepcionado.guiarecepcion.productor.nombre
                productores.add(productor)  # Agregar a conjunto de productores
                comercializador = envase.guia_patio.lote_recepcionado.guiarecepcion.comercializador.nombre
                variedad = envase.guia_patio.lote_recepcionado.envasesguiarecepcionmp_set.first().get_variedad_display()
                tipo_envase = envase.guia_patio.lote_recepcionado.envasesguiarecepcionmp_set.first().envase.nombre

            dic = {
                "id": lote.pk,
                "numero_lote": numero_lote,
                "tipo_envase": tipo_envase,
                "numero_envase": f'{envase.numero_bin}/{cantidad_envases}',
                "ubicacion": ubicacion,
                "colectado": f'{True if lote.bin_procesado else False}'
            }

            resultados.append(dic)

        serializer = PDFDetalleEnvasesSerializer(data=resultados, many=True)
        serializer.is_valid(raise_exception=True)

        return Response({
            "kilos_totales": round(kilos_fruta, 2),
            "productor": list(productores),  # Convertir a lista antes de devolver
            "comercializador": comercializador,
            "variedad": variedad,
            "detalle_envase": serializer.data
        },
        status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['GET'])
    def pdf_documento_entrada(self, request, pk=None):
        lotes_en_produccion = LotesPrograma.objects.filter(produccion=pk)
        
        resultados = {}
        productores = set() 
        comercializador = None
        kilos_fruta_totales = 0

        for lote in lotes_en_produccion:
            kilos_fruta = 0
            envase = EnvasesPatioTechadoExt.objects.get(pk=lote.bodega_techado_ext.pk)
            cantidad_envases = PatioTechadoExterior.objects.get(pk=envase.guia_patio.pk).envasespatiotechadoext_set.all().count()
            suma_kilos_fruta = lote.bodega_techado_ext.kilos_fruta
            if suma_kilos_fruta is not None:
                kilos_fruta += suma_kilos_fruta
                kilos_fruta_totales += suma_kilos_fruta
            
            if envase.guia_patio.tipo_recepcion.model == 'recepcionmp':
                numero_lote = envase.guia_patio.lote_recepcionado.numero_lote
                productor = envase.guia_patio.lote_recepcionado.guiarecepcion.productor.nombre
                productores.add(productor)
                comercializador = envase.guia_patio.lote_recepcionado.guiarecepcion.comercializador.nombre
                variedad = envase.guia_patio.lote_recepcionado.envasesguiarecepcionmp_set.first().get_variedad_display()
                
                # Si el número de lote no está en resultados, inicializarlo con los datos del lote
                if numero_lote not in resultados:
                    resultados[numero_lote] = {
                        'numero_lote': numero_lote,
                        'total_envases': cantidad_envases,
                        'productor': productor,
                        'comercializador': comercializador,
                        'variedad': variedad,
                        'kilos_fruta': round(kilos_fruta, 2)
                    }
                else:
                    # Si el número de lote ya existe, agregar los valores correspondientes
                    resultados[numero_lote]['kilos_fruta'] += round(kilos_fruta, 2)

        return Response({
            "productor": list(productores),
            "comercializador": comercializador,
            "kilos_totales": round(kilos_fruta_totales, 2),
            "detalle_lote": list(resultados.values())
            }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['get'])
    def pdf_salida_produccion(self, request, pk=None):
        produccion = self.get_object()
        serializer = ProduccionDetailSerializer(produccion)
        return Response({
            'produccion': produccion.id,
            'kilos_resultantes': serializer.data['kilos_resultantes_totales'],
            'cantidad_bines_resultantes': serializer.data['cantidad_bines_resultantes'],
            #'productores_duenos_lote': serializer.data['productores_duenos_lotes'],
            'numeros_lote': serializer.data['numeros_lote'],
            'tarjas_resultantes': serializer.data['tarjas_resultantes']
        })
      
    @action(detail=False, methods=['POST'])
    def pdf_produccion(self, request):
        tipo_informe = request.data.get('tipo_informe')
        desde_str = request.data.get('desde')
        hasta_str = request.data.get('hasta')

        if not tipo_informe or not desde_str or not hasta_str:
            return Response({'detail': 'Los campos tipo_informe, desde y hasta son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        desde_str = desde_str.replace('Z', '')
        hasta_str = hasta_str.replace('Z', '')

        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
            hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError as e:
            return Response({'detail': f'Error en la conversión de fechas: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        if tipo_informe == '1':
            # Filtrar Produccion por fecha
            queryset = Produccion.objects.filter(
            Q(fecha_inicio_proceso__gte=desde, fecha_termino_proceso__lte=hasta) |  
            Q(fecha_termino_proceso__isnull=True, fecha_inicio_proceso__lte=hasta)                                 
        )
            resultados = {}
            kilos_totales_procesados = LotesPrograma.objects.filter(
                produccion__in=queryset,
                bin_procesado=True,
                fecha_procesado__range=(desde, hasta)
            ).aggregate(total_kilos_procesados=Sum('bodega_techado_ext__kilos_fruta'))['total_kilos_procesados']

            kilos_totales_procesados = round(kilos_totales_procesados or 0, 2)

            for lote in LotesPrograma.objects.filter(fecha_procesado__range=(desde, hasta)):
                kilos_fruta = 0
                envase = EnvasesPatioTechadoExt.objects.get(pk=lote.bodega_techado_ext.pk)
                cantidad_envases = PatioTechadoExterior.objects.get(pk=envase.guia_patio.pk).envasespatiotechadoext_set.all().count()
                suma_kilos_fruta = lote.bodega_techado_ext.kilos_fruta
                if suma_kilos_fruta is not None:
                    kilos_fruta += suma_kilos_fruta

                if envase.guia_patio.tipo_recepcion.model == 'recepcionmp':
                    numero_lote = envase.guia_patio.lote_recepcionado.numero_lote
                    productor = envase.guia_patio.lote_recepcionado.guiarecepcion.productor.nombre
                    comercializador = envase.guia_patio.lote_recepcionado.guiarecepcion.comercializador.nombre
                    variedad = envase.guia_patio.lote_recepcionado.envasesguiarecepcionmp_set.first().get_variedad_display()

                    if numero_lote not in resultados:
                        resultados[numero_lote] = {
                            'numero_lote': numero_lote,
                            'total_envases': cantidad_envases,
                            'productor': productor,
                            'variedad': variedad,
                            'numero_programa': lote.produccion.pk,
                            'kilos_fruta': round(kilos_fruta,2)
                        }
                    else:
                        resultados[numero_lote]['kilos_fruta'] += round(kilos_fruta, 2)

            return Response({
                "kilos_totales_procesados": kilos_totales_procesados,
                "detalle_programas": list(resultados.values())
            })

        else:
            # Filtrar TarjaResultante por fecha
            queryset = TarjaResultante.objects.filter(Q(fecha_creacion__gte=desde) & Q(fecha_creacion__lte=hasta))
            serializer = TarjaResultanteSerializer(queryset, many=True)
            return Response(serializer.data)
        
    @action(detail=False, methods=['POST'])
    def pdf_operario_resumido(self, request):
        desde_str = request.data.get('desde').replace('Z', '')
        hasta_str = request.data.get('hasta').replace('Z', '')

        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
            hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
            
        
        except ValueError as e:
            return Response({'detail': f'Error en la conversión de fechas: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        produccion = Produccion.objects.filter(
            Q(fecha_inicio_proceso__gte=desde, fecha_termino_proceso__lte=hasta) |  
            Q(fecha_termino_proceso__isnull=True, fecha_inicio_proceso__lte=hasta)                                 
        )
        
        resultado_seria = {}
        try:
            for programa in produccion:
                operarios_en_programa = OperariosEnProduccion.objects.filter(produccion=programa.pk)

                for operario_en_programa in operarios_en_programa:          
                    nombre_operario = f"{operario_en_programa.operario.nombre} {operario_en_programa.operario.apellido}"
                    total_kilos_operario = DiaDeOperarioProduccion.objects.filter(
                        operario=operario_en_programa,
                        dia__range=(desde.date(), hasta.date())
                    ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
                    

                    # Intenta obtener el pago por kilo para pre_limpia
                    try:
                        pago_x_kilo_operario_prelimpia = SkillOperario.objects.get(
                            operario=operario_en_programa.operario, tipo_operario='p_limpia'
                        ).pago_x_kilo
                    except SkillOperario.DoesNotExist:
                        pago_x_kilo_operario_prelimpia = 0

                    # Intenta obtener el pago por kilo para despelo
                    try:
                        pago_x_kilo_operario_despelonado = SkillOperario.objects.get(
                            operario=operario_en_programa.operario, tipo_operario='despelo'
                        ).pago_x_kilo
                    except SkillOperario.DoesNotExist:
                        pago_x_kilo_operario_despelonado = 0
                        
                    operarios_skill_pre_limpia = OperariosEnProduccion.objects.filter(produccion=programa.pk, skill_operario='p_limpia')
                
                    operarios_skill_despelo = OperariosEnProduccion.objects.filter(produccion=programa.pk, skill_operario='despelo')
                    
                    
                    have_skill_pre_limpia_in_program = any(
                        operario_en_programa.operario == operario_en_produccion.operario 
                        for operario_en_produccion in operarios_skill_pre_limpia
                    )

                    have_skill_despelo_in_program = any(
                        operario_en_programa.operario == operario_en_produccion.operario 
                        for operario_en_produccion in operarios_skill_despelo
                    )
                    
                    total_prelimpia = round(pago_x_kilo_operario_prelimpia * total_kilos_operario, 2)
                    total_despelonada = round(pago_x_kilo_operario_despelonado * total_kilos_operario, 2)
                    
                    if not have_skill_despelo_in_program:
                        total_despelonada = 0
                    if not have_skill_pre_limpia_in_program:
                        total_prelimpia = 0

                    if nombre_operario not in resultado_seria:
                        resultado_seria[nombre_operario] = {
                            "numero_programa": programa.pk,
                            "nombre_operario": nombre_operario,
                            "kilos_programa": round(total_kilos_operario, 2),
                            "pre_limpia": round(total_prelimpia,2) if pago_x_kilo_operario_prelimpia > 0 else "No Tiene este Skill",
                            "despelonado": round(total_despelonada,2) if pago_x_kilo_operario_despelonado > 0 else "No Tiene este Skill",
                            "neto": round(total_prelimpia + total_despelonada, 2)
                        }
                        if resultado_seria[nombre_operario]['neto'] == 0:
                            del resultado_seria[nombre_operario]
                    else: 
                        resultado_seria[nombre_operario]['kilos_programa'] += round(total_kilos_operario, 2)
                        resultado_seria[nombre_operario]['pre_limpia'] += round(total_prelimpia,2) if pago_x_kilo_operario_prelimpia > 0 else "No Tiene este Skill"
                        resultado_seria[nombre_operario]['despelonado'] += round(total_despelonada,2) if pago_x_kilo_operario_despelonado > 0 else "No Tiene este Skill"
                        resultado_seria[nombre_operario]['neto'] += round(total_prelimpia + total_despelonada, 2)
                    
            
            return Response(list(resultado_seria.values()), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['POST'])
    def pdf_operario_x_kilo(self, request):
        desde_str = request.data.get('desde').replace('Z', '')
        hasta_str = request.data.get('hasta').replace('Z', '')

        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
            hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError as e:
            return Response({'detail': f'Error en la conversión de fechas: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        operario_front = request.data.get('operario')
        if not operario_front:
            return Response({'detail': 'El campo operario es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        operario_select = Operario.objects.filter(pk=operario_front).first()
        if not operario_select:
            return Response({'detail': 'Operario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # get all productin in the range of dates
        producciones = Produccion.objects.filter(
                Q(fecha_inicio_proceso__gte=desde, fecha_termino_proceso__lte=hasta) |  
                Q(fecha_termino_proceso__isnull=True, fecha_inicio_proceso__lte=hasta)                                 
            )
                    
        resultado_seria = {}
        nombre_operario = None
        try:
            for programa in producciones:
                operarios_en_programa = OperariosEnProduccion.objects.filter(produccion=programa.pk, operario=operario_select)
                
                # get operarios por skill en el programa
                
                if operarios_en_programa.exists():
                                        
                    nombre_operario = f'{operarios_en_programa.first().operario.nombre} {operarios_en_programa.first().operario.apellido}'
                    # get total kilos programa
                    total_kilos_operario = DiaDeOperarioProduccion.objects.filter(
                        operario__in=operarios_en_programa,
                        dia__range=(desde.date(), hasta.date())  
                    ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
                    
                    total_kilos_pre_limpia_operario = LotesPrograma.objects.filter(
                        produccion=programa,
                        bin_procesado=True,
                        fecha_procesado__range=(desde, hasta)
                    ).aggregate(
                        total_kilos=models.Sum('bodega_techado_ext__kilos_fruta')
                    )['total_kilos'] or 0
                
                    total_kilos_despelonado_operario = TarjaResultante.objects.filter(
                        produccion=programa,
                        esta_eliminado=False,
                        fecha_creacion__range=(desde, hasta)
                    ).aggregate(
                        total_kilos=models.Sum(models.F('peso') - models.F('tipo_patineta'))
                    )['total_kilos'] or 0
                    
                    print(f"total kilos despelonado {total_kilos_despelonado_operario} desde {desde} hasta {hasta}")
                    
                    operarios_skill_pre_limpia = OperariosEnProduccion.objects.filter(produccion=programa.pk, skill_operario='p_limpia')
                
                    operarios_skill_despelo = OperariosEnProduccion.objects.filter(produccion=programa.pk, skill_operario='despelo')
                    
                    have_skill_pre_limpia_in_program = any(
                        operario_select == operario_en_produccion.operario 
                        for operario_en_produccion in operarios_skill_pre_limpia
                    )

                    have_skill_despelo_in_program = any(
                        operario_select == operario_en_produccion.operario 
                        for operario_en_produccion in operarios_skill_despelo
)
                          
                    # Intenta obtener el pago por kilo para pre_limpia
                    try:
                        pago_x_kilo_operario_prelimpia = SkillOperario.objects.get(operario=operario_front, tipo_operario='p_limpia').pago_x_kilo
                    except SkillOperario.DoesNotExist:
                        pago_x_kilo_operario_prelimpia = 0
                    
                    # Intenta obtener el pago por kilo para despelo
                    try:
                        pago_x_kilo_operario_despelonado = SkillOperario.objects.get(operario=operario_front, tipo_operario='despelo').pago_x_kilo
                    except SkillOperario.DoesNotExist:
                        pago_x_kilo_operario_despelonado = 0
                    print(f"kilos despelonado {total_kilos_despelonado_operario} pagando {pago_x_kilo_operario_despelonado}")
                    total_prelimpia = round(pago_x_kilo_operario_prelimpia * total_kilos_pre_limpia_operario, 2)
                    total_despelonada = round(pago_x_kilo_operario_despelonado * total_kilos_despelonado_operario, 2)
                    print(f"TOTAL DESPELONADO   {total_despelonada}")
                    if not have_skill_despelo_in_program:
                        total_despelonada = 0
                    if not have_skill_pre_limpia_in_program:
                        total_prelimpia = 0
                    
                    print(f"total_despelo {total_despelonada}")
                        
                    if programa.pk not in resultado_seria:
                        resultado_seria[programa.pk] = {
                            "numero_programa": programa.pk,
                            "nombre_operario": nombre_operario,
                            "kilos_programa": round(total_kilos_operario, 2),
                            "pre_limpia": total_prelimpia if pago_x_kilo_operario_prelimpia > 0 else "No Tiene este Skill",
                            "despelonado": total_despelonada if pago_x_kilo_operario_despelonado > 0 else "No Tiene este Skill",
                            "neto": round(total_prelimpia + total_despelonada, 2)
                        }

            return Response({
                "operario": nombre_operario,
                "programas": list(resultado_seria.values())
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
        produccion = self.get_object()
        operario_id = request.data.get('operario_id')
        skill_operario = request.data.get('skill_operario')

        operario = Operario.objects.get(pk=operario_id)
        OperariosEnProduccion.objects.create(
            produccion=produccion,
            operario=operario,
            skill_operario=skill_operario
        )
        return Response({'status': 'Operario registrado en el programa'}, status=status.HTTP_201_CREATED)
    
    def calculate_worker_days(self, operario, produccion):
        print("Calculando días trabajados por operario ", operario)
        dias_trabajados = DiaDeOperarioProduccion.objects.filter(
        operario=operario,
        dia__range=(produccion.fecha_inicio_proceso, datetime.now().date())
            )
        if dias_trabajados.exists():
            total_dias = dias_trabajados.count()
        else:
            total_dias = 0
        
        print(f"Total días trabajados por {operario}: {total_dias}")           
            
    @action(detail=True, methods=['POST'])
    def asignar_dias_kilos(self, request, pk=None):
        produccion = self.get_object()
        # Validar fechas de inicio y término del proceso
        
        if produccion.fecha_inicio_proceso:
            start_date = produccion.fecha_inicio_proceso
            if (produccion.fecha_termino_proceso):
                end_date = produccion.fecha_termino_proceso
            else:
                end_date = datetime.now().date()
                
            laborable_dates = self.get_laborable_dates(start_date, end_date)

            operarios_limpia = OperariosEnProduccion.objects.filter(produccion=produccion, skill_operario='p_limpia')
            operarios_despelo = OperariosEnProduccion.objects.filter(produccion=produccion, skill_operario='despelo')

            for operario_limpia in operarios_limpia:
                for laborable_date in laborable_dates:  
                       
                    existing_records = DiaDeOperarioProduccion.objects.filter(
                        operario=operario_limpia,
                        dia=laborable_date
                    )
            
                    if existing_records.count() > 1:
                        existing_records.delete()
                    
                    kilos_dia_actual = LotesPrograma.objects.filter(
                        produccion=produccion,
                        bin_procesado=True,
                        fecha_procesado__date=laborable_date
                    ).aggregate(
                        total_kilos=models.Sum('bodega_techado_ext__kilos_fruta')
                    )['total_kilos'] or 0
                    

                                  
                    DiaDeOperarioProduccion.objects.filter(
                        operario=operario_limpia,
                        dia=laborable_date
                    ).update(kilos_dia=0)
                    
                    DiaDeOperarioProduccion.objects.update_or_create(
                        operario=operario_limpia,
                        dia=laborable_date,
                        defaults={'kilos_dia': kilos_dia_actual}                                                                                                        
                    )
                 
        
            for operario_despelo in operarios_despelo:
                    
                for laborable_date in laborable_dates:
                    
                    existing_records = DiaDeOperarioProduccion.objects.filter(
                        operario=operario_despelo,
                        dia=laborable_date
                        )
            
                    if existing_records.count() > 1:
                        existing_records.delete()
                    
                    kilos_dia_actual = TarjaResultante.objects.filter(
                        produccion=produccion,
                        esta_eliminado=False,
                        fecha_creacion__date=laborable_date
                    ).aggregate(
                        total_kilos=models.Sum(models.F('peso') - models.F('tipo_patineta'))
                    )['total_kilos'] or 0
                    
                    print(f"asignando {kilos_dia_actual} a {operario_despelo} en {laborable_date}")
                    
                    DiaDeOperarioProduccion.objects.filter(
                        operario=operario_despelo,
                        dia=laborable_date
                    ).update(kilos_dia=0)
                    
                    DiaDeOperarioProduccion.objects.update_or_create(
                        operario=operario_despelo,
                        dia=laborable_date,
                        defaults={'kilos_dia': kilos_dia_actual}
                    )
                    
                    

            return Response({'status': 'Días y kilos asignados a operarios'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Fechas de inicio o término no definidas'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def lista_operarios_dias(self, request, pk=None):
        produccion = self.get_object()
        operarios_en_produccion = OperariosEnProduccion.objects.filter(produccion=produccion)
        serializer = OperariosEnProduccionSerializer(operarios_en_produccion, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def metricas_en_tiempo_real(self, request, pk=None):
        produccion = self.get_object()
        now = datetime.now()

        # Asegurarse de que both now y fecha_inicio tengan zona horaria o ninguna de las dos
        if is_naive(now):
            now = make_aware(now)
        
        if produccion.fecha_inicio_proceso:
            if isinstance(produccion.fecha_inicio_proceso, datetime):
                fecha_inicio = produccion.fecha_inicio_proceso
            else:
                fecha_inicio = datetime.combine(produccion.fecha_inicio_proceso, datetime.min.time())

            if is_naive(fecha_inicio):
                fecha_inicio = make_aware(fecha_inicio)
        else:
            return Response({'detail': 'La producción no ha comenzado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Total de kilos de fruta en LotesPrograma
        total_kilos_fruta = LotesPrograma.objects.filter(
            produccion=produccion,
            esta_eliminado=False
        ).aggregate(total_kilos=Sum('bodega_techado_ext__kilos_fruta'))['total_kilos'] or 0

        # Total de kilos de fruta procesada (pre_limpia)
        kilos_procesados_pre_limpia = LotesPrograma.objects.filter(
            produccion=produccion,
            bin_procesado=True,
            esta_eliminado=False
        ).aggregate(total_kilos=Sum('bodega_techado_ext__kilos_fruta'))['total_kilos'] or 0

        # Kilos de fruta resultante (despelo)
        kilos_resultantes_despelo = TarjaResultante.objects.filter(
            produccion=produccion,
            esta_eliminado=False
        ).aggregate(total_kilos=Sum(F('peso') - F('tipo_patineta')))['total_kilos'] or 0

        # Rendimiento de producción
        rendimiento_produccion = (kilos_resultantes_despelo / kilos_procesados_pre_limpia) * 100 if kilos_procesados_pre_limpia else 0

        # Kilos procesados por operario por día
        operarios_produccion = OperariosEnProduccion.objects.filter(produccion=produccion)
        kilos_por_operario = []
        for operario in operarios_produccion:
            kilos_dia = DiaDeOperarioProduccion.objects.filter(
                operario=operario,
                dia=now.date()
            ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
            kilos_por_operario.append({
                'operario': operario.operario.nombre,
                'kilos_dia': kilos_dia
            })

        # Tasa de producción por hora
        horas_trabajadas = (now - fecha_inicio).total_seconds() / 3600
        tasa_produccion_hora = kilos_procesados_pre_limpia / horas_trabajadas if horas_trabajadas > 0 else 0

        # Eficiencia del operario
        eficiencia_operarios = []
        for operario in operarios_produccion:
            eficiencia = DiaDeOperarioProduccion.objects.filter(
                operario=operario
            ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0
            eficiencia_operarios.append({
                'operario': operario.operario.nombre,
                'eficiencia': eficiencia
            })

        metricas = {
            'total_kilos_fruta': total_kilos_fruta,
            'kilos_procesados_pre_limpia': kilos_procesados_pre_limpia,
            'kilos_resultantes_despelo': kilos_resultantes_despelo,
            'rendimiento_produccion': rendimiento_produccion,
            'kilos_por_operario': kilos_por_operario,
            'tasa_produccion_hora': tasa_produccion_hora,
            'eficiencia_operarios': eficiencia_operarios
        }

        return Response(metricas, status=status.HTTP_200_OK)
     
    @action(detail=True, methods=['GET'])
    def distribucion_kilos_tipos_resultante(self, request, pk=None):
        produccion = self.get_object()
        tipos_resultante = TarjaResultante.objects.filter(produccion=produccion, esta_eliminado=False).values('tipo_resultante').annotate(total=Sum(F('peso') - F('tipo_patineta')))
        
        tipo_choices = dict(TarjaResultante._meta.get_field('tipo_resultante').choices)

        data = {
            'series': [tipo['total'] for tipo in tipos_resultante],
            'labels': [tipo_choices[tipo['tipo_resultante']] for tipo in tipos_resultante]
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def rendimiento_produccion(self, request, pk=None):
        produccion = self.get_object()
        # Filtrar solo los lotes donde fecha_procesado no es nulo y bin_procesado es True
        fechas = LotesPrograma.objects.filter(produccion=produccion, bin_procesado=True, fecha_procesado__isnull=False).values_list('fecha_procesado__date', flat=True).distinct()
        
        data = {
            'series': [],
            'categories': list(fechas)
        }
        
        for fecha in fechas:
            # Asegurarse de filtrar por fecha_procesado que no es nulo
            kilos_procesados = LotesPrograma.objects.filter(produccion=produccion, bin_procesado=True, fecha_procesado__date=fecha).aggregate(total_kilos=Sum('bodega_techado_ext__kilos_fruta'))['total_kilos'] or 0
            kilos_resultantes = TarjaResultante.objects.filter(produccion=produccion, fecha_cc_tarja__date=fecha).aggregate(total_kilos=Sum(F('peso') - F('tipo_patineta')))['total_kilos'] or 0
            
            rendimiento = (kilos_resultantes / kilos_procesados) * 100 if kilos_procesados else 0
            data['series'].append(round(rendimiento, 2))
        
        return Response(data, status=status.HTTP_200_OK)
  
    @action(detail=True, methods=['GET'])
    def tasa_produccion_hora(self, request, pk=None):
        produccion = self.get_object()
        now = datetime.now()

        if not produccion.fecha_inicio_proceso:
            return Response({'detail': 'La producción no ha comenzado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir fecha_inicio_proceso a datetime si es una fecha
        if isinstance(produccion.fecha_inicio_proceso, datetime):
            fecha_inicio = produccion.fecha_inicio_proceso
        else:
            fecha_inicio = datetime.combine(produccion.fecha_inicio_proceso, datetime.min.time())

        # Convertir fechas a aware datetime objects si están en naive
        if fecha_inicio.tzinfo is None:
            fecha_inicio = make_aware(fecha_inicio)
        if now.tzinfo is None:
            now = make_aware(now)

        # Verificar si hoy es un día laboral (lunes a viernes)
        if now.weekday() >= 5:
            return Response({'detail': 'Hoy no es un día laboral.'}, status=status.HTTP_400_BAD_REQUEST)

        # Definir el inicio y fin del día en curso
        start_of_day = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=18, minute=0, second=0, microsecond=0)

        # Verificar si el inicio del proceso es antes del inicio del día en curso
        start_time = max(start_of_day, fecha_inicio)

        # Inicializar la estructura de datos
        horas = []
        current_time = start_time
        while current_time <= now and current_time <= end_of_day:
            horas.append(current_time)
            current_time += timedelta(hours=1)

        data = {
            'series': [],
            'categories': [hora.strftime("%H:00") for hora in horas]
        }

        for hora in horas:
            start_time = hora
            end_time = start_time + timedelta(hours=1)

            kilos_procesados = LotesPrograma.objects.filter(
                produccion=produccion,
                bin_procesado=True,
                fecha_procesado__range=(start_time, end_time)
            ).aggregate(total_kilos=Sum('bodega_techado_ext__kilos_fruta'))['total_kilos'] or 0

            data['series'].append(round(kilos_procesados, 2))

        return Response(data, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['GET'])
    def dias_trabajados_operario(self, request, pk=None):
        produccion = get_object_or_404(Produccion, pk=pk)
        operario_id = request.query_params.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        operario = get_object_or_404(Operario, pk=operario_id)
        operarios_en_produccion = OperariosEnProduccion.objects.filter(produccion=produccion, operario=operario).first()
        
        if not operarios_en_produccion:
            return Response({'error': 'No se encontraron registros de trabajo para este operario en la producción especificada'}, status=status.HTTP_404_NOT_FOUND)

        dias_trabajados = DiaDeOperarioProduccion.objects.filter(operario=operarios_en_produccion)
        serializer = DiaDeOperarioProduccionSerializer(dias_trabajados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'])
    def actualizar_ausente(self, request, pk=None):
        dia_id = request.data.get('dia_id')
        if not dia_id:
            return Response({'error': 'dia_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        dia = get_object_or_404(DiaDeOperarioProduccion, pk=dia_id)
        
        serializer = DiaDeOperarioProduccionUpdateSerializer(dia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['DELETE'])
    def eliminar_operario(self, request, pk=None):
        produccion = get_object_or_404(Produccion, pk=pk)
        operario_id = request.data.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            operario = get_object_or_404(OperariosEnProduccion, produccion=produccion, pk=operario_id)
            if operario:
                operario.delete()
                return Response({'status': 'Operario eliminado de la producción'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'No se encontro el operario en la producción'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def estado_termino_programa(self, request, pk=None):
        produccion = get_object_or_404(Produccion, pk=pk)
        tarjas = produccion.tarjaresultante_set.filter(esta_eliminado=False)
        cc_tarja_resultante = CCTarjaResultante.objects.filter(tarja__in=tarjas)
        
        # Verificar control de calidad de las tarjas
        tarjas_sin_cc = [cc for cc in cc_tarja_resultante if cc.estado_cc != '3']
        if len(tarjas_sin_cc) == 0:
            cc_estado_text = "Todas las tarjas tienen su control de calidad."
        else:
            cc_estado_text = f"{len(tarjas_sin_cc)} tarjas sin control de calidad."
        
        # Verificar operarios en producción
        operarios_produccion = OperariosEnProduccion.objects.filter(produccion=produccion)
        if operarios_produccion.exists():
            operarios_estado_text = f"Se han agregado {operarios_produccion.count()} operarios a esta producción."
        else:
            operarios_estado_text = "No hay operarios registrados."

        # Verificar estado de los lotes programa
        lotes_programa = LotesPrograma.objects.filter(produccion=produccion)
        lotes_pendientes = lotes_programa.filter(bin_procesado=False).count()
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
        produccion = get_object_or_404(Produccion, pk=pk)
        operarios_produccion = OperariosEnProduccion.objects.filter(produccion=produccion)

        estado_dias = []
        for operario in operarios_produccion:
            # dias_trabajados = DiaDeOperarioProduccion.objects.filter(operario=operario)
            # print("Dias trabajados", dias_trabajados)
            
            # calculate total days worker has worked in the production
            dias_trabajados = DiaDeOperarioProduccion.objects.filter(
                operario=operario,
                dia__range=(produccion.fecha_inicio_proceso, datetime.now().date())
            )
            if dias_trabajados.exists():
                total_dias = dias_trabajados.count()
                total_kilos = round(dias_trabajados.aggregate(total_kilos=Sum('kilos_dia'))['total_kilos']) or 0
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
        
        
        
        
class LotesProgramaViewSet(viewsets.ModelViewSet):  
    queryset = LotesPrograma.objects.all()
    serializer_class = LotesProgramaSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = LotesPrograma.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return LotesProgramaSerializer
        return DetalleLotesProgramaSerializer
    
    def retrieve(self, request, produccion_pk=None, pk=None):
        produccion = get_object_or_404(Produccion, pk=produccion_pk)
        # queryset = get_object_or_404(self.get_queryset(),produccion=produccion, pk=pk)
        queryset = LotesPrograma.objects.get(pk = pk, produccion = produccion)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
    
    def list(self, request, produccion_pk=None):
        produccion = get_object_or_404(Produccion, pk=produccion_pk)
        queryset = LotesPrograma.objects.filter(produccion=produccion, esta_eliminado = False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def registrar_lotes(self, request, produccion_pk=None):
        pks_list = request.data.get('pks_guias')
        produccion = get_object_or_404(Produccion, pk = produccion_pk)
        guias = PatioTechadoExterior.objects.filter(pk__in = pks_list)
        for guia in guias:
            for y in guia.envasespatiotechadoext_set.all():
                envase = EnvasesPatioTechadoExt.objects.filter(pk = y.pk, estado_envase='1')
                if envase:
                    LotesPrograma.objects.get_or_create(produccion = produccion, bodega_techado_ext = envase.first())
                    envase.update(estado_envase='2')
                else:
                    pass
        return Response({ 'message': 'Creado con exito'}, status=status.HTTP_201_CREATED)
    
    
    @action(detail=False, methods=['DELETE'], url_path='eliminar_lotes/(?P<pks_lotes>[^/.]+)')  
    def eliminar_lotes(self, request, pks_lotes=None, produccion_pk=None):
        pks_list = pks_lotes.split(',')
        produccion = get_object_or_404(Produccion,pk = produccion_pk)
        LotesPrograma.objects.filter(produccion = produccion, bodega_techado_ext__in = list(pks_list)).delete()
        return Response({ 'message': 'Lote Eliminado con exito'})
    
    @action(detail=False, methods=['PUT', 'PATCH'], url_path='actualizar_estados_lotes/(?P<pks_lotes>[^/.]+)')
    def actualizar_estados_lotes(self, request, pks_lotes=None, produccion_pk=None):
        pks_list = pks_lotes.split(',')
        produccion = get_object_or_404(Produccion,pk = produccion_pk)
        for x in pks_list:
            envase = EnvasesPatioTechadoExt.objects.get(pk = x)
            LotesPrograma.objects.filter(produccion = produccion, bodega_techado_ext = envase).update(bin_procesado = True, fecha_procesado = datetime.now())
        return Response({ 'message': 'Lote Actualizados con exito'})      
              
class TarjaResultanteViewSet(viewsets.ModelViewSet):
    queryset = TarjaResultante.objects.all()
    serializer_class = TarjaResultanteSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = TarjaResultante.objects.filter(fecha_creacion__year = anio, esta_eliminado = False)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):    
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return TarjaResultanteSerializer
        return DetalleTarjaResultanteSerializer
    
    def retrieve(self, request, produccion_pk=None, pk=None):
        produccion = get_object_or_404(Produccion, pk=produccion_pk)
        queryset = get_object_or_404(self.get_queryset(), produccion=produccion, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
    
    def list(self, request, produccion_pk=None):
        produccion = get_object_or_404(Produccion, pk=produccion_pk)
        queryset = TarjaResultante.objects.filter(produccion=produccion, esta_eliminado = False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['PUT', 'PATCH'])
    def eliminar_tarja(self, request, produccion_pk=None, pk=None):
        print(request.data.get('id'))
        produccion = get_object_or_404(Produccion, pk=produccion_pk)
        queryset = get_object_or_404(self.get_queryset(), produccion=produccion, pk = request.data.get('id'))
        if queryset.cc_tarja != True:
            queryset.esta_eliminado = request.data.get('esta_eliminado')
            if (queryset.tipo_resultante == '1'):
                # ct = ContentType.objects.get_for_model(BodegaG1)
                bodegag1 = BodegaG1.objects.filter(produccion = queryset.pk).first()
                bodegag1.estado_bin = '6'
                bodegag1.save()
                # BinBodega.objects.filter(id_binbodega = bodegag1.id, tipo_binbodega = ct).update(estado_binbodega = '1') # type: ignore
            elif (queryset.tipo_resultante == '3'):
                # ct = ContentType.objects.get_for_model(BodegaG2)
                bodegag2 = BodegaG2.objects.filter(produccion = queryset.pk).first()
                bodegag2.estado_bin = '6'
                bodegag2.save()
                # BinBodega.objects.filter(id_binbodega = bodegag2.id, tipo_binbodega = ct).update(estado_binbodega = '1') # type: ignore
            queryset.save()
            serializer = self.get_serializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({ 'message': 'No se puede eliminar la tarja'}, status=status.HTTP_400_BAD_REQUEST) 

class ReprocesoViewSet(viewsets.ModelViewSet):
    queryset = Reproceso.objects.all()
    serializer_class = ReprocesoSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = Reproceso.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return ReprocesoSerializer
        return DetalleReprocesoSerializer
    
    def retrieve(self, request, pk=None, ):
        produccion = get_object_or_404(Reproceso, pk=pk)
        serializer = self.get_serializer(produccion)
        return Response(serializer.data)
    
    def list(self, request, ):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail = True, methods=['GET'], url_path = 'pdf-documento-entrada')
    def pdf_documento_entrada(self, request, pk=None):
        reproceso = Reproceso.objects.filter(pk = pk).first()
        bins_reproceso = BinsEnReproceso.objects.filter(reproceso = reproceso)
        
        resultados = []
        
        for bin in bins_reproceso:
            kilos_fruta = get_kilos_bin(bin)
            codigo_tarja = obtener_codigo_tarja(bin)
            variedad = get_variedad_display(bin)
            calibre = get_variedad_display(bin)
            programa = get_programa_description(bin)
            procesado = bin.bin_procesado
            
            dic = {
                "codigo_tarja": codigo_tarja,
                "programa": programa,
                "kilos_fruta": kilos_fruta,
                "variedad": variedad,
                "calibre": calibre,
                "procesado": procesado
                }
            
            resultados.append(dic)
            
        serializer_resultado = PDFEntradaReprocesoSerializer(data = resultados, many = True)
        serializer_resultado.is_valid(raise_exception=True)
        
        return Response(serializer_resultado.data)
    
    @action(detail = True, methods=['GET'], url_path='pdf-documento-salida')
    def pdf_documento_salida(self, request, pk = None):
        reproceso = Reproceso.objects.filter(pk = pk).first()
        bins_resultante_reproceso = TarjaResultanteReproceso.objects.filter(reproceso = reproceso)
        
        resultados = []
        
        for bin in bins_resultante_reproceso:
            if bin.tipo_resultante in ['1', '2', '4']:
                bodega = BodegaG1Reproceso.objects.get(reproceso = bin)
                variedad = bodega.get_variedad_display()
                calibre = bodega.get_calibre_display()
            else:
                bodega = BodegaG2Reproceso.objects.get(reproceso = bin)
                variedad = bodega.get_variedad_display()
                calibre = bodega.get_calibre_display()
                
            kilos_fruta = round(bin.peso - bin.tipo_patineta, 2)
            codigo_tarja = bin.codigo_tarja
            fecha_creacion = bin.fecha_creacion
            
            dic = {
                "codigo_tarja": codigo_tarja,
                "kilos_fruta": kilos_fruta,
                "variedad": variedad,
                "calibre": calibre,
                "fecha_creacion": fecha_creacion
                }
            
            resultados.append(dic)
            
        serializer_resultado = PDFSalidaReprocesoSerializer(data = resultados, many = True)
        serializer_resultado.is_valid(raise_exception=True)
        serializer_reproceso = DetalleReprocesoSerializer(reproceso)
        
        return Response({
            "reproceso": serializer_reproceso.data,
            "bines_entrada": serializer_resultado.data
        })
            
    @action(detail=False, methods=['POST'], url_path='pdf-operario-resumido')
    def pdf_operario(self, request):
        desde_str = request.data.get('desde').replace('Z', '')
        hasta_str = request.data.get('hasta').replace('Z', '')

        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
            hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError as e:
            return Response({'detail': f'Error en la conversión de fechas: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        operario_front = request.data.get('operario')
        if not operario_front:
            return Response({'detail': 'El campo operario es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            operario_select = Operario.objects.get(pk=operario_front)
        except Operario.DoesNotExist:
            return Response({'detail': 'Operario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        reproceso = Reproceso.objects.filter(Q(fecha_inicio_proceso__gte=desde) & Q(fecha_termino_proceso__lte=hasta))

        resultado_seria = {}
        nombre_operario = None

        try:
            for programa in reproceso:
                operarios_en_programa = OperariosEnReproceso.objects.filter(reproceso=programa.pk, operario=operario_select)

                if operarios_en_programa.exists():
                    nombre_operario = f'{operarios_en_programa.first().operario.nombre} {operarios_en_programa.first().operario.apellido}'

                    total_kilos_operario = DiaDeOperarioReproceso.objects.filter(
                        operario__in=operarios_en_programa
                    ).aggregate(total_kilos=Sum('kilos_dia'))['total_kilos'] or 0

                    total_prelimpia = 0
                    total_despelonada = 0

                    for operario_asignado in operarios_en_programa:
                        if operario_asignado.skill_operario == 'p_limpia':
                            try:
                                pago_x_kilo_operario_prelimpia = operario_asignado.operario.skilloperario_set.get(tipo_operario='p_limpia').pago_x_kilo
                                kilos = DiaDeOperarioReproceso.objects.filter(operario=operario_asignado).aggregate(Sum('kilos_dia'))['kilos_dia__sum'] or 0
                                total_prelimpia += round(pago_x_kilo_operario_prelimpia * kilos, 2)
                            except SkillOperario.DoesNotExist:
                                total_prelimpia += 0
                        elif operario_asignado.skill_operario == 'despelo':
                            try:
                                pago_x_kilo_operario_despelonado = operario_asignado.operario.skilloperario_set.get(tipo_operario='despelo').pago_x_kilo
                                kilos = DiaDeOperarioReproceso.objects.filter(operario=operario_asignado).aggregate(Sum('kilos_dia'))['kilos_dia__sum'] or 0
                                total_despelonada += round(pago_x_kilo_operario_despelonado * kilos, 2)
                            except SkillOperario.DoesNotExist:
                                total_despelonada += 0

                    if programa.pk not in resultado_seria:
                        resultado_seria[programa.pk] = {
                            "numero_programa": programa.numero_programa,
                            "nombre_operario": nombre_operario,
                            "kilos_programa": round(total_kilos_operario, 2),
                            "pre_limpia": total_prelimpia if total_prelimpia > 0 else "No Tiene este Skill",
                            "despelonado": total_despelonada if total_despelonada > 0 else "No Tiene este Skill",
                            "neto": round(total_prelimpia + total_despelonada, 2)
                        }

            return Response({
                "operario": nombre_operario,
                "programas": list(resultado_seria.values())
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['POST'], url_path='pdf-reproceso')
    def pdf_reproceso(self, request):
        desde_str = request.data.get('desde').replace('Z', '')
        hasta_str = request.data.get('hasta').replace('Z', '')
    
        # Convertir las cadenas de fecha a objetos de datetime y luego extraer las fechas
        desde = datetime.strptime(desde_str, '%Y-%m-%dT%H:%M:%S.%f')
        hasta = datetime.strptime(hasta_str, '%Y-%m-%dT%H:%M:%S.%f')
        
        queryset = Reproceso.objects.filter(Q(fecha_creacion__gte=desde) & Q(fecha_creacion__lte=hasta))
        resultados = []
        total_kilos_procesados = 0
        
        for bin in BinsEnReproceso.objects.filter(reproceso__in = queryset):
            total_kilos_procesados += bin.binbodega.kilos_bin

        for reproceso in queryset:

            numero_programa = reproceso.id
            total_kilos_ingresados = 0
            total_kilos_salientes = 0
            for bin in BinsEnReproceso.objects.filter(reproceso = reproceso):
                total_kilos_ingresados += bin.binbodega.kilos_bin
                
            for bin in TarjaResultanteReproceso.objects.filter(reproceso = reproceso):
                total_kilos_salientes += round(bin.peso - bin.tipo_patineta, 2)
            fecha_creacion = reproceso.fecha_creacion
            dias_duracion = calcular_duracion(reproceso.fecha_inicio_proceso, reproceso.fecha_termino_proceso)

            resultados.append({
                'numero_programa': numero_programa,
                'total_kilos_ingresados': round(total_kilos_ingresados, 2),
                'total_kilos_salientes': round(total_kilos_salientes, 2),
                'fecha_creacion': fecha_creacion,
                'dias_duracion': dias_duracion
            })
        
        return Response({
            "total_kilos_procesados": total_kilos_procesados,
            "detalle_programas": resultados
            })

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
        reproceso = self.get_object()
        operario_id = request.data.get('operario_id')
        skill_operario = request.data.get('skill_operario')

        operario = get_object_or_404(Operario, pk=operario_id)
        OperariosEnReproceso.objects.create(
            reproceso=reproceso,
            operario=operario,
            skill_operario=skill_operario
        )
        return Response({'status': 'Operario registrado en el reproceso'}, status=status.HTTP_201_CREATED)
   
    @action(detail=True, methods=['POST'])
    def asignar_dias_kilos(self, request, pk=None):
        reproceso = self.get_object()
        
        
        if reproceso.fecha_inicio_proceso and reproceso.fecha_termino_proceso:
            start_date = reproceso.fecha_inicio_proceso
            end_date = reproceso.fecha_termino_proceso

            laborable_dates = self.get_laborable_dates(start_date, end_date)
            num_laborable_days = len(laborable_dates)

            operarios_limpia = OperariosEnReproceso.objects.filter(reproceso=reproceso, skill_operario='p_limpia')
            operarios_despelo = OperariosEnReproceso.objects.filter(reproceso=reproceso, skill_operario='despelo')

            # Calcular total de kilos input manualmente usando la propiedad kilos_bin
            total_kilos_input = sum(bin.binbodega.kilos_bin for bin in BinsEnReproceso.objects.filter(reproceso=reproceso))

            total_kilos_output = TarjaResultanteReproceso.objects.filter(reproceso=reproceso).aggregate(
                total_kilos=models.Sum(models.F('peso') - models.F('tipo_patineta'))
            )['total_kilos'] or 0
            
            kilos_por_dia_limpia = total_kilos_input / (num_laborable_days )
            for operario in operarios_limpia:
                for laborable_date in laborable_dates:
                    DiaDeOperarioReproceso.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        defaults={'kilos_dia': kilos_por_dia_limpia}
                    )

            kilos_por_dia_despelo = total_kilos_output / (num_laborable_days )
            for operario in operarios_despelo:
                for laborable_date in laborable_dates:
                    DiaDeOperarioReproceso.objects.update_or_create(
                        operario=operario,
                        dia=laborable_date,
                        defaults={'kilos_dia': kilos_por_dia_despelo}
                    )

            return Response({'status': 'Días y kilos asignados a operarios'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Fechas de inicio o término no definidas'}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['GET'])
    def lista_operarios_dias(self, request, pk=None):
        reproceso = self.get_object()
        operarios_en_reproceso = OperariosEnReproceso.objects.filter(reproceso=reproceso)
        serializer = OperariosEnReprocesoSerializer(operarios_en_reproceso, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def dias_trabajados_operario(self, request, pk=None):
        reproceso = get_object_or_404(Reproceso, pk=pk)
        operario_id = request.query_params.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        operario = get_object_or_404(Operario, pk=operario_id)
        operarios_en_reproceso = OperariosEnReproceso.objects.filter(reproceso=reproceso, operario=operario).first()
        
        if not operarios_en_reproceso:
            return Response({'error': 'No se encontraron registros de trabajo para este operario en el reproceso especificado'}, status=status.HTTP_404_NOT_FOUND)

        dias_trabajados = DiaDeOperarioReproceso.objects.filter(operario=operarios_en_reproceso)
        serializer = DiaDeOperarioReprocesoSerializer(dias_trabajados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def actualizar_ausente(self, request, pk=None):
        dia_id = request.data.get('dia_id')
        if not dia_id:
            return Response({'error': 'dia_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        dia = get_object_or_404(DiaDeOperarioReproceso, pk=dia_id)
        
        serializer = DiaDeOperarioReprocesoUpdateSerializer(dia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def eliminar_operario(self, request, pk=None):
        reproceso = get_object_or_404(Reproceso, pk=pk)
        operario_id = request.data.get('operario_id')
        if not operario_id:
            return Response({'error': 'operario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            operario = get_object_or_404(OperariosEnReproceso, reproceso=reproceso, pk=operario_id)
            if operario:
                operario.delete()
                return Response({'status': 'Operario eliminado de la producción'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'No se encontro el operario en la producción'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=True, methods=['GET'])
    def estado_termino_programa(self, request, pk=None):
        reproceso = get_object_or_404(Reproceso, pk=pk)
        tarjas = reproceso.tarjaresultantereproceso_set.filter(esta_eliminado=False)
        cc_tarja_resultante = CCTarjaResultanteReproceso.objects.filter(tarja__in=tarjas)
        
        # Verificar control de calidad de las tarjas
        tarjas_sin_cc = [cc for cc in cc_tarja_resultante if cc.estado_cc != '3']
        if len(tarjas_sin_cc) == 0:
            cc_estado_text = "Todas las tarjas tienen su control de calidad."
        else:
            cc_estado_text = f"{len(tarjas_sin_cc)} tarjas sin control de calidad."
        
        # Verificar operarios en producción
        operarios_reproceso = OperariosEnReproceso.objects.filter(reproceso=reproceso)
        if operarios_reproceso.exists():
            operarios_estado_text = f"Se han agregado {operarios_reproceso.count()} operarios a este reproceso."
        else:
            operarios_estado_text = "No hay operarios registrados."

        # Verificar estado de los lotes programa
        lotes_programa = BinsEnReproceso.objects.filter(reproceso=reproceso)
        lotes_pendientes = lotes_programa.filter(bin_procesado=False).count()
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
        reproceso = get_object_or_404(Reproceso, pk=pk)
        operarios_reproceso = OperariosEnReproceso.objects.filter(reproceso=reproceso)

        estado_dias = []
        for operario in operarios_reproceso:
            dias_trabajados = DiaDeOperarioReproceso.objects.filter(operario=operario)
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
                    
class BinsEnReprocesoViewSet(viewsets.ModelViewSet):
    queryset = BinsEnReproceso.objects.all()
    serializer_class = BinsEnReprocesoSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = BinsEnReproceso.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return BinsEnReprocesoSerializer
        return DetalleBinsEnReprocesoSerializer
    
    def retrieve(self, request,reproceso_pk=None, pk=None):
        reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
        produccion = get_object_or_404(self.get_queryset(),reproceso=reproceso, pk=pk)
        serializer = self.get_serializer(produccion)
        return Response(serializer.data)
    
    def list(self, request, reproceso_pk=None, ):
        reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
        queryset = get_list_or_404(BinsEnReproceso, reproceso=reproceso)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def registrar_bins_reproceso(self, request, reproceso_pk=None):
        bins = request.data.get('bins', [])

        for bin_data in bins:
            pkbinbodega = bin_data.get('id')
            binbodega = get_object_or_404(BinBodega, pk=pkbinbodega)
      
            bin_obj = BinsEnReproceso.objects.create(
                reproceso_id=reproceso_pk,
                binbodega=binbodega
                
            )
            bin_obj.save()
            binbodega.ingresado = True
            binbodega.save()
            

        return Response({"mensaje": "Bins registrados exitosamente"}, status=status.HTTP_201_CREATED)
    
class TarjaResultanteReprocesoViewSet(viewsets.ModelViewSet):
    queryset = TarjaResultanteReproceso.objects.all()
    serializer_class = TarjaResultanteReprocesoSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = TarjaResultanteReproceso.objects.filter(fecha_creacion__year = anio, esta_eliminado = False)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return TarjaResultanteReprocesoSerializer
        return DetalleTarjaResultanteReprocesoSerializer
    
    def retrieve(self, request,reproceso_pk=None, pk=None):
        reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
        produccion = get_object_or_404(self.get_queryset(),reproceso=reproceso, pk=pk)
        serializer = self.get_serializer(produccion)
        return Response(serializer.data)
    
    def list(self, request, reproceso_pk=None):
        produccion = get_object_or_404(Reproceso, pk=reproceso_pk)
        queryset = TarjaResultanteReproceso.objects.filter(reproceso=produccion, esta_eliminado = False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    # @action(detail=False, methods=['PUT', 'PATCH'])
    # def eliminar_tarja_reproceso(self, request, reproceso_pk=None,):
    #     print(request.data.get('id'))
    #     reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
    #     queryset = get_object_or_404(self.get_queryset(), reproceso=reproceso, pk = request.data.get('id'))
    #     if queryset.cc_tarja != True:
    #         queryset.esta_eliminado = request.data.get('esta_eliminado')
    #         if (queryset.tipo_resultante == '1'):
    #             ct = ContentType.objects.get_for_model(BodegaG1Reproceso)
    #             bodegag1 = BodegaG1Reproceso.objects.filter(reproceso = queryset.pk).first()
    #             BinBodega.objects.filter(id_binbodega = bodegag1.id, tipo_binbodega = ct).update(estado_binbodega = '1') # type: ignore
    #         elif (queryset.tipo_resultante == '3'):
    #             ct = ContentType.objects.get_for_model(BodegaG2Reproceso)
    #             bodegag2 = BodegaG2Reproceso.objects.filter(reproceso = queryset.pk).first()
    #             BinBodega.objects.filter(id_binbodega = bodegag2.id, tipo_binbodega = ct).update(estado_binbodega = '1') # type: ignore
    #         queryset.save()
    #         serializer = self.get_serializer(queryset)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     else:
    #         return Response({ 'message': 'No se puede eliminar la tarja una vez se a calibrado ' })    

# class OperariosEnReprocesoViewSet(viewsets.ModelViewSet):
#     queryset = OperariosEnReproceso.objects.all()
#     serializer_class = OperariosEnReprocesoSerializer
#     permission_classes = [IsAuthenticated,]
    
#     def get_queryset(self):
#         user = self.request.user
#         try:
#             anio = PersonalizacionPerfil.objects.get(usuario= user).anio
#             if anio == 'Todo':
#                 return self.queryset
#             else:
#                 qs = OperariosEnReproceso.objects.filter(fecha_creacion__year = anio)
#                 return qs
#         except:
#             return self.queryset
    
#     # def get_serializer_class(self):        
#     #     if self.action in ["create", "update", "partial_update", "destroy"]:
#     #         return OperariosEnReprocesoSerializer
#     #     return DetalleOperariosEnReprocesoSerializer
    
#     def retrieve(self, request,reproceso_pk=None, pk=None):
#         reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
#         produccion = get_object_or_404(self.get_queryset(),reproceso=reproceso, pk=pk)
#         serializer = self.get_serializer(produccion)
#         return Response(serializer.data)
    
#     def list(self, request, reproceso_pk=None):
#         produccion = get_object_or_404(Reproceso, pk=reproceso_pk)
#         queryset = OperariosEnReproceso.objects.filter(reproceso=produccion)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
    
    
#     @action(detail=False, methods=['get'])
#     def lista_filtrada_por_operario(self, request, reproceso_pk=None):
#         reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
#         operarios_agregados = OperariosEnReproceso.objects.filter(reproceso=reproceso).annotate(
#             dia_truncado=TruncDate('dia')  # Truncar la hora y conservar solo la fecha
#         ).values(
#             'operario__rut',
#             'operario__nombre', 
#             'operario__apellido',
#             'skill_operario',
#             'dia_truncado'  # Incluir día truncado para agrupación correcta
#         ).annotate(
#             total_kilos_producidos=Sum('kilos'),
#             dias_trabajados=Count('dia_truncado', distinct=True)
#         ).distinct().order_by('dia_truncado', 'operario__rut')  # Ordenar por día y RUT del operario

#         serializer = OperariosAgregadosSerializer(operarios_agregados, many=True)
#         return Response(serializer.data)
        
#     @action(detail=False, methods=['POST'])
#     def lista_detalle_dias_operario(self, request, reproceso_pk=None):
#             reproceso = get_object_or_404(Reproceso, pk=reproceso_pk)
#             rut_operario = request.data.get('rut')

#             # Filtrar operarios por producción y rut, y convertir fecha y hora a solo fecha
#             lista_operario = OperariosEnReproceso.objects.filter(
#                 reproceso=reproceso,
#                 operario__rut=rut_operario
#             ).annotate(
#                 fecha_operario=Cast('dia', output_field=DateField())
#             ).order_by('operario', 'fecha_operario', '-kilos')  # Asegurar que los registros con más kilos aparezcan primero

#             # Utilizar distinct sobre los campos operario y fecha_operario para asegurar registros únicos por día
#             lista_operario = lista_operario.distinct('operario', 'fecha_operario')

#             serializer = OperariosEnReprocesoSerializer(lista_operario, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK) # Ordenar por rut del operario y fecha_operario antes de aplicar 'distinct'
#                 # Asegurar un registro por operario y por día
    
#     @action(detail=False, methods=['DELETE'])
#     def eliminar_registro_dia_por_rut_y_id(self, request, reproceso_pk=None):
        # reproceso = get_object_or_404(Reproceso, pk = reproceso_pk)
        # OperariosEnReproceso.objects.filter(reproceso = reproceso, operario__rut = request.data.get('rut'), id = request.data.get('id')).delete()
        # return Response(status = status.HTTP_204_NO_CONTENT)
    
# class DashboardProgramasViewSet(viewsets.ViewSet):
#     @action(detail = False, methods = ['GET'])
#     def dashboard(self, request):
#         programas_produccion = Produccion.objects.exclude(estado = 5)
#         programa_reproceso = Reproceso.objects.exclude(estado = 4)
#         programa_seleccion = Seleccion.objects.exclude(estado_programa = 5)
#         programa_embalaje = Embalaje.objects.exclude(estado_embalaje = 5)
        
#         resultados = []
        
#         for programa in programas_produccion:
#             total_kilos_introducidos = 0
            
#             for lote in programa.lotesprograma_set.filter(bin_ingresado=True):
#                 total_kilos_introducidos += lote.bodega_techado_ext.kilos_fruta
        
#             total_kilos_resultantes = sum(
#                 tarja.peso 
#                 for tarja in programa.tarjaresultante_set.filter(esta_eliminado = False)
#             )

#             resultado = {
#                 'tipo_programa': 'Produccion',
#                 'total_kilos_introducidos': total_kilos_introducidos,
#                 'total_kilos_resultantes': total_kilos_resultantes,
#             }
#             resultados.append(resultado)
        
        
#         for programa in programa_reproceso:
#             total_kilos_introducidos = 0

#             for bin_reproceso in programa.binsenreproceso_set.filter(bin_ingresado=True):
#                 total_kilos_introducidos += bin_reproceso.bin_bodega.kilos_fruta

#             total_kilos_resultantes = sum(
#                 tarja.peso
#                 for tarja in programa.tarjaresultantereproceso_set.filter(esta_eliminado = False)
#             )

#             resultado = {
#                 'tipo_programa': 'Reproceso',
#                 'total_kilos_introducidos': total_kilos_introducidos,
#                 'total_kilos_resultantes': total_kilos_resultantes if total_kilos_resultantes else 0,
#             }
            
#             resultados.append(resultado)
        
        
#         # Selección
#         for programa in programa_seleccion:
#             total_kilos_introducidos = 0

#             for bin_pepa in BinsPepaCalibrada.objects.filter(seleccion=programa):
#                 total_kilos_introducidos += bin_pepa.pepa_calibrada.kilos_fruta

#             total_kilos_resultantes = sum(
#                 tarja.peso
#                 for tarja in TarjaSeleccionada.objects.filter(seleccion=programa, esta_eliminado=False)
#             )

#             resultado = {
#                 'tipo_programa': 'Seleccion',
#                 'total_kilos_introducidos': total_kilos_introducidos,
#                 'total_kilos_resultantes': total_kilos_resultantes if total_kilos_resultantes else 0,
#             }
#             resultados.append(resultado)
    
#         serializer = DashboardHomeSerializer(data = resultados, many = True)
#         serializer.is_valid(raise_exception = True)
        
#         return Response(serializer.data)