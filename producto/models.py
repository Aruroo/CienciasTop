from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Producto(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='productos')
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    costo = models.IntegerField()
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos_imagenes')
    categoria = models.TextField()
    dias = models.IntegerField(
        validators=[
            MinValueValidator(3),
            MaxValueValidator(7)
        ]
    )

    def __str__(self):
        return self.nombre + ' - ' + str(self.costo)
    
class Renta(models.Model):
    id = models.AutoField(primary_key=True)
    id_libro = models.ForeignKey(Producto,on_delete=models.CASCADE, verbose_name='Titulo')
    id_deudor = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='ID_deudor')
    fecha_prestamo = models.DateField()
