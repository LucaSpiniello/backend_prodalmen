from controlcalidad.models import *
from .models import *
from rest_framework import serializers
from recepcionmp.models import *
from bodegas.models import *
from django.db.models import Count



class CCTarjaResultanteProduccionSerializer(serializers.ModelSerializer):
    cc_registrado_por = serializers.StringRelatedField()
    class Meta:
        model = CCTarjaResultante
        fields = ['estado_cc', 'variedad', 'calibre', 'cantidad_muestra', 'trozo', 'picada', 'hongo', 
                  'daño_insecto', 'dobles', 'goma', 'basura', 'mezcla_variedad', 'canuto', 'pepa_sana', 
                  'fuera_color', 'punto_goma', 'vana_deshidratada', 'cc_registrado_por']

class TarjaResultanteProduccionSerializer(serializers.ModelSerializer):
    kilos_neto = serializers.SerializerMethodField()
    cc_info = CCTarjaResultanteProduccionSerializer(source='cctarjaresultante', read_only=True)
    
    class Meta:
        model = TarjaResultante
        fields = ['codigo_tarja', 'kilos_neto', 'cc_info']
        
    def get_kilos_neto(self, obj):
        return obj.peso - obj.tipo_patineta
    
class ProduccionDetailSerializer(serializers.ModelSerializer):
    kilos_resultantes_totales = serializers.SerializerMethodField()
    numeros_lote = serializers.SerializerMethodField()
    # productores_duenos_lotes = serializers.SerializerMethodField()
    tarjas_resultantes = TarjaResultanteProduccionSerializer(many=True, source='tarjaresultante_set')
    cantidad_bines_resultantes = serializers.SerializerMethodField()

    class Meta:
        model = Produccion
        fields = ['numero_programa', 'kilos_resultantes_totales', 'numeros_lote', 'tarjas_resultantes', 'cantidad_bines_resultantes']

    def get_kilos_resultantes_totales(self, obj):
        return sum(t.peso - t.tipo_patineta for t in obj.tarjaresultante_set.all())
    
    def get_cantidad_bines_resultantes(self, obj):
        return obj.tarjaresultante_set.count()
    
    def get_numero_lotes(self, obj):
        lotes = set()
        for lote in obj.lotesprograma_set.all():
            lotes.add(lote.bodega_techado_ext.guia_patio.lote_recepcionado.numero_lote)
        return list(lotes)
    
    # def get_productores_duenos_lotes(self, obj):
    #     productores = set()
    #     for lote in obj.lotesprograma_set.all():
    #         productores.add(lote.bodega_techado_ext.guia_patio.lote_recepcionado.guiarecepcion.productor)
    #     return list(productores)
    
    def get_numeros_lote(self, obj):
        numeros_lote = set()
        for lote in obj.lotesprograma_set.all():
            if lote.bodega_techado_ext.guia_patio.lote_recepcionado and hasattr(lote.bodega_techado_ext.guia_patio.lote_recepcionado, 'numero_lote'):
                numeros_lote.add(lote.bodega_techado_ext.guia_patio.lote_recepcionado.numero_lote)
        return list(numeros_lote)
    


class ProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produccion
        fields = '__all__'
        
