from django.db import models

import pgcrypto


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    topics_amount = models.IntegerField(default=0)
    last_updated_date = models.DateTimeField(auto_now_add=True, auto_now=True)


class Topic(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now_add=True, auto_now=True)
    topic_title = models.CharField(max_length=300)
    posts_amount = models.IntegerField(default=0)
    last_active_user = models.ForeignKey(User, default="deleted_user", on_delete=models.SET_DEFAULT)


class Post(models.Model):
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    post_body = models.TextField()
    votes = models.IntegerField(default=0)
    author_name = models.ForeignKey(User, default="deleted_user", on_delete=models.SET_DEFAULT)


class User(models.Model):
    username = models.CharField(max_length=60)
    user_password = pgcrypto.EncryptedTextField()
