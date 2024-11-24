from django.shortcuts import render, redirect
from Productos.models import *
from Empleados.models import *
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from datetime import timedelta, datetime
from django.contrib import messages
from django.db.models.functions import ExtractMonth
from Empleados.views import * 
@login_required
def panel_venta(request):
    caja_abierta = Caja.objects.filter(empleado=request.user, estado='Abierta').first()
    if caja_abierta:
        lista_productos = Producto.objects.all()
        formulario_metodoPago = Formulario_MetodoPago()
        contexto = {'lista_productos': lista_productos, 'formulario_metodoPago': formulario_metodoPago}
        id_venta = request.session.get('id_venta')
        if id_venta:
            try:
                venta = Venta.objects.get(id=id_venta)
                contexto.update({'venta': venta})

                lista_venta = venta.productos_vendidos_set.all()
                if lista_venta:
                    contexto.update({'lista_venta': lista_venta})
                    venta.total_venta = sum(producto.subtotal for producto in lista_venta)
                    venta.save()
                else:
                    venta.delete()
                    request.session.pop('id_venta', None)
                    messages.info(request, "No hay productos en la venta, la venta ha sido eliminada.")
            except Venta.DoesNotExist:
                request.session.pop('id_venta', None)
                messages.warning(request, "La venta no existe, se ha limpiado la sesión.")

        return render(request, 'ventas.html', contexto)
    else:
        return redirect('apertura')

@login_required
def cancelar_venta(request):
    id_venta = request.session.get('id_venta', None)
    if id_venta:
        try:
            venta = Venta.objects.get(id=id_venta)
            venta.productos_vendidos_set.all().delete() 
            venta.delete()
            request.session.pop('id_venta', None)
            request.session.pop('id_cliente', None)
            messages.success(request, "Venta cancelada exitosamente.")
        except Venta.DoesNotExist:
            messages.error(request, "No se encontró la venta a cancelar.")
    return redirect('panel_venta')
def agregar_producto(request,id_producto):
    producto = Producto.objects.get(id=id_producto)
    id_venta=request.session.get('id_venta')
    if id_venta:
        try:
            venta = Venta.objects.get(id=id_venta)
        except: pass
    else:
        venta = Venta.objects.create()
        request.session['id_venta'] = venta.id

    if request.method == 'POST':
        cantidad=int(request.POST.get('cantidad'))
        producto_a_vender,creado=venta.productos_vendidos_set.get_or_create(producto=producto)
        producto_a_vender.cantidad+=cantidad
        producto_a_vender.subtotal=producto_a_vender.cantidad*producto.precio
        producto_a_vender.save()

        producto.existencias-=cantidad
        producto.save()

    return redirect('panel_venta')

def eliminar_producto_venta(request, id_producto):
    id_venta = request.session.get('id_venta')
    venta = Venta.objects.get(id=id_venta)
    producto_a_eliminar = Producto.objects.get(id=id_producto)
    producto_en_venta = venta.productos_vendidos_set.get(producto=producto_a_eliminar)
    subtotal_eliminado = producto_en_venta.producto.precio * producto_en_venta.cantidad
    venta.productos.remove(producto_a_eliminar)
    producto_a_eliminar.existencias += producto_en_venta.cantidad
    producto_a_eliminar.save()
    venta.total_venta -= subtotal_eliminado
    venta.save()
    return redirect('panel_venta')

def crear_factura(request):
    venta=Venta.objects.get(id=request.session.get('id_venta'))
    if request.method == 'POST':
        formulario_metodoPago=Formulario_MetodoPago(request.POST, instance=venta)
        if formulario_metodoPago.is_valid():
            formulario_metodoPago.save()
    venta.fecha=datetime.now()
    venta.empleado=Empleado.objects.get(username=request.user.username)
    venta.id_sesion=request.session.session_key
    venta.save()
    productos_a_vender=venta.productos_vendidos_set.all()
    request.session.pop('id_venta',None)
    return render(request,'factura.html',{'venta':venta,'productos_a_vender':productos_a_vender})

