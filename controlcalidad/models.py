from django.db import models
from recepcionmp.estados_modelo import *
from simple_history.models import HistoricalRecords as Historia
from controlcalidad.estados_modelo import *
from .estados_modelo import *
from bodegas.estados_modelo import *
from core.models import *

def fotos_cc(instance, filename):
    return 'controlcalidad_recepcionmp/CDC_{0}/fotos_cc/{1}'.format(instance.pk, filename)

def fotos_cc_li(instance, filename):
    return 'controlcalidad_recepcionmp/Lote_{0}/fotos_cc/{1}'.format(instance.ccloteinterno.pk, filename)

def fotos_cc_tarja_seleccionada(instance, filename):
    return 'controlcalidad_seleccion/{0}/tarja/{1}'.format(instance.seleccion.pk, filename)




class CCRecepcionMateriaPrima(models.Model):
    recepcionmp = models.ForeignKey("recepcionmp.RecepcionMp", on_delete=models.CASCADE)
    cc_registrado_por = models.ForeignKey("cuentas.User", verbose_name="usuario_cc", on_delete=models.CASCADE, blank=True, null=True)
    #estado_cr = models.CharField(choices=ESTADOS_CONTROL_RENDIMIENTO, default='a', max_length=1)
    humedad = models.FloatField(blank=True, null=True)
    presencia_insectos = models.BooleanField(blank=True, null=True, default=False)
    observaciones = models.CharField(max_length=300, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado_cc = models.CharField(choices=ESTADO_CONTROL,max_length=1,default='2')
    control_rendimiento = models.ManyToManyField('self', through='CCRendimiento')
    historia = Historia()
    estado_aprobacion_cc = models.CharField(max_length=1, choices=ESTADO_APROBACION_CC_X_JEFATURA, default='0')
    fotos_cc = models.ManyToManyField('self', through='FotosCC')
    esta_contramuestra = models.CharField(max_length=1, choices=ESTADO_CONTRAMUESTRA, default='0')
    mailEnviado = models.BooleanField(default=False)
    class Meta:
        verbose_name = ('CC Recepcion Mp')
        verbose_name_plural = ('1.0 - CC Recepcion Materia Prima')
        ordering = ('-pk', )

    def __str__(self):
        return "Control Calidad Lote N° %s"% (self.recepcionmp.pk)

class FotosCC(models.Model):
    ccrecepcionmp = models.ForeignKey("controlcalidad.CCRecepcionMateriaPrima", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=fotos_cc, blank=True, verbose_name='Fotos Control', null=True)
    

class CCRendimiento(models.Model):    
    cc_recepcionmp = models.ForeignKey("controlcalidad.CCRecepcionMateriaPrima", on_delete=models.CASCADE)
    #cc_guiarecepcionmp = models.ForeignKey("controlcalidad.CCGuiaRecepcionMateriaPrima", on_delete=models.SET_NULL, null=True)
    peso_muestra =  models.FloatField(blank=True, null =True, default=0.0)
    basura = models.FloatField(blank=True, null =True, default=0.0)
    pelon = models.FloatField(blank=True, null =True, default=0.0)
    cascara = models.FloatField(blank=True, null =True, default=0.0)
    pepa_huerto = models.FloatField(blank=True, null =True, default=0.0)
    pepa = models.FloatField(blank=True, null =True, default=0.0)
    ciega = models.FloatField(default=0.0)
    registrado_por = models.ForeignKey("cuentas.User", on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    historia = Historia()
    aprobado_cc = models.BooleanField(default=False)
    es_contramuestra = models.BooleanField(default=False)
    

    class Meta:
        verbose_name = ('Muestra Lote RecepcionMP')
        verbose_name_plural = ('1.1 - Muestra Lote RecepcionMP')
        ordering = ('-pk', )

    def __str__(self):
        return "Muestra CC Lote N° %s"% (self.pk)



class CCPepa(models.Model):
    cc_rendimiento          = models.OneToOneField("controlcalidad.CCRendimiento", on_delete=models.CASCADE, related_name='cdcpepa')    
    fecha_creacion          = models.DateTimeField(auto_now_add=True)
    fecha_modificacion      = models.DateTimeField(auto_now=True)
    peso_muestra_calibre    = models.FloatField(blank=True, null =True, default=0.0)
    muestra_variedad        = models.FloatField(blank=True, null =True, default=0.0)
    daño_insecto            = models.FloatField(blank=True, null =True,default=0.0)
    hongo                   = models.FloatField(blank=True, null =True,default=0.0)
    doble                   = models.FloatField(blank=True, null =True,default=0.0)
    fuera_color             = models.FloatField(blank=True, null =True,default=0.0)
    vana_deshidratada       = models.FloatField(blank=True, null =True,default=0.0)
    punto_goma              = models.FloatField(blank=True, null =True,default=0.0)
    goma                    = models.FloatField(blank=True, null =True,default=0.0)       
    cc_pepaok               = models.BooleanField(default=False)
    cc_calibrespepaok       = models.BooleanField(default=False)
    pre_calibre             = models.FloatField(blank=True, null =True, default=0.0)
    calibre_18_20           = models.FloatField(blank=True, null =True, default=0.0)
    calibre_20_22           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_23_25           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_25_27           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_27_30           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_30_32           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_32_34           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_34_36           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_36_40           = models.FloatField(blank=True, null =True,default=0.0)
    calibre_40_mas          = models.FloatField(blank=True, null =True,default=0.0)
    observaciones           = models.CharField(max_length=300, blank=True, null=True)
    historia                = Historia()
    desviacion          = models.FloatField(blank=True, null =True,default=0.0)


    
    class Meta:
        verbose_name = ('CC Pepa muestra')
        verbose_name_plural = ('1.2 - CC Pepa muestras')
        ordering = ('-pk', )
    def __str__(self):
        return "CC de Pepa asociada a Muestra %s"% (self.cc_rendimiento.pk)   
    
### Modulo Produccion ###

class CCTarjaResultante(ModeloBaseHistorico):
    tarja                   = models.OneToOneField("produccion.TarjaResultante", on_delete=models.CASCADE)
    estado_cc               = models.CharField(choices=ESTADO_CC_TARJA_RESULTANTE, default='1', max_length=1)
    variedad                = models.CharField(choices=VARIEDAD, default='---', max_length=3)
    calibre                 = models.CharField(choices=CALIBRES, default='0', max_length=25)
    cantidad_muestra        = models.FloatField(choices=CANTIDAD_MUESTRA_PRODUCCION,blank=True, null=True)
    trozo                   = models.FloatField(blank=True, null=True,default=0.0 )
    picada                  = models.FloatField(blank=True, null=True,default=0.0)
    hongo                   = models.FloatField(blank=True, null=True,default=0.0)
    daño_insecto            = models.FloatField(blank=True, null=True,default=0.0)
    dobles                  = models.FloatField(blank=True, null=True,default=0.0)
    goma                    = models.FloatField(blank=True, null=True,default=0.0)
    basura                  = models.FloatField(blank=True, null=True,default=0.0)
    mezcla_variedad         = models.FloatField(blank=True, null=True,default=0.0)
    canuto                  = models.FloatField(blank=True, null=True,default=0.0)
    pepa_sana               = models.FloatField(blank=True, null=True,default=0.0)
    fuera_color             = models.FloatField(blank=True, null=True,default=0.0)
    punto_goma              = models.FloatField(blank=True, null=True,default=0.0)
    vana_deshidratada       = models.FloatField(default=0.0)
    cc_registrado_por       = models.ForeignKey("cuentas.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = ('CC Tarja Resultante Producción')
        verbose_name_plural = ('3. CC Tarjas Resultantes Producción')
        ordering = ('-pk', '-fecha_creacion')        
    
    # return calibre de la tarja resultante
    @property
    def get_calibre(self):
        if self.calibre:
            print(CALIBRES[0][1][int(self.calibre)][1])
            return CALIBRES[0][1][int(self.calibre)][1]
        else:
            return 'Sin Calibre'

    def __str__(self):
        return "CC %s de la tarja %s"% (self.pk, self.tarja.codigo_tarja)
    
class CCTarjaResultanteReproceso(ModeloBaseHistorico):
    tarja                   = models.OneToOneField("produccion.TarjaResultanteReproceso", on_delete=models.CASCADE)
    estado_cc               = models.CharField(choices=ESTADO_CC_TARJA_RESULTANTE, default='1', max_length=1)
    variedad                = models.CharField(choices=VARIEDAD, default='---', max_length=3)
    calibre                 = models.CharField(choices=CALIBRES, default='0', max_length=25)
    cantidad_muestra        = models.FloatField(choices=CANTIDAD_MUESTRA_PRODUCCION,blank=True, null=True)
    trozo                   = models.FloatField(blank=True, null=True,default=0.0 )
    picada                  = models.FloatField(blank=True, null=True,default=0.0)
    hongo                   = models.FloatField(blank=True, null=True,default=0.0)
    daño_insecto            = models.FloatField(blank=True, null=True,default=0.0)
    dobles                  = models.FloatField(blank=True, null=True,default=0.0)
    goma                    = models.FloatField(blank=True, null=True,default=0.0)
    basura                  = models.FloatField(blank=True, null=True,default=0.0)
    canuto                  = models.FloatField(blank=True, null=True,default=0.0)
    mezcla_variedad         = models.FloatField(blank=True, null=True,default=0.0)
    pepa_sana               = models.FloatField(blank=True, null=True,default=0.0)
    fuera_color             = models.FloatField(blank=True, null=True,default=0.0)
    punto_goma              = models.FloatField(blank=True, null=True,default=0.0)
    vana_deshidratada       = models.FloatField(default=0.0)
    cc_registrado_por       = models.ForeignKey("cuentas.User", on_delete=models.SET_NULL, null=True)

    
    class Meta:
        verbose_name = 'CC Tarja Resultante Reproceso'
        verbose_name_plural = '3. CC Tarjas Resultantes Reproceso'
        ordering = ('-pk', )

    def __str__(self):
        return "CC %s de la tarja %s"% (self.pk, self.tarja.codigo_tarja)





class CCTarjaSeleccionada(ModeloBaseHistorico):
    tarja_seleccionada      = models.OneToOneField("seleccion.TarjaSeleccionada", on_delete=models.CASCADE)
    estado_cc               = models.CharField(choices=ESTADO_CC_TARJA_RESULTANTE, default='1', max_length=1)
    variedad                = models.CharField(choices=VARIEDAD, default='---', max_length=3)    
    calibre                 = models.CharField(choices=CALIBRES, default='0', max_length=2)
    calidad_fruta           = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='3')
    cantidad_muestra        = models.FloatField(choices=CANTIDAD_MUESTRA_SELECCION,blank=True, null=True,default=250.0)
    trozo                   = models.FloatField(blank=True, null=True,default=0.0)
    picada                  = models.FloatField(blank=True, null=True,default=0.0)
    hongo                   = models.FloatField(blank=True, null=True,default=0.0)
    daño_insecto            = models.FloatField(blank=True, null=True,default=0.0)
    dobles                  = models.FloatField(blank=True, null=True,default=0.0)
    canuto                  = models.FloatField(blank=True, null=True,default=0.0)
    goma                    = models.FloatField(blank=True, null=True,default=0.0)    
    mezcla_variedad         = models.FloatField(blank=True, null=True,default=0.0)
    pepa_sana               = models.FloatField(blank=True, null=True,default=0.0)
    fuera_color             = models.FloatField(blank=True, null=True,default=0.0)
    punto_goma              = models.FloatField(blank=True, null=True,default=0.0)
    numero_pepa             = models.FloatField(blank=True, null=True, default=0.0)
    vana_deshidratada       = models.FloatField(default=0.0)
    basura                  = models.FloatField(default=0.0)
    # conte-o_pepa             = models.IntegerField(default=0)
    cc_registrado_por       = models.ForeignKey("cuentas.User", verbose_name="usuario_cc", on_delete=models.SET_NULL,  null=True)
    
    class Meta:
        verbose_name = "CC tarja de Selección"
        verbose_name_plural = "4. CC tarjas Programa Selección"

    def __str__(self):
        return "%s"% (self.pk)
    
    
    

################# CC Planta de Harina ###########################


class CCProgramaPH(ModeloBaseHistorico):
    programa        =   models.OneToOneField('planta_harina.ProgramaPH', on_delete=models.CASCADE)
    estado_control  =   models.CharField(max_length=50, choices=ESTADO_CONTROLCALIDAD_PH, default='0')
    humedad         =   models.FloatField(null=True)
    promedio_humedad=   models.CharField(max_length=50, blank=True)
    calidad_indicada=   models.CharField(max_length=50, blank=True, choices=CC_PROGRAMA_PH, default='0')

    class Meta:
        verbose_name = 'Control Calidad Programa PH'
        verbose_name_plural = '5.0 Control Calidad Programa PH'
        
    def __str__(self):
        return 'Control Calidad Programa N° %s'%(self.pk)
    
class CCBinResultanteProgramaPH(ModeloBaseHistorico):
    bin_resultante      = models.OneToOneField('planta_harina.BinResultantePrograma', on_delete=models.CASCADE)
    estado_cc           = models.CharField(max_length=1, choices=ESTADO_CONTROLCALIDAD_PH, default='0')
    humedad             = models.FloatField(default=0.0)
    piel_aderida        = models.FloatField(default=0.0)
    calidad             = models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    observaciones       = models.TextField(null=True, blank=True)
    realizado_por       = models.ForeignKey("cuentas.User", verbose_name="usuario_cc", on_delete=models.SET_NULL,  null=True)

    
    class Meta:
        verbose_name = 'CC Bin Resultante Programa'
        verbose_name_plural = '5.1 CC Bins Resultantes Programas'
        
    def __str__(self):
        return 'CC Bin %s'%(self.bin_resultante)

    

class CCProcesoPH(ModeloBaseHistorico):
    proceso         =   models.OneToOneField('planta_harina.ProcesoPH', on_delete=models.CASCADE)
    estado_control  =   models.CharField(max_length=50, choices=ESTADO_CONTROLCALIDAD_PH, default='0')
    humedad         =   models.FloatField(null=True)
    promedio_humedad=   models.CharField(max_length=50, blank=True)
    calidad_indicada=   models.CharField(max_length=50, blank=True, choices=CC_PROGRAMA_PH, default='0')
    
    class Meta:
        verbose_name = 'Control Calidad Proceso PH'
        verbose_name_plural = '6.0 Control Calidad Proceso PH'
        
    def __str__(self):
        return 'Control Calidad Proceso N° %s'%(self.pk)
    
class CCBinResultanteProcesoPH(models.Model):
    bin_resultante  =   models.OneToOneField('planta_harina.BinResultanteProceso', on_delete=models.CASCADE)
    estado_control  =   models.CharField(max_length=50, choices=ESTADO_CONTROLCALIDAD_PH, default='0')
    humedad         =   models.FloatField(null=True, default=0.0)
    piel_aderida    =   models.FloatField(null=True, default=0.0)
    granulometria   =   models.FloatField(null=True, default=0.0)
    parametro       =   models.CharField(max_length=13, choices=PARAMETRO_HARINA)
    observaciones   =   models.CharField(max_length=160, null=True, blank=True)
    realizado_por   =   models.ForeignKey("cuentas.User", verbose_name="usuario_cc", on_delete=models.SET_NULL,  null=True, blank=True)
    calidad         =   models.CharField(max_length=1, choices=CALIDAD_FRUTA, default='0')
    
    class Meta:
        verbose_name = 'Control Calidad Bin Resultante Proceso PH'
        verbose_name_plural = '6.1 Control Calidad Bines Resultantes Proceso PH'
    
    def __str__(self):
        return 'Control Calidad Bin N° %s'%(self.pk)
