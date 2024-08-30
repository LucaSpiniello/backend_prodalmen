from http.client import METHOD_NOT_ALLOWED
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .serializers import *
from .models import *
from produccion.models import *
from recepcionmp.models import *
from rest_framework import viewsets, filters, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .funciones import *
import json
from cuentas.models import PersonalizacionPerfil
from .filtros import *
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction



from django.db.models import Sum, Avg, F

class CCRecepcionMateriaPrimaVBViewSet(viewsets.ModelViewSet):
    search_fields = ['recepcionmp__id']
    filter_backends = (filters.SearchFilter, )
    queryset = CCRecepcionMateriaPrima.objects.all()
    permission_classes = [IsAuthenticated,]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CCRecepcionMateriaPrimaFilter
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset.filter(estado_aprobacion_cc='1')
            else:
                qs = CCRecepcionMateriaPrima.objects.filter(fecha_creacion__year = anio, estado_aprobacion_cc='1')
                return qs
        except:
            return self.queryset
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:    
            return CCRecepcionMateriaPrimaSerializer
        return DetalleCCRecepcionMateriaPrimaSerializer
    
    def retrieve(self, request, pk=None):
        ccrecepcionmp = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(ccrecepcionmp)
        return Response(serializer.data)
    
    

        
    

    @action(detail=False, methods=['get'])
    def total_guias_cc_recepcion_aprobadas(self, request):
        total_guias_cc_aprobadas = self.get_queryset().filter(estado_cc="1").count()
        return Response(total_guias_cc_aprobadas)
    
    @action(detail=False, methods=['get'])
    def total_guias_cc_recepcion_pendientes(self, request):
        total_guias_cc_pendientes = self.get_queryset().filter(estado_cc="2").count()
        return Response(total_guias_cc_pendientes)

    @action(detail=True, methods=['POST'])
    def registra_muestra_lote(self, request, pk=None):
        ccrecep = get_object_or_404(self.get_queryset(), pk=pk)
        serializadorcdr = CCRendimientoSerializer(data=request.data)
        serializadorcdr.is_valid(raise_exception=True)
        serializadorcdr.save(cc_recepcionmp=ccrecep)
        return Response(serializadorcdr.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['GET'])
    def lista_muestra_lote(self, request, pk=None):
        ccrecep = get_object_or_404(self.get_queryset(), pk=pk)
        listamuestras = get_list_or_404(CCRendimiento, cc_recepcionmp=ccrecep)
        serializer = CCRendimientoSerializer(listamuestras, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def cantidad_muestras_cdc(self, request, pk=None):
        ccrecep = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(ccrecep.ccrendimiento_set.all().count())
    
        
    @action(detail=False, methods=['POST'], url_path='rendimiento_lotes/(?P<pks_lotes>[^/.]+)')
    def rendimiento_lotes(self, request, pks_lotes=None):
        variedad = request.query_params.get('variedad')
        
        #print(variedad)
        
        lotes_pks = pks_lotes.split(',')
        cc_muestra = get_list_or_404(RecepcionMp, pk__in=lotes_pks, envasesguiarecepcionmp__variedad=variedad)
        numero_lote = cc_muestra[0].numero_lote
        muestra = cc_muestras_lotes(cc_muestra)
        cc_pepa = cc_pepa_lote(cc_muestra)
        cc_pepa_calibre = cc_pepa_calibres_lote(cc_muestra)
        cc_descuentos = descuentos_cat2_desechos(cc_pepa, muestra)
        cc_aporte_pex = aporte_pex(cc_descuentos, muestra)
        cc_porcentaje_liquidar = porcentaje_a_liquidar(cc_aporte_pex)
        cc_kilos_desc_merma = kilos_descontados_merma(cc_porcentaje_liquidar, muestra)
        cc_merma_por = merma_porcentual(cc_aporte_pex, cc_porcentaje_liquidar)
        cc_calculo_final = calculo_final(muestra, cc_merma_por, cc_descuentos, cc_kilos_desc_merma)
        
        
        promedio_cc_muestras = promedio_porcentaje_muestras(muestra)
        promedio_por_cc_pepa = promedio_porcentaje_cc_pepa(cc_pepa)
        promedio_cc_pepa_calibrada = promedio_porcentaje_calibres(cc_pepa_calibre)
        
        
        cc_muestra_serializado = MuestraSerializer(muestra, many=True).data
        cc_pepa_serializado = CCPepaMuestraSerializer(cc_pepa, many=True).data
        cc_pepa_calibre_serializado = CalibresSerializer(cc_pepa_calibre, many=True).data
        cc_descuentos_serializado = DescuentosSerializer(cc_descuentos, many=True).data
        cc_aportes_pex_serializado = AportePexSerializer(cc_aporte_pex, many=True).data
        cc_porcentaje_liquidar_serializado = PorcentajeLiquidarSerializer(cc_porcentaje_liquidar, many=True).data
        cc_kilos_desc_merma_serializado = KilosMermaSerializer(cc_kilos_desc_merma, many=True).data
        cc_merma_por_serializador = MermaPorcentajeSerializer(cc_merma_por, many=True).data
        cc_calculo_final = CalculoFinalSerializer(cc_calculo_final).data
        

        cc_promedio_porcentaje_muestra = PromedioMuestra(promedio_cc_muestras).data
        cc_promedio_porcentaje_cc_pepa = PromedioPepaMuestraSerializer(promedio_por_cc_pepa).data
        cc_promedio_porcentaje_cc_pepa_calibrada = PromedioCalibresSerializer(promedio_cc_pepa_calibrada).data
        

        return Response({   
            'cc_muestra': cc_muestra_serializado,
            'cc_pepa': cc_pepa_serializado,
            'cc_pepa_calibre': cc_pepa_calibre_serializado,
            'cc_descuentos': cc_descuentos_serializado,
            'cc_aportes_pex': cc_aportes_pex_serializado,
            'cc_porcentaje_liquidar': cc_porcentaje_liquidar_serializado,
            'cc_kilos_des_merma': cc_kilos_desc_merma_serializado,
            'cc_merma_porc': cc_merma_por_serializador,
            'cc_calculo_final': cc_calculo_final,
            'cc_promedio_porcentaje_muestras': cc_promedio_porcentaje_muestra,
            'cc_promedio_porcentaje_cc_pepa': cc_promedio_porcentaje_cc_pepa,
            'cc_promedio_porcentaje_cc_pepa_calibradas': cc_promedio_porcentaje_cc_pepa_calibrada,
            'numero_lote': numero_lote,
        })
         

    
class CCRecepcionMateriaPrimaViewSet(viewsets.ModelViewSet):
    search_fields = ['recepcionmp__id']
    filter_backends = (filters.SearchFilter, )
    queryset = CCRecepcionMateriaPrima.objects.all()
    # lookup_field = 'recepcionmp'
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCRecepcionMateriaPrima.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def list(self,request):
        queryset= self.get_queryset().exclude(estado_cc='0')
        serializer= self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):        
        if self.action in ["create", "update", "partial_update", "destroy"]:    
            return CCRecepcionMateriaPrimaSerializer
        return DetalleCCRecepcionMateriaPrimaSerializer
    
    def retrieve(self, request, pk=None):
        ccrecepcionmp = get_object_or_404(CCRecepcionMateriaPrima, pk=pk)
        serializer = self.get_serializer(ccrecepcionmp)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def total_guias_cc_recepcion_aprobadas(self, request):
        total_guias_cc_aprobadas = CCRecepcionMateriaPrima.objects.filter(estado_cc="1").count()
        return Response(total_guias_cc_aprobadas)
    
    @action(detail=False, methods=['get'])
    def total_guias_cc_recepcion_pendientes(self, request):
        total_guias_cc_pendientes = CCRecepcionMateriaPrima.objects.filter(estado_cc="2").count()
        return Response(total_guias_cc_pendientes)

    @action(detail=True, methods=['POST'])
    def registra_muestra_lote(self, request, pk=None):
        ccrecep = get_object_or_404(CCRecepcionMateriaPrima, pk=pk)
        serializadorcdr = CCRendimientoSerializer(data=request.data)
        serializadorcdr.is_valid(raise_exception=True)
        serializadorcdr.save(cc_recepcionmp=ccrecep)
        return Response(serializadorcdr.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['GET'])
    def lista_muestra_lote(self, request, pk=None):
        ccrecep = get_object_or_404(CCRecepcionMateriaPrima, pk=pk)
        listamuestras = get_list_or_404(CCRendimiento, cc_recepcionmp=ccrecep)
        serializer = CCRendimientoSerializer(listamuestras, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def cantidad_muestras_cdc(self, request, pk=None):
        ccrecep = get_object_or_404(CCRecepcionMateriaPrima, pk=pk)
        return Response(ccrecep.ccrendimiento_set.all().count())
    
        
    @action(detail=False, methods=['POST'], url_path='rendimiento_lotes/(?P<pks_lotes>[^/.]+)')
    def rendimiento_lotes(self, request, pks_lotes=None):
        variedad = request.query_params.get('variedad')
        lotes_pks = pks_lotes.split(',')
        
        cc_muestra = None
        
            # Intentar obtener lotes con la variedad específica si se proporciona
        if variedad:
            cc_muestra = RecepcionMp.objects.filter(pk__in=lotes_pks, envasesguiarecepcionmp__variedad=variedad)
            if variedad == 'todas' or variedad == 'NN':
                cc_muestra = RecepcionMp.objects.filter(pk__in=lotes_pks)
            else:
                cc_muestra = RecepcionMp.objects.filter(pk__in=lotes_pks, envasesguiarecepcionmp__variedad=variedad)
        else:
            # Si no se proporciona variedad, obtener todos los lotes
            cc_muestra = []

        
        numero_lote = cc_muestra[0].numero_lote
        muestra = cc_muestras_lotes(cc_muestra)
        cc_pepa = cc_pepa_lote(cc_muestra)
        cc_pepa_calibre = cc_pepa_calibres_lote(cc_muestra)
        cc_descuentos = descuentos_cat2_desechos(cc_pepa, muestra)
        cc_aporte_pex = aporte_pex(cc_descuentos, muestra)
        cc_porcentaje_liquidar = porcentaje_a_liquidar(cc_aporte_pex)
        cc_kilos_desc_merma = kilos_descontados_merma(cc_porcentaje_liquidar, muestra)
        cc_merma_por = merma_porcentual(cc_aporte_pex, cc_porcentaje_liquidar)
        cc_calculo_final = calculo_final(muestra, cc_merma_por, cc_descuentos, cc_kilos_desc_merma)
        
        
        promedio_cc_muestras = promedio_porcentaje_muestras(muestra)
        promedio_por_cc_pepa = promedio_porcentaje_cc_pepa(cc_pepa)
        promedio_cc_pepa_calibrada = promedio_porcentaje_calibres(cc_pepa_calibre)
        
        
        cc_muestra_serializado = MuestraSerializer(muestra, many=True).data
        cc_pepa_serializado = CCPepaMuestraSerializer(cc_pepa, many=True).data
        cc_pepa_calibre_serializado = CalibresSerializer(cc_pepa_calibre, many=True).data
        cc_descuentos_serializado = DescuentosSerializer(cc_descuentos, many=True).data
        cc_aportes_pex_serializado = AportePexSerializer(cc_aporte_pex, many=True).data
        cc_porcentaje_liquidar_serializado = PorcentajeLiquidarSerializer(cc_porcentaje_liquidar, many=True).data
        cc_kilos_desc_merma_serializado = KilosMermaSerializer(cc_kilos_desc_merma, many=True).data
        cc_merma_por_serializador = MermaPorcentajeSerializer(cc_merma_por, many=True).data
        cc_calculo_final = CalculoFinalSerializer(cc_calculo_final).data
        

        cc_promedio_porcentaje_muestra = PromedioMuestra(promedio_cc_muestras).data
        cc_promedio_porcentaje_cc_pepa = PromedioPepaMuestraSerializer(promedio_por_cc_pepa).data
        cc_promedio_porcentaje_cc_pepa_calibrada = PromedioCalibresSerializer(promedio_cc_pepa_calibrada).data
        

        return Response({   
            'cc_muestra': cc_muestra_serializado,
            'cc_pepa': cc_pepa_serializado,
            'cc_pepa_calibre': cc_pepa_calibre_serializado,
            'cc_descuentos': cc_descuentos_serializado,
            'cc_aportes_pex': cc_aportes_pex_serializado,
            'cc_porcentaje_liquidar': cc_porcentaje_liquidar_serializado,
            'cc_kilos_des_merma': cc_kilos_desc_merma_serializado,
            'cc_merma_porc': cc_merma_por_serializador,
            'cc_calculo_final': cc_calculo_final,
            'cc_promedio_porcentaje_muestras': cc_promedio_porcentaje_muestra,
            'cc_promedio_porcentaje_cc_pepa': cc_promedio_porcentaje_cc_pepa,
            'cc_promedio_porcentaje_cc_pepa_calibradas': cc_promedio_porcentaje_cc_pepa_calibrada,
            'numero_lote': numero_lote,
        })
        
        
    @action(detail=True, methods=['POST'])
    def subir_fotos_cc(self, request, pk=None):
        ccrecepcionmp = request.data.get('ccrecepcionmp')
        imagenes = request.FILES.getlist('imagen')

        if not ccrecepcionmp or not imagenes:
            return Response({'error': 'Falta ccrecepcionmp o imagen'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recepcionmp = CCRecepcionMateriaPrima.objects.get(pk=ccrecepcionmp)
        except CCRecepcionMateriaPrima.DoesNotExist:
            return Response({'error': 'CCRecepcionMateriaPrima no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                for imagen in imagenes:
                    FotosCC.objects.create(
                        ccrecepcionmp=recepcionmp,
                        imagen=imagen
                    )
            return Response({'message': 'Imágenes subidas correctamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CCRendimientoViewSet(viewsets.ModelViewSet):
    queryset = CCRendimiento.objects.all()
    serializer_class = CCRendimientoSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCRendimiento.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    def retrieve(self, request,cc_recepcionmp_pk=None , pk=None):
        ccrecep = get_object_or_404(CCRecepcionMateriaPrima, pk=cc_recepcionmp_pk)
        ccrendimiento = get_object_or_404(CCRendimiento, pk=pk, cc_recepcionmp=ccrecep)
        serializer = self.get_serializer(ccrendimiento)
        return Response(serializer.data)
    
    def list(self, request, cc_recepcionmp_pk=None):
        queryset = self.queryset.filter(cc_recepcionmp=cc_recepcionmp_pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CCPepaViewSet(viewsets.ModelViewSet):
    queryset = CCPepa.objects.all()
    serializer_class = CCPepaSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCPepa.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    

    def retrieve(self, request,cc_recepcionmp_pk=None,cc_rendimiento_pk=None, pk=None):
        ccrecep = get_object_or_404(CCRecepcionMateriaPrima, pk=cc_recepcionmp_pk)
        ccrendimiento = get_object_or_404(CCRendimiento, pk=cc_rendimiento_pk, cc_recepcionmp=ccrecep)
        ccpepa = get_object_or_404(CCPepa, pk=pk, ccrendimiento = ccrendimiento)
        serializer = self.get_serializer(ccpepa)
        return Response(serializer.data)            

class FotosCCRecepcionMateriaPrimaViewSet(viewsets.ModelViewSet):
    search_fields = ['ccrecepcionmp__id']
    filter_backends = (filters.SearchFilter, )
    queryset = FotosCC.objects.all()
    serializer_class = FotosCCRecepcionMateriaPrimaSerializer
    permission_classes = [IsAuthenticated,]
    


class CCTarjaResultanteViewSet(viewsets.ModelViewSet):
    lookup_field = 'tarja'
    queryset = CCTarjaResultante.objects.all()
    serializer_class = CCTarjaResultanteSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCTarjaResultante.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    @action(detail=False, methods=['GET'], url_path='todos_los_cdc_produccion/(?P<pk_produccion>[^/.]+)')
    def todos_los_cdc_produccion(self, request, pk_produccion=None):
        produccion = get_object_or_404(Produccion, pk=pk_produccion)
        ccrecep = get_list_or_404(CCTarjaResultante, tarja__produccion = produccion)
        serializer = self.get_serializer(ccrecep, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    
    
    @action(detail=False, methods=['GET'], url_path='rendimiento_tarja/(?P<pk_produccion>[^/.]+)')
    def rendimiento_tarja(self, request, pk_produccion=None):
        lotes_list = consulta_tarjasresultantes_en_produccion(pk_produccion)
        calibres = consulta_muestras_tarjasresultantes_cdc_calibres(lotes_list)
        consulta_kilos = consulta_kilos_tarjas_res(pk_produccion)
        #print("consulta kilo", consulta_kilos)
        
        cc_calibre_tarjas = CalibresResultadoSerializer(calibres).data
        
        return Response({
            'pepa_resultante': consulta_kilos,
            'cc_pepa_calibre': cc_calibre_tarjas,
        })
             
    

class CCTarjaResultanteReprocesoViewSet(viewsets.ModelViewSet):
    lookup_field = 'tarja'
    queryset = CCTarjaResultanteReproceso.objects.all()
    serializer_class = CCTarjaResultanteReprocesoSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = self.queryset.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset

    

class EstadoAprobacionJefaturaAPIView(generics.UpdateAPIView):
    lookup_field = 'id'
    queryset = CCRecepcionMateriaPrima.objects.all()
    serializer_class = EstadoAprobacionJefaturaSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCRecepcionMateriaPrima.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
class EstadoContraMuestraAPIView(generics.UpdateAPIView):
    lookup_field = 'id'
    queryset = CCRecepcionMateriaPrima.objects.all()
    serializer_class = EstadoContraMuestraSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCRecepcionMateriaPrima.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
        
        
class CCTarjaSeleccionadaViewSet(viewsets.ModelViewSet):
    lookup_field = 'tarja_seleccionada'
    queryset = CCTarjaSeleccionada.objects.all()
    serializer_class = CCTarjaSeleccionadaSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCTarjaSeleccionada.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
    
    
    
class CCBinResultanteViewSet(viewsets.ModelViewSet):
    lookup_field = 'bin_resultante'
    queryset = CCBinResultanteProgramaPH.objects.all()
    serializer_class = CCBinResultanteProgramaPHSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        user = self.request.user
        try:
            anio = PersonalizacionPerfil.objects.get(usuario= user).anio
            if anio == 'Todo':
                return self.queryset
            else:
                qs = CCBinResultanteProgramaPH.objects.filter(fecha_creacion__year = anio)
                return qs
        except:
            return self.queryset
        
class CCBinResultanteProcesoViewSet(viewsets.ModelViewSet):
    lookup_field = 'bin_resultante'
    queryset = CCBinResultanteProcesoPH.objects.all()
    serializer_class = CCBinResultanteProcesoPHSerializer
    permission_classes = [IsAuthenticated,]
    
    # def get_queryset(self):
    #     user = self.request.user
    #     try:
    #         anio = PersonalizacionPerfil.objects.get(usuario= user).anio
    #         if anio == 'Todo':
    #             return self.queryset
    #         else:
    #             qs = CCBinResultanteProcesoPH.objects.filter(fecha_creacion__year = anio)
    #             return qs
    #     except:
    #         return self.queryset
    
    