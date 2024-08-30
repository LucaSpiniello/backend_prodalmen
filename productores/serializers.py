from rest_framework import serializers
from .models import *
from comunas.models import *



class ProductorSerializer(serializers.ModelSerializer):
    region_nombre = serializers.SerializerMethodField()
    provincia_nombre = serializers.SerializerMethodField()
    comuna_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Productor
        fields = '__all__'
        
    def get_region_nombre(self, obj):
        try:
            return Region.objects.using('db_comunas').get(region_id = obj.region).region_nombre
        except:
            return 'No Asignada'

    def get_provincia_nombre(self, obj):
        try:
            return Provincia.objects.using('db_comunas').get(provincia_id = obj.provincia).provincia_nombre
        except:
            return 'No Asignada'

    def get_comuna_nombre(self, obj):
        try:
            return Comuna.objects.using('db_comunas').get(comuna_id = obj.comuna).comuna_nombre
        except:
            return 'No Asignada'

