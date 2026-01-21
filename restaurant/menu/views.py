from django.shortcuts import render
from adminpanel.models import FoodItemCategory, FoodItemSubCategory, FoodItem, FoodItemImage

from adminpanel.models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem
)

from django.shortcuts import render

def home(request):
    special_items = FoodItem.objects.filter(
        is_special=True,
        is_available=True
    ).prefetch_related('images')

    return render(request, 'menu/home.html', {
        'special_items': special_items
    })

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
