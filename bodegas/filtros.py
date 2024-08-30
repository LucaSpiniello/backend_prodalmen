# import django_filters
# from .models import BinBodega

# class BinBodegaFilter(django_filters.FilterSet):
#     calidad = django_filters.CharFilter(method='filter_by_calidad')
#     variedad = django_filters.CharFilter(method='filter_by_variedad')
#     calibre = django_filters.CharFilter(method='filter_by_calibre')
    

#     class Meta:
#         model = BinBodega
#         fields = []

#     def filter_by_calidad(self, queryset, name, value):
#         filtered_queryset = [obj for obj in queryset if obj.calidad and value.lower() in obj.calidad.lower()]
#         return queryset.filter(id__in=[obj.id for obj in filtered_queryset])

#     def filter_by_variedad(self, queryset, name, value):
#         filtered_queryset = [obj for obj in queryset if obj.variedad and value.lower() in obj.variedad.lower()]
#         return queryset.filter(id__in=[obj.id for obj in filtered_queryset])

#     def filter_by_calibre(self, queryset, name, value):
#         filtered_queryset = [obj for obj in queryset if obj.calibre and value.lower() in obj.calibre.lower()]
#         return queryset.filter(id__in=[obj.id for obj in filtered_queryset])

import django_filters
from .models import BinBodega
from inventario.funciones import *

class BinBodegaFilter(django_filters.FilterSet):
    calidad = django_filters.CharFilter(method='filtrar_por_calidad')
    variedad = django_filters.CharFilter(method='filtrar_por_variedad')
    calibre = django_filters.CharFilter(method='filtrar_por_calibre')
    codigo_tarja_bin = django_filters.CharFilter(method='filtrar_por_codigo_tarja_bin')
    calle_bodega = django_filters.CharFilter(method='filtrar_por_calle_bodega')

    class Meta:
        model = BinBodega
        fields = []

    def filtrar_por_codigo_tarja_bin(self, queryset, name, value):
        return queryset.filter(id__in=[obj.id for obj in filtrar_por_codigo_tarja_bin(queryset, value)])

    def filtrar_por_calidad(self, queryset, name, value):
        return queryset.filter(id__in=[obj.id for obj in filtrar_por_calidad(queryset, value)])

    def filtrar_por_variedad(self, queryset, name, value):
        return queryset.filter(id__in=[obj.id for obj in filtrar_por_variedad(queryset, value)])

    def filtrar_por_calibre(self, queryset, name, value):
        return queryset.filter(id__in=[obj.id for obj in filtrar_por_calibre(queryset, value)])

    def filtrar_por_calle_bodega(self, queryset, name, value):
        return queryset.filter(id__in=[obj.id for obj in filtrar_por_calle_bodega(queryset, value)])
