from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Empleado
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group
from Caja.views import obtener_caja_abierta
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from Compras.models import Compra 
from Ventas.models import Venta 
from Caja.models import Caja, Dinero
from Gastos.models import Gasto
from django.http import JsonResponse
def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

def is_empleado(user):
    return user.groups.filter(name='Empleado').exists()

def login_empleado(request):
    if request.method == 'GET':
        formulario_login = AuthenticationForm()
        return render(request, 'login.html', {'formulario_login': formulario_login})
    if request.method == 'POST':
        formulario_login = AuthenticationForm(request, data=request.POST)
        if formulario_login.is_valid():
            usuario = formulario_login.cleaned_data.get('username')
            contraseña = formulario_login.cleaned_data.get('password')
            validacion = authenticate(username=usuario, password=contraseña)
            if validacion is not None:
                login(request, validacion)
                request.session['is_admin'] = validacion.groups.filter(name='Administrador').exists()
                request.session['role'] = 'Administrador' if request.session['is_admin'] else 'Empleado'
                caja_abierta = obtener_caja_abierta(validacion)
                if caja_abierta:
                    request.session['caja_abierta'] = True
                    request.session['empleado'] = caja_abierta.empleado.username
                    request.session['fecha_apertura'] = caja_abierta.fecha_apertura.strftime("%Y-%m-%d %H:%M:%S")
                return JsonResponse({'success': True, 'redirect_url': 'menu'})  
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html', {'formulario_login': formulario_login})

def logout_empleado(request):
    logout(request)
    request.session.pop('is_admin', None)
    request.session.pop('role', None)
    return redirect('login')


@login_required
def agregar_empleado(request):
    if request.method == 'GET':
        formulario_empleado = crear_empleado()
        grupos = Group.objects.all()
        return render(request, 'agregar_usuario.html', {'formulario_empleado': formulario_empleado, 'grupos': grupos}) 
    elif request.method == 'POST':
        formulario_empleado = crear_empleado(request.POST)
        if formulario_empleado.is_valid():
            nuevo_empleado = formulario_empleado.save()
            grupo_nombre = request.POST.get('group')
            if grupo_nombre:
                try:
                    grupo = Group.objects.get(name=grupo_nombre)
                    nuevo_empleado.groups.add(grupo)
                except Group.DoesNotExist:
                    messages.error(request, "El grupo no existe.")
            messages.success(request, "Usuario agregado con éxito")
            return redirect('panel_empleado')  
        else:
            messages.error(request, "Hubo un error al agregar el usuario. Por favor, revisa los campos.")
            return redirect('panel_empleado')  
@login_required
def editar_empleado(request, id_empleado):
    empleado_buscado = Empleado.objects.get(id=id_empleado)
    grupo_actual = empleado_buscado.groups.all()

    if request.method == 'GET':
        formulario_editar = formulario_empleado(instance=empleado_buscado)
        grupos = Group.objects.all()
        return render(request, 'editar_empleado.html', {
            'formulario_editar': formulario_editar, 
            'id_empleado': id_empleado, 
            'grupos': grupos,
            'grupo_actual': grupo_actual 
        })
    if request.method == 'POST':
        formulario_editar = formulario_empleado(request.POST, instance=empleado_buscado)
        if formulario_editar.is_valid():
            empleado_actualizado = formulario_editar.save()
            grupo_nombre = request.POST.get('group') 
            messages.success(request, "Empleado editado con éxito")
            if grupo_nombre:
                try:
                    grupo = Group.objects.get(name=grupo_nombre)
                    empleado_actualizado.groups.set([grupo])  
                except Group.DoesNotExist:
                    messages.error(request, "El grupo no existe.")
            else:
                empleado_actualizado.groups.clear()  
            return redirect('panel_empleado')  
@login_required
@user_passes_test(is_admin)
def panel_empleado(request):
    listado= Empleado.objects.all().order_by('last_name')
    #listado = Empleado.objects.exclude(id=request.user.id).order_by('last_name') EXCLUIR EL USUARIO QUE INICIÓ SESIÓN
    paginator = Paginator(listado, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    formulario_empleado = crear_empleado()
    return render(request, 'empleado.html', {'page_obj': page_obj, 'formulario_empleado': formulario_empleado})

def eliminar_empleado(request, id_empleado):
    empleado_buscado = get_object_or_404(Empleado, id=id_empleado)    
    asociaciones = []
    if Venta.objects.filter(empleado=empleado_buscado).exists():
        asociaciones.append("ventas")
    if Compra.objects.filter(empleado=empleado_buscado).exists():
        asociaciones.append("compras")
    if Caja.objects.filter(empleado=empleado_buscado).exists():
        asociaciones.append("cajas")
    if Dinero.objects.filter(empleado=empleado_buscado,tipo_dinero='Ingreso').exists():
        asociaciones.append("ingresos")
    if Dinero.objects.filter(empleado=empleado_buscado,tipo_dinero='Egreso').exists():
        asociaciones.append("egresos")
    if Gasto.objects.filter(empleado=empleado_buscado).exists():
        asociaciones.append("gastos")
    if asociaciones:
        asociaciones_texto = ", ".join(asociaciones)
        messages.error(
            request, 
            f"El empleado {empleado_buscado.username} tiene {asociaciones_texto} asociados y no puede ser eliminado."
        )
        return redirect('panel_empleado')
    empleado_buscado.delete()
    messages.success(request, "Empleado eliminado con éxito")
    return redirect('panel_empleado')

def cambiar_contraseña(request, id_empleado):
    empleado_buscado = Empleado.objects.get(id=id_empleado)
    if request.method=='POST':
        current_password= request.POST.get('current_password')
        new_password=request.POST.get('password')
        confirm_password= request.POST.get('password_confirm')
        if not check_password(current_password,empleado_buscado.password):
            error= "La contraseña actual es incorrecta."
            return JsonResponse({'success': False, 'error': error})
        if new_password !=confirm_password:
            error="Las nuevas contraseñas no coinciden."
            return JsonResponse({'success': False,'error':error})
        empleado_buscado.set_password(new_password)
        empleado_buscado.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})
@login_required
def panel_perfil(request):
    empleado = request.user
    cambiar_password = Cambiar_Password(instance=empleado)
    if request.method == 'POST':
        cambiar_password = Cambiar_Password(request.POST, instance=empleado)
        if cambiar_password.is_valid():
            empleado.set_password(cambiar_password.cleaned_data['password'])
            empleado.save()
            return JsonResponse({'success': True})
        else:
            error_messages = [msg for error in cambiar_password.errors.values() for msg in error]
            return JsonResponse({'success': False, 'error': ', '.join(error_messages)})
    return render(request, 'perfil.html', {'empleado': empleado, 'cambiar_password': cambiar_password})

def cambiar_clave(request, id_empleado):
    empleado_buscado = Empleado.objects.get(id=id_empleado)
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('password_confirm')

        if new_password != confirm_password:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
            return redirect('panel_empleado')
        
        empleado_buscado.set_password(new_password)
        empleado_buscado.save()
        messages.success(request, "Contraseña cambiada con éxito.")
        return redirect('panel_empleado')
    
    return render(request, 'cambiar_contraseña.html', {'id_empleado': id_empleado})
