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
from datetime import datetime, timedelta

import datetime as dt

def is_user_c(user):
    """
    Verifica si el usuario pertenece al grupo 'usuario_c'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'usuario_c', False en caso contrario.
    """
    return user.groups.filter(name='usuario_c').exists()

def is_prov(user):
    """
    Verifica si el usuario pertenece al grupo 'proveedor'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'proveedor', False en caso contrario.
    """
    return user.groups.filter(name='proveedor').exists()

def is_prov_or_admin(user):
    """
    Verifica si el usuario pertenece al grupo 'proveedor' o 'administrador'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'proveedor' o 'administrador', False en caso contrario.
    """
    return user.groups.filter(name='proveedor').exists() or user.groups.filter(name='administrador').exists()

def is_user_c_or_admin(user):
    """
    Verifica si el usuario pertenece al grupo 'usuario_c' o 'administrador'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'usuario_c' o 'administrador', False en caso contrario.
    """
    return user.groups.filter(name='usuario_c').exists() or user.groups.filter(name='administrador').exists()

def is_admin(user):
    """
    Verifica si el usuario pertenece al grupo 'administrador'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'administrador', False en caso contrario.
    """
    return user.groups.filter(name='administrador').exists()

def custom_login(request):
    """
    Autentica al usuario utilizando su número de cuenta y contraseña.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista de productos si la autenticación es exitosa.
                      Si la autenticación falla, muestra un mensaje de error en la misma página de inicio de sesión.
    """
    if request.method == 'POST':
        no_cuenta = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=no_cuenta, password=password)
        if user is not None:
            login(request, user)
            return redirect('productos')
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'usuarios/login.html')

@login_required
def custom_logout(request):
    """
    Cierra la sesión del usuario autenticado y redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la página de inicio de sesión.
    """
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = None
    if username is not None:
        logout(request)
        return redirect('login')

@login_required
@user_passes_test(is_admin)
def registrar_usuario(request):
    """
    Permite al administrador registrar un nuevo usuario, validando duplicados de número de cuenta y correo electrónico.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista de usuarios si el registro es exitoso, o muestra un formulario de registro con errores en caso contrario.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            nocuenta = form.cleaned_data['nocuenta']
            if User.objects.filter(username=nocuenta).exists():
                form.add_error('nocuenta', 'Este número de cuenta ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                user = form.save(commit=False)
                user.username = nocuenta
                user = form.save()

                tipousuario = form.cleaned_data['tipousuario']
                if tipousuario == 'proveedor':
                    add_to_group = Group.objects.get(name='proveedor')
                elif tipousuario == 'administrador':
                    add_to_group = Group.objects.get(name='administrador')
                else:
                    add_to_group = Group.objects.get(name='usuario_c')

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
    """
    Muestra una lista de usuarios no ocultos, excluyendo al usuario actual.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de usuarios no ocultos.
    """
    usuario_actual = request.user
    usuarios = Usuario.objects.filter(oculto=False).exclude(user=usuario_actual)
    return render(request, 'usuarios/index.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, nocuenta):
    """
    Permite al administrador editar la información de un usuario y cambiar su tipo de usuario si es necesario.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        nocuenta (str): Número de cuenta del usuario a editar.

    Returns:
        HttpResponse: Redirige a la vista de usuarios si el formulario es válido, o muestra el formulario de edición en caso contrario.
    """
    usuario = get_object_or_404(Usuario, nocuenta=nocuenta)
    user = usuario.user

    if request.method == 'POST':
        formulario = UserEditForm(request.POST, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            if request.POST.get('toggleTipousuario') == '1':
                nuevo_tipousuario = formulario.cleaned_data.get('tipousuario')
                grupo_actual = user.groups.first().name if user.groups.exists() else None

                if nuevo_tipousuario and nuevo_tipousuario != grupo_actual:
                    user.groups.clear()
                    if nuevo_tipousuario == 'proveedor':
                        add_to_group = Group.objects.get(name='proveedor')
                    elif nuevo_tipousuario == 'administrador':
                        add_to_group = Group.objects.get(name='administrador')
                    else:
                        add_to_group = Group.objects.get(name='usuario_c')
                    
                    add_to_group.user_set.add(user)

            return redirect('usuarios')
    else:
        formulario = UserEditForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {'formulario': formulario, 'usuario': usuario})

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, nocuenta):
    """
    Permite al administrador ocultar un usuario, en lugar de eliminarlo permanentemente.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        nocuenta (str): Número de cuenta del usuario a ocultar.

    Returns:
        HttpResponse: Redirige a la vista de usuarios.
    """
    usuario = Usuario.objects.get(nocuenta=nocuenta)
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
        fecha_devolucion = renta.fecha_prestamo + dt.timedelta(days=objeto_rentado.dias)
        rentas_activas.append({'renta':renta, 'fecha_devolucion':fecha_devolucion})
    
    if len(usuario.nocuenta) == 9:
        es_estudiante = True
    else:
        es_estudiante = False
        
    if usuario_actual.groups.filter(name='proveedor').exists():
        es_proveedor = True
    else:
        es_proveedor = False
    
    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    is_prov = request.user.groups.filter(name='proveedor').exists()

    return render(request, 'usuarios/perfil.html', 
                  {'usuario':usuario, 
                   'es_estudiante':es_estudiante, 
                   'es_proveedor':es_proveedor,
                   'rentas_activas':rentas_activas,
                   'is_usuario_c': is_usuario_c,
                   'is_prov': is_prov,
                   'is_adminn': is_adminn
                   })

@login_required
def historial(request):
    usuario_actual = request.user
    historial_data = []

    hoy = datetime.now()
    primer_dia_mes = hoy.replace(day=1)
    if hoy.month == 12:
        primer_dia_siguiente_mes = hoy.replace(year=hoy.year + 1, month=1, day=1)
    else:
        primer_dia_siguiente_mes = hoy.replace(month=hoy.month + 1, day=1)

    rentas = Renta.objects.filter(
        id_deudor=usuario_actual,
        fecha_prestamo__gte=primer_dia_mes,
        fecha_prestamo__lt=primer_dia_siguiente_mes
    )

    for renta in rentas:
        producto = renta.id_libro
        fecha_devolucion = renta.fecha_prestamo + timedelta(days=producto.dias)

        historial_data.append({
            'nombre': producto.nombre,
            'costo': producto.costo,
            'descripcion': producto.descripcion,
            'imagen': producto.imagen.url if producto.imagen else None,
            'categoria': producto.categoria,
            'dias': producto.dias,
            'fecha_prestamo': renta.fecha_prestamo,
            'fecha_devolucion': fecha_devolucion,
        })

    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    is_prov = request.user.groups.filter(name='proveedor').exists()

    return render(request, 'usuarios/historial.html',
                 {'historial_data': historial_data,
                   'is_usuario_c': is_usuario_c,
                   'is_prov': is_prov,
                   'is_adminn': is_adminn})