# Generated by Django 5.1 on 2024-10-27 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='oculto',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='area',
            field=models.CharField(default='trabajador', max_length=100),
        ),
    ]
