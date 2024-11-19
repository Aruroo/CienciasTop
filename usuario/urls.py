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
    # Reportes
    path('reportes/usuarios-activos/', views.reporte_usuarios_activos, name='reporte_usuarios_activos'),
    path('reportes/productos-baratos/', views.reporte_productos_baratos, name='reporte_productos_baratos'),
    path('reportes/tardios/', views.reporte_usuarios_tardios, name='reporte_tardios'),
    path('reportes/mas-rentados/', views.reporte_productos_mas_rentados, name='reporte_mas_rentados'),
    path('reportes/usuarios-inactivos/', views.reporte_cantidad_cuentas_inactivas, name='reporte_usuarios_inactivos'),
    path('reportes/usuarios-mas-activos/', views.reporte_usuarios_mas_activos, name='reporte_usuarios_mas_activos'),
    path('reportes/', views.reportes_menu,name='reportes_menu'), 
    #path('welcome/', views.welcome, name='welcome'),  # Ruta para la vista de bienvenida
]