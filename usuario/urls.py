from django.urls import path
from . import views

urlpatterns = [
    path('', views.usuarios, name='usuarios'),
    path('usuarios/registrar', views.registrar_usuario, name='registrar'),  # Ruta para la vista de registro
    path('usuarios/editar', views.registrar_usuario, name='editar_u'),
    path('eliminar/<int:nocuenta>', views.eliminar_usuario, name='eliminar_u'),
    path('usuarios/editar/<int:nocuenta>', views.editar_usuario, name='editar_u'),
    path('usuario/perfil', views.perfil, name='perfil'),
    path('usuario/perfil/historial', views.historial, name='historial'),
    path('login/', views.custom_login, name='login'),  # Ruta para la vista de login
    path('logout/', views.custom_logout, name='logout'), 
    #path('welcome/', views.welcome, name='welcome'),  # Ruta para la vista de bienvenida
]