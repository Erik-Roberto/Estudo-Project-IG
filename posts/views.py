import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import PostModel
from users.models import CustomUser
from comments.models import CommentModel

from helpers.posts import like_unlike, create_new_coment

@login_required
def main_view(request, post_id):
    post = get_object_or_404(PostModel, id=post_id)
    logged_user = get_object_or_404(CustomUser, username=request.user)
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
        
    comments = CommentModel.objects.filter(post=post).order_by('post_date').values()
    for comment in comments:
        current_comment = CommentModel.objects.get(id=comment['id'])
        comment['user'] = CustomUser.objects.get(id=comment['user_id'])
        comment['liked_by_logged_user'] = current_comment.check_if_user_liked(logged_user)
        comment['total_likes'] = current_comment.get_likes_total()

    context = {
        'logged_user': get_object_or_404(CustomUser, username=request.user),
        'post': post,
        'likes': post.likes.count(),
        'comments': comments,
    }

    return render(request, 'posts/main_view.html', context=context)


