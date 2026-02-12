from django.urls import path
from . import views

urlpatterns = [
    # ... baki URLs
    path('order-heatmap/', views.order_heatmap, name='order_heatmap'),
]
