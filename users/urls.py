from django.urls import path, include
from django.contrib.auth import urls


from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.sign_up, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:user_id>/profile/', views.profile, name='profile'),
    path('<int:user_id>/following/', views.following, name='following'),
]