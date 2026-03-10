from rest_framework import serializers

from controlcalidad.models import *
from .models import *
from django.contrib.contenttypes.models import *
from django.db.models import Max


class CCGuiaInternaSerializer(serializers.ModelSerializer):
  class Meta:
    model = CCGuiaInterna
    fields = '__all__'
    
class EnvasesPatioTechadoExtSerializer(serializers.ModelSerializer):
  estado_envase_label = serializers.SerializerMethodField()
  variedad = serializers.SerializerMethodField()
  
  class Meta:
    model = EnvasesPatioTechadoExt
    fields = '__all__'
  
      
  def get_estado_envase_label(self, obj):
    return obj.get_estado_envase_display()
  
  def get_variedad(self, obj):
    return obj.get_variedad_display()
    
class PatioTechadoExteriorSerializer(serializers.ModelSerializer):
  envases = EnvasesPatioTechadoExtSerializer(many=True, read_only=True, source='envasespatiotechadoext_set')
  variedad = serializers.SerializerMethodField()
  estado_lote_label = serializers.SerializerMethodField()
  ubicacion_label = serializers.SerializerMethodField()
  numero_lote = serializers.SerializerMethodField()
  productor = serializers.SerializerMethodField()
  control_calidad = serializers.SerializerMethodField()
  humedad = serializers.SerializerMethodField()
  cantidad_muestras = serializers.SerializerMethodField()
  rendimiento = serializers.SerializerMethodField()
  
  class Meta:
    model = PatioTechadoExterior
    fields = '__all__'
    

  def get_rendimiento(self, obj):
    total_envases = EnvasesPatioTechadoExt.objects.filter(guia_patio=obj).count()
    if total_envases == 0:
        return 0  # Evita división por cero si no hay envases
    envases_estado_2 = EnvasesPatioTechadoExt.objects.filter(guia_patio=obj, estado_envase='2').count()
    porcentaje = round((envases_estado_2 / total_envases) * 100, 2)
    return f'Se ha procesado {porcentaje} de envases'

    
  def get_variedad(self, obj):
    try:
      variedad = EnvasesPatioTechadoExt.objects.filter(guia_patio = obj.pk).first().get_variedad_display()
      if variedad:
        return variedad
      else:
        return None
        
    except:
      return None
    
  def get_estado_lote_label(self, obj):
    return obj.get_estado_lote_display()
  
  def get_ubicacion_label(self, obj):
    return obj.get_ubicacion_display()
  
  def get_numero_lote(self, obj):
    try:
        if obj.tipo_recepcion.model == 'recepcionmp':
            recepcion = obj.lote_recepcionado.numero_lote
            if recepcion:
                return recepcion
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f'Ocurrió una excepción: {e}')
        return None
  
  def get_control_calidad(self, obj):
    try:
        if obj.tipo_recepcion.model == 'recepcionmp':
            recepcion = obj.lote_recepcionado.id
            if recepcion:
                return recepcion
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f'Ocurrió una excepción: {e}')
        return None
      
  def get_humedad(self, obj):
    try:
        if obj.tipo_recepcion.model == 'recepcionmp':
            recepcion = obj.lote_recepcionado.id
            control_calidad = CCRecepcionMateriaPrima.objects.get(recepcionmp = recepcion).humedad
            
            if control_calidad:
                return control_calidad
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f'Ocurrió una excepción: {e}')
        return None
      
  def get_cantidad_muestras(self, obj):
    try:
        if obj.tipo_recepcion.model == 'recepcionmp':
            recepcion = obj.lote_recepcionado.id
            cantidad_muestras = CCRecepcionMateriaPrima.objects.get(recepcionmp=recepcion).ccrendimiento_set.all().count()
            return cantidad_muestras
        else:
            return None
    except Exception as e:
        print(f'Ocurrió una excepción: {e}')
        return None
      
  def get_productor(self, obj):
    try:
        if obj.tipo_recepcion.model == 'recepcionmp':
            productor = obj.lote_recepcionado.guiarecepcion.productor.nombre
            if productor:
                return productor
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f'Ocurrió una excepción: {e}')
        return None
      
  


class BinBodegaSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    kilos_bin = serializers.SerializerMethodField()
    programa_produccion = serializers.SerializerMethodField()
    programa_seleccion = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
        
    
    class Meta:
        model = BinBodega
        fields = '__all__'
    
    def get_calidad(self, obj):
        return obj.calidad
    
    def get_codigo_tarja(self, obj):
        return obj.codigo_tarja_bin
    
    def get_calibre(self, obj):
        return obj.calibre
        
    def get_variedad(self, obj):
        return obj.variedad
        
    def get_programa_seleccion(self, obj):
        # Obtener el programa de selección a través de BinsPepaCalibrada
        bins_pepa_calibrada = BinsPepaCalibrada.objects.filter(binbodega=obj).first()
        if bins_pepa_calibrada and bins_pepa_calibrada.seleccion:
            return f"Seleccion N° {bins_pepa_calibrada.seleccion.numero_programa}"
        return None

    def get_programa_produccion(self, obj):
        # Primero intentamos obtener el programa de producción a través de BinsPepaCalibrada -> Seleccion -> Producción
        bins_pepa_calibrada = BinsPepaCalibrada.objects.filter(binbodega=obj).first()
        if bins_pepa_calibrada and bins_pepa_calibrada.seleccion and bins_pepa_calibrada.seleccion.produccion:
            return f"Producción N° {bins_pepa_calibrada.seleccion.produccion.id}"
        # Si no hay relación con selección, devolver origen_tarja como programa de producción
        return obj.origen_tarja
    
    def get_kilos_bin (self, obj):
        return obj.kilos_bin
    
    
      

