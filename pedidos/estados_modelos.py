ESTADOS_PEDIDOS = [
    ("0", "Creado"),
    ("1", "Componiendo Fruta Ficticia"),
    ("2", "Componiendo Fruta Real"),
    ("3", "Compuesto"),
    ("4", "Listo para Retiro"),
    ("5", "Enviado"),
    ("6", "Cancelado"),
    ("7", "Recibido"),
    ("8", "Devuelto"),
]

NOMBRE_PRODUCTO = (
    ('1', 'Almendras'),
    ('2', 'Granillo'),
    ('3', 'Harina'),
    ('4', 'Almendras Laminadas')
)

CALIDAD = (
    ('Categoria 1', (
        ('SN', 'Sin Calidad'),
        ('EXT', 'Extra N°1'), ### EXT
        ('SUP', 'Supreme'), ### SUP
        ('W&B', 'Whole & Broken'), ### W&B
    )),
    ('Elaborados', (
        ('har_cn_piel', 'Harina Con Piel'),
        ('har_sn_piel', 'Harina Sin Piel'),
        ('gra_cn_piel', 'Granillo Con Piel'),
        ('gra_sn_piel', 'Granillo Sin Piel'),
        ('gra_tos_s_pl', 'Granillo Tostado Sin Piel'),
        ('gra_tos_c_pl', 'Granillo Tostado Con Piel'),
        ('alm_tostada', 'Almendras Tostadas'),
        ('alm_repelada', 'Almendras Repeladas'),
    )),
    ('Categoria 2', (
        ('vana', 'Vana'),
        ('goma', 'Goma'),
        ('insect', 'Insecto'),
        ('hongo', 'Hongo'),
        ('des_sea', 'Descarte Sea'),
        ('polvillo', 'Polvillo'),
        ('pepasuelo', 'Pepa Suelo'),
        ('preca', 'Precalibre'),
    )),
)

VARIEDAD = (    
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
    ('RV','Sin Especificar'),
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

CALIBRES = (
    ('Categoria 1', (
        ('0','Sin Calibre'),
        ('1', 'PreCalibre'),
        ('2','18/20'),
        ('3','20/22'),
        ('4','23/25'),
        ('5','25/27'),
        ('6','27/30'),
        ('7','30/32'),
        ('8','32/34'),
        ('9','34/36'),
        ('10','36/40'),
        ('11','40+'), 
    )),
    ('Elaborados', (
        ('12', '3x5mm'),
        ('13', '2x4mm'),
        ('14', '4x6mm'),
        ('15', '3x5mm'),
        ('16', '2x4mm'),
        ('17', '4x6mm'),
        ('18', '+2mm'),
        ('19', '-2mm'),
        ('20', '+2mm'),  
        ('21', '-2mm'), 
    ))
)