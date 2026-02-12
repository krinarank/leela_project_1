from django.shortcuts import get_object_or_404,render,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from adminpanel.models import *
from .models import Cart
from decimal import Decimal
from location.models import Area
from django.utils import timezone
from datetime import datetime
from .utils import generate_offer_code
from django.contrib import messages
from django.db import transaction
from orders.models import *
from .utils import get_discounted_price
from .models import Order, OrderDetail, Payment
from orders.models import Wallet,WalletTransaction
from django.views.decorators.csrf import csrf_exempt
from .models import Wishlist
from accounts.models import Customer
import json
from .models import FeedbackRating




@login_required(login_url='/accounts/customer_login/')
def add_to_cart(request, food_id):

    if request.method != "POST":
        return JsonResponse({'status': 'invalid'})

    item = get_object_or_404(FoodItem, id=food_id)

    # 🔥 TEMP FIX: use food price directly
    # price = item.price  
    discounted_price = get_discounted_price(item)


    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        food_item=item,
        defaults={
            'quantity': 1,
            'price': discounted_price 
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
    delivery_charge = Decimal('50.00')

    grand_total = item_total + tax + delivery_charge

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
    cart_item.price = get_discounted_price(cart_item.food_item)  # ✅ UNIT PRICE
    cart_item.save()
    return redirect('cart_page')


@login_required
def decrease_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.price = get_discounted_price(cart_item.food_item)
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_page')

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


@login_required
def apply_offer(request):
    today = timezone.now().date()

    # ✅ ONLY CURRENTLY ACTIVE OFFERS (NO EXPIRED)
    offers = OfferDiscount.objects.filter(
        isactive=True,
        valid_from__lte=today,
        valid_to__gte=today
    )

    items = FoodItem.objects.all()
    categories = FoodItemCategory.objects.all()
    subcategories = FoodItemSubCategory.objects.all()

    if request.method == "POST":
        offer_id = request.POST.get("offer")
        apply_type = request.POST.get("apply_type")

        offer = get_object_or_404(
            OfferDiscount,
            id=offer_id,
            isactive=True,
            valid_from__lte=today,
            valid_to__gte=today
        )

        applied_date = offer.valid_from
        expiry_date = offer.valid_to

        # ================= ITEM OFFER =================
        if apply_type == "item":
            selected_items = request.POST.getlist("items")

            for item_id in selected_items:
                already_exists = FoodItemOfferDiscount.objects.filter(
                    food_item_id=item_id,
                    is_active=True,
                    applied_date__lte=today,
                    expiry_date__gte=today
                ).exists()

                if already_exists:
                    messages.warning(
                        request,
                        "⚠️ This food item already has an active offer"
                    )
                    return redirect("apply_offer")

                FoodItemOfferDiscount.objects.create(
                    offer=offer,
                    food_item_id=item_id,
                    applied_date=applied_date,
                    expiry_date=expiry_date,
                    is_active=True
                )

        # ================= CATEGORY OFFER =================
        elif apply_type == "category":
            selected_categories = request.POST.getlist("categories")

            for cat_id in selected_categories:
                already_exists = CategoryOfferDiscount.objects.filter(
                    category_id=cat_id,
                    is_active=True,
                    applied_date__lte=today,
                    expiry_date__gte=today
                ).exists()

                if already_exists:
                    messages.warning(
                        request,
                        "⚠️ This category already has an active offer"
                    )
                    return redirect("apply_offer")

                CategoryOfferDiscount.objects.create(
                    offer=offer,
                    category_id=cat_id,
                    applied_date=applied_date,
                    expiry_date=expiry_date,
                    is_active=True
                )

        # ================= SUBCATEGORY OFFER =================
        elif apply_type == "subcategory":
            selected_subcategories = request.POST.getlist("subcategories")

            for sub_id in selected_subcategories:
                already_exists = SubCategoryOfferDiscount.objects.filter(
                    subcategory_id=sub_id,
                    is_active=True,
                    applied_date__lte=today,
                    expiry_date__gte=today
                ).exists()

                if already_exists:
                    messages.warning(
                        request,
                        "⚠️ This subcategory already has an active offer"
                    )
                    return redirect("apply_offer")

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
def delete_active_offer(request, type, id):

    if type == "item":
        obj = get_object_or_404(FoodItemOfferDiscount, id=id)
    elif type == "category":
        obj = get_object_or_404(CategoryOfferDiscount, id=id)
    elif type == "subcategory":
        obj = get_object_or_404(SubCategoryOfferDiscount, id=id)
    else:
        messages.error(request, "Invalid offer type")
        return redirect("current_offer")

    obj.delete()
    messages.success(request, "✅ Active offer deleted successfully")
    return redirect("current_offer")


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


# def my_wishlist(request):

#     # 🔹 Logged-in user
#     if request.user.is_authenticated:
#         wishlist_items = FoodItem.objects.filter(
#             wishlist__user=request.user   # Wishlist FK
#         ).prefetch_related('images')

#     # 🔹 Guest user
#     else:
#         wishlist_ids = request.session.get('wishlist', [])
#         wishlist_items = FoodItem.objects.filter(
#             id__in=wishlist_ids
#         ).prefetch_related('images')

#     return render(request, 'orders/wishlist.html', {
#         'wishlist_items': wishlist_items
#     })
from orders.utils import get_best_offer

def my_wishlist(request):

    if request.user.is_authenticated:
        wishlist_items = FoodItem.objects.filter(
            wishlist__user=request.user
        ).prefetch_related('images')
    else:
        wishlist_ids = request.session.get('wishlist', [])
        wishlist_items = FoodItem.objects.filter(
            id__in=wishlist_ids
        ).prefetch_related('images')

    # 🔁 APPLY OFFER (MENU JEVI)
    for item in wishlist_items:
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

    return render(request, 'orders/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    
    steps = ["PLACED", "CONFIRMED", "PREPARING", "OUT_FOR_DELIVERY", "DELIVERED"]

    return render(request, "orders/my_orders.html", {
        "orders": orders,
        "steps": steps
    })


from orders.utils import get_discounted_price   # ⚠️ je file ma hoy tya thi import karje


# @login_required
# def order_detail(request, order_id):

#     # ================= ORDER =================
#     order = get_object_or_404(
#         Order,
#         id=order_id,
#         user=request.user
#     )

#     order_items = OrderDetail.objects.filter(order=order).select_related("food_item")

#     # ================= TOTALS =================
#     original_total = Decimal("0.00")
#     item_total = Decimal("0.00")
#     total_discount = Decimal("0.00")

#     for item in order_items:
#         # original price (qty sathe)
#         original_price = item.food_item.price * item.qty
#         original_total += original_price

#         # 🔥 discounted price (runtime)
#         discounted_price = get_discounted_price(item.food_item) * item.qty
#         item_total += discounted_price

#         # discount per item
#         item_discount = original_price - discounted_price
#         total_discount += item_discount

#         # 🔥 attach extra values to item (HTML mate)
#         item.discounted_price = discounted_price
#         item.item_discount = item_discount

#     # ================= EXTRA CHARGES =================
#     tax = (item_total * Decimal("0.05")).quantize(Decimal("0.01"))
#     delivery_charge = Decimal("50.00")   # tu area-wise pan kari sake

#     grand_total = item_total + tax + delivery_charge

#     # ================= CONTEXT =================
#     context = {
#         "order": order,
#         "order_items": order_items,

#         # checkout-style values
#         "original_total": original_total,
#         "total_discount": total_discount,
#         "item_total": item_total,
#         "tax": tax,
#         "delivery_charge": delivery_charge,
#         "grand_total": grand_total,
#     }

#     return render(request, "orders/order_detail.html", context)
# @login_required
# def order_detail(request, order_id):
#     # ================= ORDER =================
#     order = get_object_or_404(
#         Order,
#         id=order_id,
#         user=request.user
#     )
#     order_items = OrderDetail.objects.filter(order=order).select_related("food_item")

#     # ================= TOTALS =================
#     original_total = Decimal("0.00")
#     item_total = Decimal("0.00")
#     total_discount = Decimal("0.00")

#     for item in order_items:
#         original_price = item.food_item.price * item.qty
#         original_total += original_price

#         discounted_price = get_discounted_price(item.food_item) * item.qty
#         item_total += discounted_price

#         item_discount = original_price - discounted_price
#         total_discount += item_discount

#         item.discounted_price = discounted_price
#         item.item_discount = item_discount

#     tax = (item_total * Decimal("0.05")).quantize(Decimal("0.01"))
#     delivery_charge = Decimal("50.00")
#     grand_total = item_total + tax + delivery_charge

#     # ================= STATUS TRACKER =================
#     steps = ["placed", "confirmed", "preparing", "out_for_delivery", "delivered"]
#     try:
#         current_index = steps.index(order.order_status.lower())
#     except ValueError:
#         current_index = 0

#     # ================= CONTEXT =================
#     context = {
#         "order": order,
#         "order_items": order_items,
#         "original_total": original_total,
#         "total_discount": total_discount,
#         "item_total": item_total,
#         "tax": tax,
#         "delivery_charge": delivery_charge,
#         "grand_total": grand_total,
#         "steps": steps,
#         "current_index": current_index,
#     }

#     return render(request, "orders/order_detail.html", context)


from .models import FeedbackRating

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderDetail.objects.filter(order=order).select_related("food_item")

    # ================= TOTALS =================
    original_total = Decimal("0.00")
    item_total = Decimal("0.00")
    total_discount = Decimal("0.00")

    for item in order_items:
        original_price = item.food_item.price * item.qty
        original_total += original_price

        discounted_price = get_discounted_price(item.food_item) * item.qty
        item_total += discounted_price

        item_discount = original_price - discounted_price
        total_discount += item_discount

        item.discounted_price = discounted_price
        item.item_discount = item_discount

    tax = (item_total * Decimal("0.05")).quantize(Decimal("0.01"))
    delivery_charge = Decimal("50.00")
    grand_total = item_total + tax + delivery_charge

    # ================= STATUS TRACKER =================
    steps = ["placed", "confirmed", "preparing", "out_for_delivery", "delivered"]
    try:
        current_index = steps.index(order.order_status.lower())
    except:
        current_index = 0

    # ================= FEEDBACK LOGIC =================
    feedback = FeedbackRating.objects.filter(order=order, user=request.user).first()

    if request.method == "POST" and order.order_status.upper() == "DELIVERED":
        if not feedback:
            rating = request.POST.get("rating")
            feedback_text = request.POST.get("feedback_text")

            FeedbackRating.objects.create(
                user=request.user,
                order=order,
                rating=rating,
                feedback_text=feedback_text
            )
            return redirect("order_detail", order_id=order.id)

    context = {
        "order": order,
        "order_items": order_items,
        "original_total": original_total,
        "total_discount": total_discount,
        "item_total": item_total,
        "tax": tax,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
        "steps": steps,
        "current_index": current_index,
        "feedback": feedback,   # 🔴 VERY IMPORTANT
    }

    return render(request, "orders/order_detail.html", context)


@login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('menu_page')

    today = timezone.now().date()

    original_total = Decimal("0.00")
    item_total = Decimal("0.00")
    total_discount = Decimal("0.00")

    # ================= CART CALCULATION =================
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
        ).select_related("offer").first()

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
            ).select_related("offer").first()

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

            cat_offer = CategoryOfferDiscount.objects.filter(
                category=food.sub_cat.food_item_cat,
                is_active=True,
                applied_date__lte=today,
                expiry_date__gte=today
            ).select_related("offer").first()

            if cat_offer and cat_offer.offer.is_currently_active():
                discount = cat_offer.offer.discount_percentage
                final_price = base_price - (base_price * discount / 100)

        original_line = base_price * item.quantity
        final_line = final_price * item.quantity

        original_total += original_line
        item_total += final_line
        total_discount += (original_line - final_line)

    # ================= TAX / DELIVERY =================
    tax = (item_total * Decimal("0.05")).quantize(Decimal("0.01"))
    delivery_charge = Decimal("50.00")
    grand_total = item_total + tax + delivery_charge

    # ================= WALLET =================
    wallet, _ = Wallet.objects.get_or_create(
        user=user,
        defaults={"balance": Decimal("0.00")}
    )

    # ================= AREAS =================
    areas = Area.objects.select_related("city", "city__state").all()

    # ================= CONTEXT =================
    context = {
        "cart_items": cart_items,
        "original_total": original_total,
        "total_discount": total_discount,
        "item_total": item_total,
        "tax": tax,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
        "wallet_balance": wallet.balance,
        "areas": areas,
    }

    return render(request, "orders/checkout.html", context)


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    cart_total = sum(item.total_price for item in cart_items)

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


