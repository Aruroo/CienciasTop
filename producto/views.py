from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from usuario.models import Usuario
from .forms import ProductoForm, EditarProductoForm
from .models import Producto, Renta, User
from django.contrib import messages

import datetime

# Group Check Functions
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

def is_admin(user):
    return user.groups.filter(name='administrador').exists()

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

# Views
@login_required
def productos(request):
    """
    Muestra la lista de productos disponibles para rentar.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de productos disponibles y el estado del grupo del usuario.
    """
    productos_rentados = Renta.objects.filter(fecha_devuelto__isnull=True)
    productos = Producto.objects.exclude(rentas__in=productos_rentados)
    #productos = Producto.objects.exclude(rentas__in=productos_rentados)
    
    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    is_prov = request.user.groups.filter(name='proveedor').exists()

    return render(request, 'productos/index.html', {
        'productos': productos,
        'is_usuario_c': is_usuario_c,
        'is_prov': is_prov,
        'is_adminn': is_adminn
    })

@login_required
@user_passes_test(is_prov_or_admin)
def admin_producto(request):
    """
    Muestra la lista de productos para el administrador o proveedor.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de productos para el administrador o proveedor.
    """
    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    is_prov = request.user.groups.filter(name='proveedor').exists()

    user = request.user
    if user.groups.filter(name='proveedor').exists():
        productos = Producto.objects.filter(user=user)
    else:
        productos = Producto.objects.all()
    return render(request, 'productos/index_admin.html', {
        'productos': productos,
        'is_usuario_c': is_usuario_c,
        'is_prov': is_prov,
        'is_adminn': is_adminn
    })

@login_required
@user_passes_test(is_prov_or_admin)
def agregar_producto(request):
    """
    Permite al proveedor o administrador agregar un nuevo producto.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista de administración de productos si el formulario es válido.
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.user = request.user
            producto.save()         
            return redirect('admin_productos')
    else:
        form = ProductoForm()
    return render(request, 'agregar_producto.html', {'form': form})

@login_required
@user_passes_test(is_prov_or_admin)
def editar_producto(request, id):
    """
    Permite al proveedor o administrador editar un producto existente.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        id (int): ID del producto a editar.

    Returns:
        HttpResponse: Redirige a la vista de administración de productos si el formulario es válido.
    """
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = EditarProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('admin_productos')
    else:
        form = EditarProductoForm(instance=producto)

    return render(request, 'editar_producto.html', {'form': form})

@login_required
@user_passes_test(is_prov_or_admin)
def eliminar_producto(request, id):
    """
    Permite al proveedor o administrador eliminar un producto.
    
    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        id (int): ID del producto a eliminar.
    
    Returns:
        HttpResponse: Redirige a la vista de administración de productos.
    """
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect('admin_productos')

@login_required
@user_passes_test(is_user_c_or_admin)
def rentar_producto(request, id):
    """
    Permite al usuario o administrador rentar un producto.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        id (int): ID del producto a rentar.

    Returns:
        HttpResponse: Redirige a la vista de productos después de realizar la renta.
    """
    user = request.user
    usuario = Usuario.objects.get(user=user)
    producto = Producto.objects.get(id=id)

    if usuario.puntos >= producto.costo:
        usuario.puntos -= producto.costo
        usuario.puntos += int(producto.costo / 2) 
        usuario.save()
        renta = Renta(id_producto=producto, id_deudor=user, fecha_prestamo=timezone.now())
        renta.save()
        messages.success(request, 'Producto rentado exitosamente.')
        return redirect('productos')
    else:
        messages.error(request, 'No tienes suficientes puntos para rentar este producto.')
        return redirect('productos')
    
    
@login_required
@user_passes_test(is_admin)
def rentas_activas_usuario(request, nocuenta=None):
    try:
        usuario = User.objects.get(username=nocuenta)
    except User.DoesNotExist:
        usuario = None
    try:
        rentas = Renta.objects.filter(id_deudor=usuario).filter(fecha_devuelto__isnull=True)
    except Renta.DoesNotExist:
        rentas = None
        
    rentas_activas = []
    for renta in rentas:
        objeto_rentado = renta.id_producto
        fecha_devolucion_esperada = renta.fecha_prestamo + datetime.timedelta(days=objeto_rentado.dias)
        rentas_activas.append({'renta':renta, 'fecha_devolucion_esperada':fecha_devolucion_esperada})
    
    return render(request, 'productos/devolver.html', {'rentas_activas':rentas_activas, 'usuario':usuario})

@login_required
@user_passes_test(is_admin)
def devolver_producto(request, nocuenta, id):
    #producto = Producto.objects.get(id=id)
    renta = Renta.objects.get(id=id)
    renta.fecha_devuelto = timezone.now()
    renta.save()
    
    objeto_rentado = renta.id_producto
    fecha_devolucion_esperada = renta.fecha_prestamo + datetime.timedelta(days=objeto_rentado.dias)
    
    if fecha_devolucion_esperada < renta.fecha_devuelto.date():
        usuario = Usuario.objects.get(nocuenta=nocuenta)
        usuario.puntos -= 20
        usuario.save()
    
    messages.success(request, 'Producto devuelto exitosamente.')
    return redirect('rentas_activas', nocuenta)