from agrupacionbins.models import *
from functools import reduce

from datetime import datetime
from controlcalidad.models import *
from .models import *


def obtener_codigo_tarja_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        return bin.bin_bodega.binbodega.tarja.produccion.codigo_tarja
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        return bin.bin_bodega.binbodega.tarja.reproceso.codigo_tarja
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        return bin.bin_bodega.binbodega.tarja.seleccion.codigo_tarja
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'bodegag6':
        return bin.bin_bodega.binbodega.tarja.programa.codigo_tarja
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'bodegag7':
        return bin.bin_bodega.binbodega.tarja.proceso.codigo_tarja
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.codigo_tarja
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          return bin.bin_bodega.binbodega.tarja.tarja.produccion.codigo_tarja
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          return bin.bin_bodega.binbodega.tarja.tarja.reproceso.codigo_tarja
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          return bin.bin_bodega.binbodega.tarja.tarja.seleccion.codigo_tarja
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model == 'bodegag6':
          return bin.bin_bodega.binbodega.tarja.tarja.programa.codigo_tarja
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.mode == 'bodegag7':
          return bin.bin_bodega.binbodega.tarja.tarja.proceso.codigo_tarja
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.codigo_tarja
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
        return bin.bin_bodega.binbodega.produccion.codigo_tarja
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      return bin.bin_bodega.binbodega.reproceso.codigo_tarja
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
      return bin.bin_bodega.binbodega.seleccion.codigo_tarja
    elif bin.bin_bodega.tipo_binbodega.model == 'bodegag6':
      return bin.bin_bodega.binbodega.programa.codigo_tarja
    elif bin.bin_bodega.tipo_binbodega.model == 'bodegag7':
      return bin.bin_bodega.binbodega.proceso.codigo_tarja
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.codigo_tarja
    
def obtener_programa_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        return f'Producción N° {bin.bin_bodega.binbodega.tarja.produccion.produccion.pk}'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        return f'Reproceso N° {bin.bin_bodega.binbodega.tarja.reproceso.reproceso.pk}'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
        return f'Selección N° {bin.bin_bodega.binbodega.tarja.seleccion.seleccion.pk}'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega']:
        return f'Agrupación N° {bin.bin_bodega.binbodega.pk}'
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          return f'Producción N° {bin.bin_bodega.binbodega.tarja.tarja.produccion.produccion.pk}'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          return f'Reproceso N° {bin.bin_bodega.binbodega.tarja.tarja.reproceso.produccion.pk}'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
          return f'Selección N° {bin.bin_bodega.binbodega.tarja.tarja.seleccion.seleccion.pk}'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model == 'bodegag6':
          return f'Planta Harina N° {bin.bin_bodega.binbodega.tarja.tarja.programa.programa.pk}'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model == 'bodegag7':
          return f'Proceso Planta Harina N° {bin.bin_bodega.binbodega.tarja.tarja.proceso.proceso.pk}'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega']:
          return f'Agrupación N° {bin.bin_bodega.binbodega.tarja.pk}'
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
        return f'Producción N° {bin.bin_bodega.binbodega.produccion.produccion.pk}'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      return  f'Reproceso N° {bin.bin_bodega.binbodega.reproceso.reproceso.pk}'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5', 'binsubproductoseleccion']:
      return  f'Selección N° {bin.bin_bodega.binbodega.seleccion.seleccion.pk}'
    elif bin.bin_bodega.tipo_binbodega.model == 'bodegag6':
      return f'Planta Harina N° {bin.bin_bodega.binbodega.programa.programa.pk}'
    elif bin.bin_bodega.tipo_binbodega.model == 'bodegag7':
      return f'Proceso Planta Harina N° {bin.bin_bodega.binbodega.proceso.proceso.pk}'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega']:
      return f'Agrupación N° {bin.bin_bodega.binbodega.pk}'

