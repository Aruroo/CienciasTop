from django.urls import path
from . import views
urlpatterns =[
    path('agregar/',views.agregar_producto, name='agregar'),
]