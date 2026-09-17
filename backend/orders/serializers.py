from django.conf import settings
from rest_framework import serializers

from food.serializers import FoodItemSerializer

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    food_item_id = serializers.IntegerField(write_only=True)
    # DecimalField keeps money exact; ReadOnlyField would convert it to a float
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "food_item", "food_item_id", "quantity", "subtotal", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "cart_items", "total_price", "total_items", "updated_at"]


class AddToCartSerializer(serializers.Serializer):
    """Validates input before it reaches the view - "abc" used to cause a 500."""

    food_item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_quantity(self, value):
        if value > settings.MAX_CART_ITEM_QUANTITY:
            raise serializers.ValidationError(f"Maximum {settings.MAX_CART_ITEM_QUANTITY} per item.")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()  # 0 or less removes the item

    def validate_quantity(self, value):
        if value > settings.MAX_CART_ITEM_QUANTITY:
            raise serializers.ValidationError(f"Maximum {settings.MAX_CART_ITEM_QUANTITY} per item.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "food_item", "quantity", "price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user_name", "status", "payment_method", "payment_status",
            "delivery_address", "total_amount", "delivery_charge",
            "special_instructions", "order_items", "ordered_at", "updated_at",
        ]


class PlaceOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField(max_length=500)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)
    special_instructions = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_delivery_address(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Please enter a complete delivery address.")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    # ChoiceField rejects made-up values like "hacked"
    status = serializers.ChoiceField(choices=Order.Status.choices)