from django.db import models
from django.urls import reverse
from .estados_modelo import *
from django.contrib.contenttypes.fields import GenericForeignKey
from controlcalidad.estados_modelo import CALIDAD_FRUTA
from core.models import ModeloBase, ModeloBaseHistorico
from django.contrib.contenttypes.fields import GenericRelation
from controlcalidad.models import *
from seleccion.models import *

class CCGuiaInterna(ModeloBase):
    opciones_cc = models.Q(app_label='controlcalidad', model='ccrecepcionmateriaprima') | models.Q(app_label='controlcalidad', model='cclotesinternos') 
    tipo_cc_guia = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, limit_choices_to=opciones_cc)
    id_guia = models.PositiveIntegerField()
    cc_guia = GenericForeignKey('tipo_cc_guia', 'id_guia')
    
    class Meta:
        verbose_name = ('CC Guia Patio Exterior')
        verbose_name_plural = ('CC Guias de Patio Exterior')
    
    def __str__(self):
        
        return "%s"% (self.cc_guia)

class PatioTechadoExterior(ModeloBaseHistorico):
    cc_guia                 = models.ForeignKey("bodegas.CCGuiaInterna", on_delete=models.SET_NULL, null=True, blank=True)
    limite_opciones         = models.Q(app_label='recepcionmp', model='recepcionmp') | models.Q(app_label='recepcionmp', model='colososenlote')
    tipo_recepcion          = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, limit_choices_to=limite_opciones)
    id_recepcion            = models.PositiveIntegerField()
    lote_recepcionado       = GenericForeignKey('tipo_recepcion', 'id_recepcion')
    ubicacion               = models.CharField(choices=UBICACION_PATIO_TECHADO_EXT, max_length=1, default='0')
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, blank= True, null=True)
    estado_lote             = models.CharField(choices=ESTADO_GUIA_PATIO_EXT, max_length=1, default='1')
    envases                 = models.ManyToManyField('self', through='bodegas.EnvasesPatioTechadoExt')
    procesado               = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = ('Bodega Patio Exterior')
        verbose_name_plural = ('Bodega Patio Exterior')
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return "Bodega N°%s, %s"%(self.pk, self.lote_recepcionado)

class EnvasesPatioTechadoExt(ModeloBase):
    guia_patio           = models.ForeignKey('bodegas.PatioTechadoExterior', on_delete=models.CASCADE)
    kilos_fruta          = models.FloatField(default=0.0)
    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True)
    variedad             = models.CharField(max_length=30,choices=VARIEDAD)
    estado_envase        = models.CharField(choices=ESTADO_ENVASE_EN_PATIO_EXT, max_length=1, default='1')
    numero_bin           = models.PositiveIntegerField(default=0)
    
    
    class Meta:
        verbose_name = ('Envase Bodega Patio Exterior')
        verbose_name_plural = ('Envases Bodega Patio Exterior')
        ordering = ['-estado_envase']
    
    def __str__(self):
        
        return "%s"% self.pk
        

class BinBodega(ModeloBaseHistorico):
    limite_opciones = models.Q(app_label='bodegas', model='bodegag1') | \
                      models.Q(app_label='bodegas', model='bodegag1reproceso') | \
                      models.Q(app_label='bodegas', model='bodegag2') | \
                      models.Q(app_label='bodegas', model='bodegag2reproceso') | \
                      models.Q(app_label='bodegas', model='bodegag3') | \
                      models.Q(app_label='bodegas', model='bodegag4') | \
                      models.Q(app_label='seleccion', model='binsubproductoseleccion') | \
                      models.Q(app_label='bodegas', model='bodegag5') | \
                      models.Q(app_label='bodegas', model='bodegag6') | \
                      models.Q(app_label='bodegas', model='bodegag7') | \
                      models.Q(app_label='agrupacionbins', model='agrupaciondebinsbodegas') | \
                      models.Q(app_label='agrupacionbins', model='frutasobrantedeagrupacion')

    tipo_binbodega = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, limit_choices_to=limite_opciones)
    id_binbodega = models.PositiveIntegerField()
    binbodega = GenericForeignKey('tipo_binbodega', 'id_binbodega')
    procesado = models.BooleanField(default=False)
    ingresado = models.BooleanField(default=False)
    agrupado = models.BooleanField(default=False)
    procesado_por = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, blank=True, null=True)
    estado_binbodega = models.CharField(max_length=2, choices=ESTADO_BIN_BODEGA, default='-')

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return '%s' % self.codigo_tarja_bin

    @property
    def codigo_tarja_bin(self):
        if self.binbodega:
            model_name = self.tipo_binbodega.model
            if model_name in ['bodegag1', 'bodegag2']:
                return self.binbodega.produccion.codigo_tarja
            elif model_name in ['bodegag1reproceso', 'bodegag2reproceso']:
                return self.binbodega.reproceso.codigo_tarja
            elif model_name in ['bodegag3', 'bodegag4', 'bodegag5']:
                return self.binbodega.seleccion.codigo_tarja
            elif model_name == 'bodegag6':
                return self.binbodega.programa.codigo_tarja
            elif model_name == 'bodegag7':
                return self.binbodega.proceso.codigo_tarja
            elif model_name in ['agrupaciondebinbodega', 'sobrantedeagrupacion', 'binsubproductoseleccion']:
                return self.binbodega.codigo_tarja
        return None

    @property
    def calle_bodega(self):
        if self.binbodega:
            model_name = self.tipo_binbodega.model
            if model_name in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4', 'bodegag5', 'bodegag6', 'bodegag7', 'agrupaciondebinbodega', 'sobrantedeagrupacion', 'binsubproductoseleccion']:
                return self.binbodega.calle_bodega
        return None
    
    @property
    def origen_tarja(self):
        if self.binbodega:
            model_name = self.tipo_binbodega.model
            if model_name in ['bodegag1', 'bodegag2']:
                return f'Programa Producción N° {self.binbodega.produccion.produccion.pk}'
            elif model_name in ['bodegag1reproceso', 'bodegag2reproceso']:
                return f'Programa Reproceso N° {self.binbodega.reproceso.reproceso.pk}'
            elif model_name in ['bodegag3', 'bodegag4', 'bodegag5']:
                return f'Programa Selección N° {self.binbodega.seleccion.seleccion.pk}'
            elif model_name == 'bodegag6':
                return f'Programa PH N° {self.binbodega.programa.programa.pk}'
            elif model_name == 'bodegag7':
                return f'Proceso PH N° {self.binbodega.proceso.proceso.pk}'
            elif model_name in ['agrupaciondebinbodega',]:
                return f'Agrupación de Bins Bodega N° {self.binbodega.pk}'
            elif model_name in ['sobrantedeagrupacion',]:
                return f'Sobrante Agrupación de Bins Bodega N° {self.binbodega.pk}'
            elif model_name in ['binsubproductoseleccion']:
                return f'Bin Subproducto Selección N° {self.binbodega.pk}'
        return None
    
    @property
    def kilos_bin(self):
        modelo = self.tipo_binbodega.model
        contenido = self.binbodega

        if modelo in ['bodegag1', 'bodegag2']:
            entidad = contenido.produccion
            if entidad:
                return round(entidad.peso - entidad.tipo_patineta, 2)
        elif modelo in ['bodegag1reproceso', 'bodegag2reproceso']:
            entidad = contenido.reproceso
            if entidad:
                return round(entidad.peso - entidad.tipo_patineta, 2)
        elif modelo in ['bodegag3', 'bodegag4', 'bodegag5']:
            if contenido.seleccion:
                return round(contenido.seleccion.peso - contenido.seleccion.tipo_patineta, 2)
        elif modelo == 'bodegag6':
            if contenido.programa:
                return round(contenido.programa.peso - contenido.programa.tipo_patineta, 2)
        elif modelo == 'bodegag7':
            if contenido.proceso:
                return round(contenido.proceso.peso - contenido.proceso.tipo_patineta, 2)
        elif modelo in ['agrupaciondebinbodega', 'sobrantedeagrupacion',]:
            kilos = contenido.kilos_fruta
            return round(kilos, 2)
        elif modelo in ['binsubproductoseleccion']:
            kilos = contenido.total_peso
            return round(kilos, 2)
        return 0
    
    @property
    def calidad(self):
        try:
            if self.tipo_binbodega.model in ['bodegag3', 'bodegag4','bodegag5']:
                return self.binbodega.get_calidad_display()
            # elif self.tipo_binbodega.model in ['agrupaciondebinbodega', 'sobrantedeagrupacion']:
            #     bin_con_mas_kilos = self.binbodega.binsparaagrupacion_set.annotate(
            #         max_kilos=Max('tarja__kilos_fruta')
            #     ).order_by('-max_kilos').first()
            #     if bin_con_mas_kilos and bin_con_mas_kilos.tarja:
            #         return getattr(bin_con_mas_kilos.tarja, 'get_calidad_display', lambda: 'No disponible')()
            #     return 'No disponible'
        except AttributeError:
            return 'Sin Calidad'
        except Exception as e:
            return f'Error al obtener calidad: {str(e)}'
        return 'Sin Calidad'

    @property
    def variedad(self):
        try:
            if hasattr(self.binbodega, 'get_variedad_display'):
                return self.binbodega.get_variedad_display()
            else:
                if self.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
                    return 'Sin Variedad'
        except AttributeError:
            return 'Información no disponible'
        return 'Propiedad no definida'
    
    @property
    def variedad_clave(self):
        try:
            if hasattr(self.binbodega, 'get_variedad_display'):
                return self.binbodega.variedad
            else:
                if self.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
                    return 'Sin Variedad'
        except AttributeError:
            return 'Información no disponible'
        return 'Propiedad no definida'

    @property
    def calibre(self):
        try:
            if hasattr(self.binbodega, 'get_calibre_display'):
                return self.binbodega.get_calibre_display()
            else:
                if self.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
                    return 'Sin Calibre'
        except AttributeError:
            return 'Información no disponible'
        return 'Propiedad no definida'
    
    @property
    def calibrado(self):
        modelo = self.tipo_binbodega.model
        contenido = self.binbodega
        try:
            if modelo in ['bodegag1', 'bodegag2']:
                entidad = getattr(contenido, 'produccion', None)
                if entidad:
                    cc_registro = CCTarjaResultante.objects.filter(tarja=entidad.pk).first()
                    return 'Si' if cc_registro and cc_registro.estado_cc == '3' else 'No'
            elif modelo in ['bodegag1reproceso', 'bodegag2reproceso']:
                entidad = getattr(contenido, 'reproceso', None)
                if entidad:
                    cc_registro = CCTarjaResultanteReproceso.objects.filter(tarja=entidad.pk).first()
                    return 'Si' if cc_registro and cc_registro.estado_cc == '3' else 'No'
            elif modelo in ['bodegag3', 'bodegag4', 'bodegag5']:
                entidad = getattr(contenido, 'seleccion', None)
                if entidad:
                    cc_registro = CCTarjaSeleccionada.objects.filter(tarja_seleccionada=entidad.pk).first()
                    return 'Si' if cc_registro and cc_registro.estado_cc == '3' else 'No'
            elif modelo == 'bodegag6':
                entidad = getattr(contenido, 'programa', None)
                if entidad:
                    cc_registro = CCBinResultanteProgramaPH.objects.filter(bin_resultante=entidad.pk).first()
                    return 'Si' if cc_registro and cc_registro.estado_cc == '1' else 'No'
            elif modelo == 'bodegag7':
                entidad = getattr(contenido, 'proceso', None)
                if entidad:
                    cc_registro = CCBinResultanteProcesoPH.objects.filter(bin_resultante=entidad.pk).first()
                    return 'Si' if cc_registro and cc_registro.estado_control == '1' else 'No'
            elif modelo in ['agrupaciondebinbodega', 'sobrantedeagrupacion', 'binsubproductoseleccion']:
                return 'Sin Informacion detallada'
        except AttributeError:
            return "Propiedad no disponible"
        except:
            return "Modelo no manejado"

    @property
    def cdc_tarja(self):
        modelo = self.tipo_binbodega.model
        contenido = self.binbodega
        try:
            if modelo in ['bodegag1', 'bodegag2']:
                entidad = getattr(contenido, 'produccion', None)
                if entidad:
                    cc_registro = CCTarjaResultante.objects.filter(tarja=entidad.pk).first()
                    return cc_registro
            elif modelo in ['bodegag1reproceso', 'bodegag2reproceso']:
                entidad = getattr(contenido, 'reproceso', None)
                if entidad:
                    cc_registro = CCTarjaResultanteReproceso.objects.filter(tarja=entidad.pk).first()
                    return cc_registro
            elif modelo in ['bodegag3', 'bodegag4', 'bodegag5']:
                entidad = getattr(contenido, 'seleccion', None)
                if entidad:
                    cc_registro = CCTarjaSeleccionada.objects.filter(tarja_seleccionada=entidad.pk).first()
                    return cc_registro
            elif modelo == 'bodegag6':
                entidad = getattr(contenido, 'programa', None)
                if entidad:
                    cc_registro = CCBinResultanteProgramaPH.objects.filter(bin_resultante=entidad.pk).first()
                    return cc_registro
            elif modelo == 'bodegag7':
                entidad = getattr(contenido, 'proceso', None)
                if entidad:
                    cc_registro = CCBinResultanteProcesoPH.objects.filter(bin_resultante=entidad.pk).first()
                    return cc_registro
            elif modelo in ['agrupaciondebinbodega', 'sobrantedeagrupacion', 'binsubproductoseleccion']:
                return 'Sin Informacion detallada'
        except AttributeError:
            return "Propiedad no disponible"
        except:
            return "Modelo no manejado"

    @property
    def tipo_producto(self):
        if self.binbodega:
            model_name = self.tipo_binbodega.model
            if model_name in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion', 'agrupaciondebinbodega', 'sobrantedeagrupacion',]:
                return 'Almendras'
        
            elif model_name == 'bodegag6':
                return self.binbodega.programa.get_tipo_resultante_display()

            elif model_name == 'bodegag7':
                return self.binbodega.proceso.get_tipo_resultante_display()
        return None      
      
