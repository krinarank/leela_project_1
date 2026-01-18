

from django.shortcuts import render
from adminpanel.models import FoodItemCategory, FoodItemSubCategory, FoodItem, FoodItemImage

from adminpanel.models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem
)

# def menu_view(request):
#     categories = FoodItemCategory.objects.all()
#     menu_data = []

#     for cat in categories:
#         subcats = FoodItemSubCategory.objects.filter(food_item_cat=cat)
#         subcat_items = []

#         for sub in subcats:
#             items = FoodItem.objects.filter(
#                 sub_cat=sub,
#                 is_available=True
#             ).prefetch_related('images')   # IMPORTANT

#             subcat_items.append({
#                 'subcategory': sub,
#                 'items': items
#             })

#         menu_data.append({
#             'category': cat,
#             'subcategories': subcat_items
#         })

#     return render(request, 'menu/menu.html', {'menu_data': menu_data})
from django.shortcuts import render

def home(request):
    return render(request, 'menu/home.html')

def menu_page(request):
   categories = FoodItemCategory.objects.prefetch_related(
        'fooditemsubcategory_set__fooditem_set__images'
    )

   return render(request, 'menu/menu.html', {
        'categories': categories
    })

def about(request):
    return render(request, 'menu/about.html')

def contact(request):
    return render(request, 'menu/contact.html')
