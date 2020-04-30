from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist

from .models import Subscription, ReadPost
from discussions.views import CheckUserMixin
from discussions.models import Topic, Post


class SubscribeTopicView(CheckUserMixin, View):
    def get(self, request, topic_id):
        if not request.is_ajax():
            return HttpResponseNotFound("Page not found")

        user = get_object_or_404(User, id=request.user.pk)
        topic = get_object_or_404(Topic, id=topic_id)

        try:
            subscription = Subscription.objects.get(user=user, topic=topic)

            # remove info about read posts when unsubscribing
            read_posts = ReadPost.objects.filter(user=self.request.user,
                                                 post__in=Post.objects.filter(topic=subscription.topic))

            for read_post in read_posts:
                read_post.delete()

            subscription.delete()
            status = {'code': '200', 'message': 'Subscription removed'}
        except ObjectDoesNotExist:
            Subscription(user=user, topic=topic).save()
            status = {'code': '200', 'message': 'Subscription created'}

        return JsonResponse(status)


class FeedView(CheckUserMixin, generic.ListView):
    template_name = 'feed/feed.html'
    context_object_name = 'posts_list'

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        posts_list = []

        for subscription in subscriptions:
            posts = Post.objects.filter(topic=subscription.topic) \
                .exclude(creation_date__lte=subscription.creation_date)

            read_posts = ReadPost.objects.filter(user=self.request.user).values_list('post', flat=True)
            posts = posts.exclude(pk__in=read_posts).exclude(author=self.request.user)

            posts_list.extend(posts)

        return sorted(posts_list, key=lambda x: x.creation_date, reverse=True)


class MarkReadView(CheckUserMixin, View):
    def get(self, request, post_id):
        user = get_object_or_404(User, id=request.user.pk)
        post = get_object_or_404(Post, id=post_id)

        try:
            get_object_or_404(ReadPost, user=user, post=post)
            return HttpResponseNotFound("This post is already marked as read by user")
        except Http404:
            read_post = ReadPost(user=user, post=post)
            read_post.save()
            return redirect('feed:feed')
