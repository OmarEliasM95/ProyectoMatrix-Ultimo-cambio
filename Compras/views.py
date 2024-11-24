from django.shortcuts import render, redirect
from .models import *
from Productos.models import *
from Proveedores.models import *
from Empleados.models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,Count
from datetime import datetime, timedelta
from django.contrib import messages
from django.db.models.functions import ExtractMonth
from Caja.views import * 
from Caja.models import * 
from Gastos.models import Gasto
from django.contrib.auth.decorators import user_passes_test
from Empleados.views import *
@login_required
def panel_compras(request):
    id_proveedor = request.session.get('id_proveedor', None)
    id_compra = request.session.get('id_compra', None)
    
    if not Compra.objects.exists():
        request.session.pop('id_compra', None)
    
    if id_proveedor:
        proveedor = Proveedor.objects.get(id=id_proveedor)
        formulario_proveedor = Formulario_Proveedor({'proveedor': id_proveedor})
        lista_productos_proveedor = Producto_Intermedia.objects.filter(proveedor=proveedor)
        contexto = {
            'formulario_proveedor': formulario_proveedor,
            'lista_productos_proveedor': lista_productos_proveedor,
            'proveedor': proveedor  
        }
    else:
        formulario_proveedor = Formulario_Proveedor()
        contexto = {'formulario_proveedor': formulario_proveedor}
    
    formulario_metodo_pago = Formulario_MetodoPago()
    contexto.update({'formulario_metodo_pago': formulario_metodo_pago})
    
    if id_compra:
        compra = Compra.objects.get(id=id_compra)  
        lista_compra = compra.compra_intermedio_set.all()
        if lista_compra:
            total_compra = sum(producto.precio_de_compra * producto.cantidad for producto in lista_compra)
            compra.total = total_compra
            compra.save()
            subtotal = total_compra
            contexto.update({'compra': compra, 'lista_compra': lista_compra, 'subtotal': subtotal})
        else: 
            compra.delete() 
            request.session.pop('id_compra', None)
    
    return render(request, 'compras.html', contexto)

@login_required
def cancelar_compra(request):
    id_compra = request.session.get('id_compra', None)
    if id_compra:
        try:
            compra = Compra.objects.get(id=id_compra)
            compra.compra_intermedio_set.all().delete()
            compra.delete()
            request.session.pop('id_compra', None)
            request.session.pop('id_proveedor', None)
            messages.success(request, "Compra cancelada exitosamente.")
        except Compra.DoesNotExist:
            messages.error(request, "No se encontró la compra a cancelar.")
    return redirect('panel_compras')
def seleccionar_proveedor(request):
    if request.method == 'POST':
        proveedor_seleccionado = Formulario_Proveedor(request.POST)
        if proveedor_seleccionado.is_valid():
            id_proveedor = proveedor_seleccionado.instance.proveedor.id
            request.session['id_proveedor'] = id_proveedor
            id_compra = request.session.get('id_compra', None)
            if id_compra:
                try:
                    compra = Compra.objects.get(id=id_compra)
                    compra.proveedor = proveedor_seleccionado.instance.proveedor
                    compra.save()
                except Compra.DoesNotExist:
                    pass  
            return redirect('panel_compras')

@login_required
def agregar_producto_compra(request, id_producto):
    producto = Producto.objects.get(id=id_producto)
    id_compra = request.session.get('id_compra', None)    
    caja_abierta = obtener_caja_abierta(request.user)

    if not caja_abierta:
        request.session['caja_abierta'] = False
        return redirect('apertura')
    
    id_sesion = request.session.session_key
    lista_ventas = Venta.objects.filter(id_sesion=id_sesion)
    total_ventas = sum(venta.total_venta for venta in lista_ventas)

    lista_compras = Compra.objects.filter(id_sesion=id_sesion)
    total_compras = sum(compra.total for compra in lista_compras)
    
    lista_dinero = Dinero.objects.filter(id_sesion=id_sesion)
    dinero_ingreso = sum(dinero.ing_egre for dinero in lista_dinero if dinero.tipo_dinero == 'Ingreso')
    dinero_egreso = sum(dinero.ing_egre for dinero in lista_dinero if dinero.tipo_dinero == 'Egreso')
    
    lista_gastos= Gasto.objects.filter(id_sesion= id_sesion)
    gastos_compra= sum(gasto.costo for gasto in lista_gastos)
    
    saldo_final = total_ventas + caja_abierta.saldo_inicial -total_compras+dinero_ingreso- dinero_egreso-gastos_compra
    if id_compra:
        try:
            compra = Compra.objects.get(id=id_compra)
        except Compra.DoesNotExist:
            compra = Compra()
            proveedor = Proveedor.objects.get(id=request.session.get('id_proveedor'))
            compra.proveedor = proveedor
            compra.save()
    else:
        compra = Compra()
        id_proveedor = request.session.get('id_proveedor', None)
        proveedor = Proveedor.objects.get(id=id_proveedor)
        compra.proveedor = proveedor
        compra.save()
        request.session['id_compra'] = compra.id

    if request.method == 'POST':
        precio_compra = int(request.POST.get('precio_compra'))
        cantidad = int(request.POST.get('cantidad'))
        subtotal_nuevo_producto = precio_compra * cantidad
        total_compra_actual = sum(p.precio_de_compra * p.cantidad for p in compra.compra_intermedio_set.all())
        if total_compra_actual + subtotal_nuevo_producto > saldo_final:
            messages.error(request, f'Saldo insuficiente. Saldo disponible: ${saldo_final}')
            return redirect('panel_compras')        
        producto_a_comprar, created = compra.compra_intermedio_set.get_or_create(producto=producto)
        producto_a_comprar.cantidad += cantidad
        producto_a_comprar.precio_de_compra = precio_compra
        producto_a_comprar.subtotal = producto_a_comprar.cantidad * producto_a_comprar.precio_de_compra
        producto_a_comprar.save()
        total_compra = sum(p.precio_de_compra * p.cantidad for p in compra.compra_intermedio_set.all())
        compra.total = total_compra
        compra.save()
    return redirect('panel_compras')

