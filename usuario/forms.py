from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from .models import Usuario

class UserRegistrationForm(forms.ModelForm):
    # Campos relacionados con el perfil del usuario (modelo Usuario)
    nombre = forms.CharField(label='Nombre', max_length=40)
    apellidopaterno = forms.CharField(label='Apellido paterno', max_length=40)
    apellidomaterno = forms.CharField(label='Apellido materno', max_length=40)
    celular = PhoneNumberField(label='Número de teléfono')
    nocuenta = forms.CharField(label='Número de Cuenta', max_length=9)

    AREA_CHOICES = [
        ('actuaria', 'Actuaría'),
        ('biologia', 'Biología'),
        ('computacion', 'Ciencias de la Computación'),
        ('tierra', 'Ciencias de la Tierra'),
        ('fisica', 'Física'),
        ('biomedica', 'Física Biomédica'),
        ('matematicas', 'Matemáticas'),
        ('aplicadas', 'Matemáticas Aplicadas'),
        ('trabajador', 'Trabajador'),
    ]
    
    area = forms.ChoiceField(label='Área', choices=AREA_CHOICES)
    
    # Campos del modelo User
    email = forms.EmailField(label='Correo Electrónico')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidopaterno', 'apellidomaterno', 'celular', 'nocuenta', 'area', 'email', 'password1', 'password2']

    def clean_password2(self):
        # Validación de las contraseñas
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return password2

    def save(self, commit=True):
        # Guardamos primero el usuario y luego el perfil
        user = User(
            username=self.cleaned_data['email'],  # Usar el email como username
            email=self.cleaned_data['email']
        )
        user.set_password(self.cleaned_data['password1'])  # Establecer la contraseña
        if commit:
            user.save()

        # Creamos el perfil de Usuario
        usuario = Usuario(
            user=user,
            nombre=self.cleaned_data['nombre'],
            apellidopaterno=self.cleaned_data['apellidopaterno'],
            apellidomaterno=self.cleaned_data['apellidomaterno'],
            celular=self.cleaned_data['celular'],
            nocuenta=self.cleaned_data['nocuenta'],
            area=self.cleaned_data['area'],
            email=self.cleaned_data['email'],
        )
        if commit:
            usuario.save()
        return user
