from django.db.models.signals import post_save
from .models import *
from django.dispatch import receiver
from recepcionmp.models import RecepcionMp, EnvasesGuiaRecepcionMp
from django.db.models import Count, Sum, Avg, FloatField, F
from django.contrib.contenttypes.models import ContentType
from recepcionmp.models import GuiaRecepcionMP
import math


@receiver(post_save, sender = ClienteMercadoInterno)
def creacion_de_sucursal_casa_matriz(sender, created, instance, **kwargs):
  if created and instance:
    SucursalClienteMercado.objects.create(
      nombre = 'Casa Matriz',
      cliente = instance,
      region = instance.region,
      provincia = instance.provincia,
      comuna = instance.comuna,
      direccion = instance.direccion,
      telefono = instance.telefono,
      email_sucursal = instance.email_cliente
    )
    
@receiver(post_save, sender = ClienteExportacion)
def creacion_de_sucursal_casa_matriz_exportacion(sender, created, instance, **kwargs):
  if created and instance:
    SucursalClienteExportacion.objects.create(
      nombre = 'Casa Matriz',
      cliente = instance,
      direccion_1 = instance.direccion_1,
      direccion_2 = instance.direccion_2,
      ciudad      = instance.ciudad,
      pais        = instance.pais,
      codigo_postal = instance.codigo_postal,
      telefono    = instance.telefono,
      email_sucursal = instance.email_cliente
    )
    