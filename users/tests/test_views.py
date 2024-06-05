import json

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from posts.models import PostModel, CommentModel

from factories.factories import create_test_user


class UserViewsBase(TestCase):
    username = 'test_username'
    email = 'test_username@testemail.com'
    password='pass@123'


    def setUp(self):
        self.user = create_test_user(
            username=self.username,
            password=self.password,
            email=self.email
            )
        self.client.login(username=self.username, password=self.password)


class SignUpViewTests(UserViewsBase):

    def test_sign_up_view_fail_invalid_data(self):
        """
        Test the sign up view with a invalid email
        """
        logged_out = self.client.logout()
        data = {
            'username': 'test',
            'email': 'invalid_email'
        }
        response = self.client.post(reverse('users:sign_up'), data)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')


    def test_sign_up_view_fail_blank_data(self):
        """
        Test the sign up view with a blank form
        """
        logged_out = self.client.logout()
        response = self.client.post(reverse('users:sign_up'), {})
        self.assertFormError(response, 'form', 'email','This field is required.')
        self.assertFormError(response, 'form', 'username','This field is required.')
        self.assertFormError(response, 'form', 'password1','This field is required.')
        self.assertFormError(response, 'form', 'password2','This field is required.')


    def test_sign_up_view_success_valid_data(self):
        """
        Test the sign up view with valid data
        """
        logged_out = self.client.logout()
        data = {
            'username': 'user',
            'email': 'user@email.com',
            'password1': 'teste123456789',
            'password2': 'teste123456789',
        }
        response = self.client.post(reverse('users:sign_up'), data, follow=True)
        self.assertRedirects(response, reverse('users:login'))


    def test_sign_up_view_use_expected_template(self):
        """
        Test the sign up view template
        """
        logged_out = self.client.logout()
        response = self.client.get(reverse('users:sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')


    def test_sign_up_view_blocked_for_authenticated_user(self):
        """
        Test if the sign up view is blocked for users loged
        """
        response = self.client.get(reverse('users:sign_up'), follow=True)
        self.assertRedirects(response, reverse('users:profile', kwargs={'username': self.user.username}))


class LoginViewTests(UserViewsBase):

    def test_login_view_fail_blank_data(self):
        """
        Test the login view with a blank data
        """
        logged_out = self.client.logout()
        response = self.client.post(reverse('users:login'), {})
        self.assertFormError(response, 'form', 'username','This field is required.')
        self.assertFormError(response, 'form', 'password','This field is required.')


    def test_login_view_success_valid_data(self):
        """
        Test the login view with valid data
        """
        logged_out = self.client.logout()
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(reverse('users:login'), data, follow=True)
        self.assertRedirects(response, reverse('users:profile', kwargs={'username': self.user.username}))


    def test_login_view_use_expected_template(self):
        """
        Test the login view template
        """
        logged_out = self.client.logout()
        response = self.client.get(reverse('users:login'))
        self.assertTemplateUsed(response, 'users/login.html')


    def test_login_view_blocked_for_authenticated_user(self):
        """
        Test if the login view is blocked for users loged
        """
        response = self.client.get(reverse('users:login'), follow=True)
        self.assertRedirects(response, reverse('users:profile', kwargs={'username': self.user.username}))


class LogoutViewTests(UserViewsBase):

    def test_logout_view_blocked_for_unauthenticated_user(self):
        """
        Test if the logout view is protect of unauthenticated users
        """
        logged_out = self.client.logout()
        response = self.client.get(reverse('users:logout'), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:logout')}')

    
    def test_logout_view_success_loged_out(self):
        """
        Test if the logout view disconnect authenticated user
        """
        response = self.client.get(reverse('users:logout'), follow=True)
        self.assertRedirects(response, reverse('users:login'))


class ProfileViewTests(UserViewsBase):

    def test_profile_view_blocked_for_unauthenticated_user(self):
        """
        Test if the profile view is protect of unauthenticated users
        """
        logged_out = self.client.logout()
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:profile', kwargs={'username':self.user.username})}')


    def test_profile_view_use_expected_template(self):
        """
        Test the profile view template
        """
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')


    def test_profile_view_raise_404_inexistent_user(self):
        """
        Test profile view raise a HTTP404 for a invalid user id
        """
        invalid_username = 'ABCD100'
        response = self.client.get(reverse('users:profile', kwargs={'username':invalid_username}))
        self.assertEqual(response.status_code, 404)


    def test_profile_view_follow_user(self):
        """
        Test the funcionality of follow another user in profile view
        """
        user2 = create_test_user()
        self.assertFalse(self.user.is_following(user2.id))
        response = self.client.post(
            reverse('users:profile', kwargs={'username': user2.username}),
            data=json.dumps({
                'target': user2.username,
                'action': 'follow-unfollow',
            }),
            content_type='application/json',
        )
        self.assertTrue(response.json()['is_following'])
        self.assertTrue(self.user.is_following(user2.id))


    def test_profile_view_unfollow_user(self):
        """
        Test the funcionality of unfollow another user in profile view
        """
        user2 = create_test_user()
        self.assertFalse(self.user.is_following(user2.id))
        self.user.following.add(user2)
        self.assertTrue(self.user.is_following(user2.id))
        response = self.client.post(
            reverse('users:profile', kwargs={'username': user2.username}),
            data=json.dumps({
                'target': user2.username,
                'action': 'follow-unfollow',
            }),
            content_type='application/json',
        )
        self.assertFalse(response.json()['is_following'])
        self.assertFalse(self.user.is_following(user2.id))


    def test_profile_view_follow_unfollow_without_right_tag(self):
        """
        Test if the profile view raises expected error when the post data
        is missig a tag.
        """
        user2 = create_test_user()
        self.assertFalse(self.user.is_following(user2.id))
        with self.assertRaises(ValueError):        
            response = self.client.post(
                reverse('users:profile', kwargs={'username': user2.username}),
                data=json.dumps({
                    'target': user2.username,
                }),
                content_type='application/json',
            )


    def test_profile_view_follow_unfollow_raises_404_inexistent_user(self):
        """
        Test if the profile view raises 404 code for a iexistent user id
        """
        invalid_username = 'ABCD100'
        response = self.client.post(
                reverse('users:profile', kwargs={'username': invalid_username}),
                data=json.dumps({
                    'username': invalid_username,
                    'action': 'follow-unfollow',
                }),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 404)


    def test_profile_view_shows_all_posts(self):
        """
        Test if the profile view query passes all posts to template
        """
        qtd_posts = 5
        # Creating dummy posts
        for i in range(qtd_posts):
            PostModel.objects.create(user=self.user, description=f'Post#{i}')
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}))
        self.assertEqual(qtd_posts, response.context['posts'].count())

    
    def test_profile_view_show_correct_amount_of_users_being_followed(self):
        """
        Test if the correct amount of users that are being followed by page user are
        shown in profile view infos
        """
        qtd_users = 5
        # Creating dummy users
        for _ in range(qtd_users):
            user = create_test_user()
            self.user.following.add(user)
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}))
        self.assertEqual(qtd_users, response.context['following_qty'])
    
    
    def test_profile_view_show_correct_amount_of_followers(self):
        """
        Test if the correct amount of followers are shown in profile view infos
        """
        qtd_users = 7
        # Creating dummy users
        for _ in range(qtd_users):
            user = create_test_user()
            user.following.add(self.user)
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}))
        self.assertEqual(qtd_users, response.context['followers_qty'])
    
    
    def test_profile_view_show_correct_amount_of_likes_in_posts(self):
        """
        Test if the correct amount of likes are shown on each post
        """
        qty_users = 4
        qty_posts = 2
        # Creating dummy users
        users = [create_test_user() for _ in range(qty_users)]
        # Creating dummy posts
        for i in range(qty_posts):
            post = PostModel.objects.create(
                user=self.user,
                img='testing',
                description='desc'
            )
            for user in users:
                post.likes.add(user)
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}))
        for i in range(qty_posts):
            likes = response.context['posts'][i]['likes']
            self.assertEqual(qty_users, likes)

        
    def test_profile_view_show_correct_amount_of_comments_in_posts(self):
        """
        Test if the correct amount of comments are shown on each post
        """
        qty_users = 3
        qty_posts = 2
        # Creating dummy users
        users = [create_test_user() for _ in range(qty_users)]
        # Creating dummy posts and comments
        posts = []
        for i in range(qty_posts):
            post = PostModel.objects.create(
                user=self.user,
                img='testing',
                description='desc'
            )
            posts.append(post)
            for user in users:
                comment = CommentModel.objects.create(
                    user=user,
                    post=post,
                    text=f'Test Comment on {post.id} by {user.username}',
                )
        response = self.client.get(reverse('users:profile', kwargs={'username':self.user.username}))
        for i in range(qty_posts):
            comments = response.context['posts'][i]['comments']
            self.assertEqual(qty_users, comments)


