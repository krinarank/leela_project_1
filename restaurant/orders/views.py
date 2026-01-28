from django.shortcuts import get_object_or_404,render,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from adminpanel.models import *
from .models import Cart
from decimal import Decimal

from django.utils import timezone
from datetime import datetime
from .utils import generate_offer_code
from django.contrib import messages
from orders.models import *
from .utils import get_discounted_price

from django.views.decorators.csrf import csrf_exempt
from .models import Wishlist
from accounts.models import Customer
import json






# @login_required(login_url='/accounts/customer_login/')
# def add_to_cart(request, food_id):
#     if not request.user.is_authenticated:
#         return JsonResponse({'status': 'login_required'})

#     item = get_object_or_404(FoodItem, id=food_id)
#     cart_item, created = Cart.objects.get_or_create(
#         user=request.user,
#         food_item=item,
#         defaults={'quantity': 1, 'price': item.price}
#     )
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()

#     return JsonResponse({'status': 'success', 'quantity': cart_item.quantity})

@login_required(login_url='/accounts/customer_login/')
def add_to_cart(request, food_id):

    if request.method != "POST":
        return JsonResponse({'status': 'invalid'})

    item = get_object_or_404(FoodItem, id=food_id)

    # 🔥 TEMP FIX: use food price directly
    price = item.price  

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        food_item=item,
        defaults={
            'quantity': 1,
            'price': price
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({
        'status': 'success',
        'quantity': cart_item.quantity
    })


# ---------------- UPDATE QUANTITY ----------------
@login_required(login_url='/accounts/customer_login/')
def update_cart_quantity(request, food_id, action):
    try:
        cart_item = get_object_or_404(Cart, user=request.user, food_item_id=food_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Item not in cart', 'quantity': 0})

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # Quantity 0 → remove item
            cart_item.delete()
            return JsonResponse({'status': 'removed', 'quantity': 0, 'food_id': food_id})

    return JsonResponse({
        'status': 'updated',
        'quantity': cart_item.quantity,
        'food_id': food_id
    })


# ---------------- GET CART ----------------
@login_required(login_url='/accounts/customer_login/')
def get_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    items = []

    for item in cart_items:
        items.append({
            'food_id': item.food_item.id,
            'name': item.food_item.name,
            'price': str(item.price),
            'quantity': item.quantity
        })

    return JsonResponse({'items': items})


# @login_required(login_url='/accounts/customer_login/')
# def cart_page(request):
#     cart_items = Cart.objects.filter(user=request.user)

#     # calculate total_price for each item
#     for item in cart_items:
#         item.total_price = item.price * item.quantity  # per item total
#         # optional: food image
#         try:
#             item.image_url = item.food_item.images.first().img_url.url
#         except:
#             item.image_url = '/static/default_food.png'

#     # overall totals
#     item_total = sum(item.total_price for item in cart_items)
#     tax = (item_total * Decimal('0.05')).quantize(Decimal('0.01'))  # 5% GST
#     grand_total = item_total + tax

#     context = {
#         'cart_items': cart_items,
#         'item_total': item_total,
#         'tax': tax,
#         'grand_total': grand_total,
#     }
#     return render(request, 'orders/cart.html', context)


# @login_required(login_url='/accounts/customer_login/')
# def cart_page(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     today = timezone.now().date()

#     item_total = Decimal('0.00')
#     total_discount = Decimal('0.00')
#     original_total = Decimal('0.00')


#     for item in cart_items:
#         food = item.food_item
#         base_price = food.price
#         final_price = base_price
         
#         food_offer = None
#         category_offer = None
#         subcategory_offer = None
#         # 1️⃣ Food Item Offer
#         food_offer = FoodItemOfferDiscount.objects.filter(
#             food_item=food,
#             is_active=True,
#             applied_date__lte=today,
#             expiry_date__gte=today
#         ).first()

#         if food_offer:
#             if food_offer.discount_type == 'percentage':
#                 final_price = base_price - (base_price * food_offer.discount_value / 100)
#             else:
#                 final_price = base_price - food_offer.discount_value

#         # 2️⃣ Subcategory Offer
#         elif SubCategoryOfferDiscount.objects.filter(
#             subcategory=food.sub_cat,
#             is_active=True,
#             applied_date__lte=today,
#             expiry_date__gte=today
#         ).exists():

#             sub_offer = SubCategoryOfferDiscount.objects.filter(
#                  subcategory=food.sub_cat,
#                  is_active=True,
#                  applied_date__lte=today,
#                  expiry_date__gte=today
#                     ).select_related('offer').first()

#             if sub_offer:
#                 discount = sub_offer.offer.discount_percentage
#                 final_price = base_price - (base_price * discount / 100)


#         # 3️⃣ Category Offer
#         elif CategoryOfferDiscount.objects.filter(
#             category=food.sub_cat.food_item_cat,
#             is_active=True,
#             applied_date__lte=today,
#             expiry_date__gte=today
#         ).exists():

#            category_offer = CategoryOfferDiscount.objects.filter(
#                 category=food.sub_cat.food_item_cat,
#                 is_active=True,
#                 applied_date__lte=today,
#                 expiry_date__gte=today
#                  ).select_related('offer').first()

#         if category_offer:
#                  discount = category_offer.offer.discount_percentage
#                  final_price = base_price - (base_price * discount / 100)

#         # attach to item
#         item.final_price = final_price
#         item.total_price = final_price * item.quantity
#         item.original_total_price = food.price * item.quantity


#         item_discount = item.original_total_price - item.total_price
#         total_discount += item_discount
#         original_total += item.original_total_price
#         tax = (item_total * Decimal('0.05')).quantize(Decimal('0.01'))
#         grand_total = item_total + tax + Decimal('50')


#         item_total += item.total_price

#     tax = (item_total * Decimal('0.05')).quantize(Decimal('0.01'))
#     grand_total = item_total + tax

#     return render(request, 'orders/cart.html', {
#         'cart_items': cart_items,
#         'original_total': original_total,
#         'total_discount': total_discount,
#         'item_total': item_total,
#         'tax': tax,
#         'grand_total': grand_total
# })
@login_required(login_url='/accounts/customer_login/')
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    today = timezone.now().date()

    item_total = Decimal('0.00')
    total_discount = Decimal('0.00')
    original_total = Decimal('0.00')

    for item in cart_items:
        food = item.food_item
        base_price = food.price
        final_price = base_price

        # 1️⃣ Food Item Offer
        food_offer = FoodItemOfferDiscount.objects.filter(
            food_item=food,
            is_active=True,
            applied_date__lte=today,
            expiry_date__gte=today
        ).select_related('offer').first()

        if food_offer and food_offer.offer.is_currently_active():
            discount = food_offer.offer.discount_percentage
            final_price = base_price - (base_price * discount / 100)

        # 2️⃣ Subcategory Offer
        elif SubCategoryOfferDiscount.objects.filter(
            subcategory=food.sub_cat,
            is_active=True,
            applied_date__lte=today,
            expiry_date__gte=today
        ).exists():

            sub_offer = SubCategoryOfferDiscount.objects.filter(
                subcategory=food.sub_cat,
                is_active=True,
                applied_date__lte=today,
                expiry_date__gte=today
            ).select_related('offer').first()

            if sub_offer and sub_offer.offer.is_currently_active():
                discount = sub_offer.offer.discount_percentage
                final_price = base_price - (base_price * discount / 100)

        # 3️⃣ Category Offer
        elif CategoryOfferDiscount.objects.filter(
            category=food.sub_cat.food_item_cat,
            is_active=True,
            applied_date__lte=today,
            expiry_date__gte=today
        ).exists():

            category_offer = CategoryOfferDiscount.objects.filter(
                category=food.sub_cat.food_item_cat,
                is_active=True,
                applied_date__lte=today,
                expiry_date__gte=today
            ).select_related('offer').first()

            if category_offer and category_offer.offer.is_currently_active():
                discount = category_offer.offer.discount_percentage
                final_price = base_price - (base_price * discount / 100)

        # Attach calculated values
        item.final_price = final_price
        item.total_price = final_price * item.quantity
        item.original_total_price = base_price * item.quantity

        item_discount = item.original_total_price - item.total_price

        total_discount += item_discount
        original_total += item.original_total_price
        item_total += item.total_price

    tax = (item_total * Decimal('0.05')).quantize(Decimal('0.01'))
    grand_total = item_total + tax

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'original_total': original_total,
        'total_discount': total_discount,
        'item_total': item_total,
        'tax': tax,
        'grand_total': grand_total,
    })

