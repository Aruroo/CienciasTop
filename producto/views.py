from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductoForm , EditarProductoForm
from .models import Producto

def agregar_producto(request):
    if request.method == 'POST':
        # Hay que incluir request.FILES para manejar las imágenes
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_productos')
    else:
        form = ProductoForm()
    return render(request, 'agregar_producto.html', {'form': form})


def edita_producto(request, id):
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
