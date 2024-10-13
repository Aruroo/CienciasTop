from django.shortcuts import render

def index(request):
    return render(request, 'administrador.html')

def admin_usuarios(request):
    return render(request, 'admin_usuarios.html')