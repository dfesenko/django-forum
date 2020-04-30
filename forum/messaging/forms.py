from django.forms import ModelForm, CharField, Textarea

from .models import Message


class MessageForm(ModelForm):
    subject = CharField(max_length=100, initial='')
    msg_content = CharField(widget=Textarea({}), label='Message')

    class Meta:
        model = Message
        fields = ('sender', 'receiver', 'subject', 'msg_content')