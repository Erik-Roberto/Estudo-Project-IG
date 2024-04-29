
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required



from .forms import CustomUserCreationForm, LoginForm
from .models import CustomUser
from posts.models import PostModel
from comments.models import CommentModel

from helpers.users import follow_or_unfollow_user


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
    posts = page_user.posts.all().values()
    for post_dict in posts:
        post_obj = PostModel.objects.get(id=post_dict['id'])
        post_dict.update(
            {
                'likes': post_obj.likes.all().count(),
                'comments': CommentModel.objects.filter(post=post_obj).count(),
            })
    return render(request, 'users/profile.html',
                   {
                        'profile_user': page_user,
                        'posts': posts,
                        'logged_user': logged_user,
                        'is_following': logged_user.is_following(page_user.id),
                        'following_qty': page_user.following.all().count(),
                        'followers_qty': CustomUser.objects.filter(following=page_user).count()
                    })
    

@login_required
def following(request, username):
    if request.method == 'POST':
        return follow_or_unfollow_user(request)
    page_user =  get_object_or_404(CustomUser, username=username)
    logged_user = get_object_or_404(CustomUser, username=request.user)
    following_list = [(user, logged_user.is_following(user.id)) for user in page_user.following.all()]
    return render(request, 'users/following-followers.html',
                   {
                        'profile_user': page_user,
                        'user_list': following_list,
                        'logged_user': CustomUser.objects.get(username=request.user),
                        'page_title': 'Following',
                    })


@login_required
def followers(request, username):
    if request.method == 'POST':
        return 'sorry'
    
    page_user =  get_object_or_404(CustomUser, username=username)
    logged_user = get_object_or_404(CustomUser, username=request.user)
    followers_list = [(user, logged_user.is_following(user.id))
                       for user in CustomUser.objects.filter(following=logged_user)]
    return render(request, 'users/following-followers.html',
                   {
                        'profile_user': page_user,
                        'user_list': followers_list,
                        'logged_user': CustomUser.objects.get(username=request.user),
                        'page_title': 'Followers',
                    })