from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages  
from django.urls import reverse
from .forms import UserRegistrationForm
from .models import Profile

def custom_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        # Autenticar al usuario usando el correo electrónico
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('welcome')  # Redirige a la vista de bienvenida
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'login.html')

@login_required
def welcome(request):
    my_url = reverse('principal')
    return render(request, my_url)  # Plantilla de bienvenida

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Verifica si el correo ya está en uso
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                user = form.save(commit=False)  # Guarda el usuario sin confirmar
                user.save()  # Guarda el usuario en la base de datos
                
                # Crea el perfil
                Profile.objects.create(
                    user=user,
                    nombre=form.cleaned_data['nombre'],
                    apellidos=form.cleaned_data['apellidos'],
                    nocuenta=form.cleaned_data['nocuenta'],
                    carrera=form.cleaned_data['carrera']
                )
                return redirect('login')  # Redirige a la vista de inicio de sesión
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

