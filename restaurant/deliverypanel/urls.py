from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.delivery_login,name='delivery_login'),        # /delivery/login
    path('dashboard/', views.delivery_dashboard,name='delivery_dashboard'),# /delivery/dashboard
    path('logout/', views.delivery_logout,name='delivery_logout'),
                # /delivery/logout
    path('add/',views.add_delivery_person),
    path('forgot-password/', views.delivery_forgot_password, name='delivery_forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-otp/',views.resend_otp,name='resend_otp'),
]
