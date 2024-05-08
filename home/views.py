from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from posts.models import PostModel
from users.models import CustomUser

from helpers.posts import get_total_likes, check_user_like

# Create your views here.


@login_required
def home(request):
    if request.method == 'POST':
        return HttpResponse('Sorry. :(') # TODO: Implementar post
    logged_user = get_object_or_404(CustomUser, username=request.user)
    following_users = logged_user.following.all()
    posts = PostModel.objects.filter(user__in=following_users)
    return render(request, "home/index.html", {"posts":posts, "logged_user":logged_user})