from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied



def is_superuser(user):
    """
    Verifica si el usuario es un superusuario.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario es un superusuario, False en caso contrario.
    """
    return user.is_superuser

@user_passes_test(is_superuser)
def index(request):
    """
    Renderiza la página principal del administrador.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el contenido de 'administrador.html'.
    """
    return render(request, 'administrador.html')

@user_passes_test(is_superuser)
def admin_usuarios(request):
    """
    Renderiza la página de administración de usuarios.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el contenido de 'admin_usuarios.html'.
    """
    return render(request, 'admin_usuarios.html')

@user_passes_test(is_superuser)
def admin_productos(request):
    """
    Renderiza la página de administración de productos.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el contenido de 'admin_productos.html'.
    """
    return render(request, 'admin_productos.html')

def permission_denied(request):
    """
    Genera una excepción de permiso denegado.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Raises:
        PermissionDenied: Excepción indicando que se necesitan permisos de administrador.
    """
    raise PermissionDenied("Necesitas permisos de administrador.")
