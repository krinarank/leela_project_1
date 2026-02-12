import json
import re
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder

from adminpanel.models import FoodItemCategory, FoodItemSubCategory, FoodItem, FoodItemImage
from orders.models import Wishlist, Notification
from .models import Inquiry
from orders.utils import get_best_offer
from orders.models import Cart
from accounts.forms import CustomerProfileForm


def home(request):
    special_items = FoodItem.objects.filter(
        is_special=True,
        is_available=True
    ).prefetch_related('images')

    return render(request, 'menu/home.html', {
        'special_items': special_items
    })


# def menu_page(request):
#     """
#     Combined menu_page:
#     - Categories + Subcategories
#     - Apply offers
#     - Wishlist (authenticated/session)
#     - Cart items prefill (quantity & Go to Cart)
#     """

#     # =================== CATEGORIES & ITEMS ===================
#     categories = FoodItemCategory.objects.prefetch_related(
#         'fooditemsubcategory_set__fooditem_set__images'
#     )
#     all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

#     # =================== APPLY OFFERS ===================
#     def apply_offer(item):
#         offer = get_best_offer(item)
#         if offer:
#             discount = offer.offer.discount_percentage
#             item.offer_percent = discount
#             item.discounted_price = round(item.price - (item.price * discount / 100), 2)
#             item.has_offer = True
#         else:
#             item.has_offer = False

#     for item in all_items:
#         apply_offer(item)

#     for category in categories:
#         for sub in category.fooditemsubcategory_set.all():
#             for item in sub.fooditem_set.all():
#                 apply_offer(item)

#     # =================== WISHLIST ===================
#     if request.user.is_authenticated:
#         wishlist_items = list(
#             Wishlist.objects.filter(user=request.user)
#             .values_list('food_item_id', flat=True)
#         )
#     else:
#         wishlist_items = request.session.get('wishlist', [])

#     # =================== CART ===================
#     # Build a dict {food_item_id: quantity}
#     # =================== CART ===================
#     cart_items = {}

#     if request.user.is_authenticated:
#     # Related name check
#      if hasattr(request.user, 'cart_items'):
#          cart_qs = request.user.cart_items.all()
#          for ci in cart_qs:
#             cart_items[ci.food_item.id] = ci.quantity
#          else:
#         # Fallback, agar related_name nathi set
#            cart_items = {}
#     else:
#        cart_items = request.session.get('cart', {})

#     cart_items_json = json.dumps(cart_items, cls=DjangoJSONEncoder)

#     # =================== CONTEXT ===================
#     context = {
#         'categories': categories,
#         'all_items': all_items,
#         'wishlist_items': wishlist_items,
#         'cart_items_json': cart_items_json,
#     }

#     return render(request, 'menu/menu.html', context)
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render



def menu_page(request):
    """
    Combined menu_page:
    - Categories + Subcategories
    - Apply offers
    - Wishlist
    - Cart items prefill (variant ready structure)
    """

    # =================== CATEGORIES & ITEMS ===================
    categories = FoodItemCategory.objects.prefetch_related(
        'fooditemsubcategory_set__fooditem_set__images'
    )

    all_items = FoodItem.objects.filter(is_available=True).prefetch_related('images')

    # =================== APPLY OFFERS ===================
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

    # Apply on all items
    for item in all_items:
        apply_offer(item)

    for category in categories:
        for sub in category.fooditemsubcategory_set.all():
            for item in sub.fooditem_set.all():
                apply_offer(item)

    # =================== WISHLIST ===================
    if request.user.is_authenticated:
        wishlist_items = list(
            Wishlist.objects.filter(user=request.user)
            .values_list('food_item_id', flat=True)
        )
    else:
        wishlist_items = request.session.get('wishlist', [])

    # =================== CART (VARIANT READY STRUCTURE) ===================
    cart_items = {}

    if request.user.is_authenticated:
        cart_qs = Cart.objects.filter(user=request.user)

        for ci in cart_qs:
            food_id = str(ci.food_item.id)
            variant_id = str(ci.variant.id) if ci.variant else "default"

            if food_id not in cart_items:
                cart_items[food_id] = {
                    "total_qty": 0,
                    "variants": {}
                }

            cart_items[food_id]["variants"][variant_id] = {
                "qty": ci.quantity
            }

            cart_items[food_id]["total_qty"] += ci.quantity

    else:
        # If guest session cart simple structure hoy to pan support kariye
        session_cart = request.session.get("cart", {})

        for food_id, qty in session_cart.items():
            cart_items[str(food_id)] = {
                "total_qty": qty,
                "variants": {
                    "default": {"qty": qty}
                }
            }

    cart_items_json = json.dumps(cart_items, cls=DjangoJSONEncoder)

    # =================== CONTEXT ===================
    context = {
        "categories": categories,
        "all_items": all_items,
        "wishlist_items": wishlist_items,
        "cart_items_json": cart_items_json,
        "cart_items_json": json.dumps(cart_items), 
    }

    return render(request, "menu/menu.html", context)


