from PIL import Image
from io import BytesIO

from django.test import TestCase
from posts.models import PostModel
from django.core.files.uploadedfile import SimpleUploadedFile


from users.models import CustomUser

def test_image():
    data = BytesIO()
    image = Image.new('RGB', (100, 100))
    image.save(data, format='png')
    return SimpleUploadedFile("test.jpg", data.getvalue())


class TestPostModel(TestCase):

    username = 'test_username'
    email = 'test_username@testemail.com'
    password = 'pass@123'

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username = self.username,
            email = self.email,
            password = self.password,
        )
        self.post = PostModel.objects.create(
            user = self.user,
            img = test_image(),
            description = f'Test Post #1',
            )


    def test_model_post_exists(self):
        """Test if the model exists and if has the setup user"""
        self.assertEqual(1, PostModel.objects.all().count())


    def test_model_has_str_representation(self):
        """Test if the model has str representation returning ..."""
        self.assertEqual(
            str(self.post),
            f'{str(self.user)} - post#{self.post.id} - {self.post.date}'
            )