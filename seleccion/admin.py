from django.contrib import admin
from .models import *
from simple_history.admin import SimpleHistoryAdmin


admin.site.register(Seleccion)
admin.site.register(BinsPepaCalibrada)
admin.site.register(TarjaSeleccionada)  



#admin.site.register(OperariosEnSeleccion, SimpleHistoryAdmin)
admin.site.register(SubProductoOperario, SimpleHistoryAdmin)
admin.site.register(BinSubProductoSeleccion, SimpleHistoryAdmin)  


class DiaDeOperarioSeleccionInline(admin.TabularInline):
    model = DiaDeOperarioSeleccion
    extra = 1
    

@admin.register(OperariosEnSeleccion)
class OperariosEnSeleccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'operario','skill_operario')
    inlines = [DiaDeOperarioSeleccionInline]