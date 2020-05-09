from django.forms import ModelForm, CharField, Textarea
from .models import Topic, Post


class TopicForm(ModelForm):
    topic_title = CharField(label='Title')

    class Meta:
        model = Topic
        fields = ('topic_title', 'category')


class PostForm(ModelForm):
    post_body = CharField(widget=Textarea(attrs={'rows': 5}), label='')

    class Meta:
        model = Post
        fields = ('post_body',)

