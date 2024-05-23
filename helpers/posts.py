from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404

from posts.models import PostModel, CommentModel
from users.models import CustomUser


def like_dislike(obj: CommentModel | PostModel, user: CustomUser) -> bool:
    if obj.likes.filter(id=user.id).exists():
        obj.likes.remove(user)
        return False
    obj.likes.add(user)
    return True


def create_new_comment(user: CustomUser, post: PostModel, text: str) -> dict:
    
    new_comment = CommentModel.objects.create(
        user = user,
        post = post,
        text = text,
    )
    new_comment.save()
    # TODO: Melhorar esse loop - Talvez tenha maneira melhor de adicionar essas informações sem ter que
    #       pegar obj do comentário dnv 
    comments = list(CommentModel.objects.filter(post=post).order_by('-fixed', 'post_date').values())
    for comment in comments:
            comment_obj = get_object_or_404(CommentModel, id=comment['id'])
            comment['liked'] = check_user_like(comment_obj, user.username)
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