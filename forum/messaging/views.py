from django.views import generic
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist

from discussions.views import CheckUserMixin
from .models import Message, DeletedMessage, ReadMessages
from .forms import MessageForm


class MessageSentView(CheckUserMixin, View):

    def get(self, request, pk):
        receiver = User.objects.get(pk=pk)
        message_form = MessageForm(initial={'sender': request.user, 'receiver': receiver})
        return render(request, 'messaging/message_create.html', {'message_form': message_form,
                                                                 'receiver': receiver})

    def post(self, request, *args, **kwargs):
        message_form = MessageForm(request.POST)
        receiver_id = request.POST.get("receiver", "")
        receiver_instance = get_object_or_404(User, pk=receiver_id)

        if message_form.is_valid():
            message_form.save()

            return redirect('discussions:user_details', pk=receiver_id)

        return render(request, 'messaging/message_create.html', {'message_form': message_form,
                                                                 'receiver': receiver_instance})


class InboxView(CheckUserMixin, generic.ListView):
    template_name = 'messaging/inbox.html'
    context_object_name = 'received_messages_list'

    def get_queryset(self):
        """Return list of messages in the inbox"""
        deleted_messages = DeletedMessage.objects.filter(user=self.request.user).values_list('message', flat=True)

        messages_list = Message.objects.filter(receiver=self.request.user). \
            order_by('-created_at').exclude(pk__in=deleted_messages)

        is_read_list = []
        for message in messages_list:
            # get read status for each message in messages_list.
            # ReadMessages table store only already read messages by users.
            is_read = ReadMessages.objects.filter(user=self.request.user.pk, message=message)
            is_read_list.append(True if is_read else False)

        messages_with_read_statuses = [[message, status] for message, status in zip(messages_list, is_read_list)]

        return messages_with_read_statuses


class OutboxView(CheckUserMixin, generic.ListView):
    template_name = 'messaging/outbox.html'
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


class BucketView(CheckUserMixin, generic.ListView):
    template_name = 'messaging/bucket.html'
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
    login_url = reverse_lazy('messaging:login')

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

        return render(request, 'messaging/message.html', {'message': message,
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

                return redirect('messaging:bucket')

            else:
                # if the message was not in bucket, move it there (by creating the corresponding DeletedMessage object)
                deleted_message = DeletedMessage(user=request.user, message=message)
                deleted_message.save()

            return redirect('messaging:inbox') if is_receiver else redirect('messaging:outbox')
        return Http404('The page does not exist')


class RestoreMessageView(CheckUserMixin, View):

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)

        is_sender = request.user == message.sender
        is_receiver = request.user == message.receiver

        # only sender or receiver can restore their own messages
        if any([is_sender, is_receiver]):
            DeletedMessage.objects.get(user=request.user, message=message).delete()
            return redirect('messaging:bucket')

        return Http404('The page does not exist')


class MarkReadMessageView(CheckUserMixin, View):

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
