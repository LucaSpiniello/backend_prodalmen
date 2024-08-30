from agrupacionbins.models import *
from django.db.models import Q
from controlcalidad.models import *
from .models import *
from bodegas.models import *




def obtener_codigo_tarja_inventario(bin):
    return bin.binbodega.codigo_tarja_bin
    
def obtener_programa_inventario(bin):
    return bin.binbodega.origen_tarja


def obtener_variedad_inventario(bin):
    return bin.binbodega.variedad
    
    
def obtener_calibre_inventario(bin):
    return bin.binbodega.calibre


def obtener_calidad_inventario(bin):
    return bin.binbodega.calidad


# def obtener_kilos_fruta_pallet_inventario(pallet):
#   kilos = 0
#   for caja in CajasEnPalletProductoTerminado.objects.filter(pallet = pallet):
#     kilos += (caja.peso_x_caja *  caja.cantidad_cajas)
    
#   return round(kilos, 2)


def obtener_calle_inventario(obj):
  return obj.binbodega.binbodega.get_calle_bodega_display()

def bodegas_filtradas(bodega_list, calle_list):
    tipos_bodegas_unidas = []
    bodegasunidas = []

    bins = BinBodega.objects.all().exclude(
        Q(ingresado=True) |
        Q(procesado=True) |
        Q(agrupado=True) |
        Q(estado_binbodega='-')
    )

    for bodega in bodega_list:
        bins_filtrados = [
            bin for bin in bins 
            if bin.codigo_tarja_bin and bin.codigo_tarja_bin.lower().startswith(bodega.lower())
            and bin.calle_bodega in calle_list
        ]
        tipos_bodegas_unidas.extend([bin.tipo_binbodega for bin in bins_filtrados])
        bodegasunidas.extend(bins_filtrados)

    return {'tipos_bodegas_unidas': list(set(tipos_bodegas_unidas)), 'bodegasunidas': bodegasunidas}



def filtrar_por_codigo_tarja_bin(queryset, prefix):
    return [obj for obj in queryset if obj.codigo_tarja_bin and obj.codigo_tarja_bin.lower().startswith(prefix.lower())]

def filtrar_por_calle_bodega(queryset, calle_bodega):
    return [obj for obj in queryset if obj.calle_bodega and obj.calle_bodega.lower() == calle_bodega.lower()]

def filtrar_por_variedad(queryset, variedad):
    return [obj for obj in queryset if obj.variedad and variedad.lower() in obj.variedad.lower()]

def filtrar_por_calibre(queryset, calibre):
    return [obj for obj in queryset if obj.calibre and calibre.lower() in obj.calibre.lower()]

def filtrar_por_calidad(queryset, calidad):
    return [obj for obj in queryset if obj.calidad and calidad.lower() in obj.calidad.lower()]