import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import PostModel
from users.models import CustomUser
from comments.models import CommentModel


@login_required
def main_view(request, user_id, post_id):
    post = get_object_or_404(PostModel, id=post_id)
    if user_id != post.user.id:
        raise Http404('Post not found.')
    if not post.published:
        raise Http404('Post not found.')
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'action' not in data.keys():
            raise ValueError("Missing action tag in post request.")
        if data['action'] == 'like-unlike':
            return like_unlike(request, post, data)
        elif data['action'] == 'new-comment':
            return create_new_coment(request, post, data)
        else:
            raise ValueError("Invalid 'action' tag in post request.")
    context = {
        'post': post,
        'likes': post.likes.count(),
        'comments': CommentModel.objects.filter(post=post).order_by('post_date'),
    }

    return render(request, 'posts/main_view.html', context=context)


def like_unlike(request, post, data):
    if 'object' not in data.keys():
        raise ValueError("Missing 'object' tag in post request.")
    if data['object'] == 'post':
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return JsonResponse({'post_id': post.id, 'liked': post.likes.filter(id=request.user.id).exists()})
    elif data['object'] == 'comment':
        comment = get_object_or_404(CommentModel, id=int(data['button'][15:])) #TODO: Melhorar método de extração do id
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
        return JsonResponse({'comment_id': comment.id, 'liked': comment.likes.filter(id=request.user.id).exists()})
    else:
        raise ValueError("Invalid 'object' tag in post request.")


def create_new_coment(request, post, data):
    if 'text' not in data.keys():
        raise ValueError("Missing 'text' tag in post request.")
    new_comment = CommentModel.objects.create(
        user = request.user,
        post = post,
        text = data['text'],
    )
    new_comment.save()
    data = {
        'comments': list(CommentModel.objects.filter(post=post).order_by('-fixed', 'post_date').values())
    }
    return JsonResponse(data)
