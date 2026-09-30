from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from .models import WasteReport, ReportHistory, PickupRequest, AwarenessPost, Profile


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="profile.phone", read_only=True)
    address = serializers.CharField(source="profile.address", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "address", "is_staff", "role"]

    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        if obj.is_staff:
            return "admin"
        return getattr(getattr(obj, "profile", None), "role", "citizen")


class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = WasteReport
        fields = "__all__"
        read_only_fields = ["id", "user", "reference_code", "status", "created_at", "updated_at", "user_name", "assigned_collector"]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters.")
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters.")
        return value.strip()

    def validate_address(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Address must be at least 5 characters.")
        return value.strip()


class ReportHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.username", read_only=True)

    class Meta:
        model = ReportHistory
        fields = "__all__"


class PickupSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PickupRequest
        fields = "__all__"
        read_only_fields = ["id", "user", "reference_code", "status", "created_at", "updated_at", "user_name", "assigned_collector"]

    def validate_preferred_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Pickup date cannot be in the past.")
        return value


class AwarenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwarenessPost
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at"]
