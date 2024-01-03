from django.contrib.auth.forms import UserCreationForm
from django import forms


from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    email = forms.EmailField(label='email')  

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)