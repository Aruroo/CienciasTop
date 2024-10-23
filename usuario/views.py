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
        # Autenticar al usuario usando el correo electrónico
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
            # Verifica si el correo ya está en uso
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                user = form.save(commit=False)  # Guarda el usuario sin confirmar
                user.save()  # Guarda el usuario en la base de datos
                user.username = form.cleaned_data['nocuenta']
                user.save()  # Guarda el usuario en la base de datos
                if form.cleaned_data['tipousuario'] == 'proveedor':
                    add_to_group = Group.objects.get(name='proveedor')
                elif form.cleaned_data['tipousuario'] == 'admin':
                    add_to_group = Group.objects.get(name='administrador')
                else:
                    add_to_group = Group.objects.get(name='usuario_c')
                add_to_group.user_set.add(user)
                add_to_group.save()
                
                # Crea el perfil
                # Usuario.objects.create(
                #     user=user,
                #     nombre=form.cleaned_data['nombre'],
                #     apellidopaterno=form.cleaned_data['apellidopaterno'],
                #     apellidomaterno=form.cleaned_data['apellidomaterno'],
                #     celular=form.cleaned_data['celular'],
                #     nocuenta=form.cleaned_data['nocuenta'],
                #     area=form.cleaned_data['area'],
                #     email=form.cleaned_data['email'],
                # )
                user = form.save()
                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
                return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'usuarios/registrar.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def usuarios(request):
    usuarios = Usuario.objects.all()
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
def eliminar_usuario(request, id):
    usuario = Usuario.objects.get(id=id)
    usuario.delete()
    return redirect('usuarios')