def eliminar_producto_compra(request, id_producto):
    if request.method=='POST':
        id_compra = request.session.get('id_compra')
        compra = Compra.objects.get(id=id_compra)
        producto_a_eliminar = Compra_intermedio.objects.get(compra_id=id_compra, producto_id=id_producto)
        producto_a_eliminar.delete()
        return redirect('panel_compras')


def confirmar_compra(request):
    if request.method == 'POST':
        compra = Compra.objects.get(id=request.session.get('id_compra'))
        formulario_metodo_pago = Formulario_MetodoPago(request.POST, instance=compra)
        if formulario_metodo_pago.is_valid():
            formulario_metodo_pago.save()
            compra.empleado = Empleado.objects.get(username=request.user.username)
            compra.id_sesion = request.session.session_key
            compra.save()
            request.session.pop('id_compra')
            request.session.pop('id_proveedor')
        
        lista_productos_comprados = compra.compra_intermedio_set.all()
        for producto_comprado in lista_productos_comprados:
            producto = Producto.objects.get(id=producto_comprado.producto.id)
            producto.existencias += producto_comprado.cantidad
            producto.save()
        return redirect('panel_compras')


@user_passes_test(is_admin)
def grafico_compras(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    current_year = datetime.now().year

    meses = Compra.objects.annotate(mes=ExtractMonth('fecha_compra')).values_list('mes', flat=True).distinct().order_by('mes')
    anios = list(range(current_year - 10, current_year + 1))

    total_efectivo = 0
    total_transferencia = 0
    total_tarjeta_debito = 0
    periodo = []

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
                periodo = [(fecha_inicio + timedelta(days=x)).strftime('%Y-%m-%d') for x in range((fecha_fin - fecha_inicio).days + 1)]
                compras = Compra.objects.filter(fecha_compra__range=[fecha_inicio, fecha_fin])
                total_efectivo = int(compras.filter(metodo_pago='Efectivo').aggregate(total=Sum('total'))['total'] or 0)
                total_transferencia = int(compras.filter(metodo_pago='Transferencia').aggregate(total=Sum('total'))['total'] or 0)
                total_tarjeta_debito = int(compras.filter(metodo_pago='Tarjeta_de_Debito').aggregate(total=Sum('total'))['total'] or 0)

        elif filtro == 'mes':
            if not mes:
                messages.error(request, 'Debe seleccionar un mes.')
            else:
                mes = int(mes)
                anio = int(current_year)
                periodo = [f"{anio}-{mes:02d}"]
                compras = Compra.objects.filter(fecha_compra__year=anio, fecha_compra__month=mes)
                total_efectivo = int(compras.filter(metodo_pago='Efectivo').aggregate(total=Sum('total'))['total'] or 0)
                total_transferencia = int(compras.filter(metodo_pago='Transferencia').aggregate(total=Sum('total'))['total'] or 0)
                total_tarjeta_debito = int(compras.filter(metodo_pago='Tarjeta_de_Debito').aggregate(total=Sum('total'))['total'] or 0)

        elif filtro == 'anio':
            if not anio:
                messages.error(request, 'Debe seleccionar un año.')
            else:
                anio = int(anio)
                periodo = [str(anio)]
                compras = Compra.objects.filter(fecha_compra__year=anio)
                total_efectivo = int(compras.filter(metodo_pago='Efectivo').aggregate(total=Sum('total'))['total'] or 0)
                total_transferencia = int(compras.filter(metodo_pago='Transferencia').aggregate(total=Sum('total'))['total'] or 0)
                total_tarjeta_debito = int(compras.filter(metodo_pago='Tarjeta_de_Debito').aggregate(total=Sum('total'))['total'] or 0)

    return render(request, 'grafico_compras.html', {
        'total_efectivo': total_efectivo,
        'total_transferencia': total_transferencia,
        'total_tarjeta_debito': total_tarjeta_debito,
        'periodo': periodo,
        'meses': meses,
        'anios': anios,
    })
