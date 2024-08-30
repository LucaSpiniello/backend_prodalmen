from django.contrib import admin
from .models import Despacho, DespachoProducto

class DespachoProductoInline(admin.TabularInline):
    model = DespachoProducto
    extra = 1
    fields = ['fruta_en_pedido', 'cantidad']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']

@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'pedido', 'fecha_despacho', 'empresa_transporte', 'estado_despacho', 'creado_por', 'fecha_creacion']
    list_filter = ['estado_despacho', 'empresa_transporte', 'fecha_despacho']
    search_fields = ['pedido__id', 'empresa_transporte', 'nombre_chofer', 'rut_chofer']
    inlines = [DespachoProductoInline]
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('pedido', 'fecha_despacho', 'empresa_transporte', 'camion', 'nombre_chofer', 'rut_chofer', 'creado_por', 'estado_despacho', 'observaciones', 'despacho_parcial')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )

@admin.register(DespachoProducto)
class DespachoProductoAdmin(admin.ModelAdmin):
    list_display = ['despacho', 'fruta_en_pedido', 'cantidad', 'fecha_creacion']
    list_filter = ['despacho', 'fruta_en_pedido']
    search_fields = ['despacho__pedido__id', 'fruta_en_pedido__id']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('despacho', 'fruta_en_pedido', 'cantidad')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )
