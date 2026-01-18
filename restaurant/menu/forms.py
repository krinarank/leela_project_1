from django import forms
from .models import FoodItem, FoodItemImage

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = '__all__'


class FoodItemImageForm(forms.ModelForm):
    class Meta:
        model = FoodItemImage
        fields = ['food_item','img_url']
