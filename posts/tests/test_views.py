import json
from random import choice, randint


from django.test import TestCase
from django.urls import reverse

from posts.models import PostModel
from users.models import CustomUser
from comments.models import CommentModel
from factories import factories as f


class TestPostViews(TestCase):

    def setUp(self):
        self.user = f.create_test_user()
        self.posts = [f.create_test_post(user=self.user, desc=f'Test Post #{i}') for i in range(3)]
        

    def test_post_view_gets_right_post(self):
        """
        Test if the post view return the right post requested.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        response = self.client.get(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id})
            )
        self.assertEqual(test_post.id, response.context['post'].id)


    def test_post_view_uses_expected_template(self):
        """
        Test if post main view uses the correct template to render a response.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.get(
            reverse(
                'posts:main-view',
                kwargs={'post_id': choice(self.posts).id, 'user_id': self.user.id}
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/main_view.html')


    def test_post_view_blocked_unauthenticated_user(self):
        """
        Test if the post view redirects unauthenticated users to login page.
        """
        url = reverse('posts:main-view', kwargs={'post_id':self.posts[-1].id, 'user_id':self.user.id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users:login')+f'?next={url}')

    
    def test_post_view_raises_404_for_wrong_post_id(self):
        """
        Test 404 raise for wrong post id.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.get(
            reverse('posts:main-view', kwargs={'post_id':randint(10,20), 'user_id':self.user.id})
        )
        self.assertEqual(response.status_code, 404)


    def test_post_view_raises_404_unpublished_post(self):
        """
        Test 404 raise if a unpublished post url are accessed.
        """
        test_post = choice(self.posts)
        test_post.published = False
        test_post.save()
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.get(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id})
        )
        self.assertEqual(response.status_code, 404)


    def test_post_view_gets_likes_correctly(self):
        """
        Test post view passes correctly likes count to template.
        """
        generate_user = lambda i: CustomUser.objects.create_user(
            username=f'testuser{i}',
            email=f'testuser{i}@email.com',
            password=f'passworduser{i}',
        )
        test_post = choice(self.posts)
        users = [generate_user(i) for i in range(randint(3,10))]
        likes_count = len([test_post.likes.add(user) for user in users if choice([True, False])])
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.get(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id})
        )
        self.assertEqual(likes_count, response.context['likes'])


    def test_post_view_raises_404_incorrect_combination_user_post_url(self):
        """
        Test if the post view raises a 404 if the url requested contain wrong
        combination of user_id and post_id.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        # Correct post and non-existent user
        response = self.client.get(
            reverse(
                'posts:main-view',
                kwargs={'post_id': choice(self.posts).id, 'user_id': randint(10,100)}
                )
        )
        self.assertEqual(response.status_code, 404, msg='Post not found.')


    def test_post_view_like_post(self):
        """
        Test liking post feature.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        self.assertEqual(test_post.likes.count(), 0)
        response = self.client.post(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
            data=json.dumps({
                'button': f'button-post-{test_post.id}',
                'action': 'like-unlike',
                'object': 'post'
            }),
            content_type="application/json",
        )
        self.assertEqual(test_post.likes.count(), 1)
        self.assertTrue(response.json()['liked'])


    def test_post_view_unlike_post(self):
        """
        Test unliking post feature. 
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        test_post.likes.add(self.user)
        self.assertEqual(test_post.likes.count(), 1)
        response = self.client.post(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
            data=json.dumps({
                'button': f'button-post-{test_post.id}',
                'action': 'like-unlike',
                'object': 'post'
            }),
            content_type="application/json",
        )
        self.assertEqual(test_post.likes.count(), 0)
        self.assertFalse(response.json()['liked'])


    def test_post_view_like_unlike_missing_action_key(self):
        """
        Test if the post view raises expected error when the post data
        is missig the action key.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        with self.assertRaises(ValueError):
            response = self.client.post(
                reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
                data=json.dumps({
                    'button': f'button-post-{test_post.id}',
                    'object': 'post',
                }),
                content_type="application/json",
            )


    def test_post_view_invalid_action_key_raises_error(self):
        """
        Test if a invalid action key in post request raises a
        Value error.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        with self.assertRaises(ValueError):
            response = self.client.post(
                reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
                data=json.dumps({
                    'button': f'button-post-{test_post.id}',
                    'action': 'invalid key',
                    'object': 'post',
                }),
                content_type="application/json",
            )

    
    def test_post_view_missig_object_key_raises_error(self):
        """
        Test if a Value error is raised when the object key
        isn't passed.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        with self.assertRaises(ValueError):
            response = self.client.post(
                reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
                data=json.dumps({
                    'button': f'button-post-{test_post.id}',
                    'action': 'like-unlike',
                }),
                content_type="application/json",
            )


    def test_post_view_invalid_object_key_raises_error(self):
        """
        Test if a invalid object key in post request raises a
        Value error.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        with self.assertRaises(ValueError):
            response = self.client.post(
                reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
                data=json.dumps({
                    'button': f'button-post-{test_post.id}',
                    'action': 'like-unlike',
                    'object': 'invalid key',
                }),
                content_type="application/json",
            )


    def test_post_view_missing_text_key_raises_error(self):
        """
        Test if a Value error is raised when the text key
        isn't passed.
        """
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        test_post = choice(self.posts)
        with self.assertRaises(ValueError):
            response = self.client.post(
                reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
                data=json.dumps({
                    'button': f'button-comment-{test_post.id}',
                    'action': 'new-comment',
                    'object': 'comment',
                }),
                content_type="application/json",
            )


    def test_post_view_show_all_comments(self):
        """
        Test if the post view filter and return all the comments of
        the current post.
        """
        test_post = choice(self.posts)
        comments = [
            f.create_test_comment(self.user, test_post, f'Comment#{i}')
            for i in range(randint(1,5))
            ]
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.get(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id})
        )
        self.assertEqual(len(comments), len(response.context['comments']))


    def test_post_view_add_new_comment(self):
        """
        Test the functionality of comment in a post.
        """
        test_post = choice(self.posts)
        self.assertEqual(0, CommentModel.objects.filter(post=test_post).count())
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.post(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
            data=json.dumps({
                'action': 'new-comment',
                'text': 'Test comment',
            }),
            content_type="application/json",
        )
        self.assertEqual(1, CommentModel.objects.filter(post=test_post).count())


    def test_post_view_like_comment(self):
        """
        Test the functionality of like a comment.
        """
        test_post = choice(self.posts)
        comments = [
            f.create_test_comment(self.user, test_post, f'Comment#{i}')
            for i in range(randint(1,5))
            ]
        test_comment = choice(comments)
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        self.assertEqual(test_comment.likes.count(), 0)
        response = self.client.post(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
            data=json.dumps({
                'button': f'button-comment-{test_comment.id}',
                'action': 'like-unlike',
                'object': 'comment',
            }),
            content_type="application/json",
        )
        self.assertEqual(test_comment.likes.count(), 1)


    def test_post_view_unlike_comment(self):
        """
        Test the functionality of unlike a comment.
        """
        test_post = choice(self.posts)
        comments = [
            f.create_test_comment(self.user, test_post, f'Comment#{i}')
            for i in range(randint(1,5))
            ]
        test_comment = choice(comments)
        test_comment.likes.add(self.user)
        self.assertEqual(test_comment.likes.count(),1)
        logged_in = self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)
        self.assertTrue(logged_in)
        response = self.client.post(
            reverse('posts:main-view', kwargs={'post_id':test_post.id, 'user_id':self.user.id}),
            data=json.dumps({
                'button': f'button-comment-{test_comment.id}',
                'action': 'like-unlike',
                'object': 'comment',
            }),
            content_type="application/json",
        )
        self.assertEqual(test_comment.likes.count(), 0)