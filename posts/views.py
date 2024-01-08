import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import PostModel
from users.models import CustomUser

@login_required
def main_view(request, user_id, post_id):
    post = get_object_or_404(PostModel, id=post_id)
    if user_id != post.user.id:
        raise Http404('Post not found.')
    if not post.published:
        raise Http404('Post not found.')
    if request.method == 'POST':
        return like_unlike(request, post, get_object_or_404(CustomUser, id=user_id))
    likes = post.likes.count()
    return render(request, 'posts/main_view.html', context={'post': post, 'likes':likes})


def like_unlike(request, post, user):
    data = json.loads(request.body)
    if not 'like-unlike' in data.values():
        raise ValueError("Missing 'like-unlike' tag in post request.")
    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return JsonResponse({'post_id': post.id, 'liked':post.likes.filter(id=user.id).exists()})