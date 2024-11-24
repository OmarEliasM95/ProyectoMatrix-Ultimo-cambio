from .models import *
from django import forms
from django.forms import ModelForm

class formulario_empleado(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'dirección', 'telefono']

    def __init__(self, *args, **kwargs):
        super(formulario_empleado, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-estilo'})
            
class crear_empleado(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput, required=True)

    class Meta:
        model = Empleado
        fields = ['username', 'first_name', 'last_name', 'email', 'dni', 'dirección', 'telefono', 'password', 'password_confirm']

    def _init_(self, *args, **kwargs):
        super(crear_empleado, self)._init_(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-estilo'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self):
        empleado = super().save(commit=False)
        empleado.set_password(self.cleaned_data['password'])
        empleado.save()
        return empleado


class Cambiar_Password(forms.ModelForm):
    password_actual = forms.CharField(label="Contraseña Actual", widget=forms.PasswordInput, required=True)
    password = forms.CharField(label="Nueva Contraseña", widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(label="Confirmar Nueva Contraseña", widget=forms.PasswordInput, required=True)

    class Meta:
        model = Empleado
        fields = ['password_actual', 'password', 'password_confirm']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-estilo'})

    def clean(self):
        cleaned_data = super().clean()
        password_actual = cleaned_data.get("password_actual")
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password_actual and not self.instance.check_password(password_actual):
            self.add_error("password_actual", "La contraseña actual es incorrecta.")
        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)
        empleado.set_password(self.cleaned_data['password']) 
        if commit:
            empleado.save()
        return empleado
