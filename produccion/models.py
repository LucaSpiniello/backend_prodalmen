from django.db import models
from simple_history.models import HistoricalRecords as Historia

from core.estados_modelo import TIPOS_OPERARIO
from .estados_modelo import *
from django.urls import reverse
from bodegas.estados_modelo import *
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import ModeloBaseHistorico, ModeloBase


class Produccion(ModeloBaseHistorico):
    estado                  = models.CharField(choices=ESTADOS_PRODUCCION, max_length=1, default='1')
    lotes                   = models.ManyToManyField("bodegas.EnvasesPatioTechadoExt", through= 'produccion.LotesPrograma') ##INPUTS
    tarjas_resultantes      = models.ManyToManyField("self", through= 'produccion.TarjaResultante') ##OUTPUTS
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    fecha_inicio_proceso    = models.DateField(blank=True, null = True)
    fecha_termino_proceso   = models.DateField(blank=True, null = True)
    operarios               = models.ManyToManyField('core.Operario', through='produccion.OperariosEnProduccion')
    numero_programa         = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "1.0 - Programa de Produccion"
        verbose_name_plural = "1.0 - Programas de Produccion"
        ordering = ['-numero_programa']

    def __str__(self):
        return 'Produccion N° %s'%(self.pk)
    
class OperariosEnProduccion(ModeloBase):
    produccion          = models.ForeignKey(Produccion, on_delete=models.CASCADE)
    operario            = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    skill_operario      = models.CharField(max_length=10, choices=TIPOS_OPERARIO)       
    dias_trabajados     = models.ManyToManyField("self", through="produccion.DiaDeOperarioProduccion")
    
    class Meta:
        verbose_name = '1.1 - Operario en Programa Produccion'
        verbose_name_plural = '1.1 -Operarios en Programas Produccion'
        ordering = ['-fecha_creacion']
        constraints = [models.UniqueConstraint(
            name='%(app_label)s_%(class)s_unique_relationships',
            fields=['produccion', 'operario', 'skill_operario']
        )]
        
    def __str__(self):
        return 'Operario %s %s en %s'%(self.operario.nombre, self.operario.apellido, self.produccion)
    
class DiaDeOperarioProduccion(ModeloBase):
    operario = models.ForeignKey("produccion.OperariosEnProduccion", on_delete=models.CASCADE)
    dia = models.DateField(blank=True, null=True)
    kilos_dia = models.FloatField(default=0.0)
    ausente = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '1.2 - Dia de Operario en Programa Produccion'
        verbose_name_plural = '1.2 - Dias de Operarios en Programas Produccion'
        ordering = ('-dia',)
        
    def __str__(self):
        return '%s %s'%(self.operario, self.dia)

class LotesPrograma(ModeloBaseHistorico):   
    produccion           = models.ForeignKey("produccion.Produccion", on_delete=models.CASCADE)
    bodega_techado_ext   = models.ForeignKey("bodegas.EnvasesPatioTechadoExt", on_delete=models.CASCADE)   
    bin_ingresado        = models.BooleanField(default=False)
    bin_procesado        = models.BooleanField(default=False)
    fecha_procesado      = models.DateTimeField(blank=True, null = True)
    procesado_por        = models.ForeignKey("cuentas.User", null=True, on_delete=models.SET_NULL)
    esta_eliminado        = models.BooleanField(default=False)

    class Meta:
        verbose_name = "1.2 - Envase del Lote agregados a Produccion"
        verbose_name_plural = "1.2 - Envases del Lote en Producción"
        ordering = ['bin_procesado']

    def __str__(self):
        return 'Envase N° %s en Programa N° %s'%(self.bodega_techado_ext,self.produccion.pk)

class TarjaResultante(ModeloBaseHistorico):
    tipo_resultante      = models.CharField(choices=TIPO_RESULTANTE, default='3', max_length=1)
    produccion           = models.ForeignKey("produccion.Produccion", on_delete=models.CASCADE)
    peso                 = models.FloatField()
    tipo_patineta        = models.FloatField(choices=TIPOS_BIN)
    registrado_por       = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, blank= True, null=True)
    cc_tarja             = models.BooleanField(default=False)
    fecha_cc_tarja       = models.DateTimeField(blank=True, null = True)
    ubicacion            = models.CharField(choices=UBICACION_TARJA, default='0', max_length=1)
    codigo_tarja         = models.CharField(max_length=9,blank=True, null=True, unique=True)
    calle_bodega         = models.CharField(max_length=2, choices=CALLE_BODEGA_2)
    esta_eliminado       = models.BooleanField(default=False)

    class Meta:
        verbose_name = "1.3 - Tarja Resultante"
        verbose_name_plural = "1.3 - Tarjas Resultantes"
        ordering = ['-fecha_creacion']
        

    def __str__(self):
        return '%s'%(self.codigo_tarja) 

