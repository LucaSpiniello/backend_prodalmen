from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from .serializers import *
from pedidos.models import Pedido
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from django.db.models import *




class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.all()
    serializer_class = DespachoSerializer

    @action(detail=True, methods=['post'])
    def crear_despacho(self, request, pk=None):
        pedido = get_object_or_404(Pedido, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(pedido=pedido, creado_por=request.user)
        return Response(serializer.data)
     
    @action(detail=False, methods=['patch'])
    def actualizar_despacho(self, request):
        pk_pedido = request.query_params.get('pedido')
        pedido = get_object_or_404(Pedido, pk=pk_pedido)
        despacho = get_object_or_404(Despacho, pedido=pedido)
        
        despacho_serializer = DespachoSerializer(despacho, data=request.data, partial=True)
        if despacho_serializer.is_valid():
            despacho_serializer.save()
        
            return Response(despacho_serializer.data)
        else:
            errors = despacho_serializer.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail = False, methods = ['GET'], url_path='detalle_despacho')
    def detalle_despacho(self, request):
        pedido = request.query_params.get('pedido')
        # Obtener el pedido y despacho
        pedido = get_object_or_404(Pedido, pk=pedido)
        despacho = get_object_or_404(Despacho, pedido=pedido)
        
        despacho_serializer = DespachoSerializer(despacho)
        return Response(despacho_serializer.data)
    
    @action(detail=True, methods=['POST'])
    def agregar_fruta(self, request, pk=None):
        despacho = get_object_or_404(Despacho, pk=pk)
        frutas = request.data.get('frutas', [])

        # Antes de iniciar el proceso, asegura que puedes cumplir con todas las solicitudes de frutas.
        for fruta in frutas:
            id_fruta = fruta.get('id_fruta')
            tipo_fruta = fruta.get('tipo_fruta')
            cantidad = fruta.get('cantidad')
            pedido_id = fruta.get('pedido')

            ct = ContentType.objects.get_for_id(tipo_fruta)
            frutas_en_pedido = FrutaEnPedido.objects.filter(tipo_fruta=ct, id_fruta=id_fruta, pedido=pedido_id)

            total_disponible = frutas_en_pedido.aggregate(Sum('cantidad'))['cantidad__sum'] or 0
            if total_disponible < cantidad:
                return Response({"error": "Insufficient stock for the fruit requested."}, status=status.HTTP_404_NOT_FOUND)

        # Si todo está en orden, procedemos a crear los DespachoProducto.
        for fruta in frutas:
            id_fruta = fruta.get('id_fruta')
            tipo_fruta = fruta.get('tipo_fruta')
            cantidad = fruta.get('cantidad')
            pedido_id = fruta.get('pedido')

            ct = ContentType.objects.get_for_id(tipo_fruta)
            frutas_en_pedido = FrutaEnPedido.objects.filter(tipo_fruta=ct, id_fruta=id_fruta, pedido=pedido_id)

            for fruta_en_pedido in frutas_en_pedido:
                DespachoProducto.objects.create(
                    despacho=despacho,
                    fruta_en_pedido=fruta_en_pedido,
                    cantidad=cantidad 
                )

        return Response({"message": "Frutas added successfully to despacho."}, status=status.HTTP_201_CREATED)

    
    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
class FrutaEnDespacho(viewsets.ModelViewSet):
    queryset = DespachoProducto.objects.all()
    serializer_class = DespachoProductoSerializer
    
    def list(self, request, despacho_pk=None):
        queryset = self.queryset.filter(despacho = despacho_pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    
    