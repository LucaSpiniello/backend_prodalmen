from functools import reduce
from rest_framework import serializers
from .models import *
from django.contrib.contenttypes.models import *
from controlcalidad.models import * 
from bodegas.funciones import *
from django.db.models import Sum
from collections import defaultdict

class TipoEmbalajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEmbalaje
        fields = '__all__'

class EtiquetaEmbalajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtiquetaEmbalaje
        fields = '__all__'

class FrutaBodegaSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    programa = serializers.SerializerMethodField()
    cc_tarja = serializers.SerializerMethodField()
    tipo_binbodega = serializers.SerializerMethodField()
    kilos_fruta = serializers.SerializerMethodField()

    
    def get_kilos_fruta(self, obj):
        kilos = get_kilos_bin(obj.bin_bodega)
        return kilos

    def get_tipo_binbodega(self, obj):
        tipo_bodega = get_tipo_binbodega(obj.bin_bodega)
        return tipo_bodega
    
    def get_codigo_tarja(self, obj):
        codigo_tarja = get_codigo_tarja(obj.bin_bodega)
        return codigo_tarja
                
    def get_cc_tarja(self, obj):
        cc_tarja = get_cc_tarja(obj.bin_bodega)
        return cc_tarja   
        
    def get_programa(self, obj):
        programa = get_programa(obj.bin_bodega)
        return programa
    
    class Meta:
        model = FrutaBodega
        fields = '__all__'

# class OperariosEnEmbalajeSerializer(serializers.ModelSerializer):
#     tipo_operario_label = serializers.SerializerMethodField()
#     nombres = serializers.SerializerMethodField()
#     rut_operario = serializers.SerializerMethodField()
    
#     def get_rut_operario(self, obj):
#         return f'{obj.operario.rut}'
        
#     def get_nombres(self, obj):
#         return f'{obj.operario.nombre} {obj.operario.apellido}'
    
#     def get_tipo_operario_label(self, obj):
#         return obj.get_skill_operario_display()

        
#     class Meta:
#         model = OperariosEnEmbalaje
#         fields = '__all__'

class CajasEnPalletProductoTerminadoSerializer(serializers.ModelSerializer):
    tipo_caja_label = serializers.SerializerMethodField()
    
    def get_tipo_caja_label(self, obj):
        return f'{obj.tipo_caja.nombre} de {obj.tipo_caja.peso} Kgs'
    class Meta:
        model = CajasEnPalletProductoTerminado
        fields = '__all__'

class PalletProductoTerminadoSerializer(serializers.ModelSerializer):
    cajas_en_pallet = CajasEnPalletProductoTerminadoSerializer(many=True, read_only=True, source = 'cajasenpalletproductoterminado_set')
    calle_bodega_label = serializers.SerializerMethodField()
    peso_pallet = serializers.ReadOnlyField(source='peso_total_pallet')
    registrado_por_label = serializers.SerializerMethodField()
    variedad_programa = serializers.SerializerMethodField()
    calibre_programa = serializers.SerializerMethodField()
    calidad_programa = serializers.SerializerMethodField()
    
    def get_variedad_programa(self, obj):
        return obj.embalaje.get_variedad_display()
    
    def get_calibre_programa(self, obj):
        return obj.embalaje.get_calibre_display()
    
    def get_calidad_programa(self, obj):
        return obj.embalaje.get_calidad_display()
    
    def get_registrado_por_label(self, obj):
        return f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
    
    def get_calle_bodega_label(self, obj):
        return obj.get_calle_bodega_display()
    
    # def get_peso_pallet(self, obj):
    #     total_peso = 0  # Inicializar la variable que almacenará el total del peso
    #     if obj.cajasenpalletproductoterminado_set.exists():  # Verificar si hay cajas en el pallet
    #         for caja in obj.cajasenpalletproductoterminado_set.all():
    #             total_peso += caja.peso_x_caja * caja.cantidad_cajas  # Sumar el peso de cada caja al total
    #     return round(total_peso, 2)  # Retornar el peso total redondeado a dos decimales

    

    class Meta:
        model = PalletProductoTerminado
        fields = '__all__'

