from django.db import models
from users.models import CustomUser


class Donation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('picked_up', 'Picked Up'),
        ('distributed', 'Distributed'),
        ('rejected', 'Rejected'),
    )

    FOOD_TYPE_CHOICES = (
        ('cooked', 'Cooked Food'),
        ('raw', 'Raw Food'),
        ('packaged', 'Packaged Food'),
        ('fruits_vegetables', 'Fruits & Vegetables'),
    )

    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donations')
    food_name = models.CharField(max_length=200)
    food_type = models.CharField(max_length=30, choices=FOOD_TYPE_CHOICES)
    quantity = models.CharField(max_length=100, help_text='e.g. 5 kg, 10 plates')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='donations/', blank=True, null=True)
    pickup_address = models.TextField()
    pickup_time = models.DateTimeField()
    expiry_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_name} by {self.donor.full_name}"


class RescueCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
