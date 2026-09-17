from rest_framework import serializers

from .models import Category, FoodItem


class CategorySerializer(serializers.ModelSerializer):
    # Filled by .annotate() in the view. A SerializerMethodField that called
    # .count() would run one extra query per category (the N+1 problem).
    food_count = serializers.IntegerField(read_only=True, default=0)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "description", "image", "image_url",
            "is_active", "food_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_image(self, obj):
        if obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.image_url or None


class FoodItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    # DecimalField keeps "150.00" exact; ReadOnlyField would turn it into a float
    final_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    # Returns the uploaded file if there is one, otherwise the hosted URL.
    # The frontend just reads `image` and doesn't care which one it was.
    image = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = [
            "id", "category", "category_name", "name", "description",
            "price", "discount_price", "final_price", "image", "is_veg",
            "is_available", "status", "preparation_time", "calories",
            "rating", "total_orders", "created_at",
        ]

    def get_image(self, obj):
        if obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.image_url or None


class FoodItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            "id", "category", "name", "description", "price", "discount_price",
            "image", "image_url", "is_veg", "is_available", "status",
            "preparation_time", "calories",
        ]
        # rating and total_orders are set by the system, never by an admin form
        read_only_fields = ["id"]

    def validate(self, data):
        # On PATCH only some fields arrive, so fall back to the stored values
        price = data.get("price", getattr(self.instance, "price", None))
        discount = data.get("discount_price", getattr(self.instance, "discount_price", None))

        if price is not None and discount is not None and discount >= price:
            raise serializers.ValidationError(
                {"discount_price": "Discount price must be lower than the price."}
            )

        # The model carries both `status` and `is_available`; keep them in step
        # so a dish marked unavailable really disappears from the menu
        status = data.get("status")
        if status == "unavailable":
            data["is_available"] = False
        elif status in ("available", "rescue") and "is_available" not in data:
            data["is_available"] = True

        return data