@user_passes_test(is_admin)
def grafico_ventas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')

    current_year = datetime.now().year
    anios = list(range(current_year - 10, current_year + 1))
    meses_disponibles = Venta.objects.annotate(mes=ExtractMonth('fecha')).values_list('mes', flat=True).distinct().order_by('mes')

    efectivo_vta = 0
    transferencia_vta = 0
    tarjeta_debito_vta = 0
    tarjeta_credito_vta = 0
    periodoVta = []

    if 'filtro' in request.GET:
        filtro = request.GET.get('filtro')

        if filtro == 'fechas':
            if not fecha_inicio or not fecha_fin:
                messages.error(request, 'Debe seleccionar un rango de fechas válido.')
            else:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
                if fecha_inicio > fecha_fin:
                    fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
                    messages.info(request, "Fechas invertidas para poder realizar la búsqueda.")
                periodoVta = [(fecha_inicio + timedelta(days=x)).strftime('%Y-%m-%d') for x in range((fecha_fin - fecha_inicio).days + 1)]
                ventas = Venta.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

                efectivo_vta = int(ventas.filter(metodo_pago='Efectivo').aggregate(total=Sum('total_venta'))['total'] or 0)
                transferencia_vta = int(ventas.filter(metodo_pago='Transferencia').aggregate(total=Sum('total_venta'))['total'] or 0)
                tarjeta_debito_vta = int(ventas.filter(metodo_pago='Tarjeta_de_Debito').aggregate(total=Sum('total_venta'))['total'] or 0)
                tarjeta_credito_vta = int(ventas.filter(metodo_pago='Tarjeta_de_Credito').aggregate(total=Sum('total_venta'))['total'] or 0)

        elif filtro == 'mes':
            if not mes:
                messages.error(request, 'Debe seleccionar un mes.')
            else:
                mes = int(mes)
                anio= int(current_year)
                ventas = Venta.objects.filter(fecha__month=mes)
                periodoVta = [f"{anio}-{mes:02d}"] if anio else []
                efectivo_vta = int(ventas.filter(metodo_pago='Efectivo').aggregate(total=Sum('total_venta'))['total'] or 0)
                transferencia_vta = int(ventas.filter(metodo_pago='Transferencia').aggregate(total=Sum('total_venta'))['total'] or 0)
                tarjeta_debito_vta = int(ventas.filter(metodo_pago='Tarjeta_de_Debito').aggregate(total=Sum('total_venta'))['total'] or 0)
                tarjeta_credito_vta = int(ventas.filter(metodo_pago='Tarjeta_de_Credito').aggregate(total=Sum('total_venta'))['total'] or 0)

        elif filtro == 'anio':
            if not anio:
                messages.error(request, 'Debe seleccionar un año.')
            else:
                anio = int(anio)
                ventas = Venta.objects.filter(fecha__year=anio)
                periodoVta = [str(anio)]
                efectivo_vta = int(ventas.filter(metodo_pago='Efectivo').aggregate(total=Sum('total_venta'))['total'] or 0)
                transferencia_vta = int(ventas.filter(metodo_pago='Transferencia').aggregate(total=Sum('total_venta'))['total'] or 0)
                tarjeta_debito_vta = int(ventas.filter(metodo_pago='Tarjeta_de_Debito').aggregate(total=Sum('total_venta'))['total'] or 0)
                tarjeta_credito_vta = int(ventas.filter(metodo_pago='Tarjeta_de_Credito').aggregate(total=Sum('total_venta'))['total'] or 0)

    context = {
        'periodoVta': periodoVta,
        'efectivo_vta': efectivo_vta,
        'transferencia_vta': transferencia_vta,
        'tarjeta_debito_vta': tarjeta_debito_vta,
        'tarjeta_credito_vta': tarjeta_credito_vta,
        'meses': meses_disponibles,
        'anios': anios,
        'mes': mes,
        'anio': anio
    }
    return render(request, 'grafico_ventas.html', context)