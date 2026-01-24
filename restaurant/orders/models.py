from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Customer  
from adminpanel.models import FoodItem


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