from decimal import Decimal, InvalidOperation

def safe_decimal(val, default="0.00"):
    try:
        if val in [None, ""]:
            return Decimal(default)
        return Decimal(val)
    except InvalidOperation:
        return Decimal(default)

@login_required
@transaction.atomic
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect("cart_page")

    area = get_object_or_404(Area, id=request.POST.get("area_id"))

    # ✅ SAFE VALUES FROM CHECKOUT
    subtotal = safe_decimal(request.POST.get("final_subtotal"))
    tax = safe_decimal(request.POST.get("final_tax"))
    delivery_charge = safe_decimal(request.POST.get("final_delivery"))
    grand_total = safe_decimal(request.POST.get("final_grand_total"))
    total_discount = safe_decimal(request.POST.get("final_discount"))

    # 🛑 ABSOLUTE SAFETY FALLBACK
    if grand_total <= 0:
        # fallback to cart calculation (last option)
        for item in cart_items:
            subtotal += item.price * item.quantity
        tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
        delivery_charge = Decimal("50.00")
        grand_total = subtotal + tax + delivery_charge

    order = Order.objects.create(
        user=user,
        area=area,
        delivery_address=f"{request.POST.get('address')}, {request.POST.get('city')}, {request.POST.get('state')} - {request.POST.get('pincode')}",
        total_qty=sum(i.quantity for i in cart_items),
        total_amount=grand_total,
        dis_amount=total_discount,
        order_status="PLACED"
    )

    for item in cart_items:
        OrderDetail.objects.create(
            order=order,
            food_item=item.food_item,
            qty=item.quantity,
            price=item.price,
            total_amount=item.price * item.quantity
        )

    # payment = Payment.objects.create(
    #     method=request.POST.get("payment_method"),
    #     status="PENDING",
    #     amount_paid=Decimal("0.00"),
    #     remaining_amount=grand_total
    # )

    # OrderHasPayment.objects.create(
    #     order=order,
    #     payment=payment,
    #     amount=grand_total
    # )
    import uuid

    txn_no = "TXN-" + str(uuid.uuid4())[:10].upper()

    payment = Payment.objects.create(
       method=request.POST.get("payment_method", "COD"),
       status="PENDING",
       amount_paid=Decimal("0.00"),
       remaining_amount=grand_total
        )

    OrderHasPayment.objects.create(
        order=order,
        payment=payment,
        amount=grand_total,
        transaction_no=txn_no
        )
    cart_items.delete()
    return redirect("order_success", order.id)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        "order": order,
        "order_id": order.id,
        "total_amount": order.total_amount,   # ✅ ONLY THIS
        "order_status": order.order_status,
    }

    return render(request, "orders/order_success.html", context)