def obtener_variedad_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.produccion).first()
        if cc_tarja:
          return cc_tarja.get_variedad_display()
        return 'Sin Varidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.reproceso).first()
        if cc_tarja:
          return cc_tarja.get_variedad_display()
        return 'Sin Varidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.seleccion).first()
        if cc_tarja:
          return cc_tarja.get_variedad_display()
        return 'Sin Varidad'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
        return 'Sin Variedad'

      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.get_variedad_display()
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.produccion).first()
          if cc_tarja:
            return cc_tarja.get_variedad_display()
          return 'Sin Varidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.reproceso).first()
          if cc_tarja:
            return cc_tarja.get_variedad_display()
          return 'Sin Varidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.tarja.seleccion).first()
          if cc_tarja:
            return cc_tarja.get_variedad_display()
          return 'Sin Varidad'
        
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.get_variedad_display()
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
      cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.produccion).first()
      if cc_tarja:
        return cc_tarja.get_variedad_display()
      return 'Sin Varidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.reproceso).first()
      if cc_tarja:
        return cc_tarja.get_variedad_display()
      return 'Sin Varidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
      cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion).first()
      if cc_tarja:
        return cc_tarja.get_variedad_display()
      return 'Sin Varidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
      return 'Sin Variedad'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.get_variedad_display()
    
def obtener_variedad_id_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.produccion).first()
        if cc_tarja:
          return cc_tarja.variedad
        return 'Sin Varidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.reproceso).first()
        if cc_tarja:
          return cc_tarja.variedad
        return 'Sin Varidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.seleccion).first()
        if cc_tarja:
          return cc_tarja.variedad
        return 'Sin Varidad'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
        return 'Sin Variedad'

      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.variedad
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.produccion).first()
          if cc_tarja:
            return cc_tarja.variedad
          return 'Sin Varidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.reproceso).first()
          if cc_tarja:
            return cc_tarja.variedad
          return 'Sin Varidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.tarja.seleccion).first()
          if cc_tarja:
            return cc_tarja.variedad
          return 'Sin Varidad'
        
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.variedad
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
      cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.produccion).first()
      if cc_tarja:
        return cc_tarja.variedad
      return 'Sin Varidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.reproceso).first()
      if cc_tarja:
        return cc_tarja.variedad
      return 'Sin Varidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
      cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion).first()
      if cc_tarja:
        return cc_tarja.variedad
      return 'Sin Varidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
      return 'Sin Variedad'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.variedad
    
def obtener_calibre_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.produccion).first()
        if cc_tarja:
          return cc_tarja.get_calibre_display()
        return 'Sin '
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.reproceso).first()
        if cc_tarja:
          return cc_tarja.get_calibre_display()
        return 'Sin '
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.seleccion).first()
        if cc_tarja:
          return cc_tarja.get_calibre_display()
        return 'Sin '
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
        return 'Sin Calibre'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.get_calibre_display()
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.produccion).first()
          if cc_tarja:
            return cc_tarja.get_calibre_display()
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.reproceso).first()
          if cc_tarja:
            return cc_tarja.get_calibre_display()
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.tarja.seleccion).first()
          if cc_tarja:
            return cc_tarja.get_calibre_display()
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.get_calibre_display()
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
      cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.produccion).first()
      if cc_tarja:
        return cc_tarja.get_calibre_display()
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.reproceso).first()
      if cc_tarja:
        return cc_tarja.get_calibre_display()
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
      cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion).first()
      if cc_tarja:
        return cc_tarja.get_calibre_display()
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.get_calibre_display()
    
def obtener_calibre_id_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.produccion).first()
        if cc_tarja:
          return cc_tarja.calibre
        return 'Sin '
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.reproceso).first()
        if cc_tarja:
          return cc_tarja.calibre
        return 'Sin '
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.seleccion).first()
        if cc_tarja:
          return cc_tarja.calibre
        return 'Sin '
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
        return 'Sin Calibre'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.calibre
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.produccion).first()
          if cc_tarja:
            return cc_tarja.calibre
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.reproceso).first()
          if cc_tarja:
            return cc_tarja.calibre
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.tarja.seleccion).first()
          if cc_tarja:
            return cc_tarja.calibre
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
          return 'Sin Calibre'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.calibre
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
      cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.produccion).first()
      if cc_tarja:
        return cc_tarja.calibre
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.reproceso).first()
      if cc_tarja:
        return cc_tarja.calibre
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
      cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion).first()
      if cc_tarja:
        return cc_tarja.calibre
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
      return 'Sin Calibre'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.calibre

