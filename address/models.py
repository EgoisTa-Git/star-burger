from django.db import models
from django.utils import timezone


class Address(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        unique=True,
        db_index=True,
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
    request_date = models.DateTimeField(
        'Дата запроса к геокодеру',
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return self.address
