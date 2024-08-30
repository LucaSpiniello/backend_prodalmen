from rest_framework import serializers
from .models import PedidoExportacion
from django.contrib.contenttypes.models import ContentType
from pedidos.models import *


# class FrutaPedidoSerializer(serializers.ModelSerializer):
#     nombre_producto_label = serializers.SerializerMethodField()
#     calidad_label = serializers.SerializerMethodField()
#     variedad_label = serializers.SerializerMethodField()
#     calibre_label = serializers.SerializerMethodField()
#     formato_label = serializers.SerializerMethodField()
    
#     def get_nombre_producto_label(self, obj):
#         if obj.nombre_producto:
#             return obj.get_nombre_producto_display()
        
#     def get_calidad_label(self, obj):
#         if obj.calidad:
#             return obj.get_calidad_display()
        
#     def get_variedad_label(self, obj):
#         if obj.variedad:
#             return obj.get_variedad_display()
        
#     def get_calibre_label(self, obj):
#         if obj.calibre:
#             return obj.get_calibre_display()
        
#     def get_formato_label(self, obj):
#         if obj.formato:
#             return f'{obj.formato.nombre} de {obj.formato.peso} Kilos'
        
#     class Meta:
#         model = FrutaPedido
#         fields = '__all__'

class PedidoExportacionSerializer(serializers.ModelSerializer):
    # frutas = FrutaPedidoSerializer(many=True, required=False, read_only = True, source = 'frutapedido_set')
    moneda_venta_label = serializers.SerializerMethodField()
    estado_pedido_label = serializers.SerializerMethodField()
    tipo_flete_label = serializers.SerializerMethodField()
    cliente_info = serializers.SerializerMethodField()
    tipo_despacho_label = serializers.SerializerMethodField()
    solicitado_por_label = serializers.SerializerMethodField()
    id_pedido_padre = serializers.SerializerMethodField()
    
    
    def get_id_pedido_padre(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = obj.pk).first()
        return pedido.pk
    
    def get_moneda_venta_label(self, obj):
        return obj.get_moneda_venta_display()
    
    def get_tipo_despacho_label(self, obj):
        return obj.get_tipo_despacho_display()
    
    def get_cliente_info(self, obj):
        return {
            "nombre": obj.cliente.nombre_fantasia,
            "rut": obj.cliente.dni_cliente,
            "email": obj.cliente.email_cliente,
            "telefono": obj.cliente.telefono,
            "movil": obj.cliente.movil
        }

    
    def get_estado_pedido_label(self, obj):
        return obj.get_estado_pedido_display()
    
    def get_tipo_flete_label(self, obj):
        return obj.get_tipo_flete_display()
    
    def get_solicitado_por_label(self, obj):
        if obj.creado_por:
            return f'{obj.creado_por.first_name} {obj.creado_por.last_name}'
        else:
            return 'No se identifica quien lo creo'
    

    class Meta:
        model = PedidoExportacion
        fields = '__all__'  
