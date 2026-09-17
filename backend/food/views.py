from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.permissions import IsAdminRole

from .models import Category, FoodItem
from .serializers import CategorySerializer, FoodItemCreateSerializer, FoodItemSerializer


def categories_with_counts():
    """One query for every category plus its dish count (no N+1)."""
    return Category.objects.annotate(
        food_count=Count("food_items", filter=Q(food_items__is_available=True))
    )


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return categories_with_counts().filter(is_active=True)


class CategoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class FoodItemListView(generics.ListAPIView):
    """
    Public menu.

    Query params: category, is_veg, status, search.
    Admins may add ?include_unavailable=true to also see hidden dishes.
    """

    permission_classes = [AllowAny]
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        params = self.request.query_params
        # select_related avoids one extra query per dish for category_name
        queryset = FoodItem.objects.select_related("category")

        user = self.request.user
        is_admin = user.is_authenticated and getattr(user, "is_admin_role", False)
        if not (is_admin and params.get("include_unavailable", "").lower() == "true"):
            queryset = queryset.filter(is_available=True, category__is_active=True)

        category = params.get("category")
        if category and category.isdigit():  # "?category=abc" used to raise a 500
            queryset = queryset.filter(category_id=category)

        is_veg = params.get("is_veg")
        if is_veg in ("true", "false"):  # anything else is ignored, not treated as false
            queryset = queryset.filter(is_veg=(is_veg == "true"))

        status_filter = params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = params.get("search", "").strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return queryset


class FoodItemDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = FoodItemSerializer
    queryset = FoodItem.objects.select_related("category")


class FoodItemCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = FoodItemCreateSerializer
    queryset = FoodItem.objects.all()


class FoodItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = FoodItemCreateSerializer
    queryset = FoodItem.objects.all()

    def perform_destroy(self, instance):
        """Soft-delete dishes that appear in past orders.

        Deleting them outright would cascade into OrderItem rows and leave
        customers with orders that have no items.
        """
        if instance.orderitem_set.exists():
            instance.is_available = False
            instance.status = "unavailable"
            instance.save(update_fields=["is_available", "status", "updated_at"])
        else:
            instance.delete()


class RescueFoodListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FoodItemSerializer
    queryset = FoodItem.objects.select_related("category").filter(
        status="rescue", is_available=True
    )