class DetalleProduccionSerializer(serializers.ModelSerializer):
    fecha_inicio_proceso = serializers.SerializerMethodField()
    fecha_termino_proceso = serializers.SerializerMethodField()
    condicion_termino = serializers.SerializerMethodField()
    estado_label = serializers.SerializerMethodField()
    lotes_length = serializers.SerializerMethodField()
    lotes_por_procesar = serializers.SerializerMethodField()
    lotes_procesados = serializers.SerializerMethodField()
    condicion_cierre = serializers.SerializerMethodField()
    
    def get_fecha_inicio_proceso(self, obj):
        if obj.fecha_inicio_proceso:
            return obj.fecha_inicio_proceso
        else:
            return 'Aun no registrada'

    def get_fecha_termino_proceso(self, obj):
        return obj.fecha_termino_proceso if obj.fecha_termino_proceso else 'Aun no registrada'
    
    def get_lotes_por_procesar(self, obj):
        total = obj.lotesprograma_set.all().count()
        if total == 0:
            return "No hay envases para procesar"
        porcentaje_no_procesados = (obj.lotesprograma_set.filter(bin_procesado=False).count() / total) * 100
        return f'{round(porcentaje_no_procesados, 2)}% Envases por Procesar'

    def get_lotes_procesados(self, obj):
        total = obj.lotesprograma_set.all().count()
        if total == 0:
            return "No hay envases procesados"
        porcentaje_procesados = (obj.lotesprograma_set.filter(bin_procesado=True).count() / total) * 100
        return f'{round(porcentaje_procesados, 2)}% Envases Procesados'
    
    def get_lotes_length(self, obj):
        return obj.lotesprograma_set.all().count()
    
    def get_condicion_termino(self, obj):
        tarjas = obj.tarjaresultante_set.filter(esta_eliminado=False)
        #print(tarjas)
        cc_tarja_resultante = CCTarjaResultante.objects.filter(tarja__in=tarjas)
        #print(cc_tarja_resultante)
        all_tarjas_cc = all(cc.estado_cc == '3' for cc in cc_tarja_resultante)
        #print(all_tarjas_cc)
        
        if (cc_tarja_resultante.count() > 0 and all_tarjas_cc) and obj.estado == '2' or '3' or '0':
            #print("Valida cierre")
            return True
        #print("No valida cierre")
        return False
    
    
    def get_condicion_cierre(self, obj):
        # Pre-fetch related data to minimize database hits.
        
        tarjas = obj.tarjaresultante_set.filter(esta_eliminado=False)
        operarios = obj.operariosenproduccion_set.all()
        lotes = obj.lotesprograma_set.all()
        cc_tarja_resultante = CCTarjaResultante.objects.filter(tarja__in=tarjas)
        all_tarjas_cc = all(cc.estado_cc == '3' for cc in cc_tarja_resultante)
        
        # Check all lots have bin_procesado as True
        all_lotes_processed = all(lote.bin_procesado for lote in lotes)
        
        # Check all tarjas where esta_eliminado is False have estado_cc == '3'
        
        
        # Condition check
        if (lotes.count() > 0 and all_lotes_processed) and \
        (operarios.count() > 0) and (tarjas.count() > 0) and (cc_tarja_resultante.count() > 0 and all_tarjas_cc) and \
            (obj.estado == '4' and obj.fecha_termino_proceso):
            return True
        else:
            return False
            
    
    def get_estado_label(self, obj):
        return obj.get_estado_display()
    
    class Meta:
        model = Produccion
        exclude = ['lotes', 'operarios']