class FollowingViewTests(UserViewsBase):

    def test_following_view_blocked_for_unauthenticated_user(self):
        """
        Test if the following view is protect of unauthenticated users
        """
        logged_out = self.client.logout()
        response = self.client.get(reverse('users:following', kwargs={'username':self.user.username}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:following', kwargs={'username':self.user.username})}')
    

    def test_following_view_use_expected_template(self):
        """
        Test the following view template
        """
        response = self.client.get(reverse('users:following', kwargs={'username':self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/users_card.html')


    def test_following_view_raise_404_inexistent_user(self):
        """
        Test following view raise a HTTP404 for a invalid user id
        """
        invalid_username = 'ABCD100'
        response = self.client.get(reverse('users:following', kwargs={'username':invalid_username}))
        self.assertEqual(response.status_code, 404)


    def test_following_view_list_all_following_list(self):
        """
        Test following view passes all followers to the template
        """
        qtd_users = 5
        # Creating dummy users
        for _ in range(qtd_users):
            user = create_test_user()
            self.user.following.add(user)
        response = self.client.get(reverse('users:following', kwargs={'username':self.user.username}))
        self.assertEqual(qtd_users, len(response.context['user_list']))


    def test_following_view_list_correctly_wich_user_are_followed(self):
        """
        Test if the list of all users of visited profile lists correctly wich user
        are being followed by logged user.
        """
        qtd_users = 5
        following_count = 0
        users = []
        for _ in range(qtd_users):
            user = create_test_user()
            self.user.following.add(user)
            following_count += 1
            users.append(user)
        response = self.client.get(reverse('users:following', kwargs={'username':self.user.username}))
        context_count = len([user for user, is_following in response.context['user_list'] if is_following])
        self.assertEqual(following_count, context_count)
        self.user.following.remove(users[0])
        response = self.client.get(reverse('users:following', kwargs={'username':self.user.username}))
        context_count = len([user for user, is_following in response.context['user_list'] if is_following])
        self.assertEqual(following_count-1, context_count)
        

    def test_following_view_returns_badrequest_if_post_request(self):
        """
        Test if the following view returns a HttpResponseBadRequest if a POST request is made.
        """
        response = self.client.post(reverse('users:following', kwargs={'username':self.user.username}))
        self.assertEqual(response.status_code, 400)


    def test_following_view_returns_correct_profile_user(self):
        """
        Test if the 'profile_user' returned by the following_view matches the user expected.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:following', kwargs={'username': test_user.username}))
        self.assertEqual(response.context['profile_user'].username, test_user.username)


    def test_following_view_returns_correct_logged_user(self):
        """
        Test if the 'logged_user' returned by the following_view matches the user expected.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:following', kwargs={'username': test_user.username}))
        self.assertEqual(response.context['logged_user'].username, self.user.username)


    def test_following_view_returns_correct_page_title(self):
        """
        Test if the 'page_title' returned by the following view is 'Seguindo'.
        """
        response = self.client.get(reverse('users:following', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page_title'], 'Seguindo')


    def test_following_view_returns_correct_search_url(self):
        """
        Test if the 'search_url' returned by the following view is correct.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:following', kwargs={'username': test_user.username}))
        self.assertEqual(
            response.context['search_url'],
            reverse('users:following_search', kwargs={'username':test_user.username})
            )


class FollowersViewTests(UserViewsBase):

    def test_followers_view_blocked_for_unauthenticated_user(self):
        """
        Test if the followers view is protect of unauthenticated users.
        """
        logged_out = self.client.logout()
        response = self.client.get(reverse('users:followers', kwargs={'username':self.user.username}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:followers', kwargs={'username':self.user.username})}')


    def test_followers_view_use_expected_template(self):
        """
        Test the followers view template
        """
        response = self.client.get(reverse('users:followers', kwargs={'username':self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/users_card.html')


    def test_followers_view_raise_404_inexistent_user(self):
        """
        Test followers view raise a HTTP404 for a invalid user id
        """
        invalid_username = 'ABCD100'
        response = self.client.get(reverse('users:followers', kwargs={'username':invalid_username}))
        self.assertEqual(response.status_code, 404)


    def test_followers_view_list_all_followers(self):
        """
        Test followers view passes all followers to the template
        """
        qtd_users = 5
        # Creating dummy users
        for _ in range(qtd_users):
            user = create_test_user()
            user.following.add(self.user)
        response = self.client.get(reverse('users:followers', kwargs={'username':self.user.username}))
        self.assertEqual(qtd_users, len(response.context['user_list']))


    def test_followers_view_list_correctly_wich_user_are_followed(self):
        """
        Test if the list of all users of visited profile lists correctly wich user
        are being followed by logged user.
        """
        qty_test_user = 5
        following_count = 0
        users = []
        for _ in range(qty_test_user):
            user = create_test_user()
            user.following.add(self.user)
            self.user.following.add(user)
            following_count += 1
            users.append(user)
        response = self.client.get(reverse('users:followers', kwargs={'username':self.user.username}))
        context_count = len([user for user, is_following in response.context['user_list'] if is_following])
        self.assertEqual(following_count, context_count)
        self.user.following.remove(users[0])
        response = self.client.get(reverse('users:followers', kwargs={'username':self.user.username}))
        context_count = len([user for user, is_following in response.context['user_list'] if is_following])
        self.assertEqual(following_count-1, context_count)


    def test_followers_view_returns_badrequest_if_post_request(self):
        """
        Test if the followers view returns a HttpResponseBadRequest if a POST request is made.
        """
        response = self.client.post(reverse('users:followers', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 400)


    def test_followers_view_returns_correct_profile_user(self):
        """
        Test if the 'profile_user' returned by the followers_view matches the user expected.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:followers', kwargs={'username': test_user.username}))
        self.assertEqual(response.context['profile_user'].username, test_user.username)


    def test_followers_view_returns_correct_logged_user(self):
        """
        Test if the 'logged_user' returned by the followers_view matches the user expected.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:followers', kwargs={'username': test_user.username}))
        self.assertEqual(response.context['logged_user'].username, self.user.username)


    def test_followers_view_returns_correct_page_title(self):
        """
        Test if the 'page_title' returned by the followers view is 'Seguidores'.
        """
        response = self.client.get(reverse('users:followers', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page_title'], 'Seguidores')


    def test_followers_view_returns_correct_search_url(self):
        """
        Test if the 'search_url' returned by the followers view is correct.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:followers', kwargs={'username': test_user.username}))
        self.assertEqual(
            response.context['search_url'],
            reverse('users:followers_search', kwargs={'username':test_user.username})
            )


class SearchViewTests(UserViewsBase):
    def test_search_view_is_blocked_for_unauthenticated_users(self):
        """
        Test if the search view is blocked for unauthenticated users.
        """
        loggout = self.client.logout()
        response = self.client.get(reverse('users:search'), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:search')}')


    def test_search_view_returns_badrequest_for_post_request(self):
        """
        Test if the search view returns a HttpResponseBadRequest response if a POST request is made    
        """
        response = self.client.post(reverse('users:search'))
        self.assertEqual(response.status_code, 400)


    def test_search_view_returns_correct_info(self):
        """
        Test if the search view returns the following parameters correctly:
        profile_user, show_bio, show_relationship and show_remove.
        """
        response = self.client.get(reverse('users:search')).json()
        self.assertIsNone(response['profile_user'])
        self.assertFalse(response['show_bio'])
        self.assertFalse(response['show_relationship'])
        self.assertFalse(response['show_remove'])


    def test_search_view_returns_empty_list_if_no_user_is_found(self):
        """
        Test if the search view returns a empty list if a query that matchs no user is received.
        """
        nonexistent_user = 'nonexistent_user'
        test_user = create_test_user()
        response = self.client.get(reverse('users:search'), {'q': nonexistent_user}).json()
        self.assertEqual(len(response['user_list']), 0)


    def test_search_view_returns_empty_list_if_empty_query(self):
        """
        Test if the search view returns a empty list if a empty query is received.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:search'), {'q': ''}).json()
        self.assertEqual(len(response['user_list']), 0)


    def test_search_view_returns_correct_user_list_for_query(self):
        """
        Test if the search view returns the correct list of users if a valid query is received.
        """
        qty_users = 5
        test_users = [create_test_user() for _ in range(qty_users)]
        # partial match
        query = 'test'
        response = self.client.get(reverse('users:search'), {'q': query}).json()
        response = [u['username'] for u in response['user_list']]
        for user in test_users:
            self.assertIn(user.username, response)


class FollowersSearchViewTests(UserViewsBase):
    
    def test_followers_search_view_is_blocked_for_unauthenticated_users(self):
        """
        Test if the followers_search view is blocked for unauthenticated users.
        """
        loggout = self.client.logout()
        response = self.client.get(reverse('users:followers_search', kwargs={'username': self.user.username}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:followers_search', kwargs={'username': self.user.username})}')


    def test_followers_search_view_returns_badrequest_for_post_request(self):
        """
        Test if the followers_search view returns a HttpResponseBadRequest response if a POST request is made    
        """
        test_user = create_test_user()
        response = self.client.post(reverse('users:followers_search', kwargs={'username': test_user.username}))
        self.assertEqual(response.status_code, 400)


    def test_followers_search_view_returns_correct_info(self):
        """
        Test if the followers_search view returns the following parameters correctly:
        profile_user, show_bio, show_relationship and show_remove.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:followers_search', kwargs={'username': test_user.username})).json()
        self.assertEqual(response['profile_user'], test_user.username)
        self.assertTrue(response['show_bio'])
        self.assertTrue(response['show_relationship'])
        self.assertFalse(response['show_remove'])


    def test_followers_search_view_returns_empty_list_if_no_user_is_found(self):
        """
        Test if the followers_search view returns a empty list if a query that matchs no user is received.
        """
        qty_users = 5
        users = []
        for _ in range(qty_users):
            user = create_test_user()
            user.following.add(self.user)
            users.append(user)
        test_user = create_test_user()
        response = self.client.get(
            reverse('users:followers_search', kwargs={'username': self.user.username}),
            {'q': test_user.username}
            ).json()
        self.assertEqual(len(response['user_list']), 0)


    def test_followers_search_view_returns_all_users_if_empty_query(self):
        """
        Test if the followers_search view returns all followers if a empty query is received.
        """
        qty_users = 5
        users = []
        for _ in range(qty_users):
            user = create_test_user()
            user.following.add(self.user)
            users.append(user)
        response = self.client.get(
            reverse('users:followers_search', kwargs={'username': self.user.username}),
            {'q': ''}
            ).json()
        self.assertEqual(len(response['user_list']), qty_users)


    def test_followers_search_view_returns_correct_user_list_for_query(self):
        """
        Test if the followers_search view returns the correct list of users if a valid query is received.
        """
        qty_users = 5
        query = 'test'
        users = []
        for _ in range(qty_users):
            user = create_test_user()
            user.following.add(self.user)
            users.append(user)
        response = self.client.get(
            reverse('users:followers_search', kwargs={'username': self.user.username}),
            {'q': query}
            ).json()
        response = [u['username'] for u in response['user_list']]
        for user in users:
            self.assertIn(user.username, response)


class FollowingSearchViewTests(UserViewsBase):

    def test_following_search_view_is_blocked_for_unauthenticated_users(self):
        """
        Test if the search view is blocked for unauthenticated users.
        """
        loggout = self.client.logout()
        response = self.client.get(reverse('users:following_search', kwargs={'username': self.user.username}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:following_search', kwargs={'username': self.user.username})}')


    def test_following_search_view_returns_badrequest_for_post_request(self):
        """
        Test if the following_search view returns a HttpResponseBadRequest response if a POST request is made    
        """
        test_user = create_test_user()
        response = self.client.post(reverse('users:following_search', kwargs={'username': test_user.username}))
        self.assertEqual(response.status_code, 400)


    def test_following_search_view_returns_correct_info(self):
        """
        Test if the following_search view returns the following parameters correctly:
        profile_user, show_bio, show_relationship and show_remove.
        """
        test_user = create_test_user()
        response = self.client.get(reverse('users:followers_search', kwargs={'username': test_user.username})).json()
        self.assertEqual(response['profile_user'], test_user.username)
        self.assertTrue(response['show_bio'])
        self.assertTrue(response['show_relationship'])
        self.assertFalse(response['show_remove'])
        
        response = self.client.get(reverse('users:followers_search', kwargs={'username': self.user.username})).json()
        self.assertTrue(response['show_remove'])


    def test_following_search_view_returns_empty_list_if_no_user_is_found(self):
        """
        Test if the following_search view returns a empty list if a query that matchs no user is received.
        """
        qty_users = 5
        users = []
        for _ in range(qty_users):
            user = create_test_user()
            user.following.add(self.user)
            users.append(user)
        test_user = create_test_user()
        response = self.client.get(
            reverse('users:following_search', kwargs={'username': self.user.username}),
            {'q': test_user.username}
            ).json()
        self.assertEqual(len(response['user_list']), 0)


    def test_following_search_view_returns_all_users_if_empty_query(self):
        """
        Test if the following_search view returns a all following users if a empty query is received.
        """
        qty_users = 5
        users = []
        for _ in range(qty_users):
            user = create_test_user()
            self.user.following.add(user)
            users.append(user)
        response = self.client.get(
            reverse('users:following_search', kwargs={'username': self.user.username}),
            {'q': ''}
            ).json()
        self.assertEqual(len(response['user_list']), qty_users)


    def test_following_search_view_returns_correct_user_list_for_query(self):
        """
        Test if the following_search view returns the correct list of users if a valid query is received.
        """
        qty_users = 5
        query = 'test'
        users = []
        for _ in range(qty_users):
            user = create_test_user()
            self.user.following.add(user)
            users.append(user)
        response = self.client.get(
            reverse('users:following_search', kwargs={'username': self.user.username}),
            {'q': query}
            ).json()
        response = [u['username'] for u in response['user_list']]
        for user in users:
            self.assertIn(user.username, response)