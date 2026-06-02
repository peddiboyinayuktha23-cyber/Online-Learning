from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render

from .forms import QuizAnswerForm
from .models import Answer, Quiz, QuizAttempt


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.prefetch_related("questions"), id=quiz_id, is_active=True)
    if request.method == "POST":
        attempt = QuizAttempt.objects.create(quiz=quiz, student=request.user)
        form = QuizAnswerForm(request.POST, quiz=quiz)
        if form.is_valid():
            for question in quiz.questions.all():
                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=form.cleaned_data[str(question.id)],
                )
            attempt.calculate_score()
            return redirect("quiz_result", attempt_id=attempt.id)
    else:
        form = QuizAnswerForm(quiz=quiz)
    return render(request, "quizzes/quiz.html", {"quiz": quiz, "form": form})


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt.objects.select_related("quiz", "student"), id=attempt_id, student=request.user)
    return render(request, "quizzes/result.html", {"attempt": attempt})


def leaderboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaders = (
        QuizAttempt.objects.filter(quiz=quiz, submitted_at__isnull=False)
        .values("student__first_name", "student__last_name", "student__email")
        .annotate(best_score=Max("score"))
        .order_by("-best_score")[:20]
    )
    return render(request, "quizzes/leaderboard.html", {"quiz": quiz, "leaders": leaders})