class LotesProgramaSerializer(serializers.ModelSerializer):
    numero_lote = serializers.SerializerMethodField()
    guia_patio = serializers.SerializerMethodField()
    numero_bin = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    guia_recepcion = serializers.SerializerMethodField()
    control_calidad = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    total_envases = serializers.SerializerMethodField()
    
    class Meta:
        model = LotesPrograma
        fields = '__all__'
        
    def get_total_envases(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.guia_patio.envasespatiotechadoext_set.all().count()
        else:
            return None
        
    def get_ubicacion(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.guia_patio.get_ubicacion_display()  
        else:
            return None
        
    def get_control_calidad(self, obj):
        try:
            if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
                recepcion = RecepcionMp.objects.filter(pk=obj.bodega_techado_ext.guia_patio.id_recepcion).first()
                if recepcion:
                    return recepcion.pk
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f'Ocurrió una excepción: {e}')
            return None
        
        
    def get_numero_lote(self, obj):
        try:
            if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
                recepcion = RecepcionMp.objects.filter(pk=obj.bodega_techado_ext.guia_patio.id_recepcion).first()
                if recepcion:
                    return recepcion.numero_lote
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f'Ocurrió una excepción: {e}')
            return None
    
    def get_guia_patio(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.guia_patio.id_recepcion    
        else:
            return None
        
    def get_numero_bin(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.numero_bin
        else:
            return None 
        
    def get_kilos_fruta (self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.kilos_fruta
        else:
            return None 
    def get_variedad(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.get(pk=obj.bodega_techado_ext.pk).get_variedad_display()
        if patio_techado_ext:
            return patio_techado_ext
        else:
            return None   
        
        
    def get_guia_recepcion(self, obj):
        try:
            if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
                recepcion = RecepcionMp.objects.filter(pk = obj.bodega_techado_ext.guia_patio.id_recepcion).first().guiarecepcion.pk
                if recepcion:
                    return recepcion
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f'Ocurrió una excepción: {e}')
            return None
        
class DetalleLotesProgramaSerializer(serializers.ModelSerializer):
    numero_lote = serializers.SerializerMethodField()
    guia_patio = serializers.SerializerMethodField()
    numero_bin = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    guia_recepcion = serializers.SerializerMethodField()
    control_calidad = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    total_envases = serializers.SerializerMethodField()
    
    
    
    
    class Meta:
        model = LotesPrograma
        fields = '__all__'
        
    def get_total_envases(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.guia_patio.envasespatiotechadoext_set.all().count()
        else:
            return None
        
    def get_ubicacion(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.guia_patio.get_ubicacion_display()  
        else:
            return None
        
    def get_control_calidad(self, obj):
        try:
            if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
                recepcion = RecepcionMp.objects.filter(pk=obj.bodega_techado_ext.guia_patio.id_recepcion).first()
                if recepcion:
                    return recepcion.pk
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f'Ocurrió una excepción: {e}')
            return None
        
        
    def get_numero_lote(self, obj):
        try:
            if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
                recepcion = RecepcionMp.objects.filter(pk=obj.bodega_techado_ext.guia_patio.id_recepcion).first()
                if recepcion:
                    return recepcion.numero_lote
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f'Ocurrió una excepción: {e}')
            return None
    
    def get_guia_patio(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.guia_patio.id_recepcion    
        else:
            return None
        
    def get_numero_bin(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.numero_bin
        else:
            return None 
        
    def get_kilos_fruta (self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.filter(pk=obj.bodega_techado_ext.pk).first()
        if patio_techado_ext:
            return patio_techado_ext.kilos_fruta
        else:
            return None 
    def get_variedad(self, obj):
        patio_techado_ext = EnvasesPatioTechadoExt.objects.get(pk=obj.bodega_techado_ext.pk).get_variedad_display()
        if patio_techado_ext:
            return patio_techado_ext
        else:
            return None   
        
    # def get_guia_recepcion(self, obj):
    #     if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
    #         recepcion = RecepcionMp.objects.filter(pk = obj.bodega_techado_ext.guia_patio.id_recepcion).first().guiarecepcion.pk    
    #         return recepcion
    #     else:
    #         return None
        
    def get_guia_recepcion(self, obj):
        try:
            if obj.bodega_techado_ext.guia_patio.tipo_recepcion.model == 'recepcionmp':
                recepcion = RecepcionMp.objects.filter(pk = obj.bodega_techado_ext.guia_patio.id_recepcion).first().guiarecepcion.pk
                if recepcion:
                    return recepcion
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f'Ocurrió una excepción: {e}')
            return None

class DiaDeOperarioProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioProduccion
        fields = ['id','dia', 'kilos_dia', 'ausente']


class OperariosEnProduccionSerializer(serializers.ModelSerializer):
    dias = DiaDeOperarioProduccionSerializer(many=True, read_only=True)

    class Meta:
        model = OperariosEnProduccion
        fields = '__all__'
        
class DiaDeOperarioProduccionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioProduccion
        fields = ['ausente']
            
class OperariosEnProduccionSerializer(serializers.ModelSerializer):
    operarios = OperariosEnProduccionSerializer(source='operariosenproduccion_set', many=True, read_only=True)
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
    
    
    class Meta:
        model = OperariosEnProduccion
        fields = '__all__'
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
        
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
            
class DetalleOperariosEnProduccionSerializer(serializers.ModelSerializer):
    tipo_operario_label = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()  
    
    class Meta:
        model = OperariosEnProduccion
        fields = '__all__'
        
    def get_rut_operario(self, obj):
        return f'{obj.operario.rut}'
        
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
    
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()


        
class TarjaResultanteSerializer(serializers.ModelSerializer):
    tipo_resultante_label = serializers.SerializerMethodField()

    
    class Meta:
        model = TarjaResultante
        fields = '__all__'
        
    def get_tipo_resultante_label(self, obj):
        return obj.get_tipo_resultante_display()
        
class DetalleTarjaResultanteSerializer(serializers.ModelSerializer):
    tipo_resultante_label = serializers.SerializerMethodField()
    tipo_patineta_label = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    
    porcentajes = serializers.SerializerMethodField()
    
    def get_porcentajes(self, obj):
        # Obtener todos los tipos de tarja resultante y sus cantidades
        resultados = TarjaResultante.objects.values('tipo_resultante').annotate(total=Count('id'))
        total_tarjas = TarjaResultante.objects.count()
        porcentajes = {}

        # Calcular los porcentajes para cada tipo de tarja resultante
        for resultado in resultados:
            tipo_label = dict(TIPO_RESULTANTE).get(resultado['tipo_resultante'], 'Desconocido')
            if total_tarjas > 0:
                porcentaje = (resultado['total'] / total_tarjas) * 100
            else:
                porcentaje = 0
            porcentajes[tipo_label] = round(porcentaje, 2)

        return porcentajes
    
    class Meta:
        model = TarjaResultante
        fields = '__all__'
        
    
    def get_variedad(self, obj):
        try:
            cc_resultante = CCTarjaResultante.objects.filter(pk = obj.pk).first()
            
            return cc_resultante.get_variedad_display()
        except:
            return 'Sin Variedad'
    
    def get_tipo_patineta_label(self, obj):
        return obj.get_tipo_patineta_display() 
    
    def get_tipo_resultante_label(self, obj):
        return obj.get_tipo_resultante_display()
    
class ReprocesoSerializer(serializers.ModelSerializer):
    estado_label = serializers.SerializerMethodField()
    class Meta:
        model = Reproceso
        fields = '__all__'
        
    def get_estado_label(self, obj):
        return obj.get_estado_display()
        
class DetalleReprocesoSerializer(serializers.ModelSerializer):
    estado_label = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()
    email_registrador = serializers.SerializerMethodField()
    condicion_cierre = serializers.SerializerMethodField()
    condicion_termino = serializers.SerializerMethodField()
    bines_length = serializers.SerializerMethodField()
    bines_por_procesar = serializers.SerializerMethodField()
    bines_procesados = serializers.SerializerMethodField()
    kilos_ingresados = serializers.SerializerMethodField()
    kilos_resultantes = serializers.SerializerMethodField()
    
    def get_kilos_ingresados(self, obj):
        total = 0
        if obj.binsenreproceso_set.all().count() >= 1:
            for bin in obj.binsenreproceso_set.all():
                total += bin.binbodega.kilos_bin
            return total
        else:
            return total
        
    def get_kilos_resultantes(self, obj):
        total = 0
        if obj.tarjaresultantereproceso_set.all().count() >= 1:
            for bin in obj.tarjaresultantereproceso_set.all():
                total += (bin.peso - bin.tipo_patineta)
            return total
        else:
            return total
    
    def get_bines_por_procesar(self, obj):
        total = obj.binsenreproceso_set.all().count()
        if total == 0:
            return "No hay envases para procesar"
        porcentaje_no_procesados = (obj.binsenreproceso_set.filter(bin_procesado=False).count() / total) * 100
        return f'{round(porcentaje_no_procesados, 2)}% Envases por Procesar'

    def get_bines_procesados(self, obj):
        total = obj.binsenreproceso_set.all().count()   
        if total == 0:
            return "No hay envases procesados"
        porcentaje_procesados = (obj.binsenreproceso_set.filter(bin_procesado=True).count() / total) * 100
        return f'{round(porcentaje_procesados, 2)}% Envases Procesados'
    
    def get_bines_length(self, obj):
        return obj.binsenreproceso_set.all().count()
      
    def get_condicion_cierre(self, obj):
        # Pre-fetch related data to minimize database hits.
        
        tarjas = obj.tarjaresultantereproceso_set.filter(esta_eliminado=False)
        operarios = obj.operariosenreproceso_set.all()
        lotes = obj.binsenreproceso_set.all()
        
        # Check all lots have bin_procesado as True
        all_lotes_processed = all(lote.bin_procesado for lote in lotes)
        
        # Condition check
        if (lotes.count() > 0 and all_lotes_processed) and \
        (operarios.count() > 0) and (tarjas.count() > 0) and \
            obj.fecha_termino_proceso:
            return True
        else:
            return False
    
    def get_condicion_termino(self, obj):
        tarjas = obj.tarjaresultantereproceso_set.filter(esta_eliminado=False)
        cc_tarja_resultante = CCTarjaResultanteReproceso.objects.filter(tarja__in=tarjas)
        
        all_tarjas_cc = all(cc.estado_cc == '3' for cc in cc_tarja_resultante)
        
        if (cc_tarja_resultante.count() > 0 and all_tarjas_cc) and obj.fecha_inicio_proceso:
            return True
        return False
    
    # def get_condicion_cierre(self, obj):
    #     # Pre-fetch related data to minimize database hits.
    #     tarjas = obj.tarjaresultantereproceso_set.filter(esta_eliminado=False)
    #     cc_tarja_resultante = CCTarjaResultanteReproceso.objects.filter(tarja__in=tarjas)
    #     operarios = obj.operariosenreproceso_set.all()
    #     lotes = obj.binsenreproceso_set.all()
        
    #     # Check all lots have bin_procesado as True
    #     all_lotes_processed = all(lote.bin_procesado for lote in lotes)
        
    #     # Check all tarjas where esta_eliminado is False have estado_cc == '3'
    #     all_tarjas_cc = all(cc.estado_cc == '3' for cc in cc_tarja_resultante)
        
    #     # Condition check
    #     if (lotes.count() > 0 and all_lotes_processed) and \
    #     (operarios.count() > 0) and (tarjas.count() > 0):
    #         return True
    #     else:
    #         return False
        
    def get_registrado_por_label(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    def get_email_registrador(self, obj):
        return f'{obj.registrado_por.email}'
    
    def get_estado_label(self, obj):
        return obj.get_estado_display()

    class Meta:
        model = Reproceso
        exclude = ['operarios']
        
# class OperariosEnReprocesoSerializer(serializers.ModelSerializer):
#     nombres = serializers.SerializerMethodField()
#     rut_operario = serializers.SerializerMethodField()
#     tipo_operario_label = serializers.SerializerMethodField()
    
    
#     class Meta:
#         model = OperariosEnReproceso
#         fields = '__all__'
        
#     def get_tipo_operario_label(self, obj):
#         return obj.get_skill_operario_display()
    
#     def get_rut_operario(self, obj):
#         return obj.operario.rut
    
#     def get_nombres(self, obj):
#         return f'{obj.operario.nombre} {obj.operario.apellido}'
        
# class DetalleOperariosEnReprocesoSerializer(serializers.ModelSerializer):
#     nombres = serializers.SerializerMethodField()
#     rut_operario = serializers.SerializerMethodField()
#     tipo_operario_label = serializers.SerializerMethodField()
    
#     class Meta:
#         model = OperariosEnReproceso
#         fields = '__all__'
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
    
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
    


class DiaDeOperarioReprocesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioReproceso
        fields = ['id', 'dia', 'kilos_dia', 'ausente']

class DiaDeOperarioReprocesoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioReproceso
        fields = ['ausente']

class OperariosEnReprocesoSerializer(serializers.ModelSerializer):
    dias = DiaDeOperarioReprocesoSerializer(many=True, read_only=True)

    class Meta:
        model = OperariosEnProduccion
        fields = '__all__'
        
        
class OperariosEnReprocesoSerializer(serializers.ModelSerializer):
    operarios = OperariosEnReprocesoSerializer(source='operariosenproduccion_set', many=True, read_only=True) # type: ignore
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
    
    
    class Meta:
        model = OperariosEnReproceso
        fields = '__all__'
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
        
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'


class BinsEnReprocesoSerializer(serializers.ModelSerializer):
    programa_produccion = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField()
    calle_bodega = serializers.SerializerMethodField()

    
    def get_calle_bodega(self, obj):
        return obj.binbodega.binbodega.calle_bodega

    def get_codigo_tarja(self, obj):
        return obj.binbodega.codigo_tarja_bin
    
    class Meta:
        model = BinsEnReproceso
        fields = '__all__'
    
    def get_programa_produccion(self, obj):
        return obj.binbodega.origen_tarja
         
class DetalleBinsEnReprocesoSerializer(serializers.ModelSerializer):
    programa_produccion = serializers.SerializerMethodField()
    kilos_bin = serializers.SerializerMethodField()
    identificador_bin_bodega = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField()
    calle_bodega = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()
    
    
    def get_variedad(self, obj):
        return obj.binbodega.variedad
    
    
    def get_calibre(self, obj):
        return obj.binbodega.calibre
    
    
    
    def get_calle_bodega(self, obj):
        return obj.binbodega.binbodega.calle_bodega

    def get_codigo_tarja(self, obj):
        return obj.binbodega.codigo_tarja_bin

    def get_identificador_bin_bodega(self, obj):
        return obj.binbodega.id_binbodega
        
    def get_kilos_bin(self, obj):
        return obj.binbodega.kilos_bin
        
    def get_programa_produccion(self, obj):
        return obj.binbodega.origen_tarja
    
    class Meta:
        model = BinsEnReproceso
        fields = '__all__'
        
     
       
class TarjaResultanteReprocesoSerializer(serializers.ModelSerializer):
    tipo_patineta_label = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()

    def get_calibre(self, obj):
        if obj.tipo_resultante in ['1', '2', '4']:
            calibre = BodegaG1Reproceso.objects.filter(reproceso = obj.pk).first().calibre
        elif obj.tipo_resultante == '3':
            calibre = BodegaG2Reproceso.objects.filter(reproceso = obj.pk).first().calibre
        return calibre

    

    def get_variedad(self, obj):
        if obj.tipo_resultante in ['1', '2', '4']:
            bin_en_bodega = BodegaG1Reproceso.objects.filter(reproceso = obj.pk).first().get_variedad_display()
        elif obj.tipo_resultante == '3':
            bin_en_bodega = BodegaG2Reproceso.objects.filter(reproceso = obj.pk).first().get_variedad_display()

        return bin_en_bodega

    def get_tipo_patineta_label(self, obj):
        return obj.get_tipo_patineta_display()
    
    
    class Meta: 
        model = TarjaResultanteReproceso
        fields = '__all__'
        
class DetalleTarjaResultanteReprocesoSerializer(serializers.ModelSerializer):
    tipo_patineta_label = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()

    def get_calibre(self, obj):
        if obj.tipo_resultante in ['1', '2', '4']:
            calibre = BodegaG1Reproceso.objects.filter(reproceso = obj.pk).first().get_calibre_display()
        elif obj.tipo_resultante == '3':
            calibre = BodegaG2Reproceso.objects.filter(reproceso = obj.pk).first().get_calibre_display()
        return calibre

    

    def get_variedad(self, obj):
        if obj.tipo_resultante in ['1', '2', '4']:
            bin_en_bodega = BodegaG1Reproceso.objects.filter(reproceso = obj.pk).first().variedad
        elif obj.tipo_resultante == '3':
            bin_en_bodega = BodegaG2Reproceso.objects.filter(reproceso = obj.pk).first().variedad

        return bin_en_bodega

    
    def get_tipo_patineta_label(self, obj):
        return obj.get_tipo_patineta_display()
    
    
    class Meta:
        model = TarjaResultanteReproceso
        fields = '__all__'
        

# Opcionales

class OperariosAgregadosSerializer(serializers.Serializer):
    operario__rut = serializers.CharField()
    operario__nombre = serializers.CharField()
    operario__apellido = serializers.CharField()
    skill_operario = serializers.CharField()
    total_kilos_producidos = serializers.FloatField()
    dias_trabajados = serializers.IntegerField()      
    
class PDFInformeOperarioXKilos(serializers.Serializer):
    numero_program = serializers.CharField()
    fecha_registro = serializers.DateTimeField()
    kilos = serializers.IntegerField()
    neto = serializers.IntegerField()
    
class PDFDetalleEnvasesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    numero_lote = serializers.IntegerField()
    tipo_envase = serializers.CharField()
    numero_envase = serializers.CharField()
    ubicacion = serializers.CharField()
    colectado = serializers.BooleanField()
    
class DashboardHomeSerializer(serializers.Serializer):
    tipo_programa = serializers.CharField()
    total_kilos_introducidos = serializers.FloatField()
    total_kilos_resultantes = serializers.FloatField()
      
class PDFEntradaReprocesoSerializer(serializers.Serializer):
    codigo_tarja = serializers.CharField()
    programa = serializers.CharField()
    kilos_fruta = serializers.FloatField()
    variedad = serializers.CharField()
    calibre = serializers.CharField()
    procesado = serializers.BooleanField()

class PDFSalidaReprocesoSerializer(serializers.Serializer):
    codigo_tarja = serializers.CharField()
    kilos_fruta = serializers.FloatField()
    variedad = serializers.CharField()
    calibre = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()