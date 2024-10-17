from django.test import TestCase
from django.contrib.auth.models import User
from .models import Usuario
from .forms import UserRegistrationForm

class UsuarioModelTest(TestCase):

    def setUp(self):
        # Configuramos datos de prueba
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.usuario = Usuario.objects.create(
            user=self.user,
            nombre='Juan',
            apellidopaterno='Pérez',
            apellidomaterno='González',
            celular='+12125552368',
            nocuenta='123456789',
            area='computacion',
            email='test@example.com'
        )

    def test_usuario_creation(self):
        """Probar que el perfil de Usuario se crea correctamente vinculado a User"""
        usuario = Usuario.objects.get(user=self.user)
        self.assertEqual(usuario.nombre, 'Juan')
        self.assertEqual(usuario.apellidopaterno, 'Pérez')
        self.assertEqual(usuario.apellidomaterno, 'González')
        self.assertEqual(usuario.nocuenta, '123456789')
        self.assertEqual(usuario.user.email, 'test@example.com')

    def test_passwords_match(self):
        """Probar que las contraseñas coinciden durante el registro"""
        form_data = {
            'nombre': 'Pedro',
            'apellidopaterno': 'Lopez',
            'apellidomaterno': 'Ramírez',
            'celular': '+12125552368',
            'nocuenta': '987654321',
            'area': 'matematicas',
            'email': 'pedro@example.com',
            'password1': 'password123',
            'password2': 'password456'  # Contraseña no coincide
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())  # Este formulario debería ser inválido
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'], ["Las contraseñas no coinciden."])

    def test_nocuenta_length(self):
        """Probar que el campo nocuenta tiene como máximo 9 caracteres"""
        form_data = {
            'nombre': 'Pedro',
            'apellidopaterno': 'Lopez',
            'apellidomaterno': 'Ramírez',
            'celular': '+12125552368',
            'nocuenta': '12345678910',  # Excede 9 caracteres
            'area': 'matematicas',
            'email': 'pedro2@example.com',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())  # Este formulario debería ser inválido
        self.assertIn('nocuenta', form.errors)

    def test_save_user_profile(self):
        """Probar que el formulario guarda correctamente el perfil de usuario"""
        form_data = {
            'nombre': 'Ana',
            'apellidopaterno': 'Martinez',
            'apellidomaterno': 'Sanchez',
            'celular': '+12125552368',
            'nocuenta': '987654321',
            'area': 'fisica',
            'email': 'ana@example.com',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        usuario = Usuario.objects.get(user=user)
        self.assertEqual(usuario.nombre, 'Ana')
        self.assertEqual(usuario.apellidopaterno, 'Martinez')
        self.assertEqual(usuario.apellidomaterno, 'Sanchez')
        self.assertEqual(usuario.nocuenta, '987654321')
        self.assertEqual(usuario.area, 'fisica')
        self.assertEqual(usuario.celular, '+12125552368')
