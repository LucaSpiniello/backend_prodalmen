from pedidos.models import *
from bodegas.funciones import *


def obtener_codigo(fruta):
  if fruta.tipo_fruta.model == 'binbodega':
      return get_codigo_tarja(fruta.fruta)
  elif fruta.tipo_fruta.model == 'palletproductoterminado':
      return fruta.fruta.codigo_pallet
      
def obtener_programa_guia(fruta):
  if fruta.tipo_fruta.model == 'binbodega':
    return get_programa(fruta.fruta)
  elif fruta.tipo_fruta.model == 'palletproductoterminado':
      return f'Programa Embalaje N° {fruta.fruta.embalaje.pk}'
    
def obtener_producto(fruta):
  if fruta.tipo_fruta.model == 'binbodega':
    return 'Pepa En Bin'
  elif fruta.tipo_fruta.model == 'palletproductoterminado':
      return f'{fruta.fruta.embalaje.get_tipo_producto_display()}'
    
def obtener_variedad(fruta):
  if fruta.tipo_fruta.model == 'binbodega':
    return get_variedad_display(fruta.fruta)
  elif fruta.tipo_fruta.model == 'palletproductoterminado':
      return f'{fruta.fruta.embalaje.get_variedad_display()}'
    
def obtener_calidad(fruta):
  if fruta.tipo_fruta.model == 'binbodega':
    return get_calidad_display(fruta.fruta)
  elif fruta.tipo_fruta.model == 'palletproductoterminado':
      return f'{fruta.fruta.embalaje.get_calidad_display()}'
    
def obtener_calibre(fruta):
  if fruta.tipo_fruta.model == 'binbodega':
    return get_calibre_display(fruta.fruta)
  elif fruta.tipo_fruta.model == 'palletproductoterminado':
      return f'{fruta.fruta.embalaje.get_calibre_display()}'