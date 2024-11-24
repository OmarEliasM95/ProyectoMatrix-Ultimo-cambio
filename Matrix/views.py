from django.shortcuts import render,redirect
from Compras.models import *
from Productos.models import *
from Ventas.models import *
from Gastos.models import *
from Caja.models import * 
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib import messages
from datetime import datetime,timedelta 

def error_400(request, exception):
    if settings.DEBUG:
        return render(request, '400.html', status=400)
    return render(request, '400.html', status=400)

def error_403(request, exception):
    if settings.DEBUG:
        return render(request, '403.html', status=403)
    return render(request, '403.html', status=403)

def error_404(request, exception):
    if settings.DEBUG:
        return render(request, '404.html', status=404)
    return render(request, '404.html', status=404)

def error_500(request):
    if settings.DEBUG:
        return render(request, '500.html', status=500)
    return render(request, '500.html', status=500)

@login_required
def menu(request):
    caja_abierta = Caja.objects.filter(empleado=request.user, estado='Abierta').first()
    if caja_abierta:  
        fecha_apertura = caja_abierta.fecha_apertura  
        empleado = caja_abierta.empleado 
    else:
        fecha_apertura = None
        empleado = None
    #GRAFICO CAJA
    ventas_por_mes= []
    compras_por_mes=[]
    gastos_por_mes=[]
    ingresos_por_mes=[]
    egresos_por_mes= []
    for mes in range(1,13):
        ventas_mes=Venta.objects.filter(fecha__month=mes)
        total_ventas=int(ventas_mes.aggregate(total=Sum('total_venta'))['total'] or 0) 
        ventas_por_mes.append(total_ventas)
        compras_mes= Compra.objects.filter(fecha_compra__month=mes)
        total_compras= int(compras_mes.aggregate(total=Sum('total'))['total'] or 0 )
        compras_por_mes.append(total_compras)
        gastos_mes= Gasto.objects.filter(fecha__month=mes)
        total_gastos= int(gastos_mes.aggregate(total=Sum('costo'))['total'] or 0 )
        gastos_por_mes.append(total_gastos)
        ingresos_mes=Dinero.objects.filter(tipo_dinero='Ingreso',fecha_dinero__month=mes)
        total_ingresos= int(ingresos_mes.aggregate(total=Sum('ing_egre'))['total'] or 0)
        ingresos_por_mes.append(total_ingresos)
        egresos_mes= Dinero.objects.filter(tipo_dinero='Egreso',fecha_dinero__month=mes)
        total_egresos= int(egresos_mes.aggregate(total=Sum('ing_egre'))['total'] or 0 ) 
        egresos_por_mes.append(total_egresos) 
    #GRAFICO COMPRAS
    compras_efectivo= []
    compras_transferencia=[]
    compras_debito= []
    for mes in range (1,13):
        compras_efectivo_mes= Compra.objects.filter(fecha_compra__month=mes,metodo_pago= 'Efectivo')
        compras_transferencia_mes= Compra.objects.filter(fecha_compra__month=mes,metodo_pago= 'Transferencia')
        compras_debito_mes= Compra.objects.filter(fecha_compra__month=mes,metodo_pago= 'Tarjeta_de_Debito')
        comprasEfectivo= int(compras_efectivo_mes.aggregate(total=Sum('total'))['total'] or 0)
        comprasTransf= int(compras_transferencia_mes.aggregate(total=Sum('total'))['total'] or 0)
        comprasDebito= int(compras_debito_mes.aggregate(total=Sum('total'))['total'] or 0)
        compras_efectivo.append(comprasEfectivo)
        compras_transferencia.append(comprasTransf)
        compras_debito.append(comprasDebito)

    #GRAFICO VENTAS
    ventas_efectivo=[]
    ventas_credito=[]
    ventas_debito=[]
    ventas_transferencia=[]
    for mes in range(1,13):
        ventas_efectivo_mes= Venta.objects.filter(fecha__month=mes,metodo_pago='Efectivo')
        ventas_transferencia_mes= Venta.objects.filter(fecha__month=mes,metodo_pago='Transferencia')
        ventas_credito_mes= Venta.objects.filter(fecha__month=mes,metodo_pago='Tarjeta_de_Credito')
        ventas_debito_mes= Venta.objects.filter(fecha__month=mes,metodo_pago='Tarjeta_de_Debito')
        ventasEfectivo= int(ventas_efectivo_mes.aggregate(total=Sum('total_venta'))['total'] or 0)
        ventasTransferencia= int(ventas_transferencia_mes.aggregate(total=Sum('total_venta'))['total'] or 0)
        ventasDebito= int(ventas_debito_mes.aggregate(total=Sum('total_venta'))['total'] or 0)
        ventasCredito= int(ventas_credito_mes.aggregate(total=Sum('total_venta'))['total'] or 0)
        ventas_efectivo.append(ventasEfectivo)
        ventas_transferencia.append(ventasTransferencia)
        ventas_debito.append(ventasDebito)
        ventas_credito.append(ventasCredito)
    
    #GRAFICO EGRESOS VS INGRESOS
    ingresos_mes=[]
    egresos_mes=[]
    for mes in range(1,13):
        venta_mes= Venta.objects.filter(fecha__month=mes).aggregate(total=Sum('total_venta'))['total'] or 0 
        compra_mes= Compra.objects.filter(fecha_compra__month=mes).aggregate(total=Sum('total'))['total'] or 0
        gasto_mes=Gasto.objects.filter(fecha__month=mes).aggregate(total=Sum('costo'))['total'] or 0
        ingreso_mes= Dinero.objects.filter(fecha_dinero__month=mes,tipo_dinero='Ingreso').aggregate(total=Sum('ing_egre'))['total'] or 0 
        egreso_mes= Dinero.objects.filter(fecha_dinero__month=mes,tipo_dinero='Egreso').aggregate(total=Sum('ing_egre'))['total'] or 0 
        venta_mes=int(venta_mes)
        compra_mes= int(compra_mes)
        gasto_mes=int(gasto_mes)
        ingreso_mes=int(ingreso_mes)
        egreso_mes= int(egreso_mes)
        total_ingreso= venta_mes+ ingreso_mes
        total_egreso= gasto_mes+compra_mes+egreso_mes
        ingresos_mes.append(total_ingreso)
        egresos_mes.append(total_egreso)

    productos=Producto.objects.all()
    faltantes=[]
    for producto in productos:
        if producto.stock_minimo>=producto.existencias:
            faltantes.append({
                'nombre':producto.nombre,'existencias':producto.existencias,'stock_minimo': producto.stock_minimo
            })
    if faltantes:
        mensaje_faltantes = "Productos faltantes:\n" + "\n•".join([f"{f['nombre']} (Stock actual: {f['existencias']}, Stock mínimo: {f['stock_minimo']})" for f in faltantes])
        messages.info(request, mensaje_faltantes)
    #productos ingresados 
    fecha_hoy= datetime.now()
    lunes_semana= fecha_hoy - timedelta(days=fecha_hoy.weekday())
    productos_semana= Producto.objects.filter(fecha_ingreso__gte=lunes_semana,fecha_ingreso__lte=fecha_hoy)

    contexto= {
        'ventas_por_mes': ventas_por_mes,
        'compras_por_mes': compras_por_mes,
        'gastos_por_mes':gastos_por_mes,
        'ingresos_por_mes': ingresos_por_mes,
        'egresos_por_mes':egresos_por_mes,
        'compras_efectivo':compras_efectivo,
        'compras_transferencia':compras_transferencia,
        'compras_debito':compras_debito,
        'ventas_efectivo':ventas_efectivo,
        'ventas_credito':ventas_credito,
        'ventas_debito':ventas_debito,
        'ventas_transferencia':ventas_transferencia,
        'ingresos_mes': ingresos_mes,
        'egresos_mes': egresos_mes,
        'faltantes':faltantes,
        'productos_semana':productos_semana,
    }
    return render(request, 'ingreso.html',contexto)
