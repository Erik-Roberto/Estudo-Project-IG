import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import PostModel
from users.models import CustomUser
from comments.models import CommentModel

from helpers.posts import like_unlike, create_new_coment, is_ajax

@login_required
def main_view(request, post_id):
    post = get_object_or_404(PostModel, id=post_id)
    if not post.published:
        raise Http404('Post not found.')
    
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'action' not in data.keys():
            raise ValueError("Missing action tag in post request.")
        if data['action'] == 'like-unlike':
            return JsonResponse(like_unlike(request, post, data))
        elif data['action'] == 'new-comment':
            return JsonResponse(create_new_coment(request, post, data))
        else:
            raise ValueError("Invalid 'action' tag in post request.")
        
    context = {
        'logged_user': get_object_or_404(CustomUser, username=request.user.username),
        'post': post,
        'likes': post.likes.count(),
        'comments': CommentModel.objects.filter(post=post).order_by('post_date'),
    }
    template = 'posts/post_view.html' if is_ajax(request) else 'posts/main_view.html'
    return render(request, template, context=context)


@login_required
def post_likes(request, post_id): # TODO: Testes para essa view 
    post = get_object_or_404(PostModel, id=post_id)
    logged_user = request.user
    if not post.published:
        raise Http404('Post not found.')
    
    data = json.loads(request.body)
    if data['object'] == 'comment':
        user_list = post.comment.get(id=data['objID']).likes.all()
    elif data['object'] == 'post':
        user_list = post.likes.all()
    else:
        raise ValueError(f"Invalid tag 'object', expected 'comment' or 'post', but {data['object']} was passed.")   
    user_list = [(user, logged_user.is_following(user.id)) for user in user_list]
    return render(request, 'users/users_card.html', {
                        'profile_user': None,
                        'user_list': user_list,
                        'logged_user': get_object_or_404(CustomUser, username=request.user.username),
                        'page_title': 'Curtidas',
                    })