

from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

# Register your models here.


# class UsuariosProductorInline(admin.TabularInline):

#     model = UsuariosProductor
#     extra = 1



class ImportacionProductor(ImportExportModelAdmin):
    pass
admin.site.register(Productor, ImportacionProductor)

  
@admin.register(PagoProductor)
class PagoProductorAdmin(admin.ModelAdmin):
    list_display = ['pk', 'estado_pago']
    
class FrutaContratoInline(admin.TabularInline):
    model = FrutaContratoProductor
    extra = 1
    
@admin.register(ContratoProductor)
class ContratoProductorAdmin(admin.ModelAdmin):
    list_display = ['pk',  'fecha_contrato']
    inlines = [FrutaContratoInline]

@admin.register(FrutaContratoProductor)
class FrutaContratoAdmin(admin.ModelAdmin):
    list_display = ['pk',  'variedad', 'kilos_fruta']

@admin.register(PagoAnticipado)
class PagoAnticipadoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'monto', 'fecha_pago']
    
@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'contrato', 'tipo_liquidacion', 'fecha_liquidacion']
    
@admin.register(CalculoPrecioFinal)
class CalculoPrecioFinalAdmin(admin.ModelAdmin):
    list_display = ['pk', 'contrato', 'fecha_creacion']
