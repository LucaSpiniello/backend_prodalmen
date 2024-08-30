from django.db import models 
from simple_history.models import HistoricalRecords as Historia
from .estados_modelo import *
from django.contrib.contenttypes.fields import GenericRelation
from core.models import ModeloBase, ModeloBaseHistorico
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError


############################### INICIO MODELO RECEPCION MATERIA PRIMA ##############################  

class EnvasesMp(models.Model):
    nombre = models.CharField( max_length=50)
    peso = models.FloatField()
    descripcion = models.CharField(max_length=160, blank=True, null= True)
        
    class Meta:
        verbose_name = ('3.0 Tipo de Envase MP')
        verbose_name_plural = ('3.0 Tipos de Envases MP')

    def __str__(self):
        return "%s"% (self.nombre)

    
class GuiaRecepcionMP(ModeloBase):
    productor = models.ForeignKey("productores.Productor", on_delete=models.CASCADE)   
    camionero = models.ForeignKey("core.Chofer", on_delete=models.CASCADE)
    camion = models.ForeignKey("core.Camion", on_delete=models.CASCADE)  
    creado_por = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, null=True)
    comercializador  = models.ForeignKey("comercializador.Comercializador", on_delete=models.CASCADE,blank=True, null= True)     
    lotesrecepcionmp = models.ManyToManyField('self', through='recepcionmp.RecepcionMp')
    estado_recepcion = models.CharField(choices=ESTADOSGUIARECEPCION_MP, max_length=1, default='1')
    numero_guia_productor = models.PositiveIntegerField(null=True, blank=True)   
    mezcla_variedades = models.BooleanField(default=False)
    cierre_guia = models.BooleanField(default=False)
    terminar_guia = models.BooleanField(default=False)
     
    
    class Meta:
        verbose_name = ('1.0 Guias Recepcion MP')
        verbose_name_plural = ('1.0 Guias de Recepcion MP')
        ordering = ['-pk']
    
    
    def __str__(self):
        return "%s %s "% (self.pk, self.productor)

def validate_unique_relationships(instance):
    if instance.numero_lote and instance.fecha_creacion:
        # Check if there's another object with the same numero_lote and year of fecha_creacion
        if instance.__class__.objects.filter(numero_lote=instance.numero_lote, fecha_creacion__year=instance.fecha_creacion.year).exists():
           raise IntegrityError(f'Ya existe un Lote registrado con el N° {instance.numero_lote} en la Recepción MP {instance.fecha_creacion.year}, revise y corrija para guardar')



class RecepcionMp(ModeloBaseHistorico):
    guiarecepcion = models.ForeignKey("recepcionmp.GuiaRecepcionMP", on_delete=models.CASCADE)
    kilos_brutos_1 = models.FloatField(blank = True, null = True, default=0)
    kilos_brutos_2 = models.FloatField(blank = True, null = True, default=0)
    kilos_tara_1 = models.FloatField(blank = True, null = True, default=0)  
    kilos_tara_2 = models.FloatField(blank = True, null = True, default=0)      
    envases = models.ManyToManyField("recepcionmp.EnvasesMp", through='recepcionmp.EnvasesGuiaRecepcionMp', related_name='recepciones_mp')    
    creado_por = models.    ForeignKey("cuentas.User", on_delete=models.CASCADE, null=True)
    estado_recepcion = models.CharField(choices=ESTADOS_MP, max_length=1, default='1')
    numero_lote = models.IntegerField(default=0, blank=True, null=True)
      
    
    class Meta:
        verbose_name = ('1.1 Lote Recepción MP')
        verbose_name_plural = ('1.1 Lotes de Recepción MP')
        ordering = ['-fecha_creacion']
        constraints = [
            models.UniqueConstraint(name='%(app_label)s_%(class)s_unique_relationships',
                                    fields=['numero_lote', 'fecha_creacion'])
        ]

    def __str__(self):
        return "Lote N° %s"% (self.pk)

class LoteRecepcionMpRechazadoPorCC(models.Model):
    recepcionmp = models.ForeignKey("recepcionmp.RecepcionMp", on_delete=models.CASCADE)     
    fecha_rechazo = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    rechazado_por = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, null=True)
    resultado_rechazo = models.CharField(max_length=1, choices=RESULTADO_RECHAZO, default='0')
    numero_lote_rechazado = models.IntegerField(default=0)
    historia = Historia()
    
    
    class Meta:
        verbose_name = ('1.2 Lote Rechazado por CCR')
        verbose_name_plural = ('1.2 Lotes Rechazados por CCR')

    def __str__(self):
        return "Lote N° %s %s"% (self.recepcionmp.pk, self.get_resultado_rechazo_display())


