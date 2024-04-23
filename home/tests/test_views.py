from django.test import TestCase
from django.urls import reverse

from posts.models import PostModel
from factories import factories as f



class TestHomeView(TestCase):

    USERS_QTY = 5
    POSTS_QTY = 5
    COMMENTS_QTY = 5
    MAX_POSTS_SHOW = 25


    def setUp(self):
        self.user = f.create_test_user()
        self.users = [f.create_test_user(username=f'testuser{i}') for i in range(self.USERS_QTY)]
        self.posts = []
        for user in self.users:
            self.posts += [
                f.create_test_post(user=user, desc=f'{user.username} testpost#{i}')
                for i in range(self.POSTS_QTY)
            ]
        self.comments = []
        for post in self.posts:
            self.comments += [
                f.create_test_comment(user=post.user, post=post, text=f'Comment#{i}')
                for i in range(self.COMMENTS_QTY)
            ]


    def test_home_view_blocked_for_unauthenticated_user(self):
        """
        Test if the home view is blocked for unauthenticated users.
        """
        response = self.client.get(reverse('users:home:home'), follow=True)
        self.assertRedirects(response, f'{reverse('users:login')}?next=/')


    def test_home_view_show_posts(self):
        """
        Test whether posts are being passed to template. 
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        for user in self.users:
            self.user.following.add(user)
        response = self.client.get(reverse('users:home:home'))
        posts_count = len(response.context['posts'])
        self.assertEqual(posts_count, self.MAX_POSTS_SHOW)
