# Generated by Django 4.2.16 on 2024-11-03 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurante',
            name='closing_time',
            field=models.TimeField(verbose_name='Hora de cierre'),
        ),
        migrations.AlterField(
            model_name='restaurante',
            name='opening_time',
            field=models.TimeField(verbose_name='Hora de apertura'),
        ),
    ]