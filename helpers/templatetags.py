from django import template

from .posts import get_total_likes, check_user_like, get_total_comments


register = template.Library()


register.filter('get_total_likes', get_total_likes)
register.filter('get_total_comments', get_total_comments)
register.filter('check_user_like', check_user_like)
