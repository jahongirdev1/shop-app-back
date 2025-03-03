from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render
from jahongir import settings
from .models import *
import requests, json, urllib.parse

def branch_orders_view(request, branch_id=None):
    branches = BranchModel.objects.all()
    selected_branch = None
    orders = OrderModel.objects.all()

    # Get branch_id from request GET parameters if not provided in URL
    branch_id = request.GET.get('branch_id', branch_id)

    if branch_id:
        selected_branch = get_object_or_404(BranchModel, id=branch_id)
        orders = selected_branch.orders.all()

    return render(request, 'orders.html', {
        'branches': branches,
        'selected_branch': selected_branch,
        'orders': orders,
    })


# def branch_orders_view(request, branch_id):
#     selected_branch = get_object_or_404(BranchModel, id=branch_id)
#     orders = selected_branch.orders.all()
#     return render(request, 'orders.html', {'branch': selected_branch, 'orders': orders})


def custom_404(request):
    return render(request, '404.html', status=404)
def indexHadler(request):
    order_model = OrderModel.objects.all()
    return  render(request, 'index.html', {'order_model':order_model})

def product_list_json(request):
    products = ProductModel.objects.filter(status=0).values()
    return JsonResponse({'products': list(products)}, safe=False)

def setting_json(request):
    settings = SettingsModel.objects.all()


def branches_list_json(request):
    branches = BranchModel.objects.filter(status=0).values()
    return  JsonResponse({'branches': list(branches)}, safe=False)

def category_list_json(requests):
    categories = list(CategoryModel.objects.values())
    return  JsonResponse({'categories':categories}, safe=False)

def poster_list_json(requests):
    poster = list(PosterModel.objects.values())
    return  JsonResponse({'poster':poster}, safe=False)

