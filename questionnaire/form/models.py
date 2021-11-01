# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

class Question(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choice')
    choice = models.CharField(max_length=100)

class Answer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    q1 = models.CharField(max_length=100)
    q2 = models.CharField(max_length=100)
    q3 = models.CharField(max_length=100)
    q4 = models.CharField(max_length=100)
    q5 = models.CharField(max_length=100)

"""
class Answer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    q1 = models.CharField(max_length=100)
    q2 = models.CharField(max_length=100, choices=models.IntegerChoices('colour', 'blue red green yellow purple pink'))
    q3 = models.CharField(max_length=100, choices=models.IntegerChoices('codelang', 'java ruby javascript golang'))
    q4 = models.CharField(max_length=100, choices=models.IntegerChoices('lang', 'english chinese malay tamil hindi'))
    q5 = models.CharField(max_length=100, choices=models.IntegerChoices('bool', 'yes no'))
"""