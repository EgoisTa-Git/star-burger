from django.http import JsonResponse
from django.templatetags.static import static
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


def get_products_error(request_body):
    products = request_body['products']
    if products is None:
        return {'error': 'products: Это поле не может быть пустым.'}
    elif not products:
        return {'error': 'products: Этот список не может быть пустым.'}
    elif not isinstance(products, list):
        return {
            'error': 'products: Ожидался list со значениями, но был получен {}.'
            .format(type(products).__name__)
        }


@api_view(['POST'])
def register_order(request):
    serialized_order = request.data

    try:
        error = get_products_error(serialized_order)
    except KeyError:
        error = {'error': 'products: Обязательное поле.'}
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
