from django import template


from users.models import CustomUser

register = template.Library()


# Template tags

@register.simple_tag
def is_following(username, user_id):
    return CustomUser.objects.get(username=username).is_following(user_id=user_id)

