from django.conf import settings
from django.db import transaction
import requests
from rest_framework.serializers import ModelSerializer

from .models import OrderElement, Order
from address.models import Address
from address.coordinates import fetch_coordinates


class ProductSerializer(ModelSerializer):

    class Meta:
        model = OrderElement
        fields = [
            'product',
            'quantity',
        ]


class OrderSerializer(ModelSerializer):
    products = ProductSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products',
        ]

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            address=validated_data['address'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
        )

        products = validated_data['products']
        elements = [OrderElement(
            order=order, price=fields['product'].price, **fields
        ) for fields in products]
        OrderElement.objects.bulk_create(elements)

        api_key = settings.YANDEX_GEO_APIKEY
        address, status = Address.objects.get_or_create(
            address=validated_data['address'],
        )
        if not address.latitude or not address.longitude:
            try:
                address.latitude, address.longitude = fetch_coordinates(
                    api_key,
                    validated_data['address'],
                )

            except (requests.exceptions.HTTPError, KeyError) as err:
                pass
            address.save()
        return order
