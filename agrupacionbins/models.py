from django.db import models
from core.models import *
from .estados_modelo import *
from produccion.estados_modelo import TIPOS_BIN
from bodegas.estados_modelo import *
from controlcalidad.estados_modelo import *
import string, random
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation


def random_id(lenght=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))    

class AgrupacionDeBinsBodegas(ModeloBaseHistorico):
    bins_agrupados          = models.ManyToManyField('bodegas.BinBodega', blank=True)
    codigo_tarja            = models.CharField(max_length=9, blank=True, null=True)
    registrado_por          = models.ForeignKey('cuentas.User', on_delete=models.CASCADE)
    fruta_sobrante          = models.ForeignKey('agrupacionbins.FrutaSobranteDeAgrupacion', on_delete=models.SET_NULL, blank=True, null=True)
    transferir_bodega       = models.CharField(max_length=2, choices=BODEGAS_PRODALMEN)
    tipo_patineta           = models.FloatField(choices=TIPOS_BIN)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    kilos_fruta             = models.FloatField(default=0.0)
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calidad                 = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    calle_bodega            = models.CharField(max_length=3, choices=CALLE_BODEGA_4, default = '-')       
    agrupamiento_ok         = models.BooleanField(default=False)
    fumigado                = models.BooleanField(default=False) 

    class Meta:
        verbose_name = 'Agrupacion de BinBodega'
        verbose_name_plural = 'Agrupacion de BinBodegas'
        ordering = ['-pk']

    def __str__(self):
        return "%s"%(self.codigo_tarja)
    
    
    def save(self, *args, **kwargs):
        if not self.codigo_tarja:
            self.codigo_tarja = self.transferir_bodega+'-{}'.format(random_id())
        else:
            if self.codigo_tarja.startswith(self.transferir_bodega):
                pass
            else:
                self.codigo_tarja = self.transferir_bodega+'-{}'.format(random_id())
        super(AgrupacionDeBinsBodegas, self).save(*args, **kwargs)

    
class FrutaSobranteDeAgrupacion(ModeloBase):
    agrupacion              = models.ForeignKey("agrupacionbins.AgrupacionDeBinsBodegas", on_delete=models.CASCADE)
    binbodega               = models.ForeignKey("bodegas.BinBodega", on_delete=models.CASCADE)
    codigo_tarja            = models.CharField(max_length=9, blank=True, null=True)
    kilos_fruta             = models.FloatField(default=0.0)
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    variedad                = models.CharField(choices=VARIEDAD, max_length=3,default='---')
    calibre                 = models.CharField(choices=CALIBRES, max_length=2,default='0')
    calle_bodega            = models.CharField(max_length=2, choices=CALLE_BODEGA_4, default='-')
    estado_bin              = models.CharField(choices=ESTADO_BIN_G1, max_length=1, default='1')
    fumigado                = models.BooleanField(default=False)  
    fecha_fumigacion        = models.DateTimeField(blank=True, null=True) 
        
    class Meta:
        verbose_name = 'Fruta Sobrante de Agrupación de Bin'
        verbose_name_plural = 'Fruta Sobrante de Agrupación de Bin'
        ordering = ['-pk']

    def __str__(self):
        return "%s"%(self.codigo_tarja)