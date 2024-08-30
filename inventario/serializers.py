from rest_framework import serializers
from cuentas.models import User
from inventario.funciones import *
from .models import InventarioBodega, BinEnInventario


class BinEnInventarioSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()
    calle = serializers.SerializerMethodField()
    validado_por_label = serializers.SerializerMethodField()
    kilos = serializers.SerializerMethodField()
    
    def get_codigo_tarja(self, obj):
        return obj.binbodega.codigo_tarja_bin
    
    def get_variedad(self, obj):
        variedad = obtener_variedad_inventario(obj)
        return variedad
    
    def get_calibre(self, obj):
        calibre = obtener_calibre_inventario(obj)
        return calibre
    
    def get_calle(self, obj):
        return obj.binbodega.binbodega.get_calle_bodega_display()
    
    def get_validado_por_label(self, obj):
        try: 
            return obj.validado_por.get_nombre()
        except:
            return ''
        
    def get_kilos(self, obj):
        return obj.binbodega.kilos_bin
        
    
    class Meta:
        model = BinEnInventario
        fields = '__all__'

class InventarioBodegaSerializer(serializers.ModelSerializer):
    # binsen_inventario = BinEnInventarioSerializer(many=True, read_only=True, source='bineninventario_set')
    tipo_inventario_label = serializers.SerializerMethodField()
    # bodegas_label = serializers.SerializerMethodField()
    # calles_label = serializers.SerializerMethodField()
    creado_por_label = serializers.SerializerMethodField()
    condicion_cierre = serializers.SerializerMethodField()
    
    def get_creado_por_label(self, obj):
        return f'{obj.creado_por.first_name} {obj.creado_por.last_name}'

    
    def get_tipo_inventario_label(self, obj):
        return obj.get_tipo_inventario_display()
    
    def get_condicion_cierre(self, obj):
        bins_sinvalidar = BinEnInventario.objects.filter(inventario=obj.pk, validado=False)
        if bins_sinvalidar.exists():
            if bins_sinvalidar.filter(observaciones=None).exists():
                return False
            else:
                return True
        else:
            return True

    class Meta:
        model = InventarioBodega
        fields = '__all__'
    


