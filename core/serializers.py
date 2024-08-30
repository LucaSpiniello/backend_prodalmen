from rest_framework import serializers
from .models import *
from django.contrib.contenttypes.models import ContentType


class SkillOperarioSerializer(serializers.ModelSerializer):
    tipo_operario_label = serializers.SerializerMethodField()
    class Meta:
        model = SkillOperario
        fields = '__all__'
    
    def get_tipo_operario_label(self, obj):
        return obj.get_tipo_operario_display()
        

class OperarioSerializer(serializers.ModelSerializer):
    skills = SkillOperarioSerializer(many=True, read_only=True, source="skilloperario_set")
    class Meta:
        model = Operario
        fields = '__all__'  


class ColosoSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Coloso
        fields = '__all__'
        

class TractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tractor
        fields = '__all__'


class TractorColosoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TractorColoso
        fields = '__all__'


class EtiquetasZplSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtiquetasZpl
        fields = '__all__'




class CamionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camion
        fields = '__all__'


class ChoferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chofer
        fields = '__all__'



class ContentTypeSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    app_label = serializers.SerializerMethodField()

    def get_model(self, obj):
        return obj.model

    def get_app_label(self, obj):
        return obj.app_label

    class Meta:
        model = ContentType
        fields = ('id', 'app_label','model' )