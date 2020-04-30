from django.urls import path

from . import views

app_name = 'discussions'
urlpatterns = [
    path('forums/', views.ForumView.as_view(), name='forum'),
    path('forums/topics/new/', views.CreateTopicView.as_view(), name='new_topic'),
    path('forums/<int:category_id>/', views.CategoryView.as_view(), name='category'),
    path('forums/topics/<int:topic_id>/', views.TopicView.as_view(), name='topic'),
    path('post/vote/<int:post_id>/<slug:direction>/', views.VotePostView.as_view(), name='vote_post'),
]
