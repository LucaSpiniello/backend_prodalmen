from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Embalaje, FrutaBodega, OperariosEnEmbalaje, PalletProductoTerminado, CajasEnPalletProductoTerminado, TipoEmbalaje, EtiquetaEmbalaje

class FrutaBodegaInline(admin.TabularInline):
    model = FrutaBodega
    extra = 1
    fields = ['bin_bodega', 'procesado']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']


# @admin.action(description='Agregar cajas por kilos')
# def agregar_cajas_action(modeladmin, request, queryset):
#     for pallet in queryset:
#         kilos = int(request.POST['kilos'])  # Aquí deberías tener una forma de obtener los kilos, por ejemplo un input en la interfaz de admin.
#         razon = request.POST['razon']  # Razón de la modificación
#         pallet.agregar_cajas_por_kilos(kilos, razon)

# @admin.action(description='Descontar cajas por kilos')
# def descontar_cajas_action(modeladmin, request, queryset):
#     for pallet in queryset:
#         kilos = int(request.POST['kilos'])  # Aquí deberías tener una forma de obtener los kilos, por ejemplo un input en la interfaz de admin.
#         razon = request.POST['razon']  # Razón de la modificación
#         pallet.descontar_cajas_por_kilos(kilos, razon)


class PalletProductoTerminadoInline(admin.TabularInline):
    model = PalletProductoTerminado
    extra = 1
    fields = ['calle_bodega', 'codigo_pallet', 'estado_pallet', 'observaciones', 'registrado_por']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'codigo_pallet']
    

class CajasEnPalletProductoTerminadoInline(admin.TabularInline):
    model = CajasEnPalletProductoTerminado
    extra = 1
    fields = ['tipo_caja', 'cantidad_cajas', 'peso_x_caja', 'registrado_por']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']

@admin.register(Embalaje)
class EmbalajeAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_embalaje', 'etiquetado', 'configurado_por', 'estado_embalaje', 'fecha_creacion']
    list_filter = ['estado_embalaje', 'tipo_producto', 'calidad', 'calibre', 'variedad']
    search_fields = ['id']
    inlines = [FrutaBodegaInline, PalletProductoTerminadoInline]
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('tipo_embalaje', 'etiquetado', 'configurado_por', 'estado_embalaje', 'observaciones')
        }),
        ('Producto', {
            'fields': ('tipo_producto', 'calidad', 'calibre', 'variedad', 'kilos_solicitados', 'merma_programa')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'fecha_inicio_embalaje', 'fecha_termino_embalaje'),
        }),
    )

@admin.register(PalletProductoTerminado)
class PalletProductoTerminadoAdmin(admin.ModelAdmin):
    list_display = ['embalaje', 'calle_bodega', 'codigo_pallet', 'estado_pallet', 'fecha_creacion']
    list_filter = ['estado_pallet', 'calle_bodega']
    search_fields = ['codigo_pallet']
    inlines = [CajasEnPalletProductoTerminadoInline]
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'codigo_pallet']
    fieldsets = (
        (None, {
            'fields': ('embalaje', 'calle_bodega', 'codigo_pallet', 'estado_pallet', 'observaciones', 'registrado_por')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )
    #actions = [agregar_cajas_action, descontar_cajas_action]

@admin.register(FrutaBodega)
class FrutaBodegaAdmin(admin.ModelAdmin):
    list_display = ['embalaje', 'bin_bodega', 'procesado', 'fecha_creacion']
    list_filter = ['procesado']
    search_fields = ['embalaje__id', 'bin_bodega__id']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('embalaje', 'bin_bodega', 'procesado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )

# @admin.register(OperariosEnEmbalaje)
# class OperariosEnEmbalajeAdmin(admin.ModelAdmin):
#     list_display = ['embalaje', 'operario', 'kilos', 'dia', 'fecha_creacion']
#     list_filter = ['dia']
#     search_fields = ['embalaje__id', 'operario__nombre']
#     readonly_fields = ['fecha_creacion', 'fecha_modificacion']
#     fieldsets = (
#         (None, {
#             'fields': ('embalaje', 'operario', 'kilos', 'dia')
#         }),
#         ('Fechas', {
#             'fields': ('fecha_creacion', 'fecha_modificacion'),
#         }),
#     )

@admin.register(CajasEnPalletProductoTerminado)
class CajasEnPalletProductoTerminadoAdmin(admin.ModelAdmin):
    list_display = ['pallet', 'tipo_caja', 'cantidad_cajas', 'peso_x_caja', 'registrado_por', 'fecha_creacion']
    list_filter = ['tipo_caja']
    search_fields = ['pallet__codigo_pallet', 'tipo_caja__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('pallet', 'tipo_caja', 'cantidad_cajas', 'peso_x_caja', 'registrado_por')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )

@admin.register(TipoEmbalaje)
class TipoEmbalajeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'peso', 'fecha_creacion']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('nombre', 'peso', 'archivo_impresora_cajas', 'archivo_impresora_termica')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )

@admin.register(EtiquetaEmbalaje)
class EtiquetaEmbalajeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_creacion']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('nombre', 'archivo_impresora_cajas', 'archivo_impresora_termica')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )
