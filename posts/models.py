from django.db import models
from django.utils import timezone


from users.models import CustomUser


class PostModel(models.Model):

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='posts', default=None, null=False, blank=False)
    likes = models.ManyToManyField(to=CustomUser, related_name='likes', default=None, blank=True)
    img = models.ImageField(upload_to='images/%Y/%d', null=True, blank=True, default=None)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=True)


    def get_likes_total(self):
        """Return total number of likes of a post"""
        return self.likes.all().count()
    

    def check_if_user_liked(self, user):
        """Check if a given user liked or not the post"""
        return True if self.likes.filter(username=user.username) else False


    def __str__(self):
        return f'{str(self.user)} - post#{self.id} - {self.date}'
