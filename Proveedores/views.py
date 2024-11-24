from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 
from django.contrib import messages
from Productos.models import Producto_Intermedia
from Ventas.models import Venta
from Compras.models import Compra

def agregar_proveedor(request):
    if request.method == 'POST':
        proveedor_agregar = formulario_proveedor(request.POST)
        if proveedor_agregar.is_valid():
            nombre = proveedor_agregar.cleaned_data['nombre']
            telefono = proveedor_agregar.cleaned_data['telefono']
            email = proveedor_agregar.cleaned_data['email']
            direccion = proveedor_agregar.cleaned_data['dirección']
            if Proveedor.objects.filter(nombre=nombre).exists():
                messages.error(request, "Ya existe un proveedor con el mismo nombre.")
            elif Proveedor.objects.filter(telefono=telefono).exists():
                messages.error(request, "Ya existe un proveedor con el mismo teléfono.")
            elif Proveedor.objects.filter(email=email).exists():
                messages.error(request, "Ya existe un proveedor con el mismo email.")
            elif Proveedor.objects.filter(dirección=direccion).exists():
                messages.error(request, "Ya existe un proveedor con la misma dirección.")
            else:
                proveedor_agregar.save()
                messages.success(request, "Proveedor agregado con éxito.")
                return redirect('panel_proveedores')
    return redirect('panel_proveedores')
@login_required
def panel_proveedores(request):
    listado = Proveedor.objects.all().order_by('nombre')
    paginator=Paginator(listado,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    mostrar_formulario = formulario_proveedor()
    busqueda= request.GET.get('busqueda','')
    if busqueda:
        listado=listado.filter(
            Q(nombre__icontains=busqueda)
        )
    return render(request, 'proveedores.html', {'listado':listado, 'mostrar_formulario':mostrar_formulario,'page_obj':page_obj})

def eliminar_proveedor(request, id_proveedor):
    proveedor_buscado = get_object_or_404(Proveedor, id=id_proveedor)
    tiene_compras = Compra.objects.filter(proveedor=proveedor_buscado).exists()
    tiene_ventas = Venta.objects.filter(productos__proveedores=proveedor_buscado).exists()
    tiene_productos = Producto_Intermedia.objects.filter(proveedor=proveedor_buscado).exists()
    if tiene_compras or tiene_ventas or tiene_productos:
        asociaciones = []
        if tiene_compras:
            asociaciones.append("compras")
        if tiene_ventas:
            asociaciones.append("ventas")
        if tiene_productos:
            asociaciones.append("productos")
        
        asociaciones_texto = ", ".join(asociaciones)
        messages.error(
            request,
            f"El proveedor {proveedor_buscado.nombre} tiene {asociaciones_texto} asociados y no puede ser eliminado."
        )
        return redirect('panel_proveedores')
    proveedor_buscado.delete()
    messages.success(request, "Proveedor eliminado con éxito")
    return redirect('panel_proveedores')

def editar_proveedor(request, id_proveedor):
    proveedor_buscado=Proveedor.objects.get(id=id_proveedor)
    if request.method == 'GET':
        formulario_editar=formulario_proveedor(instance=proveedor_buscado)
        return render(request, 'editar_proveedor.html', {'formulario_editar':formulario_editar, 'id_proveedor':id_proveedor})
    if request.method == 'POST':
        formulario_editar=formulario_proveedor(request.POST, instance=proveedor_buscado)
        if formulario_editar.is_valid():
            formulario_editar.save()
            messages.success(request,"Proveedor editado con éxito.")
            return redirect('panel_proveedores')      