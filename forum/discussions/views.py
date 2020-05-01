from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.views import generic
from django.views.generic.base import View

from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.core.exceptions import ObjectDoesNotExist

from .forms import TopicForm, PostForm
from .models import Category, Topic, Post, PostVotes
from feed.models import Subscription
from core.views import CheckUserMixin


class ForumView(generic.ListView):
    template_name = 'discussions/forum.html'
    context_object_name = 'categories_list'

    def get_queryset(self):
        return Category.objects.all()


class CategoryView(generic.ListView):
    template_name = 'discussions/category.html'
    context_object_name = 'topics_list'

    def get_queryset(self):
        return Topic.objects.filter(category_id=self.kwargs['category_id'])


class TopicView(View):
    # todo: refactor this using FormView

    def get(self, request, topic_id):
        return self.post_list_response(request, PostForm())

    def post(self, request, topic_id):
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.topic = Topic.objects.get(pk=topic_id)
            post.save()
            return redirect('discussions:topic', topic_id=topic_id)

        return self.post_list_response(request, post_form)

    def post_list_response(self, request, post_form):
        topic_id = self.kwargs['topic_id']
        posts_list = Post.objects.filter(topic_id=topic_id).order_by('-creation_date')
        is_subscribed = False

        if not request.user.is_anonymous:
            user_post_votes = []
            for post in posts_list:
                try:
                    post_vote_value = PostVotes.objects.get(user=request.user, post=post).vote_value
                except ObjectDoesNotExist:
                    post_vote_value = 0
                user_post_votes.append(post_vote_value)

            posts_with_vote_statuses = [[post, vote] for post, vote in zip(posts_list, user_post_votes)]

            try:
                Subscription.objects.get(user=request.user, topic=topic_id)
                is_subscribed = True
            except ObjectDoesNotExist:
                pass

        else:
            posts_with_vote_statuses = [[post, None] for post in posts_list]

        return render(request, 'discussions/topic.html', {
            'posts_and_votes_list': posts_with_vote_statuses,
            'post_form': post_form,
            'topic_id': topic_id,
            'is_subscribed': is_subscribed
        })


class CreateTopicView(CheckUserMixin, View):
    def get(self, request):
        topic_form = TopicForm()
        post_form = PostForm()
        return render(request, 'discussions/topic_create.html', {'topic_form': topic_form,
                                                                 'post_form': post_form})

    def post(self, request, *args, **kwargs):
        topic_form = TopicForm(request.POST)
        post_form = PostForm(request.POST)

        if topic_form.is_valid() and post_form.is_valid():
            topic = topic_form.save(commit=False)
            topic.last_active_user = request.user
            topic.save()

            post = post_form.save(commit=False)
            post.author = request.user
            post.topic = topic
            post.save()

            return redirect('discussions:forum')

        return render(request, 'discussions/message_create.html', {'topic_form': topic_form,
                                                                   'post_form': post_form})


class VotePostView(CheckUserMixin, View):
    def get(self, request, direction, post_id):
        if not request.is_ajax():
            return HttpResponseNotFound("Page not found")

        vote_value = 1 if direction == 'up' else -1

        user = get_object_or_404(User, id=request.user.pk)
        post = get_object_or_404(Post, id=post_id)

        if user == post.author:
            return JsonResponse({
                'error': "You cannot vote for your own posts",
                'code': '400'
            })

        try:
            post_votes_obj = PostVotes.objects.get(user=request.user, post=post)
            previous_vote = post_votes_obj.vote_value

            # in case that the doubled  ajax request was sent somehow
            if previous_vote == vote_value:
                return JsonResponse({
                    'error': "Bad request.",
                    'code': '400'
                })

            post_votes_obj.delete()

        except ObjectDoesNotExist:
            PostVotes(user=user, post=post, vote_value=vote_value).save()
            previous_vote = 0

        status = {
            'votes': sum(PostVotes.objects.filter(post=post).values_list('vote_value', flat=True)),
            'prev_vote': previous_vote
        }
        return JsonResponse(status)
