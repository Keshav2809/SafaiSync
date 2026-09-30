from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import RegistrationForm, ReportForm, PickupForm


def _role_of(user):
    if user.is_staff or (hasattr(user, "profile") and user.profile.role == "admin"):
        return "admin"
    if hasattr(user, "profile") and user.profile.role == "collector":
        return "collector"
    return "citizen"


@ensure_csrf_cookie
def role_login(request, role):
    if request.user.is_authenticated:
        return redirect_for_role(request.user)

    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            error = "Invalid username or password."
        else:
            actual = _role_of(user)
            if actual != role:
                error = f"This account is not a {role} account."
            else:
                login(request, user)
                return redirect_for_role(user)
    return render(request, f"{role}_login.html", {"error": error})


def redirect_for_role(user):
    role = _role_of(user)
    if role == "admin":
        return redirect("admin_dashboard")
    if role == "collector":
        return redirect("collector_dashboard")
    return redirect("dashboard")


def citizen_login(request):
    return role_login(request, "citizen")


def admin_login(request):
    return role_login(request, "admin")


def collector_login(request):
    return role_login(request, "collector")


@login_required
def collector_dashboard(request):
    if _role_of(request.user) != "collector":
        return redirect_for_role(request.user)
    return render(request, "collector_dashboard.html")


def home(request):
    return render(request, "index.html", {"features": [("📝","Report Waste Issues","Report overflowing bins, missed collection, illegal dumping and more."),("🚛","Request Pickup","Request collection with a preferred date and location."),("📍","Track Complaints","Track each complaint from submission to resolution."),("📊","Admin Dashboard","Centralized statistics and operational management.")]})


@ensure_csrf_cookie
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.email = form.cleaned_data["email"]
        user.save()
        profile = user.profile
        profile.phone = form.cleaned_data.get("phone", "")
        profile.address = form.cleaned_data.get("address", "")
        profile.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "register.html", {"form": form})


@login_required
@ensure_csrf_cookie
def dashboard(request):
    if _role_of(request.user) != "citizen":
        return redirect_for_role(request.user)
    return render(request, "dashboard.html")


@login_required
@ensure_csrf_cookie
def report_page(request):
    if _role_of(request.user) != "citizen":
        return redirect_for_role(request.user)
    return render(request, "report.html", {"form": ReportForm()})


@login_required
@ensure_csrf_cookie
def pickup_page(request):
    if _role_of(request.user) != "citizen":
        return redirect_for_role(request.user)
    return render(request, "pickup.html", {"form": PickupForm()})


@login_required
@ensure_csrf_cookie
def awareness_page(request):
    if _role_of(request.user) == "admin":
        return render(request, "awareness.html")
    return render(request, "awareness.html")


@login_required
@user_passes_test(lambda u: u.is_staff)
@ensure_csrf_cookie
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")
