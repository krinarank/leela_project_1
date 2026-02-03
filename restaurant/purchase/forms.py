# forms.py
from django import forms
from .models import Purchase, PurchaseDetail

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'total_amount']


class PurchaseDetailForm(forms.ModelForm):
    class Meta:
        model = PurchaseDetail
        fields = ['ingredient', 'qty', 'price_per_unit', 'total_price']
