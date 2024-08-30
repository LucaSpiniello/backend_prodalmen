ESTADO_GUIA_INTERNA = (
    ('guia_capturada', 'Guia Interna Capturada'),
    ('guia_almacenada', 'Guia almacenada Bodega G5'),
    ('guia_procesada', 'Guia procesada en planta harina')
)
ESTADO_BIND_ENGUIA = (
    ('bind_capturado', 'Bind Capturado'),
    ('bind_disponible', 'Bind Disponible'),
    ('bind_enprograma', 'Bind asignado en programa'),
)


COLECTORES_TEMPORALES = (
    ('1', 'Colector 1'),
    ('2', 'Colector 2'),
    ('3', 'Colector 3'),
)

ESTADOS_DESPELONADO = (
    ('1', 'Registrado'),
    ('2', 'En proceso'),    
    ('3', 'Terminado, en Espera Resultados'),
    ('4', 'Proceso Completado y Cerrado'),
    
)

ESTADOS_DESCASCARADO = (
    ('1', 'Proceso registrado'),
    ('2', 'En proceso'),
    ('3', 'Terminado, en Espera Resultados'),
    ('4', 'Proceso Completado y Cerrado'),
)

TIPOS_RESIDUOS_DESPELONADO = (
    ('1', 'Piedras'),
    ('2', 'Ramas'),
    ('3', 'Basura'),
    ('4', 'Otros'),
    ('5', 'Pelón'),
)


TIPOS_BIN = (
    
    (40.0,'Patineta Negra'),
    (43.5,'Patineta Blanca'),
    (44.6,'UPC'),
 
)

TIPO_RESIDUO_DESCARADO = (
    ('1','Cascarilla'),
    ('2','Polvillo'),
    ('3','Wholen Broken'),
    ('4','Pelon'),
    ('5','Otro'),
)


ESTADOS_PRODUCCION = (
    ('0','Producción Pausada'),
    ('1','Proceso Registrado, Esperando Inicio'),
    ('2','En Proceso'),
    ('3','En Reproceso'),
    ('4','Terminado, en Espera Resultados'),
    ('5','Proceso Completado y Cerrado'),
)


TIPO_RESULTANTE = (
    ('1','Borrel'),
    ('2','Maseto'),
    ('3','Pepa Calibrada'),        
    ('4','Pepa Huerto'),
)

UBICACION_TARJA = (
    ('0','En Transito'),
    ('1','Bodega G1'),
    ('2','Bodega G2'),
    ('3','Bodega G3'),
    ('4','Bodega G4'),
    ('5','Bodega G5'),
    

)

ESTADOS_REPROCESO = (
    ('0','Proceso Registrado, Esperando Inicio'),
    ('1','Reproceso Pausado'),
    ('2','En Reproceso'),
    ('3','Terminado, en Espera Resultados'),
    ('4','Proceso Completado y Cerrado'),
)