from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AgrupacionDeBinsBodegas
from .models import *
from .serializers import AgrupacionDeBinsBodegasSerializer, FrutaSobranteDeAgrupacionSerializer
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Sum, F

class AgrupacionDeBinsBodegasViewSet(viewsets.ModelViewSet):
    queryset = AgrupacionDeBinsBodegas.objects.all()
    serializer_class = AgrupacionDeBinsBodegasSerializer

    @action(detail=True, methods=['post'])
    def agrupar(self, request, pk=None):
        agrupacion = self.get_object()
        print(f"Agrupando bins para la agrupación: {agrupacion}")

        # Asociaciones de bins en la agrupación
        bins_para_agrupacion = agrupacion.binsparaagrupacion_set.all()
        
        print("bins dentro de agrupacion", bins_para_agrupacion)
        
        
        print(bins_para_agrupacion)
        print(f"Bins en agrupación antes de agrupar: {bins_para_agrupacion.count()}")

        # Calculamos el peso total de los bins en la agrupación
        peso_total = sum(bpa.tarja.kilos_fruta for bpa in bins_para_agrupacion)
        print(f"Peso total de la agrupación: {peso_total}")

        if peso_total > 500:
            exceso = peso_total - 500
            print(f"Peso excedente a redistribuir: {exceso}")
            
            agrupacion.kilos_fruta -= exceso
            agrupacion.save()

            # Ordenamos los bins de mayor a menor peso para empezar a distribuir el exceso
            bins_ordenados = sorted(bins_para_agrupacion, key=lambda bpa: bpa.tarja.kilos_fruta, reverse=False)
            
            for bpa in bins_ordenados:
                bin = bpa.tarja
                print("soy el bin original", bin)
                print("soy la copia dentro de agrupacion", bpa)
                print(f"Trabajando con bin {bin.id}, peso actual: {bin.kilos_fruta}")
                
                if exceso <= 0:
                    print("No hay más exceso de peso para redistribuir.")
                    break
                
                if bin.kilos_fruta > exceso:
                    print(f"Reduciendo peso del bin {bin.id} en {exceso}kg")
                    bin.kilos_fruta -= exceso
                    
                    ct = ContentType.objects.get_for_model(bin)

                    # Verificar el tipo de bin para decidir qué campos incluir
                    if ct.model in ['bodegag6', 'bodegag7']:
                        FrutaSobranteDeAgrupacion.objects.create(
                            tarja=bin,
                            kilos_fruta=exceso,
                            calle_bodega=bin.calle_bodega,
                            estado_bin=bin.estado_bin,
                            fumigado=bin.fumigado,
                            fecha_fumigacion=bin.fecha_fumigacion
                        )
                    else:
                        FrutaSobranteDeAgrupacion.objects.create(
                            tarja=bin,
                            kilos_fruta=exceso,
                            calle_bodega=bin.calle_bodega,
                            calibre=bin.calibre,
                            variedad=bin.variedad,
                            estado_bin=bin.estado_bin,
                            fumigado=bin.fumigado,
                            fecha_fumigacion=bin.fecha_fumigacion
                        )
                    exceso = 0
                else:
                    print(f"El bin {bin.id} es completamente sobrante.")
                    exceso -= bin.kilos_fruta

                    # Verificar el tipo de bin para decidir qué campos incluir
                    if ct.model in ['bodegag6', 'bodegag7']:
                        FrutaSobranteDeAgrupacion.objects.create(
                            tarja=bin,
                            kilos_fruta=bin.kilos_fruta,
                            calle_bodega=bin.calle_bodega,
                            estado_bin=bin.estado_bin,
                            fumigado=bin.fumigado,
                            fecha_fumigacion=bin.fecha_fumigacion
                        )
                    else:
                        FrutaSobranteDeAgrupacion.objects.create(
                            tarja=bin,
                            kilos_fruta=bin.kilos_fruta,
                            calle_bodega=bin.calle_bodega,
                            calibre=bin.calibre,
                            variedad=bin.variedad,
                            estado_bin=bin.estado_bin,
                            fumigado=bin.fumigado,
                            fecha_fumigacion=bin.fecha_fumigacion
                        )
                    bin.kilos_fruta = 0
                
                bin.save()
                print(f"Peso del bin {bin.id} después de redistribuir: {bin.kilos_fruta}")
            

        return Response({'status': 'Bins agrupados con éxito'})

    @action(detail=True, methods=['post'])
    def add_bin(self, request, pk=None):
        agrupacion = self.get_object()
        lista_de_bins = request.data.get('bins', [])
        # print(lista_de_bins)
        
        kilos_fruta = 0
        for bin in lista_de_bins:
            bin_id = bin['id_binbodega']
            bin_type = bin['tipo_binbodega_id']
            
            
            
            try:
                content_type = ContentType.objects.get(id=bin_type)
            except ContentType.DoesNotExist:
                return Response({'status': 'Tipo de bin no válido'}, status=status.HTTP_400_BAD_REQUEST)
            if BinsParaAgrupacion.objects.filter(agrupacion=agrupacion, id_tarja=bin_id, tipo_tarja=content_type).exists():
                return Response({'status': 'Este bin ya está agregado a la agrupación'}, status=status.HTTP_409_CONFLICT)
            try:
                bin = content_type.get_object_for_this_type(pk=bin_id)
            except content_type.model_class().DoesNotExist:
                return Response({'status': 'Bin no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            bins_para_agrupacion = BinsParaAgrupacion(agrupacion=agrupacion, tipo_tarja=content_type, id_tarja=bin_id)
            
            if bins_para_agrupacion.tipo_tarja.model in ['bodegag1', 'bodegag2','bodegag1reproceso', 'bodegag2reproceso','bodegag3', 'bodegag4', 'agrupaciondebinsbodegas', ]:
                kilos_fruta += bins_para_agrupacion.tarja.kilos_fruta
            elif bins_para_agrupacion.tipo_tarja.model == 'frutasobrantedeagrupacion':
                if bins_para_agrupacion.tarja.tipo_tarja.model == 'frutasobrantedeagrupacion':
                    kilos_fruta += bins_para_agrupacion.tarja.tarja.kilos_fruta
                kilos_fruta += bins_para_agrupacion.tarja.kilos_fruta
                
            
            print("me estoy sumando", kilos_fruta)
            agrupacion.kilos_fruta = kilos_fruta
            agrupacion.save()
            
            bins_para_agrupacion.save()
            if hasattr(bin, 'estado_bin'):
                bin.estado_bin = '5' 
                bin.save()
        return Response({'status': 'Bins agregados exitosamente a la agrupación'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_bin(self, request, pk=None):
        agrupacion = self.get_object()
        bin_id = request.data.get('bin_id')
        bin_type = request.data.get('bin_type')
        model = ContentType.objects.get(model=bin_type).model_class()
        bin = get_object_or_404(model, pk=bin_id)
        content_type = ContentType.objects.get_for_model(bin)
        bin_para_agrupacion = BinsParaAgrupacion.objects.filter(
            agrupacion=agrupacion,
            id_tarja=bin_id,
            tipo_tarja=content_type
        )
        if not bin_para_agrupacion.exists():
            return Response({'status': 'Bin no está en la agrupación'}, status=status.HTTP_404_NOT_FOUND)

        bin_para_agrupacion.delete()
        if hasattr(bin, 'estado_bin'):
            bin.estado_bin = '1'
            bin.save()
        return Response({'status': 'Bin removido y estado restaurado con éxito'}, status=status.HTTP_200_OK)