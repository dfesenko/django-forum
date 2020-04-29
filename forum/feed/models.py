from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_subscription")
    topic = models.ForeignKey('discussions.Topic', on_delete=models.CASCADE, related_name="topic_subscription")
    creation_date = models.DateTimeField(auto_now_add=True, null=True)


class ReadPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey("discussions.Post", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + " - " + str(self.post.pk)
