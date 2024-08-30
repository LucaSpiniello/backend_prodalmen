from rest_framework import serializers
from .models import *
from controlcalidad.models import *
from django.contrib.contenttypes.models import *
from bodegas.models import *
from django.db.models import Q, Sum, Count, Subquery, Max,  F
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, fields
import datetime


class BinResultanteProgramaSerializer(serializers.ModelSerializer):
    tipo_patineta_label = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    cc_tarja = serializers.SerializerMethodField()
    

    def get_cc_tarja(self, obj):
        cc_tarja = CCBinResultanteProgramaPH.objects.filter(bin_resultante = obj.pk, estado_cc = '1')
        print(cc_tarja)
        if cc_tarja.exists():
            return True
        else:
            return False
    
    def get_calidad(self, obj):
        return BodegaG6.objects.filter(programa = obj).first().get_calidad_display()
    
    def get_tipo_patineta_label(self, obj):
        return obj.get_tipo_patineta_display()
    
    class Meta:
        model = BinResultantePrograma
        fields = '__all__'
        
class BinParaProgramaSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    tipo_binbodega = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    cc_tarja = serializers.SerializerMethodField()
    programa = serializers.SerializerMethodField()

    def get_tipo_binbodega(self, obj):
        return str(obj.bin_bodega.tipo_binbodega)
            
    def get_kilos_fruta(self, obj):
            return obj.bin_bodega.kilos_bin
    
    
    def get_codigo_tarja(self, obj):
        return obj.bin_bodega.codigo_tarja_bin
      
    def get_cc_tarja(self, obj):
        return f'{obj.bin_bodega.variedad} - {obj.bin_bodega.calibre} - {obj.bin_bodega.calidad}'
                
    def get_programa(self, obj):
        return obj.bin_bodega.origen_tarja
    
    class Meta:
        model = BinParaPrograma
        fields = '__all__'
        
