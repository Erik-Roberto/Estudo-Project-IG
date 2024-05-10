from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from comments.models import CommentModel
from posts.models import PostModel
from users.models import CustomUser


def like_unlike(request: HttpRequest, post: PostModel, data: dict) -> dict:
    if 'object' not in data.keys():
        raise ValueError("Missing 'object' tag in post request.")
    if 'objID' not in data.keys():
        raise ValueError("Missing 'objID' tag in post request.")
    if data['object'] == 'post':
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return {'post_id': post.id, 'liked': check_user_like(post, request.user.username), 'qty': get_total_likes(post)}
    elif data['object'] == 'comment':
        comment = get_object_or_404(CommentModel, id=int(data['objID']))
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
        return {'comment_id': comment.id, 'liked': check_user_like(comment, request.user.username), 'qty': get_total_likes(comment)}
    else:
        raise ValueError("Invalid 'object' tag in post request.")


def create_new_coment(request: HttpRequest, post: PostModel, data: dict) -> dict:
    if 'text' not in data.keys():
        raise ValueError("Missing 'text' tag in post request.")
    new_comment = CommentModel.objects.create(
        user = request.user,
        post = post,
        text = data['text'],
    )
    new_comment.save()
    # TODO: Melhorar esse loop - Talvez tenha maneira melhor de adicionar essas informações sem ter que
    #       pegar obj do comentário dnv 
    comments = list(CommentModel.objects.filter(post=post).order_by('-fixed', 'post_date').values())
    for comment in comments:
            comment_obj = get_object_or_404(CommentModel, id=comment['id'])
            comment['liked'] = check_user_like(comment_obj, request.user.username)
            comment['likes_qty'] = get_total_likes(comment_obj)
            comment['username'] = comment_obj.user.username
            comment['user_pic'] = comment_obj.user.profile_picture.url

    return {'comments': comments}


def get_total_likes(obj: PostModel | CommentModel) -> int:
    return obj.likes.all().count()


def get_total_comments(obj: PostModel) -> int:
    return obj.comment.all().count()


def check_user_like(obj: PostModel | CommentModel, username: str) -> bool:
    return True if obj.likes.filter(username=username) else False


def is_ajax(request: HttpRequest) -> bool:
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'