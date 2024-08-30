from agrupacionbins.models import *
from functools import reduce

from datetime import datetime


##BINES

def obtener_codigo_tarja(bin):
    # Diccionario para acceder directamente a la propiedad correcta de cada tipo de bin
    ruta_acceso = {
        'bodegag1': 'produccion.codigo_tarja',
        'bodegag2': 'produccion.codigo_tarja',
        'bodegag1reproceso': 'reproceso.codigo_tarja',
        'bodegag2reproceso': 'reproceso.codigo_tarja',
        'agrupaciondebinsbodegas': 'codigo_tarja',
        'frutasobrantedeagrupacion': 'tarja'
    }

    tipo_modelo = bin.tipo_bin_bodega.model

    # Manejo especial si la tarja es de tipo Fruta Sobrante de Agrupación recursivamente
    if tipo_modelo == 'frutasobrantedeagrupacion':
        tarja = bin.bin_bodega.tarja
        # Recursividad para profundizar hasta encontrar un tipo que no sea frutasobrantedeagrupacion
        while isinstance(tarja, FrutaSobranteDeAgrupacion):
            tarja = tarja.tarja
        # Una vez encontrada la tarja no sobrante, determinar el tipo y procesar como normal
        tipo_modelo = tarja.tipo_tarja.model
        return obtener_codigo_tarja(tarja)

    # Acceso estándar basado en el tipo del modelo
    try:
        propiedad = ruta_acceso[tipo_modelo]
        return reduce(getattr, propiedad.split('.'), bin.bin_bodega)
    except KeyError:
        return None  # O manejar como consideres adecuado si el tipo no está en el diccionario


def get_kilos_bin(bin):
    # Inicializar peso base y patineta como cero para manejar casos donde no se encuentren
    peso = 0
    patineta = 0

    # Definir un diccionario para mapear los tipos de bins y cómo calcular su peso
    tipo_peso = {
        'bodegag1': 'produccion',
        'bodegag2': 'produccion',
        'bodegag1reproceso': 'reproceso',
        'bodegag2reproceso': 'reproceso',
        'bodegag3': 'seleccion',
        'bodegag4': 'seleccion',
        'agrupaciondebinsbodegas': 'agrupacion',
        'frutasobrantedeagrupacion': 'fruta_sobrante',
        'binsubproductoseleccion': 'subproducto'
    }

    # Obtener el atributo relacionado basado en el tipo de bin
    relacionado = tipo_peso.get(bin.tipo_bin_bodega.model)

    # Procesar basado en el tipo de relación
    if relacionado in ['produccion', 'reproceso', 'seleccion']:
        if hasattr(bin.bin_bodega, relacionado):
            entidad = getattr(bin.bin_bodega, relacionado)
            peso = entidad.peso
            patineta = entidad.tipo_patineta
    elif relacionado == 'agrupacion':
        peso = bin.bin_bodega.kilos_fruta
    elif relacionado == 'fruta_sobrante':
        if bin.bin_bodega.tipo_tarja.model == 'frutasobrantedeagrupacion':
            peso = bin.bin_bodega.tarja.kilos_fruta
        else:
            peso = bin.bin_bodega.kilos_fruta
    elif relacionado == 'subproducto':
        peso = sum(producto.peso for producto in bin.bin_bodega.subproductosenbin_set.all())

    # Calcular el peso final restando la patineta si es aplicable
    peso_final = peso - patineta if patineta else peso

    return round(peso_final, 2)
  
  
def get_variedad_display(bin):
    # Asignar variedad basada directamente en la bodega referenciada
    variedad_display = None
    
    if bin.tipo_bin_bodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso']:
        # Asumiendo que las bodegas de estos tipos directamente tienen un atributo 'variedad'
        if hasattr(bin.bin_bodega, 'variedad'):
            variedad_display = bin.bin_bodega.get_variedad_display()
    elif bin.tipo_bin_bodega.model == 'agrupaciondebinsbodegas':
        # Si la agrupación de bins tiene una variedad específica
        if hasattr(bin.bin_bodega, 'get_variedad_display'):
            variedad_display = bin.bin_bodega.get_variedad_display()
    elif bin.tipo_bin_bodega.model == 'frutasobrantedeagrupacion':
        # Si la fruta sobrante tiene una variedad asignada
        if hasattr(bin.bin_bodega, 'get_variedad_display'):
            variedad_display = bin.bin_bodega.get_variedad_display()

    return variedad_display
  
  
