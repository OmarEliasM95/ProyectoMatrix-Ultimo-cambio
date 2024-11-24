from django import forms
from .models import Producto, Proveedor

class formulario_producto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'existencias', 'stock_maximo', 'stock_minimo', 'proveedores']
    
    def clean(self):
        cleaned_data = super().clean()
        stock_maximo = cleaned_data.get('stock_maximo')
        stock_minimo = cleaned_data.get('stock_minimo')
        existencias = cleaned_data.get('existencias')
        if stock_maximo is not None and stock_minimo is not None and existencias is not None:
            if stock_maximo <= stock_minimo:
                self.add_error('stock_maximo', 'El stock máximo debe ser mayor que el stock mínimo.')
            if existencias < 0:
                self.add_error('existencias', 'Las existencias no pueden ser negativas.')

        return cleaned_data
