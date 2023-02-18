from pprint import pprint

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field import validators
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response


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


@api_view(['POST'])
def register_order(request):
    serialized_order = request.data
    error = {}
    checklist = get_required_fields(Order)
    pprint(checklist)

    error.update(check_fields(serialized_order, checklist))
    error.update(check_types(serialized_order))
    error.update(check_null_fields(serialized_order))
    error.update(check_empty_field(serialized_order))
    error.update(check_phonenumber(serialized_order))
    error.update(check_products(serialized_order))

    if error:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
    return Response({'success': serialized_order})


def get_required_fields(model):
    fields = model._meta.get_fields()
    required_fields = []
    for field in fields:
        if not getattr(field, 'blank', True):
            required_fields.append(field)
    return required_fields


def check_fields(request_body, required_fields):
    required = []
    for field in required_fields:
        if not request_body.get(field.name):
            required.append(field.name)
    if required:
        return {
            'required_fields_error':
                '{}: Обязательное поле.'.format(', '.join(required))
        }
    return {}


def check_types(request_body):
    wrong_fields = {}
    for field, value in request_body.items():
        if field != 'products' and not isinstance(value, str):
            wrong_fields[field] = type(value).__name__
    if wrong_fields:
        return {
            'field_type_error':
                '{}: Ожидался str, но был получен {}'
                .format(
                    ', '.join(wrong_fields.keys()),
                    ', '.join(wrong_fields.values()),
                )
        }
    return {}


def check_null_fields(request_body):
    null_fields = []
    for field in request_body.keys():
        if request_body[field] is None:
            null_fields.append(field)
    if null_fields:
        return {
            'null_error': '{}: Это поле не может быть null.'
            .format(', '.join(null_fields))
        }
    return {}


def check_empty_field(request_body):
    empty_fields = []
    for field in request_body.keys():
        if not request_body[field]:
            empty_fields.append(field)
    if empty_fields:
        return {
            'empty_field_error': '{}: Это поле не может быть пустым.'
            .format(', '.join(empty_fields))
        }
    return {}


def check_phonenumber(request_body):
    phonenumber = request_body.get('phonenumber')
    if not phonenumber:
        return {
            'phonenumber_error': 'Это поле не может быть пустым.'
        }
    try:
        validators.validate_international_phonenumber(phonenumber)
    except ValidationError as error:
        return {
            'phonenumber_error': error.args[0]
        }
    return {}


def check_products(request_body):
    products = request_body.get('products')
    valid_ids = Product.objects.values_list('id', flat=True).order_by('id')
    if products is None:
        return {'products_error': 'products: Обязательное поле.'}
    elif not isinstance(products, list):
        return {
            'products_type_error':
                'Ожидался list со значениями, но был получен {}.'
                .format(type(products).__name__)
        }
    elif not products:
        return {'products_error': 'Этот список не может быть пустым.'}
    for product in products:
        if product['product'] not in valid_ids:
            return {
                'product_id_error': '{} - Недопустимый ID товара.'
                .format(product['product'])
            }
    return {}
