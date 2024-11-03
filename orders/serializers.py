# api/serializers.py
import pytz
from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import Cliente, Restaurante, Orden
from django.utils import timezone


# class CustomSerializer(serializers.ModelSerializer):
#     def is_valid(self, raise_exception=False):
#         valid = super().is_valid(raise_exception=False)
#         if not valid:
#             errors = self.errors
#             if 'non_field_errors' in errors:
#                 self._errors = {'errores': ' '.join(errors['non_field_errors'])}
#             elif errors:
#                 self._errors = {
#                     'errores': ' '.join([f"{field}: {'. '.join(error)}" for field, error in errors.items()])}
#         return valid


class AgregarClienteRestauranteSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()

    def validate_cliente_id(self, value):
        try:
            Cliente.objects.get(pk=value)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("El cliente especificado no existe.")
        return value

    def validate(self, data):
        restaurante = self.context['restaurante']
        cliente = Cliente.objects.get(pk=data['cliente_id'])

        if cliente in restaurante.clientes.all():
            raise serializers.ValidationError("Este cliente ya está asociado con este restaurante.")

        if restaurante.clientes.count() >= restaurante.capacidad:
            raise serializers.ValidationError("El restaurante ha alcanzado su capacidad máxima.")

        return data


class EliminarClienteRestauranteSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()

    def validate_cliente_id(self, value):
        try:
            Cliente.objects.get(pk=value)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("El cliente especificado no existe.")
        return value

    def validate(self, data):
        restaurante = self.context['restaurante']
        cliente = Cliente.objects.get(pk=data['cliente_id'])

        if cliente not in restaurante.clientes.all():
            raise serializers.ValidationError("Este cliente no está asociado con este restaurante.")

        return data


class ClienteSerializer(serializers.ModelSerializer):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número de teléfono debe estar en el formato: '+999999999'. Hasta 15 dígitos permitidos."
    )
    telefono = serializers.CharField(validators=[phone_regex], max_length=17)

    class Meta:
        model = Cliente
        fields = '__all__'
        extra_kwargs = {
            'nombre': {'help_text': 'Nombre completo del cliente'},
            'email': {'help_text': 'Correo electrónico del cliente, debe ser único'},
            'telefono': {'help_text': 'Número de teléfono del cliente'},
            'edad': {'help_text': 'Edad del cliente (debe ser 18 o más)'},
        }

    def validate_email(self, value):
        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']:
            # Estamos en una operación de actualización
            if Cliente.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("Ya existe otro cliente con este email.")
        else:
            # Estamos en una operación de creación
            if Cliente.objects.filter(email=value).exists():
                raise serializers.ValidationError("Ya existe un cliente con este email.")
        return value

    def validate_edad(self, value):
        if value < 18:
            raise serializers.ValidationError("El cliente debe ser mayor de 18 años.")
        return value


class RestauranteSerializer(serializers.ModelSerializer):
    clientes = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), many=True, required=False)

    class Meta:
        model = Restaurante
        fields = '__all__'
        extra_kwargs = {
            'nombre': {'help_text': 'Nombre del restaurante'},
            'direccion': {'help_text': 'Dirección del restaurante'},
            'capacidad': {'help_text': 'Capacidad máxima del restaurante'},
            'clientes': {'help_text': 'Clientes asociados al restaurante'},
            'opening_time': {'help_text': 'Hora de apertura del restaurante'},
            'closing_time': {'help_text': 'Hora de cierre del restaurante'},
        }

    def validate_capacidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La capacidad debe ser un número positivo.")
        return value

    def validate(self, data):
        if 'clientes' in data and len(data['clientes']) > data['capacidad']:
            raise serializers.ValidationError("El número de clientes no puede exceder la capacidad del restaurante.")
        if data['opening_time'] >= data['closing_time']:
            raise serializers.ValidationError("La hora de apertura debe ser anterior a la hora de cierre.")
        return data


class OrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = '__all__'
        extra_kwargs = {
            'descripcion': {'help_text': 'Descripción de la orden'},
            'cliente': {'help_text': 'ID del cliente que realiza la orden'},
            'restaurante': {'help_text': 'ID del restaurante donde se realiza la orden'},
        }

    def validate(self, data):
        if data['cliente'] not in data['restaurante'].clientes.all():
            raise serializers.ValidationError("El cliente no está asociado con este restaurante.")

        # Verificar si el restaurante está abierto (asumiendo que tienes un campo para horario de apertura)
        # Obtener la hora actual en UTC
        current_time = timezone.now()
        # Convertir a la zona horaria de Cuba
        cuba_tz = pytz.timezone('America/Havana')
        cuba_time = current_time.astimezone(cuba_tz)
        current_hour = cuba_time.time()
        print(current_hour, 'Hora actual')
        print(data['restaurante'].opening_time, 'Hora apertura')
        print(data['restaurante'].closing_time, 'Hora cierre')

        if current_hour < data['restaurante'].opening_time or current_hour > data['restaurante'].closing_time:
            raise serializers.ValidationError("El restaurante está cerrado en este momento.")

        # Verificar si el cliente ya tiene una orden pendiente
        if Orden.objects.filter(cliente=data['cliente'], restaurante=data['restaurante'], estado='pending').exists():
            raise serializers.ValidationError("El cliente ya tiene una orden pendiente.")
        return data
