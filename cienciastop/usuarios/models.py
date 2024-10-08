from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apaterno = models.CharField(max_length=100)
    amaterno = models.CharField(max_length=100)
    puntos = models.IntegerField()
    celular = models.CharField(max_length=15)
    correo = models.EmailField()
    contrasena = models.CharField(max_length=100)
    