from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AssignmentViewSet,
    CategoryViewSet,
    CertificateViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    InstructorProfileViewSet,
    LessonProgressViewSet,
    LessonViewSet,
    NotificationViewSet,
    PaymentViewSet,
    QuestionViewSet,
    QuizViewSet,
    RatingViewSet,
    RegisterAPIView,
    ResourceViewSet,
    ReviewViewSet,
    StudentProfileViewSet,
    SubmissionViewSet,
    UserViewSet,
    WishlistViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("student-profiles", StudentProfileViewSet, basename="student-profiles")
router.register("instructor-profiles", InstructorProfileViewSet, basename="instructor-profiles")
router.register("categories", CategoryViewSet, basename="categories")
router.register("courses", CourseViewSet, basename="courses")
router.register("lessons", LessonViewSet, basename="lessons")
router.register("resources", ResourceViewSet, basename="resources")
router.register("quizzes", QuizViewSet, basename="quizzes")
router.register("questions", QuestionViewSet, basename="questions")
router.register("assignments", AssignmentViewSet, basename="assignments")
router.register("submissions", SubmissionViewSet, basename="submissions")
router.register("enrollments", EnrollmentViewSet, basename="enrollments")
router.register("lesson-progress", LessonProgressViewSet, basename="lesson-progress")
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("reviews", ReviewViewSet, basename="reviews")
router.register("ratings", RatingViewSet, basename="ratings")
router.register("certificates", CertificateViewSet, basename="certificates")
router.register("payments", PaymentViewSet, basename="payments")
router.register("notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="api-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("", include(router.urls)),
]
