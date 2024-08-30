import django_filters
from .models import CCRecepcionMateriaPrima
from recepcionmp.models import EnvasesGuiaRecepcionMp, RecepcionMp
from django.db.models import Subquery, OuterRef


class CCRecepcionMateriaPrimaFilter(django_filters.FilterSet):
    cc_registrado_por_id = django_filters.NumberFilter(field_name='cc_registrado_por__id')
    humedad_min = django_filters.NumberFilter(field_name='humedad', lookup_expr='gte')
    humedad_max = django_filters.NumberFilter(field_name='humedad', lookup_expr='lte')
    presencia_insectos = django_filters.BooleanFilter(field_name='presencia_insectos')
    estado_cc = django_filters.CharFilter(field_name='estado_cc', lookup_expr='exact')
    estado_aprobacion_cc = django_filters.CharFilter(field_name='estado_aprobacion_cc', lookup_expr='exact')
    esta_contramuestra = django_filters.CharFilter(field_name='esta_contramuestra', lookup_expr='exact')
    fecha_creacion_desde = django_filters.DateTimeFilter(field_name='fecha_creacion', lookup_expr='gte')
    fecha_creacion_hasta = django_filters.DateTimeFilter(field_name='fecha_creacion', lookup_expr='lte')
    fecha_modificacion_desde = django_filters.DateTimeFilter(field_name='fecha_modificacion', lookup_expr='gte')
    fecha_modificacion_hasta = django_filters.DateTimeFilter(field_name='fecha_modificacion', lookup_expr='lte')
    variedad = django_filters.CharFilter(method='filter_variedad')
    productor = django_filters.CharFilter(method='filter_productor')


    class Meta:
        model = CCRecepcionMateriaPrima
        fields = [
            'cc_registrado_por_id', 'humedad_min', 'humedad_max', 'presencia_insectos',
            'estado_cc', 'estado_aprobacion_cc', 'esta_contramuestra', 
            'fecha_creacion_desde', 'fecha_creacion_hasta',
            'fecha_modificacion_desde', 'fecha_modificacion_hasta', 'variedad', 'productor'
        ]

    def filter_variedad(self, queryset, name, value):
        recepciones_con_variedad = Subquery(
            EnvasesGuiaRecepcionMp.objects.filter(
                recepcionmp_id=OuterRef('recepcionmp_id'),
                variedad=value
            ).values('recepcionmp_id')
        )       
        return queryset.filter(
            recepcionmp_id__in=recepciones_con_variedad
        )
    def filter_productor(self, queryset, name, value):
        recepciones_con_productor = Subquery(
            RecepcionMp.objects.filter(
                guiarecepcion__productor__nombre__icontains=value,
                pk=OuterRef('recepcionmp__pk')
            ).values('pk')
        )

        return queryset.filter(
            recepcionmp__pk__in=recepciones_con_productor
        )