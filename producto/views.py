from django.shortcuts import render, redirect
from .forms import ProductoForm

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
