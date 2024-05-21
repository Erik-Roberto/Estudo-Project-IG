from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpRequest, HttpResponseNotAllowed
from django.urls import reverse

from users.models import CustomUser
from posts.models import PostModel, CommentModel


# Definindo constantes
ALL_USERS = 'all_users'
FOLLOWING = 'following'
FOLLOWERS = 'followers'
POST_LIKES = 'post_likes'
COMMENT_LIKES = 'comment_likes'

SEARCH_OPTIONS = (ALL_USERS, FOLLOWING, FOLLOWERS, POST_LIKES, COMMENT_LIKES)


def follow_or_unfollow_user(data: dict, logged_user: CustomUser, page_user: CustomUser=None) -> JsonResponse:
    """Responsible to make logged user follow or unfollow target user."""
    if not 'target' in data.keys(): # TODO: teste para essa linha
        raise ValueError("Missing 'target' key in post request.")
    target_user = get_object_or_404(CustomUser, username=data['target'])
    page_user = page_user if page_user else target_user

    if logged_user.is_following(target_user.id):
        logged_user.following.remove(target_user)
    else:
        logged_user.following.add(target_user)

    return JsonResponse({
        'is_following': logged_user.is_following(target_user.id),
        'followers': get_total_followers(page_user), # TODO: teste para essa linha
        'following': get_total_following(page_user), # TODO: teste para essa linha
    })



def remove_follower(data: dict, logged_user: CustomUser, page_user: str):
    target_user = get_object_or_404(CustomUser, username=data['target'])
    page_user = get_object_or_404(CustomUser, username=page_user)
    
    if target_user.is_following(logged_user.id):
        target_user.following.remove(logged_user)

    return JsonResponse({
        'is_following': logged_user.is_following(target_user.id),
        'followers': get_total_followers(page_user), # TODO: teste para essa linha
        'following': get_total_following(page_user), # TODO: teste para essa linha
    })


def search_user(substring: str, logged_user: CustomUser, search_in: str = ALL_USERS, identification: int | str = None) -> list[dict] | None:

    if search_in not in SEARCH_OPTIONS:
        raise ValueError('Invalid search_in value.')


    if search_in == ALL_USERS:
        user_list = CustomUser.objects.filter(username__contains=substring)
        if not substring: # Para substring = ''
            return
    elif search_in == FOLLOWERS and identification:
        user_list = CustomUser.objects.filter(following__username=identification, username__contains=substring)
    elif search_in == FOLLOWING and identification:
        user = get_object_or_404(CustomUser, username=identification)
        user_list = user.following.filter(username__contains=substring)
    elif search_in == POST_LIKES and identification:
        post = get_object_or_404(PostModel, id=identification)
        user_list = post.likes.filter(username__contains=substring)
    elif search_in == COMMENT_LIKES and identification:
        comment = get_object_or_404(CommentModel, id=identification)
        user_list = comment.likes.filter(username__contains=substring)
    else:
        raise ValueError('Invalid search in argument or missing obj_id.')
    

    return  [{
        'username': u.username,
        'is_following': logged_user.is_following(user_id=u.id),
        'user_pic': u.profile_picture.url,
        'bio': u.bio,
        'profile_url': reverse('users:profile', kwargs={'username': u.username}),
        } for u in user_list]


def get_total_following(user: CustomUser) -> int:
    return user.following.all().count()


def get_total_followers(user: CustomUser) -> int:
    return CustomUser.objects.filter(following=user).count()