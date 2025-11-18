from rest_framework import serializers
from .models import *
from core.models import *

class EnvasesGuiaRecepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvasesGuiaRecepcionMp
        fields = '__all__'
        
class RecepcionMpSerializer(serializers.ModelSerializer):
    envases = EnvasesGuiaRecepcionSerializer(many=True, read_only=True, source='envasesguiarecepcionmp_set')
    variedad = serializers.SerializerMethodField()
    kilos_neto_fruta = serializers.SerializerMethodField()
    kilos_envases = serializers.SerializerMethodField()
    tipo_producto = serializers.SerializerMethodField()

    
    def get_tipo_producto(self, obj):
        return obj.envasesguiarecepcionmp_set.all().first().get_tipo_producto_display()

    def get_kilos_envases(self, obj):
        total_peso = 0
        for envase in obj.envasesguiarecepcionmp_set.all():
            total_peso += envase.envase.peso * envase.cantidad_envases
            
        return total_peso
    
    def get_kilos_neto_fruta(self, obj):
        kilos_brutos = (obj.kilos_brutos_1 + obj.kilos_brutos_2) - (obj.kilos_tara_1 + obj.kilos_tara_2)
        total_peso = 0
        for envase in obj.envasesguiarecepcionmp_set.all():
            total_peso += envase.envase.peso * envase.cantidad_envases
            
        return kilos_brutos - total_peso
            
    
    def get_variedad(self, obj):
        return obj.envasesguiarecepcionmp_set.all().first().get_variedad_display()
    class Meta:
        model = RecepcionMp
        fields = '__all__'

class RecepcionListMpSerializer(serializers.ModelSerializer):
    envases = EnvasesGuiaRecepcionSerializer(many=True, read_only=True, source='envasesguiarecepcionmp_set')
    estado_label = serializers.SerializerMethodField()
    lote_rechazado = serializers.SerializerMethodField()
    kilos_neto_fruta = serializers.SerializerMethodField()
    kilos_envases = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()

    def get_lote_rechazado(self, obj):
        if obj.estado_recepcion == '4':
            rechazo = LoteRecepcionMpRechazadoPorCC.objects.get(recepcionmp=obj)

            return LoteRechazadoSerializer(rechazo).data
        else:
            return None

    def get_kilos_envases(self, obj):
        total_peso = 0
        for envase in obj.envasesguiarecepcionmp_set.all():
            total_peso += envase.envase.peso * envase.cantidad_envases

        return total_peso

    def get_kilos_neto_fruta(self, obj):
        kilos_brutos = (obj.kilos_brutos_1 + obj.kilos_brutos_2) - (obj.kilos_tara_1 + obj.kilos_tara_2)
        total_peso = 0
        for envase in obj.envasesguiarecepcionmp_set.all():
            total_peso += envase.envase.peso * envase.cantidad_envases

        return kilos_brutos - total_peso

    def get_variedad(self, obj):
        if obj.envasesguiarecepcionmp_set.all().exists():
            return obj.envasesguiarecepcionmp_set.all().first().get_variedad_display()
        return ''

    class Meta:
        model = RecepcionMp
        fields = '__all__'

    def get_estado_label(self, obj):
        return obj.get_estado_recepcion_display()


class GuiaRecepcionMPSerializer(serializers.ModelSerializer):
    estado_recepcion_label = serializers.SerializerMethodField()
    
    class Meta:
        model = GuiaRecepcionMP
        fields = '__all__'
        
    def get_estado_recepcion_label(self, obj):
        return obj.get_estado_recepcion_display()
    

