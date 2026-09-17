from decimal import Decimal

from django.conf import settings
from django.db import models

from food.models import FoodItem


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.full_name}"

    def _items(self):
        # Uses prefetched rows when the view prefetched them (avoids N+1)
        return self.cart_items.all()

    @property
    def total_price(self):
        # Start from Decimal("0.00"), never 0 or 0.0 - mixing Decimal with float raises TypeError
        return sum((item.subtotal for item in self._items()), Decimal("0.00"))

    @property
    def total_items(self):
        # Sum of quantities, not number of rows - 3 plates is 3 items, not 1
        return sum(item.quantity for item in self._items())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["added_at"]
        constraints = [
            # The database itself now prevents duplicate rows and zero quantities,
            # even if two requests arrive at the same moment
            models.UniqueConstraint(fields=["cart", "food_item"], name="unique_food_item_per_cart"),
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name="cart_item_quantity_gte_1"),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"

    @property
    def subtotal(self):
        return self.food_item.final_price * self.quantity


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    # Which status can follow which - stops jumps like pending -> delivered
    ALLOWED_TRANSITIONS = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"preparing", "cancelled"},
        "preparing": {"out_for_delivery", "cancelled"},
        "out_for_delivery": {"delivered"},
        "delivered": set(),
        "cancelled": set(),
    }

    PAYMENT_CHOICES = (
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
    )

    # PROTECT: an order is a financial record; deleting a user must not erase it
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cod")
    payment_status = models.BooleanField(default=False)
    delivery_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("40.00"))
    special_instructions = models.TextField(blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(fields=["user", "-ordered_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Order #{self.id} by {self.user.full_name}"

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, set())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    # PROTECT: deleting a dish must never wipe out customers' order history
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Unit price at the time of ordering"
    )

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity