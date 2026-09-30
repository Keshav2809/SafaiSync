from django.db.models import Count, Q
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from .models import WasteReport, ReportHistory, PickupRequest, AwarenessPost
from .serializers import (
    ReportSerializer, ReportHistorySerializer, PickupSerializer,
    AwarenessSerializer, UserSerializer
)
from django.utils.crypto import get_random_string


def make_ref(prefix):
    return f"{prefix}-{get_random_string(8).upper()}"


def user_role(user):
    if user.is_staff:
        return "admin"
    return getattr(getattr(user, "profile", None), "role", "citizen")


def is_collector(user):
    return user_role(user) == "collector"


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if is_collector(self.request.user):
            return WasteReport.objects.filter(assigned_collector=self.request.user).select_related("user", "assigned_collector")
        if self.request.user.is_staff:
            qs = WasteReport.objects.select_related("user", "assigned_collector")
            status_q = self.request.query_params.get("status")
            category = self.request.query_params.get("category")
            q = self.request.query_params.get("q")
            if status_q:
                qs = qs.filter(status=status_q)
            if category:
                qs = qs.filter(category=category)
            if q:
                qs = qs.filter(Q(reference_code__icontains=q) | Q(title__icontains=q) |
                               Q(address__icontains=q) | Q(user__username__icontains=q))
            return qs
        return WasteReport.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if user_role(self.request.user) != "citizen":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only citizens can submit waste reports.")
        report = serializer.save(user=self.request.user, reference_code=make_ref("SS"))
        ReportHistory.objects.create(
            report=report, status="submitted",
            note="Complaint submitted", changed_by=self.request.user
        )

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        report = self.get_object()
        return Response(ReportHistorySerializer(report.history.all(), many=True).data)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        report = self.get_object()
        allowed = dict(WasteReport.STATUS_CHOICES)
        new_status = request.data.get("status")
        if new_status not in allowed:
            return Response({"detail": "Invalid status."}, status=400)
        report.status = new_status
        report.save()
        ReportHistory.objects.create(
            report=report, status=new_status,
            note=request.data.get("note", f"Status changed to {allowed[new_status]}"),
            changed_by=request.user
        )
        return Response(ReportSerializer(report).data)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def collector_status(self, request, pk=None):
        if not is_collector(request.user):
            return Response({"detail": "Collector access required."}, status=403)
        report = self.get_object()
        if report.assigned_collector_id != request.user.id:
            return Response({"detail": "This report is not assigned to you."}, status=403)
        allowed = {"assigned", "in_progress", "resolved"}
        new_status = request.data.get("status")
        if new_status not in allowed:
            return Response({"detail": "Invalid collector status."}, status=400)
        report.status = new_status
        report.save()
        ReportHistory.objects.create(
            report=report, status=new_status,
            note=request.data.get("note", f"Collector changed status to {new_status}"),
            changed_by=request.user
        )
        return Response(ReportSerializer(report).data)


class PickupViewSet(viewsets.ModelViewSet):
    serializer_class = PickupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if is_collector(self.request.user):
            return PickupRequest.objects.filter(assigned_collector=self.request.user).select_related("user", "assigned_collector")
        return PickupRequest.objects.all() if self.request.user.is_staff else PickupRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if user_role(self.request.user) != "citizen":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only citizens can request pickups.")
        serializer.save(user=self.request.user, reference_code=make_ref("PU"))

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        pickup = self.get_object()
        allowed = dict(PickupRequest.STATUS_CHOICES)
        new_status = request.data.get("status")
        if new_status not in allowed:
            return Response({"detail": "Invalid status."}, status=400)
        pickup.status = new_status
        pickup.save()
        return Response(PickupSerializer(pickup).data)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def collector_status(self, request, pk=None):
        if not is_collector(request.user):
            return Response({"detail": "Collector access required."}, status=403)
        pickup = self.get_object()
        if pickup.assigned_collector_id != request.user.id:
            return Response({"detail": "This pickup is not assigned to you."}, status=403)
        allowed = {"scheduled", "picked_up", "completed"}
        new_status = request.data.get("status")
        if new_status not in allowed:
            return Response({"detail": "Invalid collector pickup status."}, status=400)
        pickup.status = new_status
        pickup.save()
        return Response(PickupSerializer(pickup).data)


class AwarenessViewSet(viewsets.ModelViewSet):
    serializer_class = AwarenessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return AwarenessPost.objects.all()
        return AwarenessPost.objects.filter(is_published=True)

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can publish awareness content.")
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Admin access required."}, status=403)
        obj = self.get_object()
        obj.is_published = False
        obj.save()
        return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def collectors(request):
    users = User.objects.filter(is_staff=False, profile__role="collector").select_related("profile")
    return Response([
        {"id": u.id, "username": u.username, "phone": u.profile.phone}
        for u in users
    ])


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def assign_report(request, pk):
    try:
        report = WasteReport.objects.get(pk=pk)
    except WasteReport.DoesNotExist:
        return Response({"detail": "Report not found."}, status=404)
    collector_id = request.data.get("collector_id")
    collector = User.objects.filter(pk=collector_id, is_staff=False, profile__role="collector").first()
    if not collector:
        return Response({"detail": "Invalid collector."}, status=400)
    report.assigned_collector = collector
    if report.status == "submitted":
        report.status = "assigned"
    report.save()
    ReportHistory.objects.create(report=report, status=report.status, note=f"Assigned to {collector.username}", changed_by=request.user)
    return Response(ReportSerializer(report).data)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def assign_pickup(request, pk):
    try:
        pickup = PickupRequest.objects.get(pk=pk)
    except PickupRequest.DoesNotExist:
        return Response({"detail": "Pickup not found."}, status=404)
    collector_id = request.data.get("collector_id")
    collector = User.objects.filter(pk=collector_id, is_staff=False, profile__role="collector").first()
    if not collector:
        return Response({"detail": "Invalid collector."}, status=400)
    pickup.assigned_collector = collector
    if pickup.status == "requested":
        pickup.status = "scheduled"
    pickup.save()
    return Response(PickupSerializer(pickup).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_stats(request):
    reports = WasteReport.objects.all()
    return Response({
        "total_reports": reports.count(),
        "pending_reports": reports.filter(status__in=["submitted", "under_review", "assigned", "in_progress"]).count(),
        "resolved_reports": reports.filter(status="resolved").count(),
        "pending_pickups": PickupRequest.objects.filter(status__in=["requested", "scheduled"]).count(),
        "by_category": list(reports.values("category").annotate(count=Count("id")).order_by("-count")),
        "by_status": list(reports.values("status").annotate(count=Count("id")).order_by("-count")),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"ok": True, "service": "SafaiSync Django API"})
