from django.db import models
from .estados_modelo import *
from simple_history.models import HistoricalRecords as Historia
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from bodegas.estados_modelo import *
from .estados_modelo import *
from core.models import ModeloBaseHistorico, ModeloBase

#### Programa ####

class ProgramaPH(ModeloBaseHistorico):
    bin_bodegas         =   models.ManyToManyField('bodegas.BinBodega', through='planta_harina.BinParaPrograma')
    bin_resultante      =   models.ManyToManyField("self", through='planta_harina.BinResultantePrograma')
    tipo_programa       =   models.CharField(choices=PRODUCTO_PROGRAMA, max_length=50)
    estado_programa     =   models.CharField(choices=ESTADO_PH, max_length=2, default='1')
    creado_por          =   models.ForeignKey('cuentas.User', null=True, on_delete=models.SET_NULL)
    kilos_inicio        =   models.FloatField(default=0.0)
    kilos_merma         =   models.FloatField(default=0.0)    
    fecha_inicio_programa =   models.DateField(null=True, blank=True)
    fecha_termino_programa  =   models.DateField(null=True, blank=True)
    cerrado_el          =   models.DateTimeField(null=True, blank=True) 
    ubicacion_produc    =   models.CharField(max_length=50, choices=UBICACION_PRODUCTO, default='en_planta')
    perdidaprograma     =   models.CharField(choices=PERDIDAPROGRAMA, max_length=1)
    operarios           =   models.ManyToManyField('core.Operario', through='planta_harina.OperariosEnProgramaPH')
    
 
    def lista_bines(self):
        return "-".join([str(p) for p in self.bin_bodegas.all()])
    
    class Meta:
        verbose_name = 'Programa Planta Harina'
        verbose_name_plural = '1 Programas Planta Harina'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return '%s N° %s'%(self.get_tipo_programa_display() ,self.pk)


class BinParaPrograma(ModeloBase):
    programa                = models.ForeignKey(ProgramaPH, on_delete=models.CASCADE)
    bin_bodega              = models.ForeignKey('bodegas.BinBodega', on_delete=models.CASCADE)
    procesado               = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return '%s'%(self.pk)
    
    
class BinResultantePrograma(ModeloBaseHistorico):
    programa                = models.ForeignKey(ProgramaPH, on_delete=models.CASCADE)
    estado_bin              = models.CharField(max_length=50, choices=ESTADO_BIN_RESULTANTE_PH, default='creado')
    tipo_resultante         = models.CharField(max_length=3, choices=TIPO_RESULTANTE_PH, blank=True, null=True)
    peso                    = models.FloatField(default=0.0)
    tipo_patineta           = models.FloatField(choices=TIPOS_BIN)
    codigo_tarja            = models.CharField(max_length=9,blank=True, null=True )
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_G5, default='-')
    esta_eliminado          = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Bin Resultante Programa"
        verbose_name_plural = '1.2 Bins Resultantes del Programa'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return '%s'%(self.codigo_tarja)
    
 
class OperariosEnProgramaPH(ModeloBase):
    programa          = models.ForeignKey(ProgramaPH, on_delete=models.CASCADE)
    operario            = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    skill_operario      = models.CharField(max_length=10, choices=TIPOS_OPERARIO)       
    dias_trabajados     = models.ManyToManyField("self", through="planta_harina.DiaDeOperarioProgramaPH")
    
    class Meta:
        verbose_name = '1.1 - Operario en ProgramaPH'
        verbose_name_plural = '1.1 -Operarios en ProgramaPH'
        ordering = ['-fecha_creacion']
        constraints = [models.UniqueConstraint(
            name='%(app_label)s_%(class)s_unique_relationships',
            fields=['programa', 'operario', 'skill_operario']
        )]
        
    def __str__(self):
        return 'Operario %s %s en %s'%(self.operario.nombre, self.operario.apellido, self.programa)
    
class DiaDeOperarioProgramaPH(ModeloBase):
    operario = models.ForeignKey("planta_harina.OperariosEnProgramaPH", on_delete=models.CASCADE)
    dia = models.DateField(blank=True, null=True)
    kilos_dia = models.FloatField(default=0.0)
    ausente = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '1.2 - Dia de Operario en ProgramaPH'
        verbose_name_plural = '1.2 - Dias de Operarios en ProgramaPH'
        
    def __str__(self):
        return '%s %s'%(self.operario, self.dia)
    


