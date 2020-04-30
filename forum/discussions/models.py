from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    topics_amount = models.IntegerField(default=0)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name


class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="topics")
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    topic_title = models.CharField(max_length=300)
    posts_amount = models.IntegerField(default=0)
    last_active_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="last_active_in_topics",
                                         null=True)

    def __str__(self):
        return self.topic_title


class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts")
    creation_date = models.DateTimeField(auto_now_add=True)
    post_body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="author_of_posts", null=True)

    def __str__(self):
        return self.author.username + " -> " + str(self.pk)

    def votes(self):
        return sum(PostVotes.objects.filter(post=self).values_list('vote_value', flat=True))


class PostVotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_votes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_votes")
    vote_value = models.IntegerField()
