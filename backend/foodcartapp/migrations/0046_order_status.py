# Generated by Django 3.2.15 on 2023-03-04 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_alter_orderelement_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('created', 'Необработанный'), ('cooking', 'Готовится'), ('delivering', 'Доставляется'), ('completed', 'Доставлен')], db_index=True, default='created', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
