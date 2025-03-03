from re import sub
from django.shortcuts import render
from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
#from agrupaciondebins.models import *
from agrupacionbins.models import AgrupacionDeBinsBodegas, FrutaSobranteDeAgrupacion
from bodegas.funciones import *
from seleccion.models import BinSubProductoSeleccion
from .models import *
from .serializers import *
from .filtros import *
from django.shortcuts import get_list_or_404, get_object_or_404
from cuentas.models import PersonalizacionPerfil
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.http import JsonResponse
from itertools import chain
from django.db.models import OuterRef, Subquery, Count, Q
from django_filters import rest_framework as django_filters


class PatioTechadoExteriorViewset(viewsets.ModelViewSet):
    lookup_field = 'id_recepcion'
    queryset = PatioTechadoExterior.objects.all()
    serializer_class = PatioTechadoExteriorSerializer
    permission_classes = [IsAuthenticated,]
  
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario=user).anio
            if anio == 'Todo':
                queryset = self.queryset
            else:
                queryset = PatioTechadoExterior.objects.filter(fecha_creacion__year=anio)

            return queryset
        except PersonalizacionPerfil.DoesNotExist:
            return self.queryset
  
    def retrieve(self, request, id_recepcion=None, pk=None):
        guiapatio = get_object_or_404(PatioTechadoExterior, id_recepcion=id_recepcion)
        serializer = self.get_serializer(guiapatio)
        return Response(serializer.data)

    def list(self, request, guia_patio_pk=None):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail = False, methods = ['GET'])
    def lotes_para_produccion(self, request):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario=user).anio
            if anio == 'Todo':
                queryset = self.queryset
            else:
                queryset = PatioTechadoExterior.objects.filter(fecha_creacion__year=anio)
            
            # Subconsulta para verificar si hay algún envase con estado '2' relacionado con el lote
            subquery = EnvasesPatioTechadoExt.objects.filter(
                guia_patio=OuterRef('pk'),
                estado_envase__in = ['0', '1']  # Cambiar a '1' para envases en estado '1'
            ).values('guia_patio')
            
            
            subquery_cc = CCRecepcionMateriaPrima.objects.filter(
                recepcionmp = OuterRef('id_recepcion'),
                estado_aprobacion_cc = '1'
            ).values('recepcionmp')
            
            # Filtrar solo los lotes que tienen algún envase con estado '1'
            queryset = queryset.filter(pk__in=Subquery(subquery), id_recepcion__in =Subquery(subquery_cc))
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except PersonalizacionPerfil.DoesNotExist:
            return self.queryset
        
  
class EnvasesPatioTechadoExteriorViewset(viewsets.ModelViewSet):
  queryset = EnvasesPatioTechadoExt.objects.all()
  serializer_class = EnvasesPatioTechadoExtSerializer
  permission_classes = [IsAuthenticated,]
  
  def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario = user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = EnvasesPatioTechadoExt.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset

  def retrieve(self, request, guia_patio_pk=None, pk=None):
    guiapatio = get_object_or_404(PatioTechadoExterior, pk=guia_patio_pk)
    queryset = get_object_or_404(self.get_queryset(),guia_patio=guiapatio, pk=pk)
    serializer = self.get_serializer(queryset)
    return Response(serializer.data)

  def list(self, request, guia_patio_pk=None):
    guiapatio = get_object_or_404(PatioTechadoExterior, pk=guia_patio_pk)
    queryset = get_list_or_404(self.get_queryset(), guia_patio=guiapatio)
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)


