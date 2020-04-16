from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse, HttpResponseNotFound
from django.views import generic
from django.views.generic.base import View

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordResetDoneView, PasswordChangeDoneView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django.contrib.sites.shortcuts import get_current_site

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token

from django.core.exceptions import ObjectDoesNotExist

from django.template.loader import render_to_string
from django.core.mail import send_mail
from .decorators import async_func

from .forms import UserInfoForm, ProfileInfoForm, SignupForm, MessageForm, TopicForm, PostForm
from .models import Profile, Message, DeletedMessage, ReadMessages, Category, Topic, Post, PostVotes


class IndexView(generic.ListView):
    template_name = 'discussions/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        return User.objects.all()


class ForumView(generic.ListView):
    template_name = 'discussions/forum.html'
    context_object_name = 'categories_list'

    def get_queryset(self):
        return Category.objects.all()


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'discussions/user_profile.html'


class UserActivityView(generic.ListView):
    template_name = 'discussions/user_forum_activity.html'
    context_object_name = 'user_posts_list'

    def get_queryset(self):
        author = User.objects.get(pk=int(self.kwargs['pk']))
        return Post.objects.filter(author=author).order_by("-creation_date")


class CheckUserMixin(UserPassesTestMixin):
    login_url = reverse_lazy('discussions:login')

    def test_func(self):
        allow_access = self.request.user.is_authenticated
        return allow_access


class CheckMailboxUserMixin(CheckUserMixin):

    def test_func(self):
        allow_access = self.request.user.is_authenticated and self.request.user.pk == int(self.kwargs['pk'])
        return allow_access


class UserPageView(CheckUserMixin, View):
    """
    The view for redirecting user to his/her profile page with dynamic url
    """

    def get(self, request, *args, **kwargs):
        return redirect(f'/users/{request.user.pk}/')


