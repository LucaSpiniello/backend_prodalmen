from rest_framework import viewsets
from .models import *
from .serializers import *
from cities_light.models import City, Country

from rest_framework.decorators import action
from django.contrib.contenttypes.models import *
from rest_framework.response import Response
from rest_framework import status
from comunas.models import *




class CityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CitySerializer

    def get_queryset(self):
        return City.objects.filter(country_id=self.kwargs['country_pk'])

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    
    
class ClienteMercadoInternoViewSet(viewsets.ModelViewSet):
    lookup_field = 'rut_cliente'
    queryset = ClienteMercadoInterno.objects.all()
    serializer_class = ClienteMercadoInternoSerializer
    

class Cta_CorrienteViewSet(viewsets.ModelViewSet):
    queryset = Cta_Corriente.objects.all()
    serializer_class = Cta_CorrienteSerializer
    
    def list(self, request, *args, **kwargs):
        cliente_rut = self.kwargs.get('cliente_mercado_interno_rut_cliente')
        representantes = self.queryset.filter(cliente__rut_cliente=cliente_rut)
        serializer = self.get_serializer(representantes, many = True)
        return Response(serializer.data)

class SucursalClienteMercadoViewSet(viewsets.ModelViewSet):
    queryset = SucursalClienteMercado.objects.all()
    serializer_class = SucursalClienteMercadoSerializer

class RRLLViewSet(viewsets.ModelViewSet):
    queryset = RRLL.objects.all()
    serializer_class = RRLLSerializer
    
    
    def list(self, request, *args, **kwargs):
        cliente_rut = self.kwargs.get('cliente_mercado_interno_rut_cliente')
        representantes = self.queryset.filter(cliente__rut_cliente=cliente_rut)
        serializer = self.get_serializer(representantes, many = True)
        return Response(serializer.data)
        
        

class ClienteExportacionViewSet(viewsets.ModelViewSet):
    lookup_field = 'dni_cliente'
    queryset = ClienteExportacion.objects.all()
    serializer_class = ClienteExportacionSerializer

class SucursalClienteExportacionViewSet(viewsets.ModelViewSet):
    queryset = SucursalClienteExportacion.objects.all()
    serializer_class = SucursalClienteExportacionSerializer
    
    
class ClientesViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['GET'])
    def unificados(self, request):
        tipo_cliente = request.query_params.get('tipo_cliente')
        clientes = []

        clientes_exportacion = ClienteExportacion.objects.all()
        clientes_interno = ClienteMercadoInterno.objects.all()
        
        ct = ContentType.objects.get_for_model(ClienteExportacion)
        cta = ContentType.objects.get_for_model(ClienteMercadoInterno)
        
        def get_nombre_region(region_id):
            region = Region.objects.using("db_comunas").filter(region_id=region_id).first()
            return region.region_nombre if region else "Desconocida"
        
        def get_nombre_provincia(provincia_id):
            provincia = Provincia.objects.using("db_comunas").filter(provincia_id=provincia_id).first()
            return provincia.provincia_nombre if provincia else "Desconocida"
        
        if ct.model == tipo_cliente:
            for cliente in clientes_exportacion:
                nombre_fantasia = cliente.nombre_fantasia if cliente.nombre_fantasia else 'Aun no tiene nombre de fantasia'
                dic = {
                    "id": cliente.id,
                    "rut_dni": cliente.dni_cliente,
                    "razon_social": cliente.razon_social,
                    "nombre_fantasia": nombre_fantasia, 
                    "pais_ciudad": f'{cliente.pais} / {cliente.ciudad}',
                    "telefono": cliente.telefono if cliente.telefono else "Sin Telefono",
                    "movil": cliente.movil if cliente.movil else "Sin Movil"
                }   
                clientes.append(dic)

        elif cta.model == tipo_cliente:
            for cliente in clientes_interno:
                nombre_region = get_nombre_region(cliente.region)
                nombre_provincia = get_nombre_provincia(cliente.provincia)
                nombre_fantasia = cliente.nombre_fantasia if cliente.nombre_fantasia else 'Aun no tiene nombre de fantasia'
                dic = {
                    "id": cliente.id,
                    "rut_dni": cliente.rut_cliente,
                    "razon_social": cliente.razon_social,
                    "nombre_fantasia": nombre_fantasia,           
                    "pais_ciudad": f'{nombre_region} / {nombre_provincia}',
                    "telefono": cliente.telefono if cliente.telefono else "Sin Telefono",
                    "movil": cliente.movil if cliente.movil else "Sin Movil"
                }
                clientes.append(dic)
        else:
            for cliente in clientes_exportacion:
                nombre_fantasia = cliente.nombre_fantasia if cliente.nombre_fantasia else 'Aun no tiene nombre de fantasia'
                dic = {
                    "id": cliente.id,
                    "rut_dni": cliente.dni_cliente,
                    "razon_social": cliente.razon_social,
                    "nombre_fantasia": nombre_fantasia,
                    "pais_ciudad": f'{cliente.pais} / {cliente.ciudad}',
                    "telefono": cliente.telefono if cliente.telefono else "Sin Telefono",
                    "movil": cliente.movil if cliente.movil else "Sin Movil"
                }
                clientes.append(dic)
            
            for cliente in clientes_interno:
                nombre_region = get_nombre_region(cliente.region)
                nombre_provincia = get_nombre_provincia(cliente.provincia)
                nombre_fantasia = cliente.nombre_fantasia if cliente.nombre_fantasia else 'Aun no tiene nombre de fantasia'
                dic = {
                    "id": cliente.id,
                    "rut_dni": cliente.rut_cliente,
                    "razon_social": cliente.razon_social,
                    "nombre_fantasia": nombre_fantasia,
                    "pais_ciudad": f'{nombre_region} / {nombre_provincia}',
                    "telefono": cliente.telefono if cliente.telefono else "Sin Telefono",
                    "movil": cliente.movil if cliente.movil else "Sin Movil"
                }
                clientes.append(dic)

        serializer = ClientesSerializer(data=clientes, many=True)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
        
    @action(detail=False, methods=['DELETE'])
    def eliminar_cliente(self, request):
        rut_cliente = request.query_params.get('rut')
        
        filtro_exportacion = ClienteExportacion.objects.filter(dni_cliente=rut_cliente).first()
        filtro_interno = ClienteMercadoInterno.objects.filter(rut_cliente=rut_cliente).first()
        
        if filtro_exportacion and filtro_interno:
            if filtro_exportacion.dni_cliente == filtro_interno.rut_cliente:
                return Response({"error": "Este cliente coincide en mercado interno y externo"}, status=status.HTTP_409_CONFLICT)
        
        if filtro_exportacion:
            filtro_exportacion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if filtro_interno:
            filtro_interno.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['GET'])
    def detalle_cliente(self, request):
        rut_cliente = request.query_params.get('rut')
        
        filtro_exportacion = ClienteExportacion.objects.filter(dni_cliente=rut_cliente).first()
        filtro_interno = ClienteMercadoInterno.objects.filter(rut_cliente=rut_cliente).first()
        
        if filtro_exportacion and filtro_interno:
            if filtro_exportacion.dni_cliente == filtro_interno.rut_cliente:
                return Response({"error": "Este cliente coincide en mercado interno y externo"}, status=status.HTTP_409_CONFLICT)
        
        if filtro_exportacion:
            serializer = ClienteExportacionSerializer(filtro_exportacion)
            return Response(serializer.data)
        
        if filtro_interno:
            serializer = ClienteMercadoInternoSerializer(filtro_interno)
            return Response(serializer.data)
        
        return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail = False, methods = ['GET'])
    def sucursales_cliente(self, request):
        rut_cliente = request.query_params.get('rut')
        
        filtro_exportacion = ClienteExportacion.objects.filter(dni_cliente=rut_cliente).first()
        filtro_interno = ClienteMercadoInterno.objects.filter(rut_cliente=rut_cliente).first()
        
        if filtro_exportacion and filtro_interno:
            if filtro_exportacion.dni_cliente == filtro_interno.rut_cliente:
                return Response({"error": "Este cliente coincide en mercado interno y externo"}, status=status.HTTP_409_CONFLICT)
        
        if filtro_exportacion:
            sucursal_exportacion = SucursalClienteExportacion.objects.filter(cliente__pk = filtro_exportacion.pk)
            serializer = SucursalClienteExportacionSerializer(sucursal_exportacion, many = True)
            return Response(serializer.data)
        
        if filtro_interno:
            sucursal_mercadointerno = SucursalClienteMercado.objects.filter(cliente__pk = filtro_interno.pk)
            serializer = SucursalClienteMercadoSerializer(sucursal_mercadointerno, many = True)
            return Response(serializer.data)
        
        return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
