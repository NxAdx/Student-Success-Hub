from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Student Success Hub!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
        if hasattr(user, 'alumni_profile'):
            return redirect('alumni_detail', pk=user.alumni_profile.pk)
    else:
        user = request.user
    bookmarks = []
    # Fetch bookmarks only for the logged-in user's own profile
    if user == request.user:
        bookmarks = user.bookmarks.select_related('resource', 'resource__category').all()

    return render(request, 'accounts/profile.html', {'profile_user': user, 'bookmarks': bookmarks})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def choose_avatar_view(request):
    avatar_seeds = [
        'Felix', 'Aneka', 'Jake', 'Aria', 'Madeleine', 'Milo',
        'Sorelle', 'Jade', 'Vitaly', 'Maria', 'Oliver', 'Sofia',
        'Luna', 'Max', 'Zoe', 'Leo', 'Iris', 'Kai',
        'Nova', 'Rio', 'Elara', 'Cleo', 'phoenix', 'storm',
    ]
    return render(request, 'accounts/choose_avatar.html', {'avatar_seeds': avatar_seeds})


@login_required
def save_avatar_view(request):
    if request.method == 'POST':
        avatar_url = request.POST.get('avatar_url', '')
        if avatar_url:
            import requests as http_requests
            from django.core.files.base import ContentFile
            try:
                response = http_requests.get(avatar_url, timeout=10)
                if response.status_code == 200:
                    # Extract seed name for filename
                    seed = 'avatar'
                    if 'seed=' in avatar_url:
                        seed = avatar_url.split('seed=')[1].split('&')[0]
                    file_name = f"avatar_{request.user.username}_{seed}.png"
                    request.user.avatar.save(file_name, ContentFile(response.content), save=True)
                    messages.success(request, 'Avatar updated successfully! 🎉')
                else:
                    messages.error(request, 'Failed to download avatar. Please try again.')
            except Exception as e:
                messages.error(request, f'Error saving avatar: {e}')
        else:
            messages.warning(request, 'No avatar selected.')
    return redirect('choose_avatar')
