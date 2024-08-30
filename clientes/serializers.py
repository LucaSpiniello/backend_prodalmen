from rest_framework import serializers
from cities_light.models import City, Country
from .models import ClienteExportacion, SucursalClienteExportacion
from rest_framework import serializers
from .models import (
    ClienteMercadoInterno, Cta_Corriente, SucursalClienteMercado, RRLL,
    ClienteExportacion, SucursalClienteExportacion
)
from comunas.models import Region, Provincia, Comuna
from cities_light.models import Country, City

class ClienteMercadoInternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteMercadoInterno
        fields = '__all__'

class Cta_CorrienteSerializer(serializers.ModelSerializer):
    banco_nombre = serializers.SerializerMethodField()
    tipo_cuenta_label = serializers.SerializerMethodField()
    
    def get_banco_nombre(self, obj):
        return obj.get_banco_display()
    
    def get_tipo_cuenta_label(self, obj):
        return obj.get_tipo_cuenta_display()
    
    class Meta:
        model = Cta_Corriente
        fields = '__all__'

class SucursalClienteMercadoSerializer(serializers.ModelSerializer):
    region_nombre = serializers.SerializerMethodField()
    provincia_nombre = serializers.SerializerMethodField()
    comuna_nombre = serializers.SerializerMethodField()
    
    def get_region_nombre(self, obj):
        print(Region.objects.using('db_comunas').get(region_id = obj.region).region_nombre)
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
    class Meta:
        model = SucursalClienteMercado
        fields = '__all__'

class RRLLSerializer(serializers.ModelSerializer):
    class Meta:
        model = RRLL
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'country']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class ClienteExportacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClienteExportacion
        fields = '__all__'

class SucursalClienteExportacionSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.SerializerMethodField()
    ciudad_nombre = serializers.SerializerMethodField()
    
    def get_pais_nombre(self, obj):
        return Country.objects.filter(pk = obj.pais.pk).first().name
    
    def get_ciudad_nombre(self, obj):
        return City.objects.filter(pk = obj.ciudad.pk).first().name
        
    class Meta:
        model = SucursalClienteExportacion
        fields = '__all__'

        
        
class ClientesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rut_dni = serializers.CharField()
    razon_social = serializers.CharField()
    pais_ciudad = serializers.CharField()
    telefono = serializers.CharField()
    movil = serializers.CharField()
    nombre_fantasia = serializers.CharField()