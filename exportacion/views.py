from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import PedidoExportacion
from .serializers import PedidoExportacionSerializer
from rest_framework.decorators import action
from django.contrib.contenttypes.models import *
from pedidos.models import *
from bodegas.funciones import *
from .funciones import *
from guiassalida.funciones import *



class PedidoExportacionViewSet(viewsets.ModelViewSet):
    queryset = PedidoExportacion.objects.all()
    serializer_class = PedidoExportacionSerializer
    
    @action(detail=True, methods=['GET'])
    def pdf_pedido_exportacion(self, request, pk = None):
        pedido_exportacion = PedidoExportacion.objects.filter(pk = pk).first()
        ct = ContentType.objects.get_for_model(pedido_exportacion)
        pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = pedido_exportacion.pk).first()
        fruta_en_pedido = FrutaEnPedido.objects.filter(pedido = pedido)
        fruta_solicitada = FrutaFicticia.objects.filter(id_pedido = pedido.pk)
        if fruta_en_pedido:
            resultados = []
        else:
            resultados = None
        
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
                "calibre": calibre
            }
            
            resultados.append(dic)
            
        resultados_fruta_solicitada = []
        for fruta_solicitada in fruta_solicitada:
    
            dic = {
                "kilos_solicitados": fruta_solicitada.kilos_solicitados,
                "calibre": fruta_solicitada.get_calibre_display(),
                "variedad": fruta_solicitada.get_variedad_display(),
                "calidad": fruta_solicitada.get_calidad_display(),
                "producto": fruta_solicitada.get_nombre_producto_display(),
            }
            
            resultados_fruta_solicitada.append(dic)
            
        serializer = PedidoExportacionSerializer(pedido_exportacion)
            
        return Response({
            "pedido_exportacion": serializer.data,
            "fruta_en_pedido": resultados,
            'fruta_solicitada' : resultados_fruta_solicitada
        })
            

# class FrutaPedidoViewSet(viewsets.ModelViewSet):
#     queryset = FrutaPedido.objects.all()
#     serializer_class = FrutaPedidoSerializer
