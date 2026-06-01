from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, InstructorProfile, StudentProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "first_name", "last_name", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff", "is_superuser", "email_verified")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "profile_picture", "bio", "phone")}),
        (_("Role and verification"), {"fields": ("role", "email_verified", "email_verification_token")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "first_name", "last_name", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "headline")
    filter_horizontal = ("interests",)
    autocomplete_fields = ("user",)


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "expertise", "experience_years", "average_rating", "is_featured")
    list_filter = ("is_featured", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "expertise")
    autocomplete_fields = ("user",)
