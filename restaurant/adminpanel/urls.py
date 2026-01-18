from django.contrib import admin
from django.urls import path
from adminpanel import views


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin_menu/', views.admin_menu_view, name='admin_menu'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    # path('add_fooditem/', views.add_fooditem, name='add_fooditem'),
    path('add_foodimage/', views.add_foodimage, name='add_foodimage'),
     path('delete-category/<int:id>/', views.delete_category, name='delete_category_item'),
    # path('delete-subcategory/', views.delete_subcategory_page, name='delete_subcategory_page'),
    # path('delete-subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory_item'),
    # path('delete-fooditem/', views.delete_fooditem_page, name='delete_fooditem_page'),
    # path('delete-fooditem/<int:id>/', views.delete_fooditem, name='delete_fooditem_item'),
    # path('delete-foodimage/', views.delete_foodimage_page, name='delete_foodimage_page'),
    # path('delete-foodimage/<int:id>/', views.delete_foodimage, name='delete_foodimage_item'),
    path('update-category/', views.update_category_page, name='update_category_page'),
    path('update-category/<int:category_id>/', views.update_category_page, name='update_category'),
    path('update-subcategory/<int:id>/', views.update_subcategory, name='update_subcategory'),
    path('delete-subcategory/<int:id>/', views.delete_subcategory_item, name='delete_subcategory_item'),
    path('add-fooditem/', views.add_fooditem, name='add_fooditem'),
    path('update-fooditem/<int:id>/', views.update_fooditem, name='update_fooditem'),
    path('delete-fooditem/<int:id>/', views.delete_fooditem, name='delete_fooditem'),
    path('add-foodimage/', views.add_foodimage, name='add_foodimage'),
    path('update-foodimage/<int:id>/', views.update_foodimage, name='update_foodimage'),
    path('delete-foodimage/<int:id>/', views.delete_foodimage, name='delete_foodimage_item'),

    
]
