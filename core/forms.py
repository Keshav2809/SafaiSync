import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, WasteReport, PickupRequest, AwarenessPost


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=10)
    address = forms.CharField(required=False, max_length=255)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "address", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if len(username) < 3:
            raise forms.ValidationError("Username must contain at least 3 characters.")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone and not re.fullmatch(r"[6-9]\d{9}", phone):
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")
        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class StaffRegistrationForm(RegistrationForm):
    """Admin / collector sign-up (no access code)."""

    def __init__(self, *args, role="collector", **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        if role == "collector":
            self.fields["phone"].required = True


class ReportForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = [
            "category", "title", "description", "address",
            "latitude", "longitude", "priority", "photo_url"
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "latitude": forms.NumberInput(attrs={"step": "any", "min": "-90", "max": "90"}),
            "longitude": forms.NumberInput(attrs={"step": "any", "min": "-180", "max": "180"}),
        }

    def clean_title(self):
        value = self.cleaned_data["title"].strip()
        if len(value) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        return value

    def clean_description(self):
        value = self.cleaned_data["description"].strip()
        if len(value) < 10:
            raise forms.ValidationError("Description must be at least 10 characters.")
        return value

    def clean_address(self):
        value = self.cleaned_data["address"].strip()
        if len(value) < 5:
            raise forms.ValidationError("Address must be at least 5 characters.")
        return value


class PickupForm(forms.ModelForm):
    class Meta:
        model = PickupRequest
        fields = ["waste_type", "quantity", "address", "preferred_date", "notes"]
        widgets = {"preferred_date": forms.DateInput(attrs={"type": "date"})}

    def clean_address(self):
        value = self.cleaned_data["address"].strip()
        if len(value) < 5:
            raise forms.ValidationError("Address must be at least 5 characters.")
        return value

    def clean_preferred_date(self):
        value = self.cleaned_data["preferred_date"]
        from django.utils import timezone
        if value < timezone.localdate():
            raise forms.ValidationError("Pickup date cannot be in the past.")
        return value
