import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from users.models import CustomUser


def follow_or_unfollow_user(request, target_user_username:str = None) -> JsonResponse:
    """Responsible to make logged user follow or unfollow target user."""
    data = json.loads(request.body)
    if not 'follow-unfollow' in data.values():
        raise ValueError("Missing 'follow-unfollow' tag in post request.")
    if not target_user_username:
        target_user_username = data['username']
    logged_user = get_object_or_404(CustomUser, username=request.user)
    target_user = get_object_or_404(CustomUser, username=target_user_username)
    if logged_user.following.filter(id=target_user.id).exists():
        # Unfollowing target user
        logged_user.following.remove(target_user)
    else:
        # Following target user
        logged_user.following.add(target_user)
    logged_user.save()
    return JsonResponse({'is_following': logged_user.is_following(target_user.id), 'username': target_user_username})