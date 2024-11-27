from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.productos, name='productos'),
    path('adminproductos', views.admin_productos, name='admin_productos'),
    path('adminproductos/crear', views.agregar_producto, name='crear'),
    path('eliminar/<int:id>', views.eliminar_producto, name='eliminar'),
    path('adminproductos/editar', views.agregar_producto, name='editar'),
    path('adminproductos/editar/<int:id>', views.editar_producto, name='editar'),
    path('adminproductos/rentar/<int:id>', views.rentar_producto, name='rentar'),
    path('productos/', views.productos, name='productos'),
    path('adminproductos/rentas_activas', views.rentas_activas_usuario, name='rentas_activas'),
    path('adminproductos/rentas_activas/<int:noCuenta>', views.rentas_activas_usuario, name='rentas_activas'),
    path('adminproductos/rentas_activas/devolvera/<int:id>', views.devolver_producto, name='devolver'),
]
 + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)