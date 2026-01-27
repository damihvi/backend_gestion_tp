from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Linea, Parada, Ruta, RutaParada, Vehiculo, Chofer, 
    Horario, Viaje, Tarjeta, Boleto, Mantenimiento, Incidente, UserProfile
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    is_conductor = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_conductor']
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        """Sobrescribir para obtener is_conductor del perfil"""
        data = super().to_representation(instance)
        # Obtener is_conductor de forma segura
        try:
            data['is_conductor'] = instance.profile.is_conductor if hasattr(instance, 'profile') else False
        except UserProfile.DoesNotExist:
            data['is_conductor'] = False
        return data
    
    def update(self, instance, validated_data):
        # Extraer is_conductor antes de actualizar el usuario
        is_conductor = validated_data.pop('is_conductor', None)
        
        # Actualizar usuario
        instance = super().update(instance, validated_data)
        
        # Actualizar perfil
        if is_conductor is not None:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            profile.is_conductor = is_conductor
            profile.save()
        
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirmar contraseña')
    is_conductor = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'is_conductor']
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        """Validar que el email no esté en uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value
    
    def validate_username(self, value):
        """Validar que el username no esté en uso"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        is_conductor = validated_data.pop('is_conductor', False)
        user = User.objects.create_user(**validated_data)
        # Configurar el perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_conductor = is_conductor
        profile.save()
        return user


class LineaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Linea"""
    total_rutas = serializers.SerializerMethodField()
    
    class Meta:
        model = Linea
        fields = ['id', 'numero', 'nombre', 'color', 'descripcion', 'total_rutas']
        read_only_fields = ['id']
    
    def get_total_rutas(self, obj):
        return obj.rutas.count()


class ParadaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Parada"""
    class Meta:
        model = Parada
        fields = ['id', 'nombre', 'direccion', 'latitud', 'longitud']
        read_only_fields = ['id']


class RutaParadaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo RutaParada"""
    parada_detalle = ParadaSerializer(source='parada', read_only=True)
    
    class Meta:
        model = RutaParada
        fields = ['id', 'ruta', 'parada', 'parada_detalle', 'orden']
        read_only_fields = ['id']


class RutaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Ruta"""
    linea_detalle = LineaSerializer(source='linea', read_only=True)
    paradas = RutaParadaSerializer(source='paradas_orden', many=True, read_only=True)
    linea_numero = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Ruta
        fields = ['id', 'linea', 'linea_numero', 'linea_detalle', 'nombre', 'descripcion', 'paradas']
        read_only_fields = ['id']
        extra_kwargs = {
            'linea': {'required': False}
        }
    
    def validate(self, attrs):
        # Require either linea or linea_numero
        if 'linea' not in attrs and 'linea_numero' not in attrs:
            raise serializers.ValidationError('Debe proporcionar linea o linea_numero')
        return attrs
    
    def create(self, validated_data):
        # Si se envía linea_numero, buscar la línea por número
        linea_numero = validated_data.pop('linea_numero', None)
        if linea_numero is not None:
            try:
                linea = Linea.objects.get(numero=linea_numero)
                validated_data['linea'] = linea
            except Linea.DoesNotExist:
                raise serializers.ValidationError({'linea_numero': f'No existe una línea con número {linea_numero}'})
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Si se envía linea_numero, buscar la línea por número
        linea_numero = validated_data.pop('linea_numero', None)
        if linea_numero is not None:
            try:
                linea = Linea.objects.get(numero=linea_numero)
                validated_data['linea'] = linea
            except Linea.DoesNotExist:
                raise serializers.ValidationError({'linea_numero': f'No existe una línea con número {linea_numero}'})
        return super().update(instance, validated_data)


class VehiculoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Vehiculo"""
    total_viajes = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehiculo
        fields = ['id', 'patente', 'marca', 'modelo', 'anio', 'capacidad', 'total_viajes']
        read_only_fields = ['id']
    
    def get_total_viajes(self, obj):
        return obj.viajes.count()


class ChoferSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Chofer"""
    nombre_completo = serializers.SerializerMethodField()
    total_viajes = serializers.SerializerMethodField()
    
    class Meta:
        model = Chofer
        fields = [
            'id', 'nombre', 'apellido', 'nombre_completo', 'dni', 
            'licencia', 'telefono', 'email', 'fecha_contratacion', 'total_viajes'
        ]
        read_only_fields = ['id']
    
    def get_nombre_completo(self, obj):
        return f"{obj.apellido}, {obj.nombre}"
    
    def get_total_viajes(self, obj):
        return obj.viajes.count()


class HorarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Horario"""
    ruta_detalle = RutaSerializer(source='ruta', read_only=True)
    
    class Meta:
        model = Horario
        fields = ['id', 'ruta', 'ruta_detalle', 'hora_salida', 'hora_llegada', 'dias_semana']
        read_only_fields = ['id']


class ViajeSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Viaje"""
    ruta_detalle = RutaSerializer(source='ruta', read_only=True)
    vehiculo_detalle = VehiculoSerializer(source='vehiculo', read_only=True)
    chofer_detalle = ChoferSerializer(source='chofer', read_only=True)
    total_boletos = serializers.SerializerMethodField()
    
    class Meta:
        model = Viaje
        fields = [
            'id', 'ruta', 'ruta_detalle', 'vehiculo', 'vehiculo_detalle',
            'chofer', 'chofer_detalle', 'fecha', 'hora_salida_real',
            'hora_llegada_real', 'estado', 'total_boletos'
        ]
        read_only_fields = ['id']
    
    def get_total_boletos(self, obj):
        return obj.boletos.count()


class TarjetaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Tarjeta"""
    total_boletos = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarjeta
        fields = ['id', 'usuario', 'numero', 'tipo', 'saldo', 'fecha_emision', 'fecha_expiracion', 'activa', 'total_boletos']
        read_only_fields = ['id', 'fecha_emision']
    
    def get_total_boletos(self, obj):
        return obj.boletos.count()


class BoletoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Boleto"""
    viaje_detalle = ViajeSerializer(source='viaje', read_only=True)
    tarjeta_detalle = TarjetaSerializer(source='tarjeta', read_only=True)
    parada_subida_detalle = ParadaSerializer(source='parada_subida', read_only=True)
    
    class Meta:
        model = Boleto
        fields = [
            'id', 'viaje', 'viaje_detalle', 'tarjeta', 'tarjeta_detalle',
            'monto', 'fecha_compra', 'parada_subida', 'parada_subida_detalle'
        ]
        read_only_fields = ['id', 'fecha_compra']
    
    def validate(self, attrs):
        """Validar que la tarjeta tenga saldo suficiente"""
        tarjeta = attrs.get('tarjeta')
        monto = attrs.get('monto')
        
        if tarjeta and tarjeta.saldo < monto:
            raise serializers.ValidationError({
                'tarjeta': 'Saldo insuficiente en la tarjeta.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Descontar el saldo de la tarjeta al crear el boleto"""
        tarjeta = validated_data.get('tarjeta')
        monto = validated_data.get('monto')
        
        if tarjeta:
            tarjeta.saldo -= monto
            tarjeta.save()
        
        return super().create(validated_data)


class MantenimientoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Mantenimiento"""
    vehiculo_detalle = VehiculoSerializer(source='vehiculo', read_only=True)
    
    class Meta:
        model = Mantenimiento
        fields = ['id', 'vehiculo', 'vehiculo_detalle', 'tipo', 'fecha', 'descripcion', 'costo']
        read_only_fields = ['id']


class IncidenteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Incidente"""
    viaje_detalle = ViajeSerializer(source='viaje', read_only=True)
    
    class Meta:
        model = Incidente
        fields = ['id', 'viaje', 'viaje_detalle', 'fecha', 'descripcion', 'gravedad', 'resuelto']
        read_only_fields = ['id', 'fecha']
