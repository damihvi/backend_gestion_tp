# Tests básicos para los modelos

from django.test import TestCase
from django.contrib.auth.models import User
from .models import *
from datetime import date, time
from decimal import Decimal


class LineaModelTest(TestCase):
    def setUp(self):
        self.linea = Linea.objects.create(
            numero=101,
            nombre='Centro - Norte',
            color='azul'
        )
    
    def test_linea_creation(self):
        self.assertEqual(self.linea.numero, 101)
        self.assertEqual(self.linea.nombre, 'Centro - Norte')
        self.assertEqual(str(self.linea), 'Línea 101 - Centro - Norte')


class ParadaModelTest(TestCase):
    def setUp(self):
        self.parada = Parada.objects.create(
            nombre='Terminal Central',
            direccion='Av. Principal 1000',
            latitud=Decimal('-34.6037'),
            longitud=Decimal('-58.3816')
        )
    
    def test_parada_creation(self):
        self.assertEqual(self.parada.nombre, 'Terminal Central')
        self.assertEqual(str(self.parada), 'Terminal Central')


class VehiculoModelTest(TestCase):
    def setUp(self):
        self.vehiculo = Vehiculo.objects.create(
            patente='ABC123',
            marca='Mercedes Benz',
            modelo='OF-1721',
            anio=2020,
            capacidad=45
        )
    
    def test_vehiculo_creation(self):
        self.assertEqual(self.vehiculo.patente, 'ABC123')
        self.assertEqual(self.vehiculo.capacidad, 45)


class ChoferModelTest(TestCase):
    def setUp(self):
        self.chofer = Chofer.objects.create(
            nombre='Juan',
            apellido='Pérez',
            dni='12345678',
            licencia='D1-123456',
            fecha_contratacion=date(2025, 1, 15)
        )
    
    def test_chofer_creation(self):
        self.assertEqual(self.chofer.nombre, 'Juan')
        self.assertEqual(str(self.chofer), 'Pérez, Juan')


class TarjetaModelTest(TestCase):
    def setUp(self):
        self.tarjeta = Tarjeta.objects.create(
            numero='1234567890123456',
            tipo='estudiante',
            saldo=Decimal('100.00')
        )
    
    def test_tarjeta_creation(self):
        self.assertEqual(self.tarjeta.tipo, 'estudiante')
        self.assertEqual(self.tarjeta.saldo, Decimal('100.00'))
        self.assertTrue(self.tarjeta.activa)
    
    def test_tarjeta_descuento(self):
        self.tarjeta.saldo -= Decimal('50.00')
        self.tarjeta.save()
        self.assertEqual(self.tarjeta.saldo, Decimal('50.00'))


class ViajeModelTest(TestCase):
    def setUp(self):
        linea = Linea.objects.create(numero=101, nombre='Test')
        self.ruta = Ruta.objects.create(linea=linea, nombre='Ruta Test')
        self.vehiculo = Vehiculo.objects.create(
            patente='TEST123',
            capacidad=40
        )
        self.chofer = Chofer.objects.create(
            nombre='Test',
            apellido='Chofer',
            dni='99999999',
            licencia='TEST',
            fecha_contratacion=date.today()
        )
        self.viaje = Viaje.objects.create(
            ruta=self.ruta,
            vehiculo=self.vehiculo,
            chofer=self.chofer,
            fecha=date.today(),
            estado='programado'
        )
    
    def test_viaje_creation(self):
        self.assertEqual(self.viaje.estado, 'programado')
        self.assertIsNotNone(self.viaje.ruta)
        self.assertIsNotNone(self.viaje.vehiculo)
        self.assertIsNotNone(self.viaje.chofer)
