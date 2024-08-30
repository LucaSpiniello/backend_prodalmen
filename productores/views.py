from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.permissions import  IsAuthenticated
from rest_framework import viewsets


class ProductorViewSet(viewsets.ModelViewSet):
    queryset = Productor.objects.all()
    serializer_class = ProductorSerializer
    # permission_classes = [IsAuthenticated]
    
    


