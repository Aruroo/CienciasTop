from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=40)
    apellidos = models.CharField(max_length=40)
    #telefono = models.CharField(max_length=10)
    nocuenta = models.CharField(max_length=9)
    carrera = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"