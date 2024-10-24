"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging
from producto.models import Producto
from usuario.models import Usuario
from django.contrib.contenttypes.models import ContentType

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

GROUPS = ['proveedor', 'usuario_c', 'administrador']
MODELS = ['libro']
PERMISSIONS = ['ver', 'editar', 'rentar']  # For now only view permission by default for all, others include add, delete, change


class Command(BaseCommand):
    help = 'Crea grupos de proveedor, usuario_c y administrador'

    def handle(self, *args, **options):
        for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            #ct = ContentType.objects.get_for_model(Profile)
            # ct = ContentType.objects.get_for_model(Producto)
            
            # if group == 'proveedor':
            #     # permission = Permission.objects.create(codename='can_view_libro',
            #     #                    name='Can view libro',
            #     #                    content_type=ct)
            #     name = 'Can view libro'
            #     try:
            #         permission = Permission.objects.get(name=name)
            #     except Permission.DoesNotExist:
            #         logging.warning("Permission not found with name '{}'.".format(name))
            #     new_group.permissions.add(permission)
                
                
            #     name = 'Can edit libro'
            #     try:
            #         permission = Permission.objects.get(name=name)
            #     except Permission.DoesNotExist:
            #         logging.warning("Permission not found with name '{}', creating".format(name))
            #         permission = Permission.objects.create(codename='can_edit_libro',
            #                        name=name,
            #                        content_type=ct)
            #     new_group.permissions.add(permission)
                
            # else:
                
            #     name = 'Can view libro'
            #     try:
            #         permission = Permission.objects.get(name=name)
            #     except Permission.DoesNotExist:
            #         logging.warning("Permission not found with name '{}'.".format(name))
            #     new_group.permissions.add(permission)
                
            #     name = 'Can add renta'
            #     try:
            #         permission = Permission.objects.get(name=name)
            #     except Permission.DoesNotExist:
            #         logging.warning("Permission not found with name '{}'.".format(name))
            #     new_group.permissions.add(permission)

        print("Created default group and permissions.")