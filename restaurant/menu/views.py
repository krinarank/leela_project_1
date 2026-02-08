from django.shortcuts import render, redirect
from django.contrib import messages

from adminpanel.models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem,
    FoodItemImage
)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Inquiry
from orders.utils import get_best_offer
from decimal import Decimal
from orders.models import Wishlist


from orders.models import Wishlist
from .models import Inquiry


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

#     all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

#     # 🔁 helper function
#     def apply_offer(item):
#         offer = get_best_offer(item)
#         if offer:
#             discount = offer.offer.discount_percentage
#             item.offer_percent = discount
#             item.discounted_price = round(
#                 item.price - (item.price * discount / 100), 2
#             )
#             item.has_offer = True
#         else:
#             item.has_offer = False

#     # ✅ MAIN ALL ITEMS
#     for item in all_items:
#         apply_offer(item)

#     # ✅ CATEGORY + SUBCATEGORY ITEMS
#     for category in categories:
#         for sub in category.fooditemsubcategory_set.all():
#             for item in sub.fooditem_set.all():
#                 apply_offer(item)

#     context = {
#         'categories': categories,
#         'all_items': all_items
#     }

#     return render(request, 'menu/menu.html', context)
# def menu_page(request):

#     categories = FoodItemCategory.objects.prefetch_related(
#         'fooditemsubcategory_set__fooditem_set__images'
#     )

#     all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

#     # 🔁 helper function
#     def apply_offer(item):
#         offer = get_best_offer(item)
#         if offer:
#             discount = offer.offer.discount_percentage
#             item.offer_percent = discount
#             item.discounted_price = round(
#                 item.price - (item.price * discount / 100), 2
#             )
#             item.has_offer = True
#         else:
#             item.has_offer = False

#     # ✅ MAIN ALL ITEMS
#     for item in all_items:
#         apply_offer(item)

#     # ✅ CATEGORY + SUBCATEGORY ITEMS
#     for category in categories:
#         for sub in category.fooditemsubcategory_set.all():
#             for item in sub.fooditem_set.all():
#                 apply_offer(item)

#     context = {
#         'categories': categories,
#         'all_items': all_items
#     }

#     return render(request, 'menu/menu.html', context)


# def menu_page(request):
#     categories = FoodItemCategory.objects.all()

#     if request.user.is_authenticated:
#         wishlist_items = list(
#             Wishlist.objects.filter(user=request.user)
#             .values_list('food_item_id', flat=True)
#         )
#     else:
#         wishlist_items = request.session.get('wishlist', [])

#     return render(request, 'menu/menu.html', {
#         'categories': categories,
#         'wishlist_items': wishlist_items
#     })
def menu_page(request):

    categories = FoodItemCategory.objects.prefetch_related(
        'fooditemsubcategory_set__fooditem_set__images'
    )

    all_items = FoodItem.objects.filter(
        is_available=True
    ).prefetch_related('images')

    # 🔁 OFFER HELPER
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

    # ✅ Apply offers to all items
    for item in all_items:
        apply_offer(item)

    for category in categories:
        for sub in category.fooditemsubcategory_set.all():
            for item in sub.fooditem_set.all():
                apply_offer(item)

    # ❤️ WISHLIST DATA
    if request.user.is_authenticated:
        wishlist_items = list(
            Wishlist.objects.filter(user=request.user)
            .values_list('food_item_id', flat=True)
        )
    else:
        wishlist_items = request.session.get('wishlist', [])

    context = {
        'categories': categories,
        'all_items': all_items,
        'wishlist_items': wishlist_items
    }

    return render(request, 'menu/menu.html', context)

def about(request):
    return render(request, 'menu/about.html')


def contact(request):
    return render(request, 'menu/contact.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Inquiry
# def menu_page(request):

#     categories = FoodItemCategory.objects.prefetch_related(
#         'fooditemsubcategory_set__fooditem_set__images'
#     )

#     all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

#     # 🔁 helper function
#     def apply_offer(item):
#         offer = get_best_offer(item)
#         if offer:
#             discount = offer.offer.discount_percentage
#             item.offer_percent = discount
#             item.discounted_price = round(
#                 item.price - (item.price * discount / 100), 2
#             )
#             item.has_offer = True
#         else:
#             item.has_offer = False

#     # ✅ MAIN ALL ITEMS
#     for item in all_items:
#         apply_offer(item)

#     # ✅ CATEGORY + SUBCATEGORY ITEMS
#     for category in categories:
#         for sub in category.fooditemsubcategory_set.all():
#             for item in sub.fooditem_set.all():
#                 apply_offer(item)

#     context = {
#         'categories': categories,
#         'all_items': all_items
#     }

#     return render(request, 'menu/menu.html', context)


# def menu_page(request):
#     categories = FoodItemCategory.objects.all()

#     if request.user.is_authenticated:
#         wishlist_items = list(
#             Wishlist.objects.filter(user=request.user)
#             .values_list('food_item_id', flat=True)
#         )
#     else:
#         wishlist_items = request.session.get('wishlist', [])

#     return render(request, 'menu/menu.html', {
#         'categories': categories,
#         'wishlist_items': wishlist_items
#     })


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


def menu_page(request):

    categories = FoodItemCategory.objects.prefetch_related(
        'fooditemsubcategory_set__fooditem_set__images'
    )

    all_items = FoodItem.objects.filter(
        is_available=True
    ).prefetch_related('images')

    # 🔁 OFFER HELPER
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

    # ✅ Apply offers to all items
    for item in all_items:
        apply_offer(item)

    for category in categories:
        for sub in category.fooditemsubcategory_set.all():
            for item in sub.fooditem_set.all():
                apply_offer(item)

    # ❤️ WISHLIST DATA
    if request.user.is_authenticated:
        wishlist_items = list(
            Wishlist.objects.filter(user=request.user)
            .values_list('food_item_id', flat=True)
        )
    else:
        wishlist_items = request.session.get('wishlist', [])

    context = {
        'categories': categories,
        'all_items': all_items,
        'wishlist_items': wishlist_items
    }

    return render(request, 'menu/menu.html', context)


from orders.models import Notification
from django.utils import timezone
from django.db.models import Q

def customer_dashboard(request):
    customer = request.user.customer
    notifications = Notification.objects.filter(
        recipient_type='customer',
        send_datetime__lte=timezone.now(),
        read_status=False
    ).filter(
        Q(user_id__isnull=True) | Q(user_id=customer.id)
    )
    return render(request, 'menu/dashboard.html', {'notifications': notifications})


from django.shortcuts import render
from orders.models import Notification
from django.db.models import Q
from django.utils import timezone

# def customer_notifications(request):

#     notifications = Notification.objects.all().order_by('-id')

#     return render(request, 'adminpanel/customer_notifications.html', {
#         'notifications': notifications
#     })

from django.utils import timezone
from django.db.models import Q
from adminpanel.models import Notification

def customer_notifications(request):

    notifications = Notification.objects.filter(
        recipient_type='customer'
    ).filter(
        Q(user_id__isnull=True) | Q(user_id=request.user.id)
    ).order_by('-send_datetime')

    # unread ne read banavi de
    notifications.filter(read_status=False).update(read_status=True)

    return render(request, 'adminpanel/customer_notifications.html', {
        'notifications': notifications
    })
