from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import requests

from foodcartapp.models import Restaurant, Order
from address.coordinates import fetch_coordinates
from address.models import Address


@receiver(pre_save, sender=Restaurant)
def get_restaurant_coordinates(sender, instance, **kwargs):
    api_key = settings.YANDEX_GEO_APIKEY
    try:
        instance.latitude, instance.longitude = fetch_coordinates(
            api_key,
            instance.address,
        )
    except (requests.exceptions.HTTPError, KeyError) as err:
        pass


@receiver(post_save, sender=Order)
def update_order_coordinates(sender, instance, **kwargs):
    api_key = settings.YANDEX_GEO_APIKEY
    address, created = Address.objects.get_or_create(address=instance.address)
    if created:
        try:
            address.latitude, address.longitude = fetch_coordinates(
                api_key,
                instance.address,
            )
        except (requests.exceptions.HTTPError, KeyError) as err:
            pass
        address.save()
