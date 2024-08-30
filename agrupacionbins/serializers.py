from rest_framework import serializers
from .models import *

class FrutaSobranteDeAgrupacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrutaSobranteDeAgrupacion
        fields = '__all__'
        

class AgrupacionDeBinsBodegasSerializer(serializers.ModelSerializer):
    fruta_sobrante = FrutaSobranteDeAgrupacionSerializer(read_only=True)
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = AgrupacionDeBinsBodegas
        fields = [
            'id', 'bins_agrupados', 'codigo_tarja', 'registrado_por', 
            'fruta_sobrante', 'transferir_bodega', 'kilos_fruta', 
            'tipo_patineta', 'agrupamiento_ok', 'registrado_por_nombre'
        ]

    def get_registrado_por_nombre(self, obj):
        usuario_registrador = f'{obj.registrado_por.first_name} {obj.registrado_por.last_name}'
        if usuario_registrador:
            return usuario_registrador
        else:
            return 'No lo ha registrado nadie'