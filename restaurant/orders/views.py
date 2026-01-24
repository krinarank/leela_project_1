from django.shortcuts import get_object_or_404,render,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from adminpanel.models import FoodItem
from .models import Cart
from decimal import Decimal


@login_required(login_url='/accounts/customer_login/')
def add_to_cart(request, food_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'})

    item = get_object_or_404(FoodItem, id=food_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        food_item=item,
        defaults={'quantity': 1, 'price': item.price}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({'status': 'success', 'quantity': cart_item.quantity})



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

#     item_total = 0
#     for item in cart_items:
#         item_total += item.food_item.price * item.quantity

#     tax = round(item_total * 0.05, 2)   # 5% GST
#     grand_total = item_total + tax

#     context = {
#         'cart_items': cart_items,
#         'item_total': item_total,
#         'tax': tax,
#         'grand_total': grand_total,
#     }
#     return render(request, 'orders/cart.html', context)

@login_required(login_url='/accounts/customer_login/')
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)

    # calculate total_price for each item
    for item in cart_items:
        item.total_price = item.price * item.quantity  # per item total
        # optional: food image
        try:
            item.image_url = item.food_item.images.first().img_url.url
        except:
            item.image_url = '/static/default_food.png'

    # overall totals
    item_total = sum(item.total_price for item in cart_items)
    tax = (item_total * Decimal('0.05')).quantize(Decimal('0.01'))  # 5% GST
    grand_total = item_total + tax

    context = {
        'cart_items': cart_items,
        'item_total': item_total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/cart.html', context)

@login_required
def increase_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

@login_required
def decrease_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        # quantity 1 chhe to remove kari devu
        cart_item.delete()
    return redirect('cart')

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