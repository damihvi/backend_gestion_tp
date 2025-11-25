from django.db import models
from django.contrib.auth.models import User


class Linea(models.Model):
    """Modelo para las líneas de transporte"""
    numero = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'lineas'
        verbose_name = 'Línea'
        verbose_name_plural = 'Líneas'
        ordering = ['numero']
    
    def __str__(self):
        return f"Línea {self.numero} - {self.nombre}"


class Parada(models.Model):
    """Modelo para las paradas de transporte"""
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    class Meta:
        db_table = 'paradas'
        verbose_name = 'Parada'
        verbose_name_plural = 'Paradas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Ruta(models.Model):
    """Modelo para las rutas"""
    linea = models.ForeignKey(Linea, on_delete=models.CASCADE, related_name='rutas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'rutas'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'
    
    def __str__(self):
        return f"{self.nombre} - Línea {self.linea.numero}"


class RutaParada(models.Model):
    """Modelo intermedio para relacionar rutas y paradas con orden"""
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='paradas_orden')
    parada = models.ForeignKey(Parada, on_delete=models.CASCADE, related_name='rutas_orden')
    orden = models.IntegerField()
    
    class Meta:
        db_table = 'ruta_paradas'
        verbose_name = 'Ruta-Parada'
        verbose_name_plural = 'Ruta-Paradas'
        unique_together = [['ruta', 'parada']]
        ordering = ['ruta', 'orden']
    
    def __str__(self):
        return f"{self.ruta} - Parada {self.orden}: {self.parada}"


class Vehiculo(models.Model):
    """Modelo para los vehículos"""
    patente = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    capacidad = models.IntegerField()
    
    class Meta:
        db_table = 'vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['patente']
    
    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"


class Chofer(models.Model):
    """Modelo para los choferes"""
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    licencia = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_contratacion = models.DateField()
    
    class Meta:
        db_table = 'choferes'
        verbose_name = 'Chofer'
        verbose_name_plural = 'Choferes'
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Horario(models.Model):
    """Modelo para los horarios"""
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='horarios')
    hora_salida = models.TimeField()
    hora_llegada = models.TimeField()
    dias_semana = models.CharField(max_length=50)  # L,M,X,J,V,S,D
    
    class Meta:
        db_table = 'horarios'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['ruta', 'hora_salida']
    
    def __str__(self):
        return f"{self.ruta} - {self.hora_salida} a {self.hora_llegada}"


class Viaje(models.Model):
    """Modelo para los viajes"""
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='viajes')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='viajes')
    chofer = models.ForeignKey(Chofer, on_delete=models.CASCADE, related_name='viajes')
    fecha = models.DateField()
    hora_salida_real = models.TimeField(blank=True, null=True)
    hora_llegada_real = models.TimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')
    
    class Meta:
        db_table = 'viajes'
        verbose_name = 'Viaje'
        verbose_name_plural = 'Viajes'
        ordering = ['-fecha', '-hora_salida_real']
    
    def __str__(self):
        return f"Viaje {self.id} - {self.ruta} - {self.fecha}"


class Tarjeta(models.Model):
    """Modelo para las tarjetas de pago"""
    TIPO_CHOICES = [
        ('normal', 'Normal'),
        ('estudiante', 'Estudiante'),
        ('jubilado', 'Jubilado'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_emision = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tarjetas'
        verbose_name = 'Tarjeta'
        verbose_name_plural = 'Tarjetas'
        ordering = ['numero']
    
    def __str__(self):
        return f"Tarjeta {self.numero} - {self.tipo}"


class Boleto(models.Model):
    """Modelo para los boletos"""
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='boletos')
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE, related_name='boletos', blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    parada_subida = models.ForeignKey(
        Parada, 
        on_delete=models.SET_NULL, 
        related_name='boletos_subida',
        blank=True, 
        null=True
    )
    
    class Meta:
        db_table = 'boletos'
        verbose_name = 'Boleto'
        verbose_name_plural = 'Boletos'
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f"Boleto {self.id} - ${self.monto}"


class Mantenimiento(models.Model):
    """Modelo para el mantenimiento de vehículos"""
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]
    
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='mantenimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField()
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        db_table = 'mantenimientos'
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.vehiculo} - {self.tipo} - {self.fecha}"


class Incidente(models.Model):
    """Modelo para los incidentes"""
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='incidentes', blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    gravedad = models.CharField(max_length=20, choices=[
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ])
    resuelto = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'incidentes'
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Incidente {self.id} - {self.gravedad} - {self.fecha.strftime('%d/%m/%Y')}"
