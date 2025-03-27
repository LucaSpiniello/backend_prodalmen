from rest_framework import viewsets
from .models import Pedido, FrutaEnPedido
from .serializers import PedidoSerializer, FrutaEnPedidoSerializer
from django.shortcuts import render, get_object_or_404, get_list_or_404
from exportacion.models import *
from mercadointerno.models import *
from .serializers import *
from collections import defaultdict
from rest_framework.decorators import action
from django.contrib.contenttypes.models import *
from rest_framework.response import Response
from rest_framework import status
from comunas.models import *
from guiassalida.models import *
from django.db import transaction
from embalaje.models import PalletProductoTerminado

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    
    @action(detail=False, methods=['GET'])
    def unificados(self, request):
        tipo_pedido = request.query_params.get('tipo_pedido', None)
        comercializador = request.query_params.get('comercializador', None)
        pedidos = Pedido.objects.filter(tipo_pedido__model=tipo_pedido).order_by('-fecha_creacion')
        resultados = []
        for pedido in pedidos:
            cliente = pedido.pedido.cliente
            if pedido.tipo_pedido.model == 'pedidomercadointerno' and pedido.pedido.comercializador == comercializador:
                sucursal_set_interno = cliente.sucursalclientemercado_set
                sucursal_matriz = sucursal_set_interno.first().nombre if sucursal_set_interno.exists() else 'No tiene sucursal'
                dic = {
                    "id": pedido.pk,
                    "id_pedido": pedido.id_pedido,
                    "tipo_guia": pedido.tipo_pedido.model,
                    "pedido": f'Pedido Mercado Interno N° {pedido.id_pedido}',
                    "razon_social": cliente.razon_social,
                    "despacho_retiro": 'Retiro Cliente' if pedido.pedido.retira_cliente and not sucursal_matriz else sucursal_matriz,
                    "estado_pedido": pedido.get_estado_pedido_display(),
                    "fecha_creacion": pedido.pedido.fecha_creacion,
                    "fecha_entrega": pedido.pedido.fecha_entrega,
                    "comercializador": pedido.pedido.comercializador,
                        }
                resultados.append(dic)
            elif pedido.tipo_pedido.model == 'pedidoexportacion' and pedido.pedido.comercializador == comercializador:
                sucursal_set = cliente.sucursalclienteexportacion_set
                sucursal_matriz = sucursal_set.first().nombre if sucursal_set.exists() else 'No tiene sucursal'
                dic = {
                    "id": pedido.pk,
                    "id_pedido": pedido.id_pedido,
                    "tipo_guia": pedido.tipo_pedido.model,
                    "pedido": f'Pedido Exportación N° {pedido.id_pedido}',
                    "razon_social": cliente.razon_social,
                    "despacho_retiro": 'Retiro Cliente' if pedido.pedido.retira_cliente and not sucursal_matriz else sucursal_matriz,
                    "estado_pedido": pedido.get_estado_pedido_display(),
                    "fecha_creacion": pedido.pedido.fecha_creacion.strftime('%Y-%m-%d'),
                    "fecha_entrega": pedido.pedido.fecha_entrega.strftime('%Y-%m-%d'),
                    "comercializador": pedido.pedido.comercializador,
                        }
                resultados.append(dic)
            elif pedido.tipo_pedido.model == 'guiasalidafruta' and pedido.pedido.comercializador == comercializador:
                # Inicializa cliente_guia con un valor por defecto
                cliente_guia = "Información no disponible"

                if pedido.pedido.tipo_cliente.model == 'productor':
                    if pedido.pedido.cliente:
                        cliente_guia = pedido.pedido.cliente.nombre
                elif pedido.pedido.tipo_cliente.model == 'clientemercadointerno':
                    if pedido.pedido.cliente:
                        cliente_guia = pedido.pedido.cliente.nombre_fantasia
                elif pedido.pedido.tipo_cliente.model == 'clienteexportacion':
                    if pedido.pedido.cliente:
                        cliente_guia = pedido.pedido.cliente.nombre_fantasia
                elif pedido.pedido.tipo_cliente.model == 'user':
                    if pedido.pedido.cliente:
                        cliente_guia = f'{pedido.pedido.cliente.first_name} {pedido.pedido.cliente.last_name}'

                                
                dic = {
                    "id": pedido.pk,
                    "id_guia": pedido.pedido.id,
                    "cliente": cliente_guia,
                    "tipo_guia": pedido.pedido.get_tipo_salida_display(),
                    "despacho_retiro": 'Retiro Cliente' if pedido.pedido.retira_cliente else 'Despacho',
                    "estado_pedido": pedido.pedido.get_estado_guia_salida_display(),
                    "fecha_creacion": pedido.pedido.fecha_creacion,
                    "fecha_entrega": pedido.pedido.fecha_entrega,
                    "comercializador": pedido.pedido.comercializador,
                }
                            
                resultados.append(dic)
        if tipo_pedido == 'guiasalidafruta':
            serializer = PedidoGuiaSerializer(data = resultados, many=True)
        else:
            serializer = PedidosUnidosSerializer(data = resultados, many=True)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def all_pedidos(self, request):
        comercializador = request.query_params.get('comercializador', None)
        tipos_pedido = ['pedidomercadointerno', 'pedidoexportacion', 'guiasalidafruta']
        fruta_pedidos = []

        # Diccionario para agrupar los pedidos por calidad, calibre y variedad
        grouped_pedidos = defaultdict(float)

        for tipo_pedido in tipos_pedido:
            pedidos = Pedido.objects.filter(tipo_pedido__model=tipo_pedido)
            
            for pedido in pedidos:
                if pedido.pedido.comercializador == comercializador:
                    pedido_real = pedido.pedido_real
                    fruta_ficticia = list(pedido_real.fruta_pedido.all())
                    for fruta_pedido in fruta_ficticia:
                        key = (
                            fruta_pedido.get_calidad_display(),
                            fruta_pedido.get_calibre_display(),
                            fruta_pedido.get_variedad_display()
                        )
                        grouped_pedidos[key] += fruta_pedido.kilos_solicitados

        # Convertir el diccionario agrupado en una lista de diccionarios
        for key, kilos_solicitados in grouped_pedidos.items():
            fruta_pedidos.append({
                'kilos_solicitados': kilos_solicitados,
                'calidad': key[0],
                'calibre': key[1],
                'variedad': key[2],
            })

        return Response(fruta_pedidos)
           
    @action(detail = False, methods = ['DELETE'])
    def eliminar_pedido(self, request):
        tipo_pedido = request.query_params.get('tipo_pedido')
        id = request.query_params.get('id')
        
        pedido_exportacion = PedidoExportacion.objects.all().order_by('fecha_creacion')
        pedido_mercadointerno = PedidoMercadoInterno.objects.all().order_by('fecha_creacion')
        guia_salida = GuiaSalidaFruta.objects.all().order_by('fecha_creacion')
        
        ct_exportacion = ContentType.objects.get_for_model(PedidoExportacion)
        ct_mercadointerno = ContentType.objects.get_for_model(PedidoMercadoInterno)
        ct_guia_salida = ContentType.objects.get_for_model(GuiaSalidaFruta)
        
        if ct_exportacion.model == tipo_pedido:
            pedido_exportacion.filter(pk = id).delete()
        
        elif ct_mercadointerno.model == tipo_pedido:
            pedido_mercadointerno.filter(pk = id).delete()
            
        elif ct_guia_salida.model == tipo_pedido:
            guia_salida.filter(pk = id).delete()
            
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, pk=None):
        pedido = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

