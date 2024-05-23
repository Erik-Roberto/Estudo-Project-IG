import json

from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import PostModel, CommentModel
from users.models import CustomUser

from helpers.posts import like_dislike, create_new_comment, is_ajax, get_total_likes
from helpers.users import search_user, POST_LIKES, COMMENT_LIKES


@login_required
def post(request, post_id):
    post = get_object_or_404(PostModel, id=post_id)
    if not post.published:
        raise Http404('Post not found.')
    
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'text' not in data.keys():
            raise ValueError("Missing 'text' tag in post request.")
        return JsonResponse(create_new_comment(request.user, post, data['text']))
        
    context = {
        'logged_user': get_object_or_404(CustomUser, username=request.user.username),
        'post': post,
        'likes': get_total_likes(post),
        'comments': CommentModel.objects.filter(post=post).order_by('post_date'),
    }
    template = 'posts/post_view.html' if is_ajax(request) else 'posts/main_view.html'
    return render(request, template, context=context)


@login_required
def post_likes(request, post_id):
    post = get_object_or_404(PostModel, id=post_id)
    if not post.published:
        raise Http404('Post not found.')
    
    if request.method == 'POST':
        response = {
            'post_id': post.id,
            'liked': like_dislike(post, request.user),
            'qty': get_total_likes(post),
        }
        return JsonResponse(response)

    context = {
        'profile_user': None,
        'user_list': [(u, request.user.is_following(u.id)) for u in post.likes.all()],
        'logged_user': request.user,
        'page_title': 'Curtidas',
        'search_url': reverse('posts:post-search', kwargs={'obj_id': post_id}),
    }

    return render(request, 'users/users_card.html', context=context)


@login_required
def comment_likes(request, obj_id):
    if request.method == 'POST':
        post = get_object_or_404(PostModel, id=obj_id)
        data = json.loads(request.body)
        if 'objID' not in data.keys():
            raise ValueError("Missing 'objID' tag in POST request.")
        comment = get_object_or_404(CommentModel, id=data['objID'])
        response = {
            'post_id': post.id,
            'comment_id': comment.id,
            'liked': like_dislike(comment, request.user),
            'qty': get_total_likes(comment),
        }
        return JsonResponse(response)
    
    comment = get_object_or_404(CommentModel, id=obj_id)
    context = {
        'profile_user': None,
        'user_list': [(u, request.user.is_following(u.id)) for u in comment.likes.all()],
        'logged_user': request.user,
        'page_title': 'Curtidas',
        'search_url': reverse('posts:comment-search', kwargs={'obj_id': obj_id}),
    }
    return render(request, 'users/users_card.html', context=context)


@login_required
def post_search(request, obj_id):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        response = {
            'user_list': search_user(
                substring=query,
                logged_user=request.user,
                search_in=POST_LIKES,
                identification=obj_id
            ),
            'profile_user': request.user.username,
            'show_bio': True,
            'show_relationship': True,
            'show_remove': False,
        }
        return JsonResponse(response) 
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes
    

@login_required
def comment_search(request, obj_id):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        response = {
            'user_list': search_user(
                substring=query,
                logged_user=request.user,
                search_in=COMMENT_LIKES,
                identification=obj_id
            ),
            'profile_user': request.user.username,
            'show_bio': True,
            'show_relationship': True,
            'show_remove': False,
        }
        return JsonResponse(response) 
    else:
        return HttpResponseBadRequest('Only GET requests are allowed.') # TODO: Testes