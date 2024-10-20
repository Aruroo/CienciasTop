from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    nombre = forms.CharField(label='Nombre', max_length=40)
    costo = forms.IntegerField(label='Costo')
    descripcion = forms.CharField(
        label='Descripción', 
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        max_length=400
    )
    imagen = forms.ImageField(label='Imagen')

    CATEGORIA_CHOICES = (
        ('computadoras', 'Computadoras'),
        ('tabletas', 'Tabletas'),
        ('audifonos', 'Audifonos'),
        ('peliculas', 'Peliculas'),
        ('series', 'Series'),
        ('cds', 'CDs'),
        ('balones', 'Balones'),
        ('raquetas', 'Raquetas'),
        ('juegos', 'Juegos de mesa'),
        ('otros', 'Otros')
    )
    categoria = forms.ChoiceField(label='Categoría', choices=CATEGORIA_CHOICES)
    dias = forms.IntegerField(label='Días')

    class Meta:
        model = Producto
        fields = ['nombre', 'costo', 'descripcion', 'imagen', 'categoria', 'dias']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    # Validación personalizada para el campo 'dias' que van de 3 a 7
    def clean_dias(self):
        dias = self.cleaned_data.get('dias')
        if dias < 3 or dias > 7:
            raise forms.ValidationError("Los días de préstamo deben ser de entre 3 y 7.")
        return dias
    
    def clean_costo(self):
        costo = self.cleaned_data.get('costo')
        if costo < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return costo



class EditarProductoForm(forms.ModelForm):
    CATEGORIA_CHOICES = (
        ('computadoras', 'Computadoras'),
        ('tabletas', 'Tabletas'),
        ('audifonos', 'Audifonos'),
        ('peliculas', 'Peliculas'),
        ('series', 'Series'),
        ('cds', 'CDs'),
        ('balones', 'Balones'),
        ('raquetas', 'Raquetas'),
        ('juegos', 'Juegos de mesa'),
        ('otros', 'Otros')
    )
    categoria = forms.ChoiceField(label='Categoría', choices=CATEGORIA_CHOICES)
    class Meta:
        model = Producto
        fields = ['nombre', 'costo', 'descripcion', 'categoria', 'dias']
    
    def clean_dias(self):
        dias = self.cleaned_data.get('dias')
        if dias < 3 or dias > 7:
            raise forms.ValidationError("Los días de préstamo deben ser de entre 3 y 7.")
        return dias

    def clean_costo(self):
        costo = self.cleaned_data.get('costo')
        if costo < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return costo