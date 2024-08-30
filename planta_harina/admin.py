from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(ProgramaPH)
admin.site.register(BinParaPrograma)
admin.site.register(BinResultantePrograma)
admin.site.register(OperariosEnProgramaPH)
admin.site.register(VariablesProgramaPH)
admin.site.register(RechazoPrograma)
admin.site.register(DiaDeOperarioProgramaPH)

admin.site.register(ProcesoPH)
admin.site.register(BinsParaProceso)
admin.site.register(BinResultanteProceso)
admin.site.register(OperariosEnProcesoPH)
admin.site.register(VariablesProcesoPH)
admin.site.register(RechazoProcesoPH)



