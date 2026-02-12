from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.customer_register, name='customer_register'),
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    # 🔐 CUSTOMER FORGOT PASSWORD
path('forgot-password/', views.customer_forgot_password, name='customer_forgot_password'),
path('verify-otp/', views.customer_verify_otp, name='customer_verify_otp'),
path('reset-password/', views.customer_reset_password, name='customer_reset_password'),

path("resend-otp/", views.customer_resend_otp, name="customer_resend_otp"),


]
