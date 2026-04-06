from rest_framework import serializers
from .models import Donation, RescueCenter


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.full_name', read_only=True)
    donor_email = serializers.CharField(source='donor.email', read_only=True)

    class Meta:
        model = Donation
        fields = [
            'id', 'donor_name', 'donor_email', 'food_name', 'food_type',
            'quantity', 'description', 'image', 'pickup_address',
            'pickup_time', 'expiry_time', 'status', 'admin_note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'donor_name', 'donor_email', 'status', 'admin_note', 'created_at']


class DonationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            'food_name', 'food_type', 'quantity', 'description',
            'image', 'pickup_address', 'pickup_time', 'expiry_time'
        ]


class RescueCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescueCenter
        fields = ['id', 'name', 'address', 'contact_person', 'phone', 'email', 'is_active', 'created_at']