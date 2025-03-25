from rest_framework import serializers

from controlcalidad.models import CCTarjaSeleccionada
from cuentas.models import User
from .models import *
from .funciones import * 


class OperariosEnSeleccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperariosEnSeleccion
        fields = '__all__'
        
class BinsPepaCalibradaSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    
    def get_variedad(self, obj):
        return obj.binbodega.variedad
            
    def get_codigo_tarja(self, obj):
        return obj.binbodega.codigo_tarja_bin
        
    def get_kilos_fruta(self, obj):
        return obj.binbodega.kilos_bin
          
    class Meta:
        model = BinsPepaCalibrada
        fields = '__all__'   

class DetalleBinsPepaCalibradaSerializer(serializers.ModelSerializer):
    tipo_pepa_calibrada_label = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    
    def get_variedad(self, obj):
        return obj.binbodega.variedad
    
    def get_codigo_tarja(self, obj):
        return obj.binbodega.codigo_tarja_bin
        
    def get_kilos_fruta(self, obj):
        return obj.binbodega.kilos_bin
    
    def get_tipo_pepa_calibrada_label(self, obj):
        return obj.binbodega.tipo_binbodega.model
    
    class Meta:
        model = BinsPepaCalibrada
        fields = '__all__'

class DetalleBinsPorSelecionPorProgramaSerializer(serializers.ModelSerializer):
    tipo_pepa_calibrada_label = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    seleccion = serializers.SerializerMethodField()
    produccion = serializers.SerializerMethodField()
    
    def get_variedad(self, obj):
        return obj.binbodega.variedad
    
    def get_codigo_tarja(self, obj):
        return obj.binbodega.codigo_tarja_bin
        
    def get_kilos_fruta(self, obj):
        return obj.binbodega.kilos_bin
    
    def get_tipo_pepa_calibrada_label(self, obj):
        return obj.binbodega.tipo_binbodega.model
    
    def get_seleccion(self, obj):
        return obj.seleccion

    def get_produccion(self, obj):
        return obj.seleccion.produccion
    
    class Meta:
        model = BinsPepaCalibrada
        fields = '__all__'
        
