from django.contrib import admin
from django.urls import path
from adminpanel import views


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin_menu/', views.admin_menu_view, name='admin_menu'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('add_foodimage/', views.add_foodimage, name='add_foodimage'),
     path('delete-category/<int:id>/', views.delete_category, name='delete_category_item'),
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

    path('inquiries/', views.admin_inquiry_list, name='admin_inquiry_list'),
   # path('inquiries/reply/<int:inquiry_id>/', views.admin_reply_inquiry, name='admin_reply_inquiry'),
    path('inquiry/reply/<int:id>/', views.reply_inquiry, name='reply_inquiry'),

   
     path('states/', views.add_and_list_state, name='add_and_list_state'),
     path('states/edit/<int:id>/', views.edit_state, name='edit_state'),
    path('states/delete/<int:id>/', views.delete_state, name='delete_state'),
     

     # CITY
path('cities/', views.add_and_list_city, name='add_and_list_city'),
path('cities/edit/<int:id>/', views.edit_city, name='edit_city'),
path('cities/delete/<int:id>/', views.delete_city, name='delete_city'),
# AREA
path('areas/', views.add_and_list_area, name='add_and_list_area'),
path('areas/edit/<int:id>/', views.edit_area, name='edit_area'),
path('areas/delete/<int:id>/', views.delete_area, name='delete_area'),


    # path('cities/', views.city_list, name='city_list'),
    # path('cities/add/', views.add_city, name='add_city'),
    # path('cities/edit/<int:id>/', views.edit_city, name='edit_city'),
    # path('cities/delete/<int:id>/', views.delete_city, name='delete_city'),

    # # path('areas/', views.area_list, name='area_list'),
    # # path('areas/add/', views.add_area, name='add_area'),
    # path('areas/edit/<int:id>/', views.edit_area, name='edit_area'),
    # path('areas/delete/<int:id>/', views.delete_area, name='delete_area'),
    

     
]