@login_required
def historial_compras(request):
    historial_compras=Compra.objects.all().order_by('id')
    paginator= Paginator(historial_compras,10)
    page_number=request.GET.get('page')
    page_obj= paginator.get_page(page_number)
    return render(request,'historial_compras.html', {'historial_compras':historial_compras,'page_obj':page_obj})

def ver_detalle_compra(request, id_compras):
    compra=Compra.objects.get(id=id_compras)
    producto_comprados=compra.compra_intermedio_set.all()
    return render(request,'ver_detalle_compra.html', {'productos_comprados':producto_comprados})
@login_required
def historial_ventas(request):
    historial_ventas=Venta.objects.all().order_by('id')
    paginator=Paginator(historial_ventas,10)
    page_number=request.GET.get('page')
    page_obj= paginator.get_page(page_number)
    return render(request,'historial_ventas.html',{'historial_ventas':historial_ventas,'page_obj':page_obj})
def ver_detalle_venta(request, id_ventas):
    venta=Venta.objects.get(id=id_ventas)
    productos_vendidos=venta.productos_vendidos_set.all()
    return render(request,'ver_detalle_venta.html',{'productos_vendidos':productos_vendidos})
@login_required
def panel_historial(request):
    return render(request,'historiales.html')

def historial_gastos(request):
    historial_gastos=Gasto.objects.all().order_by('id')
    paginator=Paginator(historial_gastos,10)
    page_number=request.GET.get('page')
    page_obj= paginator.get_page(page_number)
    return render(request,'historial_gastos.html',{'historial_gastos':historial_gastos,'page_obj':page_obj})
def historial_ingresos_egresos(request):
    ingresos_egresos=Dinero.objects.all().order_by('id')
    paginator=Paginator(ingresos_egresos,10)
    page_number=request.GET.get('page')
    page_obj= paginator.get_page(page_number)
    return render(request,'historial_ingresos_egresos.html',{'ingresos_egresos':ingresos_egresos,'page_obj':page_obj})
