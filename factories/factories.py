from PIL import Image
from io import BytesIO


from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from users.models import CustomUser
from posts.models import PostModel
from comments.models import CommentModel


STD_TEST_USERNAME = 'test_user'
STD_TEST_EMAIL = 'testusername@testemail.com'
STD_TEST_PASSWORD = 'testpassword'


def create_test_user(username=STD_TEST_USERNAME, email=STD_TEST_EMAIL, password=STD_TEST_PASSWORD):
    if (CustomUser.objects.filter(username=username).exists()  or 
            CustomUser.objects.filter(email=email).exists()):
        count = CustomUser.objects.all().count()
        username = f'{count}{username}'
        email = f'{count}{email}'

    return CustomUser.objects.create_user(
        username = username,
        email = email,
        password = password
    )


def create_test_image():
    data = BytesIO()
    image = Image.new('RGB', (100, 100))
    image.save(data, format='png')
    return SimpleUploadedFile("test.jpg", data.getvalue())


def create_test_post(user=None, desc='Test Post'):
    if not user:
        user = create_test_user()
    return PostModel.objects.create(
        user = user,
        img = create_test_image(),
        description = desc,
        )


def create_test_comment(user=None, post=None, text='Test'):
    if not user:
        user = create_test_user()
    if not post:
        post = create_test_post(user)
    return CommentModel.objects.create(
        user = user,
        post = post,
        text = text,
    )