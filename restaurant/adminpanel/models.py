# adminpanel/models.py

from django.db import models

class FoodItemCategory(models.Model):
    category_name = models.CharField(max_length=100)
    def __str__(self):
        return self.category_name

class FoodItemSubCategory(models.Model):
    subcategory_name = models.CharField(max_length=100)
    food_item_cat = models.ForeignKey(FoodItemCategory, on_delete=models.CASCADE)
    def __str__(self):
        return self.subcategory_name

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    is_special = models.BooleanField(default=True)
    calories = models.IntegerField()
    has_variant = models.BooleanField(default=False)
    sub_cat = models.ForeignKey(FoodItemSubCategory, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class FoodItemImage(models.Model):
    img_url = models.ImageField(upload_to='food/')
    uploaded_date = models.DateTimeField(auto_now_add=True)
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='images'   # 🔥 VERY IMPORTANT
    )


class Notification(models.Model):
    RECIPIENT_CHOICES = [
        ('customer', 'Customer'),
        ('delivery_person', 'Delivery Person'),
    ]
    
    title = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES)
    send_datetime = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    user_id = models.IntegerField(null=True, blank=True)  # FK optional
    
    def __str__(self):
        return f"{self.title} - {self.recipient_type}"


class FoodItemVariant(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.food_item.name} - {self.variant_name}"
