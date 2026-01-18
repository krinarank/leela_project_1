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
    price = models.FloatField()
    is_available = models.BooleanField(default=True)
    calories = models.IntegerField()
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
