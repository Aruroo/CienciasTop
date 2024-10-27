from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=40)
    apellidopaterno = models.CharField(max_length=40)
    apellidomaterno = models.CharField(max_length=40)
    puntos = models.IntegerField(default=100)
    celular = PhoneNumberField()
    nocuenta = models.CharField(max_length=9)
    area = models.CharField(max_length=100, default='trabajador')
    email = models.EmailField()
    oculto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellidopaterno} {self.apellidomaterno}"