class ProgramaPHSerializer(serializers.ModelSerializer):
    condicion_inicio = serializers.SerializerMethodField()
    condicion_cierre = serializers.SerializerMethodField()
    condicion_termino = serializers.SerializerMethodField()
    estado_programa_label = serializers.SerializerMethodField()
    tipo_programa_label = serializers.SerializerMethodField()
    creado_por_nombre = serializers.SerializerMethodField()
    ubicacion_producto = serializers.SerializerMethodField()
    bins_ingresados_length = serializers.SerializerMethodField()
    metrica_bines = serializers.SerializerMethodField()
    rechazos_registrados = serializers.SerializerMethodField()
    bines_resultantes_kilos = serializers.SerializerMethodField()
    promedio_humedad = serializers.SerializerMethodField()
    promedio_piel = serializers.SerializerMethodField()
    merma_programa = serializers.SerializerMethodField()
    valor_referencial = serializers.SerializerMethodField()
    kilos_iniciales = serializers.SerializerMethodField()
    prueba_metricas = serializers.SerializerMethodField()
    
    def get_condicion_inicio(self, obj):
        variables = VariablesProgramaPH.objects.get(programa=obj.pk)
        if variables:
            if variables.lectura_luz_inicio == None and variables.lectura_gas_inicio == None:
                return False
            else:
                return True
        else:
            return False
        
    def get_prueba_metricas(self, obj):
        ingresados = BinParaPrograma.objects.filter(programa=obj)
        procesados = ingresados.filter(procesado=True).count()
        total_ingresados = ingresados.count()
        porcentaje_procesados = (procesados / total_ingresados * 100) if total_ingresados > 0 else 0
        resultantes = BinResultantePrograma.objects.filter(programa=obj).count()

        kilos_ingresados = sum(bin.bin_bodega.kilos_bin for bin in ingresados)
        kilos_resultantes = BinResultantePrograma.objects.filter(programa=obj).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )['total_kilos'] or 0

        eficiencia_produccion = (kilos_resultantes / kilos_ingresados * 100) if kilos_ingresados > 0 else 0

        tiempo_procesamiento = ingresados.annotate(
            duracion=ExpressionWrapper(F('fecha_modificacion') - F('bin_bodega__fecha_creacion'), output_field=fields.DurationField())
        ).aggregate(promedio=Avg('duracion'))['promedio'] or datetime.timedelta()

        rechazos = RechazoPrograma.objects.filter(programa=obj).aggregate(total_rechazos=Sum('kilos_rechazo'))['total_rechazos'] or 0
        porcentaje_rechazos = (rechazos / kilos_ingresados * 100) if kilos_ingresados > 0 else 0

        procesamiento_data = []
        for bin in ingresados:
            if bin.procesado:
                duracion = (bin.fecha_modificacion - bin.bin_bodega.fecha_creacion).total_seconds()
                procesamiento_data.append({
                    'kilos': bin.bin_bodega.kilos_bin,
                    'hora_procesado': bin.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'segundos_duracion': duracion,
                    'eficiencia': (bin.bin_bodega.kilos_bin / kilos_ingresados * 100) if kilos_ingresados > 0 else 0
                })

        variables = VariablesProgramaPH.objects.filter(programa=obj).first()
        if variables.lectura_gas_termino and variables.lectura_gas_inicio:
            consumo_gas = variables.lectura_gas_termino - variables.lectura_gas_inicio
        else:
            consumo_gas = 0
        if variables.lectura_luz_termino and variables.lectura_luz_inicio:
            consumo_luz = variables.lectura_luz_termino - variables.lectura_luz_inicio
        else:
            consumo_luz = 0
        return {
            "ingresados": total_ingresados,
            "procesados_porcentaje": porcentaje_procesados,
            "cantidad_rechazos": rechazos,
            "porcentaje_rechazos": porcentaje_rechazos,
            "kilos_ingresados": kilos_ingresados,
            "kilos_resultantes": kilos_resultantes,
            "eficiencia_produccion": eficiencia_produccion,
            "duracion_promedio_procesamiento": tiempo_procesamiento.total_seconds(),
            "consumo_gas": consumo_gas,
            "consumo_luz": consumo_luz,
            "detalles_procesamiento": procesamiento_data
        }

        
    def get_metrica_bines(self, obj):
        ingresados = BinParaPrograma.objects.filter(programa=obj)
        procesados = ingresados.filter(procesado=True).count()
        total_ingresados = ingresados.count()
        porcentaje_procesados = (procesados / total_ingresados * 100) if total_ingresados > 0 else 0
        resultante = BinResultantePrograma.objects.filter(programa=obj).count()

        # Calculando la eficiencia de producción
        kilos_ingresados = 0
        for bin in ingresados:
            kilos_ingresados += bin.bin_bodega.kilos_bin
        kilos_resultantes = BinResultantePrograma.objects.filter(programa=obj).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )['total_kilos'] or 0

        eficiencia_produccion = (kilos_resultantes / kilos_ingresados * 100) if kilos_ingresados > 0 else 0
        print(eficiencia_produccion)
        # Tiempo promedio de procesamiento
        tiempo_procesamiento = ingresados.annotate(
            duracion=ExpressionWrapper(F('fecha_modificacion') - F('bin_bodega__fecha_creacion'), output_field=fields.DurationField())
        ).aggregate(promedio=Avg('duracion'))['promedio'] or datetime.timedelta()

        # Cantidad de rechazos
        rechazos = RechazoPrograma.objects.filter(programa=obj).aggregate(total_rechazos=Sum('kilos_rechazo'))['total_rechazos'] or 0
        porcentaje_rechazos = (rechazos / kilos_ingresados * 100) if kilos_ingresados > 0 else 0
        
        procesamiento_data = []
        for bin in ingresados:
            if bin.procesado:
                duracion = (bin.fecha_modificacion - bin.bin_bodega.fecha_creacion).total_seconds()
                procesamiento_data.append({
                    'kilos': bin.bin_bodega.kilos_bin,
                    'hora_procesado': bin.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'segundos_duracion': duracion,
                    'eficiencia': (bin.bin_bodega.kilos_bin / kilos_ingresados * 100) if kilos_ingresados > 0 else 0
                })

        return {
            "ingresados": total_ingresados,
            "procesados_porcentaje": porcentaje_procesados,
            "cantidad_rechazos": rechazos,
            "porcentaje_rechazos": porcentaje_rechazos,
            "detalles_procesamiento": procesamiento_data
        }
        
    
    def get_kilos_iniciales(self, obj: ProgramaPH):
        kilos_inicio = 0
        for bin in BinParaPrograma.objects.filter(programa = obj):
            kilos_inicio += bin.bin_bodega.kilos_bin
        return kilos_inicio
    
    def get_valor_referencial(self, obj: ProgramaPH):
        kilos_inicio = 0
        for bin in BinParaPrograma.objects.filter(programa = obj):
            kilos_inicio += bin.bin_bodega.kilos_bin
        
        return round((kilos_inicio * float(obj.perdidaprograma)) / 100)
        
    
    
    def get_promedio_humedad(self, obj):
        bines_resultantes = BinResultantePrograma.objects.filter(programa = obj, estado_bin = '2').values_list('pk', flat=True)
        cdc = CCBinResultanteProgramaPH.objects.filter(bin_resultante__in = bines_resultantes).aggregate(promedio = Avg('humedad'))['promedio']
        if cdc is None:
            return 0
        return round(cdc, 2 )
        
    def get_promedio_piel(self, obj):
        bines_resultantes = BinResultantePrograma.objects.filter(programa = obj, estado_bin = '2').values_list('pk', flat=True)
        cdc = CCBinResultanteProgramaPH.objects.filter(bin_resultante__in = bines_resultantes).aggregate(promedio = Avg('piel_aderida'))['promedio']
        if cdc is None:
            return 0
        return round(cdc, 2 )
        
    def get_merma_programa(self, obj: ProgramaPH):
        kilos_inicio = 0
        for bin in BinParaPrograma.objects.filter(programa = obj):
            kilos_inicio += bin.bin_bodega.kilos_bin

        perdida_esperada = (kilos_inicio * float(obj.perdidaprograma)) / 100
        

        # Suma de kilos de bins resultantes aprobados.
        kilos_aprobado = BinResultantePrograma.objects.filter(
            programa=obj, estado_bin='2'
        ).aggregate(
            total_kilos_aprobado=Sum(F('peso')-F('tipo_patineta'))
        )['total_kilos_aprobado'] or 0
        

        # Suma de kilos de rechazos registrados.
        kilos_rechazo = RechazoPrograma.objects.filter(
            programa=obj
        ).aggregate(
            total_kilos_rechazo=Sum('kilos_rechazo')
        )['total_kilos_rechazo'] or 0

        #print(f'PRUEBAS DE SERIALIZADOR {kilos_aprobado} {kilos_rechazo} {perdida_esperada}')
        # Calcula la merma real considerando la producción aprobada y los rechazos.
        merma_real = (kilos_inicio-perdida_esperada) - (kilos_aprobado - kilos_rechazo)

        # Calcular el porcentaje de merma respecto a los kilos iniciales.
        if kilos_inicio > 0:
            porcentaje_merma = (merma_real / kilos_inicio) * 100
            return {
                "merma_real": round(merma_real, 2),
                "porcentaje_merma": round(porcentaje_merma, 2)
                } 
        else:
            return 0  # Retorna 0 si no hay kilos iniciales para evitar división por cero.

    def get_rechazos_registrados(self, obj):
        rechazo = RechazoPrograma.objects.filter(programa=obj).aggregate(
            total_suma=Sum('kilos_rechazo')
        )
        if rechazo['total_suma'] != None:
            return rechazo['total_suma']
        else:
            return 0
        
    def get_bines_resultantes_kilos(self, obj):
        kilos_totales_procesados = BinResultantePrograma.objects.filter(programa = obj, esta_eliminado=False).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )
        
        if kilos_totales_procesados['total_kilos'] != None:
            return kilos_totales_procesados['total_kilos']
        else:
            return 0

    def get_condicion_termino(self, obj):
        bines = all(obj.binparaprograma_set.filter(procesado=True))
        operarios = obj.operarios.count()
        variables = VariablesProgramaPH.objects.filter(programa = obj).first()
        bines_resultantes = BinResultantePrograma.objects.filter(programa = obj).count()
        cc_bines = CCBinResultanteProgramaPH.objects.filter(bin_resultante__in = obj.binresultanteprograma_set.all(), estado_cc = '0').exists()
        
        if variables.lectura_luz_inicio and variables.lectura_gas_inicio \
            and not cc_bines and operarios >= 1 and bines and bines_resultantes >= 1:
                return True
        return False
    
    def get_condicion_cierre(self, obj):
        bines = all(obj.binparaprograma_set.filter(procesado=True))
        operarios = obj.operarios.count()
        variables = VariablesProgramaPH.objects.filter(programa = obj).first()
        bines_resultantes = BinResultantePrograma.objects.filter(programa = obj).count()
        cc_bines = CCBinResultanteProgramaPH.objects.filter(bin_resultante__in = obj.binresultanteprograma_set.all(), estado_cc = '0').exists()

        if bines and operarios >= 1 and variables.lectura_luz_inicio and variables.lectura_gas_inicio \
            and not cc_bines and variables.lectura_luz_termino and variables.lectura_gas_termino and bines_resultantes >=1 :
                return True
        return False
    
    def get_cc_tarja(self, obj):
        cc_tarja = CCBinResultanteProgramaPH.objects.filter(bin_resultante=obj, estado_cc='1').first()
        return cc_tarja is not None
    
    def get_bins_ingresados_length(self, obj):
        return obj.binparaprograma_set.all().count()
    
    def get_ubicacion_producto(self, obj):
        return obj.get_ubicacion_produc_display()

    def get_tipo_programa_label(self, obj):
        return obj.get_tipo_programa_display()
    
    def get_creado_por_nombre(self, obj):
        return f'{obj.creado_por.first_name} {obj.creado_por.last_name}'    
    
    def get_estado_programa_label(self, obj):
        return obj.get_estado_programa_display()
    

    class Meta: 
        model = ProgramaPH
        exclude = ['bin_bodegas', 'operarios']

