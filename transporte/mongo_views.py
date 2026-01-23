from rest_framework import viewsets, status
from rest_framework.response import Response
from .mongo_models import Linea, Parada
from .mongo_serializers import LineaSerializer, ParadaSerializer


class LineaViewSet(viewsets.ViewSet):
    def list(self, request):
        lineas = Linea.objects.all()
        serializer = LineaSerializer(lineas, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = LineaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            linea = Linea.objects.get(id=pk)
            serializer = LineaSerializer(linea)
            return Response(serializer.data)
        except Linea.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            linea = Linea.objects.get(id=pk)
            serializer = LineaSerializer(linea, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Linea.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            linea = Linea.objects.get(id=pk)
            linea.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Linea.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ParadaViewSet(viewsets.ViewSet):
    def list(self, request):
        paradas = Parada.objects.all()
        serializer = ParadaSerializer(paradas, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ParadaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            parada = Parada.objects.get(id=pk)
            serializer = ParadaSerializer(parada)
            return Response(serializer.data)
        except Parada.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            parada = Parada.objects.get(id=pk)
            serializer = ParadaSerializer(parada, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Parada.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            parada = Parada.objects.get(id=pk)
            parada.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Parada.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