class RechazoPrograma(ModeloBase):
    programa            = models.ForeignKey(ProgramaPH, on_delete=models.CASCADE, null=True)
    kilos_rechazo       = models.FloatField(default=0.0)
    observaciones       = models.CharField(max_length=160, blank=True, null=True)
    tipo_rechazo        = models.CharField(max_length=160, choices=TIPOS_RECHAZOS, default='---')
    registrado_por      = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Rechazo del Programa"
        verbose_name_plural = "1.4 Rechazos del Programa"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return 'Rechazos del Programa %s registrado con %s Kgs'%(self.programa, self.kilos_rechazo)

class VariablesProgramaPH(ModeloBase):
    programa                = models.OneToOneField(ProgramaPH, on_delete=models.CASCADE)
    lectura_gas_inicio      = models.IntegerField(blank=True, null=True)
    lectura_luz_inicio      = models.IntegerField(blank=True, null=True)
    lectura_gas_termino     = models.IntegerField(blank=True, null=True)
    lectura_luz_termino     = models.IntegerField(blank=True, null=True)
    estado                  = models.CharField(max_length=50, choices=ESTADO_VARIABLES, default='creada')
    creado_por              = models.ForeignKey('cuentas.User', null=True, on_delete=models.SET_NULL)
    
   
    class Meta:
        verbose_name = 'Variable Programa'
        verbose_name_plural = '1.3 Variables Programa'
        ordering = ['-fecha_creacion']

    def variables_inicio(self):
        return "Variables al inicio Programa Gas %s Variable Kwh %s" % (self.lectura_gas_inicio, self.lectura_luz_inicio)
    def variables_termino(self):
        return "Variables al termino Programa Gas %s Variable Kwh %s" % (self.lectura_gas_termino, self.lectura_luz_termino)
    def __str__(self):
        return 'Variables de programa N° %s'%(self.programa.pk)
    
# #### Proceso ####

class ProcesoPH(ModeloBaseHistorico):
    bin_bodegas         = models.ManyToManyField('bodegas.BinBodega', through='planta_harina.BinsParaProceso')
    bin_resultante      = models.ManyToManyField("self", through="planta_harina.BinResultanteProceso")
    tipo_proceso        = models.CharField(max_length=50, choices=TIPO_PROCESO)
    estado_proceso      = models.CharField(max_length=50, choices=ESTADO_PH,default='1')
    observaciones       = models.CharField(max_length=500, null=True, blank=True)
    kilos_inicio        = models.FloatField(default=0.0)
    kilos_merma         = models.FloatField(default=0.0)
    perdidaproceso      = models.CharField(max_length=1, choices=PERDIDAPROGRAMA, default='7')
    fecha_inicio_proceso         = models.DateField(null=True, blank=True)
    fecha_termino_proceso        = models.DateField(null=True, blank=True)
    creado_por          = models.ForeignKey('cuentas.User', null=True, on_delete=models.SET_NULL)
    operarios           = models.ManyToManyField('core.Operario', through='planta_harina.OperariosEnProcesoPH')
    
    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = '2. Procesos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return 'Proceso N° %s'%(self.pk)
    
class BinsParaProceso(ModeloBase):
    proceso                 = models.ForeignKey(ProcesoPH, null=True, on_delete=models.CASCADE)
    bin_bodega              = models.ForeignKey('bodegas.BinBodega', on_delete=models.CASCADE)
    procesado               = models.BooleanField(default=False)
  
    
    class Meta:
        verbose_name = "Bin para Proceso"
        verbose_name_plural = "2.1 Bins para Procesos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return 'Bin %s'%(self.bin_bodega)
    