class OperariosEnProgramaPHSerializer(serializers.ModelSerializer):
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
    
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
    
    class Meta:
        model = OperariosEnProgramaPH
        fields = '__all__'

class RechazoProgramaSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.SerializerMethodField()
    tipo_rechazo_label = serializers.SerializerMethodField()
    
    def get_tipo_rechazo_label(self, obj):
        return obj.get_tipo_rechazo_display()
    
    def get_registrado_por_nombre(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    class Meta:
        model = RechazoPrograma
        fields = '__all__'

class VariablesProgramaPHSerializer(serializers.ModelSerializer):
    resultado_luz = serializers.SerializerMethodField()
    resultado_gas = serializers.SerializerMethodField()
    
    def get_resultado_luz(self, obj):
        if obj.lectura_luz_inicio and obj.lectura_luz_termino:
            return round(obj.lectura_luz_termino - obj.lectura_luz_inicio, 2)
        else:
            return 0
        
    def get_resultado_gas(self, obj):
        if obj.lectura_gas_inicio and obj.lectura_gas_termino:
            return round(obj.lectura_gas_inicio - obj.lectura_gas_termino, 2)
        else:
            return 0
         
    class Meta:
        model = VariablesProgramaPH
        fields = '__all__'

class OperariosAgregadosSerializer(serializers.Serializer):
    operario__rut = serializers.CharField()
    operario__nombre = serializers.CharField()
    operario__apellido = serializers.CharField()
    skill_operario = serializers.CharField()
    total_kilos_producidos = serializers.FloatField()
    dias_trabajados = serializers.IntegerField()      
    
    
#### Proceso PH

class ProcesoPHSerializer(serializers.ModelSerializer):
    condicion_cierre = serializers.SerializerMethodField()
    condicion_termino = serializers.SerializerMethodField()
    estado_proceso_label = serializers.SerializerMethodField()
    tipo_proceso_label = serializers.SerializerMethodField()
    creado_por_nombre = serializers.SerializerMethodField()
    bins_ingresados_length = serializers.SerializerMethodField()
    
    rechazos_registrados = serializers.SerializerMethodField()
    bines_resultantes_kilos = serializers.SerializerMethodField()
    promedio_humedad = serializers.SerializerMethodField()
    promedio_piel = serializers.SerializerMethodField()
    merma_proceso = serializers.SerializerMethodField()
    valor_referencial = serializers.SerializerMethodField()
    kilos_iniciales = serializers.SerializerMethodField()
    condicion_inicio = serializers.SerializerMethodField()

    def get_condicion_inicio(self, obj):
        variables = VariablesProcesoPH.objects.get(proceso=obj.pk)
        if variables:
            if variables.lectura_luz_inicio == None and variables.lectura_gas_inicio == None:
                return False
            else:
                return True
        else:
            return False
    
    
    def get_kilos_iniciales(self, obj: ProcesoPH):
        kilos_inicio = 0
        for bin in BinsParaProceso.objects.filter(proceso = obj):
            kilos_inicio += bin.bin_bodega.binbodega.kilos_fruta
        
        return kilos_inicio
    
    def get_valor_referencial(self, obj: ProcesoPH):
        kilos_inicio = 0
        for bin in BinsParaProceso.objects.filter(proceso = obj):
            kilos_inicio += bin.bin_bodega.binbodega.kilos_fruta
        
        return round((kilos_inicio * float(obj.perdidaproceso)) / 100)
        
    
    
    def get_promedio_humedad(self, obj):
        bin_resultante = BinResultanteProceso.objects.filter(proceso = obj, estado_bin = '2')
        humedad = []
        for x in bin_resultante:
            cc_bin = CCBinResultanteProcesoPH.objects.filter(bin_resultante = x).first()
            humedad.append(cc_bin.humedad)
            
     
        if len(humedad) > 0:
            resultado = sum(humedad) / len(humedad) 
            return resultado      
        else:
            return 0
        
    def get_promedio_piel(self, obj):
        bin_resultante = BinResultanteProceso.objects.filter(proceso = obj, estado_bin = '2')
        piel = []
        for x in bin_resultante:
            cc_bin = CCBinResultanteProcesoPH.objects.filter(bin_resultante = x).first()
            piel.append(cc_bin.piel_aderida)
            

        if len(piel) > 0:
            resultado = sum(piel) / len(piel) 
            return resultado      
        else:
            return 0
        
    def get_merma_proceso(self, obj: ProcesoPH):
        kilos_inicio = 0
        for bin in BinsParaProceso.objects.filter(proceso = obj):
            kilos_inicio += bin.bin_bodega.binbodega.kilos_fruta

        perdida_esperada = (kilos_inicio * float(obj.perdidaproceso)) / 100

        # Suma de kilos de bins resultantes aprobados.
        kilos_aprobado = BinResultanteProceso.objects.filter(
            proceso=obj, estado_bin='2'
        ).aggregate(
            total_kilos_aprobado=Sum('peso')
        )['total_kilos_aprobado'] or 0

        # Suma de kilos de rechazos registrados.
        kilos_rechazo = RechazoProcesoPH.objects.filter(
            proceso=obj
        ).aggregate(
            total_kilos_rechazo=Sum('kilos_fruta')
        )['total_kilos_rechazo'] or 0

        # Calcula la merma real considerando la producción aprobada y los rechazos.
        merma_real = kilos_inicio - (kilos_aprobado - kilos_rechazo + perdida_esperada)

        # Calcular el porcentaje de merma respecto a los kilos iniciales.
        if kilos_inicio > 0:
            porcentaje_merma = (merma_real / kilos_inicio) * 100
            return {
                "merma_real": round(merma_real, 2),
                "porcentaje_merma": round(porcentaje_merma, 2)
                } 
        else:
            return 0  # Retorna 0 si no hay kilos iniciales para evitar división por cero.

            
    def get_bines_resultantes_kilos(self, obj):
        kilos_totales_procesados = BinResultanteProceso.objects.filter(proceso = obj, esta_eliminado=False).aggregate(
            total_kilos=Sum(F('peso') - F('tipo_patineta'))
        )
        
        if kilos_totales_procesados['total_kilos'] != None:
            return kilos_totales_procesados['total_kilos']
        else:
            return 0
            
        
        
    def get_rechazos_registrados(self, obj):
        rechazo = RechazoProcesoPH.objects.filter(proceso=obj).aggregate(
            total_suma=Sum('kilos_fruta')
        )
        if rechazo['total_suma'] != None:
            return rechazo['total_suma']
        else:
            return 0

    
    def get_bins_ingresados_length(self, obj):
        return obj.binsparaproceso_set.all().count()
    
    def get_tipo_proceso_label(self, obj):
        return obj.get_tipo_proceso_display()
    
    def get_creado_por_nombre(self, obj):
        return f'{obj.creado_por.first_name} {obj.creado_por.last_name}'    
    
    def get_estado_proceso_label(self, obj):
        return obj.get_estado_proceso_display()
    
    def get_condicion_termino(self, obj):
        bines = all(obj.binsparaproceso_set.filter(procesado=True))
        operarios = obj.operarios.count()
        variables = VariablesProcesoPH.objects.filter(proceso = obj).first()
        bines_resultantes = BinResultanteProceso.objects.filter(proceso = obj).count()
        cc_bines = CCBinResultanteProcesoPH.objects.filter(bin_resultante__in = obj.binresultanteproceso_set.all(), estado_control = '0').exists()
        if variables.lectura_luz_inicio and variables.lectura_gas_inicio \
            and not cc_bines and operarios >= 1 and bines and bines_resultantes >= 1:
                return True
        return False
        
    
    def get_condicion_cierre(self, obj):
        bines = all(obj.binsparaproceso_set.filter(procesado=True))
        operarios = obj.operarios.count()
        variables = VariablesProcesoPH.objects.filter(proceso = obj).first()
        bines_resultantes = BinResultanteProceso.objects.filter(proceso = obj).count()
        cc_bines = CCBinResultanteProcesoPH.objects.filter(bin_resultante__in = obj.binresultanteproceso_set.all(), estado_control = '0').exists()

        if bines and operarios >= 1 and variables.lectura_luz_inicio and variables.lectura_gas_inicio \
            and not cc_bines and variables.lectura_luz_termino and variables.lectura_gas_termino and bines_resultantes >=1 :
                return True
        return False


    def get_cc_tarja(self, obj):
        cc_tarja = CCBinResultanteProcesoPH.objects.filter(bin_resultante=obj, estado_control='1').first()
        return cc_tarja is not None

    
    class Meta:
        model = ProcesoPH
        exclude = ['bin_bodegas', 'operarios']

class BinsParaProcesoSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    tipo_binbodega = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    cc_tarja = serializers.SerializerMethodField()
    programa = serializers.SerializerMethodField()
    
    def get_tipo_binbodega(self, obj):
        def resolve_tipo(bin_bodega):
            if bin_bodega.tipo_binbodega.model != 'frutasobrantedeagrupacion':
                return bin_bodega.tipo_binbodega.model
            while bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
                bin_bodega = bin_bodega.tarja  # Asumiendo que `tarja` es la propiedad correcta para seguir la cadena
                if bin_bodega is None:
                    break
            return bin_bodega.tipo_binbodega.model if bin_bodega else 'Tipo desconocido'
        return resolve_tipo(obj.bin_bodega)
        
    
    
    def get_kilos_fruta(self, obj):
        if obj.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
            return obj.bin_bodega.binbodega.kilos_fruta
        else:
            return obj.bin_bodega.binbodega.kilos_fruta
    
    
    def get_codigo_tarja(self, obj):
        if obj.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
            return obj.bin_bodega.binbodega.produccion.codigo_tarja
        elif obj.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            return obj.bin_bodega.binbodega.reproceso.codigo_tarja
        elif obj.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
            return obj.bin_bodega.binbodega.seleccion.codigo_tarja
        elif obj.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodegas', 'binsubproductoseleccion']: 
            return obj.bin_bodega.binbodega.codigo_tarja
        elif obj.bin_bodega.tipo_binbodega.model == 'bodegag6':
            return obj.bin_bodega.binbodega.programa.codigo_tarja
        elif obj.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
            if obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                return obj.bin_bodega.binbodega.tarja.produccion.codigo_tarja
            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                return obj.bin_bodega.binbodega.tarja.reproceso.codigo_tarja
            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4','bodegag5']:
                return obj.bin_bodega.binbodega.tarja.seleccion.codigo_tarja
            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodegas', 'binsubproductoseleccion']:
                return obj.bin_bodega.binbodega.tarja.codigo_tarja
            elif obj.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
                if obj.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                    return obj.bin_bodega.binbodega.tarja.tarja.produccion.codigo_tarja
                elif obj.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                    return obj.bin_bodega.binbodega.tarja.tarja.reproceso.codigo_tarja
                elif obj.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4, bodegag5']:
                    return obj.bin_bodega.binbodega.tarja.tarja.seleccion.codigo_tarja
                elif obj.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodegas', 'binsubproductoseleccion']:
                    return obj.bin_bodega.binbodega.codigo_tarja
    
 
                
    def get_cc_tarja(self, obj):
        if obj.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
            cc_tarja = CCTarjaResultante.objects.filter(tarja = obj.bin_bodega.binbodega.produccion).first()
            return f'{cc_tarja.get_variedad_display()} - {cc_tarja.get_calibre_display()}'

        elif obj.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            cc_tarja_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja = obj.bin_bodega.binbodega.reproceso).first()
            return f'{cc_tarja_reproceso.get_variedad_display()} - {cc_tarja_reproceso.get_calibre_display()}'

        elif obj.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
            cc_tarja_seleccion = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = obj.bin_bodega.binbodega.seleccion).first()
            return f'{cc_tarja_seleccion.get_variedad_display()} - {cc_tarja_seleccion.get_calidad_fruta_display()}'
        
        elif obj.bin_bodega.tipo_binbodega.model == 'bodegag6':
            cc_bin_resultante = CCBinResultanteProgramaPH.objects.filter(bin_resultante = obj.bin_bodega.binbodega.programa).first()
            return f'Sin Variedad / Sin Calidad'
        
        elif obj.bin_bodega.tipo_binbodega.model == 'binsubproductoseleccion':
            return f'{obj.bin_bodega.binbodega.get_variedad_display()} - {obj.bin_bodega.binbodega.get_calidad_display()}'
        
        elif obj.bin_bodega.tipo_binbodega.model == 'agrupaciondebinsbodegas':
            mayor_valor = 0
            bin_con_mas_kilos = None
            for x in obj.bin_bodega.binbodega.binsparaagrupacion_set.all():
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

        elif obj.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
            if obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                cc_tarja = CCTarjaResultante.objects.filter(tarja = obj.bin_bodega.binbodega.tarja.produccion).first()
                return f'{cc_tarja.get_variedad_display()} - {cc_tarja.get_calibre_display()}'

            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                cc_tarja_reproceso = CCTarjaResultanteReproceso.objects.filter(tarja = obj.bin_bodega.binbodega.tarja.reproceso).first()
                return f'{cc_tarja_reproceso.get_variedad_display()} - {cc_tarja_reproceso.get_calibre_display()}'

            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
                cc_tarja_seleccionada = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = obj.bin_bodega.binbodega.tarja.seleccion).first()
                return f'{cc_tarja_seleccionada.get_variedad_display()} - {cc_tarja_seleccionada.get_calidad_fruta_display()}'
            
            elif obj.bin_bodega.binbodega.tipo_tarja.model == 'bodegag6':
                cc_bin_resultante = CCBinResultanteProgramaPH.objects.filter(bin_resultante = obj.bin_bodega.binbodega.tarja.programa).first()
                return f'{cc_bin_resultante.get_variedad_display()} - {cc_bin_resultante.get_calidad_fruta_display()}'
            
            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodegas', 'binsubproductoseleccion']:
                mayor_valor = 0
                bin_con_mas_kilos = None
                for x in obj.bin_bodega.binbodega.binsparaagrupacion_set.all():
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
                
    def get_programa(self, obj):
        if obj.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
            return f'Programa Producción N° {obj.bin_bodega.binbodega.produccion.pk }'
        elif obj.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
            return f'Programa Reproceso N° {obj.bin_bodega.binbodega.reproceso.pk }'
        elif obj.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
            return f'Programa Selección N°{obj.bin_bodega.binbodega.seleccion.pk }'
        elif obj.bin_bodega.tipo_binbodega.model == 'agrupaciondebinsbodegas':
            return f'Agrupación N° {obj.bin_bodega.binbodega.pk}'
        
        elif obj.bin_bodega.tipo_binbodega.model == 'bodegag6':
            return f'Planta Harina N° {obj.bin_bodega.binbodega.pk}'
        
        elif obj.bin_bodega.tipo_binbodega.model == 'binsubproductoseleccion':
            return f'Bin SubProducto N° {obj.bin_bodega.binbodega.pk}'
        elif obj.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
            if obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                return f'Programa Producción N° {obj.bin_bodega.binbodega.tarja.produccion.pk}'
            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                return f'Programa Reproceso N° {obj.bin_bodega.binbodega.tarja.reproceso.pk}'
            elif obj.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
                return f'Programa Selección N° {obj.bin_bodega.binbodega.tarja.seleccion.pk}'
            
    class Meta:
        model = BinsParaProceso
        fields = '__all__'

