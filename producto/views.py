from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import ProductoForm , EditarProductoForm
from .models import Producto, Renta

def is_user_c(user):
    return user.groups.filter(name='usuario_c').exists()
def is_prov(user):
    return user.groups.filter(name='proveedor').exists()
def is_prov_or_admin(user):
    return user.groups.filter(name='proveedor').exists() or user.groups.filter(name='administrador').exists()
def is_user_c_or_admin(user):
    return user.groups.filter(name='usuario_c').exists() or user.groups.filter(name='administrador').exists()

#@login_required
# def inicio(request):
#     return render(request, 'productos/index.html')

# Productos
@login_required
def productos(request):
    # Obtener todos los productos que están rentados
    productos_rentados = Renta.objects.all()
    productos = Producto.objects.exclude(renta__in=productos_rentados)
    
    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    
    # Pasar la información de productos y el estado del grupo al contexto
    return render(request, 'productos/index.html', {
        'productos': productos,
        'is_usuario_c': is_usuario_c,
        'is_adminn': is_adminn
    })

@login_required
@user_passes_test(is_prov_or_admin)
def admin_producto(request):
    user = request.user
    if user.groups.filter(name='proveedor').exists():
        productos = Producto.objects.all().filter(user=user)
    else:
        productos = Producto.objects.all()
    return render(request, 'productos/index_admin.html', {'productos': productos})

@login_required
@user_passes_test(is_prov_or_admin)
def agregar_producto(request):
    if request.method == 'POST':
        # Hay que incluir request.FILES para manejar las imágenes
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.user = request.user
            producto.save()         
            return redirect('admin_productos')
    else:
        form = ProductoForm()
    return render(request, 'agregar_producto.html', {'form': form}) # TODO Redirigir

@login_required
@user_passes_test(is_prov_or_admin)
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = EditarProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            # Redirige a la vista de lista de productos (admin_productos)
            return redirect('admin_productos')
    else:
        # Cargar los datos actuales del producto en el formulario
        form = EditarProductoForm(instance=producto)

    return render(request, 'editar_producto.html', {'form': form})

@login_required
@user_passes_test(is_prov_or_admin)
def eliminar_producto(request, id):
    libro = Producto.objects.get(id=id)
    libro.delete()
    return redirect('admin_productos')

@login_required
@user_passes_test(is_user_c_or_admin)
def rentar_producto(request, id):
    usuario = request.user
    libro = Producto.objects.get(id=id)
    libro.disponibilidad = False
    renta = Renta(id_libro=libro, id_deudor=usuario, fecha_prestamo=timezone.now())
    libro.save()
    renta.save()
    return redirect('productos')
