from django.urls import path
from . import views
urlpatterns =[
    path('agregar/',views.agregar_producto, name='agregar'),
    path('editar/<int:id>/',views.edita_producto, name='editar')
]