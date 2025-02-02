from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import requests

from .coordinates import fetch_coordinates

ORDER_STATUS = [
    ('01_created', 'Необработанный'),
    ('02_cooking', 'Готовится'),
    ('03_delivering', 'Доставляется'),
    ('04_completed', 'Доставлен'),
]
PAYMENT_METHOD = [
    ('NOT_SET', 'Не выбран'),
    ('cash', 'Наличностью'),
    ('online', 'Электронно'),
]


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    longitude = models.FloatField(
        'Долгота',
        null=True,
        blank=True,
    )
    latitude = models.FloatField(
        'Широта',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_price(self):
        price = Sum(F('elements__product__price') * F('elements__quantity'))
        return self.annotate(price=price).prefetch_related('elements__product')\
            .select_related('selected_restaurant')


class Order(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        db_index=True,
    )
    firstname = models.CharField(
        'Имя',
        max_length=30,
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=30,
    )
    phonenumber = PhoneNumberField(
        verbose_name='Номер телефона',
        db_index=True,
    )
    status = models.CharField(
        'Статус заказа',
        max_length=20,
        choices=ORDER_STATUS,
        default='01_created',
        db_index=True,
    )
    comment = models.TextField(
        'Комментарий',
        blank=True,
    )
    registered_at = models.DateTimeField(
        'Дата регистрации',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        null=True,
        blank=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        null=True,
        blank=True,
        db_index=True,
    )
    payment = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_METHOD,
        default='NOT_SET',
        db_index=True,
    )
    selected_restaurant = models.ForeignKey(
        'Restaurant',
        related_name='orders',
        verbose_name='Заказ готовит ресторан',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderElement(models.Model):
    order = models.ForeignKey(
        'Order',
        verbose_name='Заказ',
        related_name='elements',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        'Product',
        verbose_name='Товар',
        related_name='order_elements',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product} {self.order}'
