
from django.test import TestCase
from posts.models import PostModel


from users.models import CustomUser
from factories import factories as f

class TestPostModel(TestCase):

    def setUp(self):
        self.user = f.create_test_user(
            username = f.STD_TEST_USERNAME,
            email = f.STD_TEST_EMAIL,
            password = f.STD_TEST_PASSWORD,
        )
        self.post = f.create_test_post(user=self.user)


    def test_model_post_exists(self):
        """Test if the model exists and if has the setup post"""
        self.assertEqual(1, PostModel.objects.all().count())


    def test_model_has_str_representation(self):
        """Test if the model has str representation returning ..."""
        self.assertEqual(
            str(self.post),
            f'{str(self.user)} - post#{self.post.id} - {self.post.date}'
            )