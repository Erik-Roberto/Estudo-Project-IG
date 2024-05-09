from PIL import Image
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):


    email = models.EmailField(unique=True, name='email')
    bio = models.TextField(max_length=600, default='', blank=True, name='bio')
    following = models.ManyToManyField(to='self', blank=True, symmetrical=False, default=None, related_name='followers')
    profile_picture = models.ImageField(upload_to='images/profiles/%Y/%d', default='images/profiles/default/default-user-icon.jpg')


    def __str__(self):
        return self.username
    

    def is_following(self, user_id):
        if self.following.filter(id=user_id).exists():
            return True
        else:
            return False
        

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        image = Image.open(self.profile_picture.path)
        image.save(self.profile_picture.path, 'JPEG', quality=40,optimize=True)