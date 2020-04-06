from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    topics_amount = models.IntegerField(default=0)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name


class Topic(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="topics")
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    topic_title = models.CharField(max_length=300)
    posts_amount = models.IntegerField(default=0)
    last_active_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="last_active_in_topics",
                                         null=True)

    def __str__(self):
        return self.topic_title


class Post(models.Model):
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts")
    creation_date = models.DateTimeField(auto_now_add=True)
    post_body = models.TextField()
    votes = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="author_of_posts", null=True)

    def __str__(self):
        return self.author.username + " -> " + str(self.pk)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<username>/<filename>
    return '{0}/{1}'.format(instance.user.username, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_location = models.CharField(max_length=30, blank=True)
    user_about = models.TextField(max_length=500, blank=True)
    user_avatar = models.ImageField(upload_to=user_directory_path, blank=True, default='/default.png')
    user_posts_amount = models.IntegerField(default=0)
    user_last_forum_activity_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()


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
