import json
from pprint import pprint

from django.http import JsonResponse
from django.templatetags.static import static


from .models import Product
from .models import Order
from .models import OrderElement


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    try:
        serialized_order = json.loads(request.body.decode())
    except ValueError:
        return JsonResponse({
            'error': 'error occurs',
        })
    pprint(serialized_order)
    order = Order.objects.create(
        address=serialized_order['address'],
        firstname=serialized_order['firstname'],
        lastname=serialized_order['lastname'],
        phonenumber=serialized_order['phonenumber'],
    )
    for order_element in serialized_order['products']:
        OrderElement.objects.create(
            order=order,
            product=Product.objects.get(pk=order_element['product']),
            quantity=order_element['quantity'],
        )
    return JsonResponse({})
