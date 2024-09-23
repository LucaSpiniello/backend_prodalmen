from rest_framework import serializers
from .models import *
from recepcionmp.models import *

        
class CCTarjaResultanteSerializer(serializers.ModelSerializer):
    estado_cc_label = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField(read_only=True)
    variedad = serializers.SerializerMethodField()
    tipo_resultante_label = serializers.SerializerMethodField()
    
    class Meta:
        model = CCTarjaResultante
        fields = '__all__'
        
    def get_variedad(self, obj):
        return obj.get_variedad_display()
    
    def get_estado_cc_label(self, obj):
        return obj.get_estado_cc_display()
    
    def get_codigo_tarja(self, obj):
        return obj.tarja.codigo_tarja
    
    def get_tipo_resultante_label(self, obj):
        return obj.tarja.get_tipo_resultante_display()

class CCTarjaResultanteReprocesoSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField(read_only=True)
    estado_cc_label = serializers.SerializerMethodField()
    tipo_resultante_label = serializers.SerializerMethodField()
    
    class Meta:
        model = CCTarjaResultanteReproceso
        fields = '__all__'
        
    def get_estado_cc_label(self, obj):
        return obj.get_estado_cc_display()
    
    def get_codigo_tarja(self, obj):
        return obj.tarja.codigo_tarja
        
    def get_tipo_resultante_label(self, obj):
        return obj.tarja.get_tipo_resultante_display()
        
class CCRecepcionMateriaPrimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCRecepcionMateriaPrima
        fields = '__all__'
        
class FotosCCRecepcionMateriaPrimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotosCC
        fields = '__all__'

class CCPepaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCPepa
        fields = '__all__'
        
class CCRendimientoSerializer(serializers.ModelSerializer):
    cc_rendimiento = CCPepaSerializer(read_only=True, source='cdcpepa')
    cc_recepcionmp = serializers.PrimaryKeyRelatedField(read_only=True)
    cc_ok = serializers.SerializerMethodField()
    cc_calibrespepaok = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()
    email_registrador = serializers.SerializerMethodField()
    
    def get_registrado_por_label(self, obj):
        if obj.registrado_por:
            return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
        else:
            return 'No se identifica el registrador'
            
    
    def get_email_registrador(self, obj):
        if obj.registrado_por:
            return obj.registrado_por.email
        else:
            return 'No se identifica el registrador'
    
    
    
    class Meta:
        model = CCRendimiento
        fields = '__all__'
        extra_kwargs = {    
            "cc_recepcionmp": {"required": False, "allow_null": False},
        }
    
    def get_cc_ok(self, obj):
        try:
            return CCPepa.objects.get(cc_rendimiento = obj.pk, cc_pepaok = True).cc_pepaok
        except: 
            return 'Sin Control Pepa Registrado'
        
    def get_cc_calibrespepaok(self, obj):
        try:
            return CCPepa.objects.get(cc_rendimiento = obj.pk, cc_calibrespepaok = True).cc_pepaok
        except: 
            return False
        


