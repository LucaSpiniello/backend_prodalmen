from django.db import models
from core.models import *
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from mercadointerno.models import PedidoMercadoInterno
from exportacion.models import PedidoExportacion
from bodegas.models import BinBodega
from embalaje.models import PalletProductoTerminado, TipoEmbalaje
from guiassalida.models import GuiaSalidaFruta
from .estados_modelos import *

class Pedido(ModeloBaseHistorico):
    limite_opciones = models.Q(app_label='exportacion', model='pedidoexportacion') | models.Q(app_label='mercadointerno', model='pedidomercadointerno') | models.Q(app_label='guiassalida', model='guiasalidafruta')
    tipo_pedido = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limite_opciones)
    id_pedido = models.PositiveIntegerField()
    pedido = GenericForeignKey('tipo_pedido', 'id_pedido')
    frutas_en_pedido = models.ManyToManyField('pedidos.FrutaEnPedido', related_name="fruta_real")
    estado_pedido = models.CharField(max_length=1, choices=ESTADOS_PEDIDOS, default='0')
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        indexes = [
            models.Index(fields=['tipo_pedido', 'id_pedido']),
        ]
    
    def __str__(self):
        return f'{self.pedido}'

    @property
    def pedido_real(self):
        if self.tipo_pedido.model == 'pedidomercadointerno':
            return PedidoMercadoInterno.objects.get(id=self.id_pedido)
        elif self.tipo_pedido.model == 'pedidoexportacion':
            return PedidoExportacion.objects.get(id=self.id_pedido)
        elif self.tipo_pedido.model == 'guiasalidafruta':
            return GuiaSalidaFruta.objects.get(id=self.id_pedido)
        return None

class FrutaEnPedido(ModeloBaseHistorico):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="frutas")
    limite_opciones = models.Q(app_label='bodegas', model='binbodega') | models.Q(app_label='embalaje', model='palletproductoterminado')
    tipo_fruta = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limite_opciones)
    id_fruta = models.PositiveIntegerField()
    fruta = GenericForeignKey('tipo_fruta', 'id_fruta')
    cantidad = models.PositiveIntegerField()
    despachado = models.BooleanField(default=False)
    caja_origen = models.ForeignKey("embalaje.CajasEnPalletProductoTerminado", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Fruta en Pedido'
        verbose_name_plural = 'Frutas en Pedidos'
        indexes = [
            models.Index(fields=['tipo_fruta', 'id_fruta']),
        ]

    def __str__(self):
        return f'{self.tipo_fruta.model}'

    @property
    def fruta_real(self):
        if self.tipo_fruta.model == 'binbodega':
            return BinBodega.objects.get(id=self.id_fruta)
        elif self.tipo_fruta.model == 'palletproductoterminado':
            return PalletProductoTerminado.objects.get(id=self.id_fruta)
        return None
 
class FrutaFicticia(ModeloBase):
    limite_opciones = models.Q(app_label='exportacion', model='pedidoexportacion') | models.Q(app_label='mercadointerno', model='pedidomercadointerno') | models.Q(app_label='guiassalida', model='guiasalidafruta')
    tipo_pedido = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limite_opciones)
    id_pedido = models.PositiveIntegerField()
    pedido = GenericForeignKey('tipo_pedido', 'id_pedido')
    nombre_producto = models.CharField(max_length=1, choices=NOMBRE_PRODUCTO)
    calidad = models.CharField(max_length=12, choices=CALIDAD)
    variedad = models.CharField(max_length=10, choices=VARIEDAD)
    calibre = models.CharField(max_length=10, choices=CALIBRES, default='0')
    fruta_en_bin = models.BooleanField(default=False)
    formato = models.ForeignKey(TipoEmbalaje, on_delete=models.CASCADE, blank=True, null=True)
    kilos_solicitados = models.FloatField()
    precio_kilo_neto = models.FloatField()
    preparado = models.BooleanField(default=False)
