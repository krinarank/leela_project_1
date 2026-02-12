

# Create your models here.
from django.db import models
from accounts.models import Customer  

from adminpanel.models import *
from django.utils import timezone
import uuid
from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model


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



class Wallet(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(auto_now=True)   # ✅ NEW FIELD

    def __str__(self):
        return f"{self.user.username} - ₹{self.balance}"

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    txn_type = models.CharField(
        max_length=10,
        choices=[
            ('CREDIT', 'Credit'),
            ('DEBIT', 'Debit')
        ]
    )
    description = models.CharField(max_length=255)
    txn_date = models.DateTimeField(auto_now_add=True)   # ✅ renamed

    def __str__(self):
        return f"{self.txn_type} - ₹{self.amount}"

class Order(models.Model):

    ORDER_STATUS = (
        ('PLACED', 'Placed'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('DELIVERED', 'Delivered'),
    )

    order_date = models.DateTimeField(auto_now_add=True)
    total_qty = models.PositiveIntegerField()
    dis_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    delivery_address = models.TextField()

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='PLACED'
    )

    area = models.ForeignKey(
        'location.Area',
        on_delete=models.SET_NULL,
        null=True
    )

    user = models.ForeignKey(
        'accounts.Customer',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Order #{self.id}"

class OrderDetail(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_details'
    )

    food_item = models.ForeignKey(
        'adminpanel.FoodItem',
        on_delete=models.CASCADE
    )

    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.food_item} - Order {self.order.id}"

class Payment(models.Model):

    PAYMENT_METHOD = (
        ('WALLET', 'Wallet'),
        ('COD', 'Cash On Delivery'),
        ('UPI', 'UPI'),
    )

    PAYMENT_STATUS = (
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    )

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateTimeField(auto_now_add=True)

    method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)

    def __str__(self):
        return f"{self.method} - {self.amount_paid}"

class OrderHasPayment(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_no = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    wallet_transaction = models.ForeignKey(
        'WalletTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Order {self.order.id} - Payment {self.payment.id}"


User = get_user_model()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'food_item')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} - {self.food_item.name}"


        return f"{self.user.username} - {self.food_item.name}"


