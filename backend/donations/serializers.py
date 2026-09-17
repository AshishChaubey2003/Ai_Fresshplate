from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Donation, RescueCenter


class DonationSerializer(serializers.ModelSerializer):
    """Read-only view of a donation, used by both the donor and the admin."""

    donor_name = serializers.CharField(source="donor.full_name", read_only=True)
    donor_email = serializers.CharField(source="donor.email", read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id", "donor_name", "donor_email", "food_name", "food_type",
            "quantity", "description", "image", "pickup_address",
            "pickup_time", "expiry_time", "status", "admin_note",
            "created_at", "updated_at",
        ]
        read_only_fields = fields  # this serializer never writes


class DonationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            "id", "food_name", "food_type", "quantity", "description",
            "image", "pickup_address", "pickup_time", "expiry_time",
            "status", "created_at",
        ]
        # A donor cannot set their own status - everything starts as pending
        read_only_fields = ["id", "status", "created_at"]

    def validate_food_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Tell us what the food is (at least 3 characters).")
        return value

    def validate_pickup_address(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Give a complete address so a volunteer can find it.")
        return value

    def validate(self, data):
        now = timezone.now()
        pickup = data["pickup_time"]
        expiry = data["expiry_time"]

        # Small grace window so a slow form submit doesn't fail
        if pickup < now - timedelta(minutes=5):
            raise serializers.ValidationError({"pickup_time": "Pickup time cannot be in the past."})

        if expiry <= pickup:
            raise serializers.ValidationError(
                {"expiry_time": "Expiry time must be after the pickup time."}
            )

        return data


class UpdateDonationStatusSerializer(serializers.Serializer):
    """Admin action. ChoiceField rejects made-up values like "hacked"."""

    status = serializers.ChoiceField(choices=Donation.Status.choices, required=False)
    admin_note = serializers.CharField(required=False, allow_blank=True, max_length=1000)


class RescueCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescueCenter
        fields = ["id", "name", "address", "contact_person", "phone", "email", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]