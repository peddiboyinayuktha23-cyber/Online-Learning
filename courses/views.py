from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from categories.models import Category
from enrollments.models import Enrollment

from .models import Course


def courses(request):
    queryset = Course.objects.filter(is_published=True).select_related("category", "instructor", "rating_summary")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    level = request.GET.get("level", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    rating = request.GET.get("rating", "").strip()

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(instructor__first_name__icontains=query)
            | Q(instructor__last_name__icontains=query)
            | Q(category__name__icontains=query)
        )
    if category:
        queryset = queryset.filter(category__slug=category)
    if level:
        queryset = queryset.filter(level=level.upper())
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if rating:
        queryset = queryset.filter(rating_summary__average_rating__gte=rating)

    return render(
        request,
        "courses/courses.html",
        {"courses": queryset, "categories": Category.objects.filter(is_active=True), "filters": request.GET},
    )


def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.select_related("category", "instructor").prefetch_related("lessons", "reviews"),
        slug=slug,
        is_published=True,
    )
    enrolled = request.user.is_authenticated and Enrollment.objects.filter(student=request.user, course=course).exists()
    return render(request, "courses/course_detail.html", {"course": course, "enrolled": enrolled})


def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if request.user.is_authenticated:
        Enrollment.objects.get_or_create(student=request.user, course=course)
        return redirect("student_dashboard")
    return redirect("login")
