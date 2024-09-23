from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from .estados_modelo import GENEROS
from core.estados_modelo import *

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        
        if not email:
            raise ValueError("La Dirección de Correo Electronico es Requerido")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        
        return user
    
    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        
        if kwargs.get('is_active') is not True:
            raise ValueError("El super usuario debe estar activo")
        
        if kwargs.get('is_staff') is not True:
            raise ValueError("El super usuario debe ser staff")
        
        if kwargs.get('is_superuser') is not True:
            raise ValueError("No es super usuario")
        
        return self.create_user(email, password, **kwargs)
    
def get_dir_image(instance, filename):
    return 'usuario/{0}/{1}'.format(instance.pk, filename)

class User(AbstractBaseUser, PermissionsMixin):
    email               = models.EmailField(max_length=250, unique=True)
    first_name          = models.CharField(max_length=250)
    second_name         = models.CharField(max_length=250, blank=True, null=True)
    last_name           = models.CharField(max_length=250)
    second_last_name    = models.CharField(max_length=250, blank=True, null=True)
    is_active           = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)
    image               = models.ImageField(upload_to=get_dir_image, blank=True, null=True)
    rut                 = models.CharField(max_length=50, unique=True, blank=True, null=True)
    celular             = models.CharField(max_length=17, blank=True, null=True)
    genero              = models.CharField(max_length=2, choices=GENEROS, default='0')
    fecha_nacimiento    = models.DateField(null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def get_nombre_completo(self):
        return f'{self.first_name} {self.second_name} {self.last_name} {self.second_last_name}'
    
    def get_nombre(self):
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        return self.email
      

class PersonalizacionPerfil(models.Model):
    usuario = models.OneToOneField("cuentas.User", on_delete=models.CASCADE, related_name="personalizacion")
    activa = models.BooleanField(default= False)
    estilo = models.CharField(max_length = 15, choices = ESTILO_CHOICES, default= 'minimal-theme')
    cabecera = models.CharField(max_length = 1, choices = CABECERA_CHOICES, default= '4')
    anio = models.CharField(max_length=4, choices=ANIO, default='2024')
    iot_balanza_recepcionmp = models.CharField(max_length=50, choices=ESTADO_IOT_BALANZA_RECEPCIONMP, default='Automático')

    class Meta:
        verbose_name = ('Personalizacion Perfil')
        verbose_name_plural = ('Personalizacion Perfiles')
