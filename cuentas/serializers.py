from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import Group

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id','email', 'first_name', 'is_staff', 'second_name', 'last_name', 'second_last_name', 'rut', 'celular', 'genero', 'fecha_nacimiento', 'image', 'comercializador')  # Añade aquí todos los campos necesarios
        

class PersonalizacionPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalizacionPerfil
        fields = '__all__'
        
        
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        
