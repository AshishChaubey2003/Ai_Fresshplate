from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    # Render wipes its disk on every deploy, so a hosted URL survives where an
    # uploaded file does not. Either field works; image_url is the fallback.
    image_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("unavailable", "Unavailable"),
        ("rescue", "Food Rescue"),
    )

    # PROTECT, not CASCADE: deleting a category must never silently wipe out
    # its dishes (and through them, rows in past orders)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="food_items")
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    image = models.ImageField(upload_to="food/", blank=True, null=True)
    # Paste a hosted photo URL here (Unsplash, Pexels, Cloudinary...). Used when
    # no file has been uploaded - and it is the only option that survives a deploy.
    image_url = models.URLField(max_length=500, blank=True)
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    preparation_time = models.PositiveIntegerField(help_text="Time in minutes", default=30)
    calories = models.PositiveIntegerField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=Decimal("0.0"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    total_orders = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Most-ordered first, so the homepage "Ordered most often" list is real
        ordering = ["-total_orders", "name"]
        indexes = [models.Index(fields=["is_available", "status"])]

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        # A discount that is higher than the price is a data-entry mistake -
        # never charge the customer more than the listed price
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price