class BodegaG1(ModeloBaseHistorico):
    produccion              = models.OneToOneField("produccion.TarjaResultante",on_delete=models.CASCADE)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    kilos_fruta             = models.FloatField(default=0.0)
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_1, default='-')
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True) 
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 
    


    class Meta:
        verbose_name = 'Bodega G1'
        verbose_name_plural = 'Bodega G1'


    
    def __str__(self):
        return "%s"% (self.produccion.codigo_tarja)
      
class BodegaG1Reproceso(ModeloBaseHistorico):
    reproceso               = models.OneToOneField("produccion.TarjaResultanteReproceso",on_delete=models.CASCADE)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    kilos_fruta             = models.FloatField(default=0.0)
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_1, default='-')
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True)  
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 


    class Meta:
        verbose_name = 'Bodega G1 Reproceso'
        verbose_name_plural = 'Bodegas G1 Reprocesos'
    
    def __str__(self):
        return "%s"% (self.reproceso.codigo_tarja)

class BodegaG2(ModeloBaseHistorico):
    produccion              = models.OneToOneField("produccion.TarjaResultante",on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G2, max_length=1, default='1')
    kilos_fruta             = models.FloatField(default=0.0)
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_2, default='-')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True)   
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 

    class Meta:
        verbose_name = 'Bodega G2'
        verbose_name_plural = 'Bodega G2'

    def __str__(self):
        return "%s"% (self.produccion.codigo_tarja)

