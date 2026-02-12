from django.contrib import admin
from .models import Order, OrderDetail

# Inline for order items inside an order
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0  # no empty rows
    readonly_fields = ('food_item', 'qty', 'price', 'total_amount')
    can_delete = False

# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'order_status', 'total_qty', 'total_amount')
    list_filter = ('order_status', 'order_date', 'area')
    search_fields = ('id', 'user__username', 'user__email', 'delivery_address')
    readonly_fields = ('order_date', 'total_qty', 'dis_amount', 'total_amount')
    inlines = [OrderDetailInline]
    list_editable = ('order_status',)  # admin can update status directly

# Optional: register OrderDetail if admin wants to see all items separately
@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'food_item', 'qty', 'price', 'total_amount')
    search_fields = ('order__id', 'food_item__name')
    readonly_fields = ('total_amount',)
