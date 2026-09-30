from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("login/", views.citizen_login, name="login"),
    path("citizen-login/", views.citizen_login, name="citizen_login"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("collector-login/", views.collector_login, name="collector_login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("report/", views.report_page, name="report"),
    path("pickup/", views.pickup_page, name="pickup"),
    path("awareness/", views.awareness_page, name="awareness"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("collector-dashboard/", views.collector_dashboard, name="collector_dashboard"),
    path("api/", include("core.api_urls")),
]
