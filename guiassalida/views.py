    # viewsets.py
from rest_framework import viewsets, status
from .models import GuiaSalidaFruta
from rest_framework.decorators import action
from .serializers import GuiaSalidaFrutaSerializer
from django.contrib.contenttypes.models import *
from productores.models import *
from productores.serializers import *
from cuentas.models import *
from cuentas.serializers import *
from clientes.models import *
from clientes.serializers import *
from rest_framework.response import Response
from pedidos.models import *
from bodegas.funciones import *
from .funciones import *

class GuiaSalidaFrutaViewSet(viewsets.ModelViewSet):
    queryset = GuiaSalidaFruta.objects.all()
    serializer_class = GuiaSalidaFrutaSerializer
    
    @action(detail = False, methods = ['GET'])
    def tipo_cliente(self, request):
        tipo_cliente = request.query_params.get('tipo_cliente')
        
        ct_productor = ContentType.objects.get_for_model(Productor)
        ct_usuarios = ContentType.objects.get_for_model(User)
        ct_clientes_interno = ContentType.objects.get_for_model(ClienteMercadoInterno)
        ct_clientes_exportacion = ContentType.objects.get_for_model(ClienteExportacion)

        if tipo_cliente == ct_productor.model:
            productores = Productor.objects.all()
            serializador_productor = ProductorSerializer(productores, many = True)
            return Response(serializador_productor.data)
        elif tipo_cliente == ct_usuarios.model:
            usuarios = User.objects.all()
            serializer_user = UserSerializer(usuarios, many = True)
            return Response(serializer_user.data)
        elif tipo_cliente == ct_clientes_interno.model:
            clientes_internos = ClienteMercadoInterno.objects.all()
            
            serializer_cliente_interno = ClienteMercadoInternoSerializer(clientes_internos, many = True)
            return Response(serializer_cliente_interno.data)
        elif tipo_cliente == ct_clientes_exportacion.model:
            cliente_exportacion = ClienteExportacion.objects.all()
            serializer_cliente_exportacion = ClienteExportacionSerializer(cliente_exportacion, many = True)
            return Response(serializer_cliente_exportacion.data)
        else:
            return Response({ 'message': 'No se encontro ningun cliente'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def pdf_guia_salida(self, request, pk = None):
        guia = GuiaSalidaFruta.objects.filter(pk = pk).first()
        ct = ContentType.objects.get_for_model(guia)
        pedido = Pedido.objects.filter(tipo_pedido = ct, id_pedido = guia.pk).first()
        fruta_pedido = FrutaEnPedido.objects.filter(pedido = pedido)
        resultados = []
        for fruta in fruta_pedido:
            codigo = obtener_codigo(fruta)
            programa = obtener_programa_guia(fruta)
            producto = obtener_producto(fruta)
            calidad = obtener_calidad(fruta)
            variedad = obtener_variedad(fruta)
            calibre = obtener_calibre(fruta)
            print(variedad)
            
            dic = {
                "codigo": codigo,
                "programa": programa,
                "producto": producto,
                "calidad": calidad,
                "variedad": variedad,
                "calibre": calibre
            }
            
            resultados.append(dic)
            
        serializer = GuiaSalidaFrutaSerializer(guia)
            
        return Response({
            "guia": serializer.data,
            "fruta_en_guia": resultados})
        
    @action(detail=False, methods=['get'])
    def lista_clientes(self, request):
        try:
            # Obtener los ContentType IDs
            content_type_productor = ContentType.objects.get_for_model(Productor)
            content_type_cliente_mercado_interno = ContentType.objects.get_for_model(ClienteMercadoInterno)
            content_type_cliente_exportacion = ContentType.objects.get_for_model(ClienteExportacion)
            content_type_user = ContentType.objects.get_for_model(User)

            # Crear una lista de diccionarios con la información deseada
            clientes_info = []

            # Productores
            for productor in Productor.objects.all():
                clientes_info.append({
                    'nombre': productor.nombre,
                    'id_cliente': productor.id,
                    'content_type_id': content_type_productor.id
                })

            # Clientes de Mercado Interno
            for cliente in ClienteMercadoInterno.objects.all():
                clientes_info.append({
                    'nombre': cliente.nombre_fantasia or cliente.razon_social,
                    'id_cliente': cliente.id,
                    'content_type_id': content_type_cliente_mercado_interno.id
                })

            # Clientes de Exportación
            for cliente in ClienteExportacion.objects.all():
                clientes_info.append({
                    'nombre': cliente.nombre_fantasia or cliente.razon_social,
                    'id_cliente': cliente.id,
                    'content_type_id': content_type_cliente_exportacion.id
                })

            # Usuarios
            for user in User.objects.all():
                clientes_info.append({
                    'nombre': user.get_nombre_completo(),
                    'id_cliente': user.id,
                    'content_type_id': content_type_user.id
                })

            # Ahora `clientes_info` contiene todos los datos necesarios
            return Response(clientes_info, status=status.HTTP_200_OK)
        except:
            return Response("Error en la lista", status=status.HTTP_400_BAD_REQUEST)
    
# class FrutaEnGuiaSalidaViewSet(viewsets.ModelViewSet):
#     queryset = FrutaEnGuiaSalida.objects.all()
#     serializer_class = FrutaEnGuiaSalidaSerializer
    
#     def list(self, request, guiasalida_pk=None):
#         queryset = self.queryset.filter(guiasalida = guiasalida_pk)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
