from django.forms import ModelForm
from .models import User, Profile


class UserInfoForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileInfoForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['user_location', 'user_about', 'user_avatar']