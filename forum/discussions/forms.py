from django.forms import ModelForm, EmailField, CharField, Textarea, Select, ChoiceField, ModelChoiceField
from .models import User, Profile, Message

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
    email = EmailField(max_length=200, help_text='Required', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class MessageForm(ModelForm):
    subject = CharField(max_length=100, initial='')
    msg_content = CharField(widget=Textarea({}), label='Message')

    class Meta:
        model = Message
        fields = ('sender', 'receiver', 'subject', 'msg_content')