class SeleccionSerializer(serializers.ModelSerializer):
    estado_programa_label = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()
    email_registrador = serializers.SerializerMethodField()
    #diferencia_rendimiento = serializers.SerializerMethodField()
    totales_kilos = serializers.SerializerMethodField()
    kilos_porcentaje = serializers.SerializerMethodField()
    condicion_cierre = serializers.SerializerMethodField()
    condicion_termino = serializers.SerializerMethodField()
    pepa_para_seleccion_length = serializers.SerializerMethodField()
    comercializador = serializers.SerializerMethodField()
    
    def get_pepa_para_seleccion_length(self, obj):
        return BinsPepaCalibrada.objects.all().count()
    
    def get_totales_kilos(self, obj):
        bins_sin_calibrar = BinsPepaCalibrada.objects.filter(seleccion = obj, bin_procesado = False)
        bins_calibrados = BinsPepaCalibrada.objects.filter(seleccion = obj, bin_procesado = True)
        return {
            "bins_sin_procesar": sum(bin.binbodega.kilos_bin for bin in bins_sin_calibrar) if bins_calibrados else 1,
            "bins_procesados": sum(bin.binbodega.kilos_bin for bin in bins_calibrados)
        }
              
    def get_kilos_porcentaje(self, obj):
        bins_sin_calibrados = BinsPepaCalibrada.objects.filter(seleccion = obj, bin_procesado = False)
        bins_calibrados = BinsPepaCalibrada.objects.filter(seleccion = obj, bin_procesado=True)
        total_kilos = sum(bin.binbodega.kilos_bin for bin in BinsPepaCalibrada.objects.filter(seleccion = obj).all()) 
        kilos_totales_sin_procesar = sum(bin.binbodega.kilos_bin for bin in bins_sin_calibrados)
        kilos_totales_procesados = sum(bin.binbodega.kilos_bin for bin in bins_calibrados)
        return {
            "bins_sin_procesar": round((kilos_totales_sin_procesar / (total_kilos or 1)) * 100, 2),
            "bins_procesados": round((kilos_totales_procesados / (total_kilos or 1)) * 100, 2),
        }
    
    def get_comercializador(self, obj):
        produccion = obj.seleccion.produccion
        lote_en_produccion = LotesPrograma.objects.filter(produccion=produccion).first()
        if lote_en_produccion:
            envase = EnvasesPatioTechadoExt.objects.get(pk=lote_en_produccion.bodega_techado_ext.pk)
            if envase.guia_patio.tipo_recepcion.model == 'recepcionmp':
                comercializador = envase.guia_patio.lote_recepcionado.guiarecepcion.comercializador.nombre
                return comercializador
        else:
            return "No definido"
    

    def get_kilos_totales_ingresados_porcentual(self, obj):
        bins_calibrados = obj.pepa_para_seleccion.all()
        total_kilos = self.get_totales_kilos_en_programa(obj)
        if not bins_calibrados:
            return 0
        kilos_totales_ingresados = sum(bin.kilos_fruta for bin in bins_calibrados)
        return round((kilos_totales_ingresados / total_kilos) * 100, 2)

    
    def get_condicion_termino(self, obj):
        tarjas = obj.tarjaseleccionada_set.filter(esta_eliminado=False)
        cc_tarja_seleccionada = CCTarjaSeleccionada.objects.filter(tarja_seleccionada__in=tarjas)
        
        all_tarjas_cc = all(cc.estado_cc == '3' for cc in cc_tarja_seleccionada)
        
        if cc_tarja_seleccionada.count() > 0 and all_tarjas_cc and obj.fecha_inicio_proceso:
            return True
        return False
    
    def get_condicion_cierre(self, obj):
        # Pre-fetch related data to minimize database hits.
        tarjas = obj.tarjaseleccionada_set.filter(esta_eliminado=False)
        cc_tarja_seleccionada = CCTarjaSeleccionada.objects.filter(tarja_seleccionada__in=tarjas)
        operarios = obj.operariosenseleccion_set.all()
        lotes = obj.pepa_calibrada.all()
        
        # Check all lots have bin_procesado as True
        all_lotes_processed = all(lote.bin_procesado for lote in lotes)
        
        # Check all tarjas where esta_eliminado is False have estado_cc == '3'
        all_tarjas_cc = all(cc.estado_cc == '3' for cc in cc_tarja_seleccionada)
        
        # Condition check
        if (lotes.count() > 0 and all_lotes_processed) and \
        (operarios.count() > 0) and (tarjas.count() > 0 and all_tarjas_cc) and obj.fecha_termino_proceso:
            return True
        else:
            return False
        
        
    
    # def get_diferencia_rendimiento(self, obj):
    #     BinFrutaCalibradaRendimiento = consulta_bins_ingresados_a_seleccion(obj.pk)
    #     BinsFrutaResultanteRendimiento = consulta_bins_seleccionados(obj.pk)
    #     porcentaje_proyeccion_entrante = porcentaje(BinFrutaCalibradaRendimiento['fruta_resultante'], BinFrutaCalibradaRendimiento['pepa_sana_proyectada'])
    #     porcentaje_proyeccion_saliente = porcentaje(BinsFrutaResultanteRendimiento['fruta_resultante'], BinsFrutaResultanteRendimiento['pepa_sana_proyectada'])
    #     porcentaje_diferencia = round(porcentaje_proyeccion_saliente - porcentaje_proyeccion_entrante, 2)

    #     return porcentaje_diferencia
    
    
    def get_email_registrador(self, obj):
        return obj.registrado_por.email
    
    def get_registrado_por_label(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    def get_estado_programa_label(self, obj):
        return obj.get_estado_programa_display()
    

    
    class Meta:
        model = Seleccion
        fields = '__all__'


class TarjaSeleccionadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarjaSeleccionada
        fields = '__all__'
        
        
class DetalleTarjaSeleccionadaSerializer(serializers.ModelSerializer):
    calibre = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    
    class Meta:     
        model = TarjaSeleccionada
        fields = '__all__'
        
    def get_variedad(self, obj):
        calibracion = CCTarjaSeleccionada.objects.get(tarja_seleccionada=obj)
        return calibracion.get_variedad_display()
        
    def get_calidad(self, obj):
        try:
            calibracion = CCTarjaSeleccionada.objects.get(tarja_seleccionada=obj)
            if calibracion.tarja_seleccionada.tipo_resultante == '2':
                if calibracion.picada is not None:
                    if calibracion.picada < 25 and calibracion.variedad == 'NP':
                        nueva_calidad = '0'  # Código de 'Extra N°1'
                    elif calibracion.picada >= 25 or calibracion.variedad != 'NP':
                        nueva_calidad = '1'  # Código de 'Supreme'
                    else:
                        nueva_calidad = calibracion.calidad_fruta

                    if calibracion.calidad_fruta != nueva_calidad:
                        calibracion.calidad_fruta = nueva_calidad
                        calibracion.save(update_fields=['calidad_fruta'])

                    return calibracion.get_calidad_fruta_display()
            
            # Si no se cumplen las condiciones, retornar la calidad actual
            return calibracion.get_calidad_fruta_display()

        except CCTarjaSeleccionada.DoesNotExist:
            return "Sin calidad"
    
    def get_calibre(self, obj):
        calibracion = CCTarjaSeleccionada.objects.get(tarja_seleccionada=obj)
        return calibracion.get_calibre_display()

class SubProductoOperarioSerializer(serializers.ModelSerializer):
    operario_nombres = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()
    tipo_subproducto_label = serializers.SerializerMethodField()


    
    
    class Meta:
        model = SubProductoOperario
        fields = '__all__'
        
    def get_tipo_subproducto_label(self, obj):
        return obj.get_tipo_subproducto_display()
    
    def get_registrado_por_label(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    def get_operario_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido} '
        
class DetalleSubProductoOperarioSerializer(serializers.ModelSerializer):
    operario_nombres = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()
    tipo_subproducto_label = serializers.SerializerMethodField()
    metricas_bin_subproducto = serializers.SerializerMethodField()
    
    def get_metricas_bin_subproducto(self, obj):
        # Accede a todos los SubproductosEnBin vinculados a este SubProductoOperario
        kilos_por_operario = obj.subproductosenbin_set.values(
            'subproducto_operario__operario__id', 
            'subproducto_operario__operario__nombre'
        ).annotate(total_kilos=Sum('peso'))

        # Preparar una lista para devolver los resultados.
        resultados = []
        for operario in kilos_por_operario:
            resultados.append({
                "nombre": operario['subproducto_operario__operario__nombre'],
                "total_kilos": operario['total_kilos']
            })

        return resultados
    
    class Meta:
        model = SubProductoOperario
        fields = '__all__'
        
    def get_tipo_subproducto_label(self, obj):
        return obj.get_tipo_subproducto_display()
    
    def get_registrado_por_label(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    def get_operario_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido} '

class SubProductoEnBinSerializer(serializers.ModelSerializer):
    programa = serializers.SerializerMethodField()
    operario = serializers.SerializerMethodField()
    tipo_subproducto = serializers.SerializerMethodField()
    registrado_por = serializers.SerializerMethodField()
    fecha_creacion = serializers.SerializerMethodField()
    
    def get_fecha_creacion(self, obj):
        return obj.subproducto_operario.fecha_creacion
    
    def get_registrado_por(self, obj):
        return f'{obj.subproducto_operario.registrado_por.first_name} {obj.subproducto_operario.registrado_por.last_name}'
    
    def get_tipo_subproducto(self, obj):
        return obj.subproducto_operario.get_tipo_subproducto_display()
    
    def get_operario(self, obj):
        return f'{obj.subproducto_operario.operario.nombre} {obj.subproducto_operario.operario.apellido}'
    
    def get_programa(self, obj):
        return f'Programa {obj.subproducto_operario.seleccion}'
    
    
    
    class Meta:
        model = SubproductosEnBin
        fields = '__all__'

class BinSubProductoSeleccionSerializer(serializers.ModelSerializer):
    subproductos = SubProductoEnBinSerializer(many = True, read_only = True, source = 'subproductosenbin_set')
    tipo_patineta_label = serializers.SerializerMethodField()
    variedad_label = serializers.SerializerMethodField()
    calidad_label = serializers.SerializerMethodField()
    calibre_label = serializers.SerializerMethodField()
    ubicacion_label = serializers.SerializerMethodField()
    calle_bodega_label = serializers.SerializerMethodField()
    tipo_subproducto_label = serializers.SerializerMethodField()
    estado_bin_label = serializers.SerializerMethodField()
    peso = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()

    
    
    def get_registrado_por_label(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    def get_peso(self, obj):
        peso_total = 0
        for producto in obj.subproductosenbin_set.all():
            peso_total += producto.subproducto_operario.peso
        return peso_total
    
    def get_estado_bin_label(self, obj):
        return obj.get_estado_bin_display()
    
    def get_tipo_subproducto_label(self, obj):
        return obj.get_tipo_subproducto_display()
    
    def get_calle_bodega_label(self, obj):
        return obj.get_calle_bodega_display()
    
    def get_ubicacion_label(self, obj):
        return obj.get_ubicacion_display()
    
    def get_calibre_label(self, obj):
        return obj.get_calibre_display()
    
    def get_calidad_label(self, obj):
        return obj.get_calidad_display()
    
    def get_variedad_label(self, obj):
        return obj.get_variedad_display()

    def get_tipo_patineta_label(self, obj):
        return obj.get_tipo_patineta_display()
    
    class Meta:
        model = BinSubProductoSeleccion
        fields = '__all__'


class DetalleOperariosEnSeleccionSerializer(serializers.ModelSerializer):
    tipo_operario_label = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    
    class Meta:
        model = OperariosEnSeleccion
        fields = '__all__'
        
    def get_rut_operario(self, obj):
        return f'{obj.operario.rut}'
        
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
    
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()


# OPCIONAL
class OperariosAgregadosSeleccionSerializer(serializers.Serializer):
    operario__rut = serializers.CharField()
    operario__nombre = serializers.CharField()
    operario__apellido = serializers.CharField()
    skill_operario = serializers.CharField()
    total_kilos_producidos = serializers.FloatField()
    dias_trabajados = serializers.IntegerField()      
    
    
from simple_history.utils import update_change_reason

class BinSubProductoSeleccionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BinSubProductoSeleccion.historia.model
        fields = '__all__'
    
    

class PepaCalibradaRendimientoSerializer(serializers.Serializer):
    sincalibre = serializers.FloatField()
    precalibre = serializers.FloatField()
    calibre_18_20 = serializers.FloatField()
    calibre_20_22 = serializers.FloatField()
    calibre_23_25 = serializers.FloatField()
    calibre_25_27 = serializers.FloatField()
    calibre_27_30 = serializers.FloatField()
    calibre_30_32 = serializers.FloatField()
    calibre_32_34 = serializers.FloatField()
    calibre_34_36 = serializers.FloatField()
    calibre_36_40 = serializers.FloatField()
    calibre_40_mas = serializers.FloatField()
    
class PepaCalibradaRendimientoConSinCalibreSerializer(serializers.Serializer):
    sincalibre = serializers.FloatField()
    precalibre = serializers.FloatField()
    calibre_18_20 = serializers.FloatField()
    calibre_20_22 = serializers.FloatField()
    calibre_23_25 = serializers.FloatField()
    calibre_25_27 = serializers.FloatField()
    calibre_27_30 = serializers.FloatField()
    calibre_30_32 = serializers.FloatField()
    calibre_32_34 = serializers.FloatField()
    calibre_34_36 = serializers.FloatField()
    calibre_36_40 = serializers.FloatField()
    calibre_40_mas = serializers.FloatField()
    
class TarjaSeleccionadaRendimientoConSinCalibreSerializer(serializers.Serializer):
    sin_calibre = serializers.FloatField()
    precalibre = serializers.FloatField()
    calibre_18_20 = serializers.FloatField()
    calibre_20_22 = serializers.FloatField()
    calibre_23_25 = serializers.FloatField()
    calibre_25_27 = serializers.FloatField()
    calibre_27_30 = serializers.FloatField()
    calibre_30_32 = serializers.FloatField()
    calibre_32_34 = serializers.FloatField()
    calibre_34_36 = serializers.FloatField()
    calibre_36_40 = serializers.FloatField()
    calibre_40_mas = serializers.FloatField()  
    
    
class TarjaSeleccionadaRendimientoSerializer(serializers.Serializer):
    sincalibre = serializers.FloatField()
    precalibre = serializers.FloatField()
    calibre_18_20 = serializers.FloatField()
    calibre_20_22 = serializers.FloatField()
    calibre_23_25 = serializers.FloatField()
    calibre_25_27 = serializers.FloatField()
    calibre_27_30 = serializers.FloatField()
    calibre_30_32 = serializers.FloatField()
    calibre_32_34 = serializers.FloatField()
    calibre_34_36 = serializers.FloatField()
    calibre_36_40 = serializers.FloatField()
    calibre_40_mas = serializers.FloatField()  
    
class BinsFrutaCalibradaRendimientoSerializer(serializers.Serializer):
    fruta_resultante = serializers.FloatField()
    pepa_sana_proyectada = serializers.FloatField()
    
class BinsFrutaResultanteRendimientoSerializer(serializers.Serializer):
    fruta_resultante = serializers.FloatField()
    pepa_sana_proyectada = serializers.FloatField()





class PDFInformeSeleccionSerializer(serializers.Serializer):
    tarja = serializers.CharField()
    programa = serializers.CharField()
    producto = serializers.CharField()
    variedad = serializers.CharField()
    calibre = serializers.CharField()
    calidad = serializers.CharField()
    kilos = serializers.CharField()

class PDFInformeKilosXOperarioSerializer(serializers.Serializer):
    tarja = serializers.CharField()
    programa = serializers.CharField()
    tipo_resultante = serializers.CharField()
    fecha_registro = serializers.DateTimeField()
    kilos = serializers.FloatField()
    neto = serializers.IntegerField()
    
class PDFInformeOperarioResumidoSerializer(serializers.Serializer):
    operario = serializers.CharField()
    kilos = serializers.FloatField()
    neto = serializers.FloatField()
    detalle = serializers.CharField()
    
    
class PDFDetalleEntradaSeleccionSerializer(serializers.Serializer):
    numero_programa = serializers.CharField()
    codigo_tarja = serializers.CharField()
    variedad = serializers.CharField()
    calibre = serializers.CharField()
    trozo = serializers.FloatField()
    picada = serializers.FloatField()
    hongo = serializers.FloatField()
    insecto = serializers.FloatField()
    dobles = serializers.FloatField()
    p_goma = serializers.FloatField()
    basura = serializers.FloatField()
    mezcla = serializers.FloatField()
    color = serializers.FloatField()
    goma = serializers.FloatField()
    pepa = serializers.FloatField()
    kilos = serializers.FloatField()
    colectado = serializers.BooleanField()
    programa_produccion = serializers.CharField()
    
    
class PDFDetalleSalidaSeleccionSerializer(serializers.Serializer):
    codigo_tarja = serializers.CharField()
    variedad = serializers.CharField()
    calibre = serializers.CharField()
    trozo = serializers.FloatField()
    picada = serializers.FloatField()
    hongo = serializers.FloatField()
    insecto = serializers.FloatField()
    dobles = serializers.FloatField()
    p_goma = serializers.FloatField()
    basura = serializers.FloatField()
    mezcla = serializers.FloatField()
    color = serializers.FloatField()
    goma = serializers.FloatField()
    pepa = serializers.FloatField()
    kilos = serializers.FloatField()
    calidad = serializers.CharField()
    tipo = serializers.CharField()
    
    
class DiaDeOperarioSeleccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioSeleccion
        fields = ['id','dia', 'kilos_dia', 'ausente']
class DiaDeOperarioSeleccionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioSeleccion
        fields = ['ausente']