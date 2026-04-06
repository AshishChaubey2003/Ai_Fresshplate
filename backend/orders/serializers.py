from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from food.serializers import FoodItemSerializer


class CartItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    food_item_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'food_item', 'food_item_id', 'quantity', 'subtotal', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'total_price', 'total_items', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'quantity', 'price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user_name', 'status', 'payment_method', 'payment_status',
            'delivery_address', 'total_amount', 'delivery_charge',
            'special_instructions', 'order_items', 'ordered_at', 'updated_at'
        ]


class PlaceOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=['cod', 'online'])
    special_instructions = serializers.CharField(required=False, allow_blank=True)