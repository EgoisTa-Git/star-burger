from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .models import OrderElement, Order


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
        return order
