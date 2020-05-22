from .models import Topic, Post
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F


# increase/decrease topics counter for categories when new topic is added/deleted, update category's last_updated_date
@receiver(post_save, sender=Topic)
def update_category_when_topic_add(sender, instance, created, **kwargs):
    if created:
        category = instance.category
        category.topics_amount = F('topics_amount') + 1
        category.save()
        category.refresh_from_db()


@receiver(post_delete, sender=Topic)
def update_category_when_topic_delete(sender, instance, **kwargs):
    category = instance.category
    category.topics_amount = F('topics_amount') - 1
    category.save()
    category.refresh_from_db()


# increase/decrease posts counter for topics when new post is added/deleted, update topic's last_updated_date
@receiver(post_save, sender=Post)
def update_topic_when_post_add(sender, instance, created, **kwargs):
    if created:
        topic = instance.topic
        topic.posts_amount = F('posts_amount') + 1
        topic.last_active_user = instance.author
        topic.save()
        topic.refresh_from_db()

        category = topic.category
        category.last_updated_date = instance.creation_date
        category.save()


@receiver(post_delete, sender=Post)
def update_topic_when_post_delete(sender, instance, **kwargs):
    topic = instance.topic
    topic.posts_amount = F('posts_amount') - 1
    topic.save()
    topic.refresh_from_db()

