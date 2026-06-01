import uuid

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import InstructorProfile, StudentProfile
from categories.models import Category
from certificates.models import Certificate
from certificates.services import generate_certificate_pdf
from courses.models import Assignment, Course, Lesson, Question, Quiz, Resource, Submission
from enrollments.models import Enrollment, LessonProgress, Wishlist
from notifications.models import Notification
from payments.models import Payment
from reviews.models import Rating, Review

from .permissions import IsAdminOrReadOnly, IsInstructorOrAdmin, IsOwnerInstructorOrAdmin
from .serializers import (
    AssignmentSerializer,
    CategorySerializer,
    CertificateSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    InstructorProfileSerializer,
    LessonProgressSerializer,
    LessonSerializer,
    NotificationSerializer,
    PaymentSerializer,
    QuestionSerializer,
    QuizSerializer,
    RatingSerializer,
    RegisterSerializer,
    ResourceSerializer,
    ReviewSerializer,
    StudentProfileSerializer,
    SubmissionSerializer,
    UserSerializer,
    WishlistSerializer,
)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ("email", "username", "first_name", "last_name")
    ordering_fields = ("date_joined", "role", "email")

    def get_queryset(self):
        if self.request.user.role == "ADMIN" or self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "PATCH":
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(request.user).data)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at")

    def get_queryset(self):
        return Category.objects.annotate(course_count=Count("courses")).filter(is_active=True)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    search_fields = ("title", "description", "instructor__first_name", "instructor__last_name", "category__name")
    ordering_fields = ("created_at", "price", "title", "level")

    def get_queryset(self):
        qs = Course.objects.select_related("instructor", "category", "rating_summary").prefetch_related("lessons")
        user = self.request.user
        if not (user.is_authenticated and user.role in {"ADMIN", "INSTRUCTOR"}):
            qs = qs.filter(is_published=True)

        query = self.request.query_params.get("search")
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(instructor__first_name__icontains=query)
                | Q(instructor__last_name__icontains=query)
                | Q(category__name__icontains=query)
            )
        category = self.request.query_params.get("category")
        level = self.request.query_params.get("level")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        min_rating = self.request.query_params.get("min_rating")
        if category:
            qs = qs.filter(Q(category__slug=category) | Q(category__name__iexact=category))
        if level:
            qs = qs.filter(level=level.upper())
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if min_rating:
            qs = qs.filter(rating_summary__average_rating__gte=min_rating)
        return qs

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related("course", "course__instructor")
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerInstructorOrAdmin]
    search_fields = ("title", "description", "course__title")
    ordering_fields = ("order", "duration", "created_at")


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.select_related("lesson", "lesson__course")
    serializer_class = ResourceSerializer
    permission_classes = [IsInstructorOrAdmin]


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related("course").prefetch_related("questions")
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("quiz", "quiz__course")
    serializer_class = QuestionSerializer
    permission_classes = [IsInstructorOrAdmin]


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related("course")
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerInstructorOrAdmin]

    def get_queryset(self):
        qs = Submission.objects.select_related("assignment", "assignment__course", "student")
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "INSTRUCTOR":
            return qs.filter(assignment__course__instructor=self.request.user)
        return qs.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerInstructorOrAdmin]

    def get_queryset(self):
        qs = Enrollment.objects.select_related("student", "course", "course__instructor", "course__category")
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "INSTRUCTOR":
            return qs.filter(course__instructor=self.request.user)
        return qs.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-progress")
    def mark_progress(self, request, pk=None):
        enrollment = self.get_object()
        progress = float(request.data.get("progress", enrollment.progress))
        enrollment.mark_progress(progress)
        if enrollment.completed and not hasattr(enrollment, "certificate"):
            certificate = Certificate.objects.create(
                student=enrollment.student,
                course=enrollment.course,
                enrollment=enrollment,
                issue_date=timezone.localdate(),
            )
            generate_certificate_pdf(certificate)
            Notification.objects.create(
                user=enrollment.student,
                notification_type=Notification.Type.CERTIFICATE,
                title="Certificate ready",
                message=f"Your certificate for {enrollment.course.title} is ready to download.",
            )
        return Response(self.get_serializer(enrollment).data)


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = LessonProgress.objects.select_related("enrollment", "lesson")
        if self.request.user.role == "ADMIN":
            return qs
        return qs.filter(enrollment__student=self.request.user)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(student=self.request.user).select_related("course")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ("course__title", "comment")
    ordering_fields = ("created_at", "rating")

    def get_queryset(self):
        qs = Review.objects.select_related("student", "course")
        if self.request.user.is_authenticated and self.request.user.role == "ADMIN":
            return qs
        return qs.filter(is_approved=True)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class RatingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rating.objects.select_related("course")
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]


class CertificateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerInstructorOrAdmin]

    def get_queryset(self):
        qs = Certificate.objects.select_related("student", "course", "enrollment")
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "INSTRUCTOR":
            return qs.filter(course__instructor=self.request.user)
        return qs.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerInstructorOrAdmin]

    def get_queryset(self):
        qs = Payment.objects.select_related("student", "course")
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "INSTRUCTOR":
            return qs.filter(course__instructor=self.request.user)
        return qs.filter(student=self.request.user)

    def perform_create(self, serializer):
        order_id = f"ORD-{uuid.uuid4().hex[:18].upper()}"
        serializer.save(student=self.request.user, order_id=order_id)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        payment = self.get_object()
        payment.transaction_id = request.data.get("transaction_id", payment.transaction_id)
        payment.gateway_response = request.data.get("gateway_response", {})
        payment.payment_status = Payment.Status.SUCCESS
        payment.save(update_fields=["transaction_id", "gateway_response", "payment_status", "updated_at"])
        Notification.objects.create(
            user=payment.student,
            notification_type=Notification.Type.PAYMENT,
            title="Payment successful",
            message=f"Payment for {payment.course.title} has been recorded.",
        )
        return Response(self.get_serializer(payment).data, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "ADMIN":
            return Notification.objects.select_related("user")
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({"status": "ok"})


class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudentProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InstructorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = InstructorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "ADMIN":
            return InstructorProfile.objects.select_related("user")
        return InstructorProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
