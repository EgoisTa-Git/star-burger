# Generated by Django 3.2.15 on 2023-03-14 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_auto_20230311_2106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='restaurant',
            new_name='selected_restaurant',
        ),
    ]
