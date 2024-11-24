from django.shortcuts import render,redirect
from .models import *
from Empleados import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Ventas.models import Venta
from Compras.models import Compra
from Caja.models import * 
from Caja.views import *
@login_required
def gasto_panel(request):
    caja_abierta = Caja.objects.filter(empleado=request.user, estado='Abierta').first()
    if caja_abierta:
        formulario=Formulario_Gasto()
        lista_gasto=Gasto.objects.filter(id_sesion=request.session.session_key)
        return render(request, 'gasto.html', {'formulario':formulario, 'lista_gasto':lista_gasto})
    else:
        return redirect('apertura')
@login_required
def agregar_gasto(request):
    if request.method == 'POST':
        caja_abierta= obtener_caja_abierta(request.user)
        formulario = Formulario_Gasto(request.POST)        
        if formulario.is_valid():
            id_sesion = request.session.session_key
            lista_ventas = Venta.objects.filter(id_sesion=id_sesion)
            total_ventas = sum(venta.total_venta for venta in lista_ventas)

            lista_compras = Compra.objects.filter(id_sesion=id_sesion)
            total_compras = sum(compra.total for compra in lista_compras)

            lista_dinero = Dinero.objects.filter(id_sesion=id_sesion)
            dinero_ingreso = sum(dinero.ing_egre for dinero in lista_dinero if dinero.tipo_dinero == 'Ingreso')
            dinero_egreso = sum(dinero.ing_egre for dinero in lista_dinero if dinero.tipo_dinero == 'Egreso')
            
            lista_gastos= Gasto.objects.filter(id_sesion=id_sesion)
            gastos_compra= sum(gasto.costo for gasto in lista_gastos)

            saldo_final= caja_abierta.saldo_inicial+total_ventas-total_compras+dinero_ingreso- dinero_egreso-gastos_compra
            monto_ingresado = formulario.cleaned_data.get('costo')
            if monto_ingresado is None or saldo_final is None:
                messages.error(request, 'Error al obtener los valores de saldo o monto ingresado.')
                return redirect('gasto_panel')

            if saldo_final < monto_ingresado:
                messages.error(request, f'Saldo insuficiente. Saldo disponible: ${saldo_final:.2f}')
                return redirect('gasto_panel')
            formulario.instance.id_sesion = request.session.session_key
            formulario.instance.empleado = Empleado.objects.get(username=request.user.username)
            formulario.save()

    return redirect('gasto_panel')
