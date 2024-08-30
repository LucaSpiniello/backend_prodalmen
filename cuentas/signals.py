from django.db.models.signals import post_save
from .models import *
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def crear_personalizacion_usuario(sender, instance, created, **kwargs):
    
    if instance and created:
        PersonalizacionPerfil.objects.update_or_create(usuario = instance)