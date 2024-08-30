from django.db import models
from django.utils import timezone
from core.models import *
from .estados_modelo import *
    
class InventarioBodega(ModeloBaseHistorico):
    tipo_inventario = models.CharField(max_length=50, choices=TIPO_INVENTARIO)
    binsbodega = models.ManyToManyField("bodegas.BinBodega", through="inventario.BinEnInventario")
    creado_por = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    bodegas = models.CharField(max_length=50)
    calles = models.CharField(max_length=250)
    estado = models.CharField(max_length=1, choices=ESTADOS_INVENTARIO, default='0')
    # estado_2 = models.CharField(max_length=1, choices=ESTADOS_INVENTARIO, default='0')
    
    class Meta:
        ordering = ['-fecha_creacion']
    
class BinEnInventario(ModeloBaseHistorico):
    inventario = models.ForeignKey(InventarioBodega, on_delete=models.CASCADE)
    binbodega = models.ForeignKey("bodegas.BinBodega", on_delete=models.CASCADE)
    validado  = models.BooleanField(default=False)
    validado_por = models.ForeignKey("cuentas.User", on_delete=models.CASCADE)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-validado']