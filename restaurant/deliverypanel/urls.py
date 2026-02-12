from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.delivery_login,name='delivery_login'),        # /delivery/login
    # path('dashboard/', views.delivery_dashboard,name='delivery_dashboard'),# /delivery/dashboard
    # path('accept-order/<int:assign_id>/', views.delivery_accept_order, name='delivery_accept_order'),
    # path('reject-order/<int:assign_id>/', views.delivery_reject_order, name='delivery_reject_order'),
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('accept/<int:assign_id>/', views.delivery_accept_order, name='delivery_accept_order'),
    path('reject/<int:assign_id>/', views.delivery_reject_order, name='delivery_reject_order'),
    path('logout/', views.delivery_logout,name='delivery_logout'),
    path(
        'mark-delivered/<int:order_id>/',
        views.delivery_mark_delivered,
        name='delivery_mark_delivered'
    ),
    
    path('forgot-password/', views.delivery_forgot_password, name='delivery_forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-otp/',views.resend_otp,name='resend_otp'),
    path('profile/', views.delivery_profile, name='delivery_profile'),
    path('profile/edit/', views.delivery_profile_edit, name='delivery_profile_edit'),
    path('change-password/', views.delivery_change_password, name='delivery_change_password'),
    path('vehicle/', views.delivery_vehicle, name='delivery_vehicle'),

]
