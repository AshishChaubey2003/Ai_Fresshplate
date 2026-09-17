from django.contrib import admin
from django.utils import timezone

from .models import Donation, RescueCenter


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "food_name", "donor", "food_type", "quantity",
        "status", "pickup_time", "expiry_time", "is_expired",
    )
    list_filter = ("status", "food_type")
    search_fields = ("food_name", "donor__email", "donor__full_name", "pickup_address")
    list_select_related = ("donor",)
    readonly_fields = ("donor", "created_at", "updated_at")
    date_hierarchy = "created_at"
    list_per_page = 25

    @admin.display(boolean=True, description="Expired")
    def is_expired(self, obj):
        return obj.expiry_time <= timezone.now()


@admin.register(RescueCenter)
class RescueCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "address", "contact_person")
    list_editable = ("is_active",)