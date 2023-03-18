# Generated by Django 3.2.15 on 2023-03-18 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_auto_20230318_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('01_created', 'Необработанный'), ('02_cooking', 'Готовится'), ('03_delivering', 'Доставляется'), ('04_completed', 'Доставлен')], db_index=True, default='01_created', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
