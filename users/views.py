import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required



from .forms import CustomUserCreationForm, LoginForm
from .models import CustomUser


def sign_up(request):
    if request.user.is_authenticated:
        return redirect(reverse('users:profile', kwargs={'username': request.user.username}))
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('users:profile', kwargs={'username': request.user}))
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome back.')
                return redirect(reverse('users:profile', kwargs={'username': username}))
            else:
                messages.error(request, 'Invalid username or password')
                return render(request, 'users/login.html',{'form': form})
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def profile(request, username):
    if request.method == 'POST':
        return follow_or_unfollow_user(request, username)
    page_user = get_object_or_404(CustomUser, username=username)
    logged_user = get_object_or_404(CustomUser, username=request.user)
    posts = page_user.posts.all()
    return render(request, 'users/profile.html',
                   {
                        'profile_user':page_user,
                        'posts':posts,
                        'logged_user':logged_user,
                        'is_following':logged_user.is_following(page_user.id),
                    })
    

@login_required
def following(request, username):
    if request.method == 'POST':
        return follow_or_unfollow_user(request)
    page_user =  get_object_or_404(CustomUser, username=username)
    logged_user = get_object_or_404(CustomUser, username=request.user)
    following_list = [(user, logged_user.is_following(user.id)) for user in page_user.following.all()]
    return render(request, 'users/following.html',
                   {
                        'profile_user':page_user,
                        'following_list':following_list,
                        'logged_user':CustomUser.objects.get(username=request.user)
                    })


@login_required
def follow_or_unfollow_user(request, username=None):
    data = json.loads(request.body)
    if not 'follow-unfollow' in data.values():
        raise ValueError("Missing 'follow-unfollow' tag in post request.")
    if not username:
        username = data['username']
    logged_user = get_object_or_404(CustomUser, username=request.user)
    target_user = get_object_or_404(CustomUser, username=username)
    if logged_user.following.filter(id=target_user.id).exists():
        # Unfollowing target user
        logged_user.following.remove(target_user)
    else:
        # Following target user
        logged_user.following.add(target_user)
    logged_user.save()
    return JsonResponse({'is_following': logged_user.is_following(target_user.id), 'username': username})