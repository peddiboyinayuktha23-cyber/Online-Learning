from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import InstructorProfile, StudentProfile
from categories.models import Category
from certificates.models import Certificate
from courses.models import Assignment, Course, Lesson, Question, Quiz, Resource, Submission
from enrollments.models import Enrollment, LessonProgress, Wishlist
from notifications.models import Notification
from payments.models import Payment
from reviews.models import Rating, Review

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "full_name", "role", "profile_picture")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "confirm_password", "first_name", "last_name", "role")
        read_only_fields = ("id",)

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "profile_picture",
            "bio",
            "phone",
            "role",
            "email_verified",
            "date_joined",
            "is_active",
        )
        read_only_fields = ("id", "role", "email_verified", "date_joined", "is_active")


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "is_active", "course_count", "created_at", "updated_at")
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "course", "title", "slug", "video_file", "description", "duration", "order", "is_preview")
        read_only_fields = ("id", "slug")


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ("id", "lesson", "title", "file", "order", "created_at")
        read_only_fields = ("id", "created_at")


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category", write_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "instructor",
            "category",
            "category_id",
            "thumbnail",
            "price",
            "level",
            "language",
            "is_published",
            "average_rating",
            "lessons",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "instructor", "created_at", "updated_at")


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "quiz",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "order",
        )
        read_only_fields = ("id",)


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "course", "title", "passing_score", "questions")
        read_only_fields = ("id",)


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ("id", "course", "title", "description", "due_date", "attachment", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSummarySerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ("id", "assignment", "student", "uploaded_file", "notes", "grade", "feedback", "submitted_at")
        read_only_fields = ("id", "student", "grade", "feedback", "submitted_at")


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSummarySerializer(read_only=True)
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "student", "course", "course_detail", "enrolled_at", "progress", "completed", "completed_at")
        read_only_fields = ("id", "student", "enrolled_at", "completed_at")


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ("id", "enrollment", "lesson", "completed", "watched_seconds", "updated_at")
        read_only_fields = ("id", "updated_at")


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ("id", "student", "course", "created_at")
        read_only_fields = ("id", "student", "created_at")


class ReviewSerializer(serializers.ModelSerializer):
    student = UserSummarySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "student", "course", "rating", "comment", "is_approved", "created_at", "updated_at")
        read_only_fields = ("id", "student", "is_approved", "created_at", "updated_at")


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("id", "course", "average_rating", "total_reviews", "updated_at")
        read_only_fields = fields


class CertificateSerializer(serializers.ModelSerializer):
    student = UserSummarySerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = ("id", "student", "course", "certificate_id", "issue_date", "pdf_file", "enrollment")
        read_only_fields = ("id", "student", "certificate_id", "issue_date", "pdf_file")


class PaymentSerializer(serializers.ModelSerializer):
    student = UserSummarySerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "student",
            "course",
            "amount",
            "gateway",
            "payment_status",
            "transaction_id",
            "order_id",
            "currency",
            "invoice_file",
            "payment_date",
        )
        read_only_fields = ("id", "student", "payment_status", "transaction_id", "order_id", "invoice_file", "payment_date")


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "user", "notification_type", "title", "message", "is_read", "created_at")
        read_only_fields = ("id", "user", "created_at")


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("id", "user", "headline", "learning_goals", "interests", "website", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")


class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = (
            "id",
            "user",
            "expertise",
            "experience_years",
            "linkedin_url",
            "website",
            "total_students",
            "average_rating",
            "is_featured",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "total_students", "average_rating", "created_at", "updated_at")