from django.views.decorators.http import require_POST
# ================= ORDER STATUS SEQUENCE =================
STATUS_SEQUENCE = ['PLACED', 'CONFIRMED', 'PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED']

# Helper to check allowed status change
def status_allowed(current_status, new_status):
    """Allow only moving forward in sequence"""
    try:
        current_index = STATUS_SEQUENCE.index(current_status)
        new_index = STATUS_SEQUENCE.index(new_status)
        return new_index >= current_index  # only forward
    except ValueError:
        return False

# def admin_orders(request):
#     orders = Order.objects.all().order_by('-order_date')  # Use your correct field
#     return render(request, 'adminpanel/admin_orders.html', {'orders': orders})
# def admin_orders(request):
#     orders = Order.objects.all().order_by('-order_date')

#     # Calculate allowed status for each order
#     order_list = []
#     for order in orders:
#         status_values = [status[0] for status in order.ORDER_STATUS]
#         current_index = status_values.index(order.order_status)
#         allowed_statuses = status_values[:current_index + 2]  # current + next
#         order_list.append({
#             'order': order,
#             'allowed_statuses': allowed_statuses
#         })

#     return render(request, 'adminpanel/admin_orders.html', {'order_list': order_list})
from deliverypanel.models import DeliveryPerson, AssignOrder

