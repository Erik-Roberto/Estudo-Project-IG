from django.db import models
from django.utils import timezone


from users.models import CustomUser


class PostModel(models.Model):

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='posts', default=None, null=True, blank=True)
    likes = models.ManyToManyField(to=CustomUser, related_name='likes', default=None, blank=True)
    img = models.ImageField(upload_to='images/%Y/%d', null=True, blank=True, default=None)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=True)


    def __str__(self):
        return f'{str(self.user)} - post#{self.id} - {self.date}'
