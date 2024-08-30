from django.db import models
from django.utils.text import slugify
from embalaje.models import TipoEmbalaje
from core.models import *
from .estados_modelo import *
from bodegas.estados_modelo import *

def guardado_oc_mercadointerno(instance, filename):
    ext = filename
    file_path = f'mercadointerno/clienteID_{instance.cliente.id}/orden_compra/{instance.fecha_creacion}/{ext}'
    return file_path

class PedidoMercadoInterno(ModeloBaseHistorico):
    cliente = models.ForeignKey("clientes.ClienteMercadoInterno", on_delete=models.CASCADE, related_name="pedidos_mercado_interno")
    retira_cliente = models.BooleanField(default=False)
    sucursal = models.ForeignKey("clientes.SucursalClienteMercado", on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos_mercado_interno")
    fecha_entrega = models.DateField(blank=True)
    solicitado_por = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos_mercado_interno")
    numero_oc = models.CharField(max_length=50, blank=True, null=True)
    archivo_oc = models.FileField(upload_to=guardado_oc_mercadointerno, blank=True, null = True)
    fruta_pedido = models.ManyToManyField('pedidos.FrutaFicticia', blank=True)
    condicion_pago = models.CharField(max_length=1, choices=CONDICION_PAGO_NOTAPEDIDO)
    estado_pedido = models.CharField(max_length=1, choices=ESTADO_NOTA_PEDIDO, default='1')
    observaciones = models.TextField(blank=True, null=True)
    quien_retira = models.CharField(max_length=50, blank=True, null=True)
    fecha_entrega_cliente = models.DateTimeField(blank=True, null=True)
    tipo_venta = models.CharField(max_length=1, choices=TIPO_VENTA, default='1')
    fecha_facturacion = models.DateField(blank=True, null=True)
    valor_dolar_fact = models.FloatField(default=0.0)
    numero_factura = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Pedido Mercado Interno'
        verbose_name_plural = 'Pedidos Mercado Interno'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['cliente']),
            models.Index(fields=['numero_oc']),
        ]

    def lista_fruta_pedido(self):
        return ", ".join([f"{p.calidad} {p.variedad} {p.formato}" for p in self.fruta_pedido.all()])

    def __str__(self):
        return f"Pedido Mercado Interno N° {self.pk}"

# class FrutaPedido(ModeloBase):
#     pedido = models.ForeignKey(PedidoMercadoInterno, on_delete=models.CASCADE)
#     nombre_producto = models.CharField(max_length=1, choices=NOMBRE_PRODUCTO)
#     calidad = models.CharField(max_length=12, choices=CALIDAD)
#     variedad = models.CharField(max_length=10, choices=VARIEDAD)
#     calibre = models.CharField(max_length=10, choices=CALIBRES, default='0')
#     formato = models.ForeignKey(TipoEmbalaje, on_delete=models.CASCADE)
#     kilos_solicitados = models.FloatField()
#     precio_kilo_neto = models.FloatField()
#     preparado = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = 'Fruta del Pedido'
#         verbose_name_plural = 'Frutas del Pedido'
#         indexes = [
#             models.Index(fields=['pedido']),
#             models.Index(fields=['nombre_producto']),
#         ]
#         ordering = ['-fecha_creacion']

#     def __str__(self):
#         return f"Fruta del {self.pedido}"
