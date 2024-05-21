from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path('', include('home.urls')),
    path('register/', views.sign_up, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search, name='search'),
    path('<str:username>/following/search/', views.following_search, name='following_search'),
    path('<str:username>/followers/search/', views.followers_search, name='followers_search'),
    path('<str:username>/following/', views.following, name='following'),
    path('<str:username>/followers/', views.followers, name='followers'),
    path('<str:username>/', views.profile, name='profile'),
]