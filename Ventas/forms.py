from .models import *
from django.forms import ModelForm

class Formulario_MetodoPago(ModelForm):
    class Meta:
        model = Venta
        fields=['metodo_pago']
        labels={'metodo_pago':'Método de Pago'}
        