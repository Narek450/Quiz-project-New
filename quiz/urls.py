from . import views
from django.urls import path
from .views import Quiz, RandomQuestion, QuizQuestion, get_question_with_answers, question_page, result_view
from django.conf import settings
from django.conf.urls.static import static


app_name='quiz'

urlpatterns = [
    path('', views.Quiz.as_view(), name='home'),
    path('question/<int:question_id>/', views.get_question_with_answers, name='question_with_answers'),
    path('quiz/<int:quiz_id>/', views.question_page, name='question_page'),
    path('quiz/result<int:quiz_id>/', views.result_view, name='quiz_result'),
    path('quiz/submit-answer/<int:quiz_id>/', views.submit_answer, name='submit-answer'),
    path('submit-answer/<int:quiz_id>/', views.submit_answer, name='submit_answer'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/category/', views.create_category, name='create_category'),
    path('quizzes/category/list/', views.category_list, name='category_list'),
    path('quizzes/question/create', views.create_question, name='create_question'),
    path('quizzes/question/list', views.question_list, name='question_list'),
    path('r/<str:topic>', views.RandomQuestion.as_view(), name='random'),
    path('q/<str:topic>', views.QuizQuestion.as_view(), name='questions'),
    path('scores/', views.user_scores, name='scores')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)