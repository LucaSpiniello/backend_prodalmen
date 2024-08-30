from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from import_export.admin import ImportExportModelAdmin
admin.site.site_header = 'Prodalweb V3 - Snabbit Tecnologias'
admin.site.unregister(Group)


class ImportacionCamion(ImportExportModelAdmin):
    pass
admin.site.register(Camion, ImportacionCamion)


class ImportacionChofer(ImportExportModelAdmin):
    pass
admin.site.register(Chofer, ImportacionChofer)

class ImportacionDeGrupos(ImportExportModelAdmin):
    pass 
admin.site.register(Group, ImportacionDeGrupos)


class ImportacionOperarios(ImportExportModelAdmin):
    pass
admin.site.register(Operario, ImportacionOperarios)

class ImportacionSkillsOperarios(ImportExportModelAdmin):
    pass
admin.site.register(SkillOperario, ImportacionSkillsOperarios)

@admin.register(EtiquetasZpl)
class EtiquetasZplAdmin(ImportExportModelAdmin):
    list_display = ['pk', 'nombre']

    
# @admin.register(Coloso)
# class ColosoAdmin(admin.ModelAdmin):
#     list_display = ('identificacion_coloso','tara', 'activo', 'fecha_creacion', )
# @admin.register(Tractor)
# class TractorAdmin(admin.ModelAdmin):
#     list_display = ('identificacion_tractor','tara', 'activo', 'fecha_creacion', )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).prefetch_related('etiquetas')

#     def lista_etiquetas(self, obj):
#         return u", ".join(o.name for o in obj.etiquetas.all())

# @admin.register(TractorColoso)
# class TractorColosoAdmin(admin.ModelAdmin):
#     list_display = ['pk', 'tractor', 'coloso_1', 'coloso_2', 'tara', 'fecha_creacion']
    