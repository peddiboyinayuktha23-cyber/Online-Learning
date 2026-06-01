from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import CustomUser


def home(request):
    from categories.models import Category
    from courses.models import Course

    featured_courses = Course.objects.filter(is_published=True).select_related("category", "instructor")[:6]
    popular_categories = Category.objects.filter(is_active=True)[:8]
    return render(
        request,
        "pages/home.html",
        {"featured_courses": featured_courses, "popular_categories": popular_categories},
    )


def page(request, template_name):
    return render(request, template_name)


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back. Your dashboard is ready.")
            return redirect("dashboard")
        messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")


def signup_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        full_name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        role = request.POST.get("role", CustomUser.Role.STUDENT)
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account already exists with this email.")
        else:
            try:
                validate_password(password)
                username = email.split("@")[0]
                base_username = username
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    counter += 1
                    username = f"{base_username}{counter}"
                user = CustomUser.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    role=role if role in dict(CustomUser.Role.choices) else CustomUser.Role.STUDENT,
                )
                user.full_name = full_name
                user.save(update_fields=["first_name", "last_name", "role"])
                login(request, user)
                messages.success(request, "Your account is ready. Welcome to Online Learning Hub.")
                return redirect("dashboard")
            except ValidationError as error:
                for message in error.messages:
                    messages.error(request, message)
    return render(request, "accounts/signup.html")


def forgot_password(request):
    if request.method == "POST":
        messages.info(request, "Password reset email flow is ready to connect to SMTP.")
    return render(request, "accounts/forgot_password.html")


def reset_password(request):
    if request.method == "POST":
        messages.info(request, "Use Django password reset tokens before enabling public reset links.")
    return render(request, "accounts/reset_password.html")


def otp_verification(request):
    return render(request, "accounts/otp_verification.html")


def change_password(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            try:
                validate_password(new_password, request.user)
                request.user.set_password(new_password)
                request.user.save(update_fields=["password"])
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password updated successfully.")
                return redirect("profile")
            except ValidationError as error:
                for message in error.messages:
                    messages.error(request, message)
    return render(request, "accounts/change_password.html")


@login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        user.full_name = request.POST.get("full_name", user.full_name).strip()
        user.email = request.POST.get("email", user.email).strip().lower()
        user.phone = request.POST.get("phone", user.phone).strip()
        user.bio = request.POST.get("bio", user.bio).strip()
        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES["profile_picture"]
        user.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")
    return render(request, "accounts/edit_profile.html")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def student_dashboard(request):
    if request.user.role == CustomUser.Role.INSTRUCTOR:
        return redirect("instructor_dashboard")
    if request.user.role == CustomUser.Role.ADMIN:
        return redirect(reverse("admin:index"))
    from enrollments.models import Enrollment

    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
    return render(request, "dashboard/student_dashboard.html", {"enrollments": enrollments})


@login_required
def instructor_dashboard(request):
    from courses.models import Course

    courses = Course.objects.filter(instructor=request.user)
    return render(request, "dashboard/instructor_dashboard.html", {"courses": courses})


def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
