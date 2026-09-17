from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Past orders are records, not editable data
    readonly_fields = ("food_item", "quantity", "price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "payment_method", "payment_status", "total_amount", "ordered_at")
    list_filter = ("status", "payment_method", "payment_status")
    search_fields = ("id", "user__email", "user__full_name", "delivery_address")
    readonly_fields = ("total_amount", "delivery_charge", "ordered_at", "updated_at")
    inlines = [OrderItemInline]
    list_select_related = ("user",)
    list_per_page = 25


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    search_fields = ("user__email",)
    inlines = [CartItemInline]