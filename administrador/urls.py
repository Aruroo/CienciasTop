from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin-usuarios/', views.admin_usuarios, name='admin_usuarios'),
]
