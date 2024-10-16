from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    nombre = forms.CharField(label='Nombre', max_length=40)
    apellidos = forms.CharField(label='Apellidos', max_length=40)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma tu contraseña', widget=forms.PasswordInput)
    
    CARRERA_CHOICES = [
        ('actuaria', 'Actuaria'),
        ('biologia', 'Biología'),
        ('computacion', 'Ciencias de la Computación'),
        ('tierra', 'Ciencias de la Tierra'),
        ('fisica', 'Física'),
        ('biomedica', 'Física Biomédica'),
        ('matematicas', 'Matemáticas'),
        ('aplicadas', 'Matemáticas Aplicadas'),
    ]
    
    carrera = forms.ChoiceField(label='Carrera', choices=CARRERA_CHOICES)
    nocuenta = forms.CharField(label='Número de Cuenta', max_length=9)
    email = forms.EmailField(label='Correo Electrónico')

    class Meta:
        model = User
        fields = ['nombre', 'apellidos', 'email', 'password1', 'password2', 'carrera', 'nocuenta']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['email'],  # Usar el email como username
            email=self.cleaned_data['email']
        )
        user.set_password(self.cleaned_data['password1'])  # Establecer la contraseña de forma segura
        if commit:
            user.save()
        return user
