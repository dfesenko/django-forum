from django.urls import path

from . import views


app_name = 'feed'
urlpatterns = [
    path('forums/topic/<int:topic_id>/subscription/', views.SubscribeTopicView.as_view(), name='subscription'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('post/<int:post_id>/mark-read/', views.MarkReadView.as_view(), name='mark_read'),
]