from django.urls import path
from . import views
from .views import toggle_wishlist

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
    


    # path('offers/', views.create_and_list_offer, name='create_and_list_offer'),
    path('offers/delete/<int:id>/', views.offer_delete, name='offer_delete'), 
    path('offers/update/<int:offer_id>/', views.offer_update, name='offer_update'),
    path('apply-offer/', views.apply_offer, name='apply_offer'),
    path("offers/create/", views.create_offer, name="create_offer"),
    path("offers/current/", views.current_offers, name="current_offer"),




    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    path('wishlist/add/<int:food_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # Add item
    path('wishlist/remove/<int:food_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # Remove item
    path('wishlist/toggle/<int:food_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    # path('wishlist/', views.my_wishlist, name='my_wishlist'),
    # path('toggle-wishlist/<int:food_id>/', views.toggle_wishlist, name='toggle_wishlist'),

]
   



