from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu_page, name='menu_page'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),  # <-- must point to contact_view
]
