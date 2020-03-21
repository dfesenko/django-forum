from django.forms import ModelForm, EmailField
from .models import User, Profile

from django.contrib.auth.forms import UserCreationForm


class UserInfoForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileInfoForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['user_location', 'user_about', 'user_avatar']


class SignupForm(UserCreationForm):
    email = EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')