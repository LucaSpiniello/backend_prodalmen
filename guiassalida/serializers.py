# serializers.py
from rest_framework import serializers
from .models import GuiaSalidaFruta
from pedidos.models import *

# class FrutaEnGuiaSalidaSerializer(serializers.ModelSerializer):
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
#         model = FrutaEnGuiaSalida
#         fields = '__all__'

class GuiaSalidaFrutaSerializer(serializers.ModelSerializer):
    # fruta_pedido = FrutaEnGuiaSalidaSerializer(many=True, read_only=True)
    fruta_ficticia = serializers.SerializerMethodField()
    id_pedido_padre = serializers.SerializerMethodField()
    tipo_salida_label = serializers.SerializerMethodField()
    estado_guia_salida_label = serializers.SerializerMethodField()
    tipo_cliente_label = serializers.SerializerMethodField()
    cliente_info = serializers.SerializerMethodField()
    solicitado_por_label = serializers.SerializerMethodField()
    
    def get_cliente_info(self, obj):
        nombre = None
        email = None
        rut = None
        if obj.tipo_cliente.model == 'productor':
            nombre = obj.cliente.nombre
            email = obj.cliente.email
            rut = obj.cliente.rut_productor
        elif obj.tipo_cliente.model in ['clientemercadointerno', 'clienteexportacion']:
            nombre = obj.cliente.nombre_fantasia
            email = obj.cliente.email_cliente
            rut = obj.cliente.rut_cliente
        elif obj.tipo_cliente.model == 'user':
            nombre = f'{obj.cliente.first_name} {obj.cliente.last_name}'
            email = obj.cliente.email
            rut = obj.cliente.rut
        
        return {
            "nombre": nombre,
            "email": email,
            "rut": rut
        }

    def get_solicitado_por_label(self, obj):
        if obj.solicitado_por:
            return obj.solicitado_por.get_nombre()
        else:
            return 'Desconocido'

    def get_tipo_cliente_label(self, obj):
        if obj.tipo_cliente.model == 'productor':
            return 'Productor'  
        elif obj.tipo_cliente.model == 'clientemercadointerno':
            return 'Cliente Interno'
        elif obj.tipo_cliente.model == 'clienteexportacion':
            return 'Cliente Exportación'
        elif obj.tipo_cliente.model == 'user':
            return 'Usuario Sistema'
    
    def get_estado_guia_salida_label(self, obj):
        return obj.get_estado_guia_salida_display()
    
    def get_tipo_salida_label(self, obj):
        return obj.get_tipo_salida_display()
    
    def get_id_pedido_padre(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = obj.pk).first()
        return pedido.pk
    
    def get_fruta_ficticia(self, obj):
        from pedidos.serializers import FrutaFicticiaSerializer
        frutapedido = obj.fruta_pedido
        return FrutaFicticiaSerializer(frutapedido, many=True).data

    class Meta:
        model = GuiaSalidaFruta
        fields = '__all__'
