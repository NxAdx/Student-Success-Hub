from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from .models import Resource, Category, ResourceBookmark


@login_required
def resource_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    rtype = request.GET.get('type', '')
    resources = Resource.objects.select_related('category', 'uploaded_by').all()
    if query:
        resources = resources.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        resources = resources.filter(category_id=category_id)
    if difficulty:
        resources = resources.filter(difficulty=difficulty)
    if rtype:
        resources = resources.filter(resource_type=rtype)
    categories = Category.objects.all()
    return render(request, 'resources/resource_list.html', {
        'resources': resources,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_difficulty': difficulty,
        'selected_type': rtype,
    })


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource.objects.select_related('category', 'uploaded_by'), pk=pk)
    resource.views_count += 1
    resource.save(update_fields=['views_count'])
    is_bookmarked = ResourceBookmark.objects.filter(user=request.user, resource=resource).exists()
    return render(request, 'resources/resource_detail.html', {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
    })


@login_required
def add_resource(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category', '')
        resource_type = request.POST.get('resource_type', 'link')
        difficulty = request.POST.get('difficulty', 'beginner')
        url = request.POST.get('url', '')
        resource = Resource(
            title=title,
            description=description,
            resource_type=resource_type,
            difficulty=difficulty,
            url=url,
            uploaded_by=request.user,
        )
        if category_id:
            resource.category_id = int(category_id)
        if 'file' in request.FILES:
            resource.file = request.FILES['file']
        if 'thumbnail' in request.FILES:
            resource.thumbnail = request.FILES['thumbnail']
        resource.save()
        django_messages.success(request, 'Resource added successfully!')
        return redirect('resource_detail', pk=resource.pk)
    categories = Category.objects.all()
    return render(request, 'resources/add_resource.html', {'categories': categories})


@login_required
def toggle_bookmark(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    bookmark, created = ResourceBookmark.objects.get_or_create(user=request.user, resource=resource)
    if not created:
        bookmark.delete()
        django_messages.info(request, 'Bookmark removed.')
    else:
        django_messages.success(request, 'Resource bookmarked!')
    return redirect('resource_detail', pk=pk)
