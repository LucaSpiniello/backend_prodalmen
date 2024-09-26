from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bodegas.models import *
from .estados_modelo import *
from core.models import *
import random, string
from simple_history.models import HistoricalRecords


def directorio_tipo_embalaje_embalaje(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'embalaje/{0}/tipo_embalaje/{1}'.format(instance.pk, filename)

def directorio_etiquetas_embalaje(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'embalaje/{0}/etiquetas/{1}'.format(instance.pk, filename)

def random_id(lenght=6):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(lenght))    

class TipoEmbalaje(ModeloBase):
    nombre = models.CharField(max_length=50)
    peso = models.IntegerField(default=0, null=True, blank=True)
    archivo_impresora_cajas = models.FileField(upload_to=directorio_tipo_embalaje_embalaje, blank=True,)
    archivo_impresora_termica = models.FileField(upload_to=directorio_tipo_embalaje_embalaje, blank=True,)

    def __str__(self):
            return '%s de %s Kilos'%(self.nombre, self.peso)

class EtiquetaEmbalaje(ModeloBase):
    nombre = models.CharField(max_length=50)
    archivo_impresora_cajas = models.FileField(upload_to=directorio_etiquetas_embalaje, blank=True,)
    archivo_impresora_termica = models.FileField(upload_to=directorio_etiquetas_embalaje, blank=True,)
    def __str__(self):
        return '%s'%self.nombre        

class Embalaje(ModeloBaseHistorico):
    fruta_bodega            = models.ManyToManyField("bodegas.BinBodega", through='embalaje.FrutaBodega')
    pallets                 = models.ManyToManyField("self", through='embalaje.PalletProductoTerminado')
    tipo_embalaje           = models.ForeignKey(TipoEmbalaje, on_delete=models.SET_NULL, null=True) 
    etiquetado              = models.ForeignKey(EtiquetaEmbalaje, on_delete=models.SET_NULL, null=True)
    configurado_por         = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    estado_embalaje         = models.CharField(max_length=1, choices=ESTADOS_PROGRAMA_EMBALAJE, default='1')
    observaciones           = models.TextField(blank= True, max_length=200)
    fecha_inicio_embalaje   = models.DateField(blank=True, null = True)
    fecha_termino_embalaje  = models.DateField(blank=True, null = True)
    tipo_producto           = models.CharField(max_length=1, choices=NOMBRE_PRODUCTO, blank=True)
    calidad                 = models.CharField(max_length=12, choices=CALIDAD, blank=True)
    calibre                 = models.CharField(max_length=10, choices=CALIBRES, blank=True)
    variedad                = models.CharField(max_length=10, choices=VARIEDAD, blank=True)
    kilos_solicitados       = models.FloatField(default=0.0)
    merma_programa          = models.FloatField(default=0.0)
    operarios               = models.ManyToManyField('core.Operario', through='embalaje.OperariosEnEmbalaje')

    def lista_tipo_fruta(self):
        return ",".join([str(p) for p in self.fruta_bodega.all()])

    class Meta:
        verbose_name = '1.0 - Programa Embalaje'
        verbose_name_plural = '1.0 - Programas de Embalaje'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return 'Programa Embalaje N° %s'%self.pk

class FrutaBodega(ModeloBaseHistorico):
    embalaje                = models.ForeignKey("embalaje.Embalaje", on_delete=models.CASCADE) 
    bin_bodega              = models.ForeignKey("bodegas.BinBodega", on_delete=models.CASCADE)
    procesado               = models.BooleanField(default=False)

    class Meta:
        verbose_name = '1.1 - Bin De Bodega En Programa'
        verbose_name_plural = '1.1 - Bins De Bodegas En Programas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return 'Bin %s'%self.bin_bodega

class OperariosEnEmbalaje(ModeloBase):
    programa          = models.ForeignKey(Embalaje, on_delete=models.CASCADE)
    operario            = models.ForeignKey('core.Operario', on_delete=models.CASCADE)
    skill_operario      = models.CharField(max_length=10, choices=TIPOS_OPERARIO)       
    dias_trabajados     = models.ManyToManyField("self", through="embalaje.DiaDeOperarioEmbalaje")

    class Meta:
        verbose_name = '1.1 - Operario en Embalaje'
        verbose_name_plural = '1.1 -Operarios en Embalaje'
        ordering = ['-fecha_creacion']
        constraints = [models.UniqueConstraint(
            name='%(app_label)s_%(class)s_unique_relationships',
            fields=['programa', 'operario', 'skill_operario']
        )]

    def __str__(self):
        return 'Operario %s %s en %s'%(self.operario.nombre, self.operario.apellido, self.programa)

class DiaDeOperarioEmbalaje(ModeloBase):
    operario = models.ForeignKey("embalaje.OperariosEnEmbalaje", on_delete=models.CASCADE)
    dia = models.DateField(blank=True, null=True)
    kilos_dia = models.FloatField(default=0.0)
    ausente = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = '1.2 - Dia de Operario en Embalaje'
        verbose_name_plural = '1.2 - Dias de Operarios en Embalaje'
        
    def __str__(self):
        return '%s %s'%(self.operario, self.dia)

class PalletProductoTerminado(ModeloBase):
    embalaje = models.ForeignKey("embalaje.Embalaje", on_delete=models.CASCADE)
    # numero_pallet = models.PositiveIntegerField(default=0)
    calle_bodega = models.CharField(max_length=2, choices=CALLES_PALLETS)
    cajas_en_pallet = models.ManyToManyField('self', through='embalaje.CajasEnPalletProductoTerminado')
    observaciones = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    codigo_pallet = models.CharField(max_length=10, null=True, blank=True)
    estado_pallet = models.CharField(max_length=15, choices=ESTADOS_PALLETS_PRODUCTO_TERMINADO, default = '0')
    peso_inicial = models.FloatField(null=True, blank=True)
    historia = HistoricalRecords(inherit=True)

    
    class Meta:
        verbose_name = '1.2 - Pallet Producto Terminado'
        verbose_name_plural = '1.2 - Pallets Productos Terminados'
        ordering = ['-fecha_creacion']

    @property
    def peso_total_pallet(self):
        total_peso = sum(
            caja.cantidad_cajas * caja.peso_x_caja for caja in self.cajasenpalletproductoterminado_set.all()
        )
        return total_peso

    @property
    def total_cajas(self):
        total_cajas = sum(
            caja.cantidad_cajas for caja in self.cajasenpalletproductoterminado_set.all()
        )
        return total_cajas

    def cajas_pedidas(self):
        # Obtener la cantidad de cajas pedidas en los pedidos
        from pedidos.models import FrutaEnPedido
        fruta_en_pedido = FrutaEnPedido.objects.filter(
            tipo_fruta=ContentType.objects.get_for_model(PalletProductoTerminado),
            id_fruta=self.id
        )
        return sum(fep.cantidad for fep in fruta_en_pedido)

    # def agregar_cajas_por_kilos(self, kilos, razon):
    #     print(f"Agregando {kilos} kilos al pallet {self.codigo_pallet} por {razon}")
    #     for caja in self.cajasenpalletproductoterminado_set.all():
    #         print(f"Procesando caja con {caja.cantidad_cajas} cajas de {caja.peso_x_caja} kg cada una")
    #         if kilos <= 0:
    #             break
    #         peso_disponible = caja.cantidad_cajas * caja.peso_x_caja
    #         print(f"Peso disponible en caja: {peso_disponible} kg")
    #         if kilos <= peso_disponible:
    #             cantidad_a_agregar = kilos / caja.peso_x_caja
    #             caja.cantidad_cajas += int(cantidad_a_agregar)
    #             print(f"Agregando {int(cantidad_a_agregar)} cajas")
    #             kilos = 0
    #         else:
    #             cantidad_a_agregar = caja.cantidad_cajas
    #             caja.cantidad_cajas += cantidad_a_agregar
    #             print(f"Agregando {cantidad_a_agregar} cajas")
    #             kilos -= peso_disponible
    #         caja.save(update_fields=['cantidad_cajas'])

    #     self.save_with_reason(razon)

    # def descontar_cajas_por_kilos(self, kilos, razon):
    #     print(f"Descontando {kilos} kilos del pallet {self.codigo_pallet} por {razon}")
    #     for caja in self.cajasenpalletproductoterminado_set.all():
    #         print(f"Procesando caja con {caja.cantidad_cajas} cajas de {caja.peso_x_caja} kg cada una")
    #         if kilos <= 0:
    #             break
    #         peso_disponible = caja.cantidad_cajas * caja.peso_x_caja
    #         print(f"Peso disponible en caja: {peso_disponible} kg")
    #         if kilos <= peso_disponible:
    #             cantidad_a_descontar = kilos / caja.peso_x_caja
    #             cajas_a_descontar = int(cantidad_a_descontar)
    #             caja.cantidad_cajas -= cajas_a_descontar
    #             print(f"Descontando {cajas_a_descontar} cajas")
    #             kilos -= cajas_a_descontar * caja.peso_x_caja
    #         else:
    #             kilos -= peso_disponible
    #             cajas_a_descontar = caja.cantidad_cajas
    #             caja.cantidad_cajas = 0
    #             print(f"Descontando todas las {cajas_a_descontar} cajas de esta caja")
    #         caja.save(update_fields=['cantidad_cajas'])

    #     self.save_with_reason(razon)
    def agregar_cajas_por_kilos(self, kilos, razon, fruta_en_pedido=None):
        print(f"Agregando {kilos} kilos al pallet {self.codigo_pallet} por {razon}")
        
        if fruta_en_pedido and fruta_en_pedido.caja_origen:
            caja = fruta_en_pedido.caja_origen
            print(f"Devolviendo cajas a la caja original con ID {caja.id}")

            peso_disponible = caja.cantidad_cajas * caja.peso_x_caja
            cantidad_a_agregar = kilos / caja.peso_x_caja
            caja.cantidad_cajas += int(cantidad_a_agregar)
            print(f"Agregando {int(cantidad_a_agregar)} cajas a la caja con ID {caja.id}")
            caja.save(update_fields=['cantidad_cajas'])
        else:
            # Iterar sobre cajas existentes y agregar kilos
            cajas_restantes = kilos
            for caja in self.cajasenpalletproductoterminado_set.all():
                if cajas_restantes <= 0:
                    break
                print(f"Procesando caja con {caja.cantidad_cajas} cajas de {caja.peso_x_caja} kg cada una")
                peso_disponible = caja.cantidad_cajas * caja.peso_x_caja
                if cajas_restantes <= peso_disponible:
                    cantidad_a_agregar = cajas_restantes / caja.peso_x_caja
                    caja.cantidad_cajas += int(cantidad_a_agregar)
                    print(f"Agregando {int(cantidad_a_agregar)} cajas")
                    cajas_restantes = 0
                else:
                    cantidad_a_agregar = caja.cantidad_cajas
                    caja.cantidad_cajas += cantidad_a_agregar
                    print(f"Agregando {cantidad_a_agregar} cajas")
                    cajas_restantes -= peso_disponible
                caja.save(update_fields=['cantidad_cajas'])

        self.save_with_reason(razon)


    def descontar_cajas_por_kilos(self, kilos, razon, fruta_en_pedido=None):
        print(f"Descontando {kilos} kilos del pallet {self.codigo_pallet} por {razon}")
        for caja in self.cajasenpalletproductoterminado_set.all():
            print(f"Procesando caja con {caja.cantidad_cajas} cajas de {caja.peso_x_caja} kg cada una")
            if kilos <= 0:
                break
            peso_disponible = caja.cantidad_cajas * caja.peso_x_caja
            print(f"Peso disponible en caja: {peso_disponible} kg")
            if kilos <= peso_disponible:
                cantidad_a_descontar = kilos / caja.peso_x_caja
                cajas_a_descontar = int(cantidad_a_descontar)
                caja.cantidad_cajas -= cajas_a_descontar
                print(f"Descontando {cajas_a_descontar} cajas")
                kilos -= cajas_a_descontar * caja.peso_x_caja
                
                # Registrar el origen de las cajas en FrutaEnPedido
                if fruta_en_pedido:
                    fruta_en_pedido.caja_origen = caja
                    fruta_en_pedido.save(update_fields=['caja_origen'])
            else:
                kilos -= peso_disponible
                cajas_a_descontar = caja.cantidad_cajas
                caja.cantidad_cajas = 0
                print(f"Descontando todas las {cajas_a_descontar} cajas de esta caja")
                
                # Registrar el origen de las cajas en FrutaEnPedido
                if fruta_en_pedido:
                    fruta_en_pedido.caja_origen = caja
                    fruta_en_pedido.save(update_fields=['caja_origen'])

            caja.save(update_fields=['cantidad_cajas'])

        self.save_with_reason(razon)

        

    def save_with_reason(self, reason, *args, **kwargs):
        self._change_reason = reason
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.codigo_pallet)

    def save(self, *args, **kwargs):
        if not self.codigo_pallet:
            self.codigo_pallet = 'PPT-{}'.format(random_id())
        super(PalletProductoTerminado, self).save(*args, **kwargs)
        
        
        
class CajasEnPalletProductoTerminado(ModeloBaseHistorico):
    pallet = models.ForeignKey("embalaje.PalletProductoTerminado", on_delete=models.CASCADE)
    tipo_caja = models.ForeignKey("embalaje.TipoEmbalaje", on_delete=models.SET_NULL, null=True)
    cantidad_cajas = models.IntegerField(default=0)
    peso_x_caja = models.FloatField(default=0.0)
    registrado_por = models.ForeignKey('cuentas.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Caja Pallet Producto Terminado'
        verbose_name_plural = 'Cajas en Pallet Productos Terminado'
        ordering = ['-fecha_creacion']

    # @property
    # def _history_cantidad_cajas(self):
    #     return self.historia.filter(cantidad_cajas=self.cantidad_cajas)

    # @_history_cantidad_cajas.setter
    # def _history_cantidad_cajas(self, value):
    #     self.cantidad_cajas = value

    def __str__(self):
        return '%s %s de %s Kgs' % (self.cantidad_cajas, self.tipo_caja, self.peso_x_caja)
