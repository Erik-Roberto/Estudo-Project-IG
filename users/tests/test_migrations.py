from django.test import TestCase
from users.models import CustomUser


class TestUserModel(TestCase):


    def setUp(self):
        self.user = CustomUser.objects.create(
            first_name = 'test', 
            last_name = 'test',
            username = 'user',
            email = 'user@test.com',
            bio = 'Some cool bio...',
            )
        self.user2 = CustomUser.objects.create(username='user2', email='user2@test.com')


    def test_model_user_exists(self):
        """Test if the model exists and if has the setup user"""
        qtd_user = CustomUser.objects.count()
        self.assertEqual(self.user.username, 'user')
        self.assertEqual(qtd_user, 2)


    def test_model_has_str_representation(self):
        """Test if the model has str representation returning the username"""
        self.assertEqual(str(self.user), 'user')


    def test_model_user_is_not_following_other_user(self):
        """
        Test if the method returns false if is_following method is called
        for a user that not follow the other.
        """
        following = self.user.is_following(self.user2.id)
        self.assertFalse(following)

    
    def test_model_user_is_following_other_user(self):
        """
        Test if the method returns True if is_following method is called
        for a user that follows the other.
        """
        self.user.following.add(self.user2)
        self.user.save()
        following = self.user.is_following(self.user2.id)
        self.assertTrue(following)

    
    def test_model_user_following_relation_is_setup_to_asymmetric(self):
        """
        Test if the relation between users in following is setup to asymmetric
        """
        self.user.following.add(self.user2)
        self.user.save()
        following_user_to_user2 = self.user.is_following(self.user2.id)
        following_user2_to_user = self.user2.is_following(self.user.id)
        self.assertTrue(following_user_to_user2)
        self.assertFalse(following_user2_to_user)


    def test_model_return_false_for_invalid_id_in_is_following_method(self):
        """
        Test the behavior when a invalid id is passed to is_following method,
        false must be returned.
        """
        following = self.user.is_following(20)
        self.assertFalse(following)