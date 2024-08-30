UBICACION_PATIO_TECHADO_EXT_LI = (
    ('0', 'Asigne Ubicación'),
    ('1','Sector 1'),
    ('2','Sector 2'),
    ('3','Sector 3'),
    ('4', 'Pavo'),
)


ESTADOS_MP = (
    ('1','MP Recepcionada'),
    ('2','MP En Inspecion Visual Por CC'),
    ('3','MP Aprobada, Esperando Ubicacion Descarga'),
    ('4','MP Rechazada'),
    ('5','MP Almacenada'),     
    ('6','MP Recepcion Completada'),
    ('7','Lote Procesado'),
    )

ESTADOSGUIARECEPCION_MP = (
    ('1','Guia Creada'),
    ('2','Guia En Proceso'),
    ('3','Guia Completada, esperando Tara'),
    ('4','Guia Cerrada'),

)

ESTADOS_RECEPCION_COLOSO = (
    ('1','Coloso Registrado'),
    ('2','Coloso Descargado'),
)
  
HUERTOS_PRODALMEN = (
    ('1', 'Huerto 1'),
    ('2', 'Huerto 2'),
    ('3', 'Huerto 3'),
    ('4', 'Huerto 4'),
    ('5', 'Huerto 5'),
    ('6', 'Huerto 6'),
    ('7', 'Huerto 7'),
)


SECTORES_PRODALMEN = (
    
    ('Sectores Individuales',(
        ('1', 'Sector 1'),
        ('2', 'Sector 2'),
        ('3', 'Sector 3'),
        ('4', 'Sector 4'),
        ('5', 'Sector 5'), 
        ('6', 'Sector 6'), 
        ('7', 'Sector 7'), 
        ('8', 'Sector 8'), 
        ('9', 'Sector 9'), 
        ('10', 'Sector 10'), 
        ('11', 'Sector 11'), 
        ('12', 'Sector 12'), 
        ('13', 'Sector 13'),
        ('14', 'Sector 14'), 
        ('15', 'Sector 15'),
        ('23', 'Sector Estuche'),
        ('24', 'Sector General'),
    )),
    ('Sectores Agrupados', (
        ('16', 'Sectores 1-2-3'),
        ('17', 'Sectores 1-2'),
        ('18', 'Sectores 3-4'),
        ('19', 'Sectores 1-1'),
        ('21', 'Sectores 1-3'),
        ('22', 'Sectores 1-4'),
    )),
)


 

CALIBRES_MP = (
    ('1','18/20'),
    ('2','20/22'),
    ('3','23/25'),
    ('4','25/27'),
    ('5','27/30'),
    ('6','30/32'),
    ('7','32/34'),
    ('8','34/36'),
    ('9','36/40'),
    
)

TIPO_PRODUCTOS_RECEPCIONMP = (
    ('1','Almendra con Pelon'),
    ('2','Pepa Calibrada'),
    ('3','Canuto'),
    
)

VARIEDADES_MP = (    
('SL','Solano'),
('MO','Mono'),
('CM','Carmel'),
('RB','Ruby'),  
('PR','Price'),
('WC','Wood Colony'),
('TK','Tokio'),
('MD','Merced'),
('TC','Tuca'),
('NP','Nonpareil'),
('RV','Revueltas'),
('PD','Padre'),
('TX','Texas'),
('MC','Marcona'),
('GU','Guara'),
('DS','Desmayo'),
('IX','Ixl'),
('TH','Thompson'),
('DK','Drake'),
('VS','Vesta'),
('NL','Neplus'),
('FR','Fritz'),
('BU','Butte'),
('MI','Mission'),
('NE','Neplus'),
('CA','Tipo California'),
('MZ','Mezcla'),
('ID','Independence'),
('AV','Avijar'),
('IS','Isabelona'),
('ST','Soleta'),
('VI','Vialfas'),
)

ESTADOS_LOTE_COLOSOS = (
    ('1','Lote Colosos Creado'),
    ('2','Lote En Inspecion Visual Por CC'),
    ('3','Lote Interno Aprobado'),
    ('4','Lote Interno Rechazado'),
    ('5', 'MP Almacenada'),
    
)

SI_NO = (
    (True,'Si'),
    (False,'No'),
)

RESULTADO_RECHAZO = (
    ('0', 'Rechazo Registrado'),
    ('1', 'Devuelto a Productor'),
    ('2', 'Derivado a Campo Secado'),
)