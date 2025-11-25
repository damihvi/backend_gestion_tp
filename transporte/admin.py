from django.contrib import admin
from .models import (
    Linea, Parada, Ruta, RutaParada, Vehiculo, Chofer,
    Horario, Viaje, Tarjeta, Boleto, Mantenimiento, Incidente
)


@admin.register(Linea)
class LineaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nombre', 'color']
    search_fields = ['nombre', 'numero']
    list_filter = ['color']


@admin.register(Parada)
class ParadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'latitud', 'longitud']
    search_fields = ['nombre', 'direccion']


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'linea']
    search_fields = ['nombre']
    list_filter = ['linea']


@admin.register(RutaParada)
class RutaParadaAdmin(admin.ModelAdmin):
    list_display = ['ruta', 'parada', 'orden']
    list_filter = ['ruta']
    ordering = ['ruta', 'orden']


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['patente', 'marca', 'modelo', 'anio', 'capacidad']
    search_fields = ['patente', 'marca', 'modelo']
    list_filter = ['marca', 'anio']


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'dni', 'licencia', 'fecha_contratacion']
    search_fields = ['apellido', 'nombre', 'dni']
    list_filter = ['fecha_contratacion']


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['ruta', 'hora_salida', 'hora_llegada', 'dias_semana']
    list_filter = ['ruta', 'dias_semana']


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ['id', 'ruta', 'vehiculo', 'chofer', 'fecha', 'estado']
    search_fields = ['ruta__nombre', 'vehiculo__patente', 'chofer__apellido']
    list_filter = ['estado', 'fecha']
    date_hierarchy = 'fecha'


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo', 'saldo', 'fecha_emision', 'activa']
    search_fields = ['numero']
    list_filter = ['tipo', 'activa']


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ['id', 'viaje', 'tarjeta', 'monto', 'fecha_compra']
    search_fields = ['tarjeta__numero']
    list_filter = ['fecha_compra']
    date_hierarchy = 'fecha_compra'


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ['vehiculo', 'tipo', 'fecha', 'costo']
    search_fields = ['vehiculo__patente', 'descripcion']
    list_filter = ['tipo', 'fecha']
    date_hierarchy = 'fecha'


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ['id', 'viaje', 'gravedad', 'fecha', 'resuelto']
    search_fields = ['descripcion']
    list_filter = ['gravedad', 'resuelto', 'fecha']
    date_hierarchy = 'fecha'
