from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns =[
    #path('', views.inicio, name='inicio'),
    path('', views.productos, name='productos'),
    path('adminproductos', views.admin_producto, name='admin_productos'),
    path('adminproductos/crear', views.agregar_producto, name='crear'),
    path('adminproductos/editar', views.agregar_producto, name='editar'),
    path('eliminar/<int:id>', views.eliminar_producto, name='eliminar'),
    path('adminproductos/editar/<int:id>', views.editar_producto, name='editar'),
    path('adminproductos/rentar/<int:id>', views.rentar_producto, name='rentar'),
    path('adminproductos/rentas_activas', views.rentas_activas_usuario, name='rentas_activas'),
    path('adminproductos/rentas_activas/<int:nocuenta>', views.rentas_activas_usuario, name='rentas_activas'),
    path('adminproductos/rentas_activas/devolver/<int:nocuenta>/<int:id>', views.devolver_producto, name='devolver'),
    path('productos/', views.productos, name='productos'),

    
    #path('agregar/',views.agregar_producto, name='agregar'),
    #path('editar/<int:id>/',views.edita_producto, name='editar')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)