from django.db import models
from bodegas.estados_modelo import *
from controlcalidad.estados_modelo import CALIDAD_FRUTA
from .estados_modelo import *
from django.contrib.contenttypes.fields import GenericForeignKey
from bodegas.estados_modelo import *
from core.models import *




class Seleccion(ModeloBaseHistorico):
    estado_programa         = models.CharField(choices=ESTADO_PROGRAMA_SELECCION, max_length=50, default='1')
    pepa_para_seleccion     = models.ManyToManyField("bodegas.BinBodega", through="seleccion.BinsPepaCalibrada")
    tarja_seleccionada      = models.ManyToManyField("self", through='seleccion.TarjaSeleccionada')
    subproductos            = models.ManyToManyField("self", through='seleccion.SubProductoOperario')
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.SET_NULL,blank=True, null = True)
    fecha_inicio_proceso    = models.DateField(blank=True, null = True)
    fecha_termino_proceso   = models.DateField(blank=True, null = True)
    observaciones           = models.CharField(max_length=160, blank=True, null = True)
    operarios               = models.ManyToManyField('core.Operario', through='seleccion.OperariosEnSeleccion')
    numero_programa         = models.PositiveIntegerField(default=0)
    produccion              = models.ForeignKey("produccion.Produccion", on_delete=models.SET_NULL, blank=True, null=True, related_name="selecciones")

    class Meta:
        verbose_name = ('Programa de Selección')
        verbose_name_plural = ('Programas de Selección')
        ordering = ['-numero_programa', '-fecha_creacion']

    def __str__(self):
        if self.numero_programa:
            return "Seleccion N° %s"% (self.id)
        else:
            return "Seleccion Sin N° %s"% (self.id)


class BinsPepaCalibrada(ModeloBase):
    seleccion               = models.ForeignKey("seleccion.Seleccion", on_delete=models.CASCADE, related_name="pepa_calibrada")
    binbodega               = models.ForeignKey("bodegas.BinBodega", on_delete=models.CASCADE)
    bin_procesado           = models.BooleanField(default=False)
    fecha_procesado         = models.DateTimeField(blank=True, null = True)
    class Meta:
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return '%s %s'%(self.binbodega, self.bin_procesado)


class TarjaSeleccionada(ModeloBaseHistorico):
    tipo_resultante         = models.CharField(choices=TIPO_RESULTANTE_SELECCION, default='2', max_length=14)
    seleccion               = models.ForeignKey("seleccion.Seleccion", on_delete=models.CASCADE)
    tipo_patineta           = models.FloatField(choices=TIPOS_BIN)
    peso                    = models.FloatField()
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    cc_tarja                = models.BooleanField(default=False)
    fecha_cc_tarja          = models.DateTimeField(blank=True, null = True)
    codigo_tarja            = models.CharField(max_length=9,blank=True, null=True, unique=True)
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_4)
    esta_eliminado          = models.BooleanField(default=False)
    

   
    class Meta:
        verbose_name = ('Tarja Seleccionada')
        verbose_name_plural = ('Tarjas Seleccionadas')
        ordering = ['-fecha_creacion']

    def __str__(self):
        return "%s"%self.codigo_tarja


class OperariosEnSeleccion(ModeloBase):
    seleccion          = models.ForeignKey(Seleccion, on_delete=models.CASCADE)
    operario            = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    skill_operario      = models.CharField(max_length=10, choices=TIPOS_OPERARIO)       
    dias_trabajados     = models.ManyToManyField("self", through="seleccion.DiaDeOperarioSeleccion")
    
    class Meta:
        verbose_name = '1.1 - Operario en Seleccion'
        verbose_name_plural = '1.1 -Operarios en Seleccion'
        ordering = ['-fecha_creacion']
        constraints = [models.UniqueConstraint(
            name='%(app_label)s_%(class)s_unique_relationships',
            fields=['seleccion', 'operario', 'skill_operario']
        )]
        
    def __str__(self):
        return 'Operario %s %s en %s'%(self.operario.nombre, self.operario.apellido, self.seleccion)
    
class DiaDeOperarioSeleccion(ModeloBase):
    operario = models.ForeignKey("seleccion.OperariosEnSeleccion", on_delete=models.CASCADE)
    dia = models.DateField(blank=True, null=True)
    kilos_dia = models.FloatField(default=0.0)
    ausente = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '1.2 - Dia de Operario en Seleccion'
        verbose_name_plural = '1.2 - Dias de Operarios en Seleccion'
        
    def __str__(self):
        return '%s %s'%(self.operario, self.dia)

class SubProductoOperario(ModeloBaseHistorico):
    seleccion               = models.ForeignKey("seleccion.Seleccion", on_delete=models.CASCADE)
    operario                = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    peso                    = models.FloatField()
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    en_bin                  = models.BooleanField(default=False)
    tipo_subproducto        = models.CharField(max_length=2, choices=TIPO_SUBPRODUCTO, default='1')

    class Meta:
        verbose_name = ('Seleccion SubProducto x operario')
        verbose_name_plural = ('Selecciones de SubProducto x operarios')
        ordering = ['-fecha_creacion']
        

    def __str__(self):
        return "%s Kgs registrado al Operario %s en programa Seleccion n° %s"% (self.peso, self.operario, self.seleccion.pk)
    
class BinSubProductoSeleccion(ModeloBaseHistorico):
    subproductos            = models.ManyToManyField('seleccion.SubProductoOperario', through='seleccion.SubproductosEnBin')
    tipo_patineta           = models.FloatField(choices=TIPOS_BIN)
    registrado_por          = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    cc_subproducto          = models.BooleanField(default=False)
    fecha_cc_subproducto    = models.DateTimeField(blank=True, null = True)
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calidad                 = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='3')
    fumigado                = models.BooleanField(default=False)
    codigo_tarja            = models.CharField(max_length=9,blank=True, null=True )
    ubicacion               = models.CharField(choices=UBICACION_TARJA_SELECCIONADA, default='4', max_length=1)
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_4)
    tipo_subproducto        = models.CharField(choices = TIPO_SUBPRODUCTO, max_length = 3)
    estado_bin              = models.CharField(max_length = 2, choices = ESTADO_BIN_G3_G4, default = '1')
    agrupado                = models.BooleanField(default=False)

    @property
    def total_peso(self):
        return round(sum([subproducto.peso for subproducto in self.subproductosenbin_set.all()]), 2)
    
    class Meta:
        verbose_name = ('SubProducto Resultante Seleccion')
        verbose_name_plural = ('SubProductos Resultantes en Seleccion')
        ordering = ['-fecha_creacion']
        

    def __str__(self):
        return "%s"% (self.codigo_tarja)
    
class SubproductosEnBin(models.Model):
    subproducto_operario   = models.ForeignKey(SubProductoOperario, on_delete=models.CASCADE)
    bin_subproducto        = models.ForeignKey(BinSubProductoSeleccion, on_delete=models.CASCADE)
    peso                   = models.FloatField()
    
    
    
