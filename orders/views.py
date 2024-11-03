# api/views.py
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cliente, Restaurante, Orden
from .serializers import ClienteSerializer, RestauranteSerializer, OrdenSerializer, AgregarClienteRestauranteSerializer, \
    EliminarClienteRestauranteSerializer
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    # @swagger_auto_schema(
    #     operation_description="Crear un nuevo cliente",
    #     request_body=ClienteSerializer,
    #     responses={
    #         201: openapi.Response('Cliente creado', ClienteSerializer),
    #         400: openapi.Response(
    #             'Error de validación',
    #             examples={
    #                 'application/json': {
    #                     "detail": "El campo 'edad' es obligatorio."
    #                 }
    #             }
    #         )
    #     }
    # )
    # def create(self, request, *args, **kwargs):
    #     edad = request.data.get('edad')
    #
    #     # Verificar si la edad está presente
    #     if edad is None:
    #         raise ValidationError({"detail": "El campo 'edad' es obligatorio."})
    #
    #     # Intentar convertir la edad a un entero
    #     try:
    #         edad = int(edad)
    #     except ValueError:
    #         raise ValidationError({"detail": "La edad debe ser un número entero."})
    #
    #     # Validar que la edad sea 18 o más
    #     if edad < 18:
    #         raise ValidationError({
    #             "detail": "El cliente debe ser un adulto (18 años o más).",
    #             "edad_proporcionada": edad,
    #             "requisito": "Edad mínima de 18 años."
    #         })
    #
    #     return super().create(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Obtener lista de clientes",
    #     responses={200: ClienteSerializer(many=True)}
    # )
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)
    #
    # @swagger_auto_schema(
    #     operation_description="Actualizar un cliente existente",
    #     request_body=ClienteSerializer,
    #     responses={
    #         200: openapi.Response('Cliente actualizado', ClienteSerializer),
    #         400: 'Error de validación',
    #         404: 'Cliente no encontrado'
    #     }
    # )
    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)
    #
    # @swagger_auto_schema(
    #     operation_description="Eliminar un cliente existente",
    #     responses={
    #         204: 'Cliente eliminado',
    #         404: 'Cliente no encontrado'
    #     }
    # )
    # def destroy(self, request, *args, **kwargs):
    #     return super().destroy(request, *args, **kwargs)


class RestauranteViewSet(viewsets.ModelViewSet):
    queryset = Restaurante.objects.all()
    serializer_class = RestauranteSerializer

    @swagger_auto_schema(
        method='post',
        request_body=AgregarClienteRestauranteSerializer,
        responses={
            200: openapi.Response('Cliente agregado exitosamente', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'clientes_actuales': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'capacidad_restante': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )),
            400: 'Error en la solicitud'
        },
        operation_description="Agrega un cliente a un restaurante específico, recibe desde el body: { 'cliente_id': "
                              "*id_del_cliente* }."
    )
    @action(detail=True, methods=['post'])
    def agregar_cliente(self, request, pk=None):
        restaurante = self.get_object()
        serializer = AgregarClienteRestauranteSerializer(data=request.data, context={'restaurante': restaurante})

        if serializer.is_valid():
            cliente = Cliente.objects.get(pk=serializer.validated_data['cliente_id'])
            restaurante.clientes.add(cliente)
            return Response({"message": f"Cliente {cliente.nombre} agregado al restaurante {restaurante.nombre}"},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        request_body=EliminarClienteRestauranteSerializer,
        responses={
            200: openapi.Response('Cliente eliminado exitosamente', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'clientes_actuales': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'capacidad_restante': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )),
            400: 'Error en la solicitud'
        },
        operation_description="Elimina un cliente de un restaurante específico, recibe desde el body: { 'cliente_id': "
                              "*id_del_cliente* }."
    )
    @action(detail=True, methods=['post'])
    def eliminar_cliente(self, request, pk=None):
        restaurante = self.get_object()
        serializer = EliminarClienteRestauranteSerializer(data=request.data, context={'restaurante': restaurante})

        if serializer.is_valid():
            cliente = Cliente.objects.get(pk=serializer.validated_data['cliente_id'])
            restaurante.clientes.remove(cliente)
            clientes_actuales = restaurante.clientes.count()
            capacidad_restante = restaurante.capacidad - clientes_actuales
            return Response({
                "message": f"Cliente {cliente.nombre} eliminado del restaurante {restaurante.nombre}",
                "clientes_actuales": clientes_actuales,
                "capacidad_restante": capacidad_restante
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(operation_description="Crear un nuevo restaurante")
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # Verificar la cantidad de clientes
    #     clientes_ids = request.data.get('clientes', [])
    #     capacidad = serializer.validated_data.get('capacidad', 0)
    #
    #     print(clientes_ids, capacidad, 'DATOS AKI')
    #
    #     if len(clientes_ids) > capacidad:
    #         return Response(
    #             {"error": "La cantidad de clientes no puede exceder la capacidad del restaurante."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     # Si la validación pasa, se guarda el restaurante
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    # @swagger_auto_schema(operation_description="Actualizar un restaurante")
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # Verificar la cantidad de clientes al actualizar
    #     clientes_ids = request.data.get('clientes', [])
    #     capacidad = serializer.validated_data.get('capacidad', 0)
    #
    #     if len(clientes_ids) > capacidad:
    #         return Response(
    #             {"error": "La cantidad de clientes no puede exceder la capacidad del restaurante."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     self.perform_update(serializer)
    #     return Response(serializer.data)


class OrdenViewSet(viewsets.ModelViewSet):
    queryset = Orden.objects.all()
    serializer_class = OrdenSerializer

    # def perform_create(self, serializer):
    #     cliente = serializer.validated_data['cliente']
    #     restaurante = serializer.validated_data['restaurante']
    #
    #     if cliente.edad < 18:
    #         raise ValidationError("El cliente debe ser un adulto (18 años o más).")
    #
    #     serializer.save()
