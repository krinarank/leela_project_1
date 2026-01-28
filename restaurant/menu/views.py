from django.shortcuts import render,render
from adminpanel.models import FoodItemCategory, FoodItemSubCategory, FoodItem, FoodItemImage
from django.contrib import messages
from adminpanel.models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem
)
from .models import Inquiry
from orders.utils import get_best_offer
from decimal import Decimal





def home(request):
    special_items = FoodItem.objects.filter(
        is_special=True,
        is_available=True
    ).prefetch_related('images')

    return render(request, 'menu/home.html', {
        'special_items': special_items
    })


# def menu_page(request):
#     categories = FoodItemCategory.objects.prefetch_related(
#         'fooditemsubcategory_set__fooditem_set__images'
#     )

#     for category in categories:
#         for sub in category.fooditemsubcategory_set.all():
#             for item in sub.fooditem_set.all():

#                 offer = get_best_offer(item)

#                 if offer:
#                     item.has_offer = True
#                     item.offer_percent = offer.offer.discount_percentage

#                     discount = (item.price * Decimal(offer.offer.discount_percentage)) / Decimal(100)
#                     item.discounted_price = item.price - discount
#                     item.discounted_price = item.discounted_price.quantize(Decimal("0.01"))

#                 else:
#                     item.has_offer = False
#                     item.discounted_price = item.price

#     return render(request, 'menu/menu.html', {
#         'categories': categories
#     })
# def menu_page(request):

#     categories = FoodItemCategory.objects.prefetch_related(
#         'fooditemsubcategory_set__fooditem_set'
#     )

#     all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

#     for item in all_items:
#         offer = get_best_offer(item)

#         if offer:
#             discount = offer.offer.discount_percentage   # ✅ FIX
#             item.offer_percent = discount
#             item.discounted_price = round(
#                 item.price - (item.price * discount / 100), 2
#             )
#             item.has_offer = True
#         else:
#             item.has_offer = False

#     context = {
#         'categories': categories,
#         'all_items': all_items
#     }

#     return render(request, 'menu/menu.html', context)
def menu_page(request):

    categories = FoodItemCategory.objects.prefetch_related(
        'fooditemsubcategory_set__fooditem_set__images'
    )

    all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

    # 🔁 helper function
    def apply_offer(item):
        offer = get_best_offer(item)
        if offer:
            discount = offer.offer.discount_percentage
            item.offer_percent = discount
            item.discounted_price = round(
                item.price - (item.price * discount / 100), 2
            )
            item.has_offer = True
        else:
            item.has_offer = False

    # ✅ MAIN ALL ITEMS
    for item in all_items:
        apply_offer(item)

    # ✅ CATEGORY + SUBCATEGORY ITEMS
    for category in categories:
        for sub in category.fooditemsubcategory_set.all():
            for item in sub.fooditem_set.all():
                apply_offer(item)

    context = {
        'categories': categories,
        'all_items': all_items
    }

    return render(request, 'menu/menu.html', context)

def about(request):
    return render(request, 'menu/about.html')

def contact(request):
    return render(request, 'menu/contact.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Inquiry

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not all([name, email, subject, message]):
            messages.error(request, "All fields are required!")
            return redirect('contact')

        Inquiry.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            user=request.user if request.user.is_authenticated else None
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')

    return render(request, 'menu/contact.html')
