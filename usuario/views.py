#from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages  
#from django.urls import reverse
from .forms import UserEditForm, UserRegistrationForm, AcumularPuntosForm
from .models import Usuario, Acumulacion
from producto.models import Renta, Producto
from datetime import datetime, timedelta, date
from django.db.models import Count, Q

import datetime as dt

def is_user_c(user):
    """
    Verifica si el usuario pertenece al grupo 'usuario_c'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'usuario_c', False en caso contrario.
    """
    return user.groups.filter(name='usuario_c').exists()

def is_prov(user):
    """
    Verifica si el usuario pertenece al grupo 'proveedor'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'proveedor', False en caso contrario.
    """
    return user.groups.filter(name='proveedor').exists()

def is_prov_or_admin(user):
    """
    Verifica si el usuario pertenece al grupo 'proveedor' o 'administrador'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'proveedor' o 'administrador', False en caso contrario.
    """
    return user.groups.filter(name='proveedor').exists() or user.groups.filter(name='administrador').exists()

def is_user_c_or_admin(user):
    """
    Verifica si el usuario pertenece al grupo 'usuario_c' o 'administrador'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'usuario_c' o 'administrador', False en caso contrario.
    """
    return user.groups.filter(name='usuario_c').exists() or user.groups.filter(name='administrador').exists()

def is_admin(user):
    """
    Verifica si el usuario pertenece al grupo 'administrador'.

    Args:
        user (User): Objeto del usuario a verificar.

    Returns:
        bool: True si el usuario pertenece al grupo 'administrador', False en caso contrario.
    """
    return user.groups.filter(name='administrador').exists()

def custom_login(request):
    """
    Autentica al usuario utilizando su número de cuenta y contraseña.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista de productos si la autenticación es exitosa.
                      Si la autenticación falla, muestra un mensaje de error en la misma página de inicio de sesión.
    """
    if request.method == 'POST':
        no_cuenta = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=no_cuenta, password=password)
        if user is not None:
            login(request, user)
            return redirect('productos')
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'usuarios/login.html')

@login_required
def custom_logout(request):
    """
    Cierra la sesión del usuario autenticado y redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la página de inicio de sesión.
    """
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = None
    if username is not None:
        logout(request)
        return redirect('login')

