from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:food_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('get_cart/', views.get_cart, name='get_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/increase/<int:id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<int:id>/', views.decrease_qty, name='decrease_qty'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove-item/<int:item_id>/', views.remove_item, name='remove_item'),


]