def get_calibre_display(bin):
    # Asignar calibre basado directamente en la bodega referenciada
    calibre_display = None
    
    if bin.tipo_bin_bodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso']:
        # Asumiendo que las bodegas de estos tipos directamente tienen un atributo 'calibre'
        if hasattr(bin.bin_bodega, 'calibre'):
            calibre_display = bin.bin_bodega.get_calibre_display()
    elif bin.tipo_bin_bodega.model == 'agrupaciondebinsbodegas':
        # Si la agrupación de bins tiene un calibre específico
        if hasattr(bin.bin_bodega, 'get_calibre_display'):
            calibre_display = bin.bin_bodega.get_calibre_display()
    elif bin.tipo_bin_bodega.model == 'frutasobrantedeagrupacion':
        # Si la fruta sobrante tiene un calibre asignado
        if hasattr(bin.bin_bodega, 'get_calibre_display'):
            calibre_display = bin.bin_bodega.get_calibre_display()

    return calibre_display


def get_programa_description(bin):
    # Determinar el tipo de programa y obtener la descripción adecuada
    if bin.tipo_bin_bodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4']:
        # Asumiendo que estos tipos de bodegas tienen una referencia directa a un programa
        if hasattr(bin.bin_bodega, 'produccion'):
            return f"Programa Producción N° {bin.bin_bodega.produccion.pk}"
        elif hasattr(bin.bin_bodega, 'reproceso'):
            return f"Programa Reproceso N° {bin.bin_bodega.reproceso.pk}"
        elif hasattr(bin.bin_bodega, 'seleccion'):
            return f"Programa Selección N° {bin.bin_bodega.seleccion.pk}"

    elif bin.tipo_bin_bodega.model == 'agrupaciondebinsbodegas':
        # Si es una agrupación de bins
        return f"Programa Agrupación N° {bin.bin_bodega.pk}"

    elif bin.tipo_bin_bodega.model == 'frutasobrantedeagrupacion':
        # Si es fruta sobrante, obtener el programa del bin original
        if hasattr(bin.bin_bodega, 'tarja') and bin.bin_bodega.tarja:
            if hasattr(bin.bin_bodega.tarja, 'produccion'):
                return f"Programa Producción N° {bin.bin_bodega.tarja.produccion.pk}"
            elif hasattr(bin.bin_bodega.tarja, 'reproceso'):
                return f"Programa Reproceso N° {bin.bin_bodega.tarja.reproceso.pk}"
            elif hasattr(bin.bin_bodega.tarja, 'seleccion'):
                return f"Programa Selección N° {bin.bin_bodega.tarja.seleccion.pk}"
    
    return "No se puede determinar el programa asociado a este bin"




def obtener_codigo_tarja_bodega(bin):
    ruta_acceso = {
        'bodegag1': 'produccion.codigo_tarja',
        'bodegag2': 'produccion.codigo_tarja',
        'bodegag1reproceso': 'reproceso.codigo_tarja',
        'bodegag2reproceso': 'reproceso.codigo_tarja',
        'agrupaciondebinsbodegas': 'codigo_tarja',
        'frutasobrantedeagrupacion': 'tarja'
    }

    tipo_modelo = bin.tipo_binbodega.model
    if tipo_modelo == 'frutasobrantedeagrupacion':
        tarja = bin.binbodega.tarja
        while isinstance(tarja, FrutaSobranteDeAgrupacion):
            tarja = tarja.tarja
        tipo_modelo = tarja.tipo_tarja.model
        return obtener_codigo_tarja(tarja)

    try:
        propiedad = ruta_acceso[tipo_modelo]
        return reduce(getattr, propiedad.split('.'), bin.binbodega)
    except KeyError:
        return None

