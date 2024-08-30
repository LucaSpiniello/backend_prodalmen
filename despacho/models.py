from django.db import models
from core.models import *
from cuentas.models import User
from pedidos.models import Pedido, FrutaEnPedido
from .estados_modelo import *

class Despacho(ModeloBaseHistorico):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='despachos')
    fecha_despacho = models.DateTimeField(blank=True, null=True)
    empresa_transporte = models.CharField(max_length=100, blank=True, null=True)
    camion = models.CharField(max_length=100, blank=True, null=True)
    nombre_chofer = models.CharField(max_length=100, blank=True, null=True)
    rut_chofer = models.CharField(max_length=100, blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='despachos_creados')
    estado_despacho = models.CharField(max_length=1, choices=ESTADO_DESPACHO, default='0')
    observaciones = models.TextField(blank=True, null=True)
    despacho_parcial = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Despacho'
        verbose_name_plural = 'Despachos'
        indexes = [
            models.Index(fields=['pedido']),
        ]

    def __str__(self):
        return f'Despacho del Pedido {self.pedido}'

class DespachoProducto(ModeloBaseHistorico):
    despacho = models.ForeignKey(Despacho, on_delete=models.CASCADE, related_name='productos_despacho')
    fruta_en_pedido = models.ForeignKey(FrutaEnPedido, on_delete=models.CASCADE, related_name='despachos_producto')
    cantidad = models.FloatField()

    class Meta:
        verbose_name = 'Despacho Producto'
        verbose_name_plural = 'Despacho Productos'
        indexes = [
            models.Index(fields=['despacho']),
        ]

    def __str__(self):
        return f'Despacho de {self.fruta_en_pedido} en Despacho {self.despacho}'
