from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def index(request):
    return render(request, 'administrador.html')

@user_passes_test(is_superuser)
def admin_usuarios(request):
    return render(request, 'admin_usuarios.html')

@user_passes_test(is_superuser)
def admin_productos(request):
    return render(request, 'admin_productos.html')

def permission_denied(request):
    raise PermissionDenied("Necesitas permisos de administrador.")
