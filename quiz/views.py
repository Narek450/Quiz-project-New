from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from .models import Quizzes, Question, Category, Answer
from .serializers import QuizSerializer, QuestionSerializer, RandomQuestionSerializer
from rest_framework.views import APIView

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

def submit_answer(request):
    if request.method == 'POST':
        score = calculate_score(request) 

        context = {
            'score': score,
        }
        return render(request, 'quiz/result.html', context)
    else:
        return render(request, 'quiz/answer_form.html')

def calculate_score(request):
    score = 0
    for question in request.POST:
        if question.startswith('question_'):
            selected_answer_id = request.POST[question]
            answer = Answer.objects.get(id=selected_answer_id)
            if answer.is_right: 
                score += 1
    return score

def result_view(request):
    score = calculate_score(request)  

    context = {
        'score': score,
    }

    return render(request, 'quiz/result.html', context)
