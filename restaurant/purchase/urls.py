from django.urls import path
from . import views

urlpatterns = [
    # path('dashboard/', views.purchase_dashboard, name='purchase_dashboard'),
    # path('supplier/add/', views.add_supplier, name='add_supplier'),
    # path('supplier/list/', views.list_supplier, name='list_supplier'),
    path('supplier', views.supplier_page, name='supplier_page'),
    path('supplier/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('supplier/delete/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),

    path('ingredients/', views.ingredient_page, name='ingredient_page'),
    path('ingredient/edit/<int:id>/', views.edit_ingredient, name='edit_ingredient'),
    path('ingredient/delete/<int:id>/', views.delete_ingredient, name='delete_ingredient'),
    # path('purchase/add/', views.add_purchase, name='add_purchase'),
    # # path('purchase/list/', views.list_purchase, name='list_purchase'),
    # path('purchases/', views.purchase_list, name='purchase_list'),
    # path('purchase/add/', views.purchase_create, name='purchase_add'),
    # path('purchase/delete/<int:pk>/', views.purchase_delete, name='purchase_delete'),
    path('get-last-recipe/', views.get_last_recipe, name='get_last_recipe'),

    path('purchase/add/', views.purchase_add, name='purchase_add'),
    path('purchase/edit/<int:purchase_id>/', views.purchase_edit, name='purchase_edit'),
    path('purchase/delete/<int:purchase_id>/', views.purchase_delete, name='purchase_delete'),
    path('purchase-return/', views.purchase_return_add, name='purchase_return_add'),
    path('prepared/add/', views.prepared_item_add, name='prepared_item_add'),
    path('prepared/edit/<int:item_id>/', views.prepared_item_edit, name='prepared_item_edit'),
    path('prepared/delete/<int:item_id>/', views.prepared_item_delete, name='prepared_item_delete'),
    
    
    


]
