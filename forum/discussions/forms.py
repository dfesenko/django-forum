from django.forms import ModelForm, EmailField, CharField, Textarea, Select, ChoiceField, ModelChoiceField
from .models import User, Topic, Post

from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    email = EmailField(max_length=200, help_text='Required', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class TopicForm(ModelForm):
    topic_title = CharField(label='Title')

    class Meta:
        model = Topic
        fields = ('topic_title', 'category')


class PostForm(ModelForm):
    post_body = CharField(widget=Textarea({}), label='Text')

    class Meta:
        model = Post
        fields = ('post_body',)

