import random
import string
from django.utils.timezone import now
from django.utils import timezone
from orders.models import *
from adminpanel.models import *
from django.db import models
from django.db.models import Q
from decimal import Decimal

def generate_offer_code():
    prefix = "OFF"
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{random_part}"


 
def get_best_offer(item):
    today = timezone.now().date()

    # 1️⃣ ITEM offer
    item_offer = FoodItemOfferDiscount.objects.filter(
        food_item=item,
        is_active=True,
        applied_date__lte=today,
        expiry_date__gte=today,
        offer__isactive=True
    ).first()

    if item_offer:
        return item_offer

    # 2️⃣ SUBCATEGORY offer  🔥 NEW
    sub_offer = SubCategoryOfferDiscount.objects.filter(
        subcategory=item.sub_cat,
        is_active=True,
        applied_date__lte=today,
        expiry_date__gte=today,
        offer__isactive=True
    ).first()

    if sub_offer:
        return sub_offer

    # 3️⃣ CATEGORY offer
    cat_offer = CategoryOfferDiscount.objects.filter(
        category=item.sub_cat.food_item_cat,
        is_active=True,
        applied_date__lte=today,
        expiry_date__gte=today,
        offer__isactive=True
    ).first()

    if cat_offer:
        return cat_offer

    return None



# def get_discounted_price(food_item):
#     today = timezone.now().date()
#     original_price = Decimal(food_item.price)
#     discount = Decimal('0.00')

#     # 1️⃣ Food item level offer
#     food_offer = FoodItemOfferDiscount.objects.filter(
#         food_item=food_item,
#         is_active=True,
#         applied_date__lte=today,
#         expiry_date__gte=today,
#         offer__isactive=True
#     ).select_related('offer').first()

#     if food_offer:
#         discount = Decimal(food_offer.offer.discount_percentage)

#     # 2️⃣ Sub category level offer
#     if discount == 0 and food_item.sub_cat:
#         sub_offer = SubCategoryOfferDiscount.objects.filter(
#             subcategory=food_item.sub_cat,
#             is_active=True,
#             applied_date__lte=today,
#             expiry_date__gte=today,
#             offer__isactive=True
#         ).select_related('offer').first()

#         if sub_offer:
#             discount = Decimal(sub_offer.offer.discount_percentage)

#     # 3️⃣ Category level offer
#     if discount == 0 and food_item.sub_cat and food_item.sub_cat.food_item_cat:
#         cat_offer = CategoryOfferDiscount.objects.filter(
#             category=food_item.sub_cat.food_item_cat,
#             is_active=True,
#             applied_date__lte=today,
#             expiry_date__gte=today,
#             offer__isactive=True
#         ).select_related('offer').first()

#         if cat_offer:
#             discount = Decimal(cat_offer.offer.discount_percentage)

#     if discount > 0:
#         discounted_price = original_price - (original_price * discount / Decimal('100'))
#         return discounted_price.quantize(Decimal('0.01'))

#     return original_price.quantize(Decimal('0.01'))

from decimal import Decimal
from django.utils import timezone

def get_discounted_price(food_item, base_price=None):
    today = timezone.now().date()

    # 👇 If variant price passed → use that
    if base_price is not None:
        original_price = Decimal(base_price)
    else:
        original_price = Decimal(food_item.price)

    discount = Decimal('0.00')

    # 1️⃣ Food item level offer
    food_offer = FoodItemOfferDiscount.objects.filter(
        food_item=food_item,
        is_active=True,
        applied_date__lte=today,
        expiry_date__gte=today,
        offer__isactive=True
    ).select_related('offer').first()

    if food_offer:
        discount = Decimal(food_offer.offer.discount_percentage)

    # 2️⃣ Sub category level offer
    if discount == 0 and food_item.sub_cat:
        sub_offer = SubCategoryOfferDiscount.objects.filter(
            subcategory=food_item.sub_cat,
            is_active=True,
            applied_date__lte=today,
            expiry_date__gte=today,
            offer__isactive=True
        ).select_related('offer').first()

        if sub_offer:
            discount = Decimal(sub_offer.offer.discount_percentage)

    # 3️⃣ Category level offer
    if discount == 0 and food_item.sub_cat and food_item.sub_cat.food_item_cat:
        cat_offer = CategoryOfferDiscount.objects.filter(
            category=food_item.sub_cat.food_item_cat,
            is_active=True,
            applied_date__lte=today,
            expiry_date__gte=today,
            offer__isactive=True
        ).select_related('offer').first()

        if cat_offer:
            discount = Decimal(cat_offer.offer.discount_percentage)

    # Apply discount
    if discount > 0:
        discounted_price = original_price - (original_price * discount / Decimal('100'))
        return discounted_price.quantize(Decimal('0.01'))

    return original_price.quantize(Decimal('0.01'))