def obtener_calidad_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        return 'Sin Calidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        return 'Sin Calidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.seleccion).first()
        if cc_tarja:
          return cc_tarja.calidad
        return 'Sin Calidad'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
        return 'Sin Calidad'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.get_calidad_display()
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.tarja.seleccion).first()
          if cc_tarja:
            return cc_tarja.calidad_fruta
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.get_calidad_display()
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.reproceso).first()
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5', ]:
      cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion).first()
      if cc_tarja:
        return cc_tarja.calidad_fruta
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.get_calidad_display()


def obtener_calidad_id_embalaje(bin):
    if bin.bin_bodega.tipo_binbodega.model == 'frutasobrantedeagrupacion':
      if bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1', 'bodegag2']:
        cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.produccion).first()
        return 'Sin Calidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
        return 'Sin Calidad'
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
        cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.seleccion).first()
        if cc_tarja:
          return cc_tarja.calidad
        return 'Sin Calidad'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['bodegag6', 'bodegag7']:
        return 'Sin Calidad'
      
      elif bin.bin_bodega.binbodega.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
        return bin.bin_bodega.binbodega.get_calidad_display()
      elif bin.bin_bodega.binbodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
        if bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1', 'bodegag2']:
          cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.tarja.tarja.produccion).first()
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag1reproceso', 'bodegag2reproceso']:
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag3', 'bodegag4', 'bodegag5']:
          cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.tarja.tarja.seleccion).first()
          if cc_tarja:
            return cc_tarja.calidad
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['bodegag6', 'bodegag7']:
          return 'Sin Calidad'
        elif bin.bin_bodega.binbodega.tarja.tipo_tarja.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
          return bin.bin_bodega.binbodega.tarja.get_calidad_display()
      
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1', 'bodegag2']:
      cc_tarja = CCTarjaResultante.objects.filter(tarja = bin.bin_bodega.binbodega.produccion).first()
      if cc_tarja:
        return cc_tarja.get_calidad_display()
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag1reproceso', 'bodegag2reproceso']:
      cc_tarja = CCTarjaResultanteReproceso.objects.filter(tarja = bin.bin_bodega.binbodega.reproceso).first()
      if cc_tarja:
        return cc_tarja.get_calidad_display()
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag3', 'bodegag4', 'bodegag5']:
      cc_tarja = CCTarjaSeleccionada.objects.filter(tarja_seleccionada = bin.bin_bodega.binbodega.seleccion).first()
      if cc_tarja:
        return cc_tarja.calidad
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['bodegag6', 'bodegag7']:
      return 'Sin Calidad'
    elif bin.bin_bodega.tipo_binbodega.model in ['agrupaciondebinsbodega', 'binsubproductoseleccion']:
      return bin.bin_bodega.binbodega.get_calidad_display()


def obtener_kilos_fruta_pallet_embalaje(pallet):
  kilos = 0
  if pallet.peso_inicial:
    kilos += pallet.peso_inicial
  else:
    kilos += pallet.peso_total_pallet
    
  return round(kilos, 2)


def clasificar_bines_por_tipo(bines):
    tipo_programa = None

    for bin in bines:
        modelo_bin = bin.tipo_binbodega.model
        if modelo_bin in ['bodegag1', 'bodegag2', 'bodegag3', 'bodegag4', 'bodegag5']:
            if tipo_programa is None:
                tipo_programa = '1'  # Almendra
            elif tipo_programa != '1':
                return None
        elif modelo_bin == 'bodegag6':
            if tipo_programa is None:
                tipo_programa = '2'  # Categoría específica para g6
            elif tipo_programa != '2':
                return None
        elif modelo_bin == 'bodegag7':
            if tipo_programa is None:
                tipo_programa = '3'  # Categoría específica para g7
            elif tipo_programa != '3':
                return None
        else:
            return None

    # Si todos los bines son válidos y homogéneos, devuelve el tipo de programa
    return tipo_programa