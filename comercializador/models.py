from django.db import models


class Comercializador(models.Model):     
    nombre                = models.CharField(max_length=64)
    razon_social          = models.CharField(max_length=64, blank=True, null=True)
    giro                  = models.CharField(max_length=64, blank=True, null=True)
    direccion             = models.CharField(max_length=64, blank=True, null=True)
    zip_code              = models.CharField(max_length=64, blank=True, null=True)
    email_comercializador = models.EmailField(max_length=45, blank=True, null=True)



    class Meta:

        verbose_name = ('Comercializador')
        verbose_name_plural = ('Comercializadores')
       
    def __str__(self):
        return "%s"% (self.nombre)
    
    
    

    
