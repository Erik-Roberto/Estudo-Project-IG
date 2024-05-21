from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import CustomUser
from posts.models import PostModel, CommentModel


STD_TEST_USERNAME = 'test_user'
STD_TEST_EMAIL = 'testusername@testemail.com'
STD_TEST_PASSWORD = 'testpassword'
TEST_IMAGE_PATH = 'media/images/tests/'
TEST_IMAGE_NAME = 'test_image.png'

def create_test_user(username=STD_TEST_USERNAME, email=STD_TEST_EMAIL, password=STD_TEST_PASSWORD):
    if (CustomUser.objects.filter(username=username).exists()  or 
            CustomUser.objects.filter(email=email).exists()):
        count = CustomUser.objects.all().count()
        username = f'{count}{username}'
        email = f'{username}@email.com'

    return CustomUser.objects.create_user(
        username = username,
        email = email,
        password = password
    )


def get_test_image():
    try:
        image = open(TEST_IMAGE_PATH + TEST_IMAGE_NAME, 'rb').read()
    except FileNotFoundError as err: 
        print('File not found. Try changing default path or create a new file.')
        raise err
    return SimpleUploadedFile(name=TEST_IMAGE_NAME, content=image, content_type='image/png')


def create_test_post(user=None, desc='Test Post'):
    if not user:
        user = create_test_user()
    return PostModel.objects.create(
        user = user,
        img = get_test_image(),
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