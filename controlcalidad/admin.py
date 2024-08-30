from django.contrib import admin
from .models import *

class MuestrasEnCCRecepcionMPInline(admin.TabularInline):
     model = CCRendimiento
     extra = 1

@admin.register(CCRecepcionMateriaPrima)
class CCRecepcionMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('recepcionmp', 'cc_registrado_por', 'estado_cc','fecha_modificacion')
    inlines = [MuestrasEnCCRecepcionMPInline]


admin.site.register(CCRendimiento)
admin.site.register(CCPepa)

admin.site.register(CCTarjaResultante)
admin.site.register(CCTarjaResultanteReproceso)

admin.site.register(CCBinResultanteProcesoPH)
admin.site.register(CCBinResultanteProgramaPH)

# Register your models here.

@admin.register(CCTarjaSeleccionada)
class CCTarjaSeleccionadaAdmin(admin.ModelAdmin):
    list_display = ('tarja_seleccionada', 'cc_registrado_por', 'estado_cc')