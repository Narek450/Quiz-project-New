from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from .models import Quizzes, Question, Category, Answer, QuizAttempt
from .serializers import QuizSerializer, QuestionSerializer, RandomQuestionSerializer
from rest_framework.views import APIView
from .forms import CategoryForm, CreateQuizForm, QuestionForm, AnswerForm, CreateQuestionForm, AnswerFormSet
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib.auth.models import User
from accounts.models import CustomUser
from django.db.models import Sum


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


def submit_answer(request, quiz_id):
    quiz = get_object_or_404(Quizzes, id=quiz_id)
    
    if request.method == 'POST':
        score = calculate_score(request, quiz_id)
        user_score = request.session.get('score', 0) 

        if score > user_score:
            user_score = score

        request.session['score'] = user_score 
        context = {
            'quiz_id': quiz_id,
            'score': user_score,
        }

        return render(request, 'quiz/quiz_result.html', context)
    else:
        context = {
            'quiz_id': quiz_id,
        }
        return render(request, 'quiz/answer_form.html', context)

def calculate_score(request, quiz_id):
    score = 0
    for question in request.POST:
        if question.startswith('question_'):
            selected_answer_id = request.POST[question]
            answer = Answer.objects.get(id=selected_answer_id)
            if answer.is_right:
                score += 1

    user = request.user

    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.score += score
    user_profile.save()

    quiz = get_object_or_404(Quizzes, id=quiz_id)

    attempt = QuizAttempt.objects.create(user=user, quiz=quiz, score=score)

    return score

def result_view(request, quiz_id):
    score = calculate_score(request, quiz_id)  

    context = {
        'score': score,
    }

    return render(request, 'quiz/result.html', context)

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


from django.db.models import Sum

def user_scores(request):
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
        user_profile.scores_by_category = scores_by_category

        user_profile.save()

    context = {
        'user_profiles': user_profiles,
    }
    return render(request, 'quiz/scores.html', context)

def save_quiz_attempt(request, quiz_id, score):
    user = request.user

    quiz = Quizzes.objects.get(id=quiz_id)

    quiz_attempt, created = QuizAttempt.objects.get_or_create(user=user, quiz=quiz)

    if not created:
        quiz_attempt.score += score
        quiz_attempt.save()

    return score

def calculate_total_score(user_profile):
    total_score = user_profile.score
    user_profile.total_score = total_score
    user_profile.save()