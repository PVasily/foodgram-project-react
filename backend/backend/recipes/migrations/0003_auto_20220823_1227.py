# Generated by Django 2.2.16 on 2022-08-23 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20220822_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=255, verbose_name='Единица измерения'),
        ),
    ]