import json

from django.test import TestCase
from django.urls import reverse

from posts.models import PostModel, CommentModel
from users.models import CustomUser

from factories import factories as f
from helpers.posts import get_total_likes, get_total_comments


class PostViewsBase(TestCase):

    def setUp(self):
        self.user = f.create_test_user()
        self.posts = [f.create_test_post(user=self.user, desc=f'Test Post #{i}') for i in range(3)]
        self.client.login(username=f.STD_TEST_USERNAME, password=f.STD_TEST_PASSWORD)


class PostViewTest(PostViewsBase):

    def test_post_view_gets_right_post(self):
        """
        Test if the post view return the right post requested.
        """
        test_post = self.posts[0]
        response = self.client.get(
            reverse('posts:post', kwargs={'post_id':test_post.id})
            )
        self.assertEqual(test_post.id, response.context['post'].id)


    def test_post_view_uses_expected_template(self):
        """
        Test if post main view uses the correct template to render a response.
        """
        response = self.client.get(
            reverse(
                'posts:post',
                kwargs={'post_id': self.posts[0].id}
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/main_view.html')


    def test_post_view_blocked_unauthenticated_user(self):
        """
        Test if the post view redirects unauthenticated users to login page.
        """
        logged_out = self.client.logout()
        url = reverse('posts:post', kwargs={'post_id':self.posts[-1].id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users:login')+f'?next={url}')

    
    def test_post_view_raises_404_for_invalid_post_id(self):
        """
        Test 404 raise for wrong post id.
        """
        invalid_id = 15
        response = self.client.get(
            reverse('posts:post', kwargs={'post_id': invalid_id})
        )
        self.assertEqual(response.status_code, 404)


    def test_post_view_raises_404_unpublished_post(self):
        """
        Test 404 raise if a unpublished post url are accessed.
        """
        test_post = self.posts[0]
        test_post.published = False
        test_post.save()
        response = self.client.get(
            reverse('posts:post', kwargs={'post_id':test_post.id})
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
        test_post = self.posts[0]
        users = [generate_user(i) for i in range(5)]
        likes_count = len([test_post.likes.add(user) for user in users])
        response = self.client.get(
            reverse('posts:post', kwargs={'post_id':test_post.id})
        )
        self.assertEqual(likes_count, response.context['likes'])


    def test_post_view_show_all_comments(self):
        """
        Test if the post view filter and return all the comments of
        the current post.
        """
        test_post = self.posts[0]
        comments = [
            f.create_test_comment(self.user, test_post, f'Comment#{i}')
            for i in range(5)
            ]
        response = self.client.get(reverse('posts:post', kwargs={'post_id':test_post.id}))
        self.assertEqual(len(comments), len(response.context['comments']))


    def test_post_view_add_new_comment(self):
        """
        Test the functionality of comment in a post.
        """
        test_post = self.posts[0]
        self.assertEqual(0, get_total_comments(test_post))
        response = self.client.post(
            reverse('posts:post', kwargs={'post_id':test_post.id}),
            data=json.dumps({'text': 'Test comment'}),
            content_type="application/json",
        )
        self.assertEqual(1, get_total_comments(test_post))


    def test_post_view_raise_error_if_missing_tag(self):
        """
        Test if the post view raises a ValueError when the tag 'text' isn't passed in 
        post request.
        """
        test_post = self.posts[0]
        with self.assertRaises(ValueError, msg="Missing 'text' tag in post request."):
            response = self.client.post(
                reverse('posts:post', kwargs={'post_id':test_post.id}),
                data=json.dumps({'invalid_tag': 'invalid tag'}),
                content_type="application/json",
            )


class PostLikesViewTest(PostViewsBase):

    def test_like_post_view_for_like(self):
        """
        Test liking post feature.
        """
        test_post = self.posts[0]
        self.assertEqual(get_total_likes(test_post), 0)
        response = self.client.post(reverse('posts:likes', kwargs={'post_id':test_post.id}))
        self.assertEqual(get_total_likes(test_post), 1)
        self.assertTrue(response.json()['liked'])


    def test_like_post_view_for_dislike(self):
        """
        Test disliking post feature. 
        """
        test_post = self.posts[0]
        test_post.likes.add(self.user)
        self.assertEqual(get_total_likes(test_post), 1)
        response = self.client.post(reverse('posts:likes', kwargs={'post_id':test_post.id}))
        self.assertEqual(get_total_likes(test_post), 0)
        self.assertFalse(response.json()['liked'])


    def test_like_post_view_raises_404_for_unpublished_post(self):
        """
        Test 404 raise if a unpublished like_post url are accessed.
        """
        test_post = self.posts[0]
        test_post.published = False
        test_post.save()
        response = self.client.get(
            reverse('posts:likes', kwargs={'post_id':test_post.id})
        )
        self.assertEqual(response.status_code, 404)


    def test_like_post_view_blocked_unauthenticated_user(self):
        """
        Test if the like_post view redirects unauthenticated users to login page.
        """
        logged_out = self.client.logout()
        url = reverse('posts:likes', kwargs={'post_id':self.posts[-1].id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users:login')+f'?next={url}')


    def test_like_post_view_return_correct_info_for_post_request(self):
        """
        Test if the like_post view returns correct post id and likes qty in JsonResponse.
        """
        test_post = self.posts[0]
        response = self.client.post(
            reverse('posts:likes', kwargs={'post_id':test_post.id})
        )
        self.assertEqual(response.json()['post_id'], test_post.id)
        self.assertEqual(response.json()['qty'], get_total_likes(test_post))


    def test_like_post_view_return_profile_user_as_none_for_get_request(self):
        """
        Test if the like_post view returns 'None' as the 'profile_user' when a GET request is made.
        """
        test_post = self.posts[0]
        response = self.client.get(reverse('posts:likes', kwargs={'post_id': test_post.id}))
        self.assertEqual(None, response.context['profile_user'])


    def test_like_post_view_return_correct_user_list_for_get_request(self):
        """
        Test if the like_post view returns correct 'user_list' when a GET request is made.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_users = []
        for _ in range(qty_test_users):
            user = f.create_test_user()
            test_post.likes.add(user)
            test_users.append(user)
        response = self.client.get(reverse('posts:likes', kwargs={'post_id': test_post.id}))
        self.assertEqual(len(test_users), len(response.context['user_list']))

        response_ids = [u[0].id for u in response.context['user_list']]
        for u in test_users:
            self.assertIn(u.id, response_ids)
    
    
    def test_like_post_view_return_correct_page_title_for_get_request(self):
        """
        Test if the like_post view returns correct 'page_title' when a GET request is made.
        """
        test_post = self.posts[0]
        response = self.client.get(reverse('posts:likes', kwargs={'post_id': test_post.id}))
        self.assertEqual('Curtidas', response.context['page_title'])
    
    
    def test_like_post_view_return_correct_search_url_for_get_request(self):
        """
        Test if the like_post view returns correct 'search_url' when a GET request is made.
        """
        test_post = self.posts[0]
        response = self.client.get(reverse('posts:likes', kwargs={'post_id': test_post.id}))
        self.assertEqual(
            reverse('posts:post-search', kwargs={'obj_id': test_post.id}),
            response.context['search_url']
        )


class CommentLikesViewTest(PostViewsBase):

    def test_comment_like_view_like_comment(self):
        """
        Test the functionality of like a comment.
        """
        test_post = self.posts[0]
        comments = [
            f.create_test_comment(self.user, test_post, f'Comment#{i}')
            for i in range(5)
            ]
        test_comment = comments[0]
        self.assertEqual(get_total_likes(test_comment), 0)
        response = self.client.post(
            reverse('posts:comments', kwargs={'obj_id':test_post.id}),
            data=json.dumps({'objID': test_comment.id}),
            content_type="application/json",
        )
        self.assertEqual(get_total_likes(test_comment), 1)


    def test_comment_like_view_dislike_comment(self):
        """
        Test the functionality of dislike a comment.
        """
        test_post = self.posts[0]
        comments = [
            f.create_test_comment(self.user, test_post, f'Comment#{i}')
            for i in range(5)
            ]
        test_comment = comments[0]
        test_comment.likes.add(self.user)
        self.assertEqual(get_total_likes(test_comment),1)
        response = self.client.post(
            reverse('posts:comments', kwargs={'obj_id':test_post.id}),
            data=json.dumps({'objID': test_comment.id}),
            content_type="application/json",
        )
        self.assertEqual(get_total_likes(test_comment), 0)

    
    def test_comment_likes_view_raise_error_if_missing_tag(self):
        """
        Test if the post view raises a ValueError when the tag 'objID' isn't passed in 
        post request.
        """
        test_post = self.posts[0]
        with self.assertRaises(ValueError, msg="Missing 'objID' tag in POST request."):
            response = self.client.post(
                reverse('posts:comments', kwargs={'obj_id': test_post.id}),
                data=json.dumps({'invalid_tag':'invalid_tag'}),
                content_type="application/json",
            )


    def test_comment_likes_view_blocked_unauthenticated_user(self):
        """
        Test if the comment_likes view redirects unauthenticated users to login page.
        """
        logged_out = self.client.logout()
        url = reverse('posts:comments', kwargs={'obj_id':self.posts[-1].id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users:login')+f'?next={url}')


    def test_comment_likes_view_return_correct_info_for_post_request(self):
        """
        Test if the comment_likes view returns correct post id and likes qty in JsonResponse.
        """
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
            text='Test comment',
        )
        response = self.client.post(
            reverse('posts:comments', kwargs={'obj_id': test_post.id}),
            data=json.dumps({'objID': test_comment.id}),
            content_type="application/json",
        )
        self.assertEqual(test_post.id, response.json()['post_id'])
        self.assertEqual(get_total_likes(test_comment), response.json()['qty'])


    def test_comment_likes_view_return_profile_user_as_none_for_get_request(self):
        """
        Test if the comment_likes view returns 'None' as the 'profile_user' when a GET request is made.
        """
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
            text='Test comment',
        )
        response = self.client.get(reverse('posts:comments', kwargs={'obj_id': test_comment.id}))
        self.assertEqual(None, response.context['profile_user'])


    def test_comment_likes_view_return_correct_user_list_for_get_request(self):
        """
        Test if the comment_likes view returns correct 'user_list' when a GET request is made.
        """
        qty_test_user = 5
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
            text='Test comment',
        )
        test_users = []
        for _ in range(qty_test_user):
            user = f.create_test_user()
            test_comment.likes.add(user)
            test_users.append(user)

        response = self.client.get(reverse('posts:comments', kwargs={'obj_id': test_comment.id}))
        self.assertEqual(len(test_users), len(response.context['user_list']))
        
        response_ids = [u[0].id for u in response.context['user_list']]
        for u in test_users:
            self.assertIn(u.id, response_ids)

    
    def test_comment_likes_view_return_correct_page_title_for_get_request(self):
        """
        Test if the comment_likes view returns correct 'page_title' when a GET request is made.
        """
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
            text='Test comment',
        )
        response = self.client.get(reverse('posts:comments', kwargs={'obj_id': test_comment.id}))
        self.assertEqual('Curtidas', response.context['page_title'])
    
    
    def test_comment_likes_view_return_correct_search_url_for_get_request(self):
        """
        Test if the comment_likes view returns correct 'search_url' when a GET request is made.
        """
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
            text='Test comment',
        )
        
        response = self.client.get(reverse('posts:comments', kwargs={'obj_id': test_comment.id}))
        self.assertEqual(
            reverse('posts:comment-search', kwargs={'obj_id': test_comment.id}),
            response.context['search_url'],
        )


class PostSearchViewTest(PostViewsBase):

    def test_post_search_view_blocked_for_unauthenticated_user(self):
        """
        Test if the post_search view redirects unauthenticated users to login page.
        """
        logged_out = self.client.logout()
        url = reverse('posts:post-search', kwargs={'obj_id':self.posts[-1].id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users:login')+f'?next={url}')
        

    def test_post_search_view_raise_bad_request_for_post_request(self):
        """
        Test if the post_search view returns a HttpResponseBadRequest if a POST request is made.
        """
        test_post = self.posts[0]
        response = self.client.post(reverse('posts:post-search', kwargs={'obj_id': test_post.id}))
        self.assertEqual(response.status_code, 400)


    def test_post_search_view_raises_not_found_for_invalid_obj_id(self):
        """
        Test if the post_search view returns Http404 if a invalid 'obj_id' is passed.
        """
        invalid_id = 100
        url = reverse('posts:post-search', kwargs={'obj_id': invalid_id})
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(404, response.status_code)


    def test_post_search_view_returns_correct_user_list_if_query_exists(self):
        """
        Test if the post_search view returns correct 'user_list' if the query match users.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_users = []
        for i in range(qty_test_users):
            user = f.create_test_user(
                username=f'testuser{i}',
                email=f'testuser{i}#email.com',
                password=f'testuser{i}password'
            )
            test_post.likes.add(user)
            test_users.append(user)
        url = reverse('posts:post-search', kwargs={'obj_id': test_post.id})
        response = self.client.get(url, {'q': test_users[0].username})
        self.assertEqual(test_users[0].username, response.json()['user_list'][0]['username'])
        
        response = self.client.get(url, {'q': '2'})
        self.assertEqual(test_users[2].username, response.json()['user_list'][0]['username'])

        response = [u['username'] for u in self.client.get(url, {'q': 'user'}).json()['user_list']]
        for u in test_users:
            self.assertIn(u.username, response)


    def test_post_search_view_returns_all_users_if_query_is_empty(self):
        """
        Test if the post_search view returns all users present in post likes if the query is empty.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_users = []
        for _ in range(qty_test_users):
            user = f.create_test_user()
            test_post.likes.add(user)
            test_users.append(user)
        url = reverse('posts:post-search', kwargs={'obj_id': test_post.id})
        response = [u['username'] for u in self.client.get(url, {'q': ''}).json()['user_list']]
        self.assertEqual(len(test_users), len(response))
        for u in test_users:
            self.assertIn(u.username, response)
    

    def test_post_search_view_returns_all_users_if_no_query_is_passed(self):
        """
        Test if the post_search view returns all users present in post likes if no query is passed.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_users = []
        for _ in range(qty_test_users):
            user = f.create_test_user()
            test_post.likes.add(user)
            test_users.append(user)
        url = reverse('posts:post-search', kwargs={'obj_id': test_post.id})
        response = [u['username'] for u in self.client.get(url).json()['user_list']]
        self.assertEqual(len(test_users), len(response))
        for u in test_users:
            self.assertIn(u.username, response)


    def test_post_search_view_returns_no_users_if_no_user_matches_query(self):
        """
        Test if the post_search view returns no users if no user matches the query.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_users = []
        for _ in range(qty_test_users):
            user = f.create_test_user()
            test_post.likes.add(user)
            test_users.append(user)
        url = reverse('posts:post-search', kwargs={'obj_id': test_post.id})
        response = self.client.get(url, {'q': 'NoMatch'}).json()
        self.assertEqual(0, len(response['user_list']))
        

    def test_post_search_view_returns_correct_parameters(self):
        """
        Test if the post_search view returns the correct values for the parameters 'show_bio',
        'show_relationship', 'show_remove' and 'profile_user'.
        """
        test_post = self.posts[0]
        url = reverse('posts:post-search', kwargs={'obj_id': test_post.id})
        response = self.client.get(url, {'q': 'NoMatch'}).json()
        self.assertTrue(response['show_bio'])
        self.assertTrue(response['show_relationship'])
        self.assertFalse(response['show_remove'])
        self.assertEqual(self.user.username, response['profile_user'])


class CommentSearchViewTest(PostViewsBase):

    def test_comment_search_view_blocked_for_unauthenticated_user(self):
        """
        Test if the comment_search view redirects unauthenticated users to login page.
        """
        logged_out = self.client.logout()
        url = reverse('posts:comment-search', kwargs={'obj_id':self.posts[-1].id})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users:login')+f'?next={url}')


    def test_comment_search_view_raise_bad_request_for_post_request(self):
        """
        Test if the comment_search view returns a HttpResponseBadRequest if a POST request is made.
        """
        test_post = self.posts[0]
        response = self.client.post(reverse('posts:comment-search', kwargs={'obj_id': test_post.id}))
        self.assertEqual(response.status_code, 400)


    def test_comment_search_view_raises_not_found_for_invalid_obj_id(self):
        """
        Test if the comment_search view returns Http404 if a invalid 'obj_id' is passed.
        """
        invalid_id = 100
        url = reverse('posts:comment-search', kwargs={'obj_id': invalid_id})
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(404, response.status_code)


    def test_comment_search_view_returns_correct_user_list_if_query_exists(self):
        """
        Test if the comment_search view returns correct 'user_list' if the query match users.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
        )
        test_users = []
        for i in range(qty_test_users):
            user = f.create_test_user(
                username=f'testuser{i}',
                email=f'testuser{i}#email.com',
                password=f'testuser{i}password'
            )
            test_comment.likes.add(user)
            test_users.append(user)

        url = reverse('posts:comment-search', kwargs={'obj_id': test_comment.id})

        response = self.client.get(url, {'q': test_users[0].username})
        self.assertEqual(test_users[0].username, response.json()['user_list'][0]['username'])
        
        response = self.client.get(url, {'q': '2'})
        self.assertEqual(test_users[2].username, response.json()['user_list'][0]['username'])

        response = [u['username'] for u in self.client.get(url, {'q': 'user'}).json()['user_list']]
        for u in test_users:
            self.assertIn(u.username, response)


    def test_comment_search_view_returns_all_users_if_query_is_empty(self):
        """
        Test if the comment_search view returns all users present in comment likes if the query is empty.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
        )
        test_users = []
        for i in range(qty_test_users):
            user = f.create_test_user(
                username=f'testuser{i}',
                email=f'testuser{i}#email.com',
                password=f'testuser{i}password'
            )
            test_comment.likes.add(user)
            test_users.append(user)

        url = reverse('posts:comment-search', kwargs={'obj_id': test_comment.id})
        response = [u['username'] for u in self.client.get(url, {'q': ''}).json()['user_list']]
        self.assertEqual(len(test_users), len(response))
        for u in test_users:
            self.assertIn(u.username, response)
        

    def test_comment_search_view_returns_no_users_if_no_query_is_passed(self):
        """
        Test if the comment_search view returns no users if no query is passed.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
        )
        test_users = []
        for i in range(qty_test_users):
            user = f.create_test_user(
                username=f'testuser{i}',
                email=f'testuser{i}#email.com',
                password=f'testuser{i}password'
            )
            test_comment.likes.add(user)
            test_users.append(user)

        url = reverse('posts:comment-search', kwargs={'obj_id': test_comment.id})
        response = [u['username'] for u in self.client.get(url).json()['user_list']]
        self.assertEqual(len(test_users), len(response))
        for u in test_users:
            self.assertIn(u.username, response)


    def test_comment_search_view_returns_no_users_if_no_user_matches_query(self):
        """
        Test if the comment_search view returns no users if no user matches the query.
        """
        qty_test_users = 5
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
        )
        test_users = []
        for i in range(qty_test_users):
            user = f.create_test_user(
                username=f'testuser{i}',
                email=f'testuser{i}#email.com',
                password=f'testuser{i}password'
            )
            test_comment.likes.add(user)
            test_users.append(user)

        url = reverse('posts:comment-search', kwargs={'obj_id': test_comment.id})

        response = self.client.get(url, {'q': 'NoMatch'}).json()
        self.assertEqual(0, len(response['user_list']))
        

    def test_comment_search_view_returns_correct_parameters(self):
        """
        Test if the comment_search view returns the correct values for the parameters 'show_bio',
        'show_relationship', 'show_remove' and 'profile_user'.
        """
        test_post = self.posts[0]
        test_comment = f.create_test_comment(
            user=self.user,
            post=test_post,
        )
        url = reverse('posts:post-search', kwargs={'obj_id': test_comment.id})
        response = self.client.get(url).json()
        self.assertTrue(response['show_bio'])
        self.assertTrue(response['show_relationship'])
        self.assertFalse(response['show_remove'])
        self.assertEqual(self.user.username, response['profile_user'])