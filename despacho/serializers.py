from rest_framework import serializers
from .models import Despacho, DespachoProducto
from pedidos.models import *
from clientes.models import *

class DespachoProductoSerializer(serializers.ModelSerializer):
    codigo_fruta = serializers.SerializerMethodField()
    tipo_fruta = serializers.SerializerMethodField()
    
    def get_tipo_fruta(self, obj):
        fruta = obj.fruta_en_pedido
        if fruta.tipo_fruta.model == 'binbodega':
            return 'Bin Bodega'
        elif fruta.tipo_fruta.model == 'palletproductoterminado':
            return 'Pallet Producto Terminado'
    
    def get_codigo_fruta(self, obj):
        fruta = obj.fruta_en_pedido
        if fruta.tipo_fruta.model == 'binbodega':
            if fruta.fruta.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
                return fruta.fruta.binbodega.produccion.codigo_tarja
            elif fruta.fruta.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                return fruta.fruta.binbodega.reproceso.codigo_tarja
            elif fruta.fruta.tipo_binbodega.model in ['bodegag3', 'bodegag4']:
                return fruta.fruta.binbodega.seleccion.codigo_tarja
            elif fruta.fruta.tipo_binbodega.model in ['binsubproductoseleccion', 'agrupaciondebinsbodegas']:
                return fruta.fruta.binbodega.codigo_tarja
            elif fruta.fruta.tipo_binbodega.model == 'frutasobrantedeagrupacion':
                if fruta.fruta.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
                    return fruta.fruta.binbodega.tarja.produccion.codigo_tarja
                elif fruta.fruta.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
                    return fruta.fruta.binbodega.tarja.reproceso.codigo_tarja
                elif fruta.fruta.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4']:
                    return fruta.fruta.binbodega.tarja.seleccion.codigo_tarja
                elif fruta.fruta.binbodega.tipo_tarja.model == 'agrupaciondebinsbodegas':
                    return fruta.fruta.binbodega.tarja.codigo_tarja
        elif fruta.tipo_fruta.model == 'palletproductoterminado':
            return fruta.fruta.codigo_pallet
    
    class Meta:
        model = DespachoProducto
        fields = ['fruta_en_pedido', 'cantidad', 'codigo_fruta', 'tipo_fruta', 'despacho']

class DespachoSerializer(serializers.ModelSerializer):
    productos_despacho = DespachoProductoSerializer(many=True, required=False)
    direccion = serializers.SerializerMethodField()
    
    def get_direccion(self, obj: Despacho):
        pedido = Pedido.objects.get(pk = obj.pedido.pk).pedido_real
        ct = ContentType.objects.get_for_model(pedido)
        if ct.model == 'pedidomercadointerno':
            cliente = ClienteMercadoInterno.objects.get(pk = pedido.cliente.pk)
            sucursal = SucursalClienteMercado.objects.filter(cliente = cliente).first()
            return {
                "direccion": sucursal.direccion,
                "telefono": sucursal.telefono,
                "correo":  sucursal.email_sucursal
            }
        elif ct.model == 'pedidoexportacion':
            cliente = ClienteExportacion.objects.get(pk = pedido.cliente.pk)
            sucursal = SucursalClienteExportacion.objects.filter(cliente = cliente).first(  )
            return {
                "direccion": sucursal.direccion,
                "telefono": sucursal.telefono,
                "correo":  sucursal.email_sucursal
            }

    
    

    class Meta:
        model = Despacho
        fields = '__all__'

    def create(self, validated_data):
        productos_data = validated_data.pop('productos_despacho', None)
        despacho = Despacho.objects.create(**validated_data)

        if productos_data:
            for producto_data in productos_data:
                DespachoProducto.objects.create(despacho=despacho, **producto_data)
        else:
            pedido = despacho.pedido
            for fruta in pedido.frutaenpedido.all():
                DespachoProducto.objects.create(
                    despacho=despacho,
                    fruta_en_pedido=fruta,
                    cantidad=fruta.cantidad  # Asumiendo que el modelo FrutaEnPedido tiene un campo `cantidad`
                )

        return despacho
