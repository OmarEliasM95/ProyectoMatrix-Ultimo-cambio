from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import formulario_producto
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from Compras.models import Compra_intermedio
from Ventas.models import Productos_Vendidos

def agregar_producto(request):
    if request.method == 'POST':
        producto_agregar = formulario_producto(request.POST)
        if producto_agregar.is_valid():
            producto_agregar.save()
            messages.success(request, "Producto agregado al inventario.")
        else:
            for field in producto_agregar.errors:
                for error in producto_agregar.errors[field]:
                    messages.error(request, error)
        return redirect('lista_producto')
    
    else:
        formulario_agregar = formulario_producto()
        return render(request, 'productos.html', {'formulario': formulario_agregar})

def lista_producto(request):
    listado = Producto_Intermedia.objects.all().order_by('producto__nombre')
    productos_unicos = set()
    productos_filtrados = []
    for item in listado:
        producto = item.producto
        if producto.id not in productos_unicos:
            productos_unicos.add(producto.id)
            productos_filtrados.append(item)
    paginator = Paginator(productos_filtrados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    mostrar_formulario = formulario_producto()
    return render(request, 'productos.html', {'listado': productos_filtrados, 'mostrar_formulario': mostrar_formulario, 'page_obj': page_obj})

def faltantes_producto(request):
    productos=Producto.objects.all()
    faltantes=[]
    for producto in productos:
        if producto.stock_minimo>=producto.existencias:
            faltantes.append(producto)
    return render(request, 'faltantes.html', {'faltantes': faltantes})

def eliminar_producto(request, id_producto):
    producto_buscado = get_object_or_404(Producto, id=id_producto)
    asociaciones = []
    if Productos_Vendidos.objects.filter(producto=producto_buscado).exists():
        asociaciones.append("ventas")
    if Compra_intermedio.objects.filter(producto=producto_buscado).exists():
        asociaciones.append("compras")
    if asociaciones:
        asociaciones_texto = ", ".join(asociaciones)
        messages.error(
            request,
            f"El producto '{producto_buscado.nombre}' tiene asociaciones con {asociaciones_texto} y no puede ser eliminado."
        )
        return redirect('lista_producto')
    producto_buscado.delete()
    messages.success(request, "Producto eliminado con éxito.")
    return redirect('lista_producto')

def editar_producto(request, id_producto):
    producto_buscado = get_object_or_404(Producto, id=id_producto)
    if request.method == 'POST':
        formulario_editar = formulario_producto(request.POST, instance=producto_buscado)
        if formulario_editar.is_valid():
            producto_editado = formulario_editar.save()
            proveedores_seleccionados = request.POST.getlist('proveedores')
            producto_editado.proveedores.set(proveedores_seleccionados)
            messages.success(request, "Producto editado con éxito.") 
            return redirect('lista_producto')
        else:
            for field in formulario_editar.errors:
                for error in formulario_editar.errors[field]:
                    messages.error(request, error)
            return redirect('lista_producto')
    else:
        formulario_editar = formulario_producto(instance=producto_buscado)
    proveedores = Proveedor.objects.all()
    return render(request, 'editar_producto.html', {
        'formulario_editar': formulario_editar,
        'id_producto': id_producto,
        'proveedores': proveedores
    })
