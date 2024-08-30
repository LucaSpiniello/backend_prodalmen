from .models import *
from django.db.models import Sum, Q
from django.utils.timezone import now
from datetime import timedelta

def get_kilos_por_hora(programa_id):
    programa = ProgramaPH.objects.get(pk=programa_id)
    if programa.terminado_el and programa.iniciado_el:
        duracion = (programa.terminado_el - programa.iniciado_el).total_seconds() / 3600  # Duración en horas
        kilos_procesados = programa.kilos_inicio - programa.kilos_merma
        kilos_por_hora = kilos_procesados / duracion if duracion > 0 else 0
    else:
        kilos_por_hora = 0
    return kilos_por_hora

def get_porcentaje_merma(programa_id):
    programa = ProgramaPH.objects.get(pk=programa_id)
    if programa.kilos_inicio > 0:
        porcentaje_merma = (programa.kilos_merma / programa.kilos_inicio) * 100
    else:
        porcentaje_merma = 0
    return porcentaje_merma

def get_produccion_por_operario(programa_id):
    operarios = OperariosEnProgramaPH.objects.filter(programa_id=programa_id).annotate(
        total_kilos=Sum('kilos')
    ).values('operario__nombre', 'operario__apellido', 'total_kilos')
    return list(operarios)

def get_estado_bins(programa_id):
    total_bins = BinParaPrograma.objects.filter(programa_id=programa_id).count()
    bins_procesados = BinParaPrograma.objects.filter(programa_id=programa_id, procesado=True).count()
    return {
        'total_bins': total_bins,
        'bins_procesados': bins_procesados,
        'bins_no_procesados': total_bins - bins_procesados
    }

def get_rechazos_programa(programa_id):
    rechazos = RechazoPrograma.objects.filter(programa_id=programa_id).values(
        'tipo_rechazo', 'kilos_rechazo', 'observaciones'
    )
    return list(rechazos)
  
def get_variables_programa(programa_id):
    variables = VariablesProgramaPH.objects.filter(programa_id=programa_id).values(
        'lectura_gas_inicio', 'lectura_luz_inicio', 'lectura_gas_termino', 'lectura_luz_termino'
    )
    return list(variables)




from datetime import datetime

def get_last_two_state_changes(programa_id, start_state, end_state):
    """Obtiene los dos últimos cambios de estado relevantes entre start_state y end_state."""
    programa = ProgramaPH.objects.get(pk=programa_id)
    programa.refresh_from_db()  # Refresca la instancia para asegurar la actualización de datos

    history = programa.historia.all().order_by('-history_date')

    # Encuentra el último cambio a end_state
    last_end_state = history.filter(estado_programa=end_state).first()
    if not last_end_state:
        return 0  # Si nunca ha alcanzado end_state, no calcular duración

    # Encuentra el último cambio a start_state antes del cambio a end_state
    last_start_state = history.filter(history_date__lt=last_end_state.history_date, estado_programa=start_state).first()
    if not last_start_state:
        return 0  # Si no hay registro de start_state antes del end_state, no calcular duración

    # Calcular la duración entre estos dos puntos
    duration_seconds = (last_end_state.history_date - last_start_state.history_date).total_seconds()
    return max(duration_seconds, 0)  # Asegúrate de que la duración no sea negativa

def format_duration(seconds):
    """Convierte segundos a formato de días, horas, minutos y segundos."""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


def get_rechazos_agrupados(programa_id):
    rechazos = RechazoPrograma.objects.filter(programa_id=programa_id).values('tipo_rechazo').annotate(
        total_kilos_rechazo=Sum('kilos_rechazo')
    )
    
    # Agregar el display del tipo_rechazo
    for rechazo in rechazos:
        tipo_rechazo_display = RechazoPrograma._meta.get_field('tipo_rechazo').choices
        rechazo['tipo_rechazo_display'] = dict(tipo_rechazo_display).get(rechazo['tipo_rechazo'])
    
    return list(rechazos)



def get_rechazos_agrupados_proceso(proceso):
    rechazos = RechazoProcesoPH.objects.filter(proceso_id=proceso).values('tipo_rechazo').annotate(
        total_kilos_fruta=Sum('kilos_fruta')
    )
    
    
    
    # Convertir choices a un diccionario una sola vez para mejorar la eficiencia
    tipo_rechazo_display = dict(RechazoProcesoPH._meta.get_field('tipo_rechazo').choices)

    # Asignar el display de tipo_rechazo para cada rechazo
    for rechazo in rechazos:
        rechazo['tipo_rechazo_display'] = tipo_rechazo_display.get(rechazo['tipo_rechazo'])

    return list(rechazos)