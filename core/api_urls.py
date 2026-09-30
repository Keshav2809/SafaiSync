from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .api_views import ReportViewSet, PickupViewSet, AwarenessViewSet, me, admin_stats, health, collectors, assign_report, assign_pickup

router = DefaultRouter()
router.register("reports", ReportViewSet, basename="reports")
router.register("pickups", PickupViewSet, basename="pickups")
router.register("awareness", AwarenessViewSet, basename="awareness")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", me),
    path("admin/stats/", admin_stats),
    path("admin/collectors/", collectors),
    path("admin/reports/<int:pk>/assign/", assign_report),
    path("admin/pickups/<int:pk>/assign/", assign_pickup),
    path("health/", health),
]
