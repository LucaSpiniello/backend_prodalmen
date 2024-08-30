from django.contrib import admin
from .models import PedidoMercadoInterno

# class FrutaFicticiaInline(admin.TabularInline):
#     model = FrutaFicticia
#     extra = 1
#     fields = ['nombre_producto', 'calidad', 'variedad', 'calibre', 'formato', 'kilos_solicitados', 'precio_kilo_neto', 'preparado']
#     readonly_fields = ['fecha_creacion', 'fecha_modificacion']

@admin.register(PedidoMercadoInterno)
class PedidoMercadoInternoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'cliente', 'retira_cliente', 'fecha_entrega', 'estado_pedido', 'fecha_creacion']
    list_filter = ['estado_pedido', 'retira_cliente', 'fecha_entrega']
    search_fields = ['cliente__nombre', 'numero_oc']
    # inlines = [FrutaFicticiaInline]
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('cliente', 'retira_cliente', 'sucursal', 'fecha_entrega', 'solicitado_por', 'numero_oc', 'archivo_oc', 'condicion_pago', 'estado_pedido', 'observaciones', 'quien_retira', 'tipo_venta', 'fecha_facturacion', 'valor_dolar_fact', 'numero_factura', 'fruta_pedido')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )
