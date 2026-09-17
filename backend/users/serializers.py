from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    # Public sign-up can NEVER create an admin. Admins are made with
    # `manage.py createsuperuser` or from the Django admin.
    role = serializers.ChoiceField(
        choices=[CustomUser.Role.CUSTOMER, CustomUser.Role.DONOR],
        default=CustomUser.Role.CUSTOMER,
    )

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "phone", "address", "role", "password", "confirm_password"]

    def validate_email(self, value):
        value = value.strip().lower()
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name is required.")
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        # Runs AUTH_PASSWORD_VALIDATORS: length, common passwords, all-numeric,
        # and similarity to the user's own name/email
        candidate = CustomUser(email=data.get("email"), full_name=data.get("full_name", ""))
        validate_password(data["password"], user=candidate)
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        user = authenticate(
            request=self.context.get("request"),
            email=data["email"].strip().lower(),
            password=data["password"],
        )
        # authenticate() also returns None for inactive users. Keeping one generic
        # message stops attackers from learning which emails are registered.
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        data["user"] = user
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "phone", "address", "role", "profile_picture", "created_at"]
        # Nobody can promote themselves by PATCHing their own profile
        read_only_fields = ["id", "email", "role", "created_at"]