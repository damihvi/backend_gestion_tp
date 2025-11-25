from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, LineaViewSet, ParadaViewSet, RutaViewSet, RutaParadaViewSet,
    VehiculoViewSet, ChoferViewSet, HorarioViewSet, ViajeViewSet,
    TarjetaViewSet, BoletoViewSet, MantenimientoViewSet, IncidenteViewSet
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuario')
router.register(r'lineas', LineaViewSet, basename='linea')
router.register(r'paradas', ParadaViewSet, basename='parada')
router.register(r'rutas', RutaViewSet, basename='ruta')
router.register(r'ruta-paradas', RutaParadaViewSet, basename='ruta-parada')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'choferes', ChoferViewSet, basename='chofer')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'viajes', ViajeViewSet, basename='viaje')
router.register(r'tarjetas', TarjetaViewSet, basename='tarjeta')
router.register(r'boletos', BoletoViewSet, basename='boleto')
router.register(r'mantenimientos', MantenimientoViewSet, basename='mantenimiento')
router.register(r'incidentes', IncidenteViewSet, basename='incidente')

urlpatterns = [
    path('', include(router.urls)),
]
