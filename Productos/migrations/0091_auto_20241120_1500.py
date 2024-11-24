# Generated by Django 3.2.25 on 2024-11-20 15:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proveedores', '0004_alter_proveedor_email'),
        ('Productos', '0090_auto_20241120_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='fecha_ingreso',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='producto',
            name='proveedores',
            field=models.ManyToManyField(through='Productos.Producto_Intermedia', to='Proveedores.Proveedor'),
        ),
    ]
