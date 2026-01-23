from rest_framework import serializers
from .mongo_models import Linea, Parada


class LineaSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    numero = serializers.IntegerField()
    nombre = serializers.CharField(max_length=100)
    color = serializers.CharField(max_length=50, required=False, allow_blank=True)
    descripcion = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        return Linea(**validated_data).save()

    def update(self, instance, validated_data):
        instance.numero = validated_data.get('numero', instance.numero)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.color = validated_data.get('color', instance.color)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.save()
        return instance


class ParadaSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(max_length=100)
    direccion = serializers.CharField(max_length=200)
    latitud = serializers.DecimalField(max_digits=10, decimal_places=8, required=False, allow_null=True)
    longitud = serializers.DecimalField(max_digits=11, decimal_places=8, required=False, allow_null=True)

    def create(self, validated_data):
        return Parada(**validated_data).save()

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.direccion = validated_data.get('direccion', instance.direccion)
        instance.latitud = validated_data.get('latitud', instance.latitud)
        instance.longitud = validated_data.get('longitud', instance.longitud)
        instance.save()
        return instance
