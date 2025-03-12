from django.shortcuts import get_list_or_404, render
from .models import *
from .serializers import *
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .models import Operario, SkillOperario
from django.shortcuts import get_object_or_404
from rest_framework.views import exception_handler
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from django_filters import rest_framework as django_filters
from djoser import email
from .filtros import *
from rest_framework import filters as rest_framework_filters


class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'email/password_reset.html'


def manejador_exepciones_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        if isinstance(exc, IntegrityError):
            return Response({'error': 'Viola una restricción de integridad.'},
                            status=status.HTTP_409_CONFLICT)
    return response

    
class ColosoViewSet(viewsets.ModelViewSet):

    queryset = Coloso.objects.all()
    serializer_class = ColosoSerializer
    permission_classes = [IsAuthenticated]
    
    
class TractorViewSet(viewsets.ModelViewSet):

    queryset = Tractor.objects.all()
    serializer_class = TractorSerializer
    permission_classes = [IsAuthenticated]
    
class TractorColosoViewSet(viewsets.ModelViewSet):

    queryset = TractorColoso.objects.all()
    serializer_class = TractorColosoSerializer
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, tractores_pk=None, pk=None):
        queryset = self.queryset.filter(tractor=tractores_pk, pk=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, tractores_pk=None, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tractor = Tractor.objects.get(pk=tractores_pk)
        serializer.save(tractor=tractor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, tractores_pk=None):
        queryset = self.queryset.filter(tractor=tractores_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class EtiquetasZplViewSet(viewsets.ModelViewSet):

    queryset = EtiquetasZpl.objects.all()
    serializer_class = EtiquetasZplSerializer
    permission_classes = [IsAuthenticated]
    
class ChoferViewSet(viewsets.ModelViewSet):

    queryset = Chofer.objects.all()
    serializer_class = ChoferSerializer
    permission_classes = [IsAuthenticated]
    
class CamionViewSet(viewsets.ModelViewSet):

    queryset = Camion.objects.all()
    serializer_class = CamionSerializer
    permission_classes = [IsAuthenticated]
    

class OperarioViewSet(viewsets.ModelViewSet):
    search_fields = ['skilloperario__tipo_operario', 'rut']
    filter_backends = (filters.DjangoFilterBackend, rest_framework_filters.SearchFilter)
    queryset = Operario.objects.all()
    serializer_class = OperarioSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = OperarioFilter
    
    
    @action(detail=True, methods=['post'], url_path='agregar-skill')
    def agregar_skill(self, request, pk=None):
        operario = self.get_object()
        skill_data = request.data
        print(f"SKILL DATA: {skill_data}")
        # Aquí deberías validar los datos de skill_data, por ejemplo, si es un ID válido.
        skill, created = SkillOperario.objects.get_or_create(operario=operario, **skill_data)
        if created:
            return Response({'status': 'skill agregado'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'skill ya existe'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='quitar-skill')
    def quitar_skill(self, request, pk=None):
        operario = self.get_object()
        skill_id = request.data.get('id')
        # Aquí deberías validar si el skill_id es válido y pertenece al operario.
        skill = get_object_or_404(SkillOperario, pk=skill_id, operario=operario)
        skill.delete()
        return Response({'status': 'skill quitado'}, status=status.HTTP_200_OK) 
    
class ContentTypeListView(generics.ListAPIView):
    serializer_class = ContentTypeSerializer
    queryset = ContentType.objects.all()
    
    