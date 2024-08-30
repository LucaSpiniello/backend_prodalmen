

ESTADO_NOTA_PEDIDO = (
    ('1', 'Creado'),
    ('2', 'En Preparacion'),
    ('3', 'Completado'),
    ('4', 'Entregado y Finalizado'),
    ('5', 'Solicitado'),
    ('6', 'Cancelado'),
    ('7', 'Devuelto A Bodega'),
)


CONDICION_PAGO_NOTAPEDIDO = (
    ('1', '7 dias'),
    ('2', '15 dias'),
    ('3', '30 dias'),
    ('4', 'Contado'),
    ('5', 'Contra Entrega'),
)

PRODUCTO = (
    ('pepa_expo', 'Pepa Exportacion'),
    ('whole', 'Whole & Broken'),
    ('picada', 'Picada'),
    ('trozo', 'Trozo'),    
    ('pepa_huerto', 'Pepa Huerto'),
    ('dano_insecto', 'Daño Insecto'),
    ('descarte_sea', 'Descarte Sea'),
    ('fruta_suelo', 'Fruta Suelo'),
    ('goma', 'Goma'),
    ('hongos', 'Hongos'),
    ('polvillo', 'Polvillo Almendra'),
    ('basura', 'Basura'),
    ('recalibre', 'Recalibre'),

)

TIPO_VENTA = (
    ('1', 'Pesos Chilenos'),
    ('2', 'Dolares Americanos'),
)