from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
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

from .forms import UserInfoForm, ProfileInfoForm, SignupForm, MessageForm
from .models import Profile, Message, DeletedMessage


class IndexView(generic.ListView):
    template_name = 'discussions/index.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        """Return list of registered users"""
        return User.objects.all()


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'discussions/user_profile.html'


class CheckUserMixin(UserPassesTestMixin):
    login_url = reverse_lazy('discussions:login')

    def test_func(self):
        allow_access = self.request.user.is_authenticated
        return allow_access


class CheckMailboxUserMixin(CheckUserMixin):
    login_url = reverse_lazy('discussions:login')

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

            return render(request, 'registration/email_confirm.html')

        else:
            return render(request, 'registration/signup.html', {'form': form})


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

            return redirect(f'/users/{request.user.pk}/')


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

            return redirect(f'/users/{receiver_id}/')

        return render(request, 'discussions/message_create.html', {'message_form': message_form,
                                                                   'receiver': receiver_instance})


class InboxView(CheckMailboxUserMixin, generic.ListView):
    template_name = 'discussions/inbox.html'
    context_object_name = 'received_messages_list'

    def get_queryset(self):
        """Return list of messages in the inbox"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).values_list('message', flat=True)
        return Message.objects.filter(receiver=self.request.user).order_by('-created_at').exclude(pk__in=
                                                                                                  deleted_messages)


class OutboxView(CheckMailboxUserMixin, generic.ListView):
    template_name = 'discussions/outbox.html'
    context_object_name = 'sent_messages_list'

    def get_queryset(self):
        """Return list of messages in the outbox"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).values_list('message', flat=True)
        return Message.objects.filter(sender=self.request.user).order_by('-created_at').exclude(pk__in=
                                                                                                deleted_messages)


class BucketView(CheckMailboxUserMixin, generic.ListView):
    template_name = 'discussions/deleted_messages.html'
    context_object_name = 'deleted_messages_list'

    def get_queryset(self):
        """Return list of deleted messages"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).exclude(is_deleted_permanently=True).\
            values_list('message', flat=True)
        return Message.objects.filter(pk__in=deleted_messages).order_by('-created_at')


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

        return render(request, 'discussions/message.html', {'message': message,
                                                            'is_from_bucket': is_from_bucket,
                                                            'is_deleted': is_deleted})


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