class BinResultanteProceso(ModeloBaseHistorico):
    proceso                 = models.ForeignKey(ProcesoPH, null=True, on_delete=models.CASCADE)
    estado_bin              = models.CharField(max_length=50, choices=ESTADO_BIN_RESULTANTE_PH, default='1')
    tipo_resultante         = models.CharField(max_length=3, choices=TIPO_RESULTANTE_PH, blank=True, null=True)
    peso                    = models.FloatField(default=0.0)
    tipo_patineta           = models.FloatField(choices=TIPOS_BIN)
    codigo_tarja            = models.CharField(max_length=9, blank=True)
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_G5, default='-')
    esta_eliminado          = models.BooleanField(default=False)
    

    
    class Meta:
        verbose_name = "Bin Resultante Proceso"
        verbose_name_plural = "2.2 Bins Resultantes del Proceso"
        ordering = ('-fecha_creacion',)

    def __str__(self):
        return '%s'%(self.codigo_tarja)
    
class OperariosEnProcesoPH(ModeloBase):
    programa          = models.ForeignKey(ProcesoPH, on_delete=models.CASCADE)
    operario            = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    skill_operario      = models.CharField(max_length=10, choices=TIPOS_OPERARIO)       
    dias_trabajados     = models.ManyToManyField("self", through="planta_harina.DiaDeOperarioProcesoPH")
    
    class Meta:
        verbose_name = '1.1 - Operario en ProcesoPH'
        verbose_name_plural = '1.1 -Operarios en ProcesoPH'
        ordering = ['-fecha_creacion']
        constraints = [models.UniqueConstraint(
            name='%(app_label)s_%(class)s_unique_relationships',
            fields=['programa', 'operario', 'skill_operario']
        )]
        
    def __str__(self):
        return 'Operario %s %s en %s'%(self.operario.nombre, self.operario.apellido, self.programa)
    
class DiaDeOperarioProcesoPH(ModeloBase):
    operario = models.ForeignKey("planta_harina.OperariosEnProcesoPH", on_delete=models.CASCADE)
    dia = models.DateField(blank=True, null=True)
    kilos_dia = models.FloatField(default=0.0)
    ausente = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '1.2 - Dia de Operario en ProcesoPH'
        verbose_name_plural = '1.2 - Dias de Operarios en ProcesoPH'
        
    def __str__(self):
        return '%s %s'%(self.operario, self.dia)
    
    
class RechazoProcesoPH(ModeloBase):
    proceso             = models.ForeignKey(ProcesoPH, on_delete=models.CASCADE)
    kilos_fruta         = models.FloatField(default=0.0)
    observaciones       = models.TextField(blank=True, null=True)
    tipo_rechazo        = models.CharField(max_length=160, choices=TIPOS_RECHAZOS)
    registrado_por      = models.ForeignKey('cuentas.User', null=True, on_delete=models.SET_NULL)
    autorizado          = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Rechazo del Programa"
        verbose_name_plural = "2.4 Rechazos del Programa"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return 'Rechazos del Proceso n° %s registrado con %s Kgs'%(self.proceso.pk, self.kilos_fruta)
    
class VariablesProcesoPH(ModeloBaseHistorico):
    proceso                 = models.OneToOneField(ProcesoPH, on_delete=models.CASCADE)
    lectura_gas_inicio      = models.IntegerField(blank=True, null=True)
    lectura_luz_inicio      = models.IntegerField(blank=True, null=True)
    lectura_gas_termino     = models.IntegerField(blank=True, null=True)
    lectura_luz_termino     = models.IntegerField(blank=True, null=True)
    estado                  = models.CharField(max_length=50, choices=ESTADO_VARIABLES, default='creada')
    creado_por              = models.ForeignKey('cuentas.User', null=True, on_delete=models.SET_NULL)
    
   
    class Meta:
        verbose_name = 'Variable Proceso'
        verbose_name_plural = '2.3 Variables Proceso'
        ordering = ['-fecha_creacion']

    def variables_inicio(self):
        return "Variables al inicio Proceso Gas %s Variable Kwh %s" % (self.lectura_gas_inicio, self.lectura_luz_inicio)
    def variables_termino(self):
        return "Variables al termino Proceso Gas %s Variable Kwh %s" % (self.lectura_gas_termino, self.lectura_luz_termino)
    def __str__(self):
        return 'Variable Proceso: %s'%(self.pk)