# class FrutaEnPedidoViewSet(viewsets.ModelViewSet):
#     queryset = FrutaEnPedido.objects.all()
#     serializer_class = FrutaEnPedidoSerializer
    
#     def list(self, request, pedido_pk=None):
#         queryset = self.queryset.filter(pedido = pedido_pk)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
    
#     @action(detail=True, methods=['post'], url_path='agregar-cajas', url_name='agregar_cajas')
#     def agregar_cajas_ppt(self, request, pedido_pk=None, pk=None):
#         pedido = get_object_or_404(Pedido, pk=pedido_pk)
#         fruta_en_pedido = get_object_or_404(FrutaEnPedido, pedido=pedido, pk=pk)
#         if fruta_en_pedido.tipo_fruta.model == 'palletproductoterminado':
#             pallet = fruta_en_pedido.fruta_real
#             kilos = request.data.get('kilos')
#             razon = request.data.get('razon')
#             if kilos and razon:
#                 try:
#                     pallet.agregar_cajas_por_kilos(kilos, razon)
#                     return Response({'status': 'cajas agregadas'}, status=status.HTTP_200_OK)
#                 except Exception as e:
#                     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({'error': 'Tipo de fruta no es PalletProductoTerminado'}, status=status.HTTP_400_BAD_REQUEST)
    