class BodegaG2Reproceso(ModeloBaseHistorico):
    reproceso               = models.OneToOneField("produccion.TarjaResultanteReproceso",on_delete=models.CASCADE)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G2, max_length=1, default='1')
    kilos_fruta             = models.FloatField(default=0.0)
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_2, default='-')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True)   
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 


    class Meta:
        verbose_name = 'Bodega G2 Reproceso'
        verbose_name_plural = 'Bodega G2 Reprocesos'

    def __str__(self):
        return "%s"% (self.reproceso.codigo_tarja)
    
# ######### Bodega G3 ##########
class BodegaG3(ModeloBaseHistorico):
    seleccion               = models.ForeignKey("seleccion.TarjaSeleccionada", on_delete=models.CASCADE)
    kilos_fruta             = models.FloatField(default=0.0)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G3_G4, max_length=1, default='1')
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calidad                 = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_3, default='-')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True)  
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 
  
    
    class Meta:
        verbose_name = 'Bodega G3'
        verbose_name_plural = 'Bodega G3'

    def __str__(self):
        return "%s"% (self.seleccion.codigo_tarja)

# ######### Bodega G4 ##########
class BodegaG4(ModeloBaseHistorico):
    seleccion                   = models.ForeignKey("seleccion.TarjaSeleccionada", on_delete=models.CASCADE)
    kilos_fruta                 = models.FloatField(default=0.0)
    estado_bin                  = models.CharField(choices=ESTADO_BIN_G3_G4, max_length=1, default='1')
    calidad                     = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    variedad                    = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                     = models.CharField(choices=CALIBRES, max_length=2,default='0')
    fumigado                    = models.BooleanField(default=False)  
    fecha_fumigacion            = models.DateTimeField(blank=True, null=True)   
    calle_bodega                = models.CharField(max_length=2, choices=CALLE_BODEGA_4, default='-')
    tarja                       = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 
    
    class Meta:
        verbose_name = 'Bodega G4'
        verbose_name_plural = 'Bodega G4'

    def __str__(self):
        return "%s"% (self.seleccion.codigo_tarja)

