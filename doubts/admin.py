from django.contrib import admin
from .models import Question, Answer, AnswerVote

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'asked_by', 'subject', 'is_resolved', 'views_count']
    list_filter = ['is_resolved', 'subject']
    search_fields = ['title', 'body']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'answered_by', 'is_best_answer', 'upvotes']
    list_filter = ['is_best_answer']

@admin.register(AnswerVote)
class AnswerVoteAdmin(admin.ModelAdmin):
    list_display = ['answer', 'user', 'is_upvote']
