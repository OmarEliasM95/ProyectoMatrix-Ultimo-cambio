from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 

class Empleado(AbstractUser):
    dni=models.IntegerField(null=True, blank=True, verbose_name="DNI")
    dirección=models.CharField(null=True, blank=True, max_length=150)
    telefono=models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.username
    
class Tarea(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=50)
    fecha_asignada = models.DateField()
    fecha_vencimiento = models.DateField()
    def __str__(self):
        return self.titulo