import json
from random import choice, randint, getrandbits


from django.test import TestCase
from django.urls import reverse


from users.models import CustomUser
from posts.models import PostModel
from factories.factories import create_test_user


class TestUserViews(TestCase):

    username = 'test_username'
    email = 'test_username@testemail.com'
    password='pass@123'


    def setUp(self):
        self.user = create_test_user(
            username=self.username,
            password=self.password,
            email=self.email
            )


    def test_sign_up_view_fail_invalid_data(self):
        """
        Test the sign up view with a invalid email
        """
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
        response = self.client.post(reverse('users:sign_up'), {})
        self.assertFormError(response, 'form', 'email','This field is required.')
        self.assertFormError(response, 'form', 'username','This field is required.')
        self.assertFormError(response, 'form', 'password1','This field is required.')
        self.assertFormError(response, 'form', 'password2','This field is required.')


    def test_sign_up_view_success_valid_data(self):
        """
        Test the sign up view with valid data
        """
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
        response = self.client.get(reverse('users:sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')


    def test_sign_up_view_blocked_for_authenticated_user(self):
        """
        Test if the sign up view is blocked for users loged
        """
        logged_in = self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('users:sign_up'), follow=True)
        self.assertTrue(logged_in)
        self.assertRedirects(response, reverse('users:profile', kwargs={'user_id': self.user.id}))


    def test_login_view_fail_blank_data(self):
        """
        Test the login view with a blank data
        """
        response = self.client.post(reverse('users:login'), {})
        self.assertFormError(response, 'form', 'username','This field is required.')
        self.assertFormError(response, 'form', 'password','This field is required.')


    def test_login_view_success_valid_data(self):
        """
        Test the login view with valid data
        """
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(reverse('users:login'), data, follow=True)
        self.assertRedirects(response, reverse('users:profile', kwargs={'user_id': self.user.id}))


    def test_login_view_use_expected_template(self):
        """
        Test the login view template
        """
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')


    def test_login_view_blocked_for_authenticated_user(self):
        """
        Test if the login view is blocked for users loged
        """
        logged_in = self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('users:login'), follow=True)
        self.assertTrue(logged_in)
        self.assertRedirects(response, reverse('users:profile', kwargs={'user_id': self.user.id}))


    def test_logout_view_blocked_for_unauthenticated_user(self):
        """
        Test if the logout view is protect of unauthenticated users
        """
        response = self.client.get(reverse('users:logout'), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:logout')}')

    
    def test_logout_view_success_loged_out(self):
        """
        Test if the logout view disconnect authenticated user
        """
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.get(reverse('users:logout'), follow=True)
        self.assertRedirects(response, reverse('users:login'))


    def test_profile_view_blocked_for_unauthenticated_user(self):
        """
        Test if the profile view is protect of unauthenticated users
        """
        response = self.client.get(reverse('users:profile', kwargs={'user_id':self.user.id}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:profile', kwargs={'user_id':self.user.id})}')


    def test_profile_view_use_expected_template(self):
        """
        Test the profile view template
        """
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.get(reverse('users:profile', kwargs={'user_id':self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')


    def test_profile_view_raise_404_inexistent_user(self):
        """
        Test profile view raise a HTTP404 for a invalid user id
        """
        wrong_id = 100
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.get(reverse('users:profile', kwargs={'user_id':wrong_id}))
        self.assertEqual(response.status_code, 404)


    def test_profile_view_follow_user(self):
        """
        Test the funcionality of follow another user in profile view
        """
        user2 = create_test_user()
        self.assertFalse(self.user.is_following(user2.id))
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.post(
            reverse('users:profile', kwargs={'user_id': user2.id}),
            data=json.dumps({
                'button': f'button-{user2.id}',
                'action': 'follow-unfollow',
            }),
            content_type="application/json",
        )
        self.assertTrue(response.json()['is_following'])
        self.assertTrue(self.user.is_following(user2.id))


    def test_profile_view_unfollow_user(self):
        """
        Test the funcionality of unfollow another user in profile view
        """
        user2 = create_test_user()
        self.assertFalse(self.user.is_following(user2.id))
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        self.user.following.add(user2)
        self.assertTrue(self.user.is_following(user2.id))
        response = self.client.post(
            reverse('users:profile', kwargs={'user_id': user2.id}),
            data=json.dumps({
                'button': f'button-{user2.id}',
                'action': 'follow-unfollow',
            }),
            content_type="application/json",
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
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        with self.assertRaises(ValueError):        
            response = self.client.post(
                reverse('users:profile', kwargs={'user_id': user2.id}),
                data=json.dumps({
                    'button': f'button-{user2.id}',
                }),
                content_type="application/json",
            )


    def test_profile_view_follow_unfollow_raises_404_inexistent_user(self):
        """
        Test if the profile view raises 404 code for a iexistent user id
        """
        wrong_id = randint(10,100)
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.post(
                reverse('users:profile', kwargs={'user_id': wrong_id}),
                data=json.dumps({
                    'button': f'button-{wrong_id}',
                    'action': 'follow-unfollow',
                }),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 404)


    def test_profile_view_shows_all_posts(self):
        """
        Test if the profile view query passes all posts to template
        """
        qtd_posts = randint(1,10)
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        # Creating dummy posts
        for i in range(qtd_posts):
            PostModel.objects.create(user=self.user, description=f'Post#{i}')
        response = self.client.get(reverse('users:profile', kwargs={'user_id':self.user.id}))
        self.assertEqual(qtd_posts, response.context['posts'].count())


    def test_following_view_blocked_for_unauthenticated_user(self):
        """
        Test if the following view is protect of unauthenticated users
        """
        response = self.client.get(reverse('users:following', kwargs={'user_id':self.user.id}), follow=True)
        self.assertRedirects(response, reverse('users:login') + f'?next={reverse('users:following', kwargs={'user_id':self.user.id})}')


    def test_following_view_use_expected_template(self):
        """
        Test the following view template
        """
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.get(reverse('users:following', kwargs={'user_id':self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/following.html')


    def test_following_view_raise_404_inexistent_user(self):
        """
        Test following view raise a HTTP404 for a invalid user id
        """
        wrong_id = randint(10, 100)
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        response = self.client.get(reverse('users:following', kwargs={'user_id':wrong_id}))
        self.assertEqual(response.status_code, 404)


    def test_following_view_list_all_following_list(self):
        """
        Test following view passes all followers to the template
        """
        qtd_users = randint(2,8)
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        # Creating dummy users
        for i in range(qtd_users):
            user = create_test_user(
                username=f'testuser{i}',
                email=f'emailuser{i}@test.com',
                password=f'passworduser{i}',
                )
            self.user.following.add(user)
        response = self.client.get(reverse('users:following', kwargs={'user_id':self.user.id}))
        self.assertEqual(qtd_users, len(response.context['following_list']))


    def test_following_view_list_correctly_wich_user_are_followed(self):
        """
        Test if the list of all users of visited profile lists correctly wich user
        are being followed by logged user.
        """
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)
        users = [
            create_test_user(
                username=f'testuser{i}',
                email=f'testuser{i}@test.com',
                password=f'passworduser{i}',
                )
            for i in range(randint(2, 8))
            ]
        random_user = choice(users)
        following_count = 0
        for user in users:
            random_user.following.add(user)
            if getrandbits(1):
                self.user.following.add(user)
                following_count += 1
        response = self.client.get(reverse('users:following', kwargs={'user_id':random_user.id}))
        context_count = len([user for user, is_following in response.context['following_list'] if is_following])
        self.assertEqual(following_count, context_count)