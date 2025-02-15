from rest_framework import serializers
from exportacion.serializers import PedidoExportacionSerializer
from guiassalida.serializers import GuiaSalidaFrutaSerializer
from .models import FrutaFicticia, Pedido, FrutaEnPedido
from bodegas.funciones import *
from embalaje.models import *

class FrutaEnPedidoSerializer(serializers.ModelSerializer):
    tipo_fruta_en_pedido = serializers.SerializerMethodField()
    codigo_fruta = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    kilos = serializers.SerializerMethodField()
    peso_caja = serializers.SerializerMethodField()
    
    def get_variedad(self, obj):
        if obj.tipo_fruta.model == 'binbodega':
            variedad = obj.fruta.variedad
            return variedad
        elif obj.tipo_fruta.model == 'palletproductoterminado':
            variedad = obj.fruta.embalaje.get_variedad_display()
            return variedad
        
    def get_calidad(self, obj):
        if obj.tipo_fruta.model == 'binbodega':
            calidad = obj.fruta.calidad
            return calidad
        elif obj.tipo_fruta.model == 'palletproductoterminado':
            calidad = obj.fruta.embalaje.get_calidad_display()
            return calidad
        
    def get_calibre(self, obj):
        if obj.tipo_fruta.model == 'binbodega':
            calibre = obj.fruta.calibre
            return calibre
        elif obj.tipo_fruta.model == 'palletproductoterminado':
            calibre = obj.fruta.embalaje.get_calibre_display()
            return calibre
    
    def get_codigo_fruta(self, obj):
        if obj.tipo_fruta.model == 'binbodega':
            codigo_fruta = obj.fruta.codigo_tarja_bin
            return codigo_fruta
        elif obj.tipo_fruta.model == 'palletproductoterminado':
            return obj.fruta.codigo_pallet
    
    def get_tipo_fruta_en_pedido(self, obj):
        if obj.tipo_fruta.model == 'binbodega':
            return 'Pepa En Bin'
        elif obj.tipo_fruta.model == 'palletproductoterminado':
            return 'Pallet Producto Terminado'

    def get_kilos(self, obj):
        if obj.tipo_fruta.model == 'binbodega':
            return obj.fruta.kilos_bin
        elif obj.tipo_fruta.model == 'palletproductoterminado':
            return obj.fruta.peso_total_pallet
        
    def get_peso_caja(self, obj):
        if obj.caja_origen:
            return obj.caja_origen.peso_x_caja
        else:
            return False

    class Meta:
        model = FrutaEnPedido
        fields = '__all__'
        
    def validate(self, data):
        tipo_fruta = data['tipo_fruta']
        id_fruta = data['id_fruta']
        cantidad = data['cantidad']

        if tipo_fruta.model == 'binbodega' and cantidad != 1:
            raise serializers.ValidationError("La cantidad debe ser 1 para BinBodega.")
        
        if tipo_fruta.model == 'palletproductoterminado':
            pallet = PalletProductoTerminado.objects.get(id=id_fruta)
            total_kilos = sum(caja.cantidad_cajas * caja.peso_x_caja for caja in pallet.cajasenpalletproductoterminado_set.all())
            if cantidad > total_kilos:
                raise serializers.ValidationError("La cantidad de kilos no puede exceder el total disponible en el pallet.")
        
        return data

class PedidoSerializer(serializers.ModelSerializer):
    frutas = FrutaEnPedidoSerializer(many=True, read_only=True)
    # pedido = serializers.SerializerMethodField()
    mercado_interno = serializers.SerializerMethodField()
    exportacion = serializers.SerializerMethodField()
    guia_salida = serializers.SerializerMethodField()
    # razon_social = serializers.SerializerMethodField()
    # despacho_retiro = serializers.SerializerMethodField()
    # fecha_entrega = serializers.SerializerMethodField()
    # estado_pedido_label = serializers.SerializerMethodField()

    # def get_razon_social(self, obj):
    #     # print(obj.pedido.cliente)
    #     return 'QUITAR RAZON SOCIAL'
    #     # return obj.pedido.cliente.razon_social

    # def get_despacho_retiro(self, obj):
    #     return 'QUITAR DESPACHO RETIRO'
    #     # return obj.pedido.retira_cliente

    # def get_fecha_entrega(self, obj):
    #     return 'QUITAR FECHA ENTREGA'
    #     # return obj.pedido.fecha_entrega

    # def get_estado_pedido_label(self, obj):
    #     if obj.tipo_pedido.model == 'pedidomercadointerno':
    #         return obj.pedido.get_estado_pedido_display()
    #     elif obj.tipo_pedido.model == 'pedidoexportacion':
    #         return obj.pedido.get_estado_pedido_display()
    #     elif obj.tipo_pedido.model == 'guiasalidafruta':
    #         return obj.pedido.get_estado_guia_salida_display()

    # def get_pedido(self, obj):
    #     return str(obj.pedido_real)

    def get_mercado_interno(self, obj):
        if obj.tipo_pedido.model == 'pedidomercadointerno':
            from mercadointerno.serializers import PedidoMercadoInternoSerializer
            return PedidoMercadoInternoSerializer(obj.pedido, read_only=True).data
        return False

    def get_exportacion(self, obj):
        if obj.tipo_pedido.model == 'pedidoexportacion':
            return PedidoExportacionSerializer(obj.pedido, read_only=True).data
        return False
        
    def get_guia_salida(self, obj):
        if obj.tipo_pedido.model == 'guiasalidafruta':
            return GuiaSalidaFrutaSerializer(obj.pedido, read_only=True).data
        return False

    class Meta:
        model = Pedido
        fields = '__all__'

class PedidosUnidosSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_pedido = serializers.IntegerField()
    pedido = serializers.CharField()
    razon_social = serializers.CharField()
    tipo_guia = serializers.CharField()
    despacho_retiro = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_entrega = serializers.DateField()
    estado_pedido = serializers.CharField()
    comercializador = serializers.CharField(allow_null=True) 
    
class PedidoGuiaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_guia = serializers.IntegerField()
    cliente = serializers.CharField()
    tipo_guia = serializers.CharField()
    despacho_retiro = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_entrega = serializers.DateField()
    estado_pedido = serializers.CharField()
    comercializador = serializers.CharField(allow_null=True) 
    
class FrutaFicticiaSerializer(serializers.ModelSerializer):
    nombre_producto_label = serializers.SerializerMethodField()
    calidad_label = serializers.SerializerMethodField()
    variedad_label = serializers.SerializerMethodField()
    calibre_label = serializers.SerializerMethodField()
    formato_label = serializers.SerializerMethodField()
    
    def get_nombre_producto_label(self, obj):
        return obj.get_nombre_producto_display()
    
    def get_calidad_label(self, obj):
        return obj.get_calidad_display()
    
    def get_variedad_label(self, obj):
        return obj.get_variedad_display()
    
    def get_calibre_label(self, obj):
        return obj.get_calibre_display()
    
    def get_formato_label(self, obj):
        if obj.formato:
            return obj.formato.nombre
        else:
            return 'Bin de Fruta'
    
    class Meta:
        model = FrutaFicticia
        fields = '__all__'