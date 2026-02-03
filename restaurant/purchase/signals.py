from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseReturnDetail, Ingredient,IngredientUsage

@receiver(post_save, sender=PurchaseReturnDetail)
def update_stock_on_return(sender, instance, created, **kwargs):
    if created:
        ingredient = instance.raw
        ingredient.available_qty -= instance.qty
        ingredient.save()

# @receiver(post_save, sender=IngredientUsage)
# def update_ingredient_stock(sender, instance, **kwargs):
#     ingredient = instance.raw
#     try:
#         # Convert qty_used to integer/float
#         qty_used = float(instance.qty_used)

#         # Update stock
#         ingredient.available_qty -= qty_used
#         if ingredient.available_qty < 0:
#             ingredient.available_qty = 0  # avoid negative stock

#         ingredient.save()
#     except Exception as e:
#         print("Error updating stock:", e)