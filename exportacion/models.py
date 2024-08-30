from django.db import models
from .estados_modelo import * 
from bodegas.estados_modelo import *
from simple_history.models import HistoricalRecords as Historia
from embalaje.models import TipoEmbalaje
from embalaje.estados_modelo import DESPACHO_EMBALAJE
from core.models import *

def guardado_archivo_pedidoexportacion(instance, filename):
    ext = filename
    file_path = f'exportaciones/pedido_N_{instance.id}/ordencompra/{ext}'
    return file_path

class PedidoExportacion(ModeloBaseHistorico):
    cliente = models.ForeignKey("clientes.ClienteExportacion", on_delete=models.SET_NULL, null=True)
    retira_cliente = models.BooleanField(default=False)
    tipo_venta = models.CharField(max_length=200, blank=True, null=True)
    empresa_naviera = models.CharField(max_length=100, blank=True, null=True)
    buque = models.CharField(max_length=100, blank=True, null=True)
    sucursal_destino = models.ForeignKey("clientes.SucursalClienteExportacion", on_delete=models.SET_NULL, null=True, blank=True)
    puerto_descarga = models.CharField(max_length=100, blank=True, null=True)
    fecha_envio = models.DateField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    fruta_pedido = models.ManyToManyField('pedidos.FrutaFicticia', blank=True)
    moneda_venta = models.CharField(max_length=1, choices=MONEDA_VENTA, default='1')
    tipo_flete = models.CharField(max_length=3, choices=TIPO_FLETE, default='CIF')
    estado_pedido = models.CharField(max_length=1, choices=ESTADO_PEDIDO_EXPORTACION, default='1')
    creado_por = models.ForeignKey("cuentas.User", on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True, null=True)
    empresa_transporte = models.CharField(max_length=100, blank=True, null=True)
    camion = models.CharField(max_length=100, blank=True, null=True)
    nombre_chofer = models.CharField(max_length=100, blank=True, null=True)
    rut_chofer = models.CharField(max_length=100, blank=True, null=True)
    numero_factura = models.CharField(max_length=50, blank=True, null=True)
    terrestre = models.BooleanField(default=False)
    archivo_oc = models.FileField(upload_to=guardado_archivo_pedidoexportacion, blank=True, null=True)
    numero_oc = models.CharField(max_length=50, blank=True, null=True)
    tipo_despacho = models.CharField(max_length=1, choices=DESPACHO_EMBALAJE, default='0')
    fecha_facturacion = models.DateField(blank=True, null=True)
    valor_dolar = models.FloatField(default=0.0)


    class Meta:
        verbose_name = 'Pedido Exportacion'
        verbose_name_plural = 'Pedidos Exportaciones'
        indexes = [
            models.Index(fields=['cliente']),
            models.Index(fields=['numero_oc']),
        ]

    def __str__(self):
        return f'Pedido Exportacion N° {self.pk}'

# class FrutaPedido(ModeloBase):
#     exportacion = models.ForeignKey(PedidoExportacion, on_delete=models.CASCADE)
#     nombre_producto = models.CharField(max_length=1, choices=NOMBRE_PRODUCTO)
#     calidad = models.CharField(max_length=12, choices=CALIDAD)
#     variedad = models.CharField(max_length=10, choices=VARIEDAD)
#     calibre = models.CharField(max_length=10, choices=CALIBRES, default='0')
#     formato = models.ForeignKey(TipoEmbalaje, on_delete=models.CASCADE, related_name="formato_exportacion")
#     kilos_solicitados = models.FloatField()
#     precio_kilo_neto = models.FloatField()
#     preparado = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = 'Fruta Pedido Exportacion'
#         verbose_name_plural = 'Frutas Pedidos Exportaciones'
#         indexes = [
#             models.Index(fields=['exportacion']),
#             models.Index(fields=['nombre_producto']),
#         ]

#     def __str__(self):
#         return f'{self.nombre_producto}'