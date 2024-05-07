from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from posts.models import PostModel
from users.models import CustomUser

# Create your views here.


@login_required
def home(request):
    if request.method == 'POST':
        return HttpResponse('Sorry. :(') # TODO: Implementar post
    logged_user = get_object_or_404(CustomUser, username=request.user)
    following_users = logged_user.following.all()
    posts = PostModel.objects.filter(user__in=following_users).values()
    for post in posts:
        current_post = PostModel.objects.get(id=post['id'])
        post['user'] = CustomUser.objects.get(id=post['user_id'])
        post['liked_by_logged_user'] = current_post.check_if_user_liked(logged_user)
        post['total_likes'] = current_post.get_likes_total()
        post['total_comments'] = current_post.get_comments_total()

    return render(request, "home/index.html", {"posts":posts, "logged_user":logged_user})