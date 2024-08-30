from rest_framework import serializers
from .models import PedidoMercadoInterno
from pedidos.models import *
from despacho.models import *
from clientes.models import *

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

class PedidoMercadoInternoSerializer(serializers.ModelSerializer):
    # fruta_ficticia = FrutaFicticiaSerializer(many=True, read_only = True, source = 'frutapedido_set')
    fruta_ficticia = serializers.SerializerMethodField()
    condicion_pago_label = serializers.SerializerMethodField()
    estado_pedido_label = serializers.SerializerMethodField()
    tipo_venta_label = serializers.SerializerMethodField()
    solicitado_por_label = serializers.SerializerMethodField()
    cliente_info = serializers.SerializerMethodField()
    # retira_cliente_info = serializers.SerializerMethodField()
    # tipo_pedido = serializers.SerializerMethodField()
    id_pedido_padre = serializers.SerializerMethodField()
    
    def get_fruta_ficticia(self, obj):
        from pedidos.serializers import FrutaFicticiaSerializer
        frutapedido = obj.fruta_pedido
        return FrutaFicticiaSerializer(frutapedido, many=True).data

    def get_id_pedido_padre(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = obj.pk).first()
        return pedido.pk
    
    # def get_tipo_pedido(self, obj):
    #     ct = ContentType.objects.get_for_model(obj)
    #     pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = obj.pk).first()
    #     fruta = FrutaEnPedido.objects.filter(pedido = pedido)
    #     if fruta.exists():
    #         fruta.first().tipo_fruta.model
    #     else:
    #         'No hay'
            

    def get_cliente_info(self, obj):
        return {
            "nombre": obj.cliente.nombre_fantasia,
            "telefono": obj.cliente.telefono,
            "movil": obj.cliente.movil,
            "sucursal": obj.sucursal.nombre if obj.sucursal != None else '',
            "rut": obj.cliente.rut_cliente,
            "email": obj.cliente.email_cliente
        }
    
    def get_condicion_pago_label(self, obj):
        return obj.get_condicion_pago_display()
    
    def get_estado_pedido_label(self, obj):
        return obj.get_estado_pedido_display()
    
    def get_tipo_venta_label(self, obj):
        return obj.get_tipo_venta_display()
    
    def get_solicitado_por_label(self, obj):    
        if obj.solicitado_por:
            return f'{obj.solicitado_por.first_name} {obj.solicitado_por.last_name}'
        else:
            return 'No se identifica quien lo creo'
        
    # def get_retira_cliente_info(self, obj):
    #     return obj.quien_retira if obj.retira_cliente else 'Despacho' 
    

    class Meta:
        model = PedidoMercadoInterno
        fields = '__all__'