class UserSignupView(View):

    @async_func
    def send_async_mail(self, subject, text_message, html_message, from_email, to_email):
        send_mail(subject=subject, message=text_message, html_message=html_message,
                  from_email=from_email, recipient_list=[to_email])

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activate your forum's account."
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            html_message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })

            text_message = render_to_string('registration/account_activation_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })

            from_email = 'forum.djangotest@gmail.com'
            to_email = form.cleaned_data.get('email')

            self.send_async_mail(subject=mail_subject, text_message=text_message, html_message=html_message,
                                 from_email=from_email, to_email=to_email)

            return redirect('discussions:email_confirm')
        else:
            return render(request, 'registration/signup.html', {'form': form})


class EmailConfirmView(View):
    def get(self, request):
        return render(request, 'registration/email_confirm.html')


class UserActivationView(View):

    def get(self, request, uidb64, token):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return render(request, 'registration/email_confirm_done.html')
        else:
            return render(request, 'registration/email_confirm_invalid.html')


class UserPageEditView(CheckUserMixin, View):

    def get(self, request, *args, **kwargs):
        user_instance = get_object_or_404(User, id=request.user.pk)
        initial_user_values = {'first_name': user_instance.first_name,
                               'last_name': user_instance.last_name,
                               'email': user_instance.email}

        profile_instance = get_object_or_404(Profile, user=request.user.pk)
        initial_profile_values = {'user_location': profile_instance.user_location,
                                  'user_about': profile_instance.user_about}

        user_avatar = profile_instance.user_avatar

        user_form = UserInfoForm(initial=initial_user_values)
        profile_form = ProfileInfoForm(initial=initial_profile_values)

        return render(request, 'discussions/profile_edit.html', {'user_form': user_form,
                                                                 'profile_form': profile_form,
                                                                 'user_avatar': user_avatar})

    def post(self, request, *args, **kwargs):
        user_instance = get_object_or_404(User, id=request.user.pk)
        profile_instance = get_object_or_404(Profile, user=request.user.pk)

        user_form = UserInfoForm(request.POST, instance=user_instance)
        profile_form = ProfileInfoForm(request.POST, request.FILES, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            not_empty_fields_user = [k for k, v in user_form.cleaned_data.items() if v]
            user_model_instance = user_form.save(commit=False)
            user_model_instance.save(update_fields=not_empty_fields_user)

            not_empty_fields_profile = [k for k, v in profile_form.cleaned_data.items() if v]
            profile_model_instance = profile_form.save(commit=False)
            profile_model_instance.save(update_fields=not_empty_fields_profile)

            return redirect('discussions:detail', pk=request.user.pk)


class UserPasswordResetDoneView(UserPassesTestMixin, PasswordResetDoneView):
    login_url = reverse_lazy('discussions:index')

    def test_func(self):
        prev_page = self.request.META.get('HTTP_REFERER')
        if prev_page:
            is_prev_page_was_passw_reset = '/password_reset/' in prev_page
        else:
            return False

        allow_access = is_prev_page_was_passw_reset and not self.request.user.is_authenticated
        return allow_access


class UserPasswordChangeDoneView(UserPassesTestMixin, PasswordChangeDoneView):
    login_url = reverse_lazy('discussions:index')

    def test_func(self):
        prev_page = self.request.META.get('HTTP_REFERER')
        if prev_page:
            is_prev_page_was_passw_change = '/password_change/' in prev_page
        else:
            return False

        allow_access = is_prev_page_was_passw_change and self.request.user.is_authenticated
        return allow_access


class MessageSentView(CheckUserMixin, View):

    def get(self, request, pk):
        receiver = User.objects.get(pk=pk)
        message_form = MessageForm(initial={'sender': request.user, 'receiver': receiver})
        return render(request, 'discussions/message_create.html', {'message_form': message_form,
                                                                   'receiver': receiver})

    def post(self, request, *args, **kwargs):
        message_form = MessageForm(request.POST)
        receiver_id = request.POST.get("receiver", "")
        receiver_instance = get_object_or_404(User, pk=receiver_id)

        if message_form.is_valid():
            message_form.save()

            return redirect('discussions:detail', pk=receiver_id)

        return render(request, 'discussions/message_create.html', {'message_form': message_form,
                                                                   'receiver': receiver_instance})


class InboxView(CheckMailboxUserMixin, generic.ListView):
    template_name = 'discussions/inbox.html'
    context_object_name = 'received_messages_list'

    def get_queryset(self):
        """Return list of messages in the inbox"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).values_list('message', flat=True)

        messages_list = Message.objects.filter(receiver=self.request.user).\
            order_by('-created_at').exclude(pk__in=deleted_messages)

        is_read_list = []
        for message in messages_list:
            # get read status for each message in messages_list.
            # ReadMessages table store only already read messages by users.
            is_read = ReadMessages.objects.filter(user=self.request.user.pk, message=message)
            is_read_list.append(True if is_read else False)

        messages_with_read_statuses = [[message, status] for message, status in zip(messages_list, is_read_list)]

        return messages_with_read_statuses


class OutboxView(CheckMailboxUserMixin, generic.ListView):
    template_name = 'discussions/outbox.html'
    context_object_name = 'sent_messages_list'

    def get_queryset(self):
        """Return list of messages in the inbox"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).values_list('message', flat=True)

        messages_list = Message.objects.filter(sender=self.request.user). \
            order_by('-created_at').exclude(pk__in=deleted_messages)

        is_read_list = []
        for message in messages_list:
            # get read status for each message in messages_list.
            # ReadMessages table store only already read messages by users.
            is_read = ReadMessages.objects.filter(user=self.request.user.pk, message=message)
            is_read_list.append(True if is_read else False)

        messages_with_read_statuses = [[message, status] for message, status in zip(messages_list, is_read_list)]

        return messages_with_read_statuses


class BucketView(CheckMailboxUserMixin, generic.ListView):
    template_name = 'discussions/deleted_messages.html'
    context_object_name = 'deleted_messages_list'

    def get_queryset(self):
        """Return list of deleted messages"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).exclude(is_deleted_permanently=True). \
            values_list('message', flat=True)

        messages_list = Message.objects.filter(pk__in=deleted_messages).order_by('-created_at')

        is_read_list = []
        for message in messages_list:
            # get read status for each message in messages_list.
            # ReadMessages table store only already read messages by users.
            is_read = ReadMessages.objects.filter(user=self.request.user.pk, message=message)
            is_read_list.append(True if is_read else False)

        messages_with_read_statuses = [[message, status] for message, status in zip(messages_list, is_read_list)]

        return messages_with_read_statuses


class MessageView(UserPassesTestMixin, View):
    login_url = reverse_lazy('discussions:login')

    def test_func(self):
        message = Message.objects.get(pk=int(self.kwargs['message_id']))

        is_sender = self.request.user == message.sender
        is_receiver = self.request.user == message.receiver

        allow_access = self.request.user.is_authenticated and (is_receiver or is_sender)
        return allow_access

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)

        try:
            is_from_bucket = 'bucket' in self.request.META.get('HTTP_REFERER')
        except TypeError as e:
            if "argument of type 'NoneType' is not iterable" in str(e):
                is_from_bucket = False

        try:
            DeletedMessage.objects.get(user=request.user, message=message)
            is_deleted = True
        except ObjectDoesNotExist:
            is_deleted = False

        is_read = ReadMessages.objects.filter(user=request.user.pk, message=message)

        return render(request, 'discussions/message.html', {'message': message,
                                                            'is_from_bucket': is_from_bucket,
                                                            'is_deleted': is_deleted,
                                                            'is_read': is_read})


class DeleteMessageView(CheckUserMixin, View):

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)

        is_sender = request.user == message.sender
        is_receiver = request.user == message.receiver

        # only sender or receiver can delete their own messages
        if any([is_sender, is_receiver]):

            # detect if the message is already in bucket or in inbox/outbox
            try:
                deleted_message = DeletedMessage.objects.get(user=request.user, message=message)
                is_in_bucket = True
            except ObjectDoesNotExist:
                is_in_bucket = False

            if is_in_bucket:
                # get the recipient if the current user is sender and the sender if the current user is recipient
                other_user = message.receiver if is_sender else message.sender

                # check if the message is already deleted by the other user
                try:
                    is_deleted_by_other_user = DeletedMessage.objects.get(user=other_user, message=message)
                except ObjectDoesNotExist:
                    is_deleted_by_other_user = False

                if is_deleted_by_other_user and is_deleted_by_other_user.is_deleted_permanently:
                    # delete message from Messages if the other user is already deleted it even from his/her bucket
                    message.delete()
                else:
                    # if the messages is in bucket, inbox, or outbox of the other user, then just set
                    # the is_deleted_permanently flag to True for the current user
                    # the message will not be shown in the current user's bucket from this moment
                    deleted_message.is_deleted_permanently = True
                    deleted_message.save()

                return redirect('discussions:bucket', pk=request.user.pk)

            else:
                # if the message was not in bucket, move it there (by creating the corresponding DeletedMessage object)
                deleted_message = DeletedMessage(user=request.user, message=message)
                deleted_message.save()

            return redirect('discussions:inbox', pk=request.user.pk) if is_receiver else redirect('discussions:outbox',
                                                                                                  pk=request.user.pk)
        return Http404('The page does not exist')


class RestoreMessageView(CheckUserMixin, View):

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)

        is_sender = request.user == message.sender
        is_receiver = request.user == message.receiver

        # only sender or receiver can restore their own messages
        if any([is_sender, is_receiver]):
            DeletedMessage.objects.get(user=request.user, message=message).delete()
            return redirect('discussions:bucket', pk=request.user.pk)

        return Http404('The page does not exist')


class ReadMessageView(CheckUserMixin, View):

    def get(self, request, message_id, read_action):
        user_instance = get_object_or_404(User, id=request.user.pk)
        message_instance = get_object_or_404(Message, id=message_id)

        if read_action == 'as_read':
            # adding the record to the ReadMessages table means that the given user has read the given message
            read_message = ReadMessages(user=user_instance, message=message_instance)
            read_message.save()
        else:
            # if there is no user-message pair in ReadMessages table - the given user hasn't read the given message yet
            read_message = get_object_or_404(ReadMessages, user=user_instance, message=message_instance)
            read_message.delete()

        # reload the current page (from which this view was called)
        return redirect(self.request.META.get('HTTP_REFERER'))


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

        if not request.user.is_anonymous:
            user_post_votes = []
            for post in posts_list:
                try:
                    post_vote_value = PostVotes.objects.get(user=request.user, post=post).vote_value
                except ObjectDoesNotExist:
                    post_vote_value = 0
                user_post_votes.append(post_vote_value)

            posts_with_vote_statuses = [[post, vote] for post, vote in zip(posts_list, user_post_votes)]

        else:
            posts_with_vote_statuses = [[post, None] for post in posts_list]

        return render(request, 'discussions/topic.html', {
            'posts_and_votes_list': posts_with_vote_statuses,
            'post_form': post_form,
            'topic_id': topic_id
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