class DetalleBinBodegaSerializer(serializers.ModelSerializer):
    tipo_binbodega_id = serializers.SerializerMethodField(read_only=True)
    tipo_binbodega = serializers.StringRelatedField(read_only=True)
    binbodega = serializers.SerializerMethodField()
    programa = serializers.SerializerMethodField()
    calibrado = serializers.SerializerMethodField()
    calle = serializers.SerializerMethodField()
    fumigado = serializers.SerializerMethodField()
    estado_binbodega = serializers.SerializerMethodField()
    kilos_bin = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    calibre = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    tipo_producto = serializers.SerializerMethodField()
    programa_seleccion = serializers.SerializerMethodField() 
    programa_produccion = serializers.SerializerMethodField()
        
    def get_tipo_producto(self, obj):
        return obj.tipo_producto
    
    
    def get_estado_binbodega(self, obj):
        return obj.get_estado_binbodega_display()
        
    def get_calidad(self, obj):
        return obj.calidad
            
    def get_variedad(self, obj):
        return obj.variedad

    def get_calibre(self, obj):
        return obj.calibre

    def get_calle(self, obj):
        return obj.binbodega.get_calle_bodega_display()
        
    def get_fumigado(self, obj):
        return 'Si' if obj.binbodega.fumigado else 'No'

        
    def get_calibrado(self, obj):
        return obj.calibrado
    
    def get_programa(self, obj):
        return obj.origen_tarja


    def get_binbodega(self, obj):
        return obj.codigo_tarja_bin

    def get_kilos_bin(self, obj):
        return obj.kilos_bin


    def get_tipo_binbodega_id(self, obj):
        # Obtén el ContentType del tipo de bin de la bodega asociado
        try:
            tipo_bin_bodega_content_type = ContentType.objects.get_for_id(obj.tipo_binbodega_id)
            return tipo_bin_bodega_content_type.id
        except ContentType.DoesNotExist:
            return None

    def get_programa_seleccion(self, obj):
        if obj.binbodega and hasattr(obj.binbodega, 'seleccion'):
            seleccion = obj.binbodega.seleccion.seleccion
            return f"Seleccion N° {seleccion.numero_programa}"
        return None

    def get_programa_produccion(self, obj):
        if obj.binbodega and hasattr(obj.binbodega, 'seleccion'):
            seleccion = obj.binbodega.seleccion.seleccion
            if seleccion and hasattr(seleccion, 'produccion'):
                return f"{seleccion.produccion}"
        
        return obj.origen_tarja
    class Meta:
        model = BinBodega
        fields = '__all__'
        
      
      
class BodegaG1Serializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    produccion = serializers.SerializerMethodField()
       
    def get_codigo_tarja(self, obj):
        return obj.produccion.codigo_tarja
    def get_produccion(self, obj):
        return obj.produccion.produccion.id
      
      
    class Meta:
      model = BodegaG1
      fields = '__all__'

class BodegaG2Serializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    produccion = serializers.SerializerMethodField()
        
    def get_codigo_tarja(self, obj):
        return obj.produccion.codigo_tarja
    def get_produccion(self, obj):
        return obj.produccion.produccion.id
    class Meta:
      model = BodegaG2
      fields = '__all__'
      
class BodegaG1ReprocesoSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    reproceso = serializers.SerializerMethodField()
        
    def get_codigo_tarja(self, obj):
        return obj.reproceso.codigo_tarja
      
    def get_reproceso(self, obj):
      return obj.reproceso.reproceso.id
    class Meta:
      model = BodegaG1Reproceso
      fields = '__all__'

class BodegaG2ReprocesoSerializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    reproceso = serializers.SerializerMethodField()

    def get_codigo_tarja(self, obj):
        return obj.reproceso.codigo_tarja
    def get_reproceso(self, obj):
      return obj.reproceso.reproceso.id
    class Meta:
      model = BodegaG2Reproceso
      fields = '__all__'

class BodegaG3Serializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    seleccion = serializers.SerializerMethodField()
       
    def get_codigo_tarja(self, obj):
        return obj.seleccion.codigo_tarja
    def get_seleccion(self, obj):
        return obj.seleccion.seleccion.id
    class Meta:
        model = BodegaG3
        fields = '__all__'
        
class BodegaG4Serializer(serializers.ModelSerializer):
    codigo_tarja = serializers.SerializerMethodField()
    seleccion = serializers.SerializerMethodField()
          
    def get_codigo_tarja(self, obj):
        return obj.seleccion.codigo_tarja
    def get_seleccion(self, obj):
        return obj.seleccion.seleccion.id
    class Meta:
        model = BodegaG4
        fields = '__all__'
        
        
        
class PDFBodegasSerializer(serializers.Serializer):
  codigo_tarja = serializers.CharField()
  programa = serializers.CharField()
  calibre = serializers.CharField()
  variedad = serializers.CharField()
  calidad = serializers.CharField()
  kilos = serializers.FloatField()