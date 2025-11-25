from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User

from .models import (
    Linea, Parada, Ruta, RutaParada, Vehiculo, Chofer,
    Horario, Viaje, Tarjeta, Boleto, Mantenimiento, Incidente
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    LineaSerializer, ParadaSerializer, RutaSerializer, RutaParadaSerializer,
    VehiculoSerializer, ChoferSerializer, HorarioSerializer, ViajeSerializer,
    TarjetaSerializer, BoletoSerializer, MantenimientoSerializer, IncidenteSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    Solo admins pueden crear, actualizar y eliminar usuarios.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['id', 'username', 'email']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Endpoint público para registrar nuevos usuarios"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Usuario creado exitosamente'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LineaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar líneas de transporte.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Linea.objects.all()
    serializer_class = LineaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['numero', 'color']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['numero', 'nombre']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ParadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar paradas.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Parada.objects.all()
    serializer_class = ParadaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'direccion']
    ordering_fields = ['nombre', 'direccion']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class RutaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar rutas.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Ruta.objects.select_related('linea').prefetch_related('paradas_orden__parada')
    serializer_class = RutaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['linea']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class RutaParadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar la relación ruta-parada.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = RutaParada.objects.select_related('ruta', 'parada')
    serializer_class = RutaParadaSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ruta', 'parada']
    ordering_fields = ['orden']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar vehículos.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['marca', 'modelo', 'anio']
    search_fields = ['patente', 'marca', 'modelo']
    ordering_fields = ['patente', 'marca', 'anio', 'capacidad']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'mantenimientos']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def mantenimientos(self, request, pk=None):
        """Obtener todos los mantenimientos de un vehículo"""
        vehiculo = self.get_object()
        mantenimientos = vehiculo.mantenimientos.all()
        serializer = MantenimientoSerializer(mantenimientos, many=True)
        return Response(serializer.data)


class ChoferViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar choferes.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Chofer.objects.all()
    serializer_class = ChoferSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'apellido', 'dni', 'licencia']
    ordering_fields = ['apellido', 'nombre', 'fecha_contratacion']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'viajes']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def viajes(self, request, pk=None):
        """Obtener todos los viajes de un chofer"""
        chofer = self.get_object()
        viajes = chofer.viajes.all()
        serializer = ViajeSerializer(viajes, many=True)
        return Response(serializer.data)


class HorarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar horarios.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Horario.objects.select_related('ruta__linea')
    serializer_class = HorarioSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ruta', 'dias_semana']
    search_fields = ['ruta__nombre']
    ordering_fields = ['hora_salida', 'hora_llegada']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ViajeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar viajes.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Viaje.objects.select_related('ruta', 'vehiculo', 'chofer')
    serializer_class = ViajeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ruta', 'vehiculo', 'chofer', 'estado', 'fecha']
    search_fields = ['ruta__nombre', 'vehiculo__patente', 'chofer__apellido']
    ordering_fields = ['fecha', 'hora_salida_real']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'boletos']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def boletos(self, request, pk=None):
        """Obtener todos los boletos de un viaje"""
        viaje = self.get_object()
        boletos = viaje.boletos.all()
        serializer = BoletoSerializer(boletos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def incidentes(self, request, pk=None):
        """Obtener todos los incidentes de un viaje"""
        viaje = self.get_object()
        incidentes = viaje.incidentes.all()
        serializer = IncidenteSerializer(incidentes, many=True)
        return Response(serializer.data)


class TarjetaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tarjetas.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Tarjeta.objects.all()
    serializer_class = TarjetaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'activa']
    search_fields = ['numero']
    ordering_fields = ['fecha_emision', 'saldo']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'boletos']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def recargar(self, request, pk=None):
        """Recargar saldo en una tarjeta"""
        from decimal import Decimal
        
        tarjeta = self.get_object()
        monto = request.data.get('monto')
        
        if not monto:
            return Response(
                {'error': 'Debe proporcionar un monto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            monto = Decimal(str(monto))
            if monto <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'El monto debe ser un número positivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tarjeta.saldo += monto
        tarjeta.save()
        
        serializer = self.get_serializer(tarjeta)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def boletos(self, request, pk=None):
        """Obtener todos los boletos de una tarjeta"""
        tarjeta = self.get_object()
        boletos = tarjeta.boletos.all()
        serializer = BoletoSerializer(boletos, many=True)
        return Response(serializer.data)


class BoletoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar boletos.
    GET: Público | POST/PUT/DELETE: Requiere autenticación
    """
    queryset = Boleto.objects.select_related('viaje', 'tarjeta', 'parada_subida')
    serializer_class = BoletoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['viaje', 'tarjeta', 'parada_subida']
    search_fields = ['tarjeta__numero']
    ordering_fields = ['fecha_compra', 'monto']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class MantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar mantenimientos.
    GET: Público | POST/PUT/DELETE: Solo Admin
    """
    queryset = Mantenimiento.objects.select_related('vehiculo')
    serializer_class = MantenimientoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehiculo', 'tipo', 'fecha']
    search_fields = ['vehiculo__patente', 'descripcion']
    ordering_fields = ['fecha', 'costo']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class IncidenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar incidentes.
    GET: Público | POST: Requiere autenticación | PUT/DELETE: Solo Admin
    """
    queryset = Incidente.objects.select_related('viaje')
    serializer_class = IncidenteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['viaje', 'gravedad', 'resuelto']
    search_fields = ['descripcion']
    ordering_fields = ['fecha', 'gravedad']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
