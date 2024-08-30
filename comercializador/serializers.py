from rest_framework import serializers
from .models import *

class ComercializadorSerializer(serializers.ModelSerializer):
  class Meta:
    model = Comercializador
    fields = '__all__'