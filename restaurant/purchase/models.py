from django.db import models
from location.models import Area


class Supplier(models.Model):
    fname = models.CharField(max_length=15)
    lname = models.CharField(max_length=25)
    contact_no = models.CharField(max_length=15)
    address = models.CharField(max_length=50)
    email = models.EmailField()
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.fname} {self.lname}"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measure = models.CharField(max_length=20)
    # available_qty = models.IntegerField()
    available_qty = models.DecimalField(max_digits=10, decimal_places=2)

    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class PreparedItem(models.Model):
    product_name = models.CharField(max_length=100)
    production_date = models.DateField()
    quantity_produced = models.IntegerField()

    def __str__(self):
        return self.product_name


class IngredientUsage(models.Model):
    # qty_used = models.IntegerField()
    qty_used = models.DecimalField(max_digits=10, decimal_places=2)

    unit = models.CharField(max_length=20)
    raw = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    production = models.ForeignKey(PreparedItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.raw.name} used in {self.production.product_name}"


class Purchase(models.Model):
    purchase_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return f"Purchase #{self.id}"

class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="items"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ingredient.name} - {self.qty}"
    
class PurchaseReturn(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    return_date = models.DateField(auto_now_add=True)
    reason = models.CharField(max_length=150)
    total_return_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Return #{self.id}"


class PurchaseReturnDetail(models.Model):
    purchase_return = models.ForeignKey(
        PurchaseReturn, on_delete=models.CASCADE, related_name="items"
    )
    raw = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.raw.name} - {self.qty}"
