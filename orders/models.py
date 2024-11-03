# api/models.py
from django.core.exceptions import ValidationError
from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    edad = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class Restaurante(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    capacidad = models.PositiveIntegerField()
    clientes = models.ManyToManyField(Cliente, related_name='restaurantes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opening_time = models.TimeField(verbose_name="Hora de apertura")
    closing_time = models.TimeField(verbose_name="Hora de cierre")

    def clean(self):
        if self.opening_time >= self.closing_time:
            raise ValidationError("La hora de apertura debe ser anterior a la hora de cierre.")

    def __str__(self):
        return self.nombre


class Orden(models.Model):
    descripcion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=[('pending', 'Pendiente'), ('completed', 'Completada')],
                              default='pending')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)

    def __str__(self):
        return f"Orden de {self.cliente} en {self.restaurante}"
