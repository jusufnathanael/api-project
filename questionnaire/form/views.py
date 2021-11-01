from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from django.db.models import query
from django.db.models.fields import IntegerField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import json


# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser

from .serializers import UserSerializer, QuestionSerializer, ChoiceSerializer, AnswerSerializer
from .models import User, Question, Choice, Answer
from django.core import serializers

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return (True if request.user.is_superuser else obj == request.user) if request.user else False

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsStaff(BasePermission):
    def has_permissions(self, request, view):
        return request.user and request.user.is_staff


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        allowed = ['retrieve', 'update', 'partial_update', 'destroy']
        if self.action in allowed:
            self.permission_classes = [IsOwner]
        elif self.action == 'list':
            self.permission_classes = [IsUser]
        return super(self.__class__, self).get_permissions()    

    def list(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            return HttpResponseRedirect(f"/users/{request.user.id}")
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer    

    def get_permissions(self):
        if self.action != 'list' and self.action != 'retrieve':
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()

"""
class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

    def get_permissions(self):
        if self.action != 'list' and self.action != 'retrieve':
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()
"""

class IsOwnerAns(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        print(obj.user)
        return (True if request.user.is_superuser else obj.user == request.user) if request.user else False


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    questions = []
    for question in Question.objects.all():
        dic = dict(filter(lambda x: x[0] != '_state', question.__dict__.items()))
        choices = [object.__dict__['choice'] for object in Choice.objects.filter(question=dic['id'])]
        dic['choices'] = choices if len(choices) > 0 else None
        questions.append(dic)

    def retrieve(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(None)
        queryset = Answer.objects.all()
        answer = get_object_or_404(queryset, pk=pk, user=request.user)
        serializer_context = { 'request': request }
        serializer = AnswerSerializer(answer, context=serializer_context)
        return Response({'answer': serializer.data, 'questions': self.questions})
    
    def list(self, request):
        user = Answer.objects.get(user=request.user) if Answer.objects.filter(user=request.user).exists() else None
        if user and not request.user.is_staff:
            return HttpResponseRedirect(f"/answers/{user.id}")
        queryset = Answer.objects.all()
        serializer_context = { 'request': request }
        serializer = AnswerSerializer(queryset, many=True, context=serializer_context)
        return Response({'answers': serializer.data, 'questions': self.questions})

    def create(self, validated_data):
        data = validated_data.data
        answer, created = Answer.objects.update_or_create(
            user = User.objects.get(id=data['user'][7:len(data['user'])-1]),
            q1 = data['q1'],
            q2 = ', '.join(data.getlist('q2')),
            q3 = data['q3'],
            q4 = ', '.join(data.getlist('q4')),
            q5 = data['q5'],
        )
        return HttpResponseRedirect(f"/answers/{answer.id}")

    def update(self, validated_data, pk=None):
        data = validated_data.data
        answer = Answer.objects.get(pk=pk)
        answer.q1 = data['q1']
        answer.q2 = ', '.join(data.getlist('q2'))
        answer.q3 = data['q3']
        answer.q4 = ', '.join(data.getlist('q4'))
        answer.q5 = data['q5']
        answer.save()
        return HttpResponseRedirect(f"/answers/{answer.id}")

    def get_permissions(self):
        allowed = ['retrieve', 'update', 'partial_update', 'destroy']
        if self.action in allowed:
            self.permission_classes = [IsOwnerAns]
        elif self.action == 'list':
            self.permission_classes = [IsUser]
        return super(self.__class__, self).get_permissions()    


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("api-root"))
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session["username"] = username
            return HttpResponseRedirect(reverse("api-root"))
        else:
            return render(request, "form/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "form/login.html")


def logout_view(request):
    logout(request)
    if "username" in request.session:
        del request.session["username"]
    return HttpResponseRedirect(reverse("api-root"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("api-root"))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "form/signup.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "form/signup.html", {
                "message": "Username already taken."
            })
        request.session["username"] = username
        login(request, user)
        return HttpResponseRedirect(reverse("api-root"))
    else:
        return render(request, "form/signup.html")
