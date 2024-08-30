from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated


class PersonalizacionPerfilViewSet(viewsets.ModelViewSet):
    lookup_field='usuario'
    queryset = PersonalizacionPerfil.objects.all()
    serializer_class = PersonalizacionPerfilSerializer
    permission_classes = [IsAuthenticated]


### Permisos ###
from django.http import JsonResponse
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.text import slugify
from django.contrib.auth.models import Group


async def get_user_groups(request):
    jwt_authenticator = JWTAuthentication()
    try:
        header = jwt_authenticator.get_header(request)
        raw_token = jwt_authenticator.get_raw_token(header)
        validated_token = jwt_authenticator.get_validated_token(raw_token)
        user = await database_sync_to_async(jwt_authenticator.get_user)(validated_token)
    except (InvalidToken, TokenError) as e:
        return JsonResponse({'error': str(e)}, status=401)
    if not user or not user.is_active:
        return JsonResponse({'error': 'Usuario no autenticado o inactivo'}, status=401)
    groups = await database_sync_to_async(list)(user.groups.values_list('name', flat=True))
    group_dict = {slugify(name): name for name in groups}
    return JsonResponse({'groups': group_dict})

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated,]
