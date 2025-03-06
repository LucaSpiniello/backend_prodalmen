from .models import EtiquetasZpl
import paho.mqtt.publish as publicamqtt
import socket

def etiqueta_produccion(codigo_tarja="", variedad="", pkprograma="", kilos_fruta="", calibre="", fecha="", fecha_programa=""):
    bodega = '2' if 'G2-' in codigo_tarja else '1'
    tipo_fruta = 'Calibrada' if 'G2-' in codigo_tarja else 'Borrel'
    fecha = fecha.split(' ')
    fecha = fecha[0].split('-')
    fecha = f'{fecha[2]}-{fecha[1]}-{fecha[0]}'
    
    fecha_programa = fecha_programa.split(' ')
    fecha_programa = fecha_programa[0].split('-')
    fecha_programa = f'{fecha_programa[2]}-{fecha_programa[1]}-{fecha_programa[0]}'
    etiqueta = EtiquetasZpl.objects.get(pk=4)
    zpl = etiqueta.zpl
    
    zpl = zpl.format(bodega, codigo_tarja, variedad.upper(), tipo_fruta, fecha, pkprograma, kilos_fruta, calibre, fecha_programa, codigo_tarja)
    #10X10.format(bodega, codigo_tarja, codigo_tarja, variedad.upper(), tipo_fruta, pkprograma, kilos_fruta, calibre, fecha)
    try:
        mqttauth = {'username': 'user01', 'password':'Hola.2020'}
        publicamqtt.single('prodalmen/produccion/pesaje', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    except Exception as e:
        print(e)
    
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('10.10.10.114', 9100))
    # s.send(zpl.encode())
    # s.close()

def etiqueta_seleccion(codigo_tarja="", variedad="", fecha="", pk="", kilos_fruta="", calibre="", calidad="", fecha_programa="", tipo_fruta=""):
    print(f"codigo_tarja: {codigo_tarja} variedad: {variedad} fecha: {fecha} pk: {pk} kilos_fruta: {kilos_fruta} calibre: {calibre} calidad: {calidad} fecha_programa: {fecha_programa} tipo_fruta: {tipo_fruta}")
    if codigo_tarja.startswith('G4-'):
        bodega = '4'
    elif codigo_tarja.startswith('G3-'):
        bodega = '3'
    elif codigo_tarja.startswith('G5-'):
        bodega = '5'
    if tipo_fruta == None:
        if codigo_tarja.startswith('G4-'):
            tipo_fruta = 'Seleccionada'
            
        elif codigo_tarja.startswith('G3-'):
            tipo_fruta = 'Descarte Sea'
            
        elif codigo_tarja.startswith('G5-'):
            tipo_fruta = 'Whole & Broken'
            
    
    fecha = fecha.split(' ')
    fecha = fecha[0].split('-')
    fecha = f'{fecha[2]}-{fecha[1]}-{fecha[0]}'
    
    fecha_programa = fecha_programa.split(' ')
    fecha_programa = fecha_programa[0].split('-')
    fecha_programa = f'{fecha_programa[2]}-{fecha_programa[1]}-{fecha_programa[0]}'
    
    etiqueta = EtiquetasZpl.objects.get(pk=5)
    zpl = etiqueta.zpl
    
    zpl = zpl.format(bodega, codigo_tarja, variedad.upper(), tipo_fruta, fecha, pk, kilos_fruta, calibre, fecha_programa, codigo_tarja, calidad)
    #10x10 .format(bodega, codigo_tarja, codigo_tarja, variedad.upper(), tipo_fruta, fecha, pk, kilos_fruta, calibre, calidad)
    
    # Descomentar para deploy
    try:
        mqttauth = {'username': 'user01', 'password':'Hola.2020'}
        publicamqtt.single('prodalmen/seleccion/programa', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    except Exception as e:
        print(e)
    
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('10.10.10.114', 9100))
    # s.send(zpl.encode())
    # s.close()
    
def etiqueta_programa_ph(codigo_tarja='', fecha='', pk='', kilos_fruta='', humedad='', piel_aderida='', calidad='', tipo_resultante='', fecha_programa=''):
    tipo_fruta = 'Semi-Elab'
    etiqueta = EtiquetasZpl.objects.get(pk=6)
    zpl = etiqueta.zpl
    
    fecha = fecha.split(' ')
    fecha = fecha[0].split('-')
    fecha = f'{fecha[2]}-{fecha[1]}-{fecha[0]}'
    
    fecha_programa = fecha_programa.split(' ')
    fecha_programa = fecha_programa[0].split('-')
    fecha_programa = f'{fecha_programa[2]}-{fecha_programa[1]}-{fecha_programa[0]}'
    
    zpl = zpl.format(codigo_tarja, tipo_resultante, calidad, fecha, pk, kilos_fruta, humedad, fecha_programa, codigo_tarja, piel_aderida)
    #10x10 .format('6', codigo_tarja, codigo_tarja, tipo_resultante, tipo_fruta, fecha, pk, kilos_fruta, f'{humedad}%', f'{piel_aderida}%', calidad)
    try:
        mqttauth = {'username': 'user01', 'password':'Hola.2020'}
        publicamqtt.single('prodalmen/embalaje/programa', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    except Exception as e:
        print(e)
    # publicamqtt.single('snabbit/produccion/pesaje', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('10.10.10.114', 9100))
    # s.send(zpl.encode())
    # s.close()
    
def etiqueta_proceso_ph(codigo_tarja='', fecha='', pk='', kilos_fruta='', humedad='', piel_aderida='', calidad='', tipo_resultante='', fecha_programa='', granulometria='', parametro=''):
    # tipo_fruta = 'Semi-Elab'
    etiqueta = EtiquetasZpl.objects.get(pk=7)
    zpl = etiqueta.zpl
    
    fecha = fecha.split(' ')
    fecha = fecha[0].split('-')
    fecha = f'{fecha[2]}-{fecha[1]}-{fecha[0]}'
    
    fecha_programa = fecha_programa.split(' ')
    fecha_programa = fecha_programa[0].split('-')
    fecha_programa = f'{fecha_programa[2]}-{fecha_programa[1]}-{fecha_programa[0]}'
    
    zpl = zpl.format(codigo_tarja, tipo_resultante, calidad, fecha, pk, kilos_fruta, humedad, fecha_programa, codigo_tarja, piel_aderida, granulometria, parametro)
    try:
        mqttauth = {'username': 'user01', 'password':'Hola.2020'}
        publicamqtt.single('prodalmen/embalaje/programa', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    except Exception as e:
        print(e)
    # publicamqtt.single('snabbit/produccion/pesaje', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('10.10.10.114', 9100))
    # s.send(zpl.encode())
    # s.close()
    
def etiqueta_pallets(codigo_tarja='', calidad='', variedad='', calibre='', pkprograma='', kilos_pallet='', fecha_programa='', fecha_pallet='', tipo_embalaje='', cantidad_cajas=''):

    fecha_pallet = fecha_pallet.split(' ')
    hora = fecha_pallet[1].split(':')
    fecha_pallet = fecha_pallet[0].split('-')
    fecha_pallet = f'{fecha_pallet[2]}-{fecha_pallet[1]}-{fecha_pallet[0]} {hora[0]}:{hora[1]} Hrs'

    fecha_programa = fecha_programa.split(' ')
    hora = fecha_programa[1].split(':')
    fecha_programa = fecha_programa[0].split('-')
    fecha_programa = f'{fecha_programa[2]}-{fecha_programa[1]}-{fecha_programa[0]} {hora[0]}:{hora[1]} Hrs'

    etiqueta = EtiquetasZpl.objects.get(pk=8)
    zpl = etiqueta.zpl
    zpl = zpl.format(codigo_tarja, calidad, variedad.upper(), calibre, pkprograma, kilos_pallet, fecha_programa, codigo_tarja, fecha_pallet, tipo_embalaje, cantidad_cajas)
    try:
        mqttauth = {'username': 'user01', 'password':'Hola.2020'}
        publicamqtt.single('prodalmen/embalaje/programa', zpl, qos = 1, hostname='192.168.200.22', auth=mqttauth)
    except Exception as e:
        print(e)

    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('10.10.10.114', 9100))
    # s.send(zpl.encode())
    # s.close()