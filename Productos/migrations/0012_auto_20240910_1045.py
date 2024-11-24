# Generated by Django 3.2.25 on 2024-09-10 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proveedores', '0001_initial'),
        ('Productos', '0011_auto_20240910_1038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producto',
            old_name='costo_producto',
            new_name='costo',
        ),
        migrations.AddField(
            model_name='producto',
            name='marca',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='producto',
            name='proveedores',
            field=models.ManyToManyField(through='Productos.Producto_Intermedia', to='Proveedores.Proveedor'),
        ),
    ]
