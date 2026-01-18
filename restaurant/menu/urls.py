from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('menu/', views.menu_page, name='menu_page'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
