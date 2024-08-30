
ESTADO_CONTROL = (
    ('1','Lote Aprobado x CC'),
    ('0','Lote Rechazado x CC'),
    ('2','Pendiente CC'),

)

ESTADO_APROBACION_CC_X_JEFATURA = (
    ('0', 'En Espera de Aprobación'),
    ('1', 'Aprobado'),
    ('2', 'Rechazado'),
)

ESTADOS_CONTROL_RENDIMIENTO = (
    ('a','Sin Muestras Registradas'),
    ('b','25% Muestras Lote'),
    ('c','50% Muestras Lote'),
    ('d','75% Muestras Lote'),
    ('e','100% Muestras Lote'),
)

ESTADO_CC_TARJA_RESULTANTE = (
    ('1','Pendiente'),
    ('2','En Analisis'),
    ('3','Completado'),
)


CANTIDAD_MUESTRA_PRODUCCION = (
    (250,'250 Gramos'),
    (500,'500 Gramos'),
)

CANTIDAD_MUESTRA_SELECCION = (
    (100,'100 Gramos'),
    (250,'250 Gramos'),
    (500, '500 Gramos'),
)

ESTADO_CONTROLCALIDAD_PH = (
    ('0', 'Sin Control de Calidad Registrado'),
    ('1', 'CC Aprobado'),
    ('2', 'CC Rechazado'),
)

CC_PROGRAMA_PH = (
    ('0', 'Sin Registro'),
    ('alm_repelada_entera', 'Almendra Repelada Entera'),
    ('wholen_broken_repelada', 'Wholen Broken Repelado'),
)

ESTADO_BIN_RESULTANTE_PH = (
    ('0', 'Pendiente Control'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
)

CALIDAD_FRUTA = (
    ('0', 'Extra N°1'),
    ('1', 'Supreme'),
    ('2', 'Whole & Broken'),
    ('3', 'Sin Calidad'),
    ('4', 'Whole para Harina'),
)

PARAMETRO_HARINA = (
    ('0', 'Sin Parametro'),
    ('harina_fina','-2MM'),
    ('harina_gruesa','+2MM'),
)


ESTADO_CONTRAMUESTRA = (
    ('0', 'Sin Solicitar'),
    ('1', 'Contramuestra Solicitada'),
    ('2', 'Muestra Tomada'),
    ('3', 'Control Pepa Ok'),
    ('4', 'Calibre Ok'),
    ('5', 'Contramuestra Cerrada')
)