######### Bodega G5 ##########
class BodegaG5(ModeloBaseHistorico):
    seleccion               = models.OneToOneField("seleccion.TarjaSeleccionada", on_delete=models.CASCADE)
    estado_bin              = models.CharField(max_length=50, choices=ESTADO_BIND_EN_FIGORIFICO, default='en_bodega')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_G5, default='-')
    codigo_tarja            = models.CharField(max_length=9, blank=True, null=True)
    kilos_fruta             = models.FloatField(default=0.0)
    calidad                 = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True)   
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 

  
  
    class Meta:
        verbose_name = "Bodega G5"
        verbose_name_plural = "Bodega G5"
    

    def __str__(self):
        return "%s"%(self.seleccion.codigo_tarja)

######### Bodega G6 ##########
class BodegaG6(ModeloBaseHistorico):
    programa            = models.ForeignKey("planta_harina.BinResultantePrograma", on_delete=models.CASCADE)
    kilos_fruta         = models.FloatField(default=0.0)
    estado_bin          = models.CharField(max_length=50, choices=ESTADO_BIND_EN_FIGORIFICO, default='en_bodega')
    calle_bodega        = models.CharField(max_length=2, choices=CALLE_BODEGA_G5, default='-')
    humedad             = models.FloatField(default=0.0)
    piel_aderida        = models.FloatField(default=0.0)
    calidad             = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    fumigado            = models.BooleanField(default=False)  
    fecha_fumigacion    = models.DateTimeField(blank=True, null=True)   
    tarja               = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 

    

    class Meta:
        verbose_name = 'Bodega G6'
        verbose_name_plural = 'Bodega G6'
    


    def __str__(self):
        return "%s"%(self.programa.codigo_tarja)
   
######### Bodega G7 ##########
class BodegaG7(ModeloBaseHistorico):
    proceso                 = models.ForeignKey("planta_harina.BinResultanteProceso", on_delete=models.CASCADE)
    estado_bin              = models.CharField(max_length=50, choices=ESTADO_BIND_EN_FIGORIFICO, default='en_bodega')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_G5, default='-')
    kilos_fruta             = models.FloatField(default=0.0)
    humedad                 = models.FloatField(null=True, default=0.0)
    piel_aderida            = models.FloatField(null=True, default=0.0)
    granulometria           = models.FloatField(null=True, default=0.0)
    parametro               = models.CharField(max_length=50, choices=PARAMETRO_HARINA)
    calidad                 = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True)  
    tarja                   = GenericRelation('bodegas.BinBodega', content_type_field='tipo_binbodega', object_id_field='id_binbodega') 

    
    class Meta:
        verbose_name = 'Bodega G7'
        verbose_name_plural = 'Bodega G7'

    def __str__(self):
        return "%s"%(self.proceso)
        
class FumigacionBodegas(ModeloBase):
    codigo_fumigacion       = models.CharField(max_length=100, unique=True)
    estado_fumigacion       = models.CharField(max_length=1, default='0', choices=ESTADOS_FUMIGACION)
    bins_en_fumigacion      = models.ManyToManyField('bodegas.BinBodega',)
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    observaciones           = models.TextField(blank=True)
    fumigacion_armada       = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Fumigacion bodega'
        verbose_name_plural = 'Fumigacion Bodegas'

    def __str__(self):
        return "Fumigacion N° %s"%(self.pk)
    
