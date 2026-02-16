import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Roadmap, RoadmapNode, UserNodeProgress


@login_required
def roadmap_list(request):
    category = request.GET.get('category', '')
    roadmaps = Roadmap.objects.filter(status='approved').select_related('created_by')
    if category:
        roadmaps = roadmaps.filter(category=category)
    # Also show user's own drafts/pending
    my_roadmaps = Roadmap.objects.filter(created_by=request.user).exclude(status='approved')
    return render(request, 'roadmaps/roadmap_list.html', {
        'roadmaps': roadmaps,
        'my_roadmaps': my_roadmaps,
        'selected_category': category,
        'categories': Roadmap.CATEGORY_CHOICES,
    })


@login_required
def roadmap_detail(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk)
    # Only allow viewing approved roadmaps or own roadmaps
    if roadmap.status != 'approved' and roadmap.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'This roadmap is not available.')
        return redirect('roadmaps:roadmap_list')

    nodes = roadmap.nodes.select_related('parent').all()
    # Get user progress for all nodes
    progress_qs = UserNodeProgress.objects.filter(user=request.user, node__roadmap=roadmap)
    progress_map = {p.node_id: p.status for p in progress_qs}

    # Build tree structure for template
    node_data = []
    for node in nodes:
        node_data.append({
            'id': node.id,
            'title': node.title,
            'description': node.description,
            'resources_text': node.resources_text,
            'parent_id': node.parent_id,
            'order': node.order,
            'progress': progress_map.get(node.id, 'not_started'),
        })

    # Calculate completion percentage
    total = len(node_data)
    done = sum(1 for n in node_data if n['progress'] == 'done')
    percent = int((done / total) * 100) if total > 0 else 0

    return render(request, 'roadmaps/roadmap_detail.html', {
        'roadmap': roadmap,
        'nodes_json': json.dumps(node_data),
        'total_nodes': total,
        'done_nodes': done,
        'percent': percent,
    })


@login_required
def create_roadmap(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other')
        nodes_json = request.POST.get('nodes_json', '[]')

        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'roadmaps/create_roadmap.html', {
                'categories': Roadmap.CATEGORY_CHOICES,
            })

        roadmap = Roadmap.objects.create(
            title=title,
            description=description,
            category=category,
            status='pending',
            created_by=request.user,
        )

        # Parse and create nodes
        try:
            nodes = json.loads(nodes_json)
            node_id_map = {}  # temp_id -> real node
            for node_data in nodes:
                node = RoadmapNode.objects.create(
                    roadmap=roadmap,
                    title=node_data.get('title', 'Untitled'),
                    description=node_data.get('description', ''),
                    resources_text=node_data.get('resources_text', ''),
                    order=node_data.get('order', 0),
                )
                node_id_map[node_data.get('temp_id', '')] = node

            # Set parent relationships
            for node_data in nodes:
                parent_temp_id = node_data.get('parent_temp_id', '')
                if parent_temp_id and parent_temp_id in node_id_map:
                    node = node_id_map[node_data.get('temp_id', '')]
                    node.parent = node_id_map[parent_temp_id]
                    node.save(update_fields=['parent'])
        except (json.JSONDecodeError, Exception):
            pass

        messages.success(request, 'Roadmap submitted for review! 🎉')
        return redirect('roadmaps:roadmap_list')

    return render(request, 'roadmaps/create_roadmap.html', {
        'categories': Roadmap.CATEGORY_CHOICES,
    })


@login_required
def edit_roadmap(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk, created_by=request.user)
    if roadmap.status == 'approved':
        messages.warning(request, 'Cannot edit an approved roadmap.')
        return redirect('roadmaps:roadmap_detail', pk=pk)

    if request.method == 'POST':
        roadmap.title = request.POST.get('title', roadmap.title).strip()
        roadmap.description = request.POST.get('description', '').strip()
        roadmap.category = request.POST.get('category', roadmap.category)
        roadmap.status = 'pending'
        roadmap.save()

        # Replace nodes
        nodes_json = request.POST.get('nodes_json', '[]')
        try:
            nodes_data = json.loads(nodes_json)
            roadmap.nodes.all().delete()
            node_id_map = {}
            for nd in nodes_data:
                node = RoadmapNode.objects.create(
                    roadmap=roadmap,
                    title=nd.get('title', 'Untitled'),
                    description=nd.get('description', ''),
                    resources_text=nd.get('resources_text', ''),
                    order=nd.get('order', 0),
                )
                node_id_map[nd.get('temp_id', '')] = node
            for nd in nodes_data:
                parent_temp_id = nd.get('parent_temp_id', '')
                if parent_temp_id and parent_temp_id in node_id_map:
                    node = node_id_map[nd.get('temp_id', '')]
                    node.parent = node_id_map[parent_temp_id]
                    node.save(update_fields=['parent'])
        except Exception:
            pass

        messages.success(request, 'Roadmap resubmitted for review!')
        return redirect('roadmaps:roadmap_list')

    existing_nodes = list(roadmap.nodes.values('id', 'title', 'description', 'resources_text', 'parent_id', 'order'))
    # Map real IDs to temp_ids for the editor
    for n in existing_nodes:
        n['temp_id'] = str(n['id'])
        n['parent_temp_id'] = str(n['parent_id']) if n['parent_id'] else ''

    return render(request, 'roadmaps/create_roadmap.html', {
        'roadmap': roadmap,
        'categories': Roadmap.CATEGORY_CHOICES,
        'existing_nodes_json': json.dumps(existing_nodes),
        'editing': True,
    })


@login_required
@require_POST
def toggle_node_progress(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk, status='approved')
    try:
        data = json.loads(request.body)
        node_id = data.get('node_id')
        new_status = data.get('status', 'not_started')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    node = get_object_or_404(RoadmapNode, pk=node_id, roadmap=roadmap)
    progress, _ = UserNodeProgress.objects.get_or_create(user=request.user, node=node)
    progress.status = new_status
    progress.save(update_fields=['status', 'updated_at'])

    # Recalculate
    total = roadmap.nodes.count()
    done = UserNodeProgress.objects.filter(user=request.user, node__roadmap=roadmap, status='done').count()
    percent = int((done / total) * 100) if total > 0 else 0

    return JsonResponse({'status': new_status, 'done': done, 'total': total, 'percent': percent})


@staff_member_required
def admin_review(request):
    pending = Roadmap.objects.filter(status='pending').select_related('created_by')
    return render(request, 'roadmaps/admin_review.html', {'pending_roadmaps': pending})


@staff_member_required
@require_POST
def approve_roadmap(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk)
    roadmap.status = 'approved'
    roadmap.save(update_fields=['status'])
    messages.success(request, f'"{roadmap.title}" has been approved!')
    return redirect('roadmaps:admin_review')


@staff_member_required
@require_POST
def reject_roadmap(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk)
    roadmap.status = 'rejected'
    roadmap.rejection_feedback = request.POST.get('feedback', '')
    roadmap.save(update_fields=['status', 'rejection_feedback'])
    messages.info(request, f'"{roadmap.title}" has been rejected.')
    return redirect('roadmaps:admin_review')