class BinBodegaViewSet(viewsets.ModelViewSet):
    queryset = BinBodega.objects.all()
    serializer_class = BinBodegaSerializer
    permission_classes = [IsAuthenticated,]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BinBodegaFilter
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario=user).anio
            if anio == 'Todo':
                queryset = BinBodega.objects.all()
            else:
                queryset = BinBodega.objects.filter(fecha_creacion__year=anio)
            # Excluir los objetos con ingresado=True y procesado=True
            queryset = queryset.exclude(Q(ingresado=True) |
                Q(procesado=True) |
                Q(agrupado=True) |
                Q(estado_binbodega='-')
            )
            return queryset
        except PersonalizacionPerfil.DoesNotExist:
            return BinBodega.objects.all().exclude(
                Q(ingresado=True) |
                Q(procesado=True) |
                Q(agrupado=True) |
                Q(estado_binbodega='-')
            )
        
    @action(detail=False, methods=['get'], url_path='buscar-por-tarja')
    def buscar_por_tarja(self, request):
        codigo_tarja = request.query_params.get('codigo_tarja_bin')
        if not codigo_tarja:
            return Response({"error": "Debe proporcionar el parámetro 'codigo_tarja_bin'"}, status=400)
        
        bins = BinBodega.objects.all()
        bin_bodega = None
        for bin in bins:
            if bin.codigo_tarja_bin == codigo_tarja:
                bin_bodega = bin
                break

        if not bin_bodega:
            return Response({"error": "No se encontró ningún bin con ese código de tarja"}, status=404)

        serializer = DetalleBinBodegaSerializer(bin_bodega)
        return Response(serializer.data)
        
    def filter_queryset(self, queryset):
        """
        Apply the default filtering and then apply custom filters.
        """
        queryset = super().filter_queryset(queryset)
        filters = {
            'bodegas': self.request.GET.get('bodegas'),
            'calidad': self.request.GET.get('calidad'),
            'variedad': self.request.GET.get('variedad'),
            'calibre': self.request.GET.get('calibre')
        }
        if filters['bodegas']:
            queryset = self.filter_by_bodegas(queryset, filters['bodegas'])
        if filters['calidad']:
            queryset = self.filter_by_calidad(queryset, filters['calidad'])
        if filters['variedad']:
            queryset = self.filter_by_variedad(queryset, filters['variedad'])
        if filters['calibre']:
            queryset = self.filter_by_calibre(queryset, filters['calibre'])
        return queryset
    
    def filter_by_bodegas(self, queryset, bodegas):
        bodegas_list = bodegas.split(',')
        filtered_queryset = []
        for bodega in bodegas_list:
            filtered_queryset.extend([obj for obj in queryset if obj.codigo_tarja_bin and obj.codigo_tarja_bin.lower().startswith(bodega.lower())])
            
        return list(set(filtered_queryset)) 
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return BinBodegaSerializer
        return DetalleBinBodegaSerializer
    
    def filter_by_calidad(self, queryset, calidad):
        filtered_queryset = [obj for obj in queryset if obj.calidad and calidad.lower() in obj.calidad.lower()]
        return queryset.filter(id__in=[obj.id for obj in filtered_queryset])

    def filter_by_variedad(self, queryset, variedad):
        filtered_queryset = [obj for obj in queryset if obj.variedad and variedad.lower() in obj.variedad.lower()]
        return queryset.filter(id__in=[obj.id for obj in filtered_queryset])

    def filter_by_calibre(self, queryset, calibre):
        filtered_queryset = [obj for obj in queryset if obj.calibre and calibre.lower() in obj.calibre.lower()]
        return queryset.filter(id__in=[obj.id for obj in filtered_queryset])

    @action(detail=False, methods=['PUT', 'PATCH'])
    def bodegas_update(self, request):
        tipo_bodega = request.data.get('tipo_bodega')
        codigo_tarja = request.data.get('codigo_tarja')
        calle = request.data.get('calle')
        id_tarja = request.data.get('id_tarja')
        
        
        ct = ContentType.objects.get_for_id(tipo_bodega)
        if ct.model == 'bodegag1':
            BodegaG1.objects.filter(produccion__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag1reproceso':
            BodegaG1Reproceso.objects.filter(reproceso__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag2':
            BodegaG2.objects.filter(produccion__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag2reproceso':
            BodegaG2Reproceso.objects.filter(reproceso__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag3':
            BodegaG3.objects.filter(seleccion__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag4':
            BodegaG4.objects.filter(seleccion__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'binsubproductoseleccion':
            BinSubProductoSeleccion.objects.filter(codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag5':
            BodegaG5.objects.filter(seleccion__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag6':
            BodegaG6.objects.filter(programa__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'bodegag7':
            BodegaG7.objects.filter(proceso__codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'agrupacionbinbodega':
            AgrupacionDeBinsBodegas.objects.filter(codigo_tarja = codigo_tarja).update(calle_bodega = calle)
        elif ct.model == 'sobranteagrupacion':
            FrutaSobranteDeAgrupacion.objects.filter(codigo_tarja = codigo_tarja).update(calle_bodega = calle)
            
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path='pdf_bodegas/(?P<prefix>[^/.]+)')
    def pdf_bodegas(self, request, prefix=None):
        # Obtener todos los registros
        bins = BinBodega.objects.all()
        
        normalized_prefix = prefix.lower()


        bins_filtrados = [
            bin for bin in bins 
            if bin.codigo_tarja_bin and bin.codigo_tarja_bin.lower().startswith(normalized_prefix)
            and not bin.procesado and not bin.ingresado and not bin.agrupado
        ]

        resultados = []
        for bin in bins_filtrados:
            dic = {
                "codigo_tarja": bin.codigo_tarja_bin,
                "programa": bin.origen_tarja,
                "calibre": bin.calibre,
                "variedad": bin.variedad,
                "calidad": bin.calidad,
                "kilos": bin.kilos_bin,
                "bodega": prefix
                
            }
            resultados.append(dic)
        
        return Response(resultados, status=status.HTTP_200_OK)

    
    
  