class EnvasesGuiaRecepcionMp(models.Model):
    envase = models.ForeignKey(EnvasesMp, on_delete=models.CASCADE)
    recepcionmp = models.ForeignKey(RecepcionMp, on_delete=models.CASCADE)
    variedad = models.CharField(max_length=2, choices=VARIEDADES_MP)
    tipo_producto = models.CharField(max_length=2, choices=TIPO_PRODUCTOS_RECEPCIONMP, default='1')
    cantidad_envases = models.PositiveIntegerField()
    class Meta:

        verbose_name = ('1.3 Envase de la Recepcion MP')
        verbose_name_plural = ('1.3 Envases del Lote RecepcionMP')
    
############################### FIN MODELO RECEPCION MATERIA PRIMA ##############################  


############################### INICIO MODELO RECEPCION COLOSOS DE MATERIA PRIMA ##############################     
class RecepcionColoso(models.Model):   
    operario            = models.ForeignKey("core.Operario", on_delete=models.CASCADE)   
    coloso              = models.ForeignKey("core.Coloso", on_delete=models.CASCADE, null=True, blank=True)
    tractor             = models.ForeignKey("core.Tractor", on_delete=models.CASCADE, null=True, blank=True)
    tractor_coloso      = models.ForeignKey("core.TractorColoso", on_delete=models.CASCADE, null=True, blank=True)
    variedad            = models.CharField(max_length=2, choices=VARIEDADES_MP)
    huerto              = models.CharField(choices=HUERTOS_PRODALMEN, max_length=2, default='1')
    sector              = models.CharField(choices=SECTORES_PRODALMEN, max_length=2, default='1')      
    kilos_brutos        = models.FloatField(blank = True, null = True, default=0)  
    fecha_recepcion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion  = models.DateTimeField(auto_now=True)
    creado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, null=True)
    estado_recepcion    = models.CharField(choices=ESTADOS_RECEPCION_COLOSO, max_length=1, default='1')
    historia            = Historia()
    en_lote             = models.BooleanField(default=False)
    observaciones       = models.CharField(max_length=160, blank=True, null=True)
    numero_vale         = models.PositiveIntegerField()
    sector_descarga     = models.CharField(max_length=1, choices=UBICACION_PATIO_TECHADO_EXT_LI, default='0')
    hora_salida_vale    = models.TimeField(null=True, blank=True)
  
    
    
    class Meta:

        verbose_name = ('2.0 Recepción Vale Coloso')
        verbose_name_plural = ('2.0 Recepción Vales Colosos')


    def __str__(self):
        return "Vale N°%s del operario %s "% (self.numero_vale, self.operario)


class ColososEnLote(models.Model):
    colosos             = models.ManyToManyField("recepcionmp.RecepcionColoso", through="recepcionmp.ColososAlLote")
    creado_por          = models.ForeignKey("cuentas.User", on_delete=models.SET_NULL, null=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_modificacion  = models.DateTimeField(auto_now=True)
    historia            = Historia()
    observaciones       = models.TextField(blank=True, null=True)
    estado_lote         = models.CharField(max_length=1, choices=ESTADOS_LOTE_COLOSOS, default='1')
    lote_cerrado        = models.BooleanField(default=False)
    peso_fruta_neto     = models.FloatField(default=0)
    pkinterno           = models.IntegerField(default=400)
    recepcionmp         = models.ForeignKey(GuiaRecepcionMP, on_delete=models.CASCADE, null=True, blank=True)
     
    class Meta:

        verbose_name = ('2.1 Lote de Coloso')
        verbose_name_plural = ('2.1 Lotes de Colosos')
        ordering = ['-pk']
        unique_together = (('pkinterno','id'))
        


    def __str__(self):
        return "Registro Lote Interno %s"% (self.pk)

class ColososAlLote(models.Model):
    recepcion_coloso        = models.ForeignKey("recepcionmp.RecepcionColoso", on_delete=models.CASCADE)
    colosos_en_lote         = models.ForeignKey("recepcionmp.ColososEnLote", on_delete=models.CASCADE)
    

    
     
    
    
    






