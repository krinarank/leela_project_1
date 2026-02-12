from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu_page, name='menu_page'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),

    path('profile/change-password/', views.customer_change_password, name='customer_change_password'),
  
    path('notifications/', views.customer_notifications, name='customer_notifications'),



    path('profile/', views.profile_page, name='profile'),

]
