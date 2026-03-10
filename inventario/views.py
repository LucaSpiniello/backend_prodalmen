
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
import random

from inventario.funciones import bodegas_filtradas
from .models import InventarioBodega, BinEnInventario
from bodegas.models import *
from .serializers import InventarioBodegaSerializer, BinEnInventarioSerializer, PDFDetalladoInventarioBodegaSerializer, PDFResumidoInventarioBodegaSerializer
from django.db.models import Q
from agrupacionbins.models import AgrupacionDeBinsBodegas, FrutaSobranteDeAgrupacion
from django.contrib.contenttypes.models import ContentType
from itertools import chain
from seleccion.models import BinSubProductoSeleccion
from .funciones import *

class InventarioBodegaViewSet(viewsets.ModelViewSet):
    queryset = InventarioBodega.objects.all()
    serializer_class = InventarioBodegaSerializer
    

    @action(detail=False, methods=['post'])
    def crear_inventario(self, request):
        tipo_inventario = request.data.get('tipo_inventario')

        if not tipo_inventario:
            return Response({"error": "Tipo Inventario es Requerido"}, status=status.HTTP_400_BAD_REQUEST)

        if tipo_inventario == '1':
            bodega = request.data.get('bodegas')

            if not bodega:
                return Response({"error": "Bodega es Requerido para Inventario por Bodega"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Obtener todos los registros excluyendo los que tienen procesado, ingresado y agrupado en True
                bins = BinBodega.objects.all().exclude(
                    Q(ingresado=True) |
                    Q(procesado=True) |
                    Q(agrupado=True) |
                    Q(estado_binbodega='-')
                )

                # Filtrar por las bodegas y calles
                bins_filtrados = []
                bins_filtrados.extend(filtrar_por_codigo_tarja_bin(bins, bodega))

                if not bins_filtrados:
                    return Response({"error": "No se encontraron bins para la Bodega %s."%(bodega)}, status=status.HTTP_404_NOT_FOUND)

                if len(bins_filtrados) < 3:
                    return Response({"error": "Se encontraron menos de 3 bins para el Inventario."}, status=status.HTTP_404_NOT_FOUND)

                # Crear el inventario
                inventario = InventarioBodega.objects.create(
                    tipo_inventario=tipo_inventario,
                    creado_por=request.user,
                    bodegas=bodega,
                    calles=''
                )

                for bin_obj in bins_filtrados:
                    # print(type(bin_obj))
                    # print(ContentType.objects.get_for_model(bin_obj))
                    BinEnInventario.objects.create(
                        inventario=inventario,
                        binbodega=BinBodega.objects.get(pk=bin_obj.pk),
                        validado=False,
                        validado_por=request.user
                    )

                serializer = InventarioBodegaSerializer(inventario)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if tipo_inventario == '2':
            calles = request.data.get('calles')
            bodegas = request.data.get('bodegas')
            
            if not calles or not tipo_inventario or not bodegas:
                return Response({"error": "calles, bodegas y tipo_inventario son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

            calle_list = [calle.strip() for calle in calles.split(',')]
            bodega_list = [bodega.strip() for bodega in bodegas.split(',')]

            try:
                # Obtener todos los registros excluyendo los que tienen procesado, ingresado y agrupado en True
                bins = BinBodega.objects.all().exclude(
                    Q(ingresado=True) |
                    Q(procesado=True) |
                    Q(agrupado=True) |
                    Q(estado_binbodega='-')
                )

                # Filtrar por las bodegas y calles
                bins_filtrados = []
                for bodega in bodega_list:
                    bins_filtrados.extend(filtrar_por_codigo_tarja_bin(bins, bodega))

                bins_filtrados = [bin for bin in bins_filtrados if bin.calle_bodega in calle_list]

                if not bins_filtrados:
                    return Response({"error": "No se encontraron bins para las bodegas y calles especificadas."}, status=status.HTTP_404_NOT_FOUND)

                if len(bins_filtrados) < 3:
                    return Response({"error": "Se encontraron menos de 3 bins para el Inventario."}, status=status.HTTP_404_NOT_FOUND)

                # Crear el inventario
                inventario = InventarioBodega.objects.create(
                    tipo_inventario=tipo_inventario,
                    creado_por=request.user,
                    bodegas=','.join(bodega_list),
                    calles=','.join(calle_list)
                )

                # Crear las relaciones en BinEnInventario con validado en False
                for bin_obj in bins_filtrados:
                    BinEnInventario.objects.create(
                        inventario=inventario,
                        binbodega=BinBodega.objects.get(pk=bin_obj.pk),
                        validado=False,
                        validado_por=request.user
                    )

                serializer = InventarioBodegaSerializer(inventario)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
        if tipo_inventario == '3':
            bodega_list = ['g1','g2','g3','g4','g5','g6','g7']
            
            try:
                # Obtener todos los registros excluyendo los que tienen procesado, ingresado y agrupado en True
                bins = BinBodega.objects.all().exclude(
                    Q(ingresado=True) |
                    Q(procesado=True) |
                    Q(agrupado=True) |
                    Q(estado_binbodega='-')
                )

                # Filtrar por las bodegas y calles
                bins_filtrados = []
                for bodega in bodega_list:
                    bins_filtrados.extend(filtrar_por_codigo_tarja_bin(bins, bodega))

                if not bins_filtrados:
                    return Response({"error": "No se encontraron bins para las bodegas y calles especificadas."}, status=status.HTTP_404_NOT_FOUND)

                # Crear el inventario
                inventario = InventarioBodega.objects.create(
                    tipo_inventario=tipo_inventario,
                    creado_por=request.user,
                    bodegas=','.join(bodega_list),
                    calles=''
                )

                # Crear las relaciones en BinEnInventario con validado en False
                for bin_obj in bins_filtrados:
                    BinEnInventario.objects.create(
                        inventario=inventario,
                        binbodega=BinBodega.objects.get(pk=bin_obj.pk),
                        validado=False,
                        validado_por=request.user
                    )

                serializer = InventarioBodegaSerializer(inventario)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        if tipo_inventario == '4':
            calles = request.data.get('calles')
            bodegas = request.data.get('bodegas')
            
            if not calles or not bodegas:
                return Response({"error": "Bodega es requerido."}, status=status.HTTP_400_BAD_REQUEST)

            # calle_list = [calle.strip() for calle in calles.split(',')]
            bodega_list = [bodega.strip() for bodega in bodegas.split(',')]
            
            calle_list = [int(x) for x in calles.split(',') if x.isdigit()]
        
            # Obtener un número aleatorio de la lista
            if calle_list:
                random_number = random.choice(calle_list)
            else:
                random_number = None
                
            try:
                # Obtener todos los registros excluyendo los que tienen procesado, ingresado y agrupado en True
                bins = BinBodega.objects.all().exclude(
                    Q(ingresado=True) |
                    Q(procesado=True) |
                    Q(agrupado=True) |
                    Q(estado_binbodega='-')
                )

                # Filtrar por las bodegas y calles
                bins_filtrados = []
                for bodega in bodega_list:
                    bins_filtrados.extend(filtrar_por_codigo_tarja_bin(bins, bodega))

                bins_filtrados = [bin for bin in bins_filtrados if bin.calle_bodega == str(random_number)]

                if not bins_filtrados:
                    return Response({"error": "No se encontraron bins para la bodega %s y calle %s."%(bodega,random_)}, status=status.HTTP_404_NOT_FOUND)

                if len(bins_filtrados) < 3:
                    return Response({"error": "Se encontraron menos de 3 bins para el Inventario."}, status=status.HTTP_404_NOT_FOUND)
                
                # Crear el inventario
                inventario = InventarioBodega.objects.create(
                    tipo_inventario=tipo_inventario,
                    creado_por=request.user,
                    bodegas=','.join(bodega_list),
                    calles='%s'%(random_number)
                )

                # Crear las relaciones en BinEnInventario con validado en False
                for bin_obj in bins_filtrados:
                    BinEnInventario.objects.create(
                        inventario=inventario,
                        binbodega=BinBodega.objects.get(pk=bin_obj.pk),
                        validado=False,
                        validado_por=request.user
                    )

                serializer = InventarioBodegaSerializer(inventario)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def pdf_resumido(self, request, pk=None):
        inventario = get_object_or_404(InventarioBodega, pk=pk)
        serializer = PDFResumidoInventarioBodegaSerializer(inventario)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def pdf_detallado(self, request, pk=None):
        inventario = get_object_or_404(InventarioBodega, pk=pk)
        serializer = PDFDetalladoInventarioBodegaSerializer(inventario)
        return Response(serializer.data)
        
  
        
class BinEnInventarioViewSet(viewsets.ModelViewSet):
    queryset = BinEnInventario.objects.all()
    serializer_class = BinEnInventarioSerializer
    
    def list(self, request, inventario_pk = None):
        inventario = InventarioBodega.objects.filter(pk = inventario_pk).first()
        bines = self.queryset.filter(inventario= inventario)
        serializer = self.get_serializer(bines, many = True)
        return Response(serializer.data)
