from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ("citizen", "Citizen"),
        ("collector", "Garbage Collector"),
        ("admin", "Admin"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="citizen")

    def __str__(self):
        return self.user.username


class WasteReport(models.Model):
    CATEGORY_CHOICES = [
        ("Overflowing Bin", "Overflowing Bin"),
        ("Missed Collection", "Missed Collection"),
        ("Illegal Dumping", "Illegal Dumping"),
        ("Garbage on Road", "Garbage on Road"),
        ("Improper Segregation", "Improper Segregation"),
        ("Other", "Other"),
    ]
    PRIORITY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    reference_code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=2000)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    photo_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    assigned_collector = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="assigned_waste_reports"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference_code


class ReportHistory(models.Model):
    report = models.ForeignKey(WasteReport, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20)
    note = models.CharField(max_length=500, blank=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class PickupRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("scheduled", "Scheduled"),
        ("picked_up", "Picked Up"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pickups")
    reference_code = models.CharField(max_length=20, unique=True)
    waste_type = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255)
    preferred_date = models.DateField()
    notes = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    assigned_collector = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="assigned_pickups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class AwarenessPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)
    category = models.CharField(max_length=80, default="General")
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
