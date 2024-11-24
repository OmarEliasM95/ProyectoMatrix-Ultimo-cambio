from django.urls import path
from . import views

urlpatterns = [
    path('panel_venta/', views.panel_venta, name='panel_venta'),
    path('agregar_producto/<int:id_producto>/', views.agregar_producto, name='agregar_producto'),
    path('eliminar_producto_venta/<int:id_producto>/', views.eliminar_producto_venta, name='eliminar_producto_venta'),
    path('crear_factura/', views.crear_factura, name='crear_factura'),
    path('grafico_ventas/',views.grafico_ventas,name='grafico_ventas'),
    path('cancelar_venta', views.cancelar_venta, name='cancelar_venta')
]