class DetalleGuiaRecepcionMPSerializer(serializers.ModelSerializer):
    lotesrecepcionmp =RecepcionListMpSerializer(many=True, read_only=True, source='recepcionmp_set')
    nombre_camion = serializers.SerializerMethodField()
    nombre_camionero = serializers.SerializerMethodField()
    estado_recepcion_label = serializers.SerializerMethodField()
    nombre_productor = serializers.SerializerMethodField()
    nombre_comercializador = serializers.SerializerMethodField()
    nombre_creado_por = serializers.SerializerMethodField()
    email_productor = serializers.SerializerMethodField()
    
    
    def get_email_productor(self, obj):
        return obj.productor.email
    
    def get_nombre_creado_por(self, obj):
        if obj.creado_por:
            return "%s %s"% (obj.creado_por.first_name, obj.creado_por.last_name)
    
    def get_nombre_comercializador(self, obj):
        if obj.comercializador:
            return obj.comercializador.nombre
        else:
            return str('Sin comercializador')
    
    def get_nombre_productor(self, obj):
        return obj.productor.nombre
    
    def get_estado_recepcion_label(self, obj):
        return obj.get_estado_recepcion_display()
    
    def get_nombre_camionero(self, obj):
        chofer = Chofer.objects.get(pk=obj.camionero.pk)
        return "%s %s"% (chofer.nombre, chofer.apellido)
    
    def get_nombre_camion(self, obj):
        return  Camion.objects.get(pk=obj.camion.pk).patente
    
    class Meta:
        model = GuiaRecepcionMP
        fields = '__all__'


class EnvasesGuiaRecepcionMpRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvasesGuiaRecepcionMp
        exclude = ['recepcionmp']


class EnvasesGuiaRecepcionMpSerializer(serializers.ModelSerializer):
    envase_nombre = serializers.SerializerMethodField()
    variedad_label = serializers.SerializerMethodField()
    tipo_producto_label = serializers.SerializerMethodField()
    
    def get_tipo_producto_label(self, obj):
        return obj.get_tipo_producto_display()
    
    def get_variedad_label(self, obj):
        return obj.get_variedad_display()
    
    def get_envase_nombre(self, obj):
        if obj.envase:
            return obj.envase.nombre
        else:
            'No hay envase registrado'
        
    class Meta:
        model = EnvasesGuiaRecepcionMp
        fields = '__all__'


class DetalleRecepcionMpSerializer(serializers.ModelSerializer):
    envases = EnvasesGuiaRecepcionSerializer(many=True, read_only=True, source='envasesguiarecepcionmp_set')
    variedad = serializers.SerializerMethodField()
    kilos_neto_fruta = serializers.SerializerMethodField()
    kilos_envases = serializers.SerializerMethodField()
    tipo_producto = serializers.SerializerMethodField()
    cantidad_envases = serializers.SerializerMethodField()
    
    
    def get_cantidad_envases(self, obj):
        if obj.envasesguiarecepcionmp_set.all().count() >= 1:
            cantidad = 0
            for envase in obj.envasesguiarecepcionmp_set.all():
                cantidad += envase.cantidad_envases 
                return cantidad
        return 0  
    
    def get_tipo_producto(self, obj):
        return obj.envasesguiarecepcionmp_set.all().first().get_tipo_producto_display()

    def get_kilos_envases(self, obj):
        total_peso = 0
        for envase in obj.envasesguiarecepcionmp_set.all():
            total_peso += envase.envase.peso * envase.cantidad_envases
            
        return total_peso
    
    def get_kilos_neto_fruta(self, obj):
        kilos_brutos = (obj.kilos_brutos_1 + obj.kilos_brutos_2) - (obj.kilos_tara_1 + obj.kilos_tara_2)
        total_peso = 0
        for envase in obj.envasesguiarecepcionmp_set.all():
            total_peso += envase.envase.peso * envase.cantidad_envases
            
        return kilos_brutos - total_peso
            
    
    def get_variedad(self, obj):
        return obj.envasesguiarecepcionmp_set.all().first().get_variedad_display()
        
        
    class Meta:
        model = RecepcionMp
        fields = '__all__'
        

class EnvasesMpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EnvasesMp
        fields = '__all__'
    

class LoteRechazadoSerializer(serializers.ModelSerializer):
    resultado_rechazo_label = serializers.SerializerMethodField()

    class Meta:
        model = LoteRecepcionMpRechazadoPorCC
        fields = '__all__'
        
    def get_resultado_rechazo_label(self, obj):
        return obj.get_resultado_rechazo_display()



