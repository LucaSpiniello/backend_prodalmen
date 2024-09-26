from django.db import models
from cities_light.models import *
from core.models import *
from .estados_modelo import *
from django.contrib.contenttypes.fields import GenericForeignKey
#import City, Country




def guardado_carpetatributaria_mercadointerno(instance,filename):
        ext = filename
        file_path = 'mercadointerno/clienteID_{nm}/carpeta_tributaria/{ct}'.format(nm = instance.id, ct = ext)
        return file_path


class ClienteMercadoInterno(ModeloBase):
    rut_cliente           = models.CharField(max_length=50, unique=True)
    razon_social          = models.CharField(max_length=200)
    nombre_fantasia       = models.CharField(max_length=200, blank=True, null=True)
    telefono              = models.CharField(max_length=17,blank=True, null=True)
    region                = models.PositiveIntegerField(default=0)
    provincia             = models.PositiveIntegerField(default=0)
    comuna                = models.PositiveIntegerField(default=0)
    direccion             = models.CharField(max_length=250,blank=True,null=False)
    movil                 = models.CharField(max_length=17,blank=True, null=True)
    pagina_web            = models.URLField(blank=True,null=False)
    sucursales            = models.ManyToManyField('self',through='clientes.SucursalClienteMercado')
    email_cliente         = models.EmailField(max_length=50, blank=True, null=True)
    representante         = models.ManyToManyField('self',through='clientes.RRLL')
    ctacte                = models.ManyToManyField('self',through='clientes.Cta_Corriente')
    carpeta_tributaria    = models.FileField(upload_to=guardado_carpetatributaria_mercadointerno, blank=True)   
    creado_por            = models.ForeignKey('cuentas.User', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Cliente Mercado Interno'
        verbose_name_plural = 'Clientes de Mercado Interno'
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return "%s"% (self.razon_social)

class Cta_Corriente(models.Model):
    tipo_cuenta = models.CharField(max_length=1, choices=TIPO_CUENTA)
    numero_cuenta  = models.CharField(max_length=50)
    banco  = models.CharField(max_length=3, choices=BANCOS)
    cliente = models.ForeignKey(ClienteMercadoInterno, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Cuenta Bancaria Cliente'
        verbose_name_plural = 'Cuentas Bancarias Cliente'
    
    def __str__(self):
        return "%s N° %s del %s del cliente %s"% (self.get_tipo_cuenta_display(),self.numero_cuenta, self.get_banco_display(), self.cliente)


class SucursalClienteMercado(ModeloBase):
    cliente                    = models.ForeignKey(ClienteMercadoInterno, on_delete=models.CASCADE)
    nombre                     = models.CharField(max_length=50, blank=True, null=True)
    region                     = models.PositiveIntegerField(default=0)
    comuna                     = models.PositiveIntegerField(default=0)
    provincia                  = models.PositiveIntegerField(default=0)
    direccion                  = models.CharField(max_length=250,blank=True,null=True)
    telefono                   = models.CharField(max_length=50, blank=True, null=True)
    email_sucursal             = models.EmailField(max_length=50, blank=True, null=True)

    
    class Meta:
        verbose_name = 'Sucursal Cliente'
        verbose_name_plural = 'Sucursales Cliente'
        
    def __str__(self):
        return "%s"% (self.nombre)
    

class RRLL(ModeloBase):
    cliente          = models.ForeignKey(ClienteMercadoInterno, on_delete=models.SET_NULL, null=True, blank=True,)
    nombres          = models.CharField(max_length=200, blank=True, null=True)
    apellidos        = models.CharField(max_length=200, blank=True, null=True)
    telefono         = models.CharField(max_length=50, blank=True, null=True)
    direccion        = models.CharField(max_length=200, blank=True, null=True)
    email            = models.EmailField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Representante Legal'
        verbose_name_plural = 'Representantes Legales'
    def __str__(self):
        return "%s %s"% (self.nombres, self.apellidos)


class ClienteExportacion(ModeloBase):
    dni_cliente           = models.CharField(max_length=50)
    razon_social          = models.CharField(max_length=250)
    nombre_fantasia       = models.CharField(max_length=200, blank=True, null=True)
    telefono              = models.CharField(max_length=17,blank=True, null=True)
    direccion_1           = models.CharField(max_length=200,blank=True,null=False)
    direccion_2           = models.CharField(max_length=200,blank=True,null=False)
    ciudad                = models.ForeignKey(City, on_delete=models.DO_NOTHING, blank=True)
    pais                  = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank=True)
    codigo_postal         = models.CharField(max_length=100, blank=True,null=False)
    movil                 = models.CharField(max_length=17,blank=True, null=True)
    pagina_web            = models.URLField(blank=True,null=False)
    email_cliente         = models.EmailField(max_length=50, blank=True, null=True)
    sucursales            = models.ManyToManyField("self", through='clientes.SucursalClienteExportacion')
   
    class Meta:
       ordering = ['-fecha_creacion']

    def __str__(self):
        return "%s"% (self.razon_social)
    

class SucursalClienteExportacion(models.Model):
    nombre                = models.CharField(max_length=50, blank=True, null=True)
    cliente               = models.ForeignKey(ClienteExportacion, on_delete=models.CASCADE)
    direccion_1           = models.CharField(max_length=200,blank=True,null=False)
    direccion_2           = models.CharField(max_length=200,blank=True,null=False)
    ciudad                = models.ForeignKey(City, on_delete=models.DO_NOTHING, blank=True)
    pais                  = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank=True)
    codigo_postal         = models.CharField(max_length=100, blank=True,null=False)
    telefono              = models.CharField(max_length=17,blank=True, null=True)
    email_sucursal        = models.EmailField(max_length=45, blank=True, null=True)


    def __str__(self):
        return "%s"% (self.nombre)
    


