from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F, Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from food.models import FoodItem
from users.permissions import IsAdminRole

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    AddToCartSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    PlaceOrderSerializer,
    UpdateCartItemSerializer,
    UpdateOrderStatusSerializer,
)


def get_cart(user):
    """The user's cart with items, dishes and categories prefetched (no N+1)."""
    Cart.objects.get_or_create(user=user)
    return Cart.objects.prefetch_related(
        Prefetch("cart_items", queryset=CartItem.objects.select_related("food_item__category"))
    ).get(user=user)


def orders_queryset():
    return Order.objects.select_related("user").prefetch_related(
        Prefetch("order_items", queryset=OrderItem.objects.select_related("food_item__category"))
    )


class CartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get(self, request):
        return Response(CartSerializer(get_cart(request.user)).data)

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        food_item_id = serializer.validated_data["food_item_id"]
        quantity = serializer.validated_data["quantity"]

        food_item = FoodItem.objects.filter(id=food_item_id, is_available=True).first()
        if not food_item:
            return Response({"error": "Food item not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        with transaction.atomic():
            cart_item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart, food_item=food_item, defaults={"quantity": quantity}
            )
            if not created:
                cart_item.quantity = min(cart_item.quantity + quantity, settings.MAX_CART_ITEM_QUANTITY)
                cart_item.save(update_fields=["quantity"])

        return Response({"message": "Item added to cart", "cart": CartSerializer(get_cart(request.user)).data})

    def delete(self, request):
        CartItem.objects.filter(cart__user=request.user).delete()
        return Response({"message": "Cart cleared"})


class CartItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateCartItemSerializer

    def patch(self, request, pk):
        # cart__user filter means you can only touch your own cart items
        cart_item = get_object_or_404(
            CartItem.objects.select_related("food_item"), id=pk, cart__user=request.user
        )
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]

        if quantity <= 0:
            cart_item.delete()
            return Response({"message": "Item removed from cart"})

        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])
        return Response({"message": "Cart updated", "item": CartItemSerializer(cart_item).data})

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        cart_item.delete()
        return Response({"message": "Item removed from cart"})


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlaceOrderSerializer

    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # atomic(): either the order, its items and the cleared cart all happen,
        # or none of them do. No half-written orders.
        with transaction.atomic():
            cart_items = list(
                CartItem.objects.select_for_update()
                .select_related("food_item")
                .filter(cart__user=request.user)
            )
            if not cart_items:
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

            # A dish may have been hidden while it sat in the cart
            unavailable = [ci.food_item.name for ci in cart_items if not ci.food_item.is_available]
            if unavailable:
                return Response(
                    {"error": f"These items are no longer available: {', '.join(unavailable)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # All Decimal. Adding a float here is what used to raise TypeError -> 500.
            items_total = sum((ci.subtotal for ci in cart_items), Decimal("0.00"))
            delivery_charge = settings.DELIVERY_CHARGE

            order = Order.objects.create(
                user=request.user,
                delivery_address=data["delivery_address"],
                payment_method=data["payment_method"],
                special_instructions=data.get("special_instructions", ""),
                total_amount=items_total + delivery_charge,
                delivery_charge=delivery_charge,
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    food_item=ci.food_item,
                    quantity=ci.quantity,
                    price=ci.food_item.final_price,  # snapshot: later price changes don't rewrite history
                )
                for ci in cart_items
            ])

            for ci in cart_items:
                # F() increments inside the database - no lost updates when two
                # customers order the same dish at the same moment
                FoodItem.objects.filter(pk=ci.food_item_id).update(
                    total_orders=F("total_orders") + ci.quantity
                )

            CartItem.objects.filter(pk__in=[ci.pk for ci in cart_items]).delete()

        order = orders_queryset().get(pk=order.pk)
        return Response(
            {"message": "Order placed successfully!", "order": OrderSerializer(order).data},
            status=status.HTTP_201_CREATED,
        )


class MyOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return orders_queryset().filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return orders_queryset().filter(user=self.request.user)


class CancelOrderView(APIView):
    """Customers can cancel their own order while it is still pending or confirmed."""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=OrderSerializer)
    def post(self, request, pk):
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), pk=pk, user=request.user)
            if order.status not in (Order.Status.PENDING, Order.Status.CONFIRMED):
                return Response(
                    {"error": f"Order cannot be cancelled once it is '{order.get_status_display()}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])

        return Response({"message": "Order cancelled", "order": OrderSerializer(orders_queryset().get(pk=pk)).data})


class AllOrdersView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = orders_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminRole]
    serializer_class = UpdateOrderStatusSerializer

    def patch(self, request, pk):
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]

        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), pk=pk)
            if new_status != order.status:
                if not order.can_transition_to(new_status):
                    return Response(
                        {"error": f"Cannot change status from '{order.status}' to '{new_status}'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                order.status = new_status
                # Cash is collected on delivery, so mark it paid at that point
                if new_status == Order.Status.DELIVERED and order.payment_method == "cod":
                    order.payment_status = True
                order.save(update_fields=["status", "payment_status", "updated_at"])

        order = orders_queryset().get(pk=pk)
        return Response({"message": "Order status updated", "order": OrderSerializer(order).data})