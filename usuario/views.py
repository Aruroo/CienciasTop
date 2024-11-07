#from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages  
#from django.urls import reverse
from .forms import UserEditForm, UserRegistrationForm
from .models import Usuario
from producto.models import Renta, Producto

import datetime

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

                messages.success(request, 'Acción exitosa.')
                return redirect('usuarios')
    else:
        form = UserRegistrationForm()
    return render(request, 'usuarios/registrar.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def usuarios(request):
    usuario_actual = request.user
    # Solo aquellos que no estan ocultos y no sean el usuario actual
    usuarios = Usuario.objects.filter(oculto=False).exclude(user = usuario_actual)
    return render(request, 'usuarios/index.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, nocuenta):
    usuario = get_object_or_404(Usuario, nocuenta=nocuenta)
    user = usuario.user  # Obtenemos el usuario relacionado

    if request.method == 'POST':
        formulario = UserEditForm(request.POST, instance=usuario)
        if formulario.is_valid():
            formulario.save()

            # Verifica si el checkbox para cambiar el tipo de usuario está activado
            if request.POST.get('toggleTipousuario') == '1':
                # Recupera el tipo de usuario del formulario solo si fue cambiado
                nuevo_tipousuario = formulario.cleaned_data.get('tipousuario')
                grupo_actual = user.groups.first().name if user.groups.exists() else None

                # Cambia el grupo solo si el nuevo tipo de usuario es diferente al actual
                if nuevo_tipousuario and nuevo_tipousuario != grupo_actual:
                    user.groups.clear()  # Limpia el grupo actual
                    
                    # Asigna el nuevo grupo basado en el valor de `nuevo_tipousuario`
                    if nuevo_tipousuario == 'proveedor':
                        add_to_group = Group.objects.get(name='proveedor')
                    elif nuevo_tipousuario == 'administrador':
                        add_to_group = Group.objects.get(name='administrador')
                    else:
                        add_to_group = Group.objects.get(name='usuario_c')
                    
                    add_to_group.user_set.add(user)  # Asigna el nuevo grupo

            return redirect('usuarios')
    else:
        formulario = UserEditForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {'formulario': formulario, 'usuario':usuario})

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, nocuenta):
    usuario = Usuario.objects.get(nocuenta=nocuenta)
    #En realidad, solo oculta a los usuarios, pero no se eliminan
    usuario.oculto = True
    usuario.save()
    return redirect('usuarios')


def perfil(request):
    usuario_actual = request.user
    usuario = Usuario.objects.get(user=usuario_actual)
    try:
        rentas = Renta.objects.filter(id_deudor=usuario_actual)
    except Renta.DoesNotExist:
        rentas = None
        
    rentas_activas = []
    for renta in rentas:
        objeto_rentado = renta.id_libro
        fecha_devolucion = renta.fecha_prestamo + datetime.timedelta(days=objeto_rentado.dias)
        rentas_activas.append({'renta':renta, 'fecha_devolucion':fecha_devolucion})
    
    if len(usuario.nocuenta) == 9:
        es_estudiante = True
    else:
        es_estudiante = False
        
    if usuario_actual.groups.filter(name='proveedor').exists():
        es_proveedor = True
    else:
        es_proveedor = False
    return render(request, 'usuarios/perfil.html', 
                  {'usuario':usuario, 
                   'es_estudiante':es_estudiante, 
                   'es_proveedor':es_proveedor,
                   'rentas_activas':rentas_activas
                   })