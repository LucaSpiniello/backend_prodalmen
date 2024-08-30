from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models import constraints
from phonenumber_field.modelfields import PhoneNumberField
from django.dispatch import receiver
from django.db.models.signals import post_save
from cities_light.models import City, Country
from .estados_modelo import *
from recepcionmp.estados_modelo import VARIEDADES_MP
from simple_history.models import HistoricalRecords as Historia
# from dbexternas.models import CitiesLightCountry, CitiesLightCity

# CitiesLightCountry.objects.using('db_paises')
# CitiesLightCity.objects.using('db_paises')


                                            
class Productor(models.Model):

    rut_productor         = models.CharField(max_length=10, unique=True)
    nombre                = models.CharField(max_length=64)
    usuarios              = models.ManyToManyField("cuentas.User",through='UsuariosProductor')
    telefono              = PhoneNumberField(blank=True, null=True)
    region                = models.PositiveIntegerField(blank=True, null=True)
    provincia             = models.PositiveIntegerField(blank=True, null=True)
    comuna                 = models.PositiveIntegerField(blank=True, null=True)
    direccion             = models.CharField(max_length=64,blank=True,null=True)
    movil                 = PhoneNumberField(blank=True, null=True)
    pagina_web            = models.CharField(blank=True,null=True)
    email                 = models.EmailField(max_length=100, blank=True, null=True)
    fecha_creacion        = models.DateTimeField(auto_now_add=True)
    numero_contrato       = models.IntegerField(default=0)
       
    class Meta:

        verbose_name = ('1.0 - Productor')
        verbose_name_plural = ('1.0 - Productores')
  

    def __str__(self):

        return "%s"% (self.nombre)

class UsuariosProductor(models.Model):

    usuario  =  models.ForeignKey("cuentas.User",on_delete=models.CASCADE)
    productor  = models.ForeignKey(Productor,on_delete=models.CASCADE)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields =['usuario','productor'],name = 'userproduc')]
    


class ContratoProductor(models.Model):
    productor               = models.ForeignKey('productores.Productor', on_delete=models.CASCADE, blank=True, null=True)
    fruta_contrato          = models.ManyToManyField('self', through='productores.FrutaContratoProductor')
    total_kilos_contrato    = models.FloatField(default=0.0)
    fecha_contrato          = models.DateField()
    precio_x_proceso        = models.FloatField(default=145)
    minimo_garantizado      = models.FloatField(null=True, blank=True)
    comision                = models.FloatField(default=7)
    costos_adm_ventas       = models.FloatField(default=0.55)
    creado_por              = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True, blank=True)
    historia                = Historia()
    
    class Meta:
        verbose_name = '2.0 - Contrato Productor'
        verbose_name_plural = '2.0 - Contratos Productores'
    
    def __str__(self):
        return "Contrato de %s del %s"%(self.productor, self.fecha_contrato)

class FrutaContratoProductor(models.Model):
    contrato            = models.ForeignKey(ContratoProductor, on_delete=models.CASCADE)
    variedad            = models.CharField(max_length=2, choices=VARIEDADES_MP)
    kilos_fruta         = models.FloatField(default=0.0)
    minimo_garantizado  = models.FloatField(default=3.8)
    historia            = Historia()
    
    class Meta:
        verbose_name = '2.1 - Fruta Contrato Productor'
        verbose_name_plural = '2.1 - Fruta Contratos Productores'
    
    def __str__(self):
        return "%s Kgs, %s de contrato N°%s"%(self.kilos_fruta, self.get_variedad_display(), self.contrato)
    
class PagoAnticipado(models.Model):
    contrato = models.ForeignKey('productores.ContratoProductor', on_delete=models.CASCADE)
    monto   = models.FloatField(default=0.0)
    valor_dolar = models.FloatField(default=0.0)
    fecha_pago = models.DateField()
    registrado_por = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    historia = Historia()
    
    class Meta:
        verbose_name = '2.2 - Pago Anticipado'
        verbose_name_plural = '2.2 - Pagos Anticipados'
        
    def __str__(self):
        return 'Anticipo Productor %s el %s'%(self.contrato.productor, self.fecha_pago)
    
class Liquidacion(models.Model):
    contrato = models.ForeignKey('productores.ContratoProductor', on_delete=models.CASCADE)
    tipo_liquidacion = models.CharField(max_length=1, choices=TIPO_LIQUIDACION)
    valor_dolar = models.FloatField(default=0.0)
    fecha_liquidacion = models.DateField()
    registrado_por = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    quien_recibe = models.CharField(max_length=70, null=True, blank=True)
    estado_liquidacion = models.CharField(max_length=1, choices=ESTADO_LIQUIDACION, default='1')
    valor_total = models.FloatField(default=0.0)
    historia = Historia()
    
    class Meta:
        verbose_name = '2.3 - Liquidacion'
        verbose_name_plural = '2.3 - Liquidaciones'
        
    def __str__(self):
        return 'Liquidación N°%s Contrato N°%s, registrado el %s'%(self.pk, self.contrato.pk, self.fecha_liquidacion)

class PagoProductor(models.Model):
    contrato            = models.ForeignKey('productores.ContratoProductor', on_delete=models.CASCADE)
    estado_pago         = models.CharField(max_length=1, choices=ESTADO_PAGO, default='1')
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_modificacion  = models.DateTimeField(auto_now=True)
    historia = Historia()
    
    class Meta:
        verbose_name = '3.0 - Pago Productor'
        verbose_name_plural = '3.0 - Pagos Productores'
        
    def __str__(self):
        return "Pago de productor %s"%(self.contrato.productor)
    
class CalculoPrecioFinal(models.Model):
    contrato = models.ForeignKey('productores.ContratoProductor', on_delete=models.CASCADE)
    costos_comex = models.FloatField(default=0.0)
    precio_x_venta = models.FloatField(default=0.0)
    costo_unit_adm_vtas = models.FloatField(default=0.0)
    prom_anual_dolar = models.FloatField(default=0.0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    historia = Historia()
    
    class Meta:
        verbose_name = '2.4 - Calculo Precio Final'
        verbose_name_plural = '2.4 - Calculos Precios Finales'
        
    def __str__(self):
        return '%s'%(self.contrato.pk)