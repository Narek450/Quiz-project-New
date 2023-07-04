from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from .models import Quizzes, Question, Category, Answer, QuizAttempt
from .serializers import QuizSerializer, QuestionSerializer, RandomQuestionSerializer
from rest_framework.views import APIView
from .forms import CategoryForm, CreateQuizForm, QuestionForm, AnswerForm, CreateQuestionForm, AnswerFormSet
from .models import UserProfile
from django.contrib.auth.models import User
from accounts.models import CustomUser
from django.db.models import Sum
from operator import attrgetter


class Quiz(APIView):

    def get(self, request, format=None):
        quizzes = Quizzes.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

class RandomQuestion(APIView):

    def get(self, request, topic, format=None):
        question = Question.objects.filter(quiz__title=topic).order_by('?')[:1]
        serializer = RandomQuestionSerializer(question, many=True)
        return Response(serializer.data)

class QuizQuestion(APIView):

    def get(self, request, topic, format=None):
        question = Question.objects.filter(quiz__title=topic)
        serializer = QuestionSerializer(question, many=True)
        return Response(serializer.data)

def get_question_with_answers(request, question_id):
    question = Question.objects.get(id=question_id)
    answers = question.answer.all()

    context = {
        'question': question,
        'answers': answers
    }
    return render(request, 'question_with_answers.html', context)

def question_page(request, quiz_id):
    quiz = Quizzes.objects.get(id=quiz_id)
    questions = Question.objects.filter(quiz__id=quiz_id)

    
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quiz/question_page.html', context)

def calculate_score(request):
    score = 0
    for question in request.POST:
        if question.startswith('question_'):
            selected_answer_id = request.POST[question]
            answer = Answer.objects.get(id=selected_answer_id)
            if answer.is_right:
                score += 1
    
    user = request.user 
    
    attempt, created = QuizAttempt.objects.get_or_create(user=user, defaults={'score': score})
    
    if not created:
        attempt.score = score
        attempt.save()
    
    return score

def submit_answer(request):
    if request.method == 'POST':
        user = request.user
        quiz_id = request.POST.get('quiz_id')
        score = calculate_score(request)

        if quiz_id:
            quiz = Quiz.objects.get(id=quiz_id)
            attempt, created = QuizAttempt.objects.get_or_create(user=user, quiz=quiz, defaults={'score': score})

            if not created:
                attempt.score = score
                attempt.save()

        return redirect('quiz:quiz_result')

    return redirect('quiz:quiz_list')
    

def result_view(request):
    score = calculate_score(request)  

    context = {
        'score': score,
    }

    return render(request, 'quiz/quiz_result.html', context)

def quiz_list(request):
    quizzes = Quizzes.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

from django.shortcuts import redirect

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:create_quiz')
    else:
        form = CategoryForm()
    
    return render(request, 'quiz/create_category.html', {'form': form})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'quiz/category_list.html', {'categories': categories})

def create_quiz(request):
    if request.method == 'POST':
        form = CreateQuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.author = request.user
            quiz.save()
            return redirect('quiz:create_question')
    else:
        form = CreateQuizForm()

    return render(request, 'quiz/create_quiz.html', {'form': form})

def create_question(request):
    if request.method == 'POST':
        form = CreateQuestionForm(request.POST)
        formset = AnswerFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            question = form.save()  

            answers = formset.save(commit=False)  
            for answer in answers:
                answer.question = question
                answer.save()  

            return redirect('quiz:question_list') 
    else:
        form = CreateQuestionForm()
        formset = AnswerFormSet()

    return render(request, 'quiz/create_question.html', {'form': form, 'formset': formset})


def question_list(request):
    questions = Question.objects.all()
    return render(request, 'quiz/question_list.html', {'questions': questions})

def save_score(request, score):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.score = score
    user_profile.save()

def quiz_results(request):
    user = request.user
    quiz_attempts = QuizAttempt.objects.filter(user=user)
    
    context = {
        'quiz_attempts': quiz_attempts
    }
    
    return render(request, 'quiz_results.html', context)

def save_quiz_attempt(request, quiz_id, score):
    user = request.user
    quiz = Quizzes.objects.get(id=quiz_id)

    user.score += score
    user.save()

    quiz_attempt, created = QuizAttempt.objects.get_or_create(user=user, quiz=quiz)

    if not created:
        quiz_attempt.score += score
        quiz_attempt.save()

    return score


def user_scores(request):
    categories = Category.objects.all()
    user_profiles = CustomUser.objects.all()

    for user_profile in user_profiles:
        quiz_attempts = QuizAttempt.objects.filter(user=user_profile)
        scores_by_category = quiz_attempts.values('quiz__category').annotate(total_score=Sum('score'))

        total_score = 0
        for score in scores_by_category:
            total_score += score['total_score']

        if total_score is not None:
            user_profile.score = total_score
        else:
            user_profile.score = 0
        user_profile.scores_by_category = scores_by_category.all()

    user_profiles = sorted(user_profiles, key=attrgetter('score'), reverse=True)

    context = {
        'categories': categories,
        'user_profiles': user_profiles,
    }

    return render(request, 'quiz/scores.html', context)