def about(request):
    return render(request, 'menu/about.html')


def contact(request):
    return render(request, 'menu/contact.html')


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


@login_required(login_url='customer_login')
def customer_dashboard(request):
    customer = request.user.customer
    notifications = Notification.objects.filter(
        recipient_type='customer',
        send_datetime__lte=timezone.now(),
        read_status=False
    ).filter(Q(user_id__isnull=True) | Q(user_id=customer.id))
    return render(request, 'menu/dashboard.html', {'notifications': notifications})


@login_required(login_url='customer_login')
def customer_notifications(request):
    notifications = Notification.objects.filter(
        recipient_type='customer'
    ).filter(Q(user_id__isnull=True) | Q(user_id=request.user.id)).order_by('-send_datetime')

    # mark unread as read
    notifications.filter(read_status=False).update(read_status=True)

    return render(request, 'adminpanel/customer_notifications.html', {
        'notifications': notifications
    })


@login_required(login_url='customer_login')
def customer_profile(request):
    customer = request.user
    errors = []
    success_msg = ""
    show_modal = False

    if request.method == 'POST':
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        contactno = request.POST.get('contactno', '').strip()
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()
        profile_image = request.FILES.get('profile_image')

        if not firstname:
            errors.append("First name is required")
        elif not re.fullmatch(r"[A-Za-z ]+", firstname):
            errors.append("First name can contain only letters and spaces")

        if not lastname:
            errors.append("Last name is required")
        elif not re.fullmatch(r"[A-Za-z ]+", lastname):
            errors.append("Last name can contain only letters and spaces")

        if not contactno:
            errors.append("Phone number is required")
        elif not re.fullmatch(r"\d{10}", contactno):
            errors.append("Enter a valid 10-digit phone number")

        if gender not in ['Male', 'Female', 'Other']:
            errors.append("Select a valid gender")

        if not address:
            errors.append("Address is required")

        if profile_image:
            if profile_image.size > 2 * 1024 * 1024:
                errors.append("Profile image size should be less than 2MB")
            if profile_image.content_type not in ['image/jpeg', 'image/png']:
                errors.append("Only JPEG or PNG images are allowed")

        if errors:
            show_modal = True
        else:
            customer.firstname = firstname
            customer.lastname = lastname
            customer.contactno = contactno
            customer.gender = gender
            customer.address = address

            if profile_image:
                ext = profile_image.name.split('.')[-1]
                filename = f"profile_{uuid.uuid4().hex}.{ext}"
                customer.profile_image.save(filename, profile_image)

            customer.updationdate = timezone.now()
            customer.save()
            success_msg = "Profile updated successfully"

    fields = [
        customer.firstname,
        customer.lastname,
        customer.contactno,
        customer.gender,
        customer.address,
        customer.profile_image
    ]
    completed = int(sum(100/6 for f in fields if f))

    return render(request, 'menu/profile.html', {
        'customer': customer,
        'completed': completed,
        'errors': errors,
        'success_msg': success_msg,
        'show_modal': show_modal
    })


@login_required(login_url='customer_login')
def customer_change_password(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        user = request.user

        if not user.check_password(old):
            messages.error(request, "Current password is incorrect")
            return redirect('customer_profile')

        if new != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('customer_profile')

        if len(new) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect('customer_profile')

        user.set_password(new)
        user.save()
        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully")
        return redirect('customer_profile')
