from django.contrib import admin

from .models import Category, FoodItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "dish_count", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)
    readonly_fields = ("created_at",)

    @admin.display(description="Dishes")
    def dish_count(self, obj):
        return obj.food_items.count()


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "price", "discount_price",
        "is_veg", "is_available", "status", "total_orders",
    )
    list_filter = ("category", "is_veg", "is_available", "status")
    search_fields = ("name", "description")
    # Toggle availability straight from the list instead of opening each dish
    list_editable = ("is_available", "status")
    list_select_related = ("category",)
    # These are set by the system when orders are placed, not by hand
    readonly_fields = ("total_orders", "created_at", "updated_at")
    list_per_page = 25

    fieldsets = (
        # image_url is the one that survives a Render deploy - paste a hosted
        # photo link there instead of uploading a file
        ("Dish", {"fields": ("name", "category", "description", "image", "image_url", "is_veg")}),
        ("Pricing", {"fields": ("price", "discount_price")}),
        ("Availability", {"fields": ("is_available", "status")}),
        ("Details", {"fields": ("preparation_time", "calories", "rating")}),
        ("Stats", {"fields": ("total_orders", "created_at", "updated_at")}),
    )