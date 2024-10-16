from django.urls import path
from . import views  # Asegúrate de importar ambas vistas

urlpatterns = [
   path('register/', views.register, name='register'),  # Ruta para la vista de registro
    path('', views.custom_login, name='login'),  # Ruta para la vista de login
    path('welcome/', views.welcome, name='welcome'),  # Ruta para la vista de bienvenida
]