class PDFResumidoInventarioBodegaSerializer(serializers.ModelSerializer):
    tipo_inventario_label = serializers.SerializerMethodField()
    creado_por_label = serializers.SerializerMethodField()
    cantidad_bins_validados = serializers.SerializerMethodField()
    bins_no_validados = serializers.SerializerMethodField()
    kilos_por_variedad_y_calibre = serializers.SerializerMethodField()
    kilos_por_variedad = serializers.SerializerMethodField()
    kilos_por_calibre = serializers.SerializerMethodField()
    total_kilos = serializers.SerializerMethodField()
    kilos_por_calidad = serializers.SerializerMethodField()

    def get_tipo_inventario_label(self, obj):
        return obj.get_tipo_inventario_display()

    def get_creado_por_label(self, obj):
        return f'{obj.creado_por.first_name} {obj.creado_por.last_name}'

    def get_cantidad_bins_validados(self, obj):
        return BinEnInventario.objects.filter(inventario=obj.pk, validado=True).count()

    def get_bins_no_validados(self, obj):
        bins = BinEnInventario.objects.filter(inventario=obj.pk, validado=False)
        if bins.count() > 0:
            return BinEnInventarioSerializer(bins, many=True).data
        return 'No hay Bins No Validados'

    def get_kilos_por_variedad_y_calibre(self, obj):
        bins_en_inventario = BinEnInventario.objects.filter(inventario=obj.pk)
        kilos_agrupados = {}

        for bin_inventario in bins_en_inventario:
            binbodega = bin_inventario.binbodega
            variedad = binbodega.variedad
            calibre = binbodega.calibre
            kilos = binbodega.kilos_bin

            if variedad and calibre:
                key = f'Variedad {variedad} Calibre {calibre}'
                if key in kilos_agrupados:
                    kilos_agrupados[key] += kilos
                else:
                    kilos_agrupados[key] = kilos

        return [f'Total {key}: {value:.2f} Kilos' for key, value in kilos_agrupados.items()]

    def get_kilos_por_variedad(self, obj):
        bins_en_inventario = BinEnInventario.objects.filter(inventario=obj.pk)
        kilos_por_variedad = {}

        for bin_inventario in bins_en_inventario:
            binbodega = bin_inventario.binbodega
            variedad = binbodega.variedad
            kilos = binbodega.kilos_bin

            if variedad:
                if variedad in kilos_por_variedad:
                    kilos_por_variedad[variedad] += kilos
                else:
                    kilos_por_variedad[variedad] = kilos

        return [f'Total {variedad}: {kilos:.2f} Kilos' for variedad, kilos in kilos_por_variedad.items()]

    def get_kilos_por_calibre(self, obj):
        bins_en_inventario = BinEnInventario.objects.filter(inventario=obj.pk)
        kilos_por_calibre = {}

        for bin_inventario in bins_en_inventario:
            binbodega = bin_inventario.binbodega
            calibre = binbodega.calibre
            kilos = binbodega.kilos_bin

            if calibre:
                if calibre in kilos_por_calibre:
                    kilos_por_calibre[calibre] += kilos
                else:
                    kilos_por_calibre[calibre] = kilos

        return [f'Total Calibre {calibre}: {kilos:.2f} Kilos' for calibre, kilos in kilos_por_calibre.items()]

    def get_total_kilos(self, obj):
        bins_en_inventario = BinEnInventario.objects.filter(inventario=obj.pk)
        total_kilos = 0

        for bin_inventario in bins_en_inventario:
            binbodega = bin_inventario.binbodega
            total_kilos += binbodega.kilos_bin

        return f'{total_kilos:.2f}'

    def get_kilos_por_calidad(self, obj):
        bins_en_inventario = BinEnInventario.objects.filter(inventario=obj.pk, validado=True)
        kilos_por_calidad = {}

        for bin_inventario in bins_en_inventario:
            binbodega = bin_inventario.binbodega
            calidad = binbodega.calidad
            kilos = binbodega.kilos_bin

            if calidad:
                if calidad in kilos_por_calidad:
                    kilos_por_calidad[calidad] += kilos
                else:
                    kilos_por_calidad[calidad] = kilos

        return [f'Total Calidad {calidad}: {kilos:.2f} Kilos' for calidad, kilos in kilos_por_calidad.items()]

    class Meta:
        model = InventarioBodega
        fields = '__all__'

class PDFDetalladoInventarioBodegaSerializer(serializers.ModelSerializer):
    bins = serializers.SerializerMethodField()
    total_kilos = serializers.SerializerMethodField()
    tipo_inventario_label = serializers.SerializerMethodField()
    creado_por_label = serializers.SerializerMethodField()
    cantidad_bins_validados = serializers.SerializerMethodField()
    cantidad_bins_no_validados = serializers.SerializerMethodField()

    class Meta:
        model = InventarioBodega
        fields = '__all__'

    def get_bins(self, obj):
        bins = BinEnInventario.objects.filter(inventario=obj.pk, validado=False)
        if bins.count() > 0:
            return BinEnInventarioSerializer(bins, many=True).data
        return 'No hay Bins'

    def get_total_kilos(self, obj):
        bins_en_inventario = BinEnInventario.objects.filter(inventario=obj.pk)
        total_kilos = 0

        for bin_inventario in bins_en_inventario:
            binbodega = bin_inventario.binbodega
            total_kilos += binbodega.kilos_bin

        return f'{total_kilos:.2f}'

    def get_tipo_inventario_label(self, obj):
        return obj.get_tipo_inventario_display()

    def get_creado_por_label(self, obj):
        return f'{obj.creado_por.first_name} {obj.creado_por.last_name}'

    def get_cantidad_bins_validados(self, obj):
        return BinEnInventario.objects.filter(inventario=obj.pk, validado=True).count()

    def get_cantidad_bins_no_validados(self, obj):
        return BinEnInventario.objects.filter(inventario=obj.pk, validado=False).count()