@login_required
@user_passes_test(is_admin)
def registrar_usuario(request):
    """
    Permite al administrador registrar un nuevo usuario, validando duplicados de número de cuenta y correo electrónico.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista de usuarios si el registro es exitoso, o muestra un formulario de registro con errores en caso contrario.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            nocuenta = form.cleaned_data['nocuenta']
            if User.objects.filter(username=nocuenta).exists():
                form.add_error('nocuenta', 'Este número de cuenta ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                user = form.save(commit=False)
                user.username = nocuenta
                user = form.save()

                tipousuario = form.cleaned_data['tipousuario']
                if tipousuario == 'proveedor':
                    add_to_group = Group.objects.get(name='proveedor')
                elif tipousuario == 'administrador':
                    add_to_group = Group.objects.get(name='administrador')
                else:
                    add_to_group = Group.objects.get(name='usuario_c')

                add_to_group.user_set.add(user)
                add_to_group.save()

                messages.success(request, 'Acción exitosa.')
                return redirect('usuarios')
    else:
        form = UserRegistrationForm()
    return render(request, 'usuarios/registrar.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def usuarios(request):
    """
    Muestra una lista de usuarios no ocultos, excluyendo al usuario actual.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con la lista de usuarios no ocultos.
    """
    keyword = request.GET.get('keyword', '')
    
    usuario_actual = request.user
    usuarios = []
    
    if keyword:
        print('KEYWORD', keyword)
        usuarios = Usuario.objects.filter( 
            Q(oculto=False) & 
            ( Q(nombre__icontains=keyword) | Q(nocuenta__icontains=keyword) | Q(email__icontains=keyword) )
        ).exclude(user=usuario_actual)
    else:
        usuarios = Usuario.objects.filter(oculto=False).exclude(user=usuario_actual)
        
    # print('QUERY', usuarios.query)
    
    return render(request, 'usuarios/index.html', {'usuarios': usuarios, 'keyword': keyword})

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, nocuenta):
    """
    Permite al administrador editar la información de un usuario y cambiar su tipo de usuario si es necesario.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        nocuenta (str): Número de cuenta del usuario a editar.

    Returns:
        HttpResponse: Redirige a la vista de usuarios si el formulario es válido, o muestra el formulario de edición en caso contrario.
    """
    usuario = get_object_or_404(Usuario, nocuenta=nocuenta)
    user = usuario.user

    if request.method == 'POST':
        formulario = UserEditForm(request.POST, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            if request.POST.get('toggleTipousuario') == '1':
                nuevo_tipousuario = formulario.cleaned_data.get('tipousuario')
                grupo_actual = user.groups.first().name if user.groups.exists() else None

                if nuevo_tipousuario and nuevo_tipousuario != grupo_actual:
                    user.groups.clear()
                    if nuevo_tipousuario == 'proveedor':
                        add_to_group = Group.objects.get(name='proveedor')
                    elif nuevo_tipousuario == 'administrador':
                        add_to_group = Group.objects.get(name='administrador')
                    else:
                        add_to_group = Group.objects.get(name='usuario_c')
                    
                    add_to_group.user_set.add(user)

            return redirect('usuarios')
    else:
        formulario = UserEditForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {'formulario': formulario, 'usuario': usuario})

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, nocuenta):
    """
    Permite al administrador ocultar un usuario, en lugar de eliminarlo permanentemente.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.
        nocuenta (str): Número de cuenta del usuario a ocultar.

    Returns:
        HttpResponse: Redirige a la vista de usuarios.
    """
    usuario = Usuario.objects.get(nocuenta=nocuenta)
    usuario_django = User.objects.get(username=nocuenta)
    usuario_ha_rentado = Renta.objects.filter(id_deudor=usuario_django)
    rentas_activas = Renta.objects.filter(id_deudor=usuario_django).filter(fecha_devuelto__isnull=True)
    
    if usuario_ha_rentado:     
        if not rentas_activas:
            usuario.oculto = True
            usuario.save()
            messages.success(request, f'Se ha eliminado el usuario {nocuenta}.')
        else:
            messages.warning(request, f'No se puede eliminar al usuario deudor {nocuenta}.')
    else:
        usuario.oculto = True
        usuario.save()
        messages.success(request, f'Se ha eliminado el usuario {nocuenta}.')
        
    return redirect('usuarios')

def acumular_puntos(request, nocuenta):
    """
    Acumula puntos para un usuario en función de su actividad realizada.
    """
    usuario = Usuario.objects.get(nocuenta=nocuenta)
    if request.method == 'POST':
        form = AcumularPuntosForm(request.POST)
        if form.is_valid():
            # Traemos todos los registros del usuario de este mes
            registros = Acumulacion.objects.filter(
                usuario=usuario,
                fecha__month=datetime.now().month,
                fecha__year=datetime.now().year
            )
            acumulado = sum(registro.puntos for registro in registros)
            if acumulado >= 500:
                messages.error(request, 'Ya has alcanzado el límite de puntos acumulables por mes.')

            form.save(usuario)
            messages.success(request, 'Puntos acumulados exitosamente.')
    else:
        form = AcumularPuntosForm()
    return render(request, 'usuarios/acumular_puntos.html', {'form': form})
   

def perfil(request):
    usuario_actual = request.user
    usuario = Usuario.objects.get(user=usuario_actual)
    try:
        rentas = Renta.objects.filter(id_deudor=usuario_actual).filter(fecha_devuelto__isnull=True)
    except Renta.DoesNotExist:
        rentas = None
        
    rentas_activas = []

    for renta in rentas:
        objeto_rentado = renta.id_producto
        fecha_devolucion = renta.fecha_prestamo + dt.timedelta(days=objeto_rentado.dias)
        rentas_activas.append({'renta':renta, 'fecha_devolucion':fecha_devolucion})
        
    hoy = datetime.now()
    puntos_del_mes = 0
    try:
        rentas_historicas = Renta.objects.filter(id_deudor=usuario_actual)
    except Renta.DoesNotExist:
        rentas = None
    
    for renta in rentas_historicas:
        objeto_rentado = renta.id_producto
        if renta.fecha_prestamo.month == hoy.month:
            puntos_del_mes += int(objeto_rentado.costo / 2) 
    
    acumulaciones_del_mes = Acumulacion.objects.filter(usuario=usuario).filter(fecha__year=hoy.year, fecha__month=hoy.month)
    for acumulacion in acumulaciones_del_mes:
        puntos_del_mes+=acumulacion.puntos
    
    if len(usuario.nocuenta) == 9:
        es_estudiante = True
    else:
        es_estudiante = False
        
    if usuario_actual.groups.filter(name='proveedor').exists():
        es_proveedor = True
    else:
        es_proveedor = False
    
    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    is_prov = request.user.groups.filter(name='proveedor').exists()

    return render(request, 'usuarios/perfil.html', 
                  {'usuario':usuario, 
                   'puntos_del_mes':puntos_del_mes,
                   'es_estudiante':es_estudiante, 
                   'es_proveedor':es_proveedor,
                   'rentas_activas':rentas_activas,
                   'is_usuario_c': is_usuario_c,
                   'is_prov': is_prov,
                   'is_adminn': is_adminn
                   })

@login_required
def historial(request):
    usuario_actual = request.user
    historial_data = []

    hoy = datetime.now()
    primer_dia_mes = hoy.replace(day=1)
    if hoy.month == 12:
        primer_dia_siguiente_mes = hoy.replace(year=hoy.year + 1, month=1, day=1)
    else:
        primer_dia_siguiente_mes = hoy.replace(month=hoy.month + 1, day=1)

    rentas = Renta.objects.filter(
        id_deudor=usuario_actual,
        fecha_prestamo__gte=primer_dia_mes,
        fecha_prestamo__lt=primer_dia_siguiente_mes
    )

    for renta in rentas:
        producto = renta.id_producto
        fecha_devolucion = renta.fecha_prestamo + timedelta(days=producto.dias)

        historial_data.append({
            'nombre': producto.nombre,
            'costo': producto.costo,
            'descripcion': producto.descripcion,
            'imagen': producto.imagen.url if producto.imagen else None,
            'categoria': producto.categoria,
            'dias': producto.dias,
            'fecha_prestamo': renta.fecha_prestamo,
            'fecha_devolucion': fecha_devolucion,
        })

    is_usuario_c = request.user.groups.filter(name='usuario_c').exists()
    is_adminn = request.user.groups.filter(name='administrador').exists()
    is_prov = request.user.groups.filter(name='proveedor').exists()

    return render(request, 'usuarios/historial.html',
                 {'historial_data': historial_data,
                   'is_usuario_c': is_usuario_c,
                   'is_prov': is_prov,
                   'is_adminn': is_adminn})

@login_required
@user_passes_test(is_admin)
def reporte_usuarios_activos(request):
    """
    Reporta la cantidad de usuarios activos por carrera.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP

    Returns:
        HttpResponse: Redirige a la vista del reporte
    """
    carreras = {
        'actuaria': 0,
        'biologia': 0,
        'computacion': 0,
        'tierra': 0,
        'fisica': 0,
        'biomedica': 0,
        'matematicas': 0,
        'aplicadas': 0
    }
    
    for carrera in carreras.keys():
        carreras[carrera] = usuarios_carrera(carrera)

    datos = [[carrera, cantidad] for carrera, cantidad in carreras.items()]
    vista = 'reportes/datos_reporte.html'
    contexto = {'datos': datos,
                'titulo': 'Usuarios activos por carrera',
                'subtitulo': 'Cantidad de usuarios activos por carrera',
                'encabezados': ['Carrera','Cantidad']
                }
    return render(request, vista, contexto)

def usuarios_carrera(carrera):
    """
    Método auxiliar que devuelve la cantidad de usuarios
    activos que pertenecen a la carrera especificada.
    """
    return Usuario.objects.filter(area=carrera, oculto=False).count()

@login_required
@user_passes_test(is_admin)
def reporte_productos_baratos(request):
    """
    Reporta los productos ordenandolos segun su costo de menor a mayor
    
    Args:
        request (HttpRequest): Objeto de la solicitud HTTP
    
    Returns:
        HttpResponse: Redirige a la vista del reporte
    """
    productos = Producto.objects.all().order_by('costo')
    datos = [[producto.nombre, producto.costo] for producto in productos]
    vista = 'reportes/datos_reporte.html'
    contexto = {'datos': datos,
                'titulo': 'Productos de menor costo',
                'subtitulo': 'Productos que requieren menor cantidad de puntos para ser canjeados',
                'encabezados': ['producto','puntos']
                }
    return render(request, vista, contexto)

@login_required
@user_passes_test(is_admin)
def reporte_usuarios_tardios(request):
    """
    Reporta los 10 usuarios que mas veces han devuelto
    un producto tarde

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP

    Returns:
        HttpResponse: Redirige a la vista del reporte
    """
    rentas_tardias = Renta.objects.filter(fecha_devuelto__isnull = False)
    usuarios_tardios = {}
    for renta in rentas_tardias:
        limite = renta.fecha_prestamo + dt.timedelta(days=renta.id_producto.dias)
        if renta.fecha_devuelto > limite:
            usuario = renta.id_deudor.usuario
            if usuario.nocuenta not in usuarios_tardios:
                usuarios_tardios[usuario.nocuenta] = 0
            usuarios_tardios[usuario.nocuenta] += 1

    # Ordenamos los usuarios por la cantidad de devoluciones tardias
    # x[0]: usuario, x[1]: cantidad de devoluciones tardias
    usuarios_tardios_ordenados = sorted(usuarios_tardios.items(), key=lambda x: x[1], reverse=True)[:10]

    datos = [[usuario, cantidad] for usuario, cantidad in usuarios_tardios_ordenados]

    vista = 'reportes/datos_reporte.html'
    contexto = {
        'titulo': 'Usuarios morosos',
        'subtitulo': 'Usuarios con más devoluciones tardías',
        'encabezados': ['No. Cuenta/Trabajador', 'Cantidad de devoluciones tardías'],
        'datos': datos
    }
    return render(request, vista, contexto)

@login_required
@user_passes_test(is_admin)
def reporte_productos_mas_rentados(request):
    """
    Reporta los 5 productos más rentados del mes.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista del reporte.
    """
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # Filtrar las rentas del mes actual
    productos_rentados = Producto.objects.filter(
        rentas__fecha_prestamo__month=mes_actual,
        rentas__fecha_prestamo__year=anio_actual
    ).annotate(
        cantidad_rentas=Count('rentas')
    ).order_by('-cantidad_rentas')[:5]
    
    # Generar la lista de datos para el template
    datos = [[producto.nombre, producto.cantidad_rentas] for producto in productos_rentados]
    
    vista = 'reportes/datos_reporte.html'
    contexto = {
        'datos': datos,
        'titulo': 'Productos más rentados del mes',
        'subtitulo': 'Los 5 productos más rentados del mes',
        'encabezados': ['Producto', 'Cantidad de rentas']
    }
    return render(request, vista, contexto)

@login_required
@user_passes_test(is_admin)
def reporte_cantidad_cuentas_inactivas(request):
    """
    Reporta la cantidad de cuentas inactivas.
    Tambien enlista dichas cuentas
    Args:
        request (HttpRequest): Objeto de la solicitud HTTP

    Returns:
        HttpResponse: Redirige a la vista del reporte
    """
    inactivos = Usuario.objects.filter(oculto=True)
    cantidad = inactivos.count()
    datos = [[usuario.nocuenta, usuario] for usuario in inactivos]
    vista = 'reportes/datos_reporte.html'
    contexto = {'datos': datos,
                'titulo': 'Usuarios inactivos',
                'subtitulo': 'Cantidad de usuarios inactivos',
                'encabezados': ['No. cuenta/Trabajador','Nombre'],
                'cantidad': cantidad
                }
    return render(request, vista, contexto)

@login_required
@user_passes_test(is_admin)
def reporte_usuarios_mas_activos(request):
    """
    Reporta los 5 usuarios con mayor cantidad de 
    productos rentados.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Redirige a la vista del reporte.
    """
    # Obtener los usuarios con mas rentas, uniendo con la tabla User y Usuario
    usuarios = (
        Renta.objects.values('id_deudor__usuario__nocuenta', 'id_deudor__usuario__nombre')
        .annotate(cantidad_rentas=Count('id'))
        .order_by('-cantidad_rentas')[:5]
    )

    # Preparar los datos para el template
    datos = [
        [usuario['id_deudor__usuario__nocuenta'], usuario['id_deudor__usuario__nombre'], usuario['cantidad_rentas']]
        for usuario in usuarios
    ]
    vista = 'reportes/datos_reporte.html'
    contexto = {
        'datos': datos,
        'titulo': 'Usuarios más activos',
        'subtitulo': 'Usuarios con mayor cantidad de productos rentados',
        'encabezados': ['No. Cuenta/Trabajador', 'Nombre del Usuario', 'Cantidad de productos rentados']
    }

    return render(request, vista, contexto)

def reportes_menu(request):
    """
    Despliega un menu de reportes para el administrador.

    Args:
        request (HttpRequest): Objeto de la solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el menú de reportes.
    """
    reportes = [
        {
            'nombre': 'Reporte de cuentas activas por carrera',
            'nombre_url': 'reporte_usuarios_activos',
            'descripcion': 'Muestra todos los estudiantes activos en el sistema'
        },
        {
            'nombre': 'Reporte de productos con menor costo',
            'nombre_url': 'reporte_productos_baratos',
            'descripcion': 'Muestra los productos que requieren menos puntos para ser canjeados'
        },
        {
            'nombre': 'Reporte de los 10 usuarios mas incumplidos',
            'nombre_url': 'reporte_tardios',
            'descripcion': 'Lista a los 10 usuarios con mas devoluciones tardias'
        },
        {
            'nombre': 'Reporte de Productos mas rentados',
            'nombre_url': 'reporte_mas_rentados',
            'descripcion': 'Muestra los 5 productos mas rentados del mes'
        },
        {
            'nombre': 'Reporte de cuentas inactivas',
            'nombre_url': 'reporte_usuarios_inactivos',
            'descripcion': 'Muestra la cantidad de cuentas inactivas'
        },
        {
            'nombre': 'Reporte de los 5 usuarios mas activos',
            'nombre_url': 'reporte_usuarios_mas_activos',
            'descripcion': 'Lista a los 5 usuarios con mayor cantidad de productos rentados'
        },
    ]

    return render(request, 'reportes/menu.html', {'reportes': reportes})
