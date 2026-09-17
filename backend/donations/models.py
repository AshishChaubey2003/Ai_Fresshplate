from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    r"^\+?[0-9]{10,15}$",
    "Enter a valid phone number (10-15 digits, optional + prefix).",
)


class Donation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PICKED_UP = "picked_up", "Picked Up"
        DISTRIBUTED = "distributed", "Distributed"
        REJECTED = "rejected", "Rejected"

    # The real 3-step lifecycle: approve -> collect -> hand out.
    # Skipping a step (pending straight to distributed) is now rejected.
    ALLOWED_TRANSITIONS = {
        "pending": {"approved", "rejected"},
        "approved": {"picked_up", "rejected"},
        "picked_up": {"distributed"},
        "distributed": set(),
        "rejected": set(),
    }

    FOOD_TYPE_CHOICES = (
        ("cooked", "Cooked Food"),
        ("raw", "Raw Food"),
        ("packaged", "Packaged Food"),
        ("fruits_vegetables", "Fruits & Vegetables"),
    )

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations"
    )
    food_name = models.CharField(max_length=200)
    food_type = models.CharField(max_length=30, choices=FOOD_TYPE_CHOICES)
    quantity = models.CharField(max_length=100, help_text="e.g. 5 kg, 10 plates")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="donations/", blank=True, null=True)
    pickup_address = models.TextField()
    pickup_time = models.DateTimeField()
    expiry_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.food_name} by {self.donor.full_name}"

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, set())


class RescueCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name