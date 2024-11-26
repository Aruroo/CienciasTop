from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from .models import Usuario, Acumulacion
import re

class UserRegistrationForm(forms.ModelForm):
    # Campos relacionados con el perfil del usuario (modelo Usuario)

    USER_CHOICES = [
        ('administrador', 'Administrador'),
        ('proveedor', 'Proveedor'),
        ('usuario', 'Usuario'),
    ]
    
    tipousuario = forms.ChoiceField(label='Tipo de Usuario', choices=USER_CHOICES)
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
    
    area = forms.ChoiceField(label='Área', choices=AREA_CHOICES, required=False)
    
    # Campos del modelo User
    email = forms.EmailField(label='Correo Electrónico')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput)
    
    # Orden de los campos
    field_order = ['tipousuario', 'area', 'nombre', 'apellidopaterno', 'apellidomaterno', 
                   'celular', 'nocuenta', 'email', 'password1', 'password2']
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidopaterno', 'apellidomaterno', 'celular', 'nocuenta', 'area', 'email', 'password1', 'password2']

    # se agrega el método clean_email para validar que sea un correo de la institucion
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validar que el correo contenga la palabra "institucional"
        #if "institucional" not in email:
        #   raise ValidationError("El correo debe contener la palabra 'institucional'.")
        # Validar que el correo termine con el dominio específico
        if not email.endswith('@ciencias.unam.mx'):
            raise ValidationError("El correo debe tener el dominio '@ciencias.unam.mx'.")
        return email
    

    def clean_password2(self):
        # Validación de las contraseñas
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return password2
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre

    def clean_apellidopaterno(self):
        apellidopaterno = self.cleaned_data.get('apellidopaterno')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidopaterno):
            raise ValidationError("El apellido paterno solo puede contener letras y espacios.")
        return apellidopaterno

    def clean_apellidomaterno(self):
        apellidomaterno = self.cleaned_data.get('apellidomaterno')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidomaterno):
            raise ValidationError("El apellido materno solo puede contener letras y espacios.")
        return apellidomaterno
    
    def clean_nocuenta(self):
        nocuenta = self.cleaned_data.get('nocuenta')
        mensaje = "El número de cuenta debe ser de 6 dígitos para trabajadores o de 9 dígitos para alumnos."
        # Verifica que nocuenta solo contenga dígitos
        if not nocuenta.isdigit():
            raise ValidationError(mensaje)
        # Verifica que nocuenta tenga una longitud válida
        if len(nocuenta) not in [6, 9]:
            raise ValidationError(mensaje)
        return nocuenta

    
    def clean(self):
        cleaned_data = super().clean()
        tipousuario = cleaned_data.get('tipousuario')
        area = cleaned_data.get('area')
        nocuenta = cleaned_data.get('nocuenta')

        # Validar que 'Área' solo se seleccione cuando el tipo de usuario es 'usuario'
        if tipousuario != 'usuario' and area:
            raise ValidationError("El campo 'Área' solo debe estar seleccionado cuando el tipo de usuario es 'usuario'.")
    
        if nocuenta is None:
            raise ValidationError("El campo 'Número de Cuenta' debe de ser un número entero.")

        # Si nocuenta tiene 6 dígitos, 'Área' debe ser 'trabajador'
        if len(nocuenta) == 6 and area != 'trabajador':
            if not tipousuario in ['administrador', 'proveedor']:    
                raise ValidationError("Si el número de cuenta es de 6 dígitos, el área debe ser 'trabajador'.")
    
        # Si nocuenta tiene 9 dígitos, 'Área' no debe ser 'trabajador'
        if len(nocuenta) == 9 and area == 'trabajador':
            raise ValidationError("Si el número de cuenta es de 9 dígitos, el área no debe ser 'trabajador'.")
        
        return cleaned_data



    def save(self, commit=True):
        # Para no guardar valores nulos, si el tipousuario es administrador
        # o proveedor, se le asigna un valor por defecto a area
        if self.cleaned_data['tipousuario'] in ['administrador', 'proveedor']:
            self.cleaned_data['area'] = 'trabajador'
        # Guardamos primero el usuario y luego el perfil
        user = User(
            username=self.cleaned_data['nocuenta'],  # Usar el email como username
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

class UserEditForm(forms.ModelForm):
    # Campos editables
    USER_CHOICES = [
        ('administrador', 'Administrador'),
        ('proveedor', 'Proveedor'),
        ('usuario', 'Usuario'),
    ]
    
    tipousuario = forms.ChoiceField(label='Tipo de Usuario', choices=USER_CHOICES, required=False)
    nombre = forms.CharField(label='Nombre', max_length=40)
    apellidopaterno = forms.CharField(label='Apellido paterno', max_length=40)
    apellidomaterno = forms.CharField(label='Apellido materno', max_length=40)
    celular = PhoneNumberField(label='Número de teléfono')
    email = forms.EmailField(label='Correo Electrónico')
    puntos = forms.IntegerField(label='Puntos')
    password = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = Usuario
        fields = ['tipousuario', 'nombre', 'apellidopaterno', 'apellidomaterno', 'celular', 'email', 'puntos', 'password', 'password2']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre

    def clean_apellidopaterno(self):
        apellidopaterno = self.cleaned_data.get('apellidopaterno')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidopaterno):
            raise ValidationError("El apellido paterno solo puede contener letras y espacios.")
        return apellidopaterno

    def clean_apellidomaterno(self):
        apellidomaterno = self.cleaned_data.get('apellidomaterno')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidomaterno):
            raise ValidationError("El apellido materno solo puede contener letras y espacios.")
        return apellidomaterno
    
    def clean_puntos(self):
        puntos = self.cleaned_data.get('puntos')
        if puntos < 0:
            raise ValidationError("Los puntos no pueden ser negativos.")
        return puntos
    
    def clean_password2(self):
        # Validación de las contraseñas
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        return password2

    def save(self, commit=True):
        usuario = super().save(commit=False)
        tipousuario = self.cleaned_data.get('tipousuario')
        password = self.cleaned_data.get('password')
        # Verificar si el campo 'tipousuario' requiere un cambio en 'area'
        if tipousuario in ['administrador', 'proveedor']:
            usuario.area = 'trabajador'

        if commit:
            usuario.save()  # Guardar cambios en el modelo Usuario
            user = usuario.user
            user.email = self.cleaned_data['email']

            # Cambiar la contraseña solo si se proporciona una nueva
            if password:
                user.set_password(password)

            user.save()

        return usuario


class AcumularPuntosForm(forms.Form):
    # Dev. libro
    # Asistir a conferencias
    # Resello de la credencial
    ACTIVIDAD_CHOICES =[
        ('libro', 'Devolver libro'),
        ('asistir', 'Asistir a conferencias o eventos'),
        ('resello', 'Resello de la credencial'),
    ]
    actividad = forms.ChoiceField(label='Actividad', choices=ACTIVIDAD_CHOICES, required=True)

    def save(self, usuario, commit=True):
        actividad = self.cleaned_data['actividad']
        obtenidos = 0
        if actividad == 'libro':
            obtenidos = 20
        elif actividad == 'asistir':
            obtenidos = 15
        elif actividad == 'resello':
            obtenidos = 10
        
        usuario.puntos += obtenidos
        if commit:
            usuario.save()
            # Generamos un nuevo registro en Acumulacion
            acumulacion = Acumulacion(usuario=usuario, actividad=actividad, puntos=obtenidos)
            acumulacion.save()
        return usuario