from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:quiz_id>/", views.quiz_detail, name="quiz_detail"),
    path("result/<uuid:attempt_id>/", views.quiz_result, name="quiz_result"),
    path("<uuid:quiz_id>/leaderboard/", views.leaderboard, name="quiz_leaderboard"),
]