@login_required
def increase_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.quantity += 1
    discounted_price = get_discounted_price(cart_item.food_item)
    cart_item.price = discounted_price * cart_item.quantity
    cart_item.save()
    return redirect('cart')
# def increase_qty(request, item_id):
#     item = Cart.objects.get(id=item_id)
#     item.quantity += 1

#     discounted_price = get_discounted_price(item.food_item)
#     item.price = discounted_price * item.quantity

#     item.save()
#     return redirect('cart_page')


@login_required
def decrease_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        discounted_price = get_discounted_price(cart_item.food_item)
        cart_item.price = discounted_price * cart_item.quantity
        cart_item.save()
    else: 
        # quantity 1 chhe to remove kari devu
        cart_item.delete()
    return redirect('cart')
# def decrease_qty(request, item_id):
#     item = Cart.objects.get(id=item_id)

#     if item.quantity > 1:
#         item.quantity -= 1

#     discounted_price = get_discounted_price(item.food_item)
#     item.price = discounted_price * item.quantity

#     item.save()
#     return redirect('cart_page')


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('menu_page')
    total = sum(item.food_item.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    cart_total = sum(item.total_price for item in cart_items)

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


@login_required
def remove_item(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_page')


def create_offer(request):
    offers = OfferDiscount.objects.all()

    if request.method == "POST":
        description = request.POST.get("description")
        discount = request.POST.get("discount_percentage")
        offer_code = request.POST.get("offer_code")
        valid_from = request.POST.get("valid_from")
        valid_to = request.POST.get("valid_to")
        isactive = bool(request.POST.get("isactive"))

        # ✅ Ensure code exists
        if not offer_code:
            # fallback code if JS fails
            import random, string
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            digits = ''.join(random.choices('0123456789', k=3))
            offer_code = letters + digits

        # Save in DB
        OfferDiscount.objects.create(
            description=description,
            discount_percentage=discount,
            offer_code=offer_code,
            valid_from=valid_from,
            valid_to=valid_to,
            isactive=isactive
        )

        return redirect('create_offer')

    return render(request, 'adminpanel/offers/create_offer.html', {'offers': offers})

@login_required
def offer_delete(request, id):
    offer = get_object_or_404(OfferDiscount, id=id)
    offer.delete()
    return redirect('create_offer')  # page reload after delete

@login_required
def offer_update(request, offer_id):
    offer = get_object_or_404(OfferDiscount, id=offer_id)
    error = None

    if request.method == 'POST':
        description = request.POST.get('description')
        discount_percentage = request.POST.get('discount_percentage')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        offer_code = request.POST.get('offer_code')
        isactive = request.POST.get('isactive') == 'on'

        if valid_from > valid_to:
            error = 'Valid To date should be after Valid From date'
        else:
            offer.description = description
            offer.discount_percentage = discount_percentage
            offer.valid_from = valid_from
            offer.valid_to = valid_to
            offer.offer_code = offer_code
            offer.isactive = isactive
            offer.save()
            # redirect with success query param
            return redirect(f"{request.path}?success=1")

    return render(request, 'adminpanel/offers/offer_update.html', {
        'offer': offer,
        'error': error
    })


@login_required
def apply_offer(request):

    offers = OfferDiscount.objects.filter(isactive=True)
    items = FoodItem.objects.all()   # 🔥 FIX
    categories = FoodItemCategory.objects.all()
    subcategories = FoodItemSubCategory.objects.all()
    selected_subcategories = []



    if request.method == "POST":
        offer_id = request.POST.get("offer")
        apply_type = request.POST.get("apply_type")

        offer = get_object_or_404(OfferDiscount, id=offer_id)

        applied_date = offer.valid_from
        expiry_date = offer.valid_to

        if apply_type == "item":
            selected_items = request.POST.getlist("items")

            for item_id in selected_items:
                FoodItemOfferDiscount.objects.create(
                    offer=offer,
                    food_item_id=item_id,
                    applied_date=applied_date,
                    expiry_date=expiry_date,
                    is_active=True
                )

        elif apply_type == "category":
            selected_categories = request.POST.getlist("categories")

            for cat_id in selected_categories:
                CategoryOfferDiscount.objects.create(
                    offer=offer,
                    category_id=cat_id,
                    applied_date=applied_date,
                    expiry_date=expiry_date,
                    is_active=True
                )

        elif apply_type == "subcategory":
           selected_subcategories = request.POST.getlist("subcategories")
           

        for sub_id in selected_subcategories:
          SubCategoryOfferDiscount.objects.create(
            offer=offer,
            subcategory_id=sub_id,
            applied_date=applied_date,
            expiry_date=expiry_date,
            is_active=True
        )

        messages.success(request, "✅ Offer applied successfully!")
        return redirect("apply_offer")

    return render(request, "adminpanel/offers/apply_offer.html", {
        "offers": offers,
        "items": items,
        "categories": categories,
        "subcategories": subcategories


    })


@login_required
def current_offers(request):
    today = timezone.now().date()

    # Filter only currently active offers
    food_item_offers = FoodItemOfferDiscount.objects.filter(
        is_active=True,
        offer__isactive=True,
        applied_date__lte=today,
        expiry_date__gte=today
    ).select_related('offer', 'food_item')

    category_offers = CategoryOfferDiscount.objects.filter(
        is_active=True,
        offer__isactive=True,
        applied_date__lte=today,
        expiry_date__gte=today
    ).select_related('offer', 'category')

    subcategory_offers = SubCategoryOfferDiscount.objects.filter(
        is_active=True,
        offer__isactive=True,
        applied_date__lte=today,
        expiry_date__gte=today
    ).select_related('offer', 'subcategory')

    context = {
        "food_item_offers": food_item_offers,
        "category_offers": category_offers,
        "subcategory_offers": subcategory_offers,
    }

    return render(request, "adminpanel/offers/current_offers.html", context)





# Toggle wishlist (logged in users only)

@csrf_exempt
def toggle_wishlist(request, food_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    food_id = int(food_id)   # 🔥 IMPORTANT FIX

    # ===============================
    # 🔹 LOGGED-IN USER → DATABASE
    # ===============================
    if request.user.is_authenticated:
        food_item = get_object_or_404(FoodItem, id=food_id)

        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            food_item=food_item
        ).first()

        if wishlist_item:
            wishlist_item.delete()
            return JsonResponse({"is_wishlisted": False})

        Wishlist.objects.create(
            user=request.user,
            food_item=food_item
        )
        return JsonResponse({"is_wishlisted": True})

    # ===============================
    # 🔹 GUEST USER → SESSION
    # ===============================
    wishlist = request.session.get("wishlist", [])

    if food_id in wishlist:          # ✅ NOW MATCHES
        wishlist.remove(food_id)     # ✅ REMOVE FROM SESSION
        is_wishlisted = False
    else:
        wishlist.append(food_id)
        is_wishlisted = True

    request.session["wishlist"] = wishlist
    request.session.modified = True

    return JsonResponse({"is_wishlisted": is_wishlisted})

# @csrf_exempt
# def toggle_wishlist(request, food_id):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=400)
    

#     # 🔹 LOGGED-IN USER
#     if request.user.is_authenticated:
#         food_item = get_object_or_404(FoodItem, id=food_id)

#         wishlist_item = Wishlist.objects.filter(
#             user=request.user,
#             food_item=food_item
#         ).first()

#         if wishlist_item:
#             wishlist_item.delete()
#             return JsonResponse({"is_wishlisted": False})

#         Wishlist.objects.create(user=request.user, food_item=food_item)
#         return JsonResponse({"is_wishlisted": True})

#     # 🔹 GUEST USER → SESSION
#     wishlist = request.session.get("wishlist", [])

#     if food_id in wishlist:
#         wishlist.remove(food_id)
#         is_wishlisted = False
#     else:
#         wishlist.append(food_id)
#         is_wishlisted = True

#     request.session["wishlist"] = wishlist
#     request.session.modified = True

#     return JsonResponse({"is_wishlisted": is_wishlisted})



def add_to_wishlist(request, food_id):
    if request.user.is_authenticated:
        # Logged-in user → DB
        Wishlist.objects.get_or_create(user=request.user, food_item_id=food_id)
    else:
        # Guest user → session
        wishlist = request.session.get('wishlist', [])
        if food_id not in wishlist:
            wishlist.append(food_id)
            request.session['wishlist'] = wishlist
            request.session.modified = True  # 💡 important
    return redirect('my_wishlist')


def remove_from_wishlist(request, food_id):
    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, food_item_id=food_id).delete()
    else:
        wishlist = request.session.get('wishlist', [])
        if food_id in wishlist:
            wishlist.remove(food_id)
            request.session['wishlist'] = wishlist
            request.session.modified = True  # 💡 important
    return redirect('my_wishlist')


def my_wishlist(request):
    """
    Wishlist page – menu jeva cards sathe
    """

    # 🔹 Logged-in user
    if request.user.is_authenticated:
        wishlist_items = FoodItem.objects.filter(
            wishlist__user=request.user   # Wishlist FK
        ).prefetch_related('images')

    # 🔹 Guest user
    else:
        wishlist_ids = request.session.get('wishlist', [])
        wishlist_items = FoodItem.objects.filter(
            id__in=wishlist_ids
        ).prefetch_related('images')

    return render(request, 'orders/wishlist.html', {
        'wishlist_items': wishlist_items
    })