class DetalleCCRecepcionMateriaPrimaSerializer(serializers.ModelSerializer):
    control_rendimiento =CCRendimientoSerializer(read_only=True, many=True, source='ccrendimiento_set')
    estado_aprobacion_cc_label = serializers.SerializerMethodField()
    estado_cc_label = serializers.SerializerMethodField()
    numero_lote = serializers.SerializerMethodField()
    presencia_insectos_selected = serializers.SerializerMethodField()
    productor = serializers.SerializerMethodField()
    guia_recepcion = serializers.SerializerMethodField()
    estado_guia = serializers.SerializerMethodField()
    fotos_cc = FotosCCRecepcionMateriaPrimaSerializer(many=True, read_only=True, source='fotoscc_set')
    kilos_totales_recepcion = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    registrado_por_label = serializers.SerializerMethodField()
    email_registrador = serializers.SerializerMethodField()
    
    comercializador = serializers.SerializerMethodField()
    def get_registrado_por_label(self, obj):
       if obj.cc_registrado_por:
            return f'{obj.cc_registrado_por.first_name} {obj.cc_registrado_por.last_name}'
       else:
           return 'Sin Registrar CC'
    
    def get_email_registrador(self, obj):
        if obj.cc_registrado_por:
            return obj.cc_registrado_por.email
        else:
            return 'Sin Registrar CC'
    
    def get_comercializador(self, obj):
        try:
            return obj.recepcionmp.guiarecepcion.comercializador.nombre
        except:
            return 'Sin Comercializador'
    
    def get_variedad(self, obj):
        variedad = None
        for envase in obj.recepcionmp.envasesguiarecepcionmp_set.all():
            variedad = envase.get_variedad_display()
        return variedad
            
    
    def get_kilos_totales_recepcion(self, obj):
        kilos_brutos = obj.recepcionmp.kilos_brutos_1 + obj.recepcionmp.kilos_brutos_2
        kilos_tara = obj.recepcionmp.kilos_tara_1 + obj.recepcionmp.kilos_tara_2
        kilos_envase = 0
        cantidad_envases = 0
        for envase in obj.recepcionmp.envasesguiarecepcionmp_set.all():
            if envase != 'Granel' and envase.envase.peso > 0:
                kilos_envase += envase.envase.peso
                cantidad_envases += envase.cantidad_envases
        #print(kilos_envase)
        #print(cantidad_envases)
        
        
        total_kilos_envases = kilos_envase * cantidad_envases
        total = (kilos_brutos - total_kilos_envases) - kilos_tara
        
        return total
    
    def get_presencia_insectos_selected(self, obj):
        if obj.presencia_insectos:
            return  "Si"
        else:
            return "No"
    
    def get_estado_cc_label(self, obj):
        return obj.get_estado_cc_display()
    
    # def get_productor(self, obj):
    #     lote = RecepcionMp.objects.get(pk = obj.recepcionmp.pk).guiarecepcion
    #     productor = GuiaRecepcionMP.objects.get(pk = lote.pk).productor.pk
    #     return productor
    
    def get_productor(self, obj):
        return obj.recepcionmp.guiarecepcion.productor.nombre
    
    def get_guia_recepcion(self, obj):
        return obj.recepcionmp.guiarecepcion.pk
        
    def get_estado_guia(self, obj):
        return obj.recepcionmp.guiarecepcion.estado_recepcion
        
    
    def get_estado_aprobacion_cc_label(self, obj):
        return obj.get_estado_aprobacion_cc_display()
    
    def get_numero_lote(self, obj):
        try:
            numero_lote_aprobado = RecepcionMp.objects.filter(id=obj.recepcionmp.id).first().numero_lote
            if numero_lote_aprobado:
                return numero_lote_aprobado
            else:
                return LoteRecepcionMpRechazadoPorCC.objects.filter(recepcionmp=obj.recepcionmp).first().numero_lote_rechazado
        except RecepcionMp.DoesNotExist:
            pass
        
    class Meta:
        model = CCRecepcionMateriaPrima
        fields = '__all__'
        

class MuestraSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    basura = serializers.FloatField()
    pelon = serializers.FloatField()
    ciega = serializers.FloatField()
    cascara = serializers.FloatField()
    pepa_huerto = serializers.FloatField()
    pepa_bruta = serializers.FloatField()
    
    
class CCPepaMuestraSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    mezcla = serializers.FloatField()
    insecto = serializers.FloatField()
    hongo = serializers.FloatField()
    dobles = serializers.FloatField()
    color = serializers.FloatField()
    vana = serializers.FloatField()
    pgoma = serializers.FloatField()
    goma = serializers.FloatField()
    
class CalibresSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
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
    
    

class DescuentosSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    pepa_exp = serializers.FloatField()
    cat2 = serializers.FloatField()
    desechos = serializers.FloatField()
    mezcla = serializers.FloatField()
    color = serializers.FloatField()
    dobles = serializers.FloatField()
    insecto = serializers.FloatField()
    hongo = serializers.FloatField()
    vana = serializers.FloatField()
    pgoma = serializers.FloatField()
    goma = serializers.FloatField()
    
class AportePexSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    exportable = serializers.FloatField()
    cat2 = serializers.FloatField()
    des = serializers.FloatField()
    

class PorcentajeLiquidarSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    exportable = serializers.FloatField()
    cat2 = serializers.FloatField()
    des = serializers.FloatField()
        
class KilosMermaSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    exportable = serializers.FloatField()
    cat2 = serializers.FloatField()
    des = serializers.FloatField()
    
class MermaPorcentajeSerializer(serializers.Serializer):
    cc_lote = serializers.IntegerField()
    exportable = serializers.FloatField()
    cat2 = serializers.FloatField()
    des = serializers.FloatField()
    
class CalculoFinalSerializer(serializers.Serializer):
    kilos_netos = serializers.FloatField()
    kilos_brutos = serializers.FloatField()
    por_brutos = serializers.FloatField()
    merma_exp = serializers.FloatField()
    final_exp = serializers.FloatField()
    merma_cat2 = serializers.FloatField()
    final_cat2 = serializers.FloatField()
    merma_des = serializers.FloatField()
    final_des = serializers.FloatField()
    
class PromedioMuestra(serializers.Serializer):
    basura = serializers.FloatField()
    pelon = serializers.FloatField()
    ciega = serializers.FloatField()
    cascara = serializers.FloatField()
    pepa_huerto = serializers.FloatField()
    pepa_bruta = serializers.FloatField()
    
class PromedioPepaMuestraSerializer(serializers.Serializer):
    mezcla = serializers.FloatField()
    insecto = serializers.FloatField()
    hongo = serializers.FloatField()
    dobles = serializers.FloatField()
    color = serializers.FloatField()
    vana = serializers.FloatField()
    pgoma = serializers.FloatField()
    goma = serializers.FloatField()
    
class PromedioCalibresSerializer(serializers.Serializer):
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
    
class CalibresResultadoSerializer(serializers.Serializer):
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
    
    
    
class EstadoAprobacionJefaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCRecepcionMateriaPrima
        fields = ['estado_aprobacion_cc']
        
class EstadoContraMuestraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCRecepcionMateriaPrima 
        fields = ['esta_contramuestra']
        
        
class CCTarjaSeleccionadaSerializer(serializers.ModelSerializer):
    estado_cc_label = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CCTarjaSeleccionada
        fields = '__all__'
        
    def get_estado_cc_label(self, obj):
        return obj.get_estado_cc_display()
    
    def get_codigo_tarja(self, obj):
        return obj.tarja_seleccionada   .codigo_tarja
    
class CCBinResultanteProgramaPHSerializer(serializers.ModelSerializer):
    estado_cc_label = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField(read_only=True)
    calidad_label = serializers.SerializerMethodField()
    
    def get_calidad_label(self, obj):
        return obj.get_calidad_display()
    
    
    class Meta:
        model = CCBinResultanteProgramaPH
        fields = '__all__'
        
    def get_estado_cc_label(self, obj):
        return obj.get_estado_cc_display()
    
    def get_codigo_tarja(self, obj):
        return obj.bin_resultante.codigo_tarja
    

class CCBinResultanteProcesoPHSerializer(serializers.ModelSerializer):
    estado_cc_label = serializers.SerializerMethodField()
    codigo_tarja = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CCBinResultanteProcesoPH
        fields = '__all__'
        
    def get_estado_cc_label(self, obj):
        return obj.get_estado_control_display()
    
    def get_codigo_tarja(self, obj):
        return obj.bin_resultante.codigo_tarja
    
    