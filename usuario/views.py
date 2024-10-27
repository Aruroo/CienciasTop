#from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages  
#from django.urls import reverse
from .forms import UserRegistrationForm
from .models import Usuario

def is_admin(user):
    return user.groups.filter(name='administrador').exists()

def custom_login(request):
    if request.method == 'POST':
        #email = request.POST['email']
        no_cuenta = request.POST['username']
        password = request.POST['password']
        # Autenticar al usuario usando el username (numero de cuenta)
        user = authenticate(request, username=no_cuenta, password=password)
        if user is not None:
            login(request, user)
            return redirect('productos')  # Redirige a la vista de bienvenida
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'usuarios/login.html')

@login_required
def custom_logout(request):
    if request.user.is_authenticated == True:
        username = request.user.username
    else:
        username = None
    if username != None:
        logout(request)
        return redirect('login')

# @login_required
# def welcome(request):
#     return redirect(reverse('principal'))
@login_required
@user_passes_test(is_admin)
def registrar_usuario(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            nocuenta = form.cleaned_data['nocuenta']
            # Verificación de duplicados para nocuenta y email
            if User.objects.filter(username=nocuenta).exists():
                form.add_error('nocuenta', 'Este número de cuenta ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                # Guardar el usuario sin duplicar llamadas a form.save()
                user = form.save(commit=False)
                user.username = nocuenta
                user = form.save()

                # Asignación de grupo según tipo de usuario
                tipousuario = form.cleaned_data['tipousuario']
                if tipousuario == 'proveedor':
                    add_to_group = Group.objects.get(name='proveedor')
                elif tipousuario == 'administrador':
                    add_to_group = Group.objects.get(name='administrador')
                else:
                    add_to_group = Group.objects.get(name='usuario_c')

                # Agregar el usuario al grupo y guardar
                add_to_group.user_set.add(user)
                add_to_group.save()

                messages.success(request, 'Registro exitoso. Ahora el usuario puede iniciar sesión.')
                return redirect('usuarios')
    else:
        form = UserRegistrationForm()
    return render(request, 'usuarios/registrar.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def usuarios(request):
    # Solo aquellos que no estan ocultos
    usuarios = Usuario.objects.filter(oculto=False)
    return render(request, 'usuarios/index.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, nocuenta):
    usuario = Usuario.objects.get(nocuenta=nocuenta)
    formulario = UserRegistrationForm(request.POST or None, request.FILES or None, instance=usuario)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('usuarios')
    return render(request, 'usuarios/editar.html', {'formulario':formulario})

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, nocuenta):
    usuario = Usuario.objects.get(nocuenta=nocuenta)
    #En realidad, solo oculta a los usuarios, pero no se eliminan
    usuario.oculto = True
    usuario.save()
    return redirect('usuarios')
