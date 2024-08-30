from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.contenttypes.models import ContentType
from pedidos.models import FrutaFicticia, Pedido, FrutaEnPedido

class FrutaEnPedidoInline(admin.TabularInline):
    model = FrutaEnPedido
    extra = 1
    fields = ['tipo_fruta', 'id_fruta', 'cantidad', 'despachado']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']

    # def get_fruta_real_link(self, obj):
    #     fruta_real = obj.fruta_real
    #     if fruta_real:
    #         content_type = ContentType.objects.get_for_model(fruta_real)
    #         url = reverse(f'admin:{content_type.app_label}_{content_type.model}_change', args=[fruta_real.pk])
    #         return format_html('<a href="{}">{}</a>', url, fruta_real)
    #     return "-"
    # get_fruta_real_link.short_description = 'Fruta Real'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_pedido', 'id_pedido', 'fecha_creacion']
    list_filter = ['tipo_pedido']
    search_fields = ['id_pedido']
    inlines = [FrutaEnPedidoInline]
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('tipo_pedido', 'estado_pedido', 'id_pedido')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )

    # def get_pedido_real_link(self, obj):
    #     pedido_real = obj.pedido_real
    #     if pedido_real:
    #         content_type = ContentType.objects.get_for_model(pedido_real)
    #         url = reverse(f'admin:{content_type.app_label}_{content_type.model}_change', args=[pedido_real.pk])
    #         return format_html('<a href="{}">{}</a>', url, pedido_real)
    #     return "-"
    # get_pedido_real_link.short_description = 'Pedido Real'
    # get_pedido_real_link.admin_order_field = 'id_pedido'

@admin.register(FrutaEnPedido)
class FrutaEnPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'tipo_fruta', 'id_fruta', 'cantidad', 'despachado', 'fecha_creacion']
    list_filter = ['tipo_fruta', 'despachado']
    search_fields = ['pedido__id', 'id_fruta']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        (None, {
            'fields': ('pedido', 'tipo_fruta', 'id_fruta', 'cantidad', 'despachado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
        }),
    )

    # def get_fruta_real_link(self, obj):
    #     fruta_real = obj.fruta_real
    #     if fruta_real:
    #         content_type = ContentType.objects.get_for_model(fruta_real)
    #         url = reverse(f'admin:{content_type.app_label}_{content_type.model}_change', args=[fruta_real.pk])
    #         return format_html('<a href="{}">{}</a>', url, fruta_real)
    #     return "-"
    # get_fruta_real_link.short_description = 'Fruta Real'

admin.site.register(FrutaFicticia)
# class FrutaFicticiaAdmin(admin.ModelAdmin):
#     list_display = ['pedido', 'nombre_producto', 'calidad', 'variedad', 'calibre', 'formato', 'kilos_solicitados', 'precio_kilo_neto', 'preparado', 'fecha_creacion']
#     list_filter = ['nombre_producto', 'calidad', 'variedad', 'preparado']
#     search_fields = ['pedido__pk', 'nombre_producto']
#     readonly_fields = ['fecha_creacion', 'fecha_modificacion']
#     fieldsets = (
#         (None, {
#             'fields': ('pedido', 'nombre_producto', 'calidad', 'variedad', 'calibre', 'formato', 'kilos_solicitados', 'precio_kilo_neto', 'preparado')
#         }),
#         ('Fechas', {
#             'fields': ('fecha_creacion', 'fecha_modificacion'),
#         }),
#     )
