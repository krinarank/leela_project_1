from django.contrib import admin
from .models import Supplier, Ingredient, Purchase, PurchaseReturn, PurchaseReturnDetail ,PreparedItem, IngredientUsage


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'fname', 'lname', 'contact_no', 'area')
    search_fields = ('fname', 'lname')

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'available_qty', 'unit_of_measure')
    list_editable = ('available_qty',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase_date', 'supplier', 'total_amount')

@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase', 'return_date', 'total_return_amount')

@admin.register(PurchaseReturnDetail)
class PurchaseReturnDetailAdmin(admin.ModelAdmin):
    list_display = ('purchase_return', 'raw', 'qty', 'total_price')


@admin.register(PreparedItem)
class PreparedItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'production_date', 'quantity_produced')


@admin.register(IngredientUsage)
class IngredientUsageAdmin(admin.ModelAdmin):
    list_display = ('production', 'raw', 'qty_used', 'unit')

    def save_model(self, request, obj, form, change):
        # Stock minus when admin adds usage
        if not change:
            ingredient = obj.raw
            ingredient.available_qty -= obj.qty_used
            ingredient.save()
        super().save_model(request, obj, form, change)
