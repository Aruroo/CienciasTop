from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
class Producto(models.Model):
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
