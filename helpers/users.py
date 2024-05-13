import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpRequest

from users.models import CustomUser


def follow_or_unfollow_user(request: HttpRequest, page_user: str) -> JsonResponse:
    """Responsible to make logged user follow or unfollow target user."""
    data = json.loads(request.body)
    if not 'action' in data.keys():
        raise ValueError("Missing 'follow-unfollow' tag in post request.")
    if not 'username' in data.keys(): # TODO: teste para essa linha
        raise ValueError("Missing 'username' key in post request.")
    
    target_username = data['username']
    logged_user = get_object_or_404(CustomUser, username=request.user)
    target_user = get_object_or_404(CustomUser, username=target_username)
    page_user = get_object_or_404(CustomUser, username=page_user)    
    if data['action'] == 'follow-unfollow': # TODO: teste para essa linha
        if logged_user.is_following(target_user.id):
            # Unfollowing target user
            logged_user.following.remove(target_user)
        else:
            # Following target user
            logged_user.following.add(target_user)
        logged_user.save()
        return JsonResponse({
            'is_following': logged_user.is_following(target_user.id),
            'username': target_username,
            'followers': get_total_followers(page_user), # TODO: teste para essa linha
            'following': get_total_following(page_user), # TODO: teste para essa linha
        })
    
    elif data['action'] == 'remove-follower': # TODO: teste para essa linha
        if target_user.is_following(logged_user.id):
            target_user.following.remove(logged_user)
        return JsonResponse({
            'is_following': False,
            'username': logged_user.username,
            'followers': get_total_followers(page_user), # TODO: teste para essa linha
            'following': get_total_following(page_user), # TODO: teste para essa linha
        })
    
    else:
        raise ValueError(f"Invalid 'action' key, expected 'remove-follower' or 'follow-unfollow', but {data['action']} was passed.")


def get_total_following(user: CustomUser) -> int:
    return user.following.all().count()


def get_total_followers(user: CustomUser) -> int:
    return CustomUser.objects.filter(following=user).count()