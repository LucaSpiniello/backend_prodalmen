from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Produccion)
admin.site.register(LotesPrograma)
admin.site.register(TarjaResultante)


admin.site.register(Reproceso)
admin.site.register(BinsEnReproceso)
admin.site.register(TarjaResultanteReproceso)


class DiaDeOperarioReprocesoInline(admin.TabularInline):
    model = DiaDeOperarioReproceso
    extra = 1



class DiaDeOperarioProduccionInline(admin.TabularInline):
    model = DiaDeOperarioProduccion
    extra = 1
    

@admin.register(OperariosEnProduccion)
class OperariosEnProduccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'operario','skill_operario')
    inlines = [DiaDeOperarioProduccionInline]
    
@admin.register(OperariosEnReproceso)
class OperariosEnReprocesoAdmin(admin.ModelAdmin):
    list_display = ('id', 'operario','skill_operario')
    inlines = [DiaDeOperarioReprocesoInline]