class PalletProductoTerminadoParaPedidoSerializer(serializers.ModelSerializer):
    total_cajas_ptt = serializers.SerializerMethodField()
    peso_total_ptt = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()
    tipo_producto = serializers.SerializerMethodField()
    peso_caja = serializers.SerializerMethodField()
            
    def get_peso_total_ptt(self, obj):
        return obj.peso_total_pallet

    def get_total_cajas_ptt(self, obj):
        return obj.total_cajas
    
    def get_calidad(self, obj):
        return obj.embalaje.get_calidad_display()
    
    def get_variedad(self, obj):
        return obj.embalaje.get_variedad_display()
    
    def get_calibre(self, obj):
        return obj.embalaje.get_calibre_display()
    
    def get_tipo_producto(self, obj):
        return obj.embalaje.get_tipo_producto_display()
    
    def get_peso_caja(self, obj):
        caja = CajasEnPalletProductoTerminado.objects.filter(pallet=obj.pk)
        if caja.exists():
            return caja.first().peso_x_caja
        else: 
            return False
    class Meta:
        model = PalletProductoTerminado
        fields = '__all__'
        # read_only_fields = ['cajas_disponibles']

class EmbalajeSerializer(serializers.ModelSerializer):
    calidad_label = serializers.SerializerMethodField()
    calibre_label = serializers.SerializerMethodField()
    variedad_label = serializers.SerializerMethodField()
    estado_embalaje_label = serializers.SerializerMethodField()
    solicitado_por = serializers.SerializerMethodField()
    tipo_producto_label = serializers.SerializerMethodField()
    tipo_embalaje_label = serializers.SerializerMethodField()
    kilos_resultantes = serializers.SerializerMethodField()
    kilos_faltantes = serializers.SerializerMethodField()
    kilos_sobrantes = serializers.SerializerMethodField()
    condicion_cierre = serializers.SerializerMethodField()
    condicion_termino = serializers.SerializerMethodField()
    kilos_ingresados = serializers.SerializerMethodField()
    #metricas_embalaje = serializers.SerializerMethodField()

    
    # def get_metricas_embalaje(self, obj):
    #     # Inicializar un diccionario para acumular los kilos por cada día
    #     kilos_por_dia = defaultdict(float)

    #     # Obtener todos los objetos FrutaBodega que han sido procesados
    #     frutas = FrutaBodega.objects.filter(embalaje = obj, procesado=True).select_related('embalaje', 'bin_bodega')

    #     for fruta in frutas:
    #         if fruta.bin_bodega and fruta.embalaje:
    #             # Asegurar que la fecha se extrae y normaliza correctamente
    #             dia = fruta.embalaje.fecha_inicio_embalaje

    #             # Sumar los kilos de fruta a la fecha correspondiente
    #             kilos_por_dia[dia] += fruta.bin_bodega.binbodega.kilos_fruta

    #     # Crear una lista de diccionarios ordenada por fecha, solo si hay kilos procesados
    #     sorted_kilos = [{'dia': dia, 'kilos': kilos} for dia, kilos in sorted(kilos_por_dia.items()) if kilos > 0]

    #     return sorted_kilos

    def get_kilos_ingresados(self, obj):
        kilos = 0
        for bin in FrutaBodega.objects.filter(embalaje=obj):
            kilos += bin.bin_bodega.binbodega.kilos_fruta
            
        if kilos != None:
            return kilos
        return 0
    
    def get_condicion_termino(self, obj):
        operarios = obj.operariosenembalaje_set.filter(programa = obj).count()
        fruta_bodega = FrutaBodega.objects.filter(embalaje=obj)
        
        pallets = PalletProductoTerminado.objects.filter(embalaje=obj)
        cajas_en_pallet = CajasEnPalletProductoTerminado.objects.filter(pallet__in=pallets).count()
        
        bines_procesado_status = [bin.procesado for bin in fruta_bodega]
        bines = all(bines_procesado_status)
        
        if bines and operarios >= 1 and cajas_en_pallet >= 1:
            return True
        return False

    def get_condicion_cierre(self, obj):
        # Contar operarios asociados
        operarios = obj.operariosenembalaje_set.all().count()

        # Obtener fruta en bodega asociada al embalaje
        fruta_bodega = FrutaBodega.objects.filter(embalaje=obj)


        # Obtener el estado de procesado de todos los bins
        bines_procesado_status = [bin.procesado for bin in fruta_bodega]
        bines = all(bines_procesado_status)
        print(bines)

        # Obtener pallets asociados al embalaje y contar las cajas en pallets
        pallets = PalletProductoTerminado.objects.filter(embalaje=obj)
        cajas_en_pallet = CajasEnPalletProductoTerminado.objects.filter(pallet__in=pallets)
        total_kilos = sum((caja.peso_x_caja * caja.cantidad_cajas) for caja in cajas_en_pallet)

        
        print((float(total_kilos) >= float(obj.kilos_solicitados)))

        # Verificar la condición de cierre
        if (float(total_kilos) >= float(obj.kilos_solicitados)) and operarios >= 1 and bines and cajas_en_pallet.count() >= 1:
            return True

        return False

    def get_kilos_faltantes(self, obj):
        kilos_totales = 0
        if obj.palletproductoterminado_set.exists():  # Verifica si hay al menos un pallet
            for pallet in obj.palletproductoterminado_set.all():
                for caja in pallet.cajasenpalletproductoterminado_set.all():
                    peso = caja.cantidad_cajas * caja.peso_x_caja
                    kilos_totales += peso
        return round(obj.kilos_solicitados - kilos_totales)

    def get_kilos_sobrantes(self, obj):
        kilos_totales = 0
        if obj.palletproductoterminado_set.exists():  # Verifica si hay al menos un pallet
            for pallet in obj.palletproductoterminado_set.all():
                for caja in pallet.cajasenpalletproductoterminado_set.all():
                    peso = caja.cantidad_cajas * caja.peso_x_caja
                    kilos_totales += peso

        # Calcular los kilos sobrantes si los kilos totales exceden los kilos solicitados
        if kilos_totales > obj.kilos_solicitados:
            kilos_sobrantes = kilos_totales - obj.kilos_solicitados
        else:
            kilos_sobrantes = 0  # No hay kilos sobrantes si no se exceden los kilos solicitados

        return round(kilos_sobrantes)  # Retorna el resultado redondeado para un manejo más sencillo de los valores

    def get_kilos_resultantes(self, obj):
        kilos_totales = 0
        if obj.palletproductoterminado_set.exists():  # Verifica si hay al menos un pallet
            for pallet in obj.palletproductoterminado_set.all():
                for caja in pallet.cajasenpalletproductoterminado_set.all():
                    peso = caja.cantidad_cajas * caja.peso_x_caja
                    kilos_totales += peso
        return kilos_totales

    def get_tipo_embalaje_label(self, obj):
        return f'{obj.tipo_embalaje.nombre} de {obj.tipo_embalaje.peso} Kilos'
    
    def get_tipo_producto_label(self, obj):
        return obj.get_tipo_producto_display()
    
    def get_estado_embalaje_label(self, obj):
        return obj.get_estado_embalaje_display()
    
    def get_calidad_label(self, obj):
        return obj.get_calidad_display()
    
    def get_calibre_label(self, obj):
        return obj.get_calibre_display()
    
    def get_variedad_label(self, obj):
        return obj.get_variedad_display()
    
    def get_solicitado_por(self, obj):
        return f'{obj.configurado_por.first_name} {obj.configurado_por.last_name}'
    

    class Meta:
        model = Embalaje
        fields = '__all__'



class PalletProductoTerminadoBodegaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo_pallet = serializers.CharField()
    calidad = serializers.CharField()
    variedad = serializers.CharField()
    calibre = serializers.CharField()
    cantidad_cajas = serializers.IntegerField()
    peso_pallet = serializers.FloatField()
    
    
class OperariosAgregadosEmbalajeSerializer(serializers.Serializer):
    operario__rut = serializers.CharField()
    operario__nombre = serializers.CharField()
    operario__apellido = serializers.CharField()
    skill_operario = serializers.CharField()
    total_kilos_producidos = serializers.FloatField()
    dias_trabajados = serializers.IntegerField()     
    
    
    
    
# class DiaDeOperarioEmbalajeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DiaDeOperarioEmbalaje
#         fields = ['id','dia', 'kilos_dia', 'ausente']
# class DiaDeOperarioEmbalajeUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DiaDeOperarioEmbalaje
#         fields = ['ausente']
        
class DiaDeOperarioEmbalajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioEmbalaje
        fields = ['id','dia', 'kilos_dia', 'ausente']


class OperariosEnEmbalajeSerializer(serializers.ModelSerializer):
    dias = DiaDeOperarioEmbalajeSerializer(many=True, read_only=True)

    class Meta:
        model = OperariosEnEmbalaje
        fields = '__all__'
        
class DiaDeOperarioEmbalajeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaDeOperarioEmbalaje
        fields = ['ausente']
            
class OperariosEnEmbalajeSerializer(serializers.ModelSerializer):
    operarios = OperariosEnEmbalajeSerializer(source='operariosenembalaje_set', many=True, read_only=True)
    nombres = serializers.SerializerMethodField()
    rut_operario = serializers.SerializerMethodField()
    tipo_operario_label = serializers.SerializerMethodField()
    
    
    class Meta:
        model = OperariosEnEmbalaje
        fields = '__all__'
        
    def get_tipo_operario_label(self, obj):
        return obj.get_skill_operario_display()
        
    def get_rut_operario(self, obj):
        return obj.operario.rut
    
    def get_nombres(self, obj):
        return f'{obj.operario.nombre} {obj.operario.apellido}'
