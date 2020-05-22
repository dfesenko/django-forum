from django.forms import ModelForm, Textarea, CharField
from .models import User, Profile


class UserInfoForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileInfoForm(ModelForm):
    user_about = CharField(widget=Textarea({}), label='About me', required=False)

    class Meta:
        model = Profile
        fields = ['user_location', 'user_about', 'user_avatar']