def get_product(request, id):
    if request.method == 'GET':
        try:
            product = get_object_or_404(ProductModel, id=id)
            product_data = {
                'id': product.id,
                'image': product.image.url if product.image else None,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'categoryName': product.category.name if product.category else None,
                'count': product.count
            }
            return JsonResponse(product_data)
        except ProductModel.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if UserModel.objects.filter(phoneNumber=data['phoneNumber']).exists():
                return JsonResponse({'status': 'error', 'message': 'This phone number is already registered.'})
            user = UserModel.objects.create(
                fullName=data['fullName'],
                phoneNumber=data['phoneNumber'],
                password=data['password']
                # password=make_password(data['password'])
            )
           
            for product_id in data.get('favoriteProducts', []):
                user.favoriteProducts.add(product_id)
            
            for order_id in data.get('orders', []):
                order = OrderModel.objects.get(id=order_id)
                user.orders.add(order)
            
            user.save()
            return JsonResponse({'status': 'success', 'user_id': user.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_user(request, user_id):
    if request.method == 'GET':
        user = get_object_or_404(UserModel, id=user_id)
        
        orders = []
        for order in user.orders.all():
            products = list(order.productsList.values())
            orders.append({
                'id': order.id,
                'user_id': order.user_id,
                'description': order.description,
                'locationLink': order.locationLink,
                'totalPrice': order.totalPrice,
                'createdAt': order.createdAt,
                'isAccepted': order.isAccepted,
                'isProcess': order.isProcess,
                'isDelivered': order.isDelivered,
                'isCompleted': order.isCompleted,
                'isCanceled': order.isCanceled,
                'productsList': products
            })
        
        user_data = {
            'id': user.id,
            'fullName': user.fullName,
            'phoneNumber': user.phoneNumber,
            'password': user.password,
            'favoriteProducts': list(user.favoriteProducts.values_list('id', flat=True)),
            'orders': orders
        }
        return JsonResponse(user_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_user_phoneNumber(request, phoneNumber):
    if request.method == 'POST':
        try:
            user = UserModel.objects.get(phoneNumber=phoneNumber)
            return JsonResponse({'status': 'success', 'user_id': user.id})
        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def update_user(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = UserModel.objects.get(id=user_id)

            if 'phoneNumber' in data:
                user.phoneNumber = data['phoneNumber']
            if 'fullName' in data:
                user.fullName = data['fullName']
            if 'password' in data:
                user.password = data['password']

            if 'favoriteProducts' in data:
                user.favoriteProducts.clear()
                for product_id in data['favoriteProducts']:
                    try:
                        product = ProductModel.objects.get(id=product_id)
                        user.favoriteProducts.add(product)
                    except ProductModel.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Product with id {product_id} not found'},
                                            status=404)

            if 'orders' in data:
                user.orders.clear()

                for order_data in data['orders']:
                    try:
                        order_id = order_data.get('id')
                        order, created = OrderModel.objects.update_or_create(
                            id=order_id,
                            defaults={
                                'user': user,
                                'description': order_data.get('description', ''),
                                'locationLink': order_data.get('locationLink'),
                                'totalPrice': order_data.get('totalPrice'),
                                'createdAt': order_data.get('createdAt'),
                                'isAccepted': order_data.get('isAccepted', False),
                                'isProcess': order_data.get('isProcess', False),
                                'isDelivered': order_data.get('isDelivered', False),
                                'isCompleted': order_data.get('isCompleted', False),
                                'isCanceled': order_data.get('isCanceled', False),
                            }
                        )

                        order.productsList.clear()
                        for product_data in order_data.get('productsList', []):
                            try:
                                product = ProductModel.objects.get(id=product_data['id'])
                                order.productsList.add(product, through_defaults={'count': product_data['count']})
                            except ProductModel.DoesNotExist:
                                return JsonResponse(
                                    {'status': 'error', 'message': f'Product with id {product_data["id"]} not found'},
                                    status=404)

                        order.save()
                        user.orders.add(order)

                    except OrderModel.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Order with id {order_id} not found'},
                                            status=404)

            user.save()

            user = UserModel.objects.get(id=user_id)

            response_data = {
                'status': 'success',
                'user_id': user.id,
                'fullName': user.fullName,
                'phoneNumber': user.phoneNumber,
                'favoriteProducts': list(user.favoriteProducts.values_list('id', flat=True)),
                'orders': [{'id': order.id, 'description': order.description} for order in user.orders.all()]
            }

            return JsonResponse(response_data)

        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        except ProductModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        except OrderModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def update_favorite_products(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = UserModel.objects.get(id=user_id)

            if 'favoriteProducts' in data:
                user.favoriteProducts.clear()
                for product_id in data['favoriteProducts']:
                    try:
                        product = ProductModel.objects.get(id=product_id)
                        user.favoriteProducts.add(product)
                    except ProductModel.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Product with id {product_id} not found'},
                                            status=404)

            user.save()

            response_data = {
                'status': 'success',
                'user_id': user.id,
                'favoriteProducts': list(user.favoriteProducts.values_list('id', flat=True)),
            }

            return JsonResponse(response_data)

        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def add_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = UserModel.objects.get(id=data['user_id'])

            for product in data['productsList']:
                product_instance = ProductModel.objects.filter(id=product['productId']).first()
                if not product_instance:
                    return JsonResponse(
                        {'status': 'error', 'message': f"Product with ID {product['productId']} does not exist."},
                        status=400)

            order = OrderModel.objects.create(
                user=user,
                description=data['description'],
                locationLink=data['locationLink'],
                totalPrice=data['totalPrice'],
                isAccepted=data['isAccepted'],
                isProcess=data['isProcess'],
                isDelivered=data['isDelivered'],
                isCompleted=data['isCompleted'],
                isCanceled=data['isCanceled']
            )

            for product in data['productsList']:
                product_instance = ProductModel.objects.get(id=product['productId'])
                order.productsList.add(product_instance, through_defaults={'count': product['count']})

            send_order_telegram(data['productsList'], order)

            return JsonResponse({'status': 'success', 'order_id': order.id}, status=201)

        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)

        except Exception as e:
            # Log the exception for debugging purposes
            logger.error(f"Failed to create order: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Failed to create order. Please try again later.'},
                                status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_order(request, order_id):
    if request.method == 'GET':
        try:
            order = OrderModel.objects.get(id=order_id)
            order_data = {
                'user_id': order.user.id,
                'id': order_id,
                'description': order.description,
                'locationLink': order.locationLink,
                'totalPrice': str(order.totalPrice),
                'createdAt': order.createdAt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'isAccepted': order.isAccepted,
                'isProcess': order.isProcess,
                'isDelivered': order.isDelivered,
                'isCompleted': order.isCompleted,
                'isCanceled': order.isCanceled,
                'productsList': list(order.productsList.values())
            }
            return JsonResponse(order_data)
        except OrderModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def add_order_user(request, order_id, user_id):
    if request.method == 'POST':
        try:
            order = OrderModel.objects.get(id=order_id)
            user = UserModel.objects.get(id=user_id)

            # Associate the user with the order

            user.orders.add(order)
            order.user = user
            order.save()

            return JsonResponse(
                {'status': 'success', 'message': f'User {user_id} associated with order {order_id} successfully'})

        except OrderModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

        except UserModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def send_order_telegram(product_list, order):

    product_counts = {}
    for product in product_list:
        product_id = product['productId']
        count = product['count']
        if product_id in product_counts:
            product_counts[product_id] += count
        else:
            product_counts[product_id] = count

    products_info = '\n'.join([f"{ProductModel.objects.get(id=product_id).name} - {count} шт" for product_id, count in
                               product_counts.items()])

    totalPrice = order.totalPrice
    locationLink = order.locationLink
    description = order.description

    info = f"№ - {order.id}\n\n{products_info}\n\nИтоговая цена: {totalPrice} ₸\nСсылка на местоположение: {locationLink}"

    text = 'Информация о заказ: \n'

    message = f"{text}{info}\n{description}"

    # URL encode the message
    encoded_message = urllib.parse.quote_plus(message)

    send_url = f'https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage?chat_id={settings.CHAT_ID}&text={encoded_message}'

    response = requests.get(send_url)

    # Log the response
    print(response.text)

@csrf_exempt
def send_sms(request):

    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            sms_body = body['sms']

            if sms_body:
                sms = f'Your code is: {sms_body}'
                send_url = f'https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage'
                response = requests.post(send_url, data={'chat_id': settings.CHAT_ID, 'text': sms})

                if response.status_code == 200:
                    return JsonResponse({'status': 'success', 'message': 'SMS sent successfully'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Failed to send SMS'}, status=response.status_code)
            else:
                return JsonResponse({'status': 'error', 'message': 'No SMS body provided'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def update_order(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = get_object_or_404(OrderModel, id=order_id)
            if 'isAccepted' in data:
                order.isAccepted = data['isAccepted']
            if 'isProcess' in data:
                order.isProcess = data['isProcess']
            if 'isDelivered' in data:
                order.isDelivered = data['isDelivered']
            if 'isCompleted' in data:
                order.isCompleted = data['isCompleted']
            if 'isCanceled' in data:
                order.isCanceled = data['isCanceled']
            order.save()
            return JsonResponse({'status': 'success', 'order_id': order.id})

        except OrderModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Order with id {order_id} not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
