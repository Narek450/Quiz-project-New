from . import views
from django.urls import path
from .views import Quiz, RandomQuestion, QuizQuestion, get_question_with_answers

app_name='quiz'

urlpatterns = [
    path('', views.Quiz.as_view(), name='quiz'),
    path('question/<int:question_id>/', views.get_question_with_answers, name='question_with_answers'),
    path('r/<str:topic>', views.RandomQuestion.as_view(), name='random'),
    path('q/<str:topic>', views.QuizQuestion.as_view(), name='questions'),
]
