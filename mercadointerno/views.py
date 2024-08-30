from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import PedidoMercadoInterno
from .serializers import PedidoMercadoInternoSerializer
from django.shortcuts import get_object_or_404, get_list_or_404
from pedidos.models import *
from bodegas.funciones import *
from rest_framework.decorators import action
from guiassalida.funciones import *


class PedidoMercadoInternoViewSet(viewsets.ModelViewSet):
    queryset = PedidoMercadoInterno.objects.all()
    serializer_class = PedidoMercadoInternoSerializer
    
    @action(detail=True, methods=['GET'])
    def pdf_pedido_interno(self, request, pk = None):
        pedido_interno = PedidoMercadoInterno.objects.filter(pk = pk).first()
        ct = ContentType.objects.get_for_model(pedido_interno)
        pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = pedido_interno.pk).first()
        fruta_en_pedido = FrutaEnPedido.objects.filter(pedido = pedido)
        
        
        resultados = []
        
        for fruta in fruta_en_pedido:
            codigo = obtener_codigo(fruta)
            programa = obtener_programa_guia(fruta)
            producto = obtener_producto(fruta)
            calidad = obtener_calidad(fruta)
            variedad = obtener_variedad(fruta)
            calibre = obtener_calibre(fruta)
    
            dic = {
                "codigo": codigo,
                "programa": programa,
                "producto": producto,
                "calidad": calidad,
                "variedad": variedad,
                "calibre": calibre,
            }
            
            resultados.append(dic)
            
        serializer = PedidoMercadoInternoSerializer(pedido_interno)
            
        return Response({
            "pedido_interno": serializer.data,
            "fruta_en_pedido": resultados
        })

# class FrutaPedidoViewSet(viewsets.ModelViewSet):
#     queryset = FrutaPedido.objects.all()
#     serializer_class = FrutaPedidoSerializer

   