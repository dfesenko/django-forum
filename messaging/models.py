from django.db import models

from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.SET_NULL, null=True)
    receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=100, blank=True, default='(No subject)')
    msg_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'{self.sender} --> {self.receiver}: {self.subject}'


class DeletedMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_deleted_permanently = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} deleted {self.message.subject} {"permanently" if self.is_deleted_permanently else ""}'


class ReadMessages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + " - " + str(self.message.subject)
