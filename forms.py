from django import forms
from django.forms.models import inlineformset_factory
from .models import Category, Quizzes, Question, Answer

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quizzes
        fields = '__all__'

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

AnswerFormSet = inlineformset_factory(Question, Answer, form=AnswerForm, extra=3)

class CreateQuizForm(forms.ModelForm):
    class Meta:
        model = Quizzes
        fields = ['title', 'category']

    def save(self, commit=True):
        quiz = super().save(commit=False)
        if commit:
            quiz.save()
        return quiz

class CreateQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    answers = AnswerFormSet()