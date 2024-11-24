from .models import *
from django.forms import ModelForm

class Formulario_Proveedor(ModelForm):
    class Meta:
        model=Compra
        fields=['proveedor']

class Formulario_MetodoPago(ModelForm):
    class Meta:
        model=Compra
        fields=['metodo_pago']
        labels={'metodo_pago':'Método de pago'}
    
   