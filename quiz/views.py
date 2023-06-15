from django.shortcuts import render
from rest_framework.response import Response
from .models import Quizzes, Question
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
