import json

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse

from .forms import CustomUserCreationForm, LoginForm
from .models import CustomUser
from posts.models import PostModel, CommentModel

from helpers.users import follow_or_unfollow_user, remove_follower, get_total_following, get_total_followers, search_user, FOLLOWERS, FOLLOWING


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
    page_user = get_object_or_404(CustomUser, username=username)
    logged_user = request.user
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'action' not in data.keys():
            raise ValueError("Missing 'action' tag in POST request.")
        
        if data['action'] == 'follow-unfollow':
            return follow_or_unfollow_user(data, logged_user, page_user)
        elif data['action'] == 'remove-follower':
            return remove_follower(data, logged_user, page_user)
        else:
            ValueError(f"Invalid 'action' key, expected 'remove-follower' or 'follow-unfollow', but {data['action']} was passed.")
    

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
                        'following_qty': get_total_following(page_user),
                        'followers_qty': get_total_followers(page_user),
                    })
    

@login_required
def following(request, username):
    if request.method == 'GET': 
        page_user =  get_object_or_404(CustomUser, username=username)
        logged_user = get_object_or_404(CustomUser, username=request.user)
        following_list = [(user, logged_user.is_following(user.id)) for user in page_user.following.all()]
        return render(request, 'users/users_card.html',
                        {
                            'profile_user': page_user,
                            'user_list': following_list,
                            'logged_user': logged_user,
                            'page_title': 'Seguindo',
                            'search_url': reverse('users:following_search', kwargs={'username':username}),
                        })
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes
    

@login_required
def followers(request, username):
    if request.method == 'GET': 
        page_user =  get_object_or_404(CustomUser, username=username)
        logged_user = get_object_or_404(CustomUser, username=request.user)
        followers_list = [(user, logged_user.is_following(user.id))
                        for user in CustomUser.objects.filter(following=page_user)]
        return render(request, 'users/users_card.html',
                        {
                            'profile_user': page_user,
                            'user_list': followers_list,
                            'logged_user': logged_user,
                            'page_title': 'Seguidores',
                            'search_url': reverse('users:followers_search', kwargs={'username':username}),
                        })
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes

@login_required
def search(request): # TODO: Testes
    if request.method == 'GET':
        query = request.GET.get('q', '')
        return JsonResponse({
            'user_list': search_user(substring=query, logged_user=request.user),
            'profile_user': None,
            'show_bio': False,
            'show_relationship': False,
            'show_remove': False,
        }) 
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes


@login_required
def following_search(request, username):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        return JsonResponse({
            'user_list': search_user(substring=query, logged_user=request.user, search_in=FOLLOWING, identification=username),
            'profile_user': username,
            'show_bio': True,
            'show_relationship': True,
            'show_remove': False,
        })
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes
    

@login_required
def followers_search(request, username):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        return JsonResponse({
            'user_list': search_user(substring=query, logged_user=request.user, search_in=FOLLOWERS, identification=username),
            'profile_user': username,
            'show_bio': True,
            'show_relationship': True,
            'show_remove': (username == request.user.username),
        })
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes
    
