from django.conf.urls.static import static
from django.contrib import admin
from jahongir import settings
from django.urls import path
from main.views import *

handler = custom_404

urlpatterns = [
    path('', indexHadler, name='index-handler'),
    path('a/', indexHadler, name='index-handler2'),
    path('admin/', admin.site.urls),
    path('poster/', poster_list_json, name='poster-list-json'),
    path('update-order/<int:order_id>/', update_order, name='update-order'),
    path('categories/', category_list_json, name='categories-list-json'),
    path('products/', product_list_json, name='product-list-json'),
    path('get-product/<int:id>/', get_product, name='get-product'),
    path('add-user/', add_user, name='add-user'),
    path('get-user/<int:user_id>/', get_user, name='user-detail-json'),
    path('get-user-phone-number/<str:phoneNumber>/', get_user_phoneNumber, name='get-user-phoneNumber'),
    path('user/update/<int:user_id>/', update_user, name='update_user'),
    path('add-order/', add_order, name='add-order'),
    path('send-sms/', send_sms, name='send-sms'),
    path('order/<int:order_id>', get_order, name='order-detail'),
    path('add-order-user/<int:order_id>/<int:user_id>', add_order_user, name='add-order-user'),
    path('add-order-user/<int:user_id>/<int:order_id>/', add_order_user, name='add_order_user'),
    path('update-favorite-products/<int:user_id>/', update_favorite_products, name='update-favorite-products'),
    path('branches/', branches_list_json, name='branches-list-json'),
    path('orders/', branch_orders_view, name='orders'),
    path('orders/<int:branch_id>/', branch_orders_view, name='branch_orders'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