def get_kilos_bin_bodega(bin):
    peso = 0
    patineta = 0
    tipo_peso = {
        'bodegag1': 'produccion',
        'bodegag2': 'produccion',
        'bodegag1reproceso': 'reproceso',
        'bodegag2reproceso': 'reproceso',
        'bodegag3': 'seleccion',
        'bodegag4': 'seleccion',
        'agrupaciondebinsbodegas': 'agrupacion',
        'frutasobrantedeagrupacion': 'fruta_sobrante',
        'binsubproductoseleccion': 'subproducto'
    }
    relacionado = tipo_peso.get(bin.tipo_binbodega.model)
    if relacionado in ['produccion', 'reproceso', 'seleccion']:
        if hasattr(bin.binbodega, relacionado):
            entidad = getattr(bin.binbodega, relacionado)
            peso = entidad.peso
            patineta = entidad.tipo_patineta
    elif relacionado == 'agrupacion':
        peso = bin.binbodega.kilos_fruta
    elif relacionado == 'fruta_sobrante':
        peso = bin.binbodega.kilos_fruta
    elif relacionado == 'subproducto':
        peso = sum(producto.peso for producto in bin.binbodega.subproductosenbin_set.all())
    peso_final = peso - patineta if patineta else peso
    return round(peso_final, 2)

def get_variedad_display_bodega(bin):
    variedad_display = None
    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso']:
        if hasattr(bin.binbodega, 'variedad'):
            variedad_display = bin.binbodega.get_variedad_display()
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
        if hasattr(bin.binbodega, 'get_variedad_display'):
            variedad_display = bin.binbodega.get_variedad_display()
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if hasattr(bin.binbodega, 'get_variedad_display'):
            variedad_display = bin.binbodega.get_variedad_display()
    return variedad_display

def get_calibre_display_bodega(bin):
    calibre_display = None
    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso']:
        if hasattr(bin.binbodega, 'calibre'):
            calibre_display = bin.binbodega.get_calibre_display()
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
        if hasattr(bin.binbodega, 'get_calibre_display'):
            calibre_display = bin.binbodega.get_calibre_display()
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if hasattr(bin.binbodega, 'get_calibre_display'):
            calibre_display = bin.binbodega.get_calibre_display()
    return calibre_display

def get_programa_description_bodega(bin):
    if bin.tipo_binbodega.model in ['bodegag1', 'bodegag2', 'bodegag1reproceso', 'bodegag2reproceso', 'bodegag3', 'bodegag4']:
        if hasattr(bin.binbodega, 'produccion'):
            return f"Programa Producción N° {bin.binbodega.produccion.pk}"
        elif hasattr(bin.binbodega, 'reproceso'):
            return f"Programa Reproceso N° {bin.binbodega.reproceso.pk}"
        elif hasattr(bin.binbodega, 'seleccion'):
            return f"Programa Selección N° {bin.binbodega.seleccion.pk}"
    elif bin.tipo_binbodega.model == 'agrupaciondebinsbodegas':
        return f"Programa Agrupación N° {bin.binbodega.pk}"
    elif bin.tipo_binbodega.model == 'frutasobrantedeagrupacion':
        if hasattr(bin.binbodega, 'tarja'):
            if hasattr(bin.binbodega.tarja, 'produccion'):
                return f"Programa Producción N° {bin.binbodega.tarja.produccion.pk}"
            elif hasattr(bin.binbodega.tarja, 'reproceso'):
                return f"Programa Reproceso N° {bin.binbodega.tarja.reproceso.pk}"
            elif hasattr(bin.binbodega.tarja, 'seleccion'):
                return f"Programa Selección N° {bin.binbodega.tarja.seleccion.pk}"
    return "No se puede determinar el programa asociado a este bin"


def calcular_duracion(fecha_inicio: datetime, fecha_termino: datetime) -> str:
    if fecha_termino:
        duracion = fecha_termino - fecha_inicio
        dias_duracion = duracion.days
        horas_duracion, remainder = divmod(duracion.seconds, 3600)
        minutos_duracion = remainder // 60
        return f"{dias_duracion} días, {horas_duracion} horas, {minutos_duracion} minutos"
    else:
        return "Duración no disponible"