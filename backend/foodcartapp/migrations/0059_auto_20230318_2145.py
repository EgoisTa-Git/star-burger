# Generated by Django 3.2.15 on 2023-03-18 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0058_alter_order_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='order',
            name='longitude',
        ),
    ]
