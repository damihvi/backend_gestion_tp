from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Linea, Parada, Ruta, RutaParada, Vehiculo, Chofer, 
    Horario, Viaje, Tarjeta, Boleto, Mantenimiento, Incidente, UserProfile
)


class FlexibleDateField(serializers.DateField):
    """Permite recibir '' y lo convierte a None antes de validar la fecha."""

    def to_internal_value(self, value):
        if value in ('', None):
            return None
        return super().to_internal_value(value)


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    is_asistente = serializers.BooleanField(required=False, default=False)
    is_chofer = serializers.BooleanField(required=False, default=False)
    chofer_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Campos del Chofer asociado
    chofer_dni = serializers.CharField(required=False, allow_blank=True)
    chofer_licencia = serializers.CharField(required=False, allow_blank=True)
    chofer_telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    chofer_fecha_contratacion = FlexibleDateField(required=False, allow_null=True, default=None)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 
                  'is_asistente', 'is_chofer', 'chofer_id', 'chofer_dni', 'chofer_licencia', 
                  'chofer_telefono', 'chofer_fecha_contratacion']
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        """Sobrescribir para obtener is_asistente, is_chofer, chofer_id y datos del chofer"""
        data = super().to_representation(instance)
        # Obtener datos del perfil de forma segura
        try:
            profile = instance.profile
            data['is_asistente'] = profile.is_asistente
            data['is_chofer'] = profile.is_chofer
            data['chofer_id'] = profile.chofer_id if profile.chofer else None
            
            # Si tiene un chofer asociado, incluir sus datos
            if profile.chofer:
                chofer = profile.chofer
                data['chofer_dni'] = chofer.dni
                data['chofer_licencia'] = chofer.licencia
                data['chofer_telefono'] = chofer.telefono
                data['chofer_fecha_contratacion'] = chofer.fecha_contratacion
            else:
                data['chofer_dni'] = ''
                data['chofer_licencia'] = ''
                data['chofer_telefono'] = ''
                data['chofer_fecha_contratacion'] = None
        except (UserProfile.DoesNotExist, AttributeError):
            data['is_asistente'] = False
            data['is_chofer'] = False
            data['chofer_id'] = None
            data['chofer_dni'] = ''
            data['chofer_licencia'] = ''
            data['chofer_telefono'] = ''
            data['chofer_fecha_contratacion'] = None
        return data
    
    def update(self, instance, validated_data):
        # Extraer campos del perfil y del chofer
        is_asistente = validated_data.pop('is_asistente', None)
        is_chofer = validated_data.pop('is_chofer', None)
        chofer_id = validated_data.pop('chofer_id', None)
        chofer_dni = validated_data.pop('chofer_dni', None)
        chofer_licencia = validated_data.pop('chofer_licencia', None)
        chofer_telefono = validated_data.pop('chofer_telefono', None)
        chofer_fecha_contratacion = validated_data.pop('chofer_fecha_contratacion', None)
        
        # Actualizar usuario
        instance = super().update(instance, validated_data)
        
        # Actualizar perfil
        profile, created = UserProfile.objects.get_or_create(user=instance)
        
        if is_asistente is not None:
            profile.is_asistente = is_asistente
        
        if is_chofer is not None:
            profile.is_chofer = is_chofer
            
            # Si se marca como chofer, crear automáticamente el registro de Chofer
            if is_chofer and not profile.chofer:
                from .models import Chofer
                from datetime import date
                chofer = Chofer.objects.create(
                    nombre=instance.first_name or instance.username,
                    apellido=instance.last_name or '',
                    dni=chofer_dni or '',
                    licencia=chofer_licencia or '',
                    telefono=chofer_telefono or '',
                    email=instance.email,
                    fecha_contratacion=chofer_fecha_contratacion or date.today()
                )
                profile.chofer = chofer
        
        # Actualizar datos del chofer si existe
        if profile.chofer:
            chofer_actualizado = False
            if chofer_dni is not None:
                profile.chofer.dni = chofer_dni
                chofer_actualizado = True
            if chofer_licencia is not None:
                profile.chofer.licencia = chofer_licencia
                chofer_actualizado = True
            if chofer_telefono is not None:
                profile.chofer.telefono = chofer_telefono
                chofer_actualizado = True
            if chofer_fecha_contratacion is not None:
                profile.chofer.fecha_contratacion = chofer_fecha_contratacion
                chofer_actualizado = True
            
            # Actualizar nombre y email del chofer con los datos del usuario
            if instance.first_name:
                profile.chofer.nombre = instance.first_name
                chofer_actualizado = True
            if instance.last_name:
                profile.chofer.apellido = instance.last_name
                chofer_actualizado = True
            if instance.email:
                profile.chofer.email = instance.email
                chofer_actualizado = True
            
            if chofer_actualizado:
                profile.chofer.save()
        
        # Actualizar chofer_id (permitir asignar None para desconectar)
        if chofer_id is not None:
            profile.chofer_id = chofer_id
        elif 'chofer_id' in self.initial_data:
            # Si explícitamente se envió None, desconectar
            profile.chofer_id = None
            
        profile.save()
        
        return instance

    def validate(self, attrs):
        # Normalizar fecha de contratación cuando llega como cadena vacía
        fecha_raw = self.initial_data.get('chofer_fecha_contratacion') if hasattr(self, 'initial_data') else None
        if fecha_raw == '':
            attrs['chofer_fecha_contratacion'] = None
        return super().validate(attrs)
    
    def create(self, validated_data):
        # Extraer campos que no pertenecen al modelo User
        is_asistente = validated_data.pop('is_asistente', False)
        is_chofer = validated_data.pop('is_chofer', False)
        chofer_id = validated_data.pop('chofer_id', None)
        chofer_dni = validated_data.pop('chofer_dni', None)
        chofer_licencia = validated_data.pop('chofer_licencia', None)
        chofer_telefono = validated_data.pop('chofer_telefono', None)
        chofer_fecha_contratacion = validated_data.pop('chofer_fecha_contratacion', None)

        # Limpiar fecha vacía
        if chofer_fecha_contratacion == '':
            chofer_fecha_contratacion = None
        
        # Crear usuario con password por defecto si no se proporciona
        password = validated_data.pop('password', None)
        if password:
            user = User.objects.create_user(**validated_data, password=password)
        else:
            # Password por defecto para creación administrativa
            username = validated_data.get('username', 'user')
            user = User.objects.create_user(**validated_data, password=f'{username}123')
        
        # Crear o actualizar perfil
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'is_asistente': is_asistente,
                'is_chofer': is_chofer
            }
        )
        if not created:
            profile.is_asistente = is_asistente
            profile.is_chofer = is_chofer
        
        # Si es chofer, crear automáticamente el registro de Chofer
        if is_chofer:
            from .models import Chofer
            from datetime import date
            chofer = Chofer.objects.create(
                nombre=user.first_name or user.username,
                apellido=user.last_name or '',
                dni=chofer_dni or '',
                licencia=chofer_licencia or '',
                telefono=chofer_telefono or '',
                email=user.email,
                fecha_contratacion=chofer_fecha_contratacion or date.today()
            )
            profile.chofer = chofer
        
        # Guardar perfil siempre
        profile.save()
        
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirmar contraseña')
    is_asistente = serializers.BooleanField(required=False, default=False)
    is_chofer = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'is_asistente', 'is_chofer']
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
        is_asistente = validated_data.pop('is_asistente', False)
        is_chofer = validated_data.pop('is_chofer', False)
        user = User.objects.create_user(**validated_data)
        # Configurar el perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_asistente = is_asistente
        profile.is_chofer = is_chofer
        
        # Si es chofer, crear automáticamente el registro de Chofer
        if is_chofer:
            from .models import Chofer
            from datetime import date
            chofer = Chofer.objects.create(
                nombre=user.first_name or user.username,
                apellido=user.last_name or '',
                dni='',  # Se deberá actualizar después
                licencia='',  # Se deberá actualizar después
                email=user.email,
                fecha_contratacion=date.today()
            )
            profile.chofer = chofer
        
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
    linea_detalle = LineaSerializer(source='linea', read_only=True)
    linea_numero = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Vehiculo
        fields = ['id', 'patente', 'marca', 'modelo', 'anio', 'capacidad', 'linea', 'linea_numero', 'linea_detalle', 'total_viajes']
        read_only_fields = ['id', 'linea_detalle']
    
    def get_total_viajes(self, obj):
        return obj.viajes.count()

    def _resolve_linea(self, validated_data):
        """Permite asignar la línea ya sea por ID o por número."""
        linea_numero = validated_data.pop('linea_numero', None)

        # Permitir linea_numero como cadena numérica
        if isinstance(linea_numero, str) and linea_numero.isdigit():
            linea_numero = int(linea_numero)

        if linea_numero is not None:
            try:
                validated_data['linea'] = Linea.objects.get(numero=linea_numero)
            except Linea.DoesNotExist:
                raise serializers.ValidationError({'linea_numero': f'No existe una línea con número {linea_numero}'})

        # Permitir linea (pk) enviada como cadena numérica
        linea_val = validated_data.get('linea')
        if isinstance(linea_val, str) and linea_val.isdigit():
            validated_data['linea'] = int(linea_val)

        # Normalizar linea vacía enviada como cadena
        if validated_data.get('linea') == '':
            validated_data['linea'] = None
        return validated_data

    def create(self, validated_data):
        validated_data = self._resolve_linea(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._resolve_linea(validated_data)
        return super().update(instance, validated_data)


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
