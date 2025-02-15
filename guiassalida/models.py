from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from core.models import ModeloBaseHistorico, ModeloBase
from embalaje.models import TipoEmbalaje
from bodegas.estados_modelo import NOMBRE_PRODUCTO, CALIBRES, CALIDAD, VARIEDAD
from .estados_modelo import *


class GuiaSalidaFruta(ModeloBaseHistorico):
    limite_opciones         = models.Q(app_label='productores', model='productor') | models.Q(app_label='clientes', model='clientemercadointerno') | models.Q(app_label='cuentas', model='user') | models.Q(app_label='clientes', model='clienteexportacion')
    tipo_cliente            = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, limit_choices_to=limite_opciones)
    id_cliente              = models.PositiveIntegerField(null=True, blank=True)
    cliente                 = GenericForeignKey('tipo_cliente', 'id_cliente')
    fecha_entrega           = models.DateField(null=True, blank=True)
    retira_cliente          = models.BooleanField(default=False)
    fruta_pedido            = models.ManyToManyField('pedidos.FrutaFicticia', blank=True)
    observaciones           = models.TextField(blank=True, null=True)
    solicitado_por          = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    quien_retira            = models.CharField(max_length=50, blank=True, null=True)
    tipo_salida             = models.CharField(max_length=2, choices=TIPOS_GUIA_SALIDA, default='0')
    estado_guia_salida      = models.CharField(max_length=2, choices=ESTADO_GUIA_SALIDA, default='0')
    guia_autorizada         = models.BooleanField(default=False)
    comercializador = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Guia de Salida Fruta'
        verbose_name_plural= 'Guias de Salida Fruta'
        
    def __str__(self):
        return "Guia Salida Fruta N° %s"% (self.pk) 
    
    
# class FrutaEnGuiaSalida(ModeloBase):
#     guiasalida = models.ForeignKey(GuiaSalidaFruta, on_delete=models.CASCADE)
#     nombre_producto = models.CharField(max_length=1, choices=NOMBRE_PRODUCTO)
#     calidad = models.CharField(max_length=12, choices=CALIDAD)
#     variedad = models.CharField(max_length=10, choices=VARIEDAD)
#     calibre = models.CharField(max_length=10, choices=CALIBRES, default='0')
#     formato = models.ForeignKey(TipoEmbalaje, on_delete=models.CASCADE)
#     kilos_solicitados = models.FloatField()
#     precio_kilo_neto = models.FloatField(blank = True, null = True)
#     preparado = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = 'Fruta de la Guia Salida'
#         verbose_name_plural = 'Frutas en la Guia de Salida'
#         indexes = [
#             models.Index(fields=['guiasalida']),
#             models.Index(fields=['nombre_producto']),
#         ]
#         ordering = ['-fecha_creacion']

#     def __str__(self):
#         return f"Fruta del {self.guiasalida}"
