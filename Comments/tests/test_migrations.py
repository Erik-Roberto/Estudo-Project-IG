from django.test import TestCase


from comments.models import CommentModel
from factories import factories as f


class TestCommentModel(TestCase):

    def setUp(self):
        self.user = f.create_test_user()
        self.post = f.create_test_post(user=self.user)
        self.comment = f.create_test_comment(user=self.user, post=self.post)


    def test_comment_model_exists(self):
        """
        Test if the model exists and has setup post.
        """
        self.assertEqual(1, CommentModel.objects.all().count())


    def test_comment_model_has_str_representation(self):
        """
        Test if the comments model has the __str__ method.
        """
        self.assertEqual(str(self.comment), f'{str(self.comment.user)}-{str(self.comment.post)}')
