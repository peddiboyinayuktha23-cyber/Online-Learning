from django import forms

from .models import Answer, Quiz


class QuizAnswerForm(forms.Form):
    def __init__(self, *args, quiz: Quiz, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiz = quiz
        for question in quiz.questions.all():
            choices = [("A", question.option_a), ("B", question.option_b)]
            if question.option_c:
                choices.append(("C", question.option_c))
            if question.option_d:
                choices.append(("D", question.option_d))
            self.fields[str(question.id)] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
            )
