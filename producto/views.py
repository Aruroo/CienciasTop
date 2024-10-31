from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import ProductoForm , EditarProductoForm
from .models import Producto, Renta

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

@login_required
def productos(request):
    """
    Muestra la lista de productos disponibles para rentar.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de productos disponibles y el estado del grupo del usuario.
    """
    productos_rentados = Renta.objects.all()
    productos = Producto.objects.exclude(renta__in=productos_rentados)
    
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
        productos = Producto.objects.all().filter(user=user)
    else:
        productos = Producto.objects.all()
    return render(request, 'productos/index_admin.html', {'productos': productos,
        'is_usuario_c': is_usuario_c,
        'is_prov': is_prov,
        'is_adminn': is_adminn})

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
    libro = Producto.objects.get(id=id)
    libro.delete()
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
    usuario = request.user
    libro = Producto.objects.get(id=id)
    libro.disponibilidad = False
    renta = Renta(id_libro=libro, id_deudor=usuario, fecha_prestamo=timezone.now())
    libro.save()
    renta.save()
    return redirect('productos')