class Reproceso(ModeloBaseHistorico):
    estado                  = models.CharField(max_length=1, choices=ESTADOS_REPROCESO, default="0")
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    fecha_inicio_proceso    = models.DateField(blank=True, null = True)
    fecha_termino_proceso   = models.DateField(blank=True, null = True)
    bins                    = models.ManyToManyField("bodegas.BinBodega", through= 'produccion.BinsEnReproceso') 
    tarjas_resultantes      = models.ManyToManyField("self", through= 'produccion.TarjaResultanteReproceso') 
    operarios               = models.ManyToManyField('core.Operario', through='produccion.OperariosEnReproceso')
    numero_programa         = models.PositiveIntegerField(default=0)
    
    
    class Meta:
        verbose_name = '2.0 - Programa de Reproceso'
        verbose_name_plural = '2.0 - Programas de Reprocesos'
        ordering = ['-numero_programa']
        
    def __str__(self):
        return 'Reproceso N°%s'%(self.pk)
    
class OperariosEnReproceso(ModeloBase):
    reproceso          = models.ForeignKey(Reproceso, on_delete=models.CASCADE)
    operario            = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    skill_operario      = models.CharField(max_length=10, choices=TIPOS_OPERARIO)       
    dias_trabajados     = models.ManyToManyField("self", through="produccion.DiaDeOperarioReproceso")
    
    class Meta:
        verbose_name = '1.1 - Operario en Reproceso Produccion'
        verbose_name_plural = '1.1 -Operarios en Reproceso Produccion'
        ordering = ['-fecha_creacion']
        constraints = [models.UniqueConstraint(
            name='%(app_label)s_%(class)s_unique_relationships',
            fields=['reproceso', 'operario', 'skill_operario']
        )]
        
    def __str__(self):
        return 'Operario %s %s en %s'%(self.operario.nombre, self.operario.apellido, self.reproceso)
    
class DiaDeOperarioReproceso(ModeloBase):
    operario = models.ForeignKey("produccion.OperariosEnReproceso", on_delete=models.CASCADE)
    dia = models.DateField(blank=True, null=True)
    kilos_dia = models.FloatField(default=0.0)
    ausente = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '1.2 - Dia de Operario en Reproceso Produccion'
        verbose_name_plural = '1.2 - Dias de Operarios en Reprocesos Produccion'
        
    def __str__(self):
        return '%s %s'%(self.operario, self.dia)
    
class BinsEnReproceso(ModeloBaseHistorico):
    reproceso           = models.ForeignKey(Reproceso, on_delete=models.CASCADE)
    binbodega           = models.ForeignKey('bodegas.BinBodega', on_delete=models.CASCADE)
    bin_ingresado       = models.BooleanField(default=False)
    bin_procesado       = models.BooleanField(default=False)
    fecha_procesado     = models.DateTimeField(blank=True, null=True)
    procesado_por       = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, blank=True, null=True)

    
    class Meta:
        verbose_name = '2.2 - Bin Ingresado a Reproceso'
        verbose_name_plural = '2.2 - Bins Ingresados a Reprocesos'
        ordering = ['-fecha_creacion']
        
        
    def __str__(self):
        return 'Bins %s en Reproceso N°%s'%(self.binbodega, self.reproceso.pk)
    
class TarjaResultanteReproceso(ModeloBaseHistorico):
    reproceso           = models.ForeignKey(Reproceso, on_delete=models.CASCADE)
    tipo_resultante     = models.CharField(max_length=1, choices=TIPO_RESULTANTE, default='3')
    peso                = models.FloatField(default=0.0)
    tipo_patineta       = models.FloatField(choices=TIPOS_BIN)
    cc_tarja            = models.BooleanField(default=False)
    fecha_cc_tarja       = models.DateTimeField(blank=True, null = True)
    codigo_tarja        = models.CharField(max_length=9,blank=True, null=True, unique=True)
    calle_bodega        = models.CharField(max_length=2, choices=CALLE_BODEGA_2)
    registrado_por      = models.ForeignKey("cuentas.User", on_delete=models.CASCADE, blank= True, null=True)
    esta_eliminado      = models.BooleanField(default=False)
 
    
    class Meta:
        verbose_name = '2.3 - Tarja Resultante Reproceso'
        verbose_name_plural = '2.3 - Tarjas Resultantes Reprocesos'
        ordering = ['-fecha_creacion']
        
        
    def __str__(self):
        return '%s'%(self.codigo_tarja)