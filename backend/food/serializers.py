from rest_framework import serializers
from .models import Category, FoodItem


class CategorySerializer(serializers.ModelSerializer):
    food_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active', 'food_count', 'created_at']

    def get_food_count(self, obj):
        return obj.food_items.filter(is_available=True).count()


class FoodItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = FoodItem
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'price', 'discount_price', 'final_price', 'image', 'is_veg',
            'is_available', 'status', 'preparation_time', 'calories',
            'rating', 'total_orders', 'created_at'
        ]


class FoodItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            'category', 'name', 'description', 'price', 'discount_price',
            'image', 'is_veg', 'is_available', 'status', 'preparation_time', 'calories'
        ]