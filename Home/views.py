from django.shortcuts import render

# Create your views here.
def pagina_principal(request):
    
    lista = [
        {'nombre': 'Balon',   'precio': 1000},
        {'nombre': 'Juego1',  'precio': 2000},
        {'nombre': 'Juego2',  'precio': 3000},
        {'nombre': 'Tablet',  'precio': 4000},
        {'nombre': 'Pelicula', 'precio': 5000},
    ]
    
    context = {
        'productos': lista
    }
    return render(request, 'pagina_principal.html', context)