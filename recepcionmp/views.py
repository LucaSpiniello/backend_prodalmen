from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, generics, filters
from .models import *
from .serializers import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import *
import json
from django_filters import rest_framework as django_filters
from cuentas.models import PersonalizacionPerfil
from rest_framework.decorators import action



class GuiaRecepcionMPViewSet(viewsets.ModelViewSet):
    queryset = GuiaRecepcionMP.objects.all()
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                guias = GuiaRecepcionMP.objects.filter(fecha_creacion__year = anio)
                return guias
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return GuiaRecepcionMPSerializer
        return DetalleGuiaRecepcionMPSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['GET'], url_path='get_by_comercializador')
    def get_by_comercializador(self, request):
        comercializador = request.query_params.get('comercializador', None)
        print("Comercializador: ", comercializador)
        guias = self.get_queryset().filter(comercializador__nombre=comercializador)
        serializer = self.get_serializer(guias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'], url_path='get_all_kilos_lotes_recepcionados')
    def get_all_kilos_lotes_recepcionados(self, request, recepcionmp_pk=None):
        
        user = self.request.user
        anio = PersonalizacionPerfil.objects.get(usuario= user).anio
        queryset = RecepcionMp.objects.filter(fecha_creacion__year = anio)
        # only include the ones that are not in estado_recepcion 6,7
        queryset = queryset.exclude(estado_recepcion__in=['1', '2', '3', '4', '5'])
        total_kilos_prodalmen = 0
        total_kilos_pacific = 0
        # filer the query set by comercializador ( Prodalmen and Pacific Nut)
        queryset_prodalmen = queryset.filter(guiarecepcion__comercializador__nombre='Prodalmen')
        queryset_pacificnut = queryset.filter(guiarecepcion__comercializador__nombre='Pacific Nut')
        
        # filter the query set by guiarecepcion__estado_recepcion 6,7
        queryset_prodalmen = queryset_prodalmen.exclude(estado_recepcion__in=['1', '2', '3', '4', '5'])
        queryset_pacificnut = queryset_pacificnut.exclude(estado_recepcion__in=['1', '2', '3', '4', '5'])
        
        for lote in queryset_prodalmen:
            kilos_brutos = lote.kilos_brutos_1 + lote.kilos_brutos_2
            kilos_tara = lote.kilos_tara_1 + lote.kilos_tara_2
            # Calcular peso de los envases
            kilos_envases = 0
            for envase in lote.envasesguiarecepcionmp_set.all():
                kilos_envases += envase.envase.peso * envase.cantidad_envases
            kilos_neto = kilos_brutos - kilos_tara - kilos_envases
            total_kilos_prodalmen += kilos_neto
        for lote in queryset_pacificnut:
            kilos_brutos = lote.kilos_brutos_1 + lote.kilos_brutos_2
            kilos_tara = lote.kilos_tara_1 + lote.kilos_tara_2
            # Calcular peso de los envases
            kilos_envases = 0
            for envase in lote.envasesguiarecepcionmp_set.all():
                kilos_envases += envase.envase.peso * envase.cantidad_envases
            kilos_neto = kilos_brutos - kilos_tara - kilos_envases
            total_kilos_pacific += kilos_neto
        # return the total kilos for each comercializador
        data = {
            'total_kilos_prodalmen': total_kilos_prodalmen,
            'total_kilos_pacificnut': total_kilos_pacific
        }
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path='editar_productor')
    def editar_productor(self, request):
        """
        Asigna un productor diferente a una guía de recepción.
        Recibe el id de la guía y el id del nuevo productor.
        """
        try:
            print("LLEGAAA")
            guia_id = request.data.get('guia_id')
            productor_id = request.data.get('productor_id')
            
            if not guia_id:
                return Response(
                    {"error": "El campo 'guia_id' es requerido"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not productor_id:
                return Response(
                    {"error": "El campo 'productor_id' es requerido"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar la guía por ID
            guia = get_object_or_404(GuiaRecepcionMP, pk=guia_id)
            print(f'Guía encontrada: {guia.pk}, Productor actual: {guia.productor.nombre} (ID: {guia.productor.pk})')
            
            # Buscar el nuevo productor por ID
            from productores.models import Productor
            nuevo_productor = get_object_or_404(Productor, pk=productor_id)
            print(f'Nuevo productor encontrado: {nuevo_productor.nombre} (ID: {nuevo_productor.pk})')
            
            # Asignar el nuevo productor a la guía
            productor_anterior = guia.productor
            guia.productor = nuevo_productor
            print(f'Se asignó el productor {nuevo_productor.nombre} a la guía {guia_id}')
            guia.save()
            print(f'Se cambió el productor de "{productor_anterior.nombre}" (ID: {productor_anterior.pk}) a "{nuevo_productor.nombre}" (ID: {nuevo_productor.pk}) para la guía {guia_id}')
            
            # Serializar y devolver la guía actualizada
            serializer = self.get_serializer(guia)
            return Response({
                "message": "Productor asignado correctamente a la guía",
                "guia": serializer.data,
                "productor_anterior": {
                    "id": productor_anterior.pk,
                    "nombre": productor_anterior.nombre
                },
                "productor_nuevo": {
                    "id": nuevo_productor.pk,
                    "nombre": nuevo_productor.nombre
                }
            }, status=status.HTTP_200_OK)
            
        except GuiaRecepcionMP.DoesNotExist:
            return Response(
                {"error": "Guía de recepción no encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Productor.DoesNotExist:
            return Response(
                {"error": "Productor no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error al asignar el productor: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        
    
class RecepcionMpViewSet(viewsets.ModelViewSet):
    queryset = RecepcionMp.objects.all()
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = RecepcionMp.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return RecepcionMpSerializer
        return DetalleRecepcionMpSerializer
    
    def retrieve(self, request, recepcionmp_pk=None, pk=None):
        guiarecepcion = get_object_or_404(GuiaRecepcionMP, pk=recepcionmp_pk)
        queryset = RecepcionMp.objects.get(guiarecepcion=guiarecepcion, pk=pk)
        serializer = DetalleRecepcionMpSerializer(queryset)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        envases = request.data.get('envases', [])
        serializador_envases = EnvasesGuiaRecepcionMpRegistroSerializer(data=envases, many=True)
        serializador_envases.is_valid(raise_exception=True)
        serializador_envases.save(recepcionmp=serializer.save())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, recepcionmp_pk=None):
        queryset = self.queryset.filter(guiarecepcion=recepcionmp_pk)
        serializer = RecepcionMpSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def lotes_pendientes(self, request, recepcionmp_pk=None):
        queryset = self.queryset.filter(guiarecepcion=recepcionmp_pk).exclude(estado_recepcion__in=['6', '7', '4'],)
        serializer = RecepcionMpSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def lotes_aprobados(self, request, recepcionmp_pk=None):
        queryset = self.queryset.filter(guiarecepcion=recepcionmp_pk, estado_recepcion__in=['6', '7'])
        serializer = RecepcionMpSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def lotes_rechazados(self, request, recepcionmp_pk=None):
        queryset = self.queryset.filter(guiarecepcion=recepcionmp_pk, estado_recepcion__in=['4',])
        rechazos = LoteRecepcionMpRechazadoPorCC.objects.filter(recepcionmp__in=queryset.values_list('pk', flat=True))
        serializador_rechazo = LoteRechazadoSerializer(rechazos, many=True)
        return Response(serializador_rechazo.data)
    
    @action(detail=False, methods=['PATCH', 'PUT'])
    def actualizar_lote_rechazado(self, request, recepcionmp_pk=None):
        queryset = self.queryset.filter(guiarecepcion=recepcionmp_pk, estado_recepcion__in=['4',])
        rechazos = LoteRecepcionMpRechazadoPorCC.objects.filter(recepcionmp__in=queryset.values_list('pk', flat=True))
        
        for rechazo in rechazos:
            data = request.data.get(str(rechazo.pk), {})
            serializer = LoteRechazadoSerializer(rechazo, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        updated_rechazos = LoteRecepcionMpRechazadoPorCC.objects.filter(recepcionmp__in=queryset.values_list('pk', flat=True))
        serializador_rechazo_actualizado = LoteRechazadoSerializer(updated_rechazos, many=True)
        return Response(serializador_rechazo_actualizado.data, status=status.HTTP_200_OK)
    
class EnvasesMpViewSet(viewsets.ModelViewSet):
    queryset = EnvasesMp.objects.all()
    serializer_class = EnvasesMpSerializer
    permission_classes = [IsAuthenticated,]
    
    # def get_queryset(self):
    #     user = self.request.user
    #     try:
    #         anio = PersonalizacionPerfil.objects.get(usuario= user).anio
    #         if anio == 'Todo':
    #             return self.queryset
    #         else:
    #             qs = EnvasesMp.objects.filter(fecha_creacion__year = anio)
    #             return qs
    #     except:
    #         return self.queryset

class EnvasesGuiaMPViewSet(viewsets.ModelViewSet):
    queryset = EnvasesGuiaRecepcionMp.objects.all()
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        """
        Este método es llamado por todas las acciones que listan o manipulan colecciones de objetos.
        Se modifica para filtrar el queryset según los parámetros de URL.
        """
        queryset = super().get_queryset()
        recepcionmp_pk = self.kwargs.get('recepcionmp_pk')
        lote_pk = self.kwargs.get('lote_pk')

        if lote_pk:
            queryset = queryset.filter(recepcionmp__pk=lote_pk)
        elif recepcionmp_pk:
            queryset = queryset.filter(recepcionmp__pk=recepcionmp_pk)

        return queryset

    
    def get_serializer_class(self): 
        return EnvasesGuiaRecepcionSerializer  
    
    # @action(detail=False, methods=['POST'], url_path='creacion-envases')
    # def creacion_envases_lote_recepcionado(self, request, recepcionmp_pk=None, lote_pk=None):
    #     envases_lote = request.data.get('envases', '[]')
    #     guia = GuiaRecepcionMP.objects.filter(pk = recepcionmp_pk).first()
    #     lote_recepcion = RecepcionMp.objects.filter(guiarecepcion = guia).first()
        
    #     if not envases_lote:
    #         return Response({"error": "No envases data provided"}, status=status.HTTP_400_BAD_REQUEST)

    #     created_envases = []
    #     for envase_data in envases_lote:
    #         envase = EnvasesGuiaRecepcionMp.objects.update_or_create(
    #             envase_id=int(envase_data.get('envase')),
    #             recepcionmp=lote_recepcion,  # Usar lote_pk directamente
    #             variedad= envase_data.get('variedad'),
    #             tipo_producto= envase_data.get('tipo_producto'),
    #             cantidad_envases= envase_data.get('cantidad_envases')
    #         )
    #         # Añadir el envase serializado a la lista de resultados
    #         serializer = self.get_serializer(envase)
    #         created_envases.append(serializer.data)

    #     # Devolver los datos de los envases creados/actualizados
    #     return Response(created_envases, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['POST'], url_path='creacion-envases')
    def creacion_envases_lote_recepcionado(self, request, recepcionmp_pk=None, lote_pk=None):
        envases_lote = request.data.get('envases', '[]')
        guia = GuiaRecepcionMP.objects.filter(pk=recepcionmp_pk).first()
        lote_recepcion = RecepcionMp.objects.filter(guiarecepcion=guia).first()
        
        if not envases_lote:
            return Response({"error": "No envases data provided"}, status=status.HTTP_400_BAD_REQUEST)
        
         # ID de envases recibidos del front-end
        envase_ids_in_request = [int(envase.get('envase')) for envase in envases_lote]

        # Encontrar y eliminar envases que no están en la lista recibida del front-end
        EnvasesGuiaRecepcionMp.objects.filter(recepcionmp=lote_recepcion).exclude(envase__in=envase_ids_in_request).delete()

        created_envases = []
        for envase_data in envases_lote:
            envase, created = EnvasesGuiaRecepcionMp.objects.update_or_create(
                envase_id=int(envase_data.get('envase')),
                recepcionmp=lote_recepcion,  # Usar lote_pk directamente
                defaults={  # Asegúrate de pasar los campos que se deben actualizar o crear como parte de 'defaults'
                    'variedad': envase_data.get('variedad'),
                    'tipo_producto': envase_data.get('tipo_producto'),
                    'cantidad_envases': envase_data.get('cantidad_envases')
                }
            )
            # Añadir el envase serializado a la lista de resultados
            serializer = self.get_serializer(envase)
            created_envases.append(serializer.data)

        # Devolver los datos de los envases creados/actualizados
        return Response(created_envases, status=status.HTTP_201_CREATED)

        
        
    
    def create(self, request, *args, **kwargs):
        envase_guia = request.data.get('envases', '[]')
        envases = json.loads(envase_guia)
        envase_ids_in_request = [envase.get('envase') for envase in envases]
        envase_instance = EnvasesGuiaRecepcionMp.objects.filter(envase__in=envase_ids_in_request)
        envase_instance_list = set(envase_instance.values_list( 'id', flat=True))
        
        
        for envase in envases:
            recepcionmp = RecepcionMp.objects.get(pk=envase['recepcionmp'])
            envases_en_recepcionmp = recepcionmp.envasesguiarecepcionmp_set.filter(recepcionmp=envase['recepcionmp'])
            envases_en_recepcionmp_list = set(envases_en_recepcionmp.values_list('id', flat=True))
            eliminables =  set(envases_en_recepcionmp_list) - set(envase_instance_list)
            recepcionmp.envasesguiarecepcionmp_set.filter(pk__in=eliminables).delete()
            envase_existente = EnvasesGuiaRecepcionMp.objects.filter(recepcionmp=envase['recepcionmp'], envase=envase['envase']).first()
            if envase_existente:
                pass
            else:
                serializer = self.get_serializer(data=envase)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Envases creados o actualizados correctamente", status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """
        La acción 'list' se personaliza para manejar adecuadamente los parámetros anidados de URL.
        """
        queryset = self.get_queryset()
        serializer =  EnvasesGuiaRecepcionMpSerializer(queryset, many = True)
        return Response(serializer.data)
    
    
# class LoteRechazadoViewset(viewsets.ModelViewSet):
#     queryset = LoteRecepcionMpRechazadoPorCC.objects.all()
#     serializer_class = LoteRechazadoSerializer  
#     permission_classes = [IsAuthenticated,]
    
#     def get_queryset(self):
#         user = self.request.user
#         try:
#             anio = PersonalizacionPerfil.objects.get(usuario= user).anio
#             if anio == 'Todo':
#                 return self.queryset
#             else:
#                 qs = LoteRecepcionMpRechazadoPorCC.objects.filter(fecha_creacion__year = anio)
#                 return qs
#         except:
#             return self.queryset
        
#     def list(self, request, recepcionmp_pk=None):
#         queryset = self.queryset.filter(recepcionmp=recepcionmp_pk)
#         serializer = LoteRechazadoSerializer(queryset, many=True)
#         return Response(serializer.data)