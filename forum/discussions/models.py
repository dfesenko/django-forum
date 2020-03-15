from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    topics_amount = models.IntegerField(default=0)
    last_updated_date = models.DateTimeField(auto_now=True)


class Topic(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    topic_title = models.CharField(max_length=300)
    posts_amount = models.IntegerField(default=0)
    last_active_user = models.ForeignKey(User, default="deleted_user", on_delete=models.SET_DEFAULT)


class Post(models.Model):
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    post_body = models.TextField()
    votes = models.IntegerField(default=0)
    author_name = models.ForeignKey(User, default="deleted_user", on_delete=models.SET_DEFAULT)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<username>/<filename>
    return '{0}/{1}'.format(instance.user.username, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_location = models.CharField(max_length=30, blank=True)
    user_about = models.TextField(max_length=500, blank=True)
    user_avatar = models.ImageField(upload_to=user_directory_path, blank=True, default='/default.png')
    user_posts_amount = models.IntegerField(default=0)
    user_last_forum_activity_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()
