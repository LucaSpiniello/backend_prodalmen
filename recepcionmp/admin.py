from django.contrib import admin
from .models import *

from import_export.admin import ImportExportModelAdmin

class RecepcionMpInline(admin.TabularInline):
     model = RecepcionMp
     extra = 1
     
class EnvasesGuiaRecepcionMpInline(admin.TabularInline):
     model = EnvasesGuiaRecepcionMp
     extra = 1

@admin.register(RecepcionMp)
class RecepcionAdmin(admin.ModelAdmin):
    list_display = ('numero_lote', 'guiarecepcion', 'estado_recepcion','creado_por')
    inlines = [EnvasesGuiaRecepcionMpInline]

@admin.register(GuiaRecepcionMP)
class GuiaRecepcionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'productor', 'numero_guia_productor')
    inlines = [RecepcionMpInline]



@admin.register(EnvasesGuiaRecepcionMp)

class EnvasesMpAdmin(admin.ModelAdmin):
    list_display = ('recepcionmp', 'envase', 'cantidad_envases','variedad',)
    
 

class ExportacionEnvasesMp(ImportExportModelAdmin):
#   #  resource_class = EnvasesMpAdmin
    pass
     
admin.site.register(EnvasesMp, ExportacionEnvasesMp)



@admin.register(RecepcionColoso)
class RecepcionColosoAdmin(admin.ModelAdmin):

    list_display = ('numero_vale','operario', 'tractor_coloso', 'fecha_recepcion')



class ColososALoteInline(admin.TabularInline):

     model = ColososAlLote
     extra = 1



@admin.register(ColososEnLote)
class ColososEnLoteAdmin(admin.ModelAdmin):
    list_display = ('id','creado_por', 'estado_lote',)
    inlines = [ColososALoteInline,]
    
    
# admin.site.register(LoteRecepcionMpRechazadoPorCC)

@admin.register(LoteRecepcionMpRechazadoPorCC)
class LoteRecepcionMpRechazadoPorCCAdmin(admin.ModelAdmin):
    list_display = ('id','recepcionmp', )