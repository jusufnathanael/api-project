from django.contrib import admin

# Register your models here.
from .models import User, Question, Choice, Answer

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)