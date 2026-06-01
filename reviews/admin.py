from django.contrib import admin

from .models import Rating, Reply, Review


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    fields = ("user", "comment", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = ("course__title", "student__email", "student__first_name", "student__last_name", "comment")
    autocomplete_fields = ("course", "student")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ReplyInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course", "student")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("course", "average_rating", "total_reviews", "updated_at")
    search_fields = ("course__title",)
    autocomplete_fields = ("course",)
    readonly_fields = ("updated_at",)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "created_at")
    search_fields = ("review__course__title", "user__email", "comment")
    autocomplete_fields = ("review", "user")
    readonly_fields = ("created_at", "updated_at")
