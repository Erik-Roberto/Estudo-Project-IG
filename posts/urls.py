from django.urls import path, include


from . import views

app_name = 'posts'

urlpatterns = [
    path('<int:post_id>', views.main_view, name='main-view')
]