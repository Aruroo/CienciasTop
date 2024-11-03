from django.shortcuts import render

def pagina_principal(request):
    """
    Renderiza la página principal con una lista de productos y sus precios.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el contenido de 'pagina_principal.html', que incluye la lista de productos y sus precios.
    """
    lista = [
        {'nombre': 'Balon', 'precio': 1000},
        {'nombre': 'Juego1', 'precio': 2000},
        {'nombre': 'Juego2', 'precio': 3000},
        {'nombre': 'Tablet', 'precio': 4000},
        {'nombre': 'Pelicula', 'precio': 5000},
    ]

    context = {
        'productos': lista
    }

    return render(request, 'pagina_principal.html', context)
