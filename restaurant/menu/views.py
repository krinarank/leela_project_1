from django.shortcuts import render, redirect
from django.contrib import messages

from adminpanel.models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem,
    FoodItemImage
)
from accounts.forms import CustomerProfileForm
from django.contrib.auth.decorators import login_required

from .models import Inquiry
from orders.utils import get_best_offer
from decimal import Decimal

from django.contrib.auth.decorators import login_required
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

# @login_required(login_url='customer_login')
# def customer_profile(request):
#     customer = request.user  # logged-in Customer

#     if request.method == 'POST':
#         form = CustomerProfileForm(
#             request.POST,
#             request.FILES,
#             instance=customer
#         )
#         if form.is_valid():
#             obj=form.save()
#             print(obj.profile_image.url)  # ✅ ye URL console me dekho
#             messages.success(request, "Profile updated successfully")
#             return redirect('customer_profile')
#     else:
#         form = CustomerProfileForm(instance=customer)

#     # 🔥 Profile completion %
#     completed = 0
#     fields = [
#         customer.firstname,
#         customer.lastname,
#         customer.contactno,
#         customer.address,
#         customer.profile_image
#     ]
#     completed = sum(20 for f in fields if f)

#     return render(request, 'menu/profile.html', {
#         'form': form,
#         'customer': customer,
#         'completed': completed
#     })


# @login_required(login_url='customer_login')
# def customer_profile(request):
#     customer = request.user

#     if request.method == 'POST':
#         # Collect POST data
#         firstname = request.POST.get('firstname', '').strip()
#         lastname = request.POST.get('lastname', '').strip()
#         contactno = request.POST.get('contactno', '').strip()
#         gender = request.POST.get('gender', '').strip()
#         address = request.POST.get('address', '').strip()
#         profile_image = request.FILES.get('profile_image')

#         # ---------------- VALIDATION ----------------
#         errors = []

#         if not firstname:
#             errors.append("First name is required")
#         if not lastname:
#             errors.append("Last name is required")
#         if not contactno:
#             errors.append("Phone number is required")
#         elif not contactno.isdigit() or len(contactno) < 10:
#             errors.append("Enter a valid 10-digit phone number")
#         if gender not in ['Male', 'Female', 'Other']:
#             errors.append("Select a valid gender")
#         if not address:
#             errors.append("Address is required")

#         if profile_image:
#             if profile_image.size > 2 * 1024 * 1024:  # 2 MB limit
#                 errors.append("Profile image size should be less than 2MB")
#             if not profile_image.content_type in ['image/jpeg', 'image/png']:
#                 errors.append("Only JPEG or PNG images are allowed")

#         if errors:
#             # Show all errors
#             for e in errors:
#                 messages.error(request, e)
#         else:
#             # Save data
#             customer.firstname = firstname
#             customer.lastname = lastname
#             customer.contactno = contactno
#             customer.gender = gender
#             customer.address = address
#             if profile_image:
#                 customer.profile_image = profile_image
#             customer.save()
#             messages.success(request, "Profile updated successfully")
#             return redirect('customer_profile')

#     # Profile completion %
#     fields = [
#         customer.firstname,
#         customer.lastname,
#         customer.contactno,
#         customer.address,
#         customer.profile_image
#     ]
#     completed = sum(20 for f in fields if f)

#     return render(request, 'menu/profile.html', {
#         'customer': customer,
#         'completed': completed
#     })

###workinggggggggggggggggggggggggggg

# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.shortcuts import render
# from django.utils import timezone

# @login_required(login_url='customer_login')
# def customer_profile(request):
#     customer = request.user
#     show_modal = False  # Flag to keep modal open if errors

#     if request.method == 'POST':
#         # Collect POST data
#         firstname = request.POST.get('firstname', '').strip()
#         lastname = request.POST.get('lastname', '').strip()
#         contactno = request.POST.get('contactno', '').strip()
#         gender = request.POST.get('gender', '').strip()
#         address = request.POST.get('address', '').strip()
#         profile_image = request.FILES.get('profile_image')

#         errors = []

#         if not firstname:
#             errors.append("First name is required")
#         if not lastname:
#             errors.append("Last name is required")
#         if not contactno:
#             errors.append("Phone number is required")
#         elif not contactno.isdigit() or len(contactno) != 10:
#             errors.append("Enter a valid 10-digit phone number")
#         if gender not in ['Male', 'Female', 'Other']:
#             errors.append("Select a valid gender")
#         if not address:
#             errors.append("Address is required")

#         if profile_image:
#             if profile_image.size > 2 * 1024 * 1024:  # 2 MB limit
#                 errors.append("Profile image size should be less than 2MB")
#             if not profile_image.content_type in ['image/jpeg', 'image/png']:
#                 errors.append("Only JPEG or PNG images are allowed")

#         if errors:
#             # Don't redirect, show errors in modal
#             for e in errors:
#                 messages.error(request, e)
#             show_modal = True
#         else:
#             # Save valid data
#             customer.firstname = firstname
#             customer.lastname = lastname
#             customer.contactno = contactno
#             customer.gender = gender
#             customer.address = address
#             if profile_image:
#                 customer.profile_image = profile_image
#             customer.updationdate = timezone.now()  # Update timestamp for cache-busting
#             customer.save()
#             messages.success(request, "Profile updated successfully")

#     # Profile completion %
#     fields = [
#         customer.firstname,
#         customer.lastname,
#         customer.contactno,
#         customer.address,
#         customer.profile_image
#     ]
#     completed = sum(20 for f in fields if f)

#     return render(request, 'menu/profile.html', {
#         'customer': customer,
#         'completed': completed,
#         'show_modal': show_modal
#     })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
import uuid
import re

@login_required(login_url='customer_login')
def customer_profile(request):
    customer = request.user
    errors = []
    success_msg = ""
    show_modal = False  # Only open modal if errors

    if request.method == 'POST':
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        contactno = request.POST.get('contactno', '').strip()
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()
        profile_image = request.FILES.get('profile_image')

        # ===== Validation =====
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

        # ===== Handle errors =====
        if errors:
            show_modal = True
        else:
            # ===== Save data =====
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

    # ===== Profile completion =====
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


from django.contrib.auth import update_session_auth_hash

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
# 
