from django.urls import path, include


from . import views

app_name = 'posts'

urlpatterns = [
    path('<int:obj_id>/post/search', views.post_search, name='post-search'),
    path('<int:obj_id>/comments/search', views.comment_search, name='comment-search'),
    path('<int:obj_id>/comments/', views.comment_likes, name='comments'),
    path('<int:post_id>/likes/', views.post_likes, name='likes'),
    path('<int:post_id>/', views.post, name='post'),
]