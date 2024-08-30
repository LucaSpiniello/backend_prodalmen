import django_filters
from django_filters import rest_framework as filters
from .models import Operario, SkillOperario
from django.db.models import Q


class OperarioFilter(filters.FilterSet):
    #nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    #apellido = django_filters.CharFilter(field_name='apellido', lookup_expr='icontains')
    skill = django_filters.CharFilter(method='filter_by_skill')

    class Meta:
        model = Operario
        fields = ['skill']

    def filter_by_skill(self, queryset, name, value):
        skills = value.split(',')
        skill_queries = Q()
        for skill in skills:
            skill_queries |= Q(skilloperario__tipo_operario__icontains=skill.strip())
        return queryset.filter(skill_queries).distinct()