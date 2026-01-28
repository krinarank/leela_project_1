

# Create your models here.
from django.db import models
from accounts.models import Customer  

from adminpanel.models import *
from django.utils import timezone
import uuid

from adminpanel.models import FoodItem
from django.contrib.auth import get_user_model
from django.conf import settings



class Cart(models.Model):
    user = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'food_item')

    def __str__(self):
        return f"{self.user} - {self.food_item} ({self.quantity})"


 
class OfferDiscount(models.Model):
    description = models.CharField(max_length=200)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    offer_code = models.CharField(max_length=20, unique=True)

    valid_from = models.DateField()
    valid_to = models.DateField()

    isactive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_currently_active(self):
        today = timezone.now().date()
        return self.isactive and self.valid_from <= today <= self.valid_to
    
    def get_status(self):
        today = timezone.now().date()

        if not self.isactive:
            return "Inactive"

        if self.valid_from > today:
            return "Upcoming"

        if self.valid_from <= today <= self.valid_to:
            return "Active"

        return "Expired"

    def __str__(self):
        return f"{self.offer_code} ({self.discount_percentage}%)"

  
class FoodItemOfferDiscount(models.Model):
    offer = models.ForeignKey(
        OfferDiscount,
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(FoodItemCategory, on_delete=models.CASCADE, blank=True, null=True)  # Add this!
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE
    )
    applied_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.offer} - {self.food_item}"

class CategoryOfferDiscount(models.Model):
    offer = models.ForeignKey(
        OfferDiscount,
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        FoodItemCategory,
        on_delete=models.CASCADE
    )
    applied_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.offer} - {self.category}"


class SubCategoryOfferDiscount(models.Model):
    offer = models.ForeignKey(OfferDiscount, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        FoodItemSubCategory,
        on_delete=models.CASCADE
    )
    applied_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.applied_date <= today <= self.expiry_date



# class Wishlist(models.Model):
#     customer = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE
#     )
#     food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
#     added_on = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('customer', 'food_item')

#     def __str__(self):
User = get_user_model()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'food_item')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} - {self.food_item.name}"


