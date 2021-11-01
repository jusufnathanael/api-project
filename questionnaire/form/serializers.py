from rest_framework import serializers

from .models import User, Question, Choice, Answer

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    choice = serializers.SlugRelatedField(many=True, read_only=True, slug_field='choice')
    class Meta:
        model = Question
        fields = ['id', 'name', 'type', 'choice']

class ChoiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'question', 'choice')

class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'user', 'q1', 'q2', 'q3', 'q4', 'q5')
