
PRODUCTO_PROGRAMA = (
    ('repelado', 'Repelado'),
    ('tostado', 'Tostado'),
)

ESTADO_PH = (
    ('1', 'Programa Creado'),
    ('2', 'En Proceso'),
    ('3', 'Pausado'),
    ('4', 'Cerrado'),
    ('5', 'Terminado'),
)

UBICACION_PRODUCTO = (
    ('1', 'En Planta Harina'),
    ('2', 'Almacenaje Temporal Frigorifico'),
    ('3', 'Ingreso de Semi Elab a G6')
)

ESTADO_VARIABLES = (
    ('inicial', 'Datos Inicial'),
    ('final', 'Datos Final'),
    ('creada', 'Creada'),
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


TIPOS_RECHAZOS = (
        ('1', 'Piel Aderida'),
        ('2', 'Pepa Piso'),
        ('3', 'Basura'),
        ('4', 'Descarte Sea'),
        ('5', 'Cascara'),
        ('6', 'Otros no especificado'),
)

EXEDENTES = (
    
    ('Exedentes Programa',(
        ('1', 'Exedente tipo 1'),
        ('2', 'Exedente tipo 2'),
        ('3', 'Exedente tipo 3'),
            
    )),
    ('Exedentes Proceso', (
        ('1', 'Exedente tipo 1'),
        ('2', 'Exedente tipo 2'),
        ('3', 'Exedente tipo 3'),
    )),
)

PERDIDAPROGRAMA = (
    ('2', '2 % de pieles perdida sugerida'),
    ('3', '3 % de pieles perdida sugerida'),
    ('4', '4 % de pieles perdida sugerida'),
    ('5', '5 % de pieles perdida sugerida'),
    ('6', '6 % de pieles perdida sugerida'),
    ('7', '7 % de pieles perdida sugerida'),
    ('8', '8 % de pieles perdida sugerida'),
    ('9', '9 % de pieles perdida sugerida'),
)


ESTADO_BIN_RESULTANTE_PH = (
    ('1', 'Bin Creado Esperando CC'),
    ('2', 'Bin Aprobado'),
    ('3', 'Bin Rechazado'),
 
)

TIPOS_BIN = (
    (40.0, 'Patineta Negra'),
    (43.5, 'Patineta Blanca'),
    (44.6, 'UPC'),
 
)

#### Proceso PH ####
TIPO_PROCESO = (


    ('Proceso de Granillado Tostado', (
        ('1', 'Granillo Tostado con Piel 3x5mm'),
        ('2', 'Granillo Tostado con Piel 2x4mm'),
        ('3', 'Granillo Tostado con Piel 4x6mm'),
        ('4', 'Granillo Tostado sin Piel 3x5mm'),
        ('5', 'Granillo Tostado sin Piel 2x4mm'),
        ('6', 'Granillo Tostado sin Piel 4x6mm'),
    )),
    ('Proceso de Harina Tostado',(
        ('7', 'Harina Tostado Con Piel +2mm'),
        ('8', 'Harina Tostado Con Piel -2mm'),
        ('9', 'Harina Tostado Sin Piel +2mm'),  
        ('10', 'Harina Tostado Sin Piel -2mm'), 
    )),
    ('Proceso de Granillado', (
        ('11', 'Granillo con Piel 3x5mm'),
        ('12', 'Granillo con Piel 2x4mm'),
        ('13', 'Granillo con Piel 4x6mm'),
        ('14', 'Granillo sin Piel 3x5mm'),
        ('15', 'Granillo sin Piel 2x4mm'),
        ('16', 'Granillo sin Piel 4x6mm'),
    )),
    ('Proceso de Harina',(
        ('17', 'Harina Con Piel +2mm'),
        ('18', 'Harina Con Piel -2mm'),
        ('19', 'Harina Sin Piel +2mm'),  
        ('20', 'Harina Sin Piel -2mm'), 
    )),
    
)


TIPO_RESULTANTE_PH = (


    ('Resultantes de Programa PH', (
        ('A', 'Almendra Repelada'),
        ('B', 'Almendra Tostada'),
    )),
    ('Resultantes de Proceso PH',(
        ('1', 'Granillo Tostado con Piel 3x5mm'),
        ('2', 'Granillo Tostado con Piel 2x4mm'),
        ('3', 'Granillo Tostado con Piel 4x6mm'),
        ('4', 'Granillo Tostado sin Piel 3x5mm'),
        ('5', 'Granillo Tostado sin Piel 2x4mm'),
        ('6', 'Granillo Tostado sin Piel 4x6mm'),
        ('7', 'Harina Tostado Con Piel +2mm'),
        ('8', 'Harina Tostado Con Piel -2mm'),
        ('9', 'Harina Tostado Sin Piel +2mm'),  
        ('10', 'Harina Tostado Sin Piel -2mm'), 
        ('11', 'Granillo con Piel 3x5mm'),
        ('12', 'Granillo con Piel 2x4mm'),
        ('13', 'Granillo con Piel 4x6mm'),
        ('14', 'Granillo sin Piel 3x5mm'),
        ('15', 'Granillo sin Piel 2x4mm'),
        ('16', 'Granillo sin Piel 4x6mm'),
        ('17', 'Harina Con Piel +2mm'),
        ('18', 'Harina Con Piel -2mm'),
        ('19', 'Harina Sin Piel +2mm'),  
        ('20', 'Harina Sin Piel -2mm'), 
    )),
    
)