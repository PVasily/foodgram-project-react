# Generated by Django 2.2.16 on 2022-08-14 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_remove_ingredient_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
    ]
