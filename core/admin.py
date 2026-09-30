from django.contrib import admin
from .models import Profile, WasteReport, ReportHistory, PickupRequest, AwarenessPost

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "address")

@admin.register(WasteReport)
class WasteReportAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "category", "priority", "status", "created_at")
    list_filter = ("status", "category", "priority")
    search_fields = ("reference_code", "title", "address", "user__username")
    readonly_fields = ("reference_code", "created_at", "updated_at")

@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ("report", "status", "changed_by", "created_at")

@admin.register(PickupRequest)
class PickupAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "waste_type", "preferred_date", "status")
    list_filter = ("status",)
    search_fields = ("reference_code", "address", "user__username")

@admin.register(AwarenessPost)
class AwarenessAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("is_published", "category")