def admin_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    delivery_persons = DeliveryPerson.objects.filter(is_active=True)

    order_list = []

    for order in orders:
        # Make a list of dictionaries for dropdown
        statuses = []
        status_values = [s[0] for s in order.ORDER_STATUS]  # ['PLACED','CONFIRMED', ...]
        current_index = status_values.index(order.order_status)

        for i, (value, label) in enumerate(order.ORDER_STATUS):
            if i < current_index:
                # Past statuses → green + disabled
                statuses.append({'value': value, 'label': label, 'disabled': True, 'green': True})
            elif i == current_index:
                # Current status → green + disabled
                statuses.append({'value': value, 'label': label, 'disabled': True, 'green': True})
            elif i == current_index + 1:
                # Next status → enabled
                statuses.append({'value': value, 'label': label, 'disabled': False, 'green': False})
            else:
                # Future statuses → disabled
                statuses.append({'value': value, 'label': label, 'disabled': True, 'green': False})
        

        # 🔴 NEW: get latest assignment for this order
        assignment = AssignOrder.objects.filter(order=order).last()

# 🔴 Get rejected delivery persons for this order
        rejected_delivery_ids = AssignOrder.objects.filter(
            order=order,
            status='REJECTED'
            ).values_list('delivery_person_id', flat=True)

