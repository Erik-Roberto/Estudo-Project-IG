from django.urls import path, include
from django.contrib.auth import urls


from . import views

app_name = 'users'

urlpatterns = [
    path('', include('home.urls')),
    path('register/', views.sign_up, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/following/', views.following, name='following'),
    path('<str:username>/followers/', views.followers, name='followers'),
]