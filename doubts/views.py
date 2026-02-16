from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Question, Answer, AnswerVote


@login_required
def question_list(request):
    query = request.GET.get('q', '')
    subject = request.GET.get('subject', '')
    status = request.GET.get('status', '')
    questions = Question.objects.select_related('asked_by').all()
    if query:
        questions = questions.filter(Q(title__icontains=query) | Q(body__icontains=query) | Q(tags__icontains=query))
    if subject:
        questions = questions.filter(subject__icontains=subject)
    if status == 'resolved':
        questions = questions.filter(is_resolved=True)
    elif status == 'open':
        questions = questions.filter(is_resolved=False)
    subjects = Question.objects.values_list('subject', flat=True).distinct().order_by('subject')
    return render(request, 'doubts/question_list.html', {
        'questions': questions,
        'query': query,
        'subject': subject,
        'status': status,
        'subjects': [s for s in subjects if s],
    })


@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question.objects.select_related('asked_by'), pk=pk)
    question.views_count += 1
    question.save(update_fields=['views_count'])
    answers = Answer.objects.filter(question=question).select_related('answered_by')
    return render(request, 'doubts/question_detail.html', {
        'question': question,
        'answers': answers,
    })


@login_required
def ask_question(request):
    if request.method == 'POST':
        question = Question.objects.create(
            title=request.POST.get('title', ''),
            body=request.POST.get('body', ''),
            subject=request.POST.get('subject', ''),
            tags=request.POST.get('tags', ''),
            asked_by=request.user,
        )
        messages.success(request, 'Question posted!')
        return redirect('question_detail', pk=question.pk)
    return render(request, 'doubts/ask_question.html')


@login_required
def post_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        body = request.POST.get('body', '')
        if body:
            Answer.objects.create(
                question=question,
                body=body,
                answered_by=request.user,
            )
            messages.success(request, 'Answer posted!')
    return redirect('question_detail', pk=pk)


@login_required
def upvote_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    vote, created = AnswerVote.objects.get_or_create(answer=answer, user=request.user)
    if created:
        answer.upvotes += 1
        answer.save(update_fields=['upvotes'])
    else:
        vote.delete()
        answer.upvotes = max(0, answer.upvotes - 1)
        answer.save(update_fields=['upvotes'])
    return redirect('question_detail', pk=answer.question.pk)


@login_required
def mark_best_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user == answer.question.asked_by:
        Answer.objects.filter(question=answer.question).update(is_best_answer=False)
        answer.is_best_answer = True
        answer.save(update_fields=['is_best_answer'])
        answer.question.is_resolved = True
        answer.question.save(update_fields=['is_resolved'])
        messages.success(request, 'Best answer selected!')
    return redirect('question_detail', pk=answer.question.pk)