# 🔴 Filter dropdown delivery persons (exclude rejected ones)
        available_delivery_persons = delivery_persons.exclude(
             id__in=rejected_delivery_ids
)


        order_list.append({
            'order': order,
            'statuses': statuses,
            'delivery_persons': available_delivery_persons,   # 🔴 NEW
            'assignment': assignment,               # 🔴 NEW
        })

    return render(request, 'adminpanel/admin_orders.html', {
        'order_list': order_list
    })


def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    order_items = []
    for item in order.order_details.all():  # use 'order_details' related_name
        order_items.append({
            'food_item': item.food_item,
            'quantity': item.qty,
            'price': item.price,
            'subtotal': item.total_amount  # or calculate: item.qty * item.price
        })

    return render(request, 'adminpanel/admin_order_detail.html', {
        'order': order,
        'order_items': order_items,
        'total_amount': order.total_amount,
        'dis_amount': order.dis_amount,
    })
def admin_order_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.order_status == 'PLACED':
        order.order_status = 'CONFIRMED'
        order.save()
        messages.success(request, f"Order #{order.id} has been confirmed.")
    else:
        messages.warning(request, f"Order #{order.id} cannot be confirmed. Current status: {order.order_status}")
    
    return redirect('admin_orders') 
@require_POST
def admin_order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('order_status')

    valid_statuses = [status[0] for status in order.ORDER_STATUS]  # dynamically get valid values

    if new_status in valid_statuses:
        order.order_status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('admin_orders')
@require_POST
def admin_assign_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    delivery_id = request.POST.get('delivery_person')
    delivery_person = get_object_or_404(DeliveryPerson, id=delivery_id, is_active=True)

    # 🔒 Check if delivery person already has a pending or active order
    busy_assignment = AssignOrder.objects.filter(
        delivery_person=delivery_person,
        status__in=['REQUESTED', 'ACCEPTED']
    ).exists()

    if busy_assignment:
        messages.error(request, f"{delivery_person.fname} already has a pending or active order. Cannot assign another.")
        return redirect('admin_orders')

    # Create new assignment
    AssignOrder.objects.create(
        order=order,
        delivery_person=delivery_person,
        user=order.user,
        status='REQUESTED'
    )

    messages.success(request, f"Order #{order.id} assigned to {delivery_person.fname}")
    return redirect('admin_orders')
