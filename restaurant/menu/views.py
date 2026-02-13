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



from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
import re
import re
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

@login_required(login_url='customer_login')
def customer_change_password(request):
    customer = request.user
    errors = []

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 1️⃣ Old password check
        if not customer.check_password(old_password):
            errors.append("Current password is incorrect")

        # 2️⃣ New = old check
        if customer.check_password(new_password):
            errors.append("New password cannot be same as old password")

        # 3️⃣ Match check
        if new_password != confirm_password:
            errors.append("New password and confirm password do not match")

        # 4️⃣ Strength validation
        if len(new_password) < 8:
            errors.append("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", new_password):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", new_password):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r"\d", new_password):
            errors.append("Password must contain at least one number")

        # ❌ Errors
        if errors:
            return render(request, "profile/profile_page.html", {
                "errors": errors,
                "show_section": "change-password"
            })

        # ✅ SUCCESS
        customer.set_password(new_password)
        customer.save()

        messages.success(request, "Password changed successfully")
        return redirect("/profile/#change-password")

    return redirect("/profile/#change-password")

# 

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

    return render(request, 'menu/customer_notifications.html', {
        'notifications': notifications
    })




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
import uuid, re


from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import re, uuid
#from .models import Customer, FoodItem  # ensure FoodItem imported

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import uuid, re


@login_required(login_url='customer_login')
def profile_page(request):
    user = request.user

    # ---------------- SAFE CHECK ----------------
    if user.isadmin or user.is_delivery_person:
        messages.error(request, "You cannot access customer profile.")
        return redirect('customer_login')

    errors = []
    success_msg = ""
    show_modal = False

    # -------- POST = Update Profile --------
    if request.method == 'POST':
        show_modal = True
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        contactno = request.POST.get('contactno', '').strip()
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()
        profile_image = request.FILES.get('profile_image')

        # -------- VALIDATIONS --------
        if not firstname or not re.fullmatch(r"[A-Za-z ]+", firstname):
            errors.append("Invalid first name")
        if not lastname or not re.fullmatch(r"[A-Za-z ]+", lastname):
            errors.append("Invalid last name")
        if not re.fullmatch(r"\d{10}", contactno):
            errors.append("Enter valid 10 digit phone number")
        if gender not in ['Male', 'Female',]:
            errors.append("Select valid gender")
        if not address:
            errors.append("Address required")

        if profile_image:
            if profile_image.size > 2 * 1024 * 1024:
                errors.append("Profile image must be less than 2MB")
            allowed_formats = ['jpg', 'jpeg', 'png']
            ext = profile_image.name.split('.')[-1].lower()
            if ext not in allowed_formats:
                errors.append("Only JPG, JPEG, PNG images allowed")

        # -------- SAVE PROFILE IF NO ERRORS --------
        if not errors:
            user.firstname = firstname
            user.lastname = lastname
            user.contactno = contactno
            user.gender = gender
            user.address = address

            if profile_image:
                ext = profile_image.name.split('.')[-1]
                filename = f"profile_{uuid.uuid4().hex}.{ext}"
                user.profile_image.save(filename, profile_image)

            user.updationdate = timezone.now()
            user.save()
            success_msg = "Profile updated successfully"
            show_modal = False


    fields = [
        user.firstname,
        user.lastname,
        user.contactno,
        user.gender,
        user.address,
        user.profile_image
    ]
    completed = int(sum(100 / 6 for f in fields if f))

    wishlist_items = FoodItem.objects.filter(wishlist__user=user).prefetch_related('images')

    return render(request, 'profile/profile_page.html', {
        'customer': user,
        'completed': completed,
        'errors': errors,
        'success_msg': success_msg,
        'show_modal': show_modal,
        'wishlist_items': wishlist_items,
    })