class BinResultanteProcesoSerializer(serializers.ModelSerializer):
    tipo_patineta_label = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    cc_tarja = serializers.SerializerMethodField()
    
    ## No hay Control de calidad aun porfavor, esperar para mañana
    def get_cc_tarja(self, obj):
        cc_tarja = CCBinResultanteProcesoPH.objects.filter(bin_resultante = obj, estado_control = '1').first()
        if cc_tarja:
            return True
        else:
            return False
    
    def get_calidad(self, obj):
        return BodegaG7.objects.filter(proceso = obj).first().get_calidad_display()
    
    def get_tipo_patineta_label(self, obj):
        return obj.get_tipo_patineta_display()
    class Meta:
        model = BinResultanteProceso
        fields = '__all__'

class OperariosEnProcesoPHSerializer(serializers.ModelSerializer):
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
    
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
    
    class Meta:
        model = OperariosEnProcesoPH
        fields = '__all__'

class RechazoProcesoPHSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.SerializerMethodField()
    tipo_rechazo_label = serializers.SerializerMethodField()
    
    def get_tipo_rechazo_label(self, obj):
        return obj.get_tipo_rechazo_display()
    
    def get_registrado_por_nombre(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    
    class Meta:
        model = RechazoProcesoPH
        fields = '__all__'

class VariablesProcesoPHSerializer(serializers.ModelSerializer):
    resultado_luz = serializers.SerializerMethodField()
    resultado_gas = serializers.SerializerMethodField()
    
    def get_resultado_luz(self, obj):
        if obj.lectura_luz_inicio and obj.lectura_luz_termino:
            return round(obj.lectura_luz_termino - obj.lectura_luz_inicio, 2)
        else:
            return 0
        
    def get_resultado_gas(self, obj):
        if obj.lectura_gas_inicio and obj.lectura_gas_termino:
            return round(obj.lectura_gas_inicio - obj.lectura_gas_termino, 2)
        else:
            return 0
        
    class Meta:
        model = VariablesProcesoPH
        fields = '__all__'
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
class PDFProgramasPHSerializer(serializers.Serializer):
    bin = serializers.CharField()
    programa = serializers.CharField()
    kilos = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    
class PDFDocumentoEntradaProgramaPHSerializer(serializers.Serializer):
    bin = serializers.CharField()
    programa = serializers.CharField()
    cc_tarja = serializers.CharField()
    kilos = serializers.CharField()
    procesado = serializers.BooleanField()
    
class PDFDocumentoSalidaProgramaPHSerializer(serializers.Serializer):
    bin = serializers.CharField()
    estado = serializers.CharField()
    humedad = serializers.CharField()
    piel_aderida = serializers.CharField()
    calidad = serializers.CharField()
    kilos = serializers.CharField()
    
    

class DiaDeOperarioProgramaPHSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioProgramaPH
        fields = ['id','dia', 'kilos_dia', 'ausente']


class OperariosEnProgramaPHSerializer(serializers.ModelSerializer):
    dias = DiaDeOperarioProgramaPHSerializer(many=True, read_only=True)

    class Meta:
        model = OperariosEnProgramaPH
        fields = '__all__'
        
class DiaDeOperarioProgramaPHUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioProgramaPH
        fields = ['ausente']
            
class OperariosEnProgramaPHSerializer(serializers.ModelSerializer):
    operarios = OperariosEnProgramaPHSerializer(source='operariosenprogramaph_set', many=True, read_only=True)
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
    
    
    class Meta:
        model = OperariosEnProgramaPH
        fields = '__all__'
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
        
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'


class DiaDeOperarioProcesoPHSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioProcesoPH
        fields = ['id','dia', 'kilos_dia', 'ausente']


class OperariosEnProcesoPHSerializer(serializers.ModelSerializer):
    dias = DiaDeOperarioProcesoPHSerializer(many=True, read_only=True)

    class Meta:
        model = OperariosEnProcesoPH
        fields = '__all__'
        
class DiaDeOperarioProcesoPHUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioProcesoPH
        fields = ['ausente']
            
class OperariosEnProcesoPHSerializer(serializers.ModelSerializer):
    operarios = OperariosEnProcesoPHSerializer(source='operariosenprocesopph_set', many=True, read_only=True)
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
    
    
    class Meta:
        model = OperariosEnProcesoPH
        fields = '__all__'
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
        
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'