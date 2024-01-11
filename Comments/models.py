from django.db import models
from django.utils import timezone

from users.models import CustomUser
from posts.models import PostModel
# Create your models here.

class CommentModel(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='owner', blank=False, null=False)
    post = models.ForeignKey(to=PostModel, on_delete=models.CASCADE, related_name='post', blank=False, null=False)
    text = models.TextField()
    likes = models.ManyToManyField(to=CustomUser, symmetrical=False, related_name='comment_likes', default=None, blank=True)
    fixed = models.BooleanField(default=False)
    post_date = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['-fixed', 'post_date']


    def __str__(self):
        return f'{str(self.user)}-{str(self.post)}'