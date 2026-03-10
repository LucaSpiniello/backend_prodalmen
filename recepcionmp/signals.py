from django.db.models.signals import post_save, pre_save, pre_delete
from bodegas.models import PatioTechadoExterior
from .models import *
from controlcalidad.models  import *
from django.dispatch import receiver
from datetime import datetime
from django.contrib.contenttypes.models import *



def sugerir_numero_faltante(numeros):
    numeros = sorted(numeros)
    for i in range(1, len(numeros) + 1):
        if i != numeros[i - 1]:
            return i
    return len(numeros) + 1

@receiver(post_save, sender=RecepcionMp)
def crear_cc_y_generar_numero_lote(sender, instance, created, **kwargs):
    if created and instance:
        CCRecepcionMateriaPrima.objects.update_or_create(recepcionmp=instance)
        numeros_lote_existentes = RecepcionMp.objects.all().exclude(numero_lote=0).values_list('numero_lote', flat=True)       
        instance.numero_lote = sugerir_numero_faltante(numeros_lote_existentes)
        instance.save()
        
@receiver(pre_delete, sender=GuiaRecepcionMP)
def eliminar_lote_guia_y_patio_techado_exterior(sender, instance, **kwargs):
    if instance:
        for lote in instance.recepcionmp_set.all():
            ct = ContentType.objects.get_for_model(RecepcionMp)
            patio = PatioTechadoExterior.objects.filter(tipo_recepcion = ct.pk, id_recepcion = lote.pk)
            if patio.exists():
                patio.delete()
                