#     @action(detail=True, methods=['post'], url_path='descontar-cajas', url_name='descontar_cajas')
#     def descontar_cajas_ppt(self, request, pk=None):
#         fruta_en_pedido = self.get_object()
#         if fruta_en_pedido.tipo_fruta.model == 'palletproductoterminado':
#             pallet = fruta_en_pedido.fruta_real
#             kilos = request.data.get('kilos')
#             razon = request.data.get('razon')
#             if kilos and razon:
#                 try:
#                     pallet.descontar_cajas_por_kilos(kilos, razon)
#                     return Response({'status': 'cajas descontadas'}, status=status.HTTP_200_OK)
#                 except Exception as e:
#                     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({'error': 'Tipo de fruta no es PalletProductoTerminado'}, status=status.HTTP_400_BAD_REQUEST)

class FrutaEnPedidoViewSet(viewsets.ModelViewSet):
    queryset = FrutaEnPedido.objects.all()
    serializer_class = FrutaEnPedidoSerializer

    def create(self, request, *args, **kwargs):
        print("Creando FrutaEnPedido")
        with transaction.atomic():
            response = super().create(request, *args, **kwargs)
            print(f"FrutaEnPedido creado con id {response.data['id']}")
            self.actualizar_inventario(response.data['id'], 'agregar')
        return response

    def update(self, request, *args, **kwargs):
        print("Actualizando FrutaEnPedido")
        with transaction.atomic():
            instance = self.get_object()
            cantidad_anterior = instance.cantidad
            response = super().update(request, *args, **kwargs)
            nueva_cantidad = response.data['cantidad']
            print(f"FrutaEnPedido actualizado con id {instance.id}, cantidad anterior {cantidad_anterior}, nueva cantidad {nueva_cantidad}")
            self.actualizar_inventario(instance.id, 'actualizar', cantidad_anterior, nueva_cantidad)
        return response

    def destroy(self, request, *args, **kwargs):
        print("Eliminando FrutaEnPedido")
        with transaction.atomic():
            instance = self.get_object()
            print(f"FrutaEnPedido eliminado con id {instance.id}")
            self.actualizar_inventario(instance.id, 'descontar')
            response = super().destroy(request, *args, **kwargs)
        return response

    # def actualizar_inventario(self, fruta_en_pedido_id, accion, cantidad_anterior=None, nueva_cantidad=None):
    #     print(f"Actualizando inventario para FrutaEnPedido id {fruta_en_pedido_id} con acción {accion}")
    #     fruta_en_pedido = FrutaEnPedido.objects.get(id=fruta_en_pedido_id)
    #     pkpallet = fruta_en_pedido.id_fruta
    #     if fruta_en_pedido.tipo_fruta.model == 'palletproductoterminado':
    #         pallet = PalletProductoTerminado.objects.get(pk=pkpallet) 

    #     if not isinstance(pallet, PalletProductoTerminado):
    #         print("El tipo de fruta no es PalletProductoTerminado, no se requiere actualizar inventario")
    #         return

    #     if accion == 'agregar':
    #         razon = "Agregado al inventario por pedido"
    #         print(f"Descontando {fruta_en_pedido.cantidad} kilos del pallet {pallet.codigo_pallet}")
    #         pallet.descontar_cajas_por_kilos(fruta_en_pedido.cantidad, razon)
            
    #     elif accion == 'descontar':
    #         razon = "Devuelto al inventario por eliminación del pedido"
    #         print(f"Agregando {fruta_en_pedido.cantidad} kilos al pallet {pallet.codigo_pallet}")
    #         pallet.agregar_cajas_por_kilos(fruta_en_pedido.cantidad, razon)
            
    #     elif accion == 'actualizar':
    #         if cantidad_anterior is not None and nueva_cantidad is not None:
    #             diferencia = nueva_cantidad - cantidad_anterior
    #             if diferencia > 0:
    #                 razon = f"Descuento adicional de {diferencia} kg por actualización del pedido"
    #                 print(f"Descontando {diferencia} kilos del pallet {pallet.codigo_pallet}")
    #                 pallet.descontar_cajas_por_kilos(diferencia, razon)
    #             elif diferencia < 0:
    #                 razon = f"Devolución de {-diferencia} kg por actualización del pedido"
    #                 print(f"Agregando {-diferencia} kilos al pallet {pallet.codigo_pallet}")
    #                 pallet.agregar_cajas_por_kilos(-diferencia, razon)
           
    def actualizar_inventario(self, fruta_en_pedido_id, accion, cantidad_anterior=None, nueva_cantidad=None):
        print(f"Actualizando inventario para FrutaEnPedido id {fruta_en_pedido_id} con acción {accion}")
        fruta_en_pedido = FrutaEnPedido.objects.get(id=fruta_en_pedido_id)
        pkpallet = fruta_en_pedido.id_fruta
        if fruta_en_pedido.tipo_fruta.model == 'palletproductoterminado':
            pallet = PalletProductoTerminado.objects.get(pk=pkpallet) 

            if not isinstance(pallet, PalletProductoTerminado):
                print("El tipo de fruta no es PalletProductoTerminado, no se requiere actualizar inventario")
                return

            if accion == 'agregar':
                razon = "Agregado al inventario por pedido"
                print(f"Descontando {fruta_en_pedido.cantidad} kilos del pallet {pallet.codigo_pallet}")
                pallet.descontar_cajas_por_kilos(fruta_en_pedido.cantidad, razon, fruta_en_pedido)
                    
            elif accion == 'descontar':
                razon = "Devuelto al inventario por eliminación del pedido"
                print(f"Agregando {fruta_en_pedido.cantidad} kilos al pallet {pallet.codigo_pallet}")
                pallet.agregar_cajas_por_kilos(fruta_en_pedido.cantidad, razon, fruta_en_pedido)
                    
            elif accion == 'actualizar':
                if cantidad_anterior is not None and nueva_cantidad is not None:
                    diferencia = nueva_cantidad - cantidad_anterior
                    if diferencia > 0:
                        razon = f"Descuento adicional de {diferencia} kg por actualización del pedido"
                        print(f"Descontando {diferencia} kilos del pallet {pallet.codigo_pallet}")
                        pallet.descontar_cajas_por_kilos(diferencia, razon, fruta_en_pedido)
                    elif diferencia < 0:
                        razon = f"Devolución de {-diferencia} kg por actualización del pedido"
                        print(f"Agregando {-diferencia} kilos al pallet {pallet.codigo_pallet}")
                        pallet.agregar_cajas_por_kilos(-diferencia, razon, fruta_en_pedido)               
class FrutaFicticaViewSet(viewsets.ModelViewSet):
    queryset = FrutaFicticia.objects.all()
    serializer_class = FrutaFicticiaSerializer