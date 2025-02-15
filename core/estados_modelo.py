
SEXO_CHOICES = (
    ('F', 'Femenino'),
    ('M', 'Masculino'),
    ('O', 'No especificado')
)
ESTADO_OTP = (
    ('0', 'no autorizado'),
    ('1', 'autorizado'),
)

TIPOS_OPERARIO = (
    ('p_limpia', 'Operario Pre Limpia'),
    ('despelo', 'Operario Despelonado'),
    ('p_harina', 'Operario Planta de Harina'),
    ('seleccion', 'Operario de Selección'),
    ('gruero', 'Operario Gruero'),
    ('embalaje', 'Operario Embalaje'),
    ('bodega', 'Operario de Bodega'),
    ('pesaje', 'Operario de Pesaje'),  
    ('sub_prod', 'Operario de Sub Producto'),
)   

      
ESTILO_CHOICES = (
    ('light', 'Tema Claro'),
    ('dark', 'Tema Oscuro'),
    ('semi-dark', 'Semi Oscuro'),
    ('minimal-theme', 'Tema Minimal'),
    
)

CABECERA_CHOICES = (
    ('1', 'Azul'),
    ('2', 'Negro'),
    ('3', 'Rojo'),
    ('4', 'Verde'),
    ('5', 'Morado'),
    ('7', 'Cafe'),
    ('8', 'Fucsia'),
    ('9', 'Naranjo'),
    
)

CARGOS_PERFILES = (
    ('1', 'RecepcionMP'),
    ('2', 'CDC Jefatura'),
    ('3', 'CDC Operario MP'),
    ('4', 'Bodega Patio Exterior'),
    ('5', 'Produccion'),
    ('6', 'Produccion Admin'),
    ('7', 'Seleccion'),
    ('8', 'Seleccion Admin'),
    ('9', 'Admininistrador'),
    
)

ANIO = (
    ('2025', '2025'),
    ('2024', '2024'),
    ('2023', '2023'),
    ('2022', '2022'),
    ('2021', '2021'),
    ('Todo', 'Todo')
)

ESTADO_IOT_BALANZA_RECEPCIONMP = (
    ('Manual', 'Manual'),
    ('Automático', 'Automático')
)
