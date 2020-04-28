from django.urls import path
from . import views


app_name = 'messages'
urlpatterns = [
    path('users/<int:pk>/message/', views.MessageSentView.as_view(), name='message_create'),
    path('users/inbox/', views.InboxView.as_view(), name='inbox'),
    path('users/outbox/', views.OutboxView.as_view(), name='outbox'),
    path('users/bucket/', views.BucketView.as_view(), name='bucket'),
    path('messages/<int:message_id>/', views.MessageView.as_view(), name='message'),
    path('messages/<int:message_id>/delete/', views.DeleteMessageView.as_view(), name='delete_message'),
    path('messages/<int:message_id>/restore/', views.RestoreMessageView.as_view(), name='restore_message'),
    path('messages/<int:message_id>/<slug:read_action>/', views.MarkReadMessageView.as_